"""String manipulation REST API — auto-generated for 2026-05-17."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import re
import textwrap

router = APIRouter(prefix="/string_manipulation", tags=["string_manipulation"])


# ── Models ────────────────────────────────────────────────────────────────────

class TextInput(BaseModel):
    text: str


class WrapInput(BaseModel):
    text: str
    width: int = 80


class ReplaceInput(BaseModel):
    text: str
    pattern: str
    replacement: str
    use_regex: bool = False


class CaseResponse(BaseModel):
    original: str
    upper: str
    lower: str
    title: str
    snake_case: str
    camel_case: str
    kebab_case: str


class StatsResponse(BaseModel):
    characters: int
    characters_no_spaces: int
    words: int
    sentences: int
    lines: int
    unique_words: int
    most_common_word: str


class WrapResponse(BaseModel):
    original: str
    wrapped: str
    line_count: int


class ReplaceResponse(BaseModel):
    original: str
    result: str
    replacements_made: int


# ── Helpers ───────────────────────────────────────────────────────────────────

def to_snake_case(text: str) -> str:
    text = re.sub(r"[\s\-]+", "_", text.strip())
    text = re.sub(r"([A-Z])", r"_\1", text).lstrip("_")
    return re.sub(r"_+", "_", text).lower()


def to_camel_case(text: str) -> str:
    words = re.split(r"[\s_\-]+", text.strip())
    return words[0].lower() + "".join(w.capitalize() for w in words[1:])


def to_kebab_case(text: str) -> str:
    return to_snake_case(text).replace("_", "-")


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/cases", response_model=CaseResponse, summary="Convert text to multiple case formats")
def convert_cases(body: TextInput):
    """
    Accept a string and return it transformed into six common case formats:
    UPPER, lower, Title, snake_case, camelCase, and kebab-case.
    """
    text = body.text
    if not text.strip():
        raise HTTPException(status_code=422, detail="text must not be blank")

    return CaseResponse(
        original=text,
        upper=text.upper(),
        lower=text.lower(),
        title=text.title(),
        snake_case=to_snake_case(text),
        camel_case=to_camel_case(text),
        kebab_case=to_kebab_case(text),
    )


@router.post("/stats", response_model=StatsResponse, summary="Compute text statistics")
def text_stats(body: TextInput):
    """
    Return character count, word count, sentence count, line count,
    unique-word count, and the most frequent word for the given text.
    """
    text = body.text
    if not text:
        raise HTTPException(status_code=422, detail="text must not be empty")

    words_raw = re.findall(r"\b\w+\b", text.lower())
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

    freq: dict[str, int] = {}
    for w in words_raw:
        freq[w] = freq.get(w, 0) + 1
    most_common = max(freq, key=lambda k: freq[k]) if freq else ""

    return StatsResponse(
        characters=len(text),
        characters_no_spaces=len(text.replace(" ", "")),
        words=len(words_raw),
        sentences=len(sentences),
        lines=len(text.splitlines()),
        unique_words=len(freq),
        most_common_word=most_common,
    )


@router.post("/wrap", response_model=WrapResponse, summary="Word-wrap text to a given column width")
def wrap_text(body: WrapInput):
    """
    Wrap the input text so that no line exceeds `width` characters (default 80).
    Returns the wrapped text and the resulting line count.
    """
    if body.width < 1:
        raise HTTPException(status_code=422, detail="width must be at least 1")
    if not body.text:
        raise HTTPException(status_code=422, detail="text must not be empty")

    wrapped = textwrap.fill(body.text, width=body.width)
    return WrapResponse(
        original=body.text,
        wrapped=wrapped,
        line_count=len(wrapped.splitlines()),
    )


@router.post("/replace", response_model=ReplaceResponse, summary="Find-and-replace in text (literal or regex)")
def find_replace(body: ReplaceInput):
    """
    Replace occurrences of `pattern` with `replacement` inside `text`.
    Set `use_regex: true` to treat `pattern` as a regular expression;
    otherwise a plain literal replacement is performed.
    Returns the modified string and the number of replacements made.
    """
    if not body.text:
        raise HTTPException(status_code=422, detail="text must not be empty")

    try:
        if body.use_regex:
            result, count = re.subn(body.pattern, body.replacement, body.text)
        else:
            count = body.text.count(body.pattern)
            result = body.text.replace(body.pattern, body.replacement)
    except re.error as exc:
        raise HTTPException(status_code=422, detail=f"Invalid regex: {exc}") from exc

    return ReplaceResponse(
        original=body.text,
        result=result,
        replacements_made=count,
    )
