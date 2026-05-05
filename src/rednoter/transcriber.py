from pathlib import Path

from .config import RednoterConfig
from .exceptions import TranscriptionError
from .models import Transcript, TranscriptSegment


def transcribe_audio(audio_path: Path, config: RednoterConfig) -> Transcript:
    """
    Transcribe audio using mlx-whisper with Metal GPU acceleration on Apple Silicon.
    The model is downloaded automatically from Hugging Face on first use (~3GB for large-v2).
    """
    try:
        import mlx_whisper
    except ImportError as e:
        raise TranscriptionError(
            "mlx-whisper is not installed. Run: uv add mlx-whisper"
        ) from e

    try:
        result = mlx_whisper.transcribe(
            str(audio_path),
            path_or_hf_repo=config.whisper_model,
            word_timestamps=False,
        )
    except Exception as e:
        raise TranscriptionError(
            f"Transcription failed for {audio_path}: {e}"
        ) from e

    segments_data = result.get("segments", [])
    segments = [
        TranscriptSegment(
            start=seg.get("start", 0.0),
            end=seg.get("end", 0.0),
            text=seg.get("text", "").strip(),
        )
        for seg in segments_data
    ]

    full_text = result.get("text", "").strip()
    if not full_text:
        full_text = " ".join(s.text for s in segments).strip()

    if not full_text:
        raise TranscriptionError(
            f"Transcription produced empty text for {audio_path}. "
            "The audio may contain no speech."
        )

    # Estimate duration from last segment end, fallback to 0
    duration = segments[-1].end if segments else 0.0

    return Transcript(
        full_text=full_text,
        segments=segments,
        language=result.get("language", "unknown"),
        duration_seconds=duration,
    )
