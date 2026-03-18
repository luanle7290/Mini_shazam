"""
Audio Fingerprinting Module
Implements the Shazam-like fingerprinting algorithm:
1. Compute spectrogram
2. Find local peaks
3. Generate hashes from peak pairs
"""

import numpy as np
from scipy import signal
from scipy.ndimage import maximum_filter
import hashlib


# --- Tunable parameters ---
SAMPLE_RATE = 22050       # Hz
FFT_WINDOW  = 4096        # samples per FFT frame
HOP_LENGTH  = 512         # samples between frames
# Peak-picking neighbourhood (time_bins x freq_bins)
PEAK_NEIGHBORHOOD = (10, 10)
# How many pairs to form per anchor peak
FAN_VALUE   = 15
# Maximum time delta (frames) between anchor and paired peak
MAX_TIME_DELTA = 200
MIN_TIME_DELTA = 1


def compute_spectrogram(audio: np.ndarray, sr: int = SAMPLE_RATE):
    """Return log-magnitude spectrogram (freq_bins x time_bins)."""
    freqs, times, spec = signal.spectrogram(
        audio,
        fs=sr,
        nperseg=FFT_WINDOW,
        noverlap=FFT_WINDOW - HOP_LENGTH,
        window='hann',
    )
    # Log compression (avoid log(0))
    log_spec = 10 * np.log10(np.maximum(spec, 1e-10))
    return freqs, times, log_spec


def find_peaks(log_spec: np.ndarray):
    """
    Detect local maxima in the spectrogram.
    Returns list of (time_bin, freq_bin) tuples.
    """
    # local maximum filter
    neighborhood = np.ones(PEAK_NEIGHBORHOOD, dtype=bool)
    local_max = maximum_filter(log_spec, footprint=neighborhood) == log_spec

    # Threshold: keep only peaks above mean
    threshold = log_spec.mean()
    detected = local_max & (log_spec > threshold)

    freq_idxs, time_idxs = np.where(detected)
    peaks = list(zip(time_idxs, freq_idxs))   # (t, f) pairs
    return peaks


def generate_hashes(peaks: list, song_id: int = None):
    """
    Pair each peak with its FAN_VALUE nearest future peaks and hash them.

    Returns list of (hash_str, time_offset) if song_id is None (query mode),
    or list of (hash_str, time_offset, song_id) for indexing mode.
    """
    # Sort by time
    peaks = sorted(peaks, key=lambda p: p[0])
    hashes = []

    for i, (t1, f1) in enumerate(peaks):
        for j in range(1, FAN_VALUE + 1):
            if i + j >= len(peaks):
                break
            t2, f2 = peaks[i + j]
            dt = t2 - t1
            if dt < MIN_TIME_DELTA or dt > MAX_TIME_DELTA:
                continue

            # Hash: freq1 | freq2 | delta_t  → SHA1 → first 20 hex chars
            raw = f"{f1}|{f2}|{dt}"
            h = hashlib.sha1(raw.encode()).hexdigest()[:20]

            if song_id is None:
                hashes.append((h, int(t1)))
            else:
                hashes.append((h, int(t1), song_id))

    return hashes


def fingerprint_audio(audio: np.ndarray, sr: int = SAMPLE_RATE, song_id: int = None):
    """Full pipeline: audio array → list of hashes."""
    _, _, log_spec = compute_spectrogram(audio, sr)
    peaks = find_peaks(log_spec)
    return generate_hashes(peaks, song_id=song_id)
