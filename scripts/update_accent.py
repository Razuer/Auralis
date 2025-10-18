#!/usr/bin/env python3
"""Update accent color values across theme files based on theme.toml."""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, Iterable

try:  # Python 3.11+
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - fallback for Python <3.11
    import tomli as tomllib  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
PALETTE_FILE = ROOT / "theme.toml"

# Markers that we search for inside files. The first match in a line is replaced.
ACCENT_MARKERS = (
    ("accent:primary-rgba", "primary_rgba"),
    ("accent:primary-bright", "primary_bright"),
    ("accent:primary", "primary"),
)

HEX_PATTERN = re.compile(r"#([0-9a-fA-F]{6})")
RGBA_PATTERN = re.compile(r"rgba\(([0-9a-fA-F]{8})\)")


def normalize_hex(value: str) -> str:
    """Return a lower-case #RRGGBB string."""
    stripped = value.strip().lower()
    if not stripped.startswith("#"):
        stripped = f"#{stripped}"
    if not HEX_PATTERN.fullmatch(stripped):
        raise ValueError(f"Invalid hex colour: {value!r}")
    return stripped


def hex_to_rgba(hex_value: str) -> str:
    return f"rgba({hex_value.lstrip('#')}ff)"


def lighten(hex_value: str, factor: float = 0.2) -> str:
    """Return a lighter #RRGGBB string using the given factor (0..1)."""
    base = normalize_hex(hex_value)
    rgb = [int(base[i : i + 2], 16) for i in (1, 3, 5)]
    adjusted = [min(255, round(channel + (255 - channel) * factor)) for channel in rgb]
    return "#" + "".join(f"{channel:02x}" for channel in adjusted)


def load_palette(
    accent_override: str | None, bright_override: str | None
) -> Dict[str, str]:
    if not PALETTE_FILE.is_file():
        raise FileNotFoundError(
            "theme.toml is missing; create it before running this script."
        )

    with PALETTE_FILE.open("rb") as fh:
        data = tomllib.load(fh)

    accent = data.get("accent", {})
    primary = accent_override or accent.get("primary")
    if primary is None:
        raise ValueError("accent.primary is not defined in theme.toml")

    bright = bright_override or accent.get("primary_bright")
    primary_hex = normalize_hex(primary)
    bright_hex = normalize_hex(bright) if bright else lighten(primary_hex)

    return {
        "primary": primary_hex,
        "primary_bright": bright_hex,
        "primary_rgba": hex_to_rgba(primary_hex),
    }


def replace_first(
    pattern: re.Pattern[str], line: str, replacement: str
) -> tuple[str, bool]:
    match = pattern.search(line)
    if not match:
        return line, False
    start, end = match.span()
    return f"{line[:start]}{replacement}{line[end:]}", True


def update_line(line: str, colours: Dict[str, str]) -> tuple[str, bool]:
    for marker, key in ACCENT_MARKERS:
        if marker not in line:
            continue
        if key == "primary_rgba":
            return replace_first(RGBA_PATTERN, line, colours[key])
        return replace_first(HEX_PATTERN, line, colours[key])
    return line, False


def iter_theme_files() -> Iterable[Path]:
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() not in {
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
        }:
            yield path


def apply_updates(colours: Dict[str, str]) -> list[Path]:
    updated: list[Path] = []
    for path in iter_theme_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "accent:" not in text:
            continue

        lines = text.splitlines()
        changed = False
        for idx, line in enumerate(lines):
            new_line, altered = update_line(line, colours)
            if altered:
                lines[idx] = new_line
                changed = True
        if changed:
            newline = "\n" if text.endswith("\n") else ""
            path.write_text("\n".join(lines) + newline, encoding="utf-8")
            updated.append(path.relative_to(ROOT))
    return updated


def update_palette_file(colours: Dict[str, str]) -> None:
    """Rewrite theme.toml [accent] while preserving other sections like [ui]."""
    existing_ui = None
    if PALETTE_FILE.exists():
        try:
            with PALETTE_FILE.open("rb") as fh:
                data = tomllib.load(fh)
                existing_ui = data.get("ui")
        except Exception:
            existing_ui = None

    lines: list[str] = [
        "# Theme configuration (colors + UI)",
        "",
        "[accent]",
        f"primary = \"{colours['primary']}\"",
        f"primary_bright = \"{colours['primary_bright']}\"",
        "",
    ]
    if isinstance(existing_ui, dict):
        lines.append("[ui]")
        # preserve known keys with inline markers if present
        rounding = existing_ui.get("rounding")
        if rounding is not None:
            lines.append(f"rounding = {int(rounding)}  # config:rounding")
        waybar_floating = existing_ui.get("waybar_floating")
        if waybar_floating is not None:
            val = str(bool(waybar_floating)).lower()
            lines.append(f"\n# Waybar style")
            lines.append(f"waybar_floating = {val}  # config:waybar_floating")
        lines.append("")

    PALETTE_FILE.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update accent colour across theme files."
    )
    parser.add_argument(
        "--accent", help="Override accent.primary with a new #RRGGBB value"
    )
    parser.add_argument(
        "--accent-bright",
        help="Override accent.primary_bright with a new #RRGGBB value",
    )
    parser.add_argument(
        "--skip-palette",
        action="store_true",
    help="Do not rewrite theme.toml (useful for dry runs)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    colours = load_palette(args.accent, args.accent_bright)

    updated_files = apply_updates(colours)
    if not args.skip_palette:
        update_palette_file(colours)

    if updated_files:
        print("Updated accent colour in:")
        for path in updated_files:
            print(f" - {path}")
    else:
        print("No files required updates.")


if __name__ == "__main__":
    main()
