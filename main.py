"""
Mini Shazam - Main Entry Point
Usage:
    python main.py index  <audio_file> <title> [artist]   # add song to DB
    python main.py listen [duration_seconds]               # record & recognise
    python main.py query  <audio_file>                     # recognise from file
    python main.py list                                    # list indexed songs
"""

import sys
import os

# Ensure src/ is importable
sys.path.insert(0, os.path.dirname(__file__))

from src.database   import init_db, insert_song, insert_fingerprints, list_songs, song_count
from src.fingerprint import fingerprint_audio
from src.recorder    import load_audio_file, record
from src.recognizer  import recognize_from_audio


def cmd_index(args):
    if len(args) < 2:
        print("Usage: python main.py index <audio_file> <title> [artist]")
        return

    path, title = args[0], args[1]
    artist = args[2] if len(args) > 2 else ""

    if not os.path.isfile(path):
        print(f"File not found: {path}")
        return

    print(f"[Index] Loading '{title}' …")
    audio = load_audio_file(path)

    song_id = insert_song(title=title, artist=artist, file=path)
    print(f"[Index] Computing fingerprints for song_id={song_id} …")

    hashes = fingerprint_audio(audio, song_id=song_id)
    insert_fingerprints(hashes)

    print(f"[Index] Done — {len(hashes)} fingerprints stored.")


def cmd_listen(args):
    duration = float(args[0]) if args else 10.0
    audio = record(duration=duration)
    result = recognize_from_audio(audio)
    _print_result(result)


def cmd_query(args):
    if not args:
        print("Usage: python main.py query <audio_file>")
        return

    path = args[0]
    if not os.path.isfile(path):
        print(f"File not found: {path}")
        return

    print(f"[Query] Loading '{path}' …")
    audio = load_audio_file(path)
    result = recognize_from_audio(audio)
    _print_result(result)


def cmd_list(_args):
    songs = list_songs()
    if not songs:
        print("No songs indexed yet.")
        return
    print(f"\n{'ID':>4}  {'Title':<30}  Artist")
    print("-" * 55)
    for s in songs:
        print(f"{s['id']:>4}  {s['title']:<30}  {s['artist'] or '—'}")
    print(f"\nTotal: {song_count()} song(s)")


def _print_result(result):
    if result:
        print("\n✓ Song recognised!")
        print(f"  Title  : {result['title']}")
        print(f"  Artist : {result['artist'] or '—'}")
        print(f"  Score  : {result['score']} matching fingerprints")
    else:
        print("\n✗ No match found.")


COMMANDS = {
    'index':  cmd_index,
    'listen': cmd_listen,
    'query':  cmd_query,
    'list':   cmd_list,
}

if __name__ == '__main__':
    init_db()

    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]
    COMMANDS[cmd](sys.argv[2:])
