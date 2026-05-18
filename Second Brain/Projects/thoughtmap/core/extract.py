"""Extract raw text segments from all data sources.

Sources:
  1. Obsidian daily notes (## Logs, ## Dziennik)
  2. Obsidian root topic notes (YYYY*.md)
  3. jointhubs-os AI-generated daily reviews
  4. Wispr Flow SQLite database (History table)
  5. Second Brain markdown files (jointhubs-os repo)
"""

from __future__ import annotations

import os
import re
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

import thoughtmap.config as config
from thoughtmap.core.models import TextSegment


def extract_all() -> list[TextSegment]:
    """Run all extractors and return combined segments."""
    segments: list[TextSegment] = []
    segments.extend(extract_obsidian_daily())
    segments.extend(extract_obsidian_root())
    segments.extend(extract_jointhubs_reviews())
    segments.extend(extract_second_brain())
    wispr = extract_wispr_flow()
    obsidian_logs = [s for s in segments if s.source == "obsidian-daily" and s.section == "logs"]
    wispr = match_and_classify_wispr(wispr, obsidian_logs)
    segments.extend(wispr)
    return segments


# ─── Obsidian daily notes ───

_SECTION_PATTERN = re.compile(r"^##\s+(.+)$", re.MULTILINE)
_TIMESTAMP_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\s*[-–]?\s*", re.MULTILINE)
_PROJECT_TAG = re.compile(r"#(\w[\w-]*)")
_DATE_PREFIX_PATTERN = re.compile(r"(\d{4})[-_]?")


def _year_glob_patterns() -> list[str]:
    """Generate glob prefix patterns for all years from MIN_YEAR to now."""
    import datetime
    current_year = datetime.datetime.now().year
    return [str(y) for y in range(config.MIN_YEAR, current_year + 1)]


def _is_2026_file(path: Path) -> bool:
    return any(path.stem.startswith(y) for y in _year_glob_patterns())


def _parse_date_from_filename(path: Path) -> datetime | None:
    match = re.match(r"(\d{4}-\d{2}-\d{2})", path.stem)
    if match:
        return datetime.strptime(match.group(1), "%Y-%m-%d")
    match = re.match(r"(\d{8})", path.stem)
    if match:
        return datetime.strptime(match.group(1), "%Y%m%d")
    return None


def _extract_sections(text: str) -> dict[str, str]:
    """Split markdown by ## headers, return {header_lower: content}."""
    sections: dict[str, str] = {}
    matches = list(_SECTION_PATTERN.finditer(text))
    for i, m in enumerate(matches):
        header = m.group(1).strip().lower()
        # Normalize known headers
        for key in ("logs", "dziennik"):
            if key in header:
                header = key
                break
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        if content:
            sections[header] = content
    return sections


def _split_log_entries(logs_text: str, file_date: datetime) -> list[tuple[datetime, str, str | None]]:
    """Split the ## Logs section into (timestamp, text, project_tag) tuples."""
    entries: list[tuple[datetime, str, str | None]] = []
    parts = _TIMESTAMP_PATTERN.split(logs_text)
    # parts: [before_first_ts, ts1, text1, ts2, text2, ...]
    i = 1
    while i < len(parts) - 1:
        ts_str = parts[i].strip()
        text = parts[i + 1].strip()
        if text:
            try:
                ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M")
            except ValueError:
                ts = file_date
            # Extract first project tag
            tag_match = _PROJECT_TAG.search(text)
            project_tag = tag_match.group(1) if tag_match else None
            # Remove the tag marker from text for cleaner embedding
            clean_text = _PROJECT_TAG.sub("", text).strip() if tag_match else text
            entries.append((ts, clean_text, project_tag))
        i += 2
    # If no timestamps found, treat entire block as one entry
    if not entries and logs_text.strip():
        tag_match = _PROJECT_TAG.search(logs_text)
        project_tag = tag_match.group(1) if tag_match else None
        entries.append((file_date, logs_text.strip(), project_tag))
    return entries


def extract_obsidian_daily() -> list[TextSegment]:
    """Extract segments from Obsidian daily notes (MIN_YEAR+)."""
    segments: list[TextSegment] = []
    daily_dir = config.OBSIDIAN_DAILY
    if not daily_dir.exists():
        return segments

    for year_prefix in _year_glob_patterns():
        for path in sorted(daily_dir.glob(f"{year_prefix}-*.md")):
            file_date = _parse_date_from_filename(path)
            if not file_date:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            sections = _extract_sections(text)

            # ## Logs — split by timestamps
            if "logs" in sections:
                for ts, entry_text, tag in _split_log_entries(sections["logs"], file_date):
                    segments.append(TextSegment(
                        text=entry_text, timestamp=ts, source="obsidian-daily",
                        source_file=str(path), section="logs", project_tag=tag,
                    ))

            # ## Dziennik — single block
            if "dziennik" in sections:
                segments.append(TextSegment(
                    text=sections["dziennik"], timestamp=file_date, source="obsidian-daily",
                    source_file=str(path), section="dziennik",
                ))

    return segments


# ─── Obsidian root topic notes ───

def extract_obsidian_root() -> list[TextSegment]:
    """Extract segments from root-level YYYY*.md files in the vault."""
    segments: list[TextSegment] = []
    vault_root = config.OBSIDIAN_VAULT
    if not vault_root.exists():
        return segments

    for year_prefix in _year_glob_patterns():
        for path in sorted(vault_root.glob(f"{year_prefix}*.md")):
            if not path.is_file():
                continue
            file_date = _parse_date_from_filename(path)
            if not file_date:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            # Strip frontmatter
            if text.startswith("---"):
                end = text.find("---", 3)
                if end != -1:
                    text = text[end + 3:].strip()
            if text:
                segments.append(TextSegment(
                    text=text, timestamp=file_date, source="obsidian-root",
                    source_file=str(path),
                ))

    return segments


# ─── jointhubs-os AI reviews ───

def extract_jointhubs_reviews() -> list[TextSegment]:
    """Extract segments from jointhubs-os AI-generated daily reviews (MIN_YEAR+)."""
    segments: list[TextSegment] = []
    reviews_dir = config.JOINTHUBS_DAILY
    if not reviews_dir.exists():
        return segments

    for year_prefix in _year_glob_patterns():
        for path in sorted(reviews_dir.glob(f"{year_prefix}-*.md")):
            if "-review" in path.stem:
                continue  # Skip review files, take main daily files only
            file_date = _parse_date_from_filename(path)
            if not file_date:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            sections = _extract_sections(text)

            # Extract key sections, skip boilerplate (GitHub tables, etc.)
            for key in ("notatki stworzone/zmienione dziś", "otwarte sprawy na jutro",
                         "z osobistego vaultu (dziś)"):
                for sec_name, sec_text in sections.items():
                    if key in sec_name:
                        segments.append(TextSegment(
                            text=sec_text, timestamp=file_date, source="jointhubs-review",
                            source_file=str(path), section=sec_name,
                        ))

    return segments


# ─── Second Brain markdown files ───

def _strip_frontmatter(text: str) -> str:
    """Remove YAML frontmatter from markdown text."""
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3:].strip()
    return text


def extract_second_brain() -> list[TextSegment]:
    """Extract segments from all .md files in Second Brain (repo), skipping generated dirs."""
    segments: list[TextSegment] = []
    sb_dir = config.SECOND_BRAIN_DIR
    if not sb_dir.exists():
        return segments

    exclude_dirs = config.SECOND_BRAIN_EXCLUDE_DIRS
    # Also skip daily/ — already covered by extract_jointhubs_reviews
    daily_dir = config.JOINTHUBS_DAILY.resolve()

    markdown_paths: list[Path] = []
    for root, dirnames, filenames in os.walk(sb_dir, topdown=True):
        dirnames[:] = [dirname for dirname in dirnames if dirname not in exclude_dirs]
        root_path = Path(root)
        for filename in filenames:
            if filename.lower().endswith(".md"):
                markdown_paths.append(root_path / filename)

    for md_path in sorted(markdown_paths):
        # Skip the daily reviews folder (already extracted separately)
        try:
            md_path.resolve().relative_to(daily_dir)
            continue
        except ValueError:
            pass
        # Skip README files — they're structural, not content
        if md_path.stem.upper() == "README":
            continue
        # Skip boilerplate files (LICENSE, CONTRIBUTING, CHANGELOG, etc.)
        if md_path.stem.upper().replace("-", "_") in {f.upper() for f in config.SECOND_BRAIN_EXCLUDE_FILES}:
            continue

        text = md_path.read_text(encoding="utf-8", errors="replace")
        text = _strip_frontmatter(text)
        # Skip very short files (< 50 chars after frontmatter removal)
        if len(text.strip()) < 50:
            continue

        # Try to get date from filename, fall back to file modification time
        file_date = _parse_date_from_filename(md_path)
        if not file_date:
            mtime = os.path.getmtime(md_path)
            file_date = datetime.fromtimestamp(mtime)

        segments.append(TextSegment(
            text=text, timestamp=file_date, source="second-brain",
            source_file=str(md_path),
        ))

    return segments


# ─── Wispr Flow ───

def _copy_wispr_snapshot(db_path: Path) -> Path:
    """Copy the live Wispr DB and sidecars so reads don't race active writes."""
    snapshot_dir = config.CACHE_DIR / "wispr"
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    snapshot_path = snapshot_dir / db_path.name
    shutil.copy2(db_path, snapshot_path)

    for suffix in ("-wal", "-shm"):
        src = Path(f"{db_path}{suffix}")
        dst = Path(f"{snapshot_path}{suffix}")
        if src.exists():
            shutil.copy2(src, dst)
        elif dst.exists():
            dst.unlink()

    return snapshot_path


def extract_wispr_flow() -> list[TextSegment]:
    """Extract dictation transcripts from Wispr Flow SQLite database (MIN_YEAR+)."""
    segments: list[TextSegment] = []
    db_path = config.WISPR_DB
    if not db_path.exists():
        return segments

    try:
        snapshot_path = _copy_wispr_snapshot(db_path)
    except OSError as exc:
        print(f"  Warning: failed to snapshot Wispr Flow DB at {db_path}: {exc}")
        snapshot_path = db_path

    try:
        conn = sqlite3.connect(str(snapshot_path))
    except sqlite3.Error as exc:
        print(f"  Warning: failed to open Wispr Flow DB at {db_path}: {exc}")
        return segments

    try:
        conn.text_factory = lambda data: data.decode("utf-8", errors="replace")
        conn.execute("PRAGMA query_only = ON")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT transcriptEntityId, formattedText, timestamp, app,
                   duration, numWords, detectedLanguage
            FROM History
            WHERE timestamp >= ?
              AND formattedText IS NOT NULL
              AND formattedText != ''
            ORDER BY timestamp ASC
        """, (f"{config.MIN_YEAR}-01-01",))
        rows = cursor.fetchall()
    except sqlite3.DatabaseError as exc:
        print(f"  Warning: failed to read Wispr Flow DB at {db_path}: {exc}")
        return segments
    finally:
        conn.close()

    for row in rows:
            entity_id, text, ts_str, app, duration, num_words, lang = row
            # Strip HTML tags from formattedText (Wispr sometimes adds <ul>, <li>, <ol>)
            clean = re.sub(r"<[^>]+>", "", text).strip()
            if not clean:
                continue
            try:
                ts = datetime.strptime(ts_str[:19], "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                continue
            segments.append(TextSegment(
                text=clean, timestamp=ts, source="wispr-flow",
                source_file=f"wispr:{entity_id}",
                language=lang, wispr_app=app,
                wispr_duration=duration, wispr_word_count=num_words,
            ))

    return segments


# ─── Wispr ↔ Obsidian matching ───

def _normalized_levenshtein(s1: str, s2: str) -> float:
    """Normalized Levenshtein distance (0.0 = identical, 1.0 = completely different)."""
    if not s1 and not s2:
        return 0.0
    if not s1 or not s2:
        return 1.0
    len1, len2 = len(s1), len(s2)
    if abs(len1 - len2) / max(len1, len2) > 0.5:
        return 1.0  # Fast reject if lengths differ drastically

    # Use simple substring check first (Wispr text is often pasted verbatim)
    shorter = s1 if len1 <= len2 else s2
    longer = s2 if len1 <= len2 else s1
    if shorter in longer:
        return 0.0

    # Fall back to Levenshtein for fuzzy cases
    # Simplified: compare first 200 chars to keep it fast
    a, b = s1[:200].lower(), s2[:200].lower()
    if len(a) == 0 or len(b) == 0:
        return 1.0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (ca != cb)))
        prev = curr
    return prev[len(b)] / max(len(a), len(b))


def match_and_classify_wispr(
    wispr_segments: list[TextSegment],
    obsidian_logs: list[TextSegment],
) -> list[TextSegment]:
    """Match Wispr Flow entries against Obsidian Logs and classify unmatched."""
    # Index obsidian logs by date for fast lookup
    logs_by_date: dict[str, list[str]] = {}
    for seg in obsidian_logs:
        date_key = seg.timestamp.strftime("%Y-%m-%d")
        logs_by_date.setdefault(date_key, []).append(seg.text)

    for seg in wispr_segments:
        date_key = seg.timestamp.strftime("%Y-%m-%d")
        matched = False

        # Only try matching if this was dictated in Obsidian
        if seg.wispr_app and "obsidian" in seg.wispr_app.lower():
            day_logs = logs_by_date.get(date_key, [])
            for log_text in day_logs:
                dist = _normalized_levenshtein(seg.text[:300], log_text[:300])
                if dist < config.WISPR_MATCH_THRESHOLD:
                    matched = True
                    break
                # Also check substring containment
                if seg.text[:100] in log_text or log_text[:100] in seg.text:
                    matched = True
                    break

        if matched:
            seg.intent = "note"
            seg.category = "note-taking"
        else:
            app = seg.wispr_app or ""
            seg.category = config.APP_CATEGORIES.get(app, config.APP_DEFAULT_CATEGORY)

    return wispr_segments
