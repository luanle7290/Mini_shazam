"""
Tự động index tất cả file nhạc trong thư mục songs/
Chạy: python index_all.py
"""

import os
import sys

# Fix Vietnamese text on Windows terminal
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))

from src.database    import init_db, insert_song, insert_fingerprints, list_songs
from src.fingerprint import fingerprint_audio
from src.recorder    import load_audio_file

SONGS_DIR = os.path.join(os.path.dirname(__file__), 'songs')
SUPPORTED  = ('.mp3', '.wav', '.flac', '.m4a', '.ogg')


def parse_filename(filename: str) -> tuple[str, str]:
    """
    Tự đoán title và artist từ tên file.
    Hỗ trợ 2 định dạng:
      "Hãy Trao Cho Anh - Sơn Tùng.mp3"  →  title="Hãy Trao Cho Anh", artist="Sơn Tùng"
      "Shape Of You.mp3"                  →  title="Shape Of You",       artist=""
    """
    name = os.path.splitext(filename)[0]   # bỏ đuôi .mp3
    if ' - ' in name:
        title, artist = name.split(' - ', 1)
        return title.strip(), artist.strip()
    return name.strip(), ""


def index_all():
    init_db()

    # Lấy danh sách file đã index để không index trùng
    indexed_files = {row['file'] for row in list_songs()}

    files = [
        f for f in os.listdir(SONGS_DIR)
        if f.lower().endswith(SUPPORTED)
    ]

    if not files:
        print(f"Không tìm thấy file nhạc nào trong '{SONGS_DIR}'")
        print(f"Hỗ trợ: {', '.join(SUPPORTED)}")
        return

    print(f"Tìm thấy {len(files)} file nhạc.\n")

    success, skipped, failed = 0, 0, 0

    for i, filename in enumerate(files, 1):
        filepath = os.path.join(SONGS_DIR, filename)

        if filepath in indexed_files:
            print(f"[{i}/{len(files)}] BỎ QUA (đã index): {filename}")
            skipped += 1
            continue

        title, artist = parse_filename(filename)
        print(f"[{i}/{len(files)}] Đang index: {filename}")
        print(f"           Title : {title}")
        print(f"           Artist: {artist or '(không rõ)'}")

        try:
            audio   = load_audio_file(filepath)
            song_id = insert_song(title=title, artist=artist, file=filepath)
            hashes  = fingerprint_audio(audio, song_id=song_id)
            insert_fingerprints(hashes)
            print(f"           ✓ {len(hashes)} fingerprints lưu xong.\n")
            success += 1
        except Exception as e:
            print(f"           ✗ Lỗi: {e}\n")
            failed += 1

    print("=" * 45)
    print(f"Hoàn tất: {success} thành công | {skipped} bỏ qua | {failed} lỗi")


if __name__ == '__main__':
    index_all()
