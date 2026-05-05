from dataclasses import dataclass


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str


@dataclass
class Transcript:
    full_text: str
    segments: list[TranscriptSegment]
    language: str
    duration_seconds: float


@dataclass
class TranscriptResult:
    transcript: Transcript
    source_url: str
    hermes_prompt: str
