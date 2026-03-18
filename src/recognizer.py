"""
Song Recognition Module
Matches query fingerprints against the database using time-coherence voting.
"""

import numpy as np
from collections import defaultdict


def recognize(hashes: list) -> dict | None:
    """
    Given query hashes [(hash, t_query), ...], find the best matching song.
    Returns dict with match info, or None if no confident match found.
    """
    if not hashes:
        return None

    hash_list = [h for h, _ in hashes]
    query_map = defaultdict(list)        # hash → [t_query, ...]
    for h, t in hashes:
        query_map[h].append(t)

    # Fetch candidates from DB
    db_rows = query_hashes_from_db(hash_list)
    if not db_rows:
        return None

    # For each candidate match, compute time difference histogram
    # A true match will have many pairs with the same Δt = t_db - t_query
    song_deltas = defaultdict(list)     # song_id → [delta, ...]

    for row in db_rows:
        h, t_db, song_id = row['hash'], row['offset'], row['song_id']
        for t_q in query_map.get(h, []):
            song_deltas[song_id].append(t_db - t_q)

    # Vote: best song is the one with the largest peak in its delta histogram
    best_song_id = None
    best_score   = 0

    for song_id, deltas in song_deltas.items():
        if not deltas:
            continue
        counts = np.bincount(np.array(deltas) - min(deltas))
        score = int(counts.max())
        if score > best_score:
            best_score   = score
            best_song_id = song_id

    if best_song_id is None or best_score < 5:   # minimum confidence
        return None

    # Retrieve song metadata for the winner
    for row in db_rows:
        if row['song_id'] == best_song_id:
            return {
                'song_id': best_song_id,
                'title':   row['title'],
                'artist':  row['artist'],
                'score':   best_score,
            }

    return None


def recognize_from_audio(audio: np.ndarray, sr: int = 22050) -> dict | None:
    """Full pipeline: raw audio → recognition result."""
    from .fingerprint import fingerprint_audio
    hashes = fingerprint_audio(audio, sr=sr)
    return recognize(hashes)


# ---------------------------------------------------------------------------
# Helper (avoids circular import by importing inside module)
# ---------------------------------------------------------------------------
def query_hashes_from_db(hash_list):
    """Thin wrapper so recognizer can call the DB query."""
    from .database import query_hashes as _q
    return _q(hash_list)
