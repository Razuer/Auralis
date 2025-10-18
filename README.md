# Ayaka Theme - Customizable Edition

A personalized variant of the [Ayaka Theme](https://github.com/abhijeet-swami/omarchy-ayaka-theme) for Omarchy Linux, designed for easy customization and accent color personalization.

This theme builds upon the original Ayaka's elegant dark foundation while introducing an automated accent system that makes it effortless to personalize your desktop's color scheme. Change the entire theme's accents and UI with a single command.

## Features

-   **Customizable Accent Colors** - Change primary, bright, and secondary accents using a single script
-   **Easy UI Configuration** - Toggle rounded corners and Waybar floating style with simple flags
-   **Comprehensive Coverage** - Supports Hyprland, Waybar, Mako, SwayOSD, Walker, Neovim, and popular terminals (Alacritty, Ghostty, Kitty)
-   **Consistent Design Language** - Unified color scheme across all applications
-   **Modern Aesthetics** - Light cyan accent (#7dd6f6) with smooth animations and polished UI elements
-   **Floating Waybar** - Modern floating status bar with rounded corners and spacing

## Quick Install

```bash
omarchy-theme-install https://github.com/abhijeet-swami/omarchy-ayaka-theme
```

## Apply and customize the theme

One entry point script powers all changes: accents and UI.

```bash
# Read values from theme.toml and apply everywhere
python3 scripts/apply_theme.py

# Override accents on the fly (hex #RRGGBB)
python3 scripts/apply_theme.py --accent "#70c7f0" \
							   --accent-bright "#b3ecff" \
							   --accent-secondary "#88cc88"

# UI tweaks
python3 scripts/apply_theme.py --rounding 10            # rounded corners
python3 scripts/apply_theme.py --rounding 0             # square corners
python3 scripts/apply_theme.py --waybar-floating true   # floating Waybar
python3 scripts/apply_theme.py --waybar-floating false  # full-width Waybar
```

You can also edit `theme.toml` directly under `[accent]` and `[ui]` and run the script without arguments.

### Accent markers supported

The script scans files and replaces colors on lines containing the following markers:

-   `accent:primary` → `#RRGGBB`
-   `accent:primary-bright` → `#RRGGBB`
-   `accent:primary-rgba` → `rgba(RRGGBBAA)` (auto-appends ff if not provided)
-   `accent:secondary` → `#RRGGBB`
-   `accent:secondary-rgba` → `rgba(RRGGBBAA)`

### Requirements

For Python versions before 3.11:

```bash
pip install -r scripts/requirements.txt
```

### Applying Changes

After applying the theme or updating colors, reload the affected applications:

-   **Hyprland**: `hyprctl reload` or restart Hyprland
-   **Waybar/Mako/Walker**: Restart the respective services
-   **Terminals**: Open new instances or reload configs (if supported)
-   **Neovim**: Restart or `:source` your configuration

## Screenshots

![Ayaka 1](https://github.com/abhijeet-swami/omarchy-ayaka-theme/blob/main/screenshots/1.png)
![Ayaka 2](https://github.com/abhijeet-swami/omarchy-ayaka-theme/blob/main/screenshots/2.png)

## Theme Components

-   **Hyprland** - Window manager configuration with cyan accent borders
-   **Hyprlock** - Lock screen styling
-   **Waybar** - Status bar theme
-   **Mako** - Notification daemon styling
-   **SwayOSD** - On-screen display theme
-   **Walker** - Application launcher theme
-   **Neovim** - Editor color scheme
-   **Terminals** - Alacritty, Ghostty, and Kitty configurations
-   **btop** - System monitor theme

## Credits

-   Original theme inspired by [Ayaka Theme](https://github.com/abhijeet-swami/omarchy-ayaka-theme) by **abhijeet-swami**
-   Animation by **Raze**
-   Cyan accent variant and automation script by **razuer**

## License

See [LICENSE](LICENSE) for details.
