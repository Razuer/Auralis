#!/usr/bin/env python3
"""Apply theme: merge accent + UI updates from theme.toml in one go.

This script replaces scripts/update_accent.py and scripts/update_config.py.
It will:
 - Load [accent] and [ui] from theme.toml
 - Update all files that contain special markers like `# accent:...`
 - Sync Hyprland rounding and required Waybar layerrules
 - Toggle Waybar floating styling using CSS markers

Idempotent and safe to run multiple times.
"""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable

try:  # Python 3.11+
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - fallback for Python <3.11
    import tomli as tomllib  # type: ignore


ROOT = Path(__file__).resolve().parent.parent
PALETTE_FILE = ROOT / "theme.toml"


HEX_PATTERN = re.compile(r"#([0-9a-fA-F]{6})")
RGBA_PATTERN = re.compile(r"rgba\(([0-9a-fA-F]{8})\)")


@dataclass
class Theme:
    primary: str  # #RRGGBB
    primary_bright: str  # #RRGGBB
    primary_rgba: str  # rgba(RRGGBBAA)
    secondary: str  # #RRGGBB
    secondary_rgba: str  # rgba(RRGGBBAA)
    secondary_bright: str  # #RRGGBB
    secondary_bright_rgba: str  # rgba(RRGGBBAA)
    tertiary: str
    tertiary_rgba: str
    tertiary_bright: str
    tertiary_bright_rgba: str
    quaternary: str
    quaternary_rgba: str
    quaternary_bright: str
    quaternary_bright_rgba: str
    quinary: str
    quinary_rgba: str
    quinary_bright: str
    quinary_bright_rgba: str
    rounding: int
    waybar_floating: bool
    waybar_border_radius: int
    waybar_padding: str
    waybar_margin: str


def normalize_hex(value: str) -> str:
    s = value.strip().lower()
    if not s.startswith("#"):
        s = f"#{s}"
    if not HEX_PATTERN.fullmatch(s):
        raise ValueError(f"Invalid hex colour: {value!r}")
    return s


def hex_to_rgba(hex_value: str) -> str:
    return f"rgba({hex_value.lstrip('#')}ff)"


def lighten(hex_value: str, factor: float = 0.2) -> str:
    base = normalize_hex(hex_value)
    rgb = [int(base[i : i + 2], 16) for i in (1, 3, 5)]
    adj = [min(255, round(ch + (255 - ch) * factor)) for ch in rgb]
    return "#" + "".join(f"{c:02x}" for c in adj)


def load_theme(
    accent_override: str | None = None,
    bright_override: str | None = None,
    secondary_override: str | None = None,
    secondary_bright_override: str | None = None,
    tertiary_override: str | None = None,
    tertiary_bright_override: str | None = None,
    quaternary_override: str | None = None,
    quaternary_bright_override: str | None = None,
    quinary_override: str | None = None,
    quinary_bright_override: str | None = None,
    rounding_override: int | None = None,
    waybar_floating_override: bool | None = None,
    waybar_border_radius_override: int | None = None,
    waybar_padding_override: str | None = None,
    waybar_margin_override: str | None = None,
) -> Theme:
    if not PALETTE_FILE.is_file():
        raise FileNotFoundError(
            "theme.toml is missing; create it before running this script."
        )

    with PALETTE_FILE.open("rb") as fh:
        data = tomllib.load(fh)

    acc = data.get("accent", {})
    ui = data.get("ui", {})

    primary = normalize_hex(accent_override or acc.get("primary") or "#7dd6f6")
    bright = normalize_hex(
        bright_override or acc.get("primary_bright") or lighten(primary)
    )
    secondary = normalize_hex(secondary_override or acc.get("secondary") or primary)
    secondary_bright = normalize_hex(
        secondary_bright_override or acc.get("secondary_bright") or lighten(secondary)
    )
    tertiary = normalize_hex(tertiary_override or acc.get("tertiary") or "#66cc66")
    tertiary_bright = normalize_hex(
        tertiary_bright_override or acc.get("tertiary_bright") or lighten(tertiary)
    )
    quaternary = normalize_hex(
        quaternary_override or acc.get("quaternary") or "#e65c5c"
    )
    quaternary_bright = normalize_hex(
        quaternary_bright_override
        or acc.get("quaternary_bright")
        or lighten(quaternary)
    )
    quinary = normalize_hex(quinary_override or acc.get("quinary") or "#ffcc66")
    quinary_bright = normalize_hex(
        quinary_bright_override or acc.get("quinary_bright") or lighten(quinary)
    )

    rounding = int(
        rounding_override if rounding_override is not None else ui.get("rounding", 10)
    )
    waybar_floating = bool(
        waybar_floating_override
        if waybar_floating_override is not None
        else ui.get("waybar_floating", True)
    )
    waybar_border_radius = int(
        waybar_border_radius_override
        if waybar_border_radius_override is not None
        else ui.get("waybar_border_radius", 12)
    )
    waybar_padding = str(
        waybar_padding_override
        if waybar_padding_override is not None
        else ui.get("waybar_padding", "3px 4px")
    )
    waybar_margin = str(
        waybar_margin_override
        if waybar_margin_override is not None
        else ui.get("waybar_margin", "4px 6px")
    )

    return Theme(
        primary=primary,
        primary_bright=bright,
        primary_rgba=hex_to_rgba(primary),
        secondary=secondary,
        secondary_rgba=hex_to_rgba(secondary),
        secondary_bright=secondary_bright,
        secondary_bright_rgba=hex_to_rgba(secondary_bright),
        tertiary=tertiary,
        tertiary_rgba=hex_to_rgba(tertiary),
        tertiary_bright=tertiary_bright,
        tertiary_bright_rgba=hex_to_rgba(tertiary_bright),
        quaternary=quaternary,
        quaternary_rgba=hex_to_rgba(quaternary),
        quaternary_bright=quaternary_bright,
        quaternary_bright_rgba=hex_to_rgba(quaternary_bright),
        quinary=quinary,
        quinary_rgba=hex_to_rgba(quinary),
        quinary_bright=quinary_bright,
        quinary_bright_rgba=hex_to_rgba(quinary_bright),
        rounding=rounding,
        waybar_floating=waybar_floating,
        waybar_border_radius=waybar_border_radius,
        waybar_padding=waybar_padding,
        waybar_margin=waybar_margin,
    )


# ---------- Accent propagation ----------

ACCENT_MARKERS: tuple[tuple[str, str], ...] = (
    # Primary: check more specific markers before generic ones
    ("accent:primary-rgba", "primary_rgba"),
    ("accent:primary-bright", "primary_bright"),
    ("accent:primary", "primary"),
    # Secondary: ensure '-bright' is matched before base to avoid substring collisions
    ("accent:secondary-bright-rgba", "secondary_bright_rgba"),
    ("accent:secondary-bright", "secondary_bright"),
    ("accent:secondary-rgba", "secondary_rgba"),
    ("accent:secondary", "secondary"),
    # Tertiary
    ("accent:tertiary-bright-rgba", "tertiary_bright_rgba"),
    ("accent:tertiary-bright", "tertiary_bright"),
    ("accent:tertiary-rgba", "tertiary_rgba"),
    ("accent:tertiary", "tertiary"),
    # Quaternary
    ("accent:quaternary-bright-rgba", "quaternary_bright_rgba"),
    ("accent:quaternary-bright", "quaternary_bright"),
    ("accent:quaternary-rgba", "quaternary_rgba"),
    ("accent:quaternary", "quaternary"),
    # Quinary
    ("accent:quinary-bright-rgba", "quinary_bright_rgba"),
    ("accent:quinary-bright", "quinary_bright"),
    ("accent:quinary-rgba", "quinary_rgba"),
    ("accent:quinary", "quinary"),
)

# Mapping for quick marker/token -> Theme attribute lookup
ACCENT_MAP: dict[str, str] = {}
for _marker, _key in ACCENT_MARKERS:
    ACCENT_MAP[_marker] = _key
    _token = _marker.split(":", 1)[1]
    ACCENT_MAP[_token] = _key


def replace_first(
    pattern: re.Pattern[str], line: str, replacement: str
) -> tuple[str, bool]:
    m = pattern.search(line)
    if not m:
        return line, False
    a, b = m.span()
    # If the existing substring already equals the replacement, don't mark as changed
    if line[a:b] == replacement:
        return line, False
    return f"{line[:a]}{replacement}{line[b:]}", True


def update_line_with_accent(line: str, theme: Theme) -> tuple[str, bool]:
    for marker, key in ACCENT_MARKERS:
        if marker not in line:
            continue
        # Use RGBA replacement for any key that specifies an RGBA value
        if key.endswith("_rgba"):
            return replace_first(RGBA_PATTERN, line, getattr(theme, key))
        # Otherwise replace the first hex color occurrence
        return replace_first(HEX_PATTERN, line, getattr(theme, key))
    return line, False


def iter_theme_files() -> Iterable[Path]:
    skip_suffixes = {".png", ".jpg", ".jpeg", ".gif"}
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() not in skip_suffixes:
            yield path


def apply_accent(theme: Theme) -> list[Path]:
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
        pending_marker: str | None = None
        for i, line in enumerate(lines):
            # 1) Inline marker on the same line
            new_line, altered = update_line_with_accent(line, theme)
            if altered:
                lines[i] = new_line
                changed = True
                pending_marker = None
                continue

            # 2) Standalone marker line like: '# accent:primary'
            m = re.search(r"(^|\s)#\s*accent:([a-z0-9_-]+)", line, re.IGNORECASE)
            if (
                m
                and HEX_PATTERN.search(line) is None
                and RGBA_PATTERN.search(line) is None
            ):
                token = m.group(2).lower()
                if token in ACCENT_MAP:
                    pending_marker = token
                continue

            # 3) Apply pending marker to next line that contains a color token
            if pending_marker:
                # Only consume the marker when we hit a line that contains a color token
                has_hex = HEX_PATTERN.search(line) is not None
                has_rgba = RGBA_PATTERN.search(line) is not None
                if has_hex or has_rgba:
                    key = ACCENT_MAP[pending_marker]
                    repl = getattr(theme, key)
                    if key.endswith("_rgba"):
                        new_line2, altered2 = replace_first(RGBA_PATTERN, line, repl)
                    else:
                        new_line2, altered2 = replace_first(HEX_PATTERN, line, repl)
                    if altered2:
                        lines[i] = new_line2
                        changed = True
                    # Consume the marker regardless of whether a change was needed
                    pending_marker = None
        if changed:
            path.write_text(
                "\n".join(lines) + ("\n" if text.endswith("\n") else ""),
                encoding="utf-8",
            )
            updated.append(path.relative_to(ROOT))
    return updated


# ---------- UI updates ----------


def ensure_hypr_rounding(rounding: int) -> list[Path]:
    updated: list[Path] = []
    hypr = ROOT / "hyprland.conf"
    if not hypr.exists():
        return updated
    text = hypr.read_text(encoding="utf-8")
    pat = re.compile(r"(rounding\s*=\s*)\d+(\s*#\s*config:rounding)")
    if pat.search(text):
        new = pat.sub(rf"\g<1>{rounding}\g<2>", text)
        if new != text:
            hypr.write_text(new, encoding="utf-8")
            updated.append(hypr.relative_to(ROOT))
    return updated


def ensure_hypr_waybar_layerrules() -> list[Path]:
    updated: list[Path] = []
    hypr = ROOT / "hyprland.conf"
    if not hypr.exists():
        return updated
    text = hypr.read_text(encoding="utf-8")
    need = [
        "layerrule = blur, waybar",
        "layerrule = ignorezero, waybar",
    ]
    changed = False
    for rule in need:
        if rule not in text:
            text += ("\n" if not text.endswith("\n") else "") + rule + "\n"
            changed = True
    if changed:
        hypr.write_text(text, encoding="utf-8")
        updated.append(hypr.relative_to(ROOT))
    return updated


def update_waybar_floating(theme: Theme) -> list[Path]:
    """Toggle floating CSS lines that are marked with config comments.

    We operate only on lines containing these markers inside waybar.css:
      - config:waybar_floating:border-radius
      - config:waybar_floating:padding
      - config:waybar_floating:margin
    """
    updated: list[Path] = []
    css = ROOT / "waybar.css"
    if not css.exists():
        return updated
    text = css.read_text(encoding="utf-8")
    original_text = text

    def edit_waybar_block(edit_fn) -> None:
        nonlocal text
        m = re.search(r"(window#waybar\s*>\s*box\s*\{)([^}]*)\}", text, re.DOTALL)
        if not m:
            return
        head_start, head_end = m.span(1)
        body_start, body_end = m.span(2)
        body = text[body_start:body_end]
        body_lines = body.splitlines(True)

        def find_line_with_marker(marker: str) -> int:
            for idx, ln in enumerate(body_lines):
                if marker in ln:
                    return idx
            return -1

        def insert_after_background(new_line: str) -> None:
            for idx, ln in enumerate(body_lines):
                if re.search(r"background-color:\s*[^;]+;", ln):
                    body_lines.insert(idx + 1, new_line)
                    return
            body_lines.append(new_line)

        def set_prop(prop: str, value: str, marker: str) -> None:
            target = f" /* {marker} */\n"
            i = find_line_with_marker(marker)
            if i >= 0:
                indent = re.match(r"\s*", body_lines[i]).group(0)
                body_lines[i] = f"{indent}{prop}: {value};{target}"
            else:
                insert_after_background(f"    {prop}: {value};{target}")

        def remove_marker_lines(markers: list[str]) -> None:
            nonlocal body_lines
            body_lines = [
                ln for ln in body_lines if not any(mk in ln for mk in markers)
            ]

        edit_fn(set_prop, remove_marker_lines)

        new_body = "".join(body_lines)
        text = text[:body_start] + new_body + text[body_end:]

    if theme.waybar_floating:

        def editor(set_prop, remove_marker_lines):
            set_prop(
                "border-radius",
                f"{theme.waybar_border_radius}px",
                "config:waybar_floating:border-radius",
            )
            set_prop("padding", theme.waybar_padding, "config:waybar_floating:padding")
            set_prop("margin", theme.waybar_margin, "config:waybar_floating:margin")

        edit_waybar_block(editor)
    else:

        def editor(set_prop, remove_marker_lines):
            remove_marker_lines(
                [
                    "config:waybar_floating:border-radius",
                    "config:waybar_floating:padding",
                    "config:waybar_floating:margin",
                ]
            )

        edit_waybar_block(editor)

    if text != original_text:
        css.write_text(text, encoding="utf-8")
        updated.append(css.relative_to(ROOT))
    return updated


def update_theme_file(theme: Theme) -> None:
    """Rewrite theme.toml [accent] and preserve other sections like [ui]."""
    existing_ui: Dict[str, Any] | None = None
    if PALETTE_FILE.exists():
        try:
            with PALETTE_FILE.open("rb") as fh:
                data = tomllib.load(fh)
                existing_ui = data.get("ui")
        except Exception:
            existing_ui = None

    lines: list[str] = [
        "# Theme configuration (colors + UI)",
        "# Managed by scripts/apply_theme.py",
        "",
        "[accent]",
        f'primary = "{theme.primary}"',
        f'primary_bright = "{theme.primary_bright}"',
        f'secondary = "{theme.secondary}"',
        f'secondary_bright = "{theme.secondary_bright}"',
        f'tertiary = "{theme.tertiary}"',
        f'tertiary_bright = "{theme.tertiary_bright}"',
        f'quaternary = "{theme.quaternary}"',
        f'quaternary_bright = "{theme.quaternary_bright}"',
        f'quinary = "{theme.quinary}"',
        f'quinary_bright = "{theme.quinary_bright}"',
        "",
    ]
    if isinstance(existing_ui, dict):
        lines.append("[ui]")
        lines.append(f"rounding = {int(theme.rounding)}  # config:rounding")
        lines.append("\n# Waybar style")
        lines.append(
            f"waybar_floating = {str(theme.waybar_floating).lower()}  # config:waybar_floating"
        )
        lines.append(
            f"waybar_border_radius = {int(theme.waybar_border_radius)}  # config:waybar_floating:border-radius"
        )
        lines.append(
            f'waybar_padding = "{theme.waybar_padding}"  # config:waybar_floating:padding'
        )
        lines.append(
            f'waybar_margin = "{theme.waybar_margin}"  # config:waybar_floating:margin'
        )
        lines.append("")

    PALETTE_FILE.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Apply Omarchy theme (accent + UI) from theme.toml"
    )
    p.add_argument("--accent", help="Override accent.primary (#RRGGBB)")
    p.add_argument("--accent-bright", help="Override accent.primary_bright (#RRGGBB)")
    p.add_argument("--accent-secondary", help="Override accent.secondary (#RRGGBB)")
    p.add_argument(
        "--accent-secondary-bright", help="Override accent.secondary_bright (#RRGGBB)"
    )
    p.add_argument("--accent-tertiary", help="Override accent.tertiary (#RRGGBB)")
    p.add_argument(
        "--accent-tertiary-bright", help="Override accent.tertiary_bright (#RRGGBB)"
    )
    p.add_argument("--accent-quaternary", help="Override accent.quaternary (#RRGGBB)")
    p.add_argument(
        "--accent-quaternary-bright",
        help="Override accent.quaternary_bright (#RRGGBB)",
    )
    p.add_argument("--accent-quinary", help="Override accent.quinary (#RRGGBB)")
    p.add_argument(
        "--accent-quinary-bright", help="Override accent.quinary_bright (#RRGGBB)"
    )
    p.add_argument("--rounding", type=int, help="Set window rounding (0..30)")
    p.add_argument(
        "--waybar-floating",
        type=lambda x: x.lower() in {"true", "1", "yes"},
        help="Enable/disable Waybar floating",
    )
    p.add_argument(
        "--waybar-border-radius",
        type=int,
        help="Set Waybar border-radius in pixels (e.g., 12)",
    )
    p.add_argument(
        "--waybar-padding",
        help="Set Waybar padding (e.g., '3px 4px')",
    )
    p.add_argument(
        "--waybar-margin",
        help="Set Waybar margin (e.g., '4px 6px')",
    )
    p.add_argument(
        "--skip-palette",
        action="store_true",
        help="Do not rewrite theme.toml with computed values",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    theme = load_theme(
        args.accent,
        args.accent_bright,
        args.accent_secondary,
        args.accent_secondary_bright,
        args.accent_tertiary,
        args.accent_tertiary_bright,
        args.accent_quaternary,
        args.accent_quaternary_bright,
        args.accent_quinary,
        args.accent_quinary_bright,
        args.rounding,
        args.waybar_floating,
        args.waybar_border_radius,
        args.waybar_padding,
        args.waybar_margin,
    )

    updated: list[Path] = []
    updated += apply_accent(theme)
    updated += ensure_hypr_rounding(theme.rounding)
    updated += ensure_hypr_waybar_layerrules()
    updated += update_waybar_floating(theme)

    if not args.skip_palette:
        update_theme_file(theme)

    if updated:
        print("Applied theme updates in:")
        for p in updated:
            print(f" - {p}")
        print("\nReminder: reload to apply:")
        print("  hyprctl reload")
        print("  killall waybar && waybar &  # or pkill -SIGUSR2 waybar")
        print("  makoctl reload  # if using mako")
    else:
        print("No files required updates.")


if __name__ == "__main__":
    main()
