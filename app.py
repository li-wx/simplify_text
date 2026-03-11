"""
Text Simplifier — Web application.

A Flask-based web GUI for the text simplification pipeline.
Supports model selection between o3-mini and GPT-4.1 mini.

Usage (local):
    uv run python app.py

Usage (Azure App Service):
    Deployed via gunicorn — see startup.txt.
"""

import os

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from simplifier import TextSimplifier

load_dotenv()

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Rate limiting (in-memory, resets on restart)
# ---------------------------------------------------------------------------
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[],
    storage_uri="memory://",
)


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429

# ---------------------------------------------------------------------------
# Model configurations
# ---------------------------------------------------------------------------
MODELS = {
    "o3-mini": {
        "deployment": "o3-mini",
        "api_version": "2024-12-01-preview",
        "debug_dir": "debug_output",
        "label": "o3-mini (reasoning)",
    },
    "gpt-4.1-mini": {
        "deployment": "gpt-4.1-mini",
        "api_version": "2024-12-01-preview",
        "debug_dir": "debug_output_4_1_mini",
        "label": "GPT-4.1 mini (recommended)",
    },
}

DEFAULT_MODEL = "gpt-4.1-mini"


def _get_simplifier(model_key: str) -> TextSimplifier:
    """Create a TextSimplifier for the chosen model."""
    cfg = MODELS.get(model_key, MODELS[DEFAULT_MODEL])
    return TextSimplifier(
        deployment=cfg["deployment"],
        api_version=cfg["api_version"],
        debug_dir=cfg["debug_dir"],
        save_debug=False,
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Render the main page."""
    return render_template("index.html", models=MODELS, default_model=DEFAULT_MODEL)


@app.route("/simplify", methods=["POST"])
@limiter.limit("15 per hour")
@limiter.limit("150 per day")
def simplify():
    """API endpoint — accepts JSON, returns simplified text."""
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()
    model_key = data.get("model", DEFAULT_MODEL)

    if not text:
        return jsonify({"error": "No text provided."}), 400

    if len(text) > 7000:
        return jsonify({"error": "Text exceeds the 7 000 character limit."}), 400

    try:
        simplifier = _get_simplifier(model_key)
        result = simplifier.simplify(text)
        return jsonify({"result": result, "model": model_key})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        return jsonify({"error": f"Simplification failed: {exc}"}), 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
