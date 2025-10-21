#!/bin/bash
# Openbox autostart script for Zero Trust Kiosk
# Copy this to: ~/.config/openbox/autostart

# Disable screen saver and power management
xset s off
xset -dpms
xset s noblank

# Hide mouse cursor after 5 seconds of inactivity (optional)
# unclutter -idle 5 &

# Start the kiosk application
# Replace with the actual path to your built Electron app
KIOSK_APP="/opt/zero-trust-kiosk/zero-trust-kiosk"

# Check if app exists
if [ -f "$KIOSK_APP" ]; then
    $KIOSK_APP &
else
    echo "Error: Kiosk app not found at $KIOSK_APP"
    # Fallback: try to run from AppImage
    if [ -f "/opt/zero-trust-kiosk/ZeroTrust-Kiosk.AppImage" ]; then
        /opt/zero-trust-kiosk/ZeroTrust-Kiosk.AppImage &
    fi
fi
