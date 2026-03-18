"""
Mini Shazam – Streamlit App
Run locally : streamlit run streamlit_app.py
Deploy      : Streamlit Cloud (connect GitHub repo)
"""

import html
import os
import sys
import tempfile

import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

from src.database import (
    init_db, list_songs, song_count,
    insert_song, insert_fingerprints, delete_song,
    log_recognition, get_history,
)
from src.fingerprint import fingerprint_audio
from src.recorder   import load_audio_file
from src.recognizer import recognize_from_audio

# ── Bootstrap ────────────────────────────────────────────────────────────────

init_db()

st.set_page_config(
    page_title="Mini Shazam",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Minimal custom CSS ───────────────────────────────────────────────────────

st.markdown("""
<style>
/* Result card */
.result-box {
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    margin-top: 1.5rem;
    animation: fadeIn 0.2s ease-out;
}
.result-title  { font-size: 1.8rem; font-weight: 700; margin-bottom: .25rem; }
.result-artist { font-size: 1.1rem; color: #aaa; }
.result-score  { font-size: .85rem; color: #888; margin-top: .5rem; }

/* Page fade-in */
@keyframes fadeIn { from { opacity: 0.5; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
section[data-testid="stMainBlockContainer"] > div { animation: fadeIn 0.15s ease-out; }

/* Library row separator */
div[data-testid="stHorizontalBlock"] {
    border-bottom: 1px solid rgba(255, 255, 255, 0.07);
    padding-bottom: 0.4rem;
    padding-top: 0.4rem;
}

/* Sidebar */
section[data-testid="stSidebar"] { min-width: 200px; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar navigation ───────────────────────────────────────────────────────

with st.sidebar:
    st.title("🎵 Mini Shazam")
    st.markdown("---")
    page = st.radio(
        "Menu",
        ["🎤  Recognize", "📚  Library", "➕  Add Song", "🕘  History"],
        label_visibility="collapsed",
        key="nav_page",
    )

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 – RECOGNIZE
# ══════════════════════════════════════════════════════════════════════════════

if page == "🎤  Recognize":
    st.title("Identify a Song")
    st.caption("Record a snippet of any song in your library — I'll tell you what it is.")

    total = song_count()
    if total == 0:
        st.warning("No songs in the library yet. Go to **Add Song** to index some music first!")
    else:
        songs = list_songs()
        song_names = " · ".join(f"**{s['title']}**" for s in songs)
        st.info(
            f"This MVP has **{total} songs** in its library: {song_names}.\n\n"
            f"Play one of these songs near your mic and Mini Shazam will identify it. "
            f"*(For reference, Shazam has over 11 million songs — this is just a demo!)*"
        )

    st.markdown("---")

    st.caption("Tip: play music loudly near your mic, 5–10 seconds is enough.")
    audio_value = st.audio_input("Press record, then play music near your mic")

    if audio_value:
        with st.spinner("Extracting audio fingerprint… (this takes 2–5 s)"):
            suffix = ".wav"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(audio_value.read())
                tmp_path = tmp.name

            result = None
            error  = None
            try:
                audio  = load_audio_file(tmp_path)
                result = recognize_from_audio(audio)
            except Exception as exc:
                error = str(exc)
            finally:
                os.unlink(tmp_path)

        if error:
            st.error(f"Processing error: {error}")

        elif result:
            # Confidence badge — bright colors for readability on dark bg
            score = result['score']
            if score >= 30:
                conf_label, conf_color = "High", "#4caf50"
            elif score >= 15:
                conf_label, conf_color = "Medium", "#ffc107"
            else:
                conf_label, conf_color = "Low", "#ff7043"

            title_q  = result['title'].replace(' ', '+')
            artist_q = (result['artist'] or '').replace(' ', '+')
            query_q  = f"{title_q}+{artist_q}" if artist_q else title_q
            yt_url   = f"https://www.youtube.com/results?search_query={query_q}"
            sp_url   = f"https://open.spotify.com/search/{query_q}"

            st.markdown(f"""
            <div class="result-box" style="background:#1a3a1a; border: 2px solid #2d6a2d;">
                <div style="font-size:2.5rem;">✅</div>
                <div class="result-title">{html.escape(result['title'])}</div>
                <div class="result-artist">{html.escape(result['artist'] or 'Unknown artist')}</div>
                <div class="result-score">{score} matching fingerprints &nbsp;|&nbsp;
                    <span style="color:{conf_color}; font-weight:600;">Confidence: {conf_label}</span>
                </div>
                <div style="margin-top:1rem;">
                    <a href="{yt_url}" target="_blank"
                       style="margin-right:1rem; color:#ff8080; text-decoration:none; font-weight:600;">
                       ▶ YouTube
                    </a>
                    <a href="{sp_url}" target="_blank"
                       style="color:#7ed9a5; text-decoration:none; font-weight:600;">
                       ♪ Spotify
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)

            log_recognition(result['song_id'], result['title'], result['artist'])

        else:
            st.markdown("""
            <div class="result-box" style="background:#2a2a1a; border: 2px solid #6a6a2d;">
                <div style="font-size:2.5rem;">🤔</div>
                <div class="result-title">No match found</div>
                <div class="result-artist">Try playing louder or closer to the mic</div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 – LIBRARY
# ══════════════════════════════════════════════════════════════════════════════

elif page == "📚  Library":
    st.title("Song Library")

    songs = list_songs()
    total = song_count()

    col1, col2 = st.columns([3, 1])
    col1.caption(f"{total} song{'s' if total != 1 else ''} indexed")
    if col2.button("+ Add Song"):
        st.session_state["nav_page"] = "➕  Add Song"
        st.rerun()

    st.markdown("---")

    if not songs:
        st.info("No songs yet. Head over to **Add Song** to get started!")
    else:
        for song in songs:
            cols = st.columns([3, 2, 1])
            cols[0].markdown(f"**{song['title']}**")
            cols[1].markdown(f"<span style='color:#888'>{song['artist'] or '—'}</span>", unsafe_allow_html=True)
            if cols[2].button("🗑️", key=f"del_{song['id']}", help=f"Delete {song['title']}"):
                delete_song(song['id'])
                st.toast(f"'{song['title']}' deleted.")
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 – HISTORY
# ══════════════════════════════════════════════════════════════════════════════

elif page == "🕘  History":
    st.title("Recognition History")
    st.caption("Every song you've successfully identified.")
    st.markdown("---")

    rows = get_history()
    if not rows:
        st.info("No recognitions yet — go to **Recognize** to identify a song!")
    else:
        for row in rows:
            cols = st.columns([3, 2, 2])
            cols[0].markdown(f"**{row['title']}**")
            cols[1].markdown(f"<span style='color:#888'>{row['artist'] or '—'}</span>", unsafe_allow_html=True)
            cols[2].markdown(f"<span style='color:#555; font-size:.85rem'>{row['recognized_at']}</span>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 – ADD SONG
# ══════════════════════════════════════════════════════════════════════════════

elif page == "➕  Add Song":
    st.title("Add Song")
    st.caption("Upload an audio file to index it into the recognition library.")
    st.markdown("---")

    with st.form("add_song_form", clear_on_submit=True):
        title  = st.text_input("Song title *")
        artist = st.text_input("Artist")
        file   = st.file_uploader(
            "Audio file *",
            type=["mp3", "wav", "flac", "m4a", "ogg"],
            help="Any common audio format works",
        )
        submitted = st.form_submit_button("Index Song", use_container_width=True)

    if submitted:
        if not title:
            st.error("Title is required.")
        elif file is None:
            st.error("Please choose an audio file.")
        else:
            songs_dir = os.path.join(os.path.dirname(__file__), "songs")
            os.makedirs(songs_dir, exist_ok=True)
            save_path = os.path.join(songs_dir, os.path.basename(file.name))

            with open(save_path, "wb") as f:
                f.write(file.read())

            with st.spinner(f"Indexing '{title}'… (this may take 10–30 s for long files)"):
                song_id = None
                try:
                    audio   = load_audio_file(save_path)
                    song_id = insert_song(title=title, artist=artist, file=save_path)
                    hashes  = fingerprint_audio(audio, song_id=song_id)
                    insert_fingerprints(hashes)
                    st.success(f"**{title}** indexed! ({len(hashes):,} fingerprints generated)")
                    st.balloons()
                except Exception as exc:
                    if song_id is not None:
                        delete_song(song_id)
                    st.error(f"Error during indexing: {exc}")
