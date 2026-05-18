"""ThoughtMap configuration — paths, thresholds, model settings.

All paths support environment variable overrides for Docker deployment.
"""

import os
from pathlib import Path

# Load .env from the thoughtmap project directory
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")

# ─── Repo paths ───
# thoughtmap lives at: <repo>/Second Brain/Projects/thoughtmap/
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUTPUT_DIR = Path(os.environ.get(
    "THOUGHTMAP_OUTPUT_DIR",
    str(REPO_ROOT / "Second Brain" / "Operations" / "thoughtmap-out"),
))
DATA_DIR = Path(os.environ.get(
    "THOUGHTMAP_DATA_DIR",
    str(Path(__file__).resolve().parent / "data"),
))
CURATION_DIR = DATA_DIR / "curation"
CHROMA_DIR = DATA_DIR / "chroma"
CACHE_DIR = DATA_DIR / "cache"


def _default_obsidian_vault() -> Path:
    return Path.home() / "Documents" / "Obsidian Vault"


def _default_wispr_db() -> Path:
    appdata_dir = os.environ.get("APPDATA")
    if appdata_dir:
        return Path(appdata_dir) / "Wispr Flow" / "flow.sqlite"
    return Path.home() / "AppData" / "Roaming" / "Wispr Flow" / "flow.sqlite"

# ─── Data source paths (env-overridable for Docker) ───
OBSIDIAN_VAULT = Path(os.environ.get(
    "THOUGHTMAP_OBSIDIAN_VAULT",
    str(_default_obsidian_vault()),
))
OBSIDIAN_DAILY = Path(os.environ.get(
    "THOUGHTMAP_OBSIDIAN_DAILY",
    str(OBSIDIAN_VAULT / "10. Operations" / "Daily"),
))
JOINTHUBS_DAILY = Path(os.environ.get(
    "THOUGHTMAP_JOINTHUBS_DAILY",
    str(REPO_ROOT / "Second Brain" / "Personal" / "daily"),
))
WISPR_DB = Path(os.environ.get(
    "THOUGHTMAP_WISPR_DB",
    str(_default_wispr_db()),
))
SECOND_BRAIN_DIR = Path(os.environ.get(
    "THOUGHTMAP_SECOND_BRAIN_DIR",
    str(REPO_ROOT / "Second Brain"),
))
REVIEWS_DIR = Path(os.environ.get(
    "THOUGHTMAP_REVIEWS_DIR",
    str(SECOND_BRAIN_DIR / "Operations" / "Reviews"),
))
PEERS_DIR = Path(os.environ.get(
    "THOUGHTMAP_PEERS_DIR",
    str(SECOND_BRAIN_DIR / "Personal" / "peers"),
))
KANBAN_DIR = Path(os.environ.get(
    "THOUGHTMAP_KANBAN_DIR",
    str(SECOND_BRAIN_DIR / "Operations" / "Kanban"),
))
KANBAN_INTAKE_PATH = Path(os.environ.get(
    "THOUGHTMAP_KANBAN_INTAKE_PATH",
    str(KANBAN_DIR / "ThoughtMap Intake.md"),
))
KANBAN_TASKS_PATH = Path(os.environ.get(
    "THOUGHTMAP_KANBAN_TASKS_PATH",
    str(OUTPUT_DIR / "kanban_tasks.json"),
))
KANBAN_CURATION_PATH = Path(os.environ.get(
    "THOUGHTMAP_KANBAN_CURATION_PATH",
    str(OUTPUT_DIR / "kanban_curation.json"),
))
ENTITY_REGISTRY_PATH = Path(os.environ.get(
    "THOUGHTMAP_ENTITY_REGISTRY_PATH",
    str(CURATION_DIR / "entity_registry.json"),
))
ENTITY_CURATION_BOARD_PATH = Path(os.environ.get(
    "THOUGHTMAP_ENTITY_CURATION_BOARD_PATH",
    str(KANBAN_DIR / "ThoughtMap Entity Curation.md"),
))
SEGMENT_CURATION_BOARD_PATH = Path(os.environ.get(
    "THOUGHTMAP_SEGMENT_CURATION_BOARD_PATH",
    str(KANBAN_DIR / "ThoughtMap Segment Curation.md"),
))
DOMAIN_CURATION_BOARD_PATH = Path(os.environ.get(
    "THOUGHTMAP_DOMAIN_CURATION_BOARD_PATH",
    str(KANBAN_DIR / "ThoughtMap Domain Curation.md"),
))
CURATION_REPORT_PATH = Path(os.environ.get(
    "THOUGHTMAP_CURATION_REPORT_PATH",
    str(OUTPUT_DIR / "curation_report.md"),
))

# ─── Date filter ───
MIN_YEAR = int(os.environ.get("THOUGHTMAP_MIN_YEAR", "2025"))

# ─── Second Brain extraction ───
# Folder names to skip when walking Second Brain (generated output, data, etc.)
SECOND_BRAIN_EXCLUDE_DIRS = {
    "graphify-out", "graphify-out-strategic", "graphify-strategic",
    "thoughtmap-out", "thoughtmap", "tmp", "data",
    ".obsidian", "automation-logs", "assets", "attachments",
    "budget-calculator", "demo", "cache",
    "node_modules", ".git", "dist", "build",
    ".venv", "venv", "env", "__pycache__", "site-packages",
    ".mypy_cache", ".pytest_cache",
}

# File name patterns to skip (case-insensitive stem matching)
SECOND_BRAIN_EXCLUDE_FILES = {
    "license", "licence", "contributing", "changelog",
    "code_of_conduct", "security", "authors",
}

# ─── Chunking ───
CHUNK_TARGET_TOKENS = 200       # Target chunk size in tokens
CHUNK_MIN_TOKENS = 40           # Minimum chunk size (smaller → discard)
CHUNK_OVERLAP_SENTENCES = 2     # Overlap between chunks in sentences
MERGE_SIMILARITY_THRESHOLD = 0.85  # Cosine similarity above which chunks merge

# ─── ThoughtAtom migration ───
# Keep the production pipeline on v1 chunking until ThoughtAtom quality has
# been reviewed through the prototype and curation workflow.
ENABLE_ATOM_PIPELINE = os.environ.get("THOUGHTMAP_ENABLE_ATOM_PIPELINE", "false").lower() == "true"

# ─── Embedding ───
EMBEDDING_PROVIDER = os.environ.get("EMBEDDING_PROVIDER", "ollama")  # "ollama" | "openai" | "google"

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_EMBEDDING_MODEL = os.environ.get("OLLAMA_EMBEDDING_MODEL", "qwen3-embedding:8b")
OLLAMA_EMBED_BATCH_SIZE = int(os.environ.get("THOUGHTMAP_OLLAMA_EMBED_BATCH_SIZE", "8"))
OLLAMA_EMBED_CONCURRENCY = int(os.environ.get("THOUGHTMAP_OLLAMA_EMBED_CONCURRENCY", "2"))

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_EMBEDDING_MODEL = os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
GOOGLE_EMBEDDING_MODEL = os.environ.get("GOOGLE_EMBEDDING_MODEL", "text-embedding-004")

# Legacy alias — resolved from provider
EMBEDDING_MODEL = {
    "ollama": OLLAMA_EMBEDDING_MODEL,
    "openai": OPENAI_EMBEDDING_MODEL,
    "google": GOOGLE_EMBEDDING_MODEL,
}.get(EMBEDDING_PROVIDER, OLLAMA_EMBEDDING_MODEL)

EMBEDDING_DIMENSIONS = int(os.environ.get("EMBEDDING_DIMENSIONS", "1024"))
VIZ_DIMENSIONS = 256            # Matryoshka truncation for visualization

# ─── Clustering ───
UMAP_N_NEIGHBORS = 15           # Higher = more global structure → fewer, broader clusters
UMAP_MIN_DIST = 0.05            # Tighter packing → cleaner cluster boundaries
UMAP_N_COMPONENTS = 2           # For visualization
UMAP_CLUSTER_COMPONENTS = 15    # Intermediate dims for HDBSCAN (lower = smoother, fewer clusters)
HDBSCAN_MIN_CLUSTER_SIZE = 30   # Smallest allowed cluster (higher = fewer, larger clusters)
HDBSCAN_MIN_SAMPLES = 10        # Density sensitivity (higher = stricter density requirement)
CLUSTER_MERGE_THRESHOLD = 0.94  # Cosine similarity above which cluster centroids get merged

# ─── Wispr Flow matching ───
WISPR_MATCH_THRESHOLD = 0.15    # Max normalized Levenshtein distance for match

# ─── Wispr Flow app → category mapping ───
APP_CATEGORIES = {
    "Code": "coding",
    "Terminal": "coding",
    "WindowsTerminal": "coding",
    "chrome": "browsing",
    "Chrome": "browsing",
    "Edge": "browsing",
    "Firefox": "browsing",
    "Obsidian": "note-taking",
    "Discord": "communication",
    "Slack": "communication",
    "WhatsApp": "communication",
    "Teams": "communication",
}
APP_DEFAULT_CATEGORY = "general"

# ─── Condensation ───
CONDENSE_MODEL = os.environ.get("THOUGHTMAP_CONDENSE_MODEL", "gemma4:e2b")
CONDENSE_EDGE_THRESHOLD = float(os.environ.get(
    "THOUGHTMAP_CONDENSE_EDGE_THRESHOLD", "0.70",
))  # cosine similarity — clusters above this get an edge in condensed graph
SUPER_CLUSTER_MIN_SIZE = int(os.environ.get(
    "THOUGHTMAP_SUPER_CLUSTER_MIN_SIZE", "3",
))  # minimum clusters per super-cluster
TOPICS_DIR = OUTPUT_DIR / "topics"

# ─── Semantic layers ───
GLOSSARY_PATH = Path(os.environ.get(
    "THOUGHTMAP_GLOSSARY_PATH",
    str(OUTPUT_DIR / "glossary.json"),
))
TAXONOMY_PATH = Path(os.environ.get(
    "THOUGHTMAP_TAXONOMY_PATH",
    str(OUTPUT_DIR / "taxonomy.json"),
))
TOPOLOGY_PATH = Path(os.environ.get(
    "THOUGHTMAP_TOPOLOGY_PATH",
    str(OUTPUT_DIR / "topology.json"),
))
ONTOLOGY_PATH = Path(os.environ.get(
    "THOUGHTMAP_ONTOLOGY_PATH",
    str(OUTPUT_DIR / "ontology.json"),
))
SEMANTIC_ENTITY_EDGE_MIN = float(os.environ.get(
    "THOUGHTMAP_SEMANTIC_ENTITY_EDGE_MIN",
    "0.34",
))
ONTOLOGY_ENTITY_EDGE_MIN = float(os.environ.get(
    "THOUGHTMAP_ONTOLOGY_ENTITY_EDGE_MIN",
    "0.42",
))
ONTOLOGY_MAX_TRIPLES = int(os.environ.get(
    "THOUGHTMAP_ONTOLOGY_MAX_TRIPLES",
    "400",
))

# ─── Named Entity Recognition ───
NER_ENABLED = os.environ.get("THOUGHTMAP_NER_ENABLED", "true").lower() == "true"
NER_SPACY_MODEL = os.environ.get("THOUGHTMAP_NER_SPACY_MODEL", "xx_ent_wiki_sm")
NER_MIN_MENTIONS = int(os.environ.get("THOUGHTMAP_NER_MIN_MENTIONS", "2"))
NER_MAX_ENTITIES = int(os.environ.get("THOUGHTMAP_NER_MAX_ENTITIES", "250"))
NER_MAX_OLLAMA_SUMMARIES = int(os.environ.get("THOUGHTMAP_NER_MAX_OLLAMA_SUMMARIES", "50"))
NER_ENTITY_TYPES = {"PERSON", "PER", "ORG", "GPE", "PRODUCT", "WORK_OF_ART", "LOC", "FAC"}
NER_CACHE_FILE = DATA_DIR / "entities_cache.json"
ENTITIES_DIR = OUTPUT_DIR / "entities"

# ─── ChromaDB ───
CHROMA_COLLECTION = "thoughtmap"

# ─── Server ───
SERVER_PORT = int(os.environ.get("THOUGHTMAP_PORT", "8585"))
