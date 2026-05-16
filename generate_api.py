import anthropic
import os
import re
import sys
from datetime import date

THEMES = [
    "text_processing",
    "math_and_statistics",
    "date_and_time",
    "string_manipulation",
    "data_validation",
    "encoding_utilities",
    "unit_conversion",
    "password_utilities",
    "random_data_generation",
    "list_utilities",
    "number_theory",
    "color_utilities",
    "file_utilities",
    "hashing_utilities",
    "weather_simulation",
    "geography_utilities",
    "networking_utilities",
    "currency_utilities",
    "sorting_algorithms",
    "search_utilities",
    "regex_utilities",
    "base_conversion",
    "roman_numerals",
    "prime_numbers",
    "fibonacci_utilities",
]

SYSTEM_PROMPT = """You are an expert Python developer. Generate production-quality FastAPI router code.
Output ONLY valid Python code — no markdown fences, no explanations, no comments outside the code itself."""

USER_PROMPT_TEMPLATE = """Generate a FastAPI router module for the theme: "{theme}".

Requirements:
- Import `from fastapi import APIRouter` and create `router = APIRouter(prefix="/{theme}", tags=["{theme}"])`
- Include exactly 4 REST endpoints (GET, POST, or a mix) that are genuinely useful for this theme
- Use Pydantic BaseModel for any request/response bodies
- Add clear docstrings to each endpoint
- All logic must be self-contained (no external API calls, no file I/O, no databases)
- Use proper HTTP status codes and type hints throughout

Output only the Python code."""


def pick_theme(today: date) -> str:
    return THEMES[today.toordinal() % len(THEMES)]


def strip_code_fences(text: str) -> str:
    text = re.sub(r"^```python\s*", "", text.strip())
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def generate_router(theme: str) -> str:
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": USER_PROMPT_TEMPLATE.format(theme=theme),
            }
        ],
    )
    return strip_code_fences(message.content[0].text)


def write_router(theme: str, code: str, today: date) -> str:
    filename = f"{today.strftime('%Y_%m_%d')}_{theme}.py"
    path = os.path.join("api", "routes", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(code + "\n")
    return path


def regenerate_main():
    routes_dir = os.path.join("api", "routes")
    route_files = sorted(
        f for f in os.listdir(routes_dir)
        if f.endswith(".py") and f != "__init__.py"
    )

    import_lines = []
    include_lines = []
    for i, fname in enumerate(route_files):
        module = fname[:-3]
        alias = f"r{i}"
        import_lines.append(f"from api.routes.{module} import router as {alias}")
        include_lines.append(f"app.include_router({alias})")

    main_src = (
        '"""Auto-generated FastAPI application — new endpoint added daily."""\n'
        "from fastapi import FastAPI\n"
        + "\n".join(import_lines)
        + "\n\n"
        "app = FastAPI(\n"
        '    title="KSRRtech Experimenting API",\n'
        '    description="Daily auto-generated public REST API endpoints powered by Claude.",\n'
        '    version="1.0.0",\n'
        ")\n\n"
        "@app.get('/', tags=['root'])\n"
        "def root():\n"
        '    """API index — lists available route prefixes."""\n'
        "    return {\n"
        '        "message": "Welcome to KSRRtech Experimenting API",\n'
        '        "docs": "/docs",\n'
        '        "total_route_modules": ' + str(len(route_files)) + ",\n"
        "    }\n\n"
        + "\n".join(include_lines)
        + "\n"
    )

    with open(os.path.join("api", "main.py"), "w", encoding="utf-8") as f:
        f.write(main_src)


def main():
    today = date.today()
    theme = pick_theme(today)
    print(f"Theme for {today}: {theme}")

    print("Calling Claude API...")
    code = generate_router(theme)

    path = write_router(theme, code, today)
    print(f"Written: {path}")

    regenerate_main()
    print("Updated api/main.py")


if __name__ == "__main__":
    main()
