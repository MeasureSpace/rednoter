"""
Hermes agent integration for rednoter.

How this works:
1. Hermes calls handle_rednote_request(url) as a tool
2. The function downloads + transcribes the audio, returns a structured dict
3. Hermes passes result["hermes_prompt"] to its LLM with the xiaohongshu_specialist
   system prompt (see prompts/xiaohongshu_specialist.md)
4. Hermes writes the generated post to result["save_path"]
5. Hermes sends the post text + file path to the user via Discord

System prompt for the LLM step:
    Load the contents of prompts/xiaohongshu_specialist.md as the system prompt.
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rednoter import RednoterError, RednoterConfig, transcribe_url


def handle_rednote_request(url: str, config: RednoterConfig | None = None) -> dict:
    """
    Hermes tool handler: download and transcribe audio, return prompt for LLM.

    Returns a dict with:
        success       bool
        hermes_prompt str   — pass this to LLM with xiaohongshu_specialist system prompt
        save_path     str   — write the LLM output here, then share path via Discord
        transcript    str   — raw transcript text (for debugging)
        duration_mins int
        language      str
        source_url    str
        error         str | None
    """
    try:
        result = transcribe_url(url, config=config)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = f"/tmp/rednoter_posts/{ts}_post.txt"
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)

        return {
            "success": True,
            "hermes_prompt": result.hermes_prompt,
            "save_path": save_path,
            "transcript": result.transcript.full_text,
            "duration_mins": max(1, int(result.transcript.duration_seconds / 60)),
            "language": result.transcript.language,
            "source_url": url,
            "error": None,
        }

    except RednoterError as e:
        return {
            "success": False,
            "hermes_prompt": "",
            "save_path": "",
            "transcript": "",
            "duration_mins": 0,
            "language": "",
            "source_url": url,
            "error": f"{type(e).__name__}: {e}",
        }


# Quick CLI test — not the Hermes path
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python hermes_usage.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    print(f"Processing: {url}")

    result = handle_rednote_request(url)

    if not result["success"]:
        print(f"ERROR: {result['error']}", file=sys.stderr)
        sys.exit(1)

    print(f"Transcript language: {result['language']}")
    print(f"Duration: {result['duration_mins']} min")
    print(f"Transcript length: {len(result['transcript'])} chars")
    print(f"Save path (for Hermes to write generated post): {result['save_path']}")
    print()
    print("=" * 60)
    print("HERMES PROMPT (pass to LLM with xiaohongshu_specialist system prompt):")
    print("=" * 60)
    print(result["hermes_prompt"])
