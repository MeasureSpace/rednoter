# rednoter

Convert a podcast or YouTube URL into a Xiaohongshu (小红书) post draft in Chinese.

The library handles audio download and transcription locally. Post generation is delegated to your LLM of choice via a Hermes agent, using the included specialist prompt.

## How it works

```
URL → yt-dlp (download) → mlx-whisper (transcribe) → prompt → Hermes LLM → post
```

1. `yt-dlp` downloads the audio from YouTube, podcasts, or any supported URL
2. `mlx-whisper` transcribes it locally using the Metal GPU on Apple Silicon (large-v2 model)
3. The library returns a structured prompt ready for your Hermes agent to pass to its LLM
4. The LLM generates a natural-sounding Chinese Xiaohongshu post using the included specialist prompt
5. Hermes delivers the result to you via Discord and saves a copy as a `.txt` file

No OpenAI or Anthropic API calls are made by this library. Generation is entirely up to your Hermes setup.

## Requirements

- macOS with Apple Silicon (M1 or later) — required for GPU-accelerated transcription
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) for package management
- ffmpeg for audio extraction

## Installation

```bash
# Install ffmpeg if you don't have it
brew install ffmpeg

# Clone the repo
git clone <repo-url>
cd rednoter

# Install Python dependencies
uv sync
```

On first transcription run, `whisper-large-v2-mlx` (~3 GB) will be downloaded automatically from Hugging Face.

## Usage

### From Python

```python
from rednoter import transcribe_url

result = transcribe_url("https://www.youtube.com/watch?v=...")

print(result.transcript.full_text)   # raw transcript
print(result.hermes_prompt)          # prompt to pass to your LLM
```

### CLI test

```bash
uv run python examples/hermes_usage.py "https://www.youtube.com/watch?v=..."
```

This prints the transcript metadata and the full Hermes prompt. Pass that prompt to any LLM with the system prompt in `prompts/xiaohongshu_specialist.md` to get the post.

### Hermes integration

In your Hermes agent, expose `handle_rednote_request` as a tool:

```python
from examples.hermes_usage import handle_rednote_request

result = handle_rednote_request("https://www.youtube.com/watch?v=...")
# result["hermes_prompt"]  → pass to LLM
# result["save_path"]      → write LLM output here, share via Discord
```

See [examples/hermes_usage.py](examples/hermes_usage.py) for the full implementation including Discord delivery notes.

## Post generation prompt

The Hermes system prompt is in [prompts/xiaohongshu_specialist.md](prompts/xiaohongshu_specialist.md).

It produces posts with these characteristics:

- Written from the perspective of an AI/tech content creator with an established audience
- Chinese, conversational tone — not corporate, not academic
- 15–25 character title with a concrete, specific angle
- 3–5 short paragraphs with a personal point of view
- No emoji, no filler phrases (首先、其次、综上所述、不得不说…)
- 6–10 hashtags mixing niche tech tags with broader discovery tags

## Configuration

Copy `.env.example` to `.env` and adjust as needed:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `REDNOTER_WHISPER_MODEL` | `mlx-community/whisper-large-v2-mlx` | Whisper model. Use `mlx-community/whisper-small-mlx` for faster, lighter transcription |
| `REDNOTER_AUDIO_RETENTION_DAYS` | `5` | Downloaded audio files older than this are deleted automatically on each run |

## Project structure

```
rednoter/
├── prompts/
│   └── xiaohongshu_specialist.md   # Hermes system prompt for post generation
├── src/rednoter/
│   ├── __init__.py                 # Public API: transcribe_url()
│   ├── config.py                   # RednoterConfig
│   ├── models.py                   # Transcript, TranscriptResult
│   ├── exceptions.py               # DownloadError, TranscriptionError, etc.
│   ├── downloader.py               # yt-dlp audio download
│   ├── transcriber.py              # mlx-whisper GPU transcription
│   └── cleanup.py                  # Audio file retention management
└── examples/
    └── hermes_usage.py             # Hermes tool handler
```

## Error handling

All errors raised by this library inherit from `RednoterError`:

```python
from rednoter import RednoterError, DownloadError, TranscriptionError

try:
    result = transcribe_url(url)
except DownloadError as e:
    # URL is private, geo-blocked, or unsupported
except TranscriptionError as e:
    # Audio contains no speech, or transcription failed
except RednoterError as e:
    # Catch-all for any other library error
```
