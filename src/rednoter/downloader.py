from pathlib import Path

import yt_dlp

from .config import RednoterConfig
from .exceptions import DownloadError


def download_audio(url: str, config: RednoterConfig) -> Path:
    """
    Download audio from url using yt-dlp and convert to mp3 via ffmpeg.
    Returns the path to the downloaded .mp3 file.
    """
    output_dir = Path(config.audio_output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_template = str(output_dir / "%(id)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "128",
            }
        ],
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info.get("id", "audio")
            audio_path = output_dir / f"{video_id}.mp3"
            if not audio_path.exists():
                candidates = list(output_dir.glob(f"{video_id}.*"))
                if not candidates:
                    raise DownloadError(f"Downloaded file not found for {url}")
                audio_path = candidates[0]
            return audio_path
    except DownloadError:
        raise
    except yt_dlp.utils.DownloadError as e:
        raise DownloadError(f"Failed to download audio from {url}: {e}") from e
    except Exception as e:
        raise DownloadError(f"Unexpected download error for {url}: {e}") from e
