"""Generate Kanban intake artifacts from ThoughtMap-adjacent operational sources."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from difflib import SequenceMatcher
from hashlib import sha1
import json
import re
from pathlib import Path
import unicodedata
from typing import TYPE_CHECKING, Any, Callable

import thoughtmap.config as config

if TYPE_CHECKING:
    from thoughtmap.analysis.ner import Entity


_COLUMN_ORDER = {
    "Inbox": 0,
    "Backlog": 1,
    "Research": 2,
    "Waiting": 3,
    "Blocked": 4,
    "Done": 5,
}

_COLUMN_PRECEDENCE = {
    "Done": 5,
    "Blocked": 4,
    "Waiting": 3,
    "Inbox": 2,
    "Research": 1,
    "Backlog": 0,
}

_PRIORITY_ORDER = {
    "critical": 4,
    "important": 3,
    "medium": 2,
    "low": 1,
    "info": 0,
}

_PRIORITY_HINTS = {
    "🔴": "critical",
    "⏫": "critical",
    "🟡": "important",
    "🔼": "important",
    "🔺": "medium",
    "⚪": "low",
    "🔽": "low",
    "ℹ️": "info",
}

_RESEARCH_HINTS = {
    "research", "sprawdzic", "sprawdzić", "zweryfikowac", "zweryfikować",
    "compare", "porownac", "porównać", "evaluate", "ocenic", "ocenić",
    "find", "znajdz", "znajdź", "investigate", "analiza", "analysis",
}

_WAITING_HINTS = {
    "waiting", "piłka", "pilka", "po stronie", "ball-on-her-side",
    "pending-reply-from-anna", "pending-reply-from-them",
}

_BLOCKED_HINTS = {
    "blocked", "brak", "missing", "unclear", "niejasny", "status niejasny",
    "auth unavailable", "missing dataset", "tool auth unavailable",
}

_CARD_LINE_RE = re.compile(r"^- \[(?P<checked>[ xX])\] (?P<body>.+?)\s*$")
_INLINE_META_RE = re.compile(r"\s+%%tm:id=(?P<card_id>[a-f0-9]{12})%%\s*$")


@dataclass
class KanbanCard:
    title: str
    column: str
    priority: str
    source_kind: str
    source_file: str
    source_excerpt: str = ""
    notes: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    entity_links: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    needs_research: bool = False
    tavily_query: str | None = None
    card_id: str = ""
    tracking_refs: list[str] = field(default_factory=list)


@dataclass
class BoardCardState:
    title: str
    column: str
    card_id: str | None = None
    checked: bool = False


def sync_kanban_curation(on_status: Callable[[str], None] | None = None) -> dict[str, Any]:
    """Harvest manual edits from the current intake board into reusable curation state."""

    def status(message: str) -> None:
        if on_status:
            on_status(message)

    curation = _load_curation()
    previous_cards = _load_previous_cards()
    board_cards = _parse_board_cards(config.KANBAN_INTAKE_PATH)

    if previous_cards and board_cards:
        previous_by_id = {card.card_id: card for card in previous_cards if card.card_id}
        unmatched_previous = list(previous_cards)
        matched_ids: set[str] = set()
        override_count = 0
        suppressed_count = 0

        for board_card in board_cards:
            previous = _match_previous_card(board_card, unmatched_previous, previous_by_id)
            if previous is None:
                continue

            matched_ids.add(previous.card_id)
            unmatched_previous = [card for card in unmatched_previous if card.card_id != previous.card_id]

            for ref in previous.tracking_refs:
                curation["suppressed_refs"].pop(ref, None)

            if _normalize_board_title(board_card.title) != _normalize_board_title(previous.title):
                curation["title_overrides"][previous.card_id] = board_card.title
                _record_entity_alias_override(curation, previous.title, board_card.title)
                override_count += 1

        for previous in previous_cards:
            if previous.card_id in matched_ids or previous.column == "Done":
                continue
            for ref in previous.tracking_refs:
                if ref not in curation["suppressed_refs"]:
                    curation["suppressed_refs"][ref] = {
                        "card_id": previous.card_id,
                        "title": previous.title,
                        "source_kind": previous.source_kind,
                        "source_excerpt": previous.source_excerpt,
                        "suppressed_at": datetime.now().isoformat(timespec="seconds"),
                    }
                    suppressed_count += 1

        status(
            f"  Intake curation synced: {override_count} title overrides, "
            f"{suppressed_count} suppressed tracking refs"
        )

    _save_curation(curation)
    _sync_entity_registry_from_curation(curation, on_status=status)
    _apply_curation_aliases_to_ner_cache(curation, on_status=status)
    return curation


def generate_kanban_artifacts(
    entities: list[Entity] | None = None,
    on_status: Callable[[str], None] | None = None,
) -> dict[str, Path]:
    """Generate machine-readable Kanban tasks plus a markdown-backed intake board."""

    def status(message: str) -> None:
        if on_status:
            on_status(message)

    curation = _load_curation()
    review_files = _latest_review_files(limit=3)
    cards: dict[str, KanbanCard] = {}

    for review_path in review_files:
        sections = _read_h2_sections(review_path)
        for card in _cards_from_action_items(review_path, sections.get("Action Items", "")):
            _merge_card(cards, card)
        for card in _cards_from_carry_forward(review_path, sections.get("Carry-Forward", "")):
            _merge_card(cards, card)
        for card in _cards_from_obsidian_tasks(review_path, sections.get("Obsidian Tasks", "")):
            _merge_card(cards, card)

    for card in _cards_from_thread_state(config.PEERS_DIR / "thread-state.json"):
        _merge_card(cards, card)

    for card in _cards_from_linkedin_tracker(config.PEERS_DIR / "linkedin-tracker.md"):
        _merge_card(cards, card)

    for card in _cards_from_communication_map(config.PEERS_DIR / "communication-map.md"):
        _merge_card(cards, card)

    entity_index = entities or []
    curated_cards: list[KanbanCard] = []
    for card in cards.values():
        _ensure_card_identity(card)
        if _is_suppressed(card, curation):
            continue
        if card.card_id in curation.get("title_overrides", {}):
            card.title = curation["title_overrides"][card.card_id]
        _resolve_entities(card, entity_index)
        if card.column == "Backlog" and _needs_research(card):
            card.column = "Research"
            card.needs_research = True
            card.tavily_query = _build_tavily_query(card)
        curated_cards.append(card)

    ordered_cards = sorted(
        curated_cards,
        key=lambda card: (
            _COLUMN_ORDER.get(card.column, 99),
            -_PRIORITY_ORDER.get(card.priority, 0),
            _normalize_text(card.title),
        ),
    )

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_review_files": [path.as_posix() for path in review_files],
        "sources": {
            "communication_map": config.PEERS_DIR.joinpath("communication-map.md").as_posix(),
            "linkedin_tracker": config.PEERS_DIR.joinpath("linkedin-tracker.md").as_posix(),
            "thread_state": config.PEERS_DIR.joinpath("thread-state.json").as_posix(),
        },
        "cards": [asdict(card) for card in ordered_cards],
    }

    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    config.KANBAN_DIR.mkdir(parents=True, exist_ok=True)
    config.KANBAN_TASKS_PATH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    config.KANBAN_INTAKE_PATH.write_text(_render_kanban_board(ordered_cards), encoding="utf-8")

    status(
        f"  Kanban intake: {len(ordered_cards)} cards → {config.KANBAN_TASKS_PATH.name}, "
        f"{config.KANBAN_INTAKE_PATH.name}"
    )
    return {
        "json": config.KANBAN_TASKS_PATH,
        "board": config.KANBAN_INTAKE_PATH,
    }


def _latest_review_files(limit: int) -> list[Path]:
    if not config.REVIEWS_DIR.exists():
        return []
    files = sorted(config.REVIEWS_DIR.glob("*-review.md"), reverse=True)
    return files[:limit]


def _read_h2_sections(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        match = re.match(r"^##\s+(.*)$", line)
        if match:
            current = match.group(1).strip()
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def _cards_from_action_items(source_file: Path, section: str) -> list[KanbanCard]:
    cards: list[KanbanCard] = []
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not re.match(r"^\d+\.\s+", line):
            continue
        priority = _extract_priority(line)
        title = _clean_text(re.sub(r"^\d+\.\s+", "", line))
        cards.append(_make_card(
            title=title,
            column="Backlog",
            priority=priority,
            source_kind="review-action-items",
            source_file=source_file.as_posix(),
            source_excerpt=line,
            tracking_key=title,
        ))
    return cards


def _cards_from_carry_forward(source_file: Path, section: str) -> list[KanbanCard]:
    cards: list[KanbanCard] = []
    for row in _parse_markdown_table(section):
        issue = _clean_text(row.get("Sprawa", ""))
        status_text = row.get("Status", "")
        if not issue:
            continue
        cards.append(_make_card(
            title=issue,
            column=_column_from_status(status_text, default="Backlog"),
            priority=_extract_priority(status_text),
            source_kind="review-carry-forward",
            source_file=source_file.as_posix(),
            source_excerpt=status_text,
            tracking_key=issue,
        ))
    return cards


def _cards_from_obsidian_tasks(source_file: Path, section: str) -> list[KanbanCard]:
    cards: list[KanbanCard] = []
    for row in _parse_markdown_table(section):
        task = _clean_text(row.get("Task", "") or row.get("Zadanie", ""))
        if not task:
            continue
        priority = _extract_priority(row.get("Priorytet", "") or row.get("Priority", ""))
        age = row.get("Dni otwarte", "") or row.get("Status", "")
        cards.append(_make_card(
            title=task,
            column="Backlog",
            priority=priority,
            source_kind="review-obsidian-task",
            source_file=source_file.as_posix(),
            source_excerpt=age,
            tracking_key=task,
        ))
    return cards


def _cards_from_thread_state(path: Path) -> list[KanbanCard]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    cards: list[KanbanCard] = []
    gmail = payload.get("channels", {}).get("gmail", {})
    for thread in gmail.get("threads", {}).values():
        status_value = str(thread.get("status", ""))
        if status_value in {"answered", "closed", "info"}:
            continue
        counterparty = _display_counterparty(thread.get("counterparty", "email"))
        subject = _clean_text(str(thread.get("subject", "")))
        title = _title_from_gmail_status(status_value, counterparty, subject)
        cards.append(_make_card(
            title=title,
            column=_column_from_status(status_value, default="Inbox"),
            priority=_priority_from_thread_status(status_value, str(thread.get("priority", "info"))),
            source_kind="thread-state-gmail",
            source_file=path.as_posix(),
            source_excerpt=subject,
            notes=[f"thread_status={status_value}"],
            tracking_key=f"{counterparty}|{subject or status_value}",
        ))

    discord = payload.get("channels", {}).get("discord", {})
    for name, dm in discord.get("dms", {}).items():
        status_value = str(dm.get("status", ""))
        if "pending" not in status_value:
            continue
        cards.append(_make_card(
            title=_title_from_discord_status(name, status_value),
            column=_column_from_status(status_value, default="Inbox"),
            priority="important",
            source_kind="thread-state-discord",
            source_file=path.as_posix(),
            source_excerpt=str(dm.get("note", "")),
            notes=[f"discord_status={status_value}"],
            tracking_key=f"{name}|{status_value}",
        ))
    return cards


def _cards_from_linkedin_tracker(path: Path) -> list[KanbanCard]:
    if not path.exists():
        return []
    sections = _read_h2_sections(path)
    cards: list[KanbanCard] = []

    for row in _parse_markdown_table(sections.get("Active Threads", "")):
        contact = _clean_text(row.get("Contact", ""))
        status_value = row.get("Status", "")
        if (
            not contact
            or "✅" in status_value
            or "confirmed" in _normalize_text(status_value)
            or "done" in _normalize_text(status_value)
        ):
            continue
        cards.append(_make_card(
            title=f"[linkedin] Follow up with {contact}",
            column=_column_from_status(status_value, default="Inbox"),
            priority=_extract_priority(status_value),
            source_kind="linkedin-active-thread",
            source_file=path.as_posix(),
            source_excerpt=status_value,
            tracking_key=f"{contact}|{status_value}",
        ))

    for row in _parse_markdown_table(sections.get("Pending Outreach", "")):
        contact = _clean_text(row.get("Contact", ""))
        purpose = _clean_text(row.get("Purpose", ""))
        if (
            not contact
            or "✅" in purpose
            or "done" in _normalize_text(purpose)
        ):
            continue
        cards.append(_make_card(
            title=f"[linkedin] Reach out to {contact}",
            column="Inbox",
            priority=_extract_priority(row.get("Priority", "")),
            source_kind="linkedin-pending-outreach",
            source_file=path.as_posix(),
            source_excerpt=purpose,
            tracking_key=f"{contact}|{purpose}",
        ))
    return cards


def _cards_from_communication_map(path: Path) -> list[KanbanCard]:
    if not path.exists():
        return []
    sections = _read_h2_sections(path)
    cards: list[KanbanCard] = []

    for row in _parse_markdown_table(sections.get("Active contacts (last 2 weeks)", "")):
        person = _clean_text(row.get("Person", ""))
        open_thread = row.get("Open thread?", "")
        peer_exists = row.get("Peer note exists?", "")
        if person and "❌" in peer_exists:
            cards.append(_make_card(
                title=f"[peers] Create peer note for {person}",
                column="Backlog",
                priority="important",
                source_kind="communication-map-peer-gap",
                source_file=path.as_posix(),
                source_excerpt=peer_exists,
                tracking_key=f"peer-gap|{person}",
            ))
        if person and open_thread and ("⌛" in open_thread or "⚠️" in open_thread or "🔴" in open_thread):
            cards.append(_make_card(
                title=f"[communication] Resolve thread with {person}",
                column=_column_from_status(open_thread, default="Inbox"),
                priority=_extract_priority(open_thread),
                source_kind="communication-map-thread",
                source_file=path.as_posix(),
                source_excerpt=open_thread,
                tracking_key=f"thread|{person}|{open_thread}",
            ))
    return cards


def _make_card(
    *,
    title: str,
    column: str,
    priority: str,
    source_kind: str,
    source_file: str,
    source_excerpt: str = "",
    notes: list[str] | None = None,
    tracking_key: str | None = None,
) -> KanbanCard:
    ref = _tracking_ref(source_kind, tracking_key or source_excerpt or title)
    return KanbanCard(
        title=title,
        column=column,
        priority=priority,
        source_kind=source_kind,
        source_file=source_file,
        source_excerpt=source_excerpt,
        notes=list(notes or []),
        tracking_refs=[ref],
    )


def _parse_markdown_table(section: str) -> list[dict[str, str]]:
    lines = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        return []
    headers = [cell.strip() for cell in lines[0].strip("|").split("|")]
    rows: list[dict[str, str]] = []
    for line in lines[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(headers):
            continue
        rows.append(dict(zip(headers, cells, strict=False)))
    return rows


def _merge_card(cards: dict[str, KanbanCard], incoming: KanbanCard) -> None:
    key = _card_merge_key(incoming)
    if key not in cards:
        cards[key] = incoming
        return

    current = cards[key]
    if _COLUMN_PRECEDENCE.get(incoming.column, -1) > _COLUMN_PRECEDENCE.get(current.column, -1):
        current.column = incoming.column
    if _PRIORITY_ORDER.get(incoming.priority, -1) > _PRIORITY_ORDER.get(current.priority, -1):
        current.priority = incoming.priority
    if incoming.source_excerpt and incoming.source_excerpt not in current.notes:
        current.notes.append(incoming.source_excerpt)
    if incoming.source_kind not in current.notes:
        current.notes.append(f"source={incoming.source_kind}")
    for ref in incoming.tracking_refs:
        if ref not in current.tracking_refs:
            current.tracking_refs.append(ref)


def _resolve_entities(card: KanbanCard, entities: list[Entity]) -> None:
    normalized_title = _normalize_text(card.title)
    matches: list[Entity] = []
    for entity in sorted(entities, key=lambda value: value.mention_count, reverse=True):
        normalized = entity.normalized.strip()
        if not normalized:
            continue
        if normalized in normalized_title:
            matches.append(entity)
        elif any(alias and _normalize_text(alias) in normalized_title for alias in entity.aliases):
            matches.append(entity)
        if len(matches) >= 3:
            break

    for entity in matches:
        slug = _slugify(entity.name)
        entity_link = f"Operations/thoughtmap-out/entities/{entity.type}/{slug}"
        card.entities.append(entity.name)
        card.entity_links.append(entity_link)
        card.tags.append(f"#entity/{slug}")
        card.tags.append(f"#entity-type/{entity.type}")


def _needs_research(card: KanbanCard) -> bool:
    normalized_title = _normalize_text(card.title)
    return any(term in normalized_title for term in _RESEARCH_HINTS)


def _build_tavily_query(card: KanbanCard) -> str:
    if card.entities:
        return f"{card.entities[0]} current status next step"
    return _clean_text(re.sub(r"^\[[^\]]+\]\s*", "", card.title))


def _column_from_status(status_text: str, default: str) -> str:
    normalized = _normalize_text(status_text)
    if any(hint in normalized for hint in _BLOCKED_HINTS):
        return "Blocked"
    if any(hint in normalized for hint in _WAITING_HINTS):
        return "Waiting"
    if any(token in normalized for token in {"pending reply", "pending action", "pending verification"}):
        return "Inbox"
    return default


def _extract_priority(text: str) -> str:
    for marker, priority in _PRIORITY_HINTS.items():
        if marker in text:
            return priority
    normalized = _normalize_text(text)
    if "critical" in normalized or "pilne" in normalized:
        return "critical"
    if "important" in normalized or "today" in normalized or "dzis" in normalized:
        return "important"
    return "medium"


def _priority_from_thread_status(status_value: str, explicit_priority: str) -> str:
    normalized = _normalize_text(status_value)
    explicit = _normalize_text(explicit_priority)
    if explicit in _PRIORITY_ORDER:
        return explicit
    if "action" in normalized or "reply" in normalized:
        return "important"
    if "verification" in normalized:
        return "medium"
    return "info"


def _title_from_gmail_status(status_value: str, counterparty: str, subject: str) -> str:
    normalized = _normalize_text(status_value)
    if "reply" in normalized:
        return f"[email] Reply to {counterparty}"
    if "verification" in normalized:
        return f"[email] Verify {subject or counterparty}"
    if "action" in normalized:
        return f"[email] Action: {subject or counterparty}"
    return f"[email] Review {subject or counterparty}"


def _title_from_discord_status(name: str, status_value: str) -> str:
    normalized = _normalize_text(status_value)
    display_name = _clean_person_name(name)
    if "from-user" in normalized or "from-me" in normalized:
        return f"[discord] Reply to {display_name}"
    return f"[discord] Waiting for {display_name}"


def _display_counterparty(value: str) -> str:
    text = value.strip()
    if "@" not in text:
        return _clean_person_name(text)
    local = text.split("@", 1)[0].replace(".", " ").replace("_", " ").replace("-", " ")
    return _clean_person_name(local)


def _clean_person_name(value: str) -> str:
    cleaned = value.replace("_", " ").replace("-", " ").strip()
    return " ".join(part.capitalize() for part in cleaned.split()) or value


def _tracking_ref(source_kind: str, tracking_key: str) -> str:
    normalized = _normalize_text(tracking_key) or "untitled"
    return sha1(f"{source_kind}|{normalized}".encode("utf-8")).hexdigest()[:12]


def _card_merge_key(card: KanbanCard) -> str:
    return _normalize_board_title(card.title)


def _normalize_board_title(value: str) -> str:
    return _normalize_text(_strip_generated_suffix(value))


def _strip_generated_suffix(value: str) -> str:
    text = _INLINE_META_RE.sub("", value).strip()
    text = re.sub(r"(?:\s+#\S+)+$", "", text)
    return _clean_text(text)


def _ensure_card_identity(card: KanbanCard) -> None:
    if not card.tracking_refs:
        fallback = card.source_excerpt if _is_meaningful_tracking_text(card.source_excerpt) else card.title
        card.tracking_refs = [_tracking_ref(card.source_kind, fallback)]
    if not card.card_id:
        card.card_id = sha1(f"card|{_card_merge_key(card)}".encode("utf-8")).hexdigest()[:12]


def _is_meaningful_tracking_text(value: str) -> bool:
    normalized = _normalize_text(value)
    return bool(normalized and not normalized.isdigit() and len(normalized) >= 4)


def _load_curation() -> dict[str, Any]:
    default = {
        "updated_at": "",
        "suppressed_refs": {},
        "title_overrides": {},
        "entity_alias_overrides": {},
    }
    if not config.KANBAN_CURATION_PATH.exists():
        return default
    try:
        payload = json.loads(config.KANBAN_CURATION_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default
    default["suppressed_refs"] = payload.get("suppressed_refs", {}) or {}
    default["title_overrides"] = payload.get("title_overrides", {}) or {}
    default["entity_alias_overrides"] = payload.get("entity_alias_overrides", {}) or {}
    default["updated_at"] = payload.get("updated_at", "") or ""
    return default


def _save_curation(curation: dict[str, Any]) -> None:
    curation["updated_at"] = datetime.now().isoformat(timespec="seconds")
    config.KANBAN_CURATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    config.KANBAN_CURATION_PATH.write_text(
        json.dumps(curation, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _load_previous_cards() -> list[KanbanCard]:
    if not config.KANBAN_TASKS_PATH.exists():
        return []
    try:
        payload = json.loads(config.KANBAN_TASKS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    cards: list[KanbanCard] = []
    for raw in payload.get("cards", []):
        card = KanbanCard(
            title=str(raw.get("title", "")).strip(),
            column=str(raw.get("column", "Backlog")),
            priority=str(raw.get("priority", "medium")),
            source_kind=str(raw.get("source_kind", "unknown")),
            source_file=str(raw.get("source_file", "")),
            source_excerpt=str(raw.get("source_excerpt", "")),
            notes=[str(value) for value in raw.get("notes", []) if value],
            entities=[str(value) for value in raw.get("entities", []) if value],
            entity_links=[str(value) for value in raw.get("entity_links", []) if value],
            tags=[str(value) for value in raw.get("tags", []) if value],
            needs_research=bool(raw.get("needs_research", False)),
            tavily_query=raw.get("tavily_query"),
            card_id=str(raw.get("card_id", "")),
            tracking_refs=[str(value) for value in raw.get("tracking_refs", []) if value],
        )
        _ensure_card_identity(card)
        cards.append(card)
    return cards


def _parse_board_cards(path: Path) -> list[BoardCardState]:
    if not path.exists():
        return []

    cards: list[BoardCardState] = []
    current_column: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        header = re.match(r"^##\s+(.*)$", raw_line)
        if header:
            current_column = header.group(1).strip()
            continue
        if current_column is None:
            continue

        line = raw_line.strip()
        match = _CARD_LINE_RE.match(line)
        if not match:
            continue

        body = match.group("body")
        card_id: str | None = None
        meta_match = _INLINE_META_RE.search(body)
        if meta_match:
            card_id = meta_match.group("card_id")
        title = _strip_generated_suffix(body)
        if not title:
            continue
        cards.append(BoardCardState(
            title=title,
            column=current_column,
            card_id=card_id,
            checked=match.group("checked").lower() == "x",
        ))
    return cards


def _match_previous_card(
    board_card: BoardCardState,
    previous_cards: list[KanbanCard],
    previous_by_id: dict[str, KanbanCard],
) -> KanbanCard | None:
    if board_card.card_id and board_card.card_id in previous_by_id:
        return previous_by_id[board_card.card_id]

    board_key = _normalize_board_title(board_card.title)
    exact = [card for card in previous_cards if _card_merge_key(card) == board_key]
    if len(exact) == 1:
        return exact[0]

    best_card: KanbanCard | None = None
    best_score = 0.0
    for previous in previous_cards:
        score = SequenceMatcher(None, board_key, _card_merge_key(previous)).ratio()
        if previous.column == board_card.column:
            score += 0.05
        if score > best_score:
            best_score = score
            best_card = previous
    if best_card and best_score >= 0.72:
        return best_card
    return None


def _is_suppressed(card: KanbanCard, curation: dict[str, Any]) -> bool:
    suppressed = curation.get("suppressed_refs", {})
    return any(ref in suppressed for ref in card.tracking_refs)


def _record_entity_alias_override(curation: dict[str, Any], previous_title: str, new_title: str) -> None:
    previous_subject = _extract_entity_subject(previous_title)
    new_subject = _extract_entity_subject(new_title)
    if not previous_subject or not new_subject:
        return
    if _normalize_text(previous_subject) == _normalize_text(new_subject):
        return

    alias_key = _normalize_text(previous_subject)
    overrides = curation.setdefault("entity_alias_overrides", {})
    entry = overrides.setdefault(alias_key, {
        "name": new_subject,
        "type": "person",
        "aliases": [],
    })
    if len(new_subject) >= len(str(entry.get("name", ""))):
        entry["name"] = new_subject
    for alias in {previous_subject, new_subject, *entry.get("aliases", [])}:
        if alias and alias not in entry["aliases"]:
            entry["aliases"].append(alias)


def _extract_entity_subject(title: str) -> str | None:
    subject = re.sub(r"^\[[^\]]+\]\s*", "", _strip_generated_suffix(title)).strip()
    patterns = [
        r"^(?:reply to|reach out to|follow up with|waiting for|resolve thread with|create peer note for)\s+(?P<subject>.+)$",
    ]
    for pattern in patterns:
        match = re.match(pattern, subject, flags=re.IGNORECASE)
        if not match:
            continue
        candidate = _clean_text(match.group("subject"))
        candidate = re.sub(r"\s+\([^)]*\)$", "", candidate).strip()
        if _looks_entityish_subject(candidate):
            return candidate
    return None


def _looks_entityish_subject(value: str) -> bool:
    tokens = re.findall(r"[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż0-9-]+", value)
    if not 1 <= len(tokens) <= 5:
        return False
    return len(value.strip()) <= 60


def _apply_curation_aliases_to_ner_cache(
    curation: dict[str, Any],
    on_status: Callable[[str], None] | None = None,
) -> None:
    overrides = curation.get("entity_alias_overrides", {})
    if not overrides:
        return

    try:
        from thoughtmap.analysis.ner import load_cache, normalize_entity, save_cache
    except Exception:
        return

    cache = load_cache()
    changed = False
    today = datetime.now().strftime("%Y-%m-%d")

    for alias_key, override in overrides.items():
        target_name = str(override.get("name", "")).strip()
        if not target_name:
            continue
        target_normalized = normalize_entity(target_name)
        if not target_normalized:
            continue

        existing = cache.get(target_normalized)
        if existing is None:
            existing = {
                "name": target_name,
                "type": str(override.get("type", "person")) or "person",
                "aliases": [],
                "normalized": target_normalized,
                "first_seen": today,
            }
            cache[target_normalized] = existing
            changed = True

        if len(target_name) >= len(str(existing.get("name", ""))):
            existing["name"] = target_name
        aliases = list(existing.get("aliases", []))
        for alias in override.get("aliases", []):
            if alias and alias not in aliases:
                aliases.append(alias)
                changed = True
        existing["aliases"] = aliases

        legacy = cache.get(alias_key)
        if legacy and legacy.get("type") and not existing.get("type"):
            existing["type"] = legacy["type"]

    if not changed:
        return

    save_cache(cache)
    if on_status:
        on_status(f"  Persisted {len(overrides)} manual entity alias overrides into NER cache")


def _sync_entity_registry_from_curation(
    curation: dict[str, Any],
    on_status: Callable[[str], None] | None = None,
) -> None:
    try:
        from thoughtmap.analysis.curation import write_entity_curation_board
        from thoughtmap.analysis.entities.registry import (
            apply_kanban_alias_overrides_to_registry,
            ensure_entity_registry,
            save_entity_registry,
        )
    except Exception:
        return

    overrides = curation.get("entity_alias_overrides", {})
    registry = ensure_entity_registry()
    updated = apply_kanban_alias_overrides_to_registry(registry, overrides)
    save_entity_registry(updated)
    write_entity_curation_board(updated)
    if on_status:
        on_status(
            f"  Synced {len(overrides)} manual alias overrides into entity_registry.json "
            f"and {config.ENTITY_CURATION_BOARD_PATH.name}"
        )


def _slugify(value: str) -> str:
    slug = _normalize_text(value).replace(" ", "-")
    slug = re.sub(r"-+", "-", slug)
    return slug or "entity"


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.lower().strip())
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^a-z0-9\s-]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def _clean_text(value: str) -> str:
    text = value.replace("**", "")
    text = text.replace("~~", "")
    text = re.sub(r"\[\[(.*?)\]\]", r"\1", text)
    text = re.sub(r"\[(.*?)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" -–—")


def _render_kanban_board(cards: list[KanbanCard]) -> str:
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")
    columns = ["Inbox", "Backlog", "Research", "Waiting", "Blocked", "Done"]
    by_column: dict[str, list[KanbanCard]] = {column: [] for column in columns}
    for card in cards:
        by_column.setdefault(card.column, []).append(card)

    lines = [
        "---",
        "kanban-plugin: board",
        "type: kanban-generated",
        "status: active",
        "source: thoughtmap",
        f"generated: {generated}",
        "---",
        "",
        "%% Generated by ThoughtMap. Treat this as an intake board, not the manual source of truth.",
        "Manual curation rules:",
        "- delete a card to suppress this exact tracked thread on future reruns",
        "- rename a card to keep your corrected display title on future reruns",
        "- leave %%tm:id=...%% comments intact; they let ThoughtMap preserve your edits",
        "%%",
        "",
    ]

    for column in columns:
        lines.append(f"## {column}")
        lines.append("")
        for card in by_column.get(column, []):
            suffix = f" {' '.join(dict.fromkeys(card.tags))}" if card.tags else ""
            lines.append(f"- [ ] {card.title}{suffix} %%tm:id={card.card_id}%%")
        lines.append("")

    return "\n".join(lines)