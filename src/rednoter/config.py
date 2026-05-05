import os
from dataclasses import dataclass


@dataclass
class RednoterConfig:
    whisper_model: str = "mlx-community/whisper-large-v2-mlx"
    audio_output_dir: str = "/tmp/rednoter_audio"
    audio_retention_days: int = 5
    max_transcript_chars: int = 80_000

    @classmethod
    def from_env(cls) -> "RednoterConfig":
        return cls(
            whisper_model=os.environ.get(
                "REDNOTER_WHISPER_MODEL", "mlx-community/whisper-large-v2-mlx"
            ),
            audio_retention_days=int(
                os.environ.get("REDNOTER_AUDIO_RETENTION_DAYS", "5")
            ),
        )
