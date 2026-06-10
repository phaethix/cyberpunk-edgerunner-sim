#!/usr/bin/env python3
"""HTML template loader.

This module handles loading the main HTML template and injecting game data
as inline JSON.
"""
import json
from pathlib import Path

from ..config.constants import WEB_DIR
from ..config.data import JOBS, CYBERWARE


def load_html_template() -> str:
    """Load *web/index.html* and inject game data as inline JSON.

    Returns:
        The HTML content with injected JSON data.
    """
    html_path = WEB_DIR / "index.html"
    html = html_path.read_text(encoding="utf-8")
    
    # Convert game data to JSON
    jobs_json = json.dumps(JOBS)
    cw_json = json.dumps(CYBERWARE)
    
    # Inject data into template
    html = html.replace("{{JOBS_JSON}}", jobs_json)
    html = html.replace("{{CW_JSON}}", cw_json)
    
    return html
