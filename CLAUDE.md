# Mini Shazam — Claude Instructions

## Project Overview
Mini Shazam is a song recognition app that uses audio fingerprinting to identify songs.
It has a Streamlit web UI and a Flask-based backend with a SQLite fingerprint database.

## Tech Stack
- Python + Streamlit (web UI)
- Flask (backend server with HTML templates)
- librosa + scipy (audio fingerprinting)
- SQLite (fingerprint database at `database/fingerprints.db`)
- Songs stored in `songs/` folder as MP3 files

## Project Structure
- `streamlit_app.py` — Streamlit web UI
- `app.py` / `main.py` — Flask backend
- `src/fingerprint.py` — audio fingerprinting logic
- `src/recognizer.py` — song recognition logic
- `src/database.py` — database operations
- `src/recorder.py` — audio recording
- `index_all.py` — script to index all songs in `songs/` folder
- `database/fingerprints.db` — SQLite fingerprint database
- `songs/` — MP3 song library

## gstack

Use gstack skills for all planning, code review, QA, and shipping tasks.

**IMPORTANT:** For all web browsing, use the `/browse` skill from gstack.
NEVER use `mcp__claude-in-chrome__*` tools — they are slow and unreliable compared to gstack's browser.

### Available Skills

| Skill | What it does |
|---|---|
| `/plan-ceo-review` | Product planning — review features, priorities, user value |
| `/plan-eng-review` | Engineering planning — review architecture, tech decisions |
| `/review` | Code review — catch bugs, security issues, best practices |
| `/ship` | Ship workflow — pre-flight checks before deploying |
| `/browse` | Headless browser — QA test the live app, verify deployments |
| `/qa` | Full QA — test + fix issues found |
| `/qa-only` | QA report only — find issues without auto-fixing |
| `/retro` | Retrospective — what went well, what to improve |

### Typical Workflow for This App
1. `/plan-eng-review` — before adding new features (e.g. new recognition algorithm)
2. `/review` — after writing code changes
3. `/qa` — test the Streamlit UI and recognition accuracy
4. `/ship` — before deploying
