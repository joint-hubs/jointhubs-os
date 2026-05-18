"""Named entity extraction for ThoughtMap clusters and chunks."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Callable

import Levenshtein
import numpy as np
import requests

import thoughtmap.config as config
from thoughtmap.core.cluster import ThoughtMapResult

_SPACY_NLP = None

_TYPE_DIRS = {
    "person": "person",
    "organization": "organization",
    "project": "project",
    "tool": "tool",
    "location": "location",
}

_STOP_WORDS = {
    "ai",
    "api",
    "app",
    "assistant",
    "brain",
    "calendar",
    "claude",
    "code",
    "copilot",
    "day",
    "demo",
    "document",
    "github",
    "google",
    "idea",
    "jointhubs",
    "meeting",
    "note",
    "notes",
    "obsidian",
    "ollama",
    "page",
    "project",
    "review",
    "task",
    "thoughtmap",
    "today",
    "vault",
    "vscode",
    "week",
    "wispr",
    "jointhubs-os",
}

_NOISY_ENTITY_TOKENS = {
    "action",
    "actions",
    "aggregated",
    "agreement",
    "analysis",
    "analiza",
    "analytics",
    "answer",
    "audience",
    "architecture",
    "agents",
    "arising",
    "author",
    "authors",
    "appendix",
    "any",
    "build",
    "based",
    "building",
    "can",
    "categories",
    "category",
    "candidates",
    "capital",
    "company",
    "configure",
    "context",
    "create",
    "current",
    "dashboard",
    "data",
    "decision",
    "decisions",
    "deps",
    "derivative",
    "development",
    "drafts",
    "document",
    "documentation",
    "economy",
    "execution",
    "file",
    "files",
    "fixed",
    "forecasting",
    "followup",
    "framework",
    "bug",
    "click",
    "cycles",
    "cycle",
    "generic",
    "developer",
    "ideas",
    "implementation",
    "improvements",
    "including",
    "integration",
    "interaction",
    "industry",
    "items",
    "knowledge",
    "lead",
    "learnings",
    "liability",
    "limited",
    "list",
    "model",
    "models",
    "manualne",
    "monitoring",
    "mozesz",
    "out",
    "outlines",
    "partnership",
    "pipeline",
    "planning",
    "prod",
    "project",
    "projects",
    "prompt",
    "primary",
    "privacy",
    "policy",
    "real-time",
    "remain",
    "report",
    "recruitment",
    "response",
    "review",
    "role",
    "rows",
    "section",
    "sections",
    "skills",
    "software",
    "stack",
    "standard",
    "status",
    "strategy",
    "steps",
    "summary",
    "system",
    "systems",
    "tasks",
    "templates",
    "technology",
    "testing",
    "timeline",
    "tracking",
    "audiences",
    "usage",
    "user",
    "users",
    "workspace",
    "without",
    "works",
    "workflow",
    "yes",
    "senior",
    "teraz",
    "odpowiedz",
    "odpowiedziec",
    "hosting",
    "pulldown",
    "banana",
    "auth",
    "cloud",
    "dev",
    "developers",
    "duration",
    "external",
    "field",
    "fields",
    "handoffs",
    "interaction",
    "initiative",
    "initiatives",
    "internal",
    "milestones",
    "needs",
    "new",
    "next",
    "owner",
    "option",
    "optional",
    "optionally",
    "path",
    "platform",
    "platforma",
    "pozycja",
    "post",
    "posts",
    "przygotowac",
    "rekomendacja",
    "from",
    "get",
    "helper",
    "helpers",
    "high",
    "low",
    "one",
    "request",
    "services",
    "setup",
    "specific",
    "spotkania",
    "target",
    "training",
    "wdrozenie",
    "wymagania",
    "zarzadzanie",
}

_CURRENCY_TOKENS = {"pln", "usd", "eur", "gbp"}

_FUNCTION_WORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "by",
    "dla",
    "for",
    "in",
    "is",
    "na",
    "not",
    "of",
    "on",
    "or",
    "oraz",
    "the",
    "to",
    "w",
    "with",
    "z",
}

_ACTION_LEADING_TOKENS = {
    "add",
    "apply",
    "build",
    "configure",
    "create",
    "document",
    "finish",
    "fix",
    "follow",
    "followup",
    "improve",
    "improved",
    "improvement",
    "merge",
    "migrate",
    "move",
    "pass",
    "pay",
    "record",
    "review",
    "schedule",
    "turn",
    "update",
    "updated",
    "upgrade",
    "write",
}

_CONTEXT_TRAILING_TOKENS = {
    "analysis",
    "brief",
    "context",
    "cycles",
    "email",
    "flow",
    "ideas",
    "initiatives",
    "logs",
    "milestones",
    "operations",
    "path",
    "plan",
    "regular",
    "review",
    "roadmap",
    "status",
    "summary",
    "tracker",
    "updated",
    "use",
    "user",
}

_TOOL_HINT_TOKENS = {
    "api",
    "apis",
    "bigquery",
    "ci",
    "cnn",
    "docker",
    "firebase",
    "github",
    "jira",
    "llms",
    "nlp",
    "oauth",
    "python",
    "rag",
    "react",
    "recharts",
    "render",
    "rtx",
    "scada",
    "toolkit",
}

_PERSON_PREFIX_TOKENS = {"dr", "mr", "mrs", "ms", "pan", "pani", "prof"}

_PERSON_BANNED_TOKENS = {
    "bench",
    "dzialalnosc",
    "entity",
    "fenix",
    "finance",
    "globallogic",
    "home",
    "intellectual",
    "jointhubs",
    "lanka",
    "loan",
    "looking",
    "lotus",
    "named",
    "neurohubs",
    "office",
    "ollama",
    "press",
    "privacy",
    "policy",
    "pov",
    "property",
    "react",
    "recognition",
    "rights",
    "router",
    "sri",
    "state",
    "university",
}

_BANNED_ENTITY_PHRASES = {
    "privacy policy",
    "skills based hiring",
    "target user s",
    "operations daily yyyy mm dd md",
    "optionally",
    "follow up art pov",
    "follow-up art pov",
    "internal user external helpers",
    "capital to execution flow 1",
    "daily summary timeline",
    "ai scoping organization",
    "mcp target audience primary",
    "unclear prompt concatenation before",
}

_TYPE_BANNED_ENTITY_PHRASES = {
    "person": {
        "bylby pan",
        "coca cola",
        "classification stanford medicine",
        "dynamic prices",
        "europie zachodniej",
        "europy srodkowej",
        "features poza",
        "geopolityka bliskiego wschodu",
        "mall group",
        "ministerstwo funduszy",
        "personalization capabilities",
        "tab koszty",
    },
    "organization": {
        "accept",
        "all ac",
        "animation",
        "bi tool",
        "branza it security",
        "changelog md",
        "clients",
        "community 1",
        "company intellectual property rights",
        "created",
        "dzis",
        "edtech media entertainment manufacturing",
        "explore cfo",
        "fazy monetyzacji faza 1",
        "fenix dev team fund",
        "fine tuning",
        "forecasting service",
        "forecasting service prognozy przyszlosci",
        "gdzie",
        "hero kpi band",
        "interpretacja kis",
        "international",
        "jct token economy integration",
        "jesli nie",
        "kpi",
        "kto",
        "kupuj",
        "mcp",
        "named entity recognition",
        "nda przypisywanie",
        "new feature exact",
        "nie",
        "organization planning 13",
        "poc",
        "research publications peer reviewed",
        "team",
        "time log",
        "timelog",
        "total dsu",
        "total",
        "urls",
        "usprawnienie poc",
        "visual",
    },
    "project": {
        "business",
        "inbox",
        "jhubs",
        "jointhubs os",
        "pitch",
        "proof of itself",
        "search",
    },
    "location": {
        "agent",
        "agents",
        "allowed",
        "allow",
        "analiza",
        "art",
        "auth patterns l3",
        "auto empty",
        "benchmarks",
        "best",
        "brakuje",
        "bufor",
        "budzetowy",
        "cel",
        "cycles",
        "date",
        "daily",
        "demand",
        "decyzje",
        "developer",
        "equipment",
        "earnings",
        "expands",
        "fenixem",
        "frontend",
        "functional",
        "growth",
        "industry specific",
        "jakie",
        "knowledgegraphclient",
        "koszty",
        "laczenie",
        "manualne",
        "machine",
        "monitoring",
        "mozesz",
        "opens",
        "optymalizacja",
        "outlines",
        "partnerstwo wskm wymiana danych",
        "procurement",
        "projektowanie",
        "pozycja",
        "przygotowac",
        "push",
        "salary",
        "rekomendacja",
        "rozbudowa",
        "spotkania",
        "stopa",
        "textarea",
        "techcrunch",
        "total",
        "tooltips",
        "transactions",
        "twoja",
        "twojej",
        "wdrozenie",
        "wymagania",
        "wysoka",
        "wypacona",
        "wycena p",
        "zarzadzanie",
        "zmiana",
        "zyski",
        "zysk",
    },
}

_NOISE_SOURCE_NAMES = {
    "api",
    "authors",
    "changelog",
    "content",
    "contributing",
    "copying",
    "developing",
    "key-concepts",
    "key-concepts-2",
    "license",
    "readme",
    "security",
    "threat_model",
}


@dataclass
class Entity:
    name: str
    type: str
    aliases: list[str]
    normalized: str
    cluster_ids: list[int]
    source_files: list[str]
    mention_count: int
    summary: str
    first_seen: str
    boundaries: str = ""
    area_context: str = ""
    distinctive_signature: str = ""
    chunk_indices: list[int] = field(default_factory=list, repr=False)
    cluster_mentions: dict[int, int] = field(default_factory=dict, repr=False)
    cluster_labels: dict[int, str] = field(default_factory=dict, repr=False)


def load_cache() -> dict[str, dict]:
    """Load the entity cache from disk."""
    if not config.NER_CACHE_FILE.exists():
        return {}

    try:
        return json.loads(config.NER_CACHE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_cache(cache: dict[str, dict]) -> None:
    """Persist the entity cache atomically."""
    config.NER_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", delete=False, encoding="utf-8", dir=config.NER_CACHE_FILE.parent) as handle:
        json.dump(cache, handle, indent=2, ensure_ascii=False)
        temp_path = Path(handle.name)
    temp_path.replace(config.NER_CACHE_FILE)


def normalize_entity(name: str) -> str:
    """Normalize an entity name for matching and deduplication."""
    normalized = unicodedata.normalize("NFKD", name.lower().strip())
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^a-z0-9\s-]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def _canonical_entity_phrase(name: str) -> str:
    canonicalized = normalize_entity(name).replace("-", " ")
    canonicalized = re.sub(r"\s+", " ", canonicalized)
    return canonicalized.strip()


def _normalized_entity_terms(name: str) -> list[str]:
    return [term for term in _canonical_entity_phrase(name).split() if term]


def _is_type_banned_phrase(name: str, entity_type: str) -> bool:
    normalized = _canonical_entity_phrase(name)
    return normalized in _TYPE_BANNED_ENTITY_PHRASES.get(entity_type, set())


def _slugify(name: str) -> str:
    slug = normalize_entity(name).replace(" ", "-")
    slug = re.sub(r"-+", "-", slug)
    return slug or "entity"


def _display_source_file(source_file: str) -> str:
    if source_file.startswith("wispr:"):
        return source_file

    try:
        return Path(source_file).resolve().relative_to(config.REPO_ROOT).as_posix()
    except Exception:
        return source_file.replace("\\", "/")


def _coerce_date(value: str | None) -> str:
    if not value:
        return datetime.now().strftime("%Y-%m-%d")
    return value[:10]


def _entity_type_from_spacy(label: str) -> str | None:
    label_upper = label.upper()
    if label_upper in {"PERSON", "PER"}:
        return "person"
    if label_upper == "ORG":
        return "organization"
    if label_upper in {"GPE", "LOC", "FAC"}:
        return "location"
    if label_upper == "PRODUCT":
        return "tool"
    return None


def _sanitize_candidate_name(name: str, entity_type: str) -> str:
    candidate = re.sub(r"\s+", " ", name.replace("\n", " ")).strip()
    candidate = re.sub(r"\]\(https?://\S+", "", candidate)
    candidate = re.sub(r"https?://\S+", "", candidate)
    candidate = re.sub(r"^[\W_]+", "", candidate)
    candidate = candidate.strip("-–—:;,.!?/\\|[]{}()<>'\"")
    if not candidate:
        return ""

    tokens = candidate.split()
    if tokens:
        first_token = normalize_entity(tokens[0])
        if first_token in _PERSON_PREFIX_TOKENS:
            trimmed = " ".join(tokens[1:])
            if _is_person_name_shape(trimmed):
                return trimmed
    if entity_type == "person" and len(tokens) >= 3:
        trailing = normalize_entity(tokens[-1])
        trimmed = " ".join(tokens[:-1])
        if trailing in _CONTEXT_TRAILING_TOKENS and _is_person_name_shape(trimmed):
            return trimmed

    return candidate


def _resolve_entity_type(name: str, entity_type: str) -> str:
    if _is_person_name_shape(name):
        return "person"

    tokens = _normalized_entity_terms(name)
    if entity_type in {"organization", "location"} and any(token in _TOOL_HINT_TOKENS for token in tokens):
        return "tool"
    return entity_type


def _has_entity_signal(name: str, entity_type: str) -> bool:
    tokens = [token.strip("-_/.,()[]{}:;!?\"'") for token in name.split() if token.strip("-_/.,()[]{}:;!?\"'")]
    if not tokens or len(tokens) > 4:
        return False

    uppercase_tokens = 0
    digit_tokens = 0
    for token in tokens:
        if any(ch.isdigit() for ch in token):
            digit_tokens += 1
        if token[:1].isupper() or token.isupper():
            uppercase_tokens += 1

    if entity_type == "person":
        return len(tokens) >= 2 and uppercase_tokens >= 2
    if entity_type == "organization":
        required_uppercase = 2 if len(tokens) > 1 else 1
        return uppercase_tokens >= required_uppercase or digit_tokens >= 1
    if entity_type == "location":
        required_uppercase = 2 if len(tokens) > 1 else 1
        return uppercase_tokens >= required_uppercase
    if entity_type == "tool":
        return uppercase_tokens >= 1 or digit_tokens >= 1
    if entity_type == "project":
        return uppercase_tokens >= 1 or digit_tokens >= 1
    return False


def _is_person_name_shape(name: str) -> bool:
    tokens = re.findall(r"[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż-]+", name)
    if not 2 <= len(tokens) <= 3:
        return False
    normalized_tokens = [normalize_entity(token) for token in tokens]
    if any(
        token in _PERSON_BANNED_TOKENS
        or token in _NOISY_ENTITY_TOKENS
        or token in _TOOL_HINT_TOKENS
        or token in _STOP_WORDS
        or token in _CONTEXT_TRAILING_TOKENS
        for token in normalized_tokens
    ):
        return False
    for token in tokens:
        if not re.fullmatch(r"[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż-]+", token):
            return False
    return True


def _is_valid_candidate(name: str, entity_type: str) -> bool:
    candidate = name.strip()
    normalized = normalize_entity(candidate)
    canonicalized = _canonical_entity_phrase(candidate)
    tokens = _normalized_entity_terms(candidate)
    alpha_tokens = re.findall(r"[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż-]+", candidate)
    if not normalized or len(normalized) < 2:
        return False
    if normalized in _STOP_WORDS:
        return False
    if canonicalized in _BANNED_ENTITY_PHRASES:
        return False
    if _is_type_banned_phrase(candidate, entity_type):
        return False
    if len(normalized) > 60:
        return False
    if len(normalized.split()) == 1 and len(normalized) < 3:
        return False
    if entity_type in {"person", "organization", "location"} and candidate[:1].isdigit():
        return False
    if entity_type == "person" and any(ch.isdigit() for ch in candidate):
        return False
    if entity_type != "project" and len(alpha_tokens) >= 2 and all(token.isupper() for token in alpha_tokens):
        return False
    if tokens and tokens[0] in _ACTION_LEADING_TOKENS and entity_type != "project":
        return False
    if len(tokens) > 1 and tokens[-1] in _CONTEXT_TRAILING_TOKENS and entity_type != "project":
        return False
    if entity_type in {"organization", "location"} and any(token in _NOISY_ENTITY_TOKENS for token in tokens):
        meaningful_non_noisy = [token for token in tokens if token not in _STOP_WORDS and token not in _NOISY_ENTITY_TOKENS]
        if len(meaningful_non_noisy) < 2:
            return False
    if any(token in _FUNCTION_WORDS for token in tokens):
        return False
    if any(token in _CURRENCY_TOKENS for token in tokens):
        return False
    meaningful_tokens = [token for token in tokens if token not in _STOP_WORDS and token not in _NOISY_ENTITY_TOKENS]
    if not meaningful_tokens:
        return False
    if entity_type == "person":
        if any(token in _NOISY_ENTITY_TOKENS for token in tokens):
            return False
        if not _is_person_name_shape(candidate):
            return False
    if entity_type == "organization" and len(tokens) > 1 and len(meaningful_tokens) < 2:
        return False
    if entity_type == "location" and len(tokens) > 1 and len(meaningful_tokens) < 2:
        return False
    if entity_type == "organization" and len(tokens) == 1 and candidate.isupper() and len(candidate) > 5:
        return False
    if not _has_entity_signal(candidate, entity_type):
        return False
    return True


def _build_alias_pattern(alias: str) -> str:
    normalized = normalize_entity(alias)
    if not normalized:
        return ""

    tokens = [re.escape(token) for token in normalized.split() if token]
    if not tokens:
        return ""
    if len(tokens) == 1:
        return rf"(?<!\w){tokens[0]}(?!\w)"
    token_pattern = r"\s+".join(tokens)
    return rf"(?<!\w){token_pattern}(?!\w)"


def build_regex_patterns(cache: dict[str, dict]) -> dict[str, re.Pattern[str]]:
    """Build regex patterns for cached entities and aliases."""
    patterns: dict[str, re.Pattern[str]] = {}
    for normalized, data in cache.items():
        candidate_name = _sanitize_candidate_name(data.get("name", ""), data.get("type", "person"))
        candidate_type = _resolve_entity_type(candidate_name, data.get("type", "person"))
        if not candidate_name or not _is_valid_candidate(candidate_name, candidate_type):
            continue

        aliases = [candidate_name, *data.get("aliases", [])]
        alias_patterns = []
        for alias in aliases:
            alias_name = _sanitize_candidate_name(alias, candidate_type)
            if not alias_name or not _is_valid_candidate(alias_name, candidate_type):
                continue
            pattern = _build_alias_pattern(alias_name)
            if pattern:
                alias_patterns.append(pattern)
        if not alias_patterns:
            continue
        combined = "|".join(sorted(set(alias_patterns), key=len, reverse=True))
        patterns[normalized] = re.compile(combined, re.IGNORECASE)
    return patterns


def regex_scan(chunks: list[dict], patterns: dict[str, re.Pattern[str]]) -> dict[str, list[int]]:
    """Find cached entities in chunk text using regex patterns."""
    matches: dict[str, set[int]] = {normalized: set() for normalized in patterns}
    if not patterns:
        return {}

    for index, chunk in enumerate(chunks):
        normalized_text = normalize_entity(chunk.get("text", ""))
        if not normalized_text:
            continue
        for normalized, pattern in patterns.items():
            if pattern.search(normalized_text):
                matches[normalized].add(index)

    return {normalized: sorted(indices) for normalized, indices in matches.items() if indices}


def _load_spacy_model():
    global _SPACY_NLP
    if _SPACY_NLP is None:
        import spacy

        try:
            _SPACY_NLP = spacy.load(config.NER_SPACY_MODEL)
        except OSError as exc:
            raise RuntimeError(
                f"spaCy model '{config.NER_SPACY_MODEL}' is not installed. Rebuild the ThoughtMap image or run 'python -m spacy download {config.NER_SPACY_MODEL}'."
            ) from exc
    return _SPACY_NLP


def spacy_extract(chunks: list[dict], already_matched: set[int]) -> list[Entity]:
    """Extract new entities from chunks not already covered by the cache."""
    nlp = _load_spacy_model()
    candidates: dict[tuple[str, str], Entity] = {}

    pending_indices = [index for index in range(len(chunks)) if index not in already_matched]
    texts = [chunks[index].get("text", "") for index in pending_indices]

    for chunk_index, doc in zip(pending_indices, nlp.pipe(texts, batch_size=32)):
        chunk = chunks[chunk_index]
        for ent in doc.ents:
            entity_type = _entity_type_from_spacy(ent.label_)
            if entity_type is None:
                continue

            candidate_name = _sanitize_candidate_name(ent.text, entity_type)
            if not candidate_name:
                continue
            entity_type = _resolve_entity_type(candidate_name, entity_type)
            if not _is_valid_candidate(candidate_name, entity_type):
                continue

            normalized = normalize_entity(candidate_name)
            key = (normalized, entity_type)
            existing = candidates.get(key)
            if existing is None:
                candidates[key] = Entity(
                    name=candidate_name,
                    type=entity_type,
                    aliases=[candidate_name],
                    normalized=normalized,
                    cluster_ids=[],
                    source_files=[],
                    mention_count=0,
                    summary="",
                    first_seen=_coerce_date(chunk.get("timestamp")),
                    chunk_indices=[chunk_index],
                )
            else:
                existing.aliases.append(candidate_name)
                existing.chunk_indices.append(chunk_index)
                existing.first_seen = min(existing.first_seen, _coerce_date(chunk.get("timestamp")))

    return list(candidates.values())


def _extract_project_entities(chunks: list[dict]) -> list[Entity]:
    """Create project entities from structured metadata and project paths."""
    candidates: dict[str, Entity] = {}

    for index, chunk in enumerate(chunks):
        project_names: set[str] = set()

        project_tag = chunk.get("project_tag")
        if project_tag:
            project_names.add(project_tag)

        source_file = chunk.get("source_file", "").replace("\\", "/")
        match = re.search(r"/Projects/([^/]+)/", "/" + source_file)
        if match:
            project_names.add(match.group(1))

        for raw_name in project_names:
            display_name = " ".join(part.capitalize() for part in re.split(r"[-_\s]+", raw_name) if part)
            normalized = normalize_entity(display_name)
            if not normalized:
                continue
            if normalized in _STOP_WORDS or _is_type_banned_phrase(display_name, "project"):
                continue
            entity = candidates.get(normalized)
            if entity is None:
                candidates[normalized] = Entity(
                    name=display_name,
                    type="project",
                    aliases=[raw_name, display_name],
                    normalized=normalized,
                    cluster_ids=[],
                    source_files=[],
                    mention_count=0,
                    summary="",
                    first_seen=_coerce_date(chunk.get("timestamp")),
                    chunk_indices=[index],
                )
            else:
                entity.aliases.extend([raw_name, display_name])
                entity.chunk_indices.append(index)
                entity.first_seen = min(entity.first_seen, _coerce_date(chunk.get("timestamp")))

    return list(candidates.values())


def _is_same_entity(left: Entity, right: Entity) -> bool:
    if left.type != right.type:
        return False
    if left.normalized == right.normalized:
        return True
    if left.normalized in right.normalized or right.normalized in left.normalized:
        return True
    distance = Levenshtein.distance(left.normalized, right.normalized)
    max_len = max(len(left.normalized), len(right.normalized), 1)
    return (distance / max_len) < 0.15


def _merge_entity(target: Entity, source: Entity) -> None:
    if len(source.name) > len(target.name):
        target.name = source.name
    if len(source.normalized) > len(target.normalized):
        target.normalized = source.normalized
    target.aliases.extend(alias for alias in source.aliases if alias)
    target.chunk_indices.extend(source.chunk_indices)
    target.first_seen = min(target.first_seen, source.first_seen)


def _entity_bucket_keys(normalized: str) -> set[str]:
    tokens = [token for token in normalized.split() if token]
    if not tokens:
        return {normalized}

    keys = {token for token in tokens if len(token) >= 3}
    compact = normalized.replace(" ", "")
    if compact:
        keys.add(compact[:4])
        keys.add(compact[-4:])
    return keys or {normalized}


def deduplicate(entities: list[Entity]) -> list[Entity]:
    """Merge entity candidates that refer to the same underlying entity."""
    exact_matches: dict[tuple[str, str], Entity] = {}

    for candidate in entities:
        if not candidate.normalized:
            continue

        key = (candidate.type, candidate.normalized)
        existing = exact_matches.get(key)
        if existing is None:
            exact_matches[key] = candidate
        else:
            _merge_entity(existing, candidate)

    merged: list[Entity] = []
    buckets: dict[tuple[str, str], list[Entity]] = {}

    for candidate in exact_matches.values():
        possible_matches: dict[int, Entity] = {}
        for bucket_key in _entity_bucket_keys(candidate.normalized):
            for existing in buckets.get((candidate.type, bucket_key), []):
                possible_matches[id(existing)] = existing

        target = None
        for existing in possible_matches.values():
            if _is_same_entity(existing, candidate):
                target = existing
                break

        if target is None:
            merged.append(candidate)
            targets_to_register = [candidate]
        else:
            _merge_entity(target, candidate)
            targets_to_register = [target]

        for entity in targets_to_register:
            for bucket_key in _entity_bucket_keys(candidate.normalized):
                bucket = buckets.setdefault((entity.type, bucket_key), [])
                if entity not in bucket:
                    bucket.append(entity)

    for entity in merged:
        entity.aliases = sorted(set(alias for alias in entity.aliases if alias), key=str.lower)
        entity.chunk_indices = sorted(set(entity.chunk_indices))

    return merged


def _load_kanban_entity_alias_overrides() -> dict[str, dict]:
    """Load manual entity overrides harvested from ThoughtMap Intake curation."""
    path = getattr(config, "KANBAN_CURATION_PATH", None)
    if path is None or not path.exists():
        return {}

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload.get("entity_alias_overrides", {}) or {}


def _apply_manual_entity_overrides(entities: list[Entity]) -> list[Entity]:
    """Promote user-curated intake renames into canonical entity names and aliases."""
    try:
        from thoughtmap.analysis.entities.registry import (
            apply_kanban_alias_overrides_to_registry,
            load_entity_registry,
        )
        from thoughtmap.analysis.entities.resolve import apply_manual_entity_decisions
    except Exception:
        return entities

    registry = load_entity_registry()
    registry = apply_kanban_alias_overrides_to_registry(registry, _load_kanban_entity_alias_overrides())
    return apply_manual_entity_decisions(entities, registry)


def _combined_alias_pattern(entity: Entity) -> re.Pattern[str]:
    alias_patterns = []
    for alias in [entity.name, *entity.aliases]:
        pattern = _build_alias_pattern(alias)
        if pattern:
            alias_patterns.append(pattern)
    combined = "|".join(sorted(set(alias_patterns), key=len, reverse=True))
    return re.compile(combined, re.IGNORECASE)


def _is_noise_source_file(source_file: str) -> bool:
    normalized = source_file.replace("\\", "/").lower()
    stem = Path(normalized).stem.lower().replace(" ", "-")
    return (
        "/node_modules/" in normalized
        or stem in _NOISE_SOURCE_NAMES
        or "license" in stem
        or "changelog" in stem
    )


_ENTITY_BLOCKLIST = {
    # Generic English words commonly misclassified as entities
    "learning", "patterns", "availability", "enhanced", "trainers",
    "purple", "parties", "legs", "expand", "credit memo", "vocabulary choices",
    "tool", "read more", "read-more", "click here", "submit", "next", "back",
    "spent", "carbs", "party", "sun", "goes", "solid", "switches", "prepares",
    "lighthouse", "typography scale", "best balance", "cash burn", "cash risk",
    "go solo", "canva pro canva", "central task lists", "ai-assisted survey unlike",
    # Generic Polish words commonly misclassified
    "aplikacja", "konfiguracja", "konkurencja", "zastosowanie", "strone", "stronę",
    "zaprojektowania", "agenci", "ciebie", "klaster", "rozwiazanie", "warstwa",
    "siec", "srednie-wysokie", "średnie-wysokie", "fazy", "bookmark", "currency",
    "serwis i niezawodność", "razem", "suma", "objaśnienia",
    "tak", "poprzednia", "poprawki", "twoje", "domyslny", "prawnik",
    "izolacja", "obszar", "sesja 1", "fazy 1",
    "wyjaśnienie", "normalizacja", "oferta", "opcjonalnie", "profil",
    # Job titles / role abbreviations (not organisations)
    "cto", "ceo", "cfo", "coo", "cmo", "vp",
    # Generic technical / financial abbreviations (not organisations or products)
    "vram", "pos", "prd", "fte", "roa", "roe", "roi", "ica", "sft", "dlc",
    "cagr", "lfl", "akt", "edf", "nim", "pit", "rsi", "eps", "etf",
    "raft", "pyspark", "dockerfile", "middleware",
    # Code tokens / cloud regions
    "europe-central2", "us-east-1", "us-west-2",
    # Multi-word descriptive phrases commonly misclassified
    "expand organization section", "data quality & metadata",
    "cta inna kreacja", "mne best practices", "epic crud",
    "it infrastructure composition",
    # Descriptive phrases misclassified as person/org/location
    "kontekst jeśli", "monthly goals", "expected clarification questions",
    "polityki regionalnej", "daniel deliverable", "kto-co-jak-gdzie stwórz",
    "differentiator", "crm product owner", "podjęcie zadania dev",
}

# Pattern: entity name looks like a pure abbreviation body (2-5 uppercase letters)
# but is NOT a known real entity. Checked separately with a whitelist.
_ABBREVIATION_WHITELIST = {
    "aws", "ncbr", "ipcei", "kghm", "ksef", "rodo", "apac", "icml",
    "esop", "saas", "nasa", "ieee", "nato", "opec", "gdpr",
    "adhd", "eeg", "nif", "bci", "gtm", "nlp", "cnn", "llm",
}


def _is_noise_entity(entity: Entity) -> bool:
    tokens = [token for token in entity.normalized.split() if token]
    if not tokens:
        return True
    if _is_type_banned_phrase(entity.name, entity.type):
        return True
    if all(token in _NOISY_ENTITY_TOKENS or token in _STOP_WORDS for token in tokens):
        return True
    if entity.source_files and all(_is_noise_source_file(source_file) for source_file in entity.source_files):
        return True
    # Blocklist check (case-insensitive on full name)
    name_lower = entity.name.lower().strip()
    if name_lower in _ENTITY_BLOCKLIST:
        return True
    # Strip markdown/url artifacts
    if re.search(r"[#\[\](){}<>]", entity.name):
        return True
    # Pure abbreviation check: 2-5 uppercase letters not in whitelist
    stripped = re.sub(r"[^a-zA-Z]", "", entity.name)
    if stripped.isupper() and 2 <= len(stripped) <= 5 and stripped.lower() not in _ABBREVIATION_WHITELIST:
        return True
    return False


def _llm_validate_entities(
    entities: list[Entity],
    chunks: list[dict],
    on_status: Callable[[str], None] | None = None,
) -> list[Entity]:
    """Use LLM to filter out false-positive entities in batches."""
    BATCH_SIZE = 10
    validated: list[Entity] = []

    for batch_start in range(0, len(entities), BATCH_SIZE):
        batch = entities[batch_start:batch_start + BATCH_SIZE]
        descriptions: list[str] = []

        for i, entity in enumerate(batch):
            snippets: list[str] = []
            for idx in entity.chunk_indices[:3]:
                if idx < len(chunks):
                    text = chunks[idx].get("text", "").strip()[:200]
                    if text:
                        snippets.append(text)

            cluster_names = [
                entity.cluster_labels.get(cid, f"Cluster {cid}")
                for cid in entity.cluster_ids[:3]
            ]
            descriptions.append(
                f"{i + 1}. \"{entity.name}\" (type: {entity.type}, "
                f"mentions: {entity.mention_count}, "
                f"clusters: {', '.join(cluster_names) or 'none'})\n"
                f"   Context: {' | '.join(snippets) if snippets else '(no context)'}"
            )

        prompt = (
            "You are validating named entities extracted from a personal knowledge base.\n"
            "The extraction was done automatically and contains MANY false positives.\n"
            "For each entity decide:\n"
            "- KEEP — this is a genuine, specific named entity of the stated type\n"
            "- RETYPE <new_type> — genuine entity but wrong type "
            "(person / organization / location / tool / project)\n"
            "- REJECT — not a real named entity\n\n"
            "REJECT if any of these apply:\n"
            "- Common Polish or English word (even if capitalised): nouns, verbs, "
            "adjectives, adverbs, pronouns, prepositions\n"
            "  Examples of words to REJECT: Agenci, Availability, Bookmark, Currency, "
            "Ciebie, Klaster, Rozwiazanie, Warstwa, Siec, Strone, Tool\n"
            "- Generic technical/IT term: Dockerfile, PySpark, Render, Middleware, API, "
            "Framework, Pipeline, Cluster, Query, Schema, Cache\n"
            "- UI text or navigation label: Read More, Click Here, Submit, Next, Back\n"
            "- Code token, variable name, or Docker image tag\n"
            "- Multi-word descriptive phrase rather than a proper name\n"
            "- Abbreviation that is not a well-known organisation or product\n"
            "- Category/concept rather than a specific named thing\n\n"
            "KEEP only specific proper nouns: real people, real companies, real cities/"
            "countries, well-known software products, or named projects.\n"
            "When in doubt, REJECT.\n\n"
            "Entities:\n\n"
            + "\n\n".join(descriptions)
            + "\n\nRespond with ONLY one line per entity:\n"
            "<number>. KEEP|RETYPE <type>|REJECT\n"
        )

        try:
            resp = requests.post(
                f"{config.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": config.CONDENSE_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "think": False,
                    "options": {"temperature": 0.1, "num_predict": 200},
                },
                timeout=120,
            )
            resp.raise_for_status()
            result_text = resp.json().get("response", "")

            decisions: dict[int, str] = {}
            retype_map: dict[int, str] = {}
            for line in result_text.strip().splitlines():
                m = re.match(
                    r"(\d+)\.\s*(KEEP|REJECT|RETYPE\s+(\w+))",
                    line.strip(),
                    re.IGNORECASE,
                )
                if m:
                    idx = int(m.group(1)) - 1
                    action = m.group(2).upper()
                    if action.startswith("RETYPE") and m.group(3):
                        retype_map[idx] = m.group(3).lower()
                    decisions[idx] = "RETYPE" if action.startswith("RETYPE") else action

            for i, entity in enumerate(batch):
                decision = decisions.get(i, "KEEP")  # default keep if LLM skipped
                if decision == "REJECT":
                    continue
                if decision == "RETYPE":
                    new_type = retype_map.get(i)
                    if new_type and new_type in _TYPE_DIRS:
                        entity.type = new_type
                validated.append(entity)
        except Exception:
            validated.extend(batch)  # on failure, keep everything

        if on_status:
            on_status(
                f"  LLM validated {min(batch_start + BATCH_SIZE, len(entities))}"
                f"/{len(entities)} entities"
            )

    return validated


def _enrich_entities(entities: list[Entity], result: ThoughtMapResult, items: list[dict]) -> None:
    cluster_lookup: dict[int, int] = {}
    cluster_labels: dict[int, str] = {}
    normalized_texts = [normalize_entity(item.get("text", "")) for item in items]

    for cluster in result.clusters:
        cluster_labels[cluster.cluster_id] = cluster.label
        for index in cluster.member_indices:
            cluster_lookup[index] = cluster.cluster_id

    for entity in entities:
        pattern = _combined_alias_pattern(entity)
        entity.source_files = []
        entity.cluster_ids = []
        entity.cluster_mentions = {}
        entity.cluster_labels = {}
        mention_count = 0

        for chunk_index in entity.chunk_indices:
            if chunk_index >= len(items):
                continue

            item = items[chunk_index]
            source_file = _display_source_file(item.get("source_file", ""))
            if source_file and source_file not in entity.source_files:
                entity.source_files.append(source_file)

            cluster_id = cluster_lookup.get(chunk_index)
            if cluster_id is not None:
                entity.cluster_mentions[cluster_id] = entity.cluster_mentions.get(cluster_id, 0) + 1
                entity.cluster_labels[cluster_id] = cluster_labels.get(cluster_id, f"Cluster {cluster_id}")

            occurrences = len(pattern.findall(normalized_texts[chunk_index]))
            mention_count += max(occurrences, 1)

        entity.cluster_ids = sorted(entity.cluster_mentions)
        entity.source_files.sort()
        entity.mention_count = mention_count
        if not entity.first_seen:
            entity.first_seen = datetime.now().strftime("%Y-%m-%d")


def _parse_summary_boundaries(text: str) -> tuple[str, str]:
    """Split an LLM response into (summary, boundaries) sections."""
    # Try to find explicit section markers
    # Match "TOPIC BOUNDARIES" preceded by optional ##, **, or __ formatting
    _HDR = r"(?:#{0,3}\s*|\*{0,2}|_{0,2})"
    boundaries_marker = re.search(
        r"(?:^|\n)\s*" + _HDR + r"(?:TOPIC BOUNDARIES|Topic Boundaries|Boundaries)" + _HDR + r"[:\s]*\n",
        text,
        re.IGNORECASE,
    )
    if boundaries_marker:
        summary = text[: boundaries_marker.start()].strip()
        boundaries = text[boundaries_marker.end() :].strip()
        # Strip leading "SUMMARY" / "## SUMMARY" / "**SUMMARY**" header if present
        summary = re.sub(r"^(?:#{0,3}\s*|\*{0,2}|_{0,2})(?:SUMMARY|Summary)(?:\*{0,2}|_{0,2})[:\s]*\n?", "", summary, flags=re.IGNORECASE).strip()
        # Strip leading header from boundaries text (shouldn't remain, but just in case)
        boundaries = re.sub(r"^(?:#{0,3}\s*|\*{0,2}|_{0,2})(?:TOPIC BOUNDARIES|Topic Boundaries|Boundaries)(?:\*{0,2}|_{0,2})[:\s]*\n?", "", boundaries, flags=re.IGNORECASE).strip()
        return summary, boundaries

    # Fall back: look for CENTER/EDGES markers
    center_match = re.search(r"(?:^|\n)\s*[-*]*\s*(?:CENTER|Center)[:\s]", text, re.IGNORECASE)
    if center_match:
        summary = text[: center_match.start()].strip()
        boundaries = text[center_match.start() :].strip()
        summary = re.sub(r"^(?:#{0,3}\s*|\*{0,2}|_{0,2})(?:SUMMARY|Summary)(?:\*{0,2}|_{0,2})[:\s]*\n?", "", summary, flags=re.IGNORECASE).strip()
        return summary, boundaries

    # No clear split — everything is summary
    clean = re.sub(r"^(?:#{0,3}\s*|\*{0,2}|_{0,2})(?:SUMMARY|Summary)(?:\*{0,2}|_{0,2})[:\s]*\n?", "", text, flags=re.IGNORECASE).strip()
    return clean, ""


def summarize_entity(entity: Entity, chunks: list[dict]) -> tuple[str, str]:
    """Summarize an entity with topic boundary analysis using Ollama.

    Returns (summary, boundaries) tuple.
    """
    fragments = []
    for chunk_index in entity.chunk_indices[:5]:
        if chunk_index >= len(chunks):
            continue
        text = chunks[chunk_index].get("text", "").strip()
        if text:
            fragments.append(text[:300])

    representative_mentions = "\n---\n".join(fragments)

    cluster_info: list[str] = []
    for cid in entity.cluster_ids:
        label = entity.cluster_labels.get(cid, f"Cluster {cid}")
        mentions = entity.cluster_mentions.get(cid, 0)
        cluster_info.append(f"- {label} ({mentions} mentions)")
    cluster_section = "\n".join(cluster_info[:10]) or "(no cluster data)"

    prompt = (
        "You are analyzing a named entity found across a personal knowledge base.\n\n"
        f"Entity: {entity.name} (type: {entity.type})\n"
        f"Found in {entity.mention_count} text fragments across "
        f"{len(entity.cluster_ids)} topic clusters.\n\n"
        f"Cluster distribution:\n{cluster_section}\n\n"
        f"Representative mentions:\n{representative_mentions}\n\n"
        "Write TWO sections:\n\n"
        "SUMMARY\n"
        "A concise 2-3 sentence summary of this entity's role and context "
        "in the knowledge base. Include relationships to projects, people, "
        "or topics if apparent.\n\n"
        "TOPIC BOUNDARIES\n"
        "Describe the range of this entity's relevance:\n"
        "- CENTER: What are the core themes where this entity is most central? "
        "(1-2 sentences)\n"
        "- EDGES: What are the peripheral or surprising connections? Where does "
        "this entity appear less frequently but still meaningfully? "
        "(1-2 sentences)\n\n"
        "Write in the same language as the fragments. Use plain text."
    )

    try:
        response = requests.post(
            f"{config.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": config.CONDENSE_MODEL,
                "prompt": prompt,
                "stream": False,
                "think": False,
                "options": {"temperature": 0.3, "num_predict": 400},
            },
            timeout=120,
        )
        response.raise_for_status()
        raw = response.json().get("response", "").strip()
        return _parse_summary_boundaries(raw)
    except Exception as exc:
        return f"(Summary generation failed: {exc})", ""


def _fallback_summary(entity: Entity) -> tuple[str, str]:
    labels = [entity.cluster_labels.get(cluster_id, f"Cluster {cluster_id}") for cluster_id in entity.cluster_ids[:3]]
    summary_parts = [
        f"This {entity.type} appears {entity.mention_count} times across {len(entity.cluster_ids)} clusters."
    ]
    if labels:
        summary_parts.append(f"It is most associated with {', '.join(labels)}.")
    if entity.source_files:
        summary_parts.append(f"Source files include {', '.join(entity.source_files[:3])}.")
    summary = " ".join(summary_parts)

    if labels:
        boundaries = (
            f"CENTER: Primarily relevant to {labels[0]}."
        )
        if len(labels) > 1:
            boundaries += f"\nEDGES: Also appears in {', '.join(labels[1:])}."
    else:
        boundaries = ""

    return summary, boundaries


def _cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two vectors."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def compute_area_contexts(
    entities: list[Entity],
    all_embeddings: np.ndarray,
    result: ThoughtMapResult,
) -> None:
    """Compute embedding-space area context for each entity in-place."""
    if all_embeddings is None or len(all_embeddings) == 0:
        return

    total_chunks = len(all_embeddings)
    global_centroid = np.mean(all_embeddings, axis=0)

    # Precompute cluster centroids (use HD centroid if available, else compute from members)
    cluster_data: list[tuple[int, str, np.ndarray]] = []
    for cluster in result.clusters:
        if cluster.centroid_hd:
            cluster_data.append(
                (cluster.cluster_id, cluster.label, np.array(cluster.centroid_hd))
            )
        elif cluster.member_indices:
            valid = [i for i in cluster.member_indices if i < total_chunks]
            if valid:
                centroid = np.mean(all_embeddings[valid], axis=0)
                cluster_data.append((cluster.cluster_id, cluster.label, centroid))

    for entity in entities:
        indices = [i for i in entity.chunk_indices if i < total_chunks]
        if not indices:
            continue

        entity_embs = all_embeddings[indices]
        entity_centroid = np.mean(entity_embs, axis=0)

        # Coverage: fraction of chunks this entity spans
        coverage_pct = len(indices) / total_chunks * 100

        # Focus (spread): mean cosine distance of entity chunks to entity centroid
        entity_dists = [1.0 - _cosine_sim(e, entity_centroid) for e in entity_embs]
        spread = float(np.mean(entity_dists)) if entity_dists else 0.0

        # Distinctiveness: cosine distance from entity center to global center
        distinctiveness = 1.0 - _cosine_sim(entity_centroid, global_centroid)

        # Cluster proximity ranking
        cluster_sims = [
            (cid, label, _cosine_sim(entity_centroid, centroid))
            for cid, label, centroid in cluster_data
        ]
        cluster_sims.sort(key=lambda x: x[2], reverse=True)

        # Focus interpretation
        if spread < 0.10:
            focus_label = "very tight"
        elif spread < 0.20:
            focus_label = "tight"
        elif spread < 0.35:
            focus_label = "moderate"
        else:
            focus_label = "broad"

        # Build text
        lines = [
            f"- **Coverage:** {len(indices):,}/{total_chunks:,} chunks ({coverage_pct:.1f}% of knowledge base)",
            f"- **Focus:** {spread:.3f} cosine σ ({focus_label})",
            f"- **Distinctiveness:** {distinctiveness:.3f} (distance from global center)",
        ]

        if cluster_sims:
            nearest = cluster_sims[:3]
            lines.append(
                "- **Nearest clusters:** "
                + ", ".join(f"{label} ({sim:.2f})" for _, label, sim in nearest)
            )
            if len(cluster_sims) > 3:
                farthest = cluster_sims[-2:]
                lines.append(
                    "- **Farthest clusters:** "
                    + ", ".join(f"{label} ({sim:.2f})" for _, label, sim in farthest)
                )

        entity.area_context = "\n".join(lines)

    # ── Distinctive Signatures via concept arithmetic + LLM ──
    # Only compute for entities that got area_context and have enough chunks
    sig_candidates = [
        e for e in entities
        if e.area_context and len([i for i in e.chunk_indices if i < total_chunks]) >= 2
    ]
    # Limit to top N by mention count to avoid excessive LLM calls
    sig_candidates.sort(key=lambda e: e.mention_count, reverse=True)
    sig_candidates = sig_candidates[:config.NER_MAX_OLLAMA_SUMMARIES]

    for idx, entity in enumerate(sig_candidates):
        indices = [i for i in entity.chunk_indices if i < total_chunks]
        entity_embs = all_embeddings[indices]
        entity_centroid = np.mean(entity_embs, axis=0)

        # Concept arithmetic: what makes this entity distinctive vs global average
        diff_vector = entity_centroid - global_centroid
        diff_norm = np.linalg.norm(diff_vector)
        if diff_norm == 0:
            continue
        diff_unit = diff_vector / diff_norm

        # Find 3 chunks most aligned with the difference vector
        sims = np.array([
            float(np.dot(all_embeddings[i], diff_unit) / max(np.linalg.norm(all_embeddings[i]), 1e-9))
            for i in range(total_chunks)
        ])
        top3_indices = np.argsort(sims)[-3:][::-1]
        top3_texts = []
        for ci in top3_indices:
            text = result.items[ci].get("text", "") if ci < len(result.items) else ""
            top3_texts.append(text[:400])

        fragments = "\n---\n".join(
            f"Fragment {k+1}:\n{t}" for k, t in enumerate(top3_texts) if t
        )
        if not fragments:
            continue

        prompt = (
            "You are analyzing a named entity's distinctive presence in a personal knowledge base.\n\n"
            f"Entity: {entity.name} (type: {entity.type})\n\n"
            "The following text fragments were found using concept arithmetic — they represent "
            "the directions in embedding space that make this entity MOST DIFFERENT from the "
            "average content in the knowledge base. These fragments capture what is unique "
            "about this entity's thematic footprint.\n\n"
            f"{fragments}\n\n"
            "Based on these fragments, write a 2-3 sentence DISTINCTIVE SIGNATURE: "
            "What uniquely defines this entity's presence? What themes, roles, or connections "
            "make it stand out from everything else in the knowledge base? "
            "Be specific and concrete, not generic. "
            "Write in the same language as the fragments. Use plain text."
        )

        try:
            response = requests.post(
                f"{config.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": config.CONDENSE_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "think": False,
                    "options": {"temperature": 0.3, "num_predict": 200},
                },
                timeout=120,
            )
            response.raise_for_status()
            sig = response.json().get("response", "").strip()
            if sig:
                entity.distinctive_signature = sig
                print(f"  [{idx+1}/{len(sig_candidates)}] Signature: {entity.name}")
        except Exception as exc:
            print(f"  [{idx+1}/{len(sig_candidates)}] Signature failed for {entity.name}: {exc}")


def generate_entity_notes(entities: list[Entity], output_dir: Path) -> None:
    """Write per-entity notes plus a master index and JSON export."""
    output_dir.mkdir(parents=True, exist_ok=True)
    for subdir in _TYPE_DIRS.values():
        typed_dir = output_dir / subdir
        typed_dir.mkdir(parents=True, exist_ok=True)
        for stale_note in typed_dir.glob("*.md"):
            stale_note.unlink()

    generated_date = datetime.now().strftime("%Y-%m-%d")
    entity_payload = []
    counts_by_type = {entity_type: 0 for entity_type in _TYPE_DIRS}
    cluster_ids = set()

    for entity in sorted(entities, key=lambda item: (item.type, item.name.lower())):
        counts_by_type[entity.type] = counts_by_type.get(entity.type, 0) + 1
        cluster_ids.update(entity.cluster_ids)
        slug = _slugify(entity.name)
        note_path = output_dir / _TYPE_DIRS.get(entity.type, entity.type) / f"{slug}.md"

        cluster_lines = ["| Cluster | Label | Mentions |", "|---------|-------|----------|"]
        for cluster_id in entity.cluster_ids:
            label = entity.cluster_labels.get(cluster_id, f"Cluster {cluster_id}")
            mentions = entity.cluster_mentions.get(cluster_id, 0)
            cluster_lines.append(f"| {cluster_id} | {label} | {mentions} |")

        source_lines = [f"- {source_file}" for source_file in entity.source_files] or ["- (none)"]
        aliases = ", ".join(entity.aliases)
        note = [
            "---",
            "type: entity",
            f"entity_type: {entity.type}",
            f"name: {entity.name}",
            f"aliases: [{aliases}]" if aliases else "aliases: []",
            f"clusters: {entity.cluster_ids}",
            f"mentions: {entity.mention_count}",
            f"first_seen: {entity.first_seen}",
            f"generated: {generated_date}",
            "---",
            "",
            f"# {entity.name}",
            "",
            "## Summary",
            "",
            entity.summary or "(No summary generated)",
            "",
        ]
        if entity.boundaries:
            note.extend([
                "## Topic Boundaries",
                "",
                entity.boundaries,
                "",
            ])
        if entity.area_context:
            note.extend([
                "## Area Context",
                "",
                entity.area_context,
                "",
            ])
        if entity.distinctive_signature:
            note.extend([
                "## Distinctive Signature",
                "",
                entity.distinctive_signature,
                "",
            ])
        note.extend([
            "## Appearances by Cluster",
            "",
            *cluster_lines,
            "",
            "## Source Files",
            "",
            *source_lines,
            "",
        ])
        note_path.write_text("\n".join(note), encoding="utf-8")

        payload = asdict(entity)
        payload.pop("chunk_indices", None)
        payload.pop("cluster_mentions", None)
        payload.pop("cluster_labels", None)
        payload.pop("area_context", None)
        payload.pop("distinctive_signature", None)
        entity_payload.append(payload)

    index_lines = [
        f"# ThoughtMap Entity Index - {generated_date}",
        "",
        "## Summary",
        f"- **{len(entities)}** entities discovered across **{len(cluster_ids)}** clusters",
        (
            f"- People: {counts_by_type.get('person', 0)} | Organizations: {counts_by_type.get('organization', 0)} | "
            f"Projects: {counts_by_type.get('project', 0)} | Tools: {counts_by_type.get('tool', 0)} | Locations: {counts_by_type.get('location', 0)}"
        ),
        "",
    ]

    for entity_type, label in [
        ("person", "People"),
        ("organization", "Organizations"),
        ("project", "Projects"),
        ("tool", "Tools"),
        ("location", "Locations"),
    ]:
        typed_entities = [entity for entity in entities if entity.type == entity_type]
        index_lines.extend([f"## {label}", "| Entity | Mentions | Clusters | Summary |", "|--------|----------|----------|---------|"])
        for entity in sorted(typed_entities, key=lambda item: item.mention_count, reverse=True):
            slug = _slugify(entity.name)
            summary = entity.summary.replace("\n", " ").strip()
            summary = summary[:100] + "..." if len(summary) > 100 else summary
            index_lines.append(
                f"| [[{_TYPE_DIRS.get(entity.type, entity.type)}/{slug}|{entity.name}]] | {entity.mention_count} | {len(entity.cluster_ids)} | {summary} |"
            )
        index_lines.append("")

    (output_dir / "_entity-index.md").write_text("\n".join(index_lines), encoding="utf-8")
    (output_dir.parent / "entities.json").write_text(
        json.dumps(entity_payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def extract_entities(
    result: ThoughtMapResult,
    items: list[dict],
    on_status: Callable[[str], None] | None = None,
    embeddings: list[list[float]] | None = None,
) -> list[Entity]:
    """Extract, summarize, and persist named entities for a ThoughtMap run."""

    def status(message: str) -> None:
        if on_status:
            on_status(message)

    if not items:
        return []

    status("  Loading entity cache...")
    cache = load_cache()

    status("  Regex scan for cached entities...")
    patterns = build_regex_patterns(cache)
    regex_matches = regex_scan(items, patterns)
    matched_indices = {index for indices in regex_matches.values() for index in indices}

    candidates: list[Entity] = []
    for normalized, chunk_indices in regex_matches.items():
        cached = cache.get(normalized, {})
        candidate_name = _sanitize_candidate_name(cached.get("name", normalized.title()), cached.get("type", "person"))
        candidate_type = _resolve_entity_type(candidate_name, cached.get("type", "person"))
        if not candidate_name or not _is_valid_candidate(candidate_name, candidate_type):
            continue
        candidates.append(
            Entity(
                name=candidate_name,
                type=candidate_type,
                aliases=cached.get("aliases", []),
                normalized=normalized,
                cluster_ids=[],
                source_files=[],
                mention_count=0,
                summary="",
                first_seen=cached.get("first_seen", datetime.now().strftime("%Y-%m-%d")),
                chunk_indices=chunk_indices,
            )
        )

    status("  spaCy extraction for new chunks...")
    candidates.extend(spacy_extract(items, matched_indices))

    status("  Heuristic project extraction...")
    candidates.extend(_extract_project_entities(items))

    status(f"  Deduplicating {len(candidates)} entity candidates...")
    entities = deduplicate(candidates)
    status("  Applying manual entity overrides from ThoughtMap Intake curation...")
    entities = _apply_manual_entity_overrides(entities)
    status(f"  Enriching {len(entities)} deduplicated entities...")
    _enrich_entities(entities, result, items)

    entities = [
        entity
        for entity in entities
        if entity.mention_count >= config.NER_MIN_MENTIONS and not _is_noise_entity(entity)
    ]
    entities.sort(key=lambda entity: (-entity.mention_count, entity.name.lower()))
    if config.NER_MAX_ENTITIES > 0:
        entities = entities[:config.NER_MAX_ENTITIES]
    status(f"  Retained {len(entities)} entities with >= {config.NER_MIN_MENTIONS} mentions")

    # LLM validation — filter false positives
    pre_validation_count = len(entities)
    status(f"  LLM validating {pre_validation_count} entities...")
    entities = _llm_validate_entities(entities, items, on_status=on_status)
    status(
        f"  LLM validation kept {len(entities)}/{pre_validation_count} entities"
    )

    if entities:
        ollama_summaries = min(len(entities), max(config.NER_MAX_OLLAMA_SUMMARIES, 0))
        status(f"  Summarizing {ollama_summaries}/{len(entities)} entities via Ollama...")
        for index, entity in enumerate(entities, start=1):
            if index <= ollama_summaries:
                entity.summary, entity.boundaries = summarize_entity(entity, items)
                if on_status and (index == ollama_summaries or index % 10 == 0):
                    on_status(f"  Summarized {index}/{ollama_summaries} entities via Ollama")
                continue
            entity.summary, entity.boundaries = _fallback_summary(entity)
        if on_status and len(entities) > ollama_summaries:
            on_status(f"  Wrote fallback summaries for {len(entities) - ollama_summaries} entities")

    # Embedding-space area context
    if embeddings is not None:
        status("  Computing area context from embeddings...")
        emb_array = np.array(embeddings) if not isinstance(embeddings, np.ndarray) else embeddings
        compute_area_contexts(entities, emb_array, result)

    status("  Writing entity notes and cache...")
    generate_entity_notes(entities, config.ENTITIES_DIR)

    updated_cache = dict(cache)
    for entity in entities:
        updated_cache[entity.normalized] = {
            "name": entity.name,
            "type": entity.type,
            "aliases": entity.aliases,
            "normalized": entity.normalized,
            "first_seen": entity.first_seen,
        }
    save_cache(updated_cache)

    return entities