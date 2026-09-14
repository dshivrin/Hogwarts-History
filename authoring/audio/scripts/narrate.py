from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import re
from typing import Sequence

import yaml


class BlockKind(str, Enum):
    CHAPTER = "chapter"
    SECTION = "section"
    PARAGRAPH = "paragraph"


@dataclass(frozen=True)
class SpeechBlock:
    kind: BlockKind
    text: str


@dataclass(frozen=True)
class Pronunciation:
    term: str
    replacement: str
    reason: str


@dataclass(frozen=True)
class SpeechChunk:
    kind: BlockKind
    text: str
    ends_block: bool


def load_pronunciations(path: Path) -> list[Pronunciation]:
    with path.open(encoding="utf-8") as guide:
        contents = yaml.safe_load(guide)

    if not isinstance(contents, dict):
        raise ValueError("Pronunciation guide must be a mapping")
    if type(contents.get("version")) is not int or contents["version"] != 1:
        raise ValueError("Pronunciation guide must have version 1")
    substitutions = contents.get("substitutions")
    if not isinstance(substitutions, list):
        raise ValueError("Pronunciation guide substitutions must be a list")

    entries: list[Pronunciation] = []
    terms: set[str] = set()
    for substitution in substitutions:
        if not isinstance(substitution, dict):
            raise ValueError("Each pronunciation substitution must be a mapping")
        fields = ("term", "replacement", "reason")
        if any(
            not isinstance(substitution.get(field), str)
            or not substitution[field].strip()
            for field in fields
        ):
            raise ValueError("Pronunciation substitutions require non-empty strings")
        term = substitution["term"]
        if term in terms:
            raise ValueError(f"Duplicate pronunciation term: {term}")
        terms.add(term)
        entries.append(
            Pronunciation(
                term=term,
                replacement=substitution["replacement"],
                reason=substitution["reason"],
            )
        )
    return entries


def apply_pronunciations(text: str, entries: Sequence[Pronunciation]) -> str:
    for entry in entries:
        text = re.sub(
            rf"(?<!\w){re.escape(entry.term)}(?!\w)", entry.replacement, text
        )
    return text


def split_sentences(text: str) -> list[str]:
    normalized = " ".join(text.split())
    if not normalized:
        return []

    sentences: list[str] = []
    start = 0
    for match in re.finditer(r"[.!?](?:[\"'\u201d\u2019]+)?", normalized):
        sentence = normalized[start : match.end()].strip()
        if sentence:
            sentences.append(sentence)
        start = match.end()
    tail = normalized[start:].strip()
    if tail:
        sentences.append(tail)
    return sentences


def chunk_blocks(
    blocks: Sequence[SpeechBlock], max_words: int
) -> list[SpeechChunk]:
    if max_words < 1:
        raise ValueError("max_words must be at least 1")

    chunks: list[SpeechChunk] = []
    for block in blocks:
        block_chunks: list[str] = []
        current_sentences: list[str] = []
        current_word_count = 0
        for sentence in split_sentences(block.text):
            sentence_word_count = len(sentence.split())
            if sentence_word_count > max_words:
                raise ValueError("A single sentence exceeds the word limit")
            if current_sentences and current_word_count + sentence_word_count > max_words:
                block_chunks.append(" ".join(current_sentences))
                current_sentences = []
                current_word_count = 0
            current_sentences.append(sentence)
            current_word_count += sentence_word_count
        if current_sentences:
            block_chunks.append(" ".join(current_sentences))
        chunks.extend(
            SpeechChunk(block.kind, text, index == len(block_chunks) - 1)
            for index, text in enumerate(block_chunks)
        )
    return chunks


def strip_front_matter(text: str) -> str:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        return text

    for index, line in enumerate(lines[1:], start=1):
        if line.rstrip("\r\n") == "---":
            return "".join(lines[index + 1 :])
    return text


def remove_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def strip_inline_markdown(text: str) -> str:
    code_spans: list[str] = []
    sentinel = "\0"
    while sentinel in text:
        sentinel += "\0"

    def protect_code_span(match: re.Match[str]) -> str:
        code_spans.append(match.group("content"))
        return f"{sentinel}{len(code_spans) - 1}{sentinel}"

    text = re.sub(
        r"(?P<delimiter>`+)(?P<content>.+?)(?P=delimiter)",
        protect_code_span,
        text,
    )
    text = re.sub(r"!\[([^]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"(?m)^\s*>\s?", "", text)
    text = text.replace("`", "")
    text = re.sub(r"(?<!\w)\*\*(?=\S)(.+?)(?<=\S)\*\*(?!\w)", r"\1", text)
    text = re.sub(r"(?<!\w)__(?=\S)(.+?)(?<=\S)__(?!\w)", r"\1", text)
    text = re.sub(
        r"(?<![\w_])([*_])(?!_)(?=\S)(.+?)(?<=\S)\1(?![\w_])",
        r"\2",
        text,
    )
    for index, code_span in enumerate(code_spans):
        text = text.replace(f"{sentinel}{index}{sentinel}", code_span)
    return " ".join(text.split())


def markdown_to_blocks(markdown: str) -> list[SpeechBlock]:
    blocks: list[SpeechBlock] = []
    prose_lines: list[str] = []

    def flush_prose() -> None:
        if prose_lines:
            text = strip_inline_markdown("\n".join(prose_lines))
            if text:
                blocks.append(SpeechBlock(BlockKind.PARAGRAPH, text))
            prose_lines.clear()

    prepared = remove_html_comments(strip_front_matter(markdown))
    for line in prepared.splitlines():
        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            flush_prose()
            kind = BlockKind.CHAPTER if len(heading.group(1)) == 1 else BlockKind.SECTION
            heading_text = re.sub(r"\s+#+\s*$", "", heading.group(2))
            text = strip_inline_markdown(heading_text)
            if text:
                blocks.append(SpeechBlock(kind, text))
        elif not line.strip():
            flush_prose()
        else:
            prose_lines.append(line.strip())
    flush_prose()
    return blocks


def extract_prose_excerpt(
    markdown: str, min_words: int = 400, max_words: int = 500
) -> str:
    selected: list[str] = []
    word_count = 0

    for block in markdown_to_blocks(markdown):
        if block.kind is not BlockKind.PARAGRAPH:
            continue
        paragraph_words = len(block.text.split())
        if word_count + paragraph_words > max_words:
            if word_count >= min_words:
                break
            raise ValueError("Cannot collect the minimum excerpt length within the maximum")
        selected.append(block.text)
        word_count += paragraph_words
        if word_count >= min_words:
            break

    if word_count < min_words:
        raise ValueError("Cannot collect the minimum excerpt length")
    return "\n\n".join(selected)
