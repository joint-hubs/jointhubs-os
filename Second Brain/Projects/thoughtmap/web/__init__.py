"""ThoughtMap web entrypoints."""

from thoughtmap.web.server import serve, serve_static
from thoughtmap.web.viz import generate_viz

__all__ = ["generate_viz", "serve", "serve_static"]