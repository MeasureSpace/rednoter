import time
from pathlib import Path

_AUDIO_EXTENSIONS = {".mp3", ".m4a", ".wav", ".webm", ".ogg"}


def cleanup_old_audio(audio_dir: str, retention_days: int = 5) -> list[Path]:
    """Delete audio files older than retention_days. Returns list of deleted paths."""
    cutoff = time.time() - retention_days * 86400
    deleted: list[Path] = []
    p = Path(audio_dir)
    if not p.exists():
        return deleted
    for f in p.iterdir():
        if f.is_file() and f.suffix.lower() in _AUDIO_EXTENSIONS:
            if f.stat().st_mtime < cutoff:
                f.unlink()
                deleted.append(f)
    return deleted
