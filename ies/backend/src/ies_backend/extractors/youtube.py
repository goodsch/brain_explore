"""YouTube transcript extraction using yt-dlp."""

import re
from urllib.parse import parse_qs, urlparse

from .base import ExtractedContent


class YouTubeExtractor:
    """Extract transcripts from YouTube videos."""

    YOUTUBE_PATTERNS = [
        re.compile(r"(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})"),
        re.compile(r"youtube\.com/embed/([a-zA-Z0-9_-]{11})"),
    ]

    @staticmethod
    def can_handle(source: str) -> bool:
        """Check if source is a YouTube URL or video ID."""
        if len(source) == 11 and re.match(r"^[a-zA-Z0-9_-]+$", source):
            return True  # Bare video ID
        for pattern in YouTubeExtractor.YOUTUBE_PATTERNS:
            if pattern.search(source):
                return True
        return False

    @staticmethod
    def _extract_video_id(source: str) -> str:
        """Extract video ID from URL or return as-is if already an ID."""
        if len(source) == 11 and re.match(r"^[a-zA-Z0-9_-]+$", source):
            return source

        for pattern in YouTubeExtractor.YOUTUBE_PATTERNS:
            match = pattern.search(source)
            if match:
                return match.group(1)

        # Try parsing as URL with v parameter
        parsed = urlparse(source)
        params = parse_qs(parsed.query)
        if "v" in params:
            return params["v"][0]

        raise ValueError(f"Could not extract video ID from: {source}")

    async def extract(self, source: str) -> ExtractedContent:
        """Extract transcript from YouTube video."""
        import yt_dlp

        video_id = self._extract_video_id(source)
        url = f"https://www.youtube.com/watch?v={video_id}"

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en", "en-US", "en-GB"],
            "subtitlesformat": "vtt",
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        if not info:
            raise ValueError(f"Failed to get video info: {url}")

        title = info.get("title")
        channel = info.get("channel") or info.get("uploader")
        duration = info.get("duration")
        upload_date = info.get("upload_date")

        # Get subtitles - prefer manual over auto-generated
        subtitles = info.get("subtitles", {})
        auto_subs = info.get("automatic_captions", {})

        transcript_text = None
        transcript_source = None

        # Try manual English subtitles first
        for lang in ["en", "en-US", "en-GB"]:
            if lang in subtitles:
                transcript_text = await self._fetch_subtitle(subtitles[lang], ydl_opts)
                transcript_source = f"manual ({lang})"
                break

        # Fall back to auto-generated
        if not transcript_text:
            for lang in ["en", "en-US", "en-GB"]:
                if lang in auto_subs:
                    transcript_text = await self._fetch_subtitle(auto_subs[lang], ydl_opts)
                    transcript_source = f"auto-generated ({lang})"
                    break

        if not transcript_text:
            raise ValueError(f"No English transcript available for: {url}")

        metadata: dict[str, str] = {
            "url": url,
            "video_id": video_id,
        }
        if channel:
            metadata["channel"] = channel
        if duration:
            metadata["duration"] = f"{duration // 60}:{duration % 60:02d}"
        if upload_date:
            metadata["upload_date"] = upload_date
        if transcript_source:
            metadata["transcript_source"] = transcript_source

        return ExtractedContent(
            title=title,
            content=transcript_text,
            metadata=metadata,
        )

    async def _fetch_subtitle(
        self, subtitle_info: list[dict], ydl_opts: dict
    ) -> str | None:
        """Fetch and parse subtitle content."""
        import yt_dlp

        # Find best format (prefer vtt, then srv3, then json3)
        preferred = ["vtt", "srv3", "json3", "ttml"]
        sub_url = None

        for fmt in preferred:
            for sub in subtitle_info:
                if sub.get("ext") == fmt:
                    sub_url = sub.get("url")
                    break
            if sub_url:
                break

        if not sub_url and subtitle_info:
            sub_url = subtitle_info[0].get("url")

        if not sub_url:
            return None

        # Fetch subtitle content
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            try:
                response = ydl.urlopen(sub_url)
                content = response.read().decode("utf-8")
                return self._parse_vtt(content)
            except Exception:
                return None

    @staticmethod
    def _parse_vtt(vtt_content: str) -> str:
        """Parse VTT content to plain text, removing timestamps and duplicates."""
        lines = []
        seen = set()

        for line in vtt_content.split("\n"):
            line = line.strip()
            # Skip headers, timestamps, and empty lines
            if not line or line.startswith("WEBVTT") or "-->" in line:
                continue
            if line.startswith("Kind:") or line.startswith("Language:"):
                continue
            # Skip numeric cue identifiers
            if line.isdigit():
                continue
            # Remove HTML-like tags
            line = re.sub(r"<[^>]+>", "", line)
            # Skip duplicates (common in auto-generated)
            if line not in seen:
                seen.add(line)
                lines.append(line)

        return " ".join(lines)
