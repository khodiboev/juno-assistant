import re
from dataclasses import dataclass
from pathlib import Path

HEADING = re.compile(r"^(#{1,3})\s+(.+)$")


@dataclass
class Chunk:
    source: str
    title: str
    section: str
    text: str

    def for_embedding(self, subject: str = "") -> str:
        header = " | ".join(part for part in (subject, self.title, self.section) if part)
        return f"{header}\n{self.text}"


def split_sections(markdown: str) -> tuple[str, list[tuple[str, str]]]:
    title = ""
    h2 = ""
    section = "Overview"
    buffer: list[str] = []
    sections: list[tuple[str, str]] = []

    def flush():
        body = "\n".join(buffer).strip()
        if body:
            sections.append((section, body))
        buffer.clear()

    for line in markdown.splitlines():
        match = HEADING.match(line)
        if not match:
            buffer.append(line)
            continue

        flush()
        level, text = len(match.group(1)), match.group(2).strip()
        if level == 1:
            title = text
            h2, section = "", "Overview"
        elif level == 2:
            h2 = section = text
        else:
            section = f"{h2} > {text}" if h2 else text

    flush()
    return title, sections


def split_long(text: str, size: int, overlap: int) -> list[str]:
    if len(text) <= size:
        return [text]

    parts: list[str] = []
    current = ""
    for line in text.splitlines():
        if current and len(current) + len(line) + 1 > size:
            parts.append(current.strip())
            current = current[-overlap:] if overlap else ""
        current += line + "\n"
    if current.strip():
        parts.append(current.strip())
    return parts


def chunk_file(path: Path, root: Path, size: int, overlap: int) -> list[Chunk]:
    title, sections = split_sections(path.read_text(encoding="utf-8"))
    title = title or path.stem
    source = str(path.relative_to(root.parent))

    chunks: list[Chunk] = []
    for section, body in sections:
        for piece in split_long(body, size, overlap):
            chunks.append(Chunk(source=source, title=title, section=section, text=piece))
    return chunks


def chunk_directory(root: Path, size: int = 1200, overlap: int = 200) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in sorted(root.rglob("*.md")):
        chunks.extend(chunk_file(path, root, size, overlap))
    return chunks
