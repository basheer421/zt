# Zero Trust Kiosk - Linux Setup Guide

This guide covers setting up the Zero Trust Kiosk on Ubuntu/Linux with Openbox for true kiosk mode.

## Quick Start

### 1. Install Dependencies

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y openbox xorg unclutter firefox

# For development
cd kiosk
npm install
npm run electron:install
```

### 2. Run in Development Mode

```bash
# Start Vite dev server + Electron
npm run electron:dev
```

### 3. Build for Production

```bash
# Build Linux packages (.AppImage and .deb)
npm run electron:build
```

## Production Kiosk Setup (Ubuntu)

### Option 1: Openbox (Recommended - Minimal)

**Step 1: Install Openbox**

```bash
sudo apt install openbox xorg xinit
```

**Step 2: Create Kiosk User**

```bash
sudo adduser kiosk
sudo usermod -aG sudo kiosk  # Optional: for maintenance
```

**Step 3: Configure Auto-Login**

Edit `/etc/lightdm/lightdm.conf` (or `/etc/gdm3/custom.conf` for GDM):

```ini
[Seat:*]
autologin-user=kiosk
autologin-user-timeout=0
user-session=openbox
```

**Step 4: Install the Kiosk App**

```bash
# Copy built app
sudo mkdir -p /opt/zero-trust-kiosk
sudo cp release/ZeroTrust-Kiosk.AppImage /opt/zero-trust-kiosk/
sudo chmod +x /opt/zero-trust-kiosk/ZeroTrust-Kiosk.AppImage

# Or install .deb package
sudo dpkg -i release/zero-trust-kiosk_1.0.0_amd64.deb
```

**Step 5: Configure Openbox Autostart**

```bash
# As kiosk user
mkdir -p ~/.config/openbox
cp linux-config/openbox-autostart.sh ~/.config/openbox/autostart
chmod +x ~/.config/openbox/autostart
```

**Step 6: Configure Openbox Settings** (Optional)

```bash
cp linux-config/openbox-rc.xml ~/.config/openbox/rc.xml
```

**Step 7: Reboot**

```bash
sudo reboot
```

### Option 2: GNOME (If using existing Ubuntu Desktop)

**Step 1: Disable GNOME Shortcuts**

```bash
chmod +x linux-config/disable-gnome-shortcuts.sh
./linux-config/disable-gnome-shortcuts.sh
```

**Step 2: Add to Startup Applications**

```bash
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/kiosk.desktop << EOF
[Desktop Entry]
Type=Application
Name=Zero Trust Kiosk
Exec=/opt/zero-trust-kiosk/zero-trust-kiosk
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF
```

### Option 3: Systemd Service (Auto-Recovery)

For maximum reliability with automatic restart on crash:

```bash
# Copy service file
sudo cp linux-config/zero-trust-kiosk.service /etc/systemd/system/

# Enable and start
sudo systemctl enable zero-trust-kiosk
sudo systemctl start zero-trust-kiosk

# Check status
sudo systemctl status zero-trust-kiosk
```

## Security Features

### Electron Global Shortcuts (Blocked)

The Electron app blocks these OS-level shortcuts:

- ✅ Alt+Tab / Alt+Shift+Tab - Window switching
- ✅ Alt+F4 - Close window
- ✅ Super/Windows key - Application launcher
- ✅ Ctrl+Alt+Delete - System menu
- ✅ Ctrl+Shift+Escape - Task manager
- ✅ F11 - Fullscreen toggle
- ✅ Ctrl+Q / Ctrl+W - Quit/Close
- ✅ Alt+F2 - Run dialog
- ✅ Ctrl+Alt+T - Terminal

### Additional OS-Level Hardening

**Disable Virtual Terminals** (Ctrl+Alt+F1-F12):

```bash
sudo systemctl mask getty@tty{2,3,4,5,6}.service
```

**Disable Suspend/Hibernate**:

```bash
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

**Disable Screen Blanking**:

```bash
# In Openbox autostart (already included)
xset s off
xset -dpms
xset s noblank
```

## Troubleshooting

### Kiosk Won't Start

```bash
# Check logs
journalctl -u zero-trust-kiosk -f

# Check if app exists
ls -la /opt/zero-trust-kiosk/
```

### Shortcuts Still Work

```bash
# Verify GNOME settings (if using GNOME)
gsettings get org.gnome.desktop.wm.keybindings switch-applications

# Should return: []
```

### Re-enable Shortcuts (For Maintenance)

```bash
# GNOME
dconf reset -f /org/gnome/desktop/wm/keybindings/

# Openbox - edit ~/.config/openbox/rc.xml
```

### Access Terminal for Maintenance

```bash
# Ctrl+Alt+F3 (if not disabled)
# Or SSH from another machine
ssh kiosk@kiosk-ip-address
```

## Development Tips

### Running Without Kiosk Mode (For Testing)

Modify `electron/main.js`:

```javascript
const mainWindow = new BrowserWindow({
  fullscreen: false, // Change this
  kiosk: false, // And this
  // ...
});
```

### Debugging Electron

```bash
# Electron will open DevTools automatically in dev mode
npm run electron:dev
```

### Building for Different Architectures

```bash
# ARM64 (Raspberry Pi, etc.)
cd electron && electron-builder --linux --arm64

# Both x64 and ARM64
cd electron && electron-builder --linux --x64 --arm64
```

## Deployment Checklist

- [ ] Built production Electron app (`npm run electron:build`)
- [ ] Copied app to `/opt/zero-trust-kiosk/`
- [ ] Created kiosk user account
- [ ] Configured auto-login
- [ ] Set up Openbox autostart or systemd service
- [ ] Disabled GNOME/desktop shortcuts (if applicable)
- [ ] Disabled virtual terminals
- [ ] Tested Alt+Tab blocking
- [ ] Tested auto-recovery on crash
- [ ] Configured backend API endpoint
- [ ] Tested login flow

## File Locations

| File            | Purpose                 | Location                                       |
| --------------- | ----------------------- | ---------------------------------------------- |
| Main app        | Electron executable     | `/opt/zero-trust-kiosk/`                       |
| Autostart       | Launch on login         | `~/.config/openbox/autostart`                  |
| Openbox config  | Window manager settings | `~/.config/openbox/rc.xml`                     |
| Systemd service | Auto-recovery           | `/etc/systemd/system/zero-trust-kiosk.service` |
| Logs            | System logs             | `journalctl -u zero-trust-kiosk`               |

## Performance Optimization

### Reduce Memory Usage

```javascript
// In electron/main.js
webPreferences: {
  backgroundThrottling: true,
}
```

### Faster Startup

```bash
# Use AppImage for faster startup
# Or compile from source with custom flags
```

## Remote Management

### SSH Access

```bash
# Enable SSH
sudo apt install openssh-server
sudo systemctl enable ssh

# Connect remotely
ssh kiosk@192.168.1.100
```

### Remote Restart

```bash
# Via SSH
sudo systemctl restart zero-trust-kiosk
```

## License

MIT
