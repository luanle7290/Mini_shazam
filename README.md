# Mini Shazam

A song recognition app built with Python — identifies songs from short audio clips using audio fingerprinting, similar to how Shazam works.

## How it works

1. Songs are indexed by computing a spectrogram, finding local peaks, and storing SHA1 hashes of peak pairs in a SQLite database
2. To recognize a clip, the same fingerprinting runs on the query audio
3. Matching uses time-coherence voting: the song with the most consistent time-offset delta wins

## Quick start

```bash
pip install -r requirements.txt

# Add songs to songs/ folder, then bulk-index them:
python index_all.py

# Launch the web UI:
streamlit run streamlit_app.py
```

## Web UI pages

| Page | Description |
|---|---|
| Recognize | Record a clip and identify the song |
| Library | View and manage indexed songs |
| Add Song | Upload an audio file to index |
| History | Log of previously recognized songs |

## CLI (optional)

```bash
python main.py index  <file> <title> [artist]   # index one song
python main.py query  <file>                     # recognize from file
python main.py listen [seconds]                  # record mic and recognize
python main.py list                              # list all indexed songs
```

## Tech stack

- **Streamlit** — web UI
- **librosa / scipy** — audio loading and spectrogram
- **SQLite** — fingerprint database (`database/fingerprints.db`)
- **sounddevice** — microphone recording (CLI only)

## Project structure

```
streamlit_app.py     # Streamlit web UI
main.py              # CLI entry point
index_all.py         # Bulk indexer for songs/ folder
src/
  fingerprint.py     # Spectrogram → peaks → SHA1 hashes
  recognizer.py      # Time-coherence matching
  database.py        # SQLite CRUD
  recorder.py        # Audio loading + mic recording
database/            # SQLite DB lives here (gitignored)
songs/               # Put your MP3/WAV files here (gitignored)
```
