"""
rednoter — Convert podcast/YouTube audio to Xiaohongshu post prompts.

Usage:
    from rednoter import transcribe_url
    result = transcribe_url("https://www.youtube.com/watch?v=...")
    # Pass result.hermes_prompt to your LLM (via Hermes) to generate the post
    print(result.hermes_prompt)
"""

from .cleanup import cleanup_old_audio
from .config import RednoterConfig
from .downloader import download_audio
from .exceptions import ConfigurationError, DownloadError, RednoterError, TranscriptionError
from .models import Transcript, TranscriptResult, TranscriptSegment
from .transcriber import transcribe_audio


def _truncate_transcript(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    head = text[: int(max_chars * 0.1)]
    tail = text[-int(max_chars * 0.1) :]
    middle_budget = max_chars - len(head) - len(tail)
    mid_start = len(text) // 2 - middle_budget // 2
    middle = text[mid_start : mid_start + middle_budget]
    return head + "\n[...部分内容已省略...]\n" + middle + "\n[...]\n" + tail


def build_hermes_prompt(transcript: Transcript, source_url: str, config: RednoterConfig) -> str:
    """Build the user-turn prompt that Hermes passes to its LLM."""
    text = _truncate_transcript(transcript.full_text, config.max_transcript_chars)
    duration_mins = max(1, int(transcript.duration_seconds / 60))
    return (
        f"请根据以下播客/视频的文字稿，创作一篇小红书笔记。\n\n"
        f"来源：{source_url}\n"
        f"时长：约{duration_mins}分钟\n"
        f"语言：{transcript.language}\n\n"
        f"【文字稿】\n{text}\n\n"
        f"请按以下格式输出（不要使用emoji）：\n\n"
        f"标题：[标题内容]\n\n"
        f"[正文内容]\n\n"
        f"[#话题1 #话题2 ...]"
    )


def transcribe_url(
    url: str,
    config: RednoterConfig | None = None,
    *,
    keep_audio: bool = False,
) -> TranscriptResult:
    """
    Download audio from url, transcribe it, and return a TranscriptResult
    containing the transcript and a ready-to-use Hermes prompt.

    Automatically deletes audio files older than config.audio_retention_days
    before downloading.

    Args:
        url:        YouTube or podcast URL.
        config:     RednoterConfig. If None, loaded from environment variables.
        keep_audio: Keep the downloaded audio file after transcription (default: False).

    Returns:
        TranscriptResult with transcript and hermes_prompt.

    Raises:
        DownloadError:       Audio could not be downloaded.
        TranscriptionError:  Audio could not be transcribed.
        ConfigurationError:  Invalid configuration.
    """
    if config is None:
        config = RednoterConfig.from_env()

    cleanup_old_audio(config.audio_output_dir, config.audio_retention_days)

    audio_path = None
    try:
        audio_path = download_audio(url, config)
        transcript = transcribe_audio(audio_path, config)
        prompt = build_hermes_prompt(transcript, url, config)
        return TranscriptResult(
            transcript=transcript,
            source_url=url,
            hermes_prompt=prompt,
        )
    finally:
        if audio_path and audio_path.exists() and not keep_audio:
            audio_path.unlink(missing_ok=True)


__all__ = [
    "transcribe_url",
    "build_hermes_prompt",
    "download_audio",
    "transcribe_audio",
    "cleanup_old_audio",
    "RednoterConfig",
    "TranscriptResult",
    "Transcript",
    "TranscriptSegment",
    "RednoterError",
    "DownloadError",
    "TranscriptionError",
    "ConfigurationError",
]
