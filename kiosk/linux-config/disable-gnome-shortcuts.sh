#!/bin/bash
# GNOME Settings Disabler for Ubuntu Kiosk Mode
# Run this script to disable common GNOME shortcuts that could escape the kiosk

echo "🔒 Disabling GNOME shortcuts for kiosk mode..."

# Disable Alt+Tab and Alt+Shift+Tab (window switching)
gsettings set org.gnome.desktop.wm.keybindings switch-applications "[]"
gsettings set org.gnome.desktop.wm.keybindings switch-applications-backward "[]"
gsettings set org.gnome.desktop.wm.keybindings switch-windows "[]"
gsettings set org.gnome.desktop.wm.keybindings switch-windows-backward "[]"

# Disable Activities overview (Super key)
gsettings set org.gnome.mutter overlay-key ""

# Disable showing desktop
gsettings set org.gnome.desktop.wm.keybindings show-desktop "[]"

# Disable workspace switching
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-left "[]"
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-right "[]"
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-up "[]"
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-down "[]"

# Disable close window (Ctrl+Q, Alt+F4 will be handled by Electron)
gsettings set org.gnome.desktop.wm.keybindings close "[]"

# Disable system menu
gsettings set org.gnome.desktop.wm.keybindings panel-main-menu "[]"

# Disable run dialog (Alt+F2)
gsettings set org.gnome.desktop.wm.keybindings panel-run-dialog "[]"

# Disable terminal shortcut (Ctrl+Alt+T)
gsettings set org.gnome.settings-daemon.plugins.media-keys terminal "[]"

echo "✅ GNOME shortcuts disabled"
echo "💡 To re-enable, use: dconf reset -f /org/gnome/desktop/wm/keybindings/"
