from dataclasses import dataclass
from enum import Enum
import re


_PYTHON_DUNDER_IDENTIFIERS = frozenset(
    {
        "__all__",
        "__bool__",
        "__call__",
        "__class__",
        "__contains__",
        "__del__",
        "__delattr__",
        "__delitem__",
        "__dict__",
        "__dir__",
        "__doc__",
        "__enter__",
        "__eq__",
        "__exit__",
        "__file__",
        "__format__",
        "__getattr__",
        "__getitem__",
        "__hash__",
        "__init__",
        "__iter__",
        "__len__",
        "__main__",
        "__module__",
        "__name__",
        "__ne__",
        "__new__",
        "__next__",
        "__repr__",
        "__setattr__",
        "__setitem__",
        "__slots__",
        "__str__",
        "__version__",
    }
)


class BlockKind(str, Enum):
    CHAPTER = "chapter"
    SECTION = "section"
    PARAGRAPH = "paragraph"


@dataclass(frozen=True)
class SpeechBlock:
    kind: BlockKind
    text: str


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
    text = re.sub(r"!\[([^]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"(?m)^\s*>\s?", "", text)
    text = text.replace("`", "")
    text = re.sub(r"(?<!\w)\*\*(?=\S)(.+?)(?<=\S)\*\*(?!\w)", r"\1", text)
    text = re.sub(
        r"(?<!\w)__(?=\S)(.+?)(?<=\S)__(?!\w)",
        _strip_double_underscore_emphasis,
        text,
    )
    text = re.sub(
        r"(?<![\w_])([*_])(?!_)(?=\S)(.+?)(?<=\S)\1(?![\w_])",
        r"\2",
        text,
    )
    return " ".join(text.split())


def _strip_double_underscore_emphasis(match: re.Match[str]) -> str:
    if match.group(0) in _PYTHON_DUNDER_IDENTIFIERS:
        return match.group(0)
    return match.group(1)


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
