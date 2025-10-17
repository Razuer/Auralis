# Ayaka Theme - Customizable Edition

A personalized variant of the [Ayaka Theme](https://github.com/abhijeet-swami/omarchy-ayaka-theme) for Omarchy Linux, designed for easy customization and accent color personalization.

This theme builds upon the original Ayaka's elegant dark foundation while introducing an automated accent system that makes it effortless to personalize your desktop's primary color scheme to match your preferences. Change the entire theme's accent with a single command.

## Features

- **Customizable Accent Colors** - Easily change the primary accent color using an automated script
- **Comprehensive Coverage** - Supports Hyprland, Waybar, Mako, SwayOSD, Walker, Neovim, and popular terminals (Alacritty, Ghostty, Kitty)
- **Consistent Design Language** - Unified color scheme across all applications
- **Modern Aesthetics** - Light cyan accent (#7dd6f6) with smooth animations and polished UI elements

## Quick Install

```bash
omarchy-theme-install https://github.com/abhijeet-swami/omarchy-ayaka-theme
```

## Changing the Accent Color

This theme includes a Python script that automatically updates the accent color across all configuration files:

```bash
# Change the primary accent color
python3 scripts/update_accent.py --accent "#your-color"

# Change both primary and bright accent colors
python3 scripts/update_accent.py --accent "#primary-color" --accent-bright "#bright-variant"
```

The script reads from `palette.toml` and updates all files with special markers (`# accent:primary`, `# accent:primary-rgba`, etc.) to ensure consistent theming.

### Requirements

For Python versions before 3.11:
```bash
pip install -r scripts/requirements.txt
```

### Applying Changes

After updating colors, reload the affected applications:
- **Hyprland**: `hyprctl reload` or restart Hyprland
- **Waybar/Mako/Walker**: Restart the respective services
- **Terminals**: Open new instances or reload configs (if supported)
- **Neovim**: Restart or `:source` your configuration

## Screenshots

![Ayaka 1](https://github.com/abhijeet-swami/omarchy-ayaka-theme/blob/main/screenshots/1.png)
![Ayaka 2](https://github.com/abhijeet-swami/omarchy-ayaka-theme/blob/main/screenshots/2.png)

## Theme Components

- **Hyprland** - Window manager configuration with cyan accent borders
- **Hyprlock** - Lock screen styling
- **Waybar** - Status bar theme
- **Mako** - Notification daemon styling
- **SwayOSD** - On-screen display theme
- **Walker** - Application launcher theme
- **Neovim** - Editor color scheme
- **Terminals** - Alacritty, Ghostty, and Kitty configurations
- **btop** - System monitor theme

## Credits

- Original theme inspired by [Ayaka Theme](https://github.com/abhijeet-swami/omarchy-ayaka-theme) by **abhijeet-swami**
- Animation by **Raze**  
- Cyan accent variant and automation script by **razuer**

## License

See [LICENSE](LICENSE) for details.
