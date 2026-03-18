# TODOS — Mini Shazam

## P1 — High Priority

### [ ] Write basic test suite
**What:** Unit tests for fingerprint pipeline and recognizer.
**Why:** Zero test coverage means regressions go undetected.
**Effort:** M
**Where to start:** `tests/` folder, test `fingerprint_audio()` with a sine wave and assert hash count > 0. Test `recognize()` with empty input returns None.

### [ ] Add file size limit on upload
**What:** Reject audio files > 50 MB in Streamlit Add Song page.
**Why:** Large files cause long blocking indexing and potential OOM.
**Effort:** S
**Where to start:** `streamlit_app.py` — check `file.size` before saving.

---

## P2 — Medium Priority

### [ ] "Test recognition" flow after indexing
**What:** After indexing a song, offer a button to immediately test recognition by re-uploading a snippet.
**Why:** Gives instant confidence that the song was indexed correctly.
**Effort:** M
**Where to start:** After `st.success()` in Add Song page, add a `st.button("Test recognition")` that switches to Recognize tab.

### [ ] Deduplication on index
**What:** Before indexing, check if a song with the same title+artist already exists in DB. Warn user if so.
**Why:** Currently easy to double-index the same song, polluting the DB with duplicate fingerprints.
**Effort:** S
**Where to start:** `database.py` — add `find_song(title, artist)` query. Call before `insert_song()`.

### [ ] Deploy to Streamlit Cloud
**What:** Push to GitHub and connect to Streamlit Cloud for public URL.
**Why:** Right now only runs locally. Streamlit Cloud is free for public repos.
**Effort:** S
**Depends on:** Git repo must be on GitHub first.

---

## P3 — Nice to Have

### [ ] MusicBrainz metadata lookup
**What:** After indexing from filename, optionally fetch proper metadata (title, artist, album, cover art) from MusicBrainz API.
**Why:** Filenames are often wrong or incomplete.
**Effort:** L

### [ ] Accuracy benchmark script
**What:** Script that indexes N songs, then queries each with a snippet, reports recognition rate %.
**Why:** No way to know if algorithm changes improve or hurt accuracy.
**Effort:** M

### [ ] Clear history button
**What:** Button in History tab to wipe recognition history.
**Effort:** S
**Where to start:** Add `DELETE FROM history` function in `database.py`.
