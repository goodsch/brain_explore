"""Rendering helpers for reader view and EPUB export."""

from __future__ import annotations

import html
import io
import textwrap
import zipfile
from datetime import datetime
from typing import Iterable

from fastapi.responses import HTMLResponse, StreamingResponse

from ies_backend.schemas.conversation import ConversationSession, ConversationTurn


BASE_CSS = """
body { font-family: 'Georgia', serif; margin: 2.5rem auto; max-width: 760px; line-height: 1.6; color: #1d1d1f; }
h1, h2, h3 { font-family: 'Inter', sans-serif; }
.meta { color: #555; font-size: 0.95rem; margin-bottom: 1rem; }
.turn { padding: 0.65rem 0.85rem; margin: 0.35rem 0; border-radius: 10px; }
.role-user { background: #f4f7ff; }
.role-assistant { background: #f8f8f8; }
.role-system { background: #fff3e0; }
.badge { font-size: 0.75rem; color: #555; text-transform: uppercase; letter-spacing: 0.05em; }
pre { background: #111; color: #f2f2f2; padding: 0.75rem; border-radius: 6px; overflow-x: auto; }
code { font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace; }
blockquote { border-left: 3px solid #ddd; padding-left: 0.75rem; color: #444; margin: 0.5rem 0; }
"""


class RenderingService:
    """Render conversations as reader HTML or EPUB."""

    @staticmethod
    def render_reader_view(session: ConversationSession) -> HTMLResponse:
        """Return HTMLResponse for a conversation."""
        title = html.escape(session.topic or "Conversation")
        meta = RenderingService._meta_line(session)
        body = "\n".join(RenderingService._render_turns(session.turns))
        html_doc = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{title}</title>
<style>{BASE_CSS}</style></head>
<body>
<h1>{title}</h1>
<div class="meta">{meta}</div>
{body}
</body></html>"""
        return HTMLResponse(html_doc)

    @staticmethod
    def render_epub(session: ConversationSession):
        """Return StreamingResponse with EPUB bytes for a conversation."""
        title = session.topic or "Conversation"
        meta = RenderingService._meta_line(session)
        body = "\n".join(RenderingService._render_turns(session.turns))
        chapter = f"<h1>{html.escape(title)}</h1><p class='meta'>{meta}</p>{body}"

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            # Required mimetype (must be stored)
            zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
            zf.writestr(
                "META-INF/container.xml",
                """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>""",
            )
            zf.writestr(
                "OEBPS/content.opf",
                textwrap.dedent(
                    f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="3.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="BookId">{html.escape(session.id)}</dc:identifier>
    <dc:title>{html.escape(title)}</dc:title>
    <dc:language>en</dc:language>
  </metadata>
  <manifest>
    <item id="chap1" href="chap1.xhtml" media-type="application/xhtml+xml"/>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
  </manifest>
  <spine>
    <itemref idref="chap1"/>
  </spine>
</package>"""
                ).strip(),
            )
            zf.writestr(
                "OEBPS/nav.xhtml",
                textwrap.dedent(
                    f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Nav</title></head>
<body>
<nav epub:type="toc" id="toc"><h1>Contents</h1>
<ol><li><a href="chap1.xhtml">{html.escape(title)}</a></li></ol>
</nav>
</body></html>"""
                ).strip(),
            )
            zf.writestr(
                "OEBPS/chap1.xhtml",
                f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>{html.escape(title)}</title><style>{html.escape(BASE_CSS)}</style></head>
<body>{chapter}</body></html>""",
            )

        buf.seek(0)
        filename = f"{session.id}.epub"
        return StreamingResponse(
            buf,
            media_type="application/epub+zip",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    @staticmethod
    def _render_turns(turns: Iterable[ConversationTurn]) -> list[str]:
        """Render turns as HTML blocks."""
        rendered: list[str] = []
        last_role: str | None = None
        buffer: list[str] = []

        def flush():
            nonlocal buffer, last_role
            if not buffer:
                return
            role_class = f"role-{last_role}" if last_role else ""
            label = last_role.capitalize() if last_role else "Turn"
            rendered.append(
                f'<div class="turn {role_class}"><div class="badge">{html.escape(label)}</div><div>'
                f'{"<br>".join(buffer)}</div></div>'
            )
            buffer = []

        for turn in turns:
            role = (turn.role or "user").lower()
            text = html.escape(turn.text or "")
            text = text.replace("\n\n", "<br><br>").replace("\n", "<br>")
            if last_role is None or role == last_role:
                buffer.append(text)
            else:
                flush()
                buffer = [text]
            last_role = role
        flush()
        return rendered

    @staticmethod
    def _meta_line(session: ConversationSession) -> str:
        """Build metadata line."""
        ts = session.imported_at
        ts_str = ts.isoformat() if isinstance(ts, datetime) else str(ts)
        return f"Source: {html.escape(session.source.value)} · Imported: {html.escape(ts_str)} · Turns: {session.turn_count}"
