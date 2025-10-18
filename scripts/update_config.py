#!/usr/bin/env python3
"""Update UI configuration values across theme files based on palette.toml."""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, Any

try:  # Python 3.11+
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - fallback for Python <3.11
    import tomli as tomllib  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
PALETTE_FILE = ROOT / "palette.toml"


def load_config() -> Dict[str, Any]:
    """Load configuration from palette.toml."""
    if not PALETTE_FILE.is_file():
        raise FileNotFoundError("palette.toml is missing; create it before running this script.")

    with PALETTE_FILE.open("rb") as fh:
        data = tomllib.load(fh)

    return data.get("ui", {})


def update_rounding(config: Dict[str, Any]) -> list[Path]:
    """Update rounding value in Hyprland config."""
    rounding = config.get("rounding", 10)
    updated = []
    
    hyprland_conf = ROOT / "hyprland.conf"
    if not hyprland_conf.exists():
        return updated
    
    text = hyprland_conf.read_text(encoding="utf-8")
    pattern = re.compile(r"(rounding\s*=\s*)\d+(\s*#\s*config:rounding)")
    
    if pattern.search(text):
        new_text = pattern.sub(rf"\g<1>{rounding}\g<2>", text)
        if new_text != text:
            hyprland_conf.write_text(new_text, encoding="utf-8")
            updated.append(hyprland_conf.relative_to(ROOT))
    
    return updated


def update_waybar_floating(config: Dict[str, Any]) -> list[Path]:
    """Update Waybar floating style."""
    floating = config.get("waybar_floating", True)
    updated = []
    
    waybar_css = ROOT / "waybar.css"
    if not waybar_css.exists():
        return updated
    
    text = waybar_css.read_text(encoding="utf-8")
    
    if floating:
        # Apply floating style (with markers)
        margin_pattern = re.compile(
            r"(#waybar\s*\{[^}]*?)(margin:\s*[^;]*;\s*/\*\s*config:waybar_floating:margin\s*\*/)",
            re.DOTALL
        )
        border_pattern = re.compile(
            r"(border-radius:\s*[^;]*;\s*/\*\s*config:waybar_floating:border-radius\s*\*/)"
        )
        padding_pattern = re.compile(
            r"(padding:\s*[^;]*;\s*/\*\s*config:waybar_floating:padding\s*\*/)"
        )
        
        # Check if markers exist but are commented out
        if "/* config:waybar_floating:margin */" not in text:
            # Add floating styles
            text = re.sub(
                r"(#waybar\s*\{\s*\n\s*background-color:\s*@waybarBg;)",
                r"\1\n    margin: 8px 12px 0px 12px;  /* config:waybar_floating:margin */\n    border-radius: 10px;  /* config:waybar_floating:border-radius */\n    padding: 0px 8px;  /* config:waybar_floating:padding */",
                text
            )
    else:
        # Remove floating style (comment out or remove lines with markers)
        text = re.sub(
            r"\s*margin:\s*[^;]*;\s*/\*\s*config:waybar_floating:margin\s*\*/\n?",
            "",
            text
        )
        text = re.sub(
            r"\s*border-radius:\s*[^;]*;\s*/\*\s*config:waybar_floating:border-radius\s*\*/\n?",
            "",
            text
        )
        text = re.sub(
            r"\s*padding:\s*[^;]*;\s*/\*\s*config:waybar_floating:padding\s*\*/\n?",
            "",
            text
        )
    
    waybar_css.write_text(text, encoding="utf-8")
    updated.append(waybar_css.relative_to(ROOT))
    
    return updated


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update UI configuration across theme files.")
    parser.add_argument("--rounding", type=int, help="Set window rounding (0 = square, 10 = rounded)")
    parser.add_argument(
        "--waybar-floating",
        type=lambda x: x.lower() in ["true", "yes", "1"],
        help="Enable/disable Waybar floating style (true/false)",
    )
    parser.add_argument(
        "--skip-palette",
        action="store_true",
        help="Do not rewrite palette.toml with new values",
    )
    return parser.parse_args()


def update_palette_file(rounding: int | None, waybar_floating: bool | None) -> None:
    """Update palette.toml with new values."""
    text = PALETTE_FILE.read_text(encoding="utf-8")
    
    if rounding is not None:
        text = re.sub(
            r"(rounding\s*=\s*)\d+(\s*#\s*config:rounding)",
            rf"\g<1>{rounding}\g<2>",
            text
        )
    
    if waybar_floating is not None:
        text = re.sub(
            r"(waybar_floating\s*=\s*)(true|false)(\s*#\s*config:waybar_floating)",
            rf"\g<1>{str(waybar_floating).lower()}\g<3>",
            text
        )
    
    PALETTE_FILE.write_text(text, encoding="utf-8")


def main() -> None:
    args = parse_args()
    
    # Load current config or use overrides
    config = load_config()
    
    if args.rounding is not None:
        config["rounding"] = args.rounding
    if args.waybar_floating is not None:
        config["waybar_floating"] = args.waybar_floating
    
    updated_files = []
    
    # Update files
    updated_files.extend(update_rounding(config))
    updated_files.extend(update_waybar_floating(config))
    
    # Update palette.toml if needed
    if not args.skip_palette and (args.rounding is not None or args.waybar_floating is not None):
        update_palette_file(args.rounding, args.waybar_floating)
    
    if updated_files:
        print("Updated configuration in:")
        for path in updated_files:
            print(f" - {path}")
        print("\nReload Hyprland and Waybar to apply changes:")
        print("  hyprctl reload")
        print("  killall waybar && waybar &")
    else:
        print("No files required updates.")


if __name__ == "__main__":
    main()
