"""Rendering helpers for reader view and EPUB export."""

from __future__ import annotations

import html
import io
import textwrap
import zipfile
from datetime import datetime
from typing import Iterable, Optional

from fastapi.responses import HTMLResponse, StreamingResponse

from ies_backend.schemas.conversation import ConversationSession, ConversationTurn
from ies_backend.schemas.source_document import SourceDocument
from ies_backend.schemas.entity import ExtractionResult, ExtractedEntity, EntityKind


BASE_CSS = """
/* ============================================
   CSS CUSTOM PROPERTIES — DARK MODE (DEFAULT)
   ============================================ */
:root {
  /* === Base Colors === */
  --bg-primary: #0f0f10;        /* Near black, warm undertone */
  --bg-secondary: #1a1a1c;      /* Elevated surfaces */
  --bg-tertiary: #252528;       /* Cards, panels */
  --bg-hover: #2a2a2e;          /* Hover states */

  /* === Text === */
  --text-primary: #f5f5f5;      /* Primary content */
  --text-secondary: #a0a0a5;    /* Secondary, labels */
  --text-muted: #6b6b70;        /* Disabled, hints */

  /* === Borders === */
  --border-subtle: #2a2a2e;     /* Dividers */
  --border-default: #3a3a3e;    /* Input borders */
  --border-focus: #5a5a60;      /* Focus states */

  /* === Entity Type Colors — Bold, not muted === */
  --entity-concept: #3b82f6;    /* Blue */
  --entity-person: #10b981;     /* Green */
  --entity-theory: #8b5cf6;     /* Purple */
  --entity-framework: #f59e0b;  /* Amber */
  --entity-assessment: #ef4444; /* Red */
  --entity-spark: #ec4899;      /* Pink */
  --entity-insight: #06b6d4;    /* Cyan */
  --entity-thread: #84cc16;     /* Lime */

  /* === Gradients for active states === */
  --gradient-concept: linear-gradient(135deg, #3b82f6, #1d4ed8);
  --gradient-person: linear-gradient(135deg, #10b981, #059669);
  --gradient-theory: linear-gradient(135deg, #8b5cf6, #6d28d9);
  --gradient-framework: linear-gradient(135deg, #f59e0b, #d97706);
  --gradient-assessment: linear-gradient(135deg, #ef4444, #dc2626);

  /* === Semantic Colors === */
  --success: #10b981;
  --warning: #f59e0b;
  --error: #ef4444;
  --info: #3b82f6;

  /* === Typography === */
  --font-sans: sans-serif;
  --font-serif: Georgia, serif;
  --font-mono: monospace;

  /* Font Sizes */
  --text-xs: 0.75rem;     /* 12px */
  --text-sm: 0.875rem;    /* 14px */
  --text-base: 1rem;      /* 16px */
  --text-lg: 1.125rem;    /* 18px */
  --text-xl: 1.25rem;     /* 20px */
  --text-2xl: 1.5rem;     /* 24px */
  --text-3xl: 2rem;       /* 32px */

  /* Font Weights */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  /* Line Heights */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
  --leading-reader: 1.6; /* New line height for reader content */

  /* === Spacing (8px base) === */
  --space-0: 0;
  --space-1: 0.25rem;     /* 4px */
  --space-2: 0.5rem;      /* 8px */
  --space-3: 0.75rem;     /* 12px */
  --space-4: 1rem;        /* 16px */
  --space-5: 1.25rem;     /* 20px */
  --space-6: 1.5rem;      /* 24px */
  --space-8: 2rem;        /* 32px */
  --space-10: 2.5rem;     /* 40px */
  --space-12: 3rem;       /* 48px */
  --space-16: 4rem;       /* 64px */

  /* === Border Radius === */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 9999px;

  /* Border Width */
  --border-thin: 1px;
  --border-medium: 2px;

  /* === Shadows & Depth === */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.5);
  --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.6);

  /* Glass effect for floating panels */
  --glass-bg: rgba(26, 26, 28, 0.8);
  --glass-blur: blur(12px);
  --glass-border: 1px solid rgba(255, 255, 255, 0.1);

  /* === Layout === */
  --content-max-width: 72ch; /* Updated max-width for readability */
}

/* ============================================
   LIGHT MODE (Optional)
   ============================================ */
:root.light,
[data-theme="light"] {
  --bg-primary: #fafafa;
  --bg-secondary: #f0f0f2;
  --bg-tertiary: #ffffff;
  --bg-hover: #e8e8ea;

  --text-primary: #1a1a1c;
  --text-secondary: #6b6b70;
  --text-muted: #a0a0a5;

  --border-subtle: #e0e0e2;
  --border-default: #d0d0d2;
  --border-focus: #b0b0b5;

  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15);

  --glass-bg: rgba(255, 255, 255, 0.8);
  --glass-border: 1px solid rgba(0, 0, 0, 0.1);
}

/* ============================================
   BASE STYLES
   ============================================ */
*, *::before, *::after {
  box-sizing: border-box;
}

html {
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  margin: 0;
  padding: 0;
  font-family: var(--font-serif); /* Use serif font for body */
  font-size: var(--text-base);
  line-height: var(--leading-reader); /* Use new reader line height */
  color: var(--text-primary);
  background-color: var(--bg-primary);
  max-width: var(--content-max-width); /* Apply max-width */
  margin-left: auto; /* Center the content */
  margin-right: auto; /* Center the content */
  padding: var(--space-4); /* Add some padding around the content */
}

/* ============================================
   TYPOGRAPHY
   ============================================ */
h1, h2, h3, h4, h5, h6 { /* Apply heading styles directly to tags */
  font-family: var(--font-sans); /* Humanist sans for headings */
  font-weight: var(--font-semibold);
  line-height: var(--leading-tight);
  color: var(--text-primary);
  margin-top: var(--space-8);
  margin-bottom: var(--space-4);
}

h1 { font-size: var(--text-3xl); }
h2 { font-size: var(--text-2xl); }
h3 { font-size: var(--text-xl); }
h4 { font-size: var(--text-lg); }
h5 { font-size: var(--text-base); }
h6 { font-size: var(--text-sm); }

p {
  margin-top: var(--space-4);
  margin-bottom: var(--space-4);
}

.body-text {
  font-family: var(--font-serif); /* Ensure body text also uses serif */
  font-size: var(--text-base);
  line-height: var(--leading-reader);
}

/* ============================================
   READER VIEW COMPONENTS
   ============================================ */
.reader-container {
  padding: var(--space-4);
  max-width: var(--content-max-width);
  margin-left: auto;
  margin-right: auto;
}

.conversation-turn {
  background: var(--bg-tertiary);
  border: var(--border-thin) solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  margin-bottom: var(--space-6);
  position: relative;
}

.conversation-turn + .conversation-turn {
  margin-top: var(--space-4);
  border-top: none;
}

.conversation-turn:not(:last-child)::after {
  content: '';
  position: absolute;
  bottom: calc(-1 * var(--space-3)); /* Position divider between cards */
  left: 50%;
  transform: translateX(-50%);
  width: 25%;
  height: var(--border-thin);
  background-color: var(--border-subtle);
  border-radius: var(--radius-full);
}

.role-badge {
  font-family: var(--font-sans);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-full);
  display: inline-flex;
  align-items: center;
  margin-bottom: var(--space-3);
}

.role-badge.user {
  background: rgba(59, 130, 246, 0.15); /* Blue */
  color: var(--entity-concept);
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.role-badge.assistant {
  background: rgba(16, 185, 129, 0.15); /* Green */
  color: var(--entity-person); /* Using person color for assistant for now */
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.role-badge.system {
  background: rgba(139, 92, 246, 0.15); /* Purple */
  color: var(--entity-theory); /* Using theory color for system for now */
  border: 1px solid rgba(139, 92, 246, 0.3);
}

blockquote {
  border-left: 4px solid var(--border-default);
  padding-left: var(--space-4);
  margin-left: 0;
  color: var(--text-secondary);
  font-style: italic;
}

code {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  background-color: var(--bg-secondary);
  border-radius: var(--radius-sm);
  padding: 0.2em 0.4em;
}

pre {
  background-color: var(--bg-secondary);
  border-radius: var(--radius-md);
  padding: var(--space-3);
  overflow-x: auto;
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  line-height: var(--leading-normal);
  color: var(--text-primary);
  margin-top: var(--space-4);
  margin-bottom: var(--space-4);
}

pre code {
  background-color: transparent;
  padding: 0;
  border-radius: 0;
}
"""


class RenderingService:
    """Render conversations as reader HTML or EPUB."""

    @staticmethod
    def render_reader_view(session: ConversationSession, theme: str = "dark") -> HTMLResponse:
        """Return HTMLResponse for a conversation."""
        title = html.escape(session.topic or "Conversation")
        meta = RenderingService._meta_line(session)
        body = "\n".join(RenderingService._render_turns(session.turns))
        html_doc = f"""<!doctype html>
<html lang="en" data-theme="{html.escape(theme)}">
<head><meta charset="utf-8"><title>{title}</title>
<style>{BASE_CSS}</style></head>
<body>
<div class="reader-container">
<h1>{title}</h1>
<div class="meta">{meta}</div>
{body}
</div>
</body></html>"""
        return HTMLResponse(html_doc)
        return HTMLResponse(html_doc)

    @staticmethod
    def render_epub(session: ConversationSession, extraction_result: Optional[ExtractionResult] = None):
        """Return StreamingResponse with EPUB bytes for a conversation."""
        title = session.topic or "Conversation"
        
        chapters = []
        # Intro Chapter
        intro_filename, intro_content = RenderingService._generate_conversation_intro_chapter(session)
        chapters.append({"id": "chap_intro", "filename": intro_filename, "title": "Introduction", "content": intro_content})

        # Body Chapter
        body_filename, body_content = RenderingService._generate_conversation_body_chapter(session)
        chapters.append({"id": "chap_body", "filename": body_filename, "title": "Conversation", "content": body_content})

        # Entities Appendix
        entities_chapter = RenderingService._generate_entities_appendix_chapter(extraction_result)
        if entities_chapter:
            entities_filename, entities_content = entities_chapter
            chapters.append({"id": "chap_entities", "filename": entities_filename, "title": "Entities", "content": entities_content})

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

            # Build manifest and spine for content.opf
            manifest_items = []
            spine_itemrefs = []
            nav_points = []

            for chapter in chapters:
                manifest_items.append(f'<item id="{chapter["id"]}" href="{chapter["filename"]}" media-type="application/xhtml+xml"/>')
                spine_itemrefs.append(f'<itemref idref="{chapter["id"]}"/>')
                nav_points.append(f'<li><a href="{chapter["filename"]}">{html.escape(chapter["title"])}</a></li>')

            manifest_items_str = "\n    ".join(manifest_items)
            spine_itemrefs_str = "\n    ".join(spine_itemrefs)
            nav_points_str = "\n".join(nav_points)

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
    {manifest_items_str}
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
  </manifest>
  <spine>
    {spine_itemrefs_str}
  </spine>
</package>"""
                ).strip(),
            )
            zf.writestr(
                "OEBPS/nav.xhtml",
                textwrap.dedent(
                    f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>Nav</title></head>
<body>
<nav epub:type="toc" id="toc"><h1>Contents</h1>
<ol>
{nav_points_str}
</ol>
</nav>
</body></html>"""
                ).strip(),
            )

            for chapter in chapters:
                chapter_html = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>{html.escape(chapter["title"])}</title><style>{html.escape(BASE_CSS)}</style></head>
<body><div class="reader-container">{chapter["content"]}</div></body></html>"""
                zf.writestr(f"OEBPS/{chapter['filename']}", chapter_html)

        buf.seek(0)
        filename = f"{session.id}.epub"
        return StreamingResponse(
            buf,
            media_type="application/epub+zip",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    @staticmethod
    def _render_turns(turns: Iterable[ConversationTurn]) -> list[str]:
        """Render turns as HTML blocks, grouped by role."""
        rendered: list[str] = []
        last_role: str | None = None
        buffer: list[str] = []

        def flush():
            nonlocal buffer, last_role
            if not buffer:
                return
            
            # Sanitize role for class name
            role_class = f"role-{(last_role or 'unknown').lower()}"
            # Ensure label is capitalized, default to 'Unknown'
            label = (last_role or 'unknown').capitalize()

            rendered.append(
                f'<div class="conversation-turn {role_class}"><div class="role-badge {role_class}">'
                f'{html.escape(label)}</div><div>'
                f'{"".join(buffer)}</div></div>'
            )
            buffer = []

        for turn in turns:
            role = (turn.role or "user").lower()
            text = html.escape(turn.text or "")
            # Preserve newlines but allow paragraph breaks for better styling
            text = text.replace("\n\n", "</p><p>").replace("\n", "<br>")
            if not text.startswith("<p>"):
                text = "<p>" + text
            if not text.endswith("</p>"):
                text = text + "</p>"

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

    @staticmethod
    def _generate_conversation_intro_chapter(session: ConversationSession) -> tuple[str, str]:
        title = html.escape(session.topic or "Conversation Intro")
        meta = RenderingService._meta_line(session)
        content = f"""<h1>{title}</h1>
<p class="meta">{meta}</p>
<p><strong>Source:</strong> {html.escape(session.source.value)}</p>
<p><strong>Imported:</strong> {session.imported_at.isoformat()}</p>
"""
        return "chap_intro.xhtml", content

    @staticmethod
    def _generate_conversation_body_chapter(session: ConversationSession) -> tuple[str, str]:
        title = html.escape(session.topic or "Conversation Body")
        body_content = "\n".join(RenderingService._render_turns(session.turns))
        content = f"""<h1>{title} - Conversation</h1>
{body_content}
"""
        return "chap_body.xhtml", content

    @staticmethod
    def _generate_entities_appendix_chapter(extraction_result: Optional[ExtractionResult]) -> Optional[tuple[str, str]]:
        if not extraction_result or not extraction_result.entities:
            return None

        content = "<h1>Entities Appendix</h1>"
        for entity in extraction_result.entities:
            content += f"""
<div class="entity-entry">
    <h2>{html.escape(entity.name)}</h2>
    <p><strong>Kind:</strong> <span class="entity-kind-{entity.kind.value}">{html.escape(entity.kind.value.capitalize())}</span></p>
    <p><strong>Description:</strong> {html.escape(entity.description)}</p>
    <h3>Quotes:</h3>
    <ul>
"""
            for quote in entity.quotes:
                content += f"        <li>{html.escape(quote)}</li>\n"
            content += "    </ul>\n</div>\n"
        return "chap_entities.xhtml", content

    @staticmethod
    def _generate_source_intro_chapter(doc: SourceDocument) -> tuple[str, str]:
        title = html.escape(doc.title or doc.topic or "Source Intro")
        meta = f"Type: {html.escape(doc.source_type.value)}"
        if doc.uri:
            meta += f" · Original: <a href=\"{html.escape(doc.uri)}\">{html.escape(doc.uri)}</a>"
        meta += f" · Imported: {doc.imported_at.isoformat()}"

        content = f"""<h1>{title}</h1>
<p class="meta">{meta}</p>
<p><strong>Source Type:</strong> {html.escape(doc.source_type.value)}</p>
{f'<p><strong>Original URI:</strong> <a href="{html.escape(doc.uri)}">{html.escape(doc.uri)}</a></p>' if doc.uri else ''}
<p><strong>Imported At:</strong> {doc.imported_at.isoformat()}</p>
"""
        return "chap_source_intro.xhtml", content

    @staticmethod
    def _generate_source_body_chapter(doc: SourceDocument) -> tuple[str, str]:
        title = html.escape(doc.title or doc.topic or "Source Body")
        body_content = "<p>" + "<br><br>".join(html.escape(doc.content).split("\n\n")) + "</p>"
        content = f"""<h1>{title} - Content</h1>
{body_content}
"""
        return "chap_source_body.xhtml", content

    # ---- SourceDocument rendering ----
    @staticmethod
    def render_source_reader(doc: SourceDocument, theme: str = "dark") -> HTMLResponse:
        """Render a source document as reader view."""
        title = html.escape(doc.title or doc.topic or "Source")
        meta = f"Type: {html.escape(doc.source_type.value)}"
        if doc.uri:
            meta += f" · <a href=\"{html.escape(doc.uri)}\">Original</a>"
        meta += f" · Imported: {html.escape(doc.imported_at.isoformat())}"
        body = "<p>" + "<br><br>".join(html.escape(doc.content).split("\n\n")) + "</p>"
        html_doc = f"""<!doctype html>
<html lang="en" data-theme="{html.escape(theme)}">
<head><meta charset="utf-8"><title>{title}</title>
<style>{BASE_CSS}</style></head>
<body>
<div class="reader-container">
<h1>{title}</h1>
<div class="meta">{meta}</div>
{body}
</div>
</body></html>"""
        return HTMLResponse(html_doc)

    @staticmethod
    def render_source_epub(doc: SourceDocument, extraction_result: Optional[ExtractionResult] = None):
        """Return EPUB for a source document."""
        title = doc.title or doc.topic or "Source"

        chapters = []
        # Intro Chapter
        intro_filename, intro_content = RenderingService._generate_source_intro_chapter(doc)
        chapters.append({"id": "chap_intro", "filename": intro_filename, "title": "Introduction", "content": intro_content})

        # Body Chapter
        body_filename, body_content = RenderingService._generate_source_body_chapter(doc)
        chapters.append({"id": "chap_body", "filename": body_filename, "title": "Source Content", "content": body_content})

        # Entities Appendix
        entities_chapter = RenderingService._generate_entities_appendix_chapter(extraction_result)
        if entities_chapter:
            entities_filename, entities_content = entities_chapter
            chapters.append({"id": "chap_entities", "filename": entities_filename, "title": "Entities", "content": entities_content})

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

            # Build manifest and spine for content.opf
            manifest_items = []
            spine_itemrefs = []
            nav_points = []

            for chapter in chapters:
                manifest_items.append(f'<item id="{chapter["id"]}" href="{chapter["filename"]}" media-type="application/xhtml+xml"/>')
                spine_itemrefs.append(f'<itemref idref="{chapter["id"]}"/>')
                nav_points.append(f'<li><a href="{chapter["filename"]}">{html.escape(chapter["title"])}</a></li>')

            manifest_items_str = "\n    ".join(manifest_items)
            spine_itemrefs_str = "\n    ".join(spine_itemrefs)
            nav_points_str = "\n".join(nav_points)

            zf.writestr(
                "OEBPS/content.opf",
                textwrap.dedent(
                    f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="3.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="BookId">{html.escape(doc.id)}</dc:identifier>
    <dc:title>{html.escape(title)}</dc:title>
    <dc:language>en</dc:language>
  </metadata>
  <manifest>
    {manifest_items_str}
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
  </manifest>
  <spine>
    {spine_itemrefs_str}
  </spine>
</package>"""
                ).strip(),
            )
            zf.writestr(
                "OEBPS/nav.xhtml",
                textwrap.dedent(
                    f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>Nav</title></head>
<body>
<nav epub:type="toc" id="toc"><h1>Contents</h1>
<ol>
{nav_points_str}
</ol>
</nav>
</body></html>"""
                ).strip(),
            )

            for chapter in chapters:
                chapter_html = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>{html.escape(chapter["title"])}</title><style>{html.escape(BASE_CSS)}</style></head>
<body><div class="reader-container">{chapter["content"]}</div></body></html>"""
                zf.writestr(f"OEBPS/{chapter['filename']}", chapter_html)

        buf.seek(0)
        filename = f"{doc.id}.epub"
        return StreamingResponse(
            buf,
            media_type="application/epub+zip",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
