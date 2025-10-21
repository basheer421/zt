# Kiosk Mode Security

This document describes the security features implemented to prevent users from escaping the kiosk application.

## ⚠️ IMPORTANT LIMITATIONS

**Web browsers CANNOT block OS-level keyboard shortcuts!**

The following shortcuts are handled by the operating system and **CANNOT be blocked by JavaScript**:

- ❌ **Alt+Tab** - OS window switching
- ❌ **Alt+F4** - OS window close
- ❌ **Windows Key** - Start menu (Windows)
- ❌ **Cmd+Tab** - App switching (macOS)
- ❌ **Ctrl+Alt+Delete** - Security screen (Windows)

### True Kiosk Security Requires:

1. **Browser Kiosk Mode** - Launch with `--kiosk` flag
2. **OS-Level Kiosk Configuration**:
   - **Windows**: Group Policy to disable Alt+Tab, Start menu, Task Manager
   - **Linux**: Configure window manager to disable shortcuts
   - **macOS**: Use Guided Access or kiosk mode utilities
3. **Physical Security** - Lock down the hardware

This JavaScript implementation only blocks **browser-level** shortcuts that could expose browser UI or features.

## Overview

The kiosk application implements comprehensive input blocking to prevent users from:

- Opening new windows or tabs **within the browser**
- Accessing browser features (DevTools, history, downloads, etc.)
- Using keyboard shortcuts to access browser UI
- Right-clicking to access context menus
- Dragging and dropping files

## Blocked Keyboard Shortcuts (Browser-Level Only)

### ✅ Successfully Blocked (Browser-Level)

#### Tab Management

#### Tab Management

- **Ctrl+Tab** / **Ctrl+Shift+Tab** - Tab switching ✅
- **Ctrl+N** - New window ✅
- **Ctrl+T** - New tab ✅
- **Ctrl+W** - Close tab ✅
- **Ctrl+Shift+T** - Reopen closed tab ✅
- **Ctrl+Shift+N** - New private/incognito window ✅

#### Browser Navigation

- **Alt+Left/Right** - Browser back/forward ✅
- **Backspace** - Browser back (except in input fields) ✅
- **Ctrl+H** - History ✅
- **Ctrl+L** - Address bar focus ✅
- **Ctrl+K** - Search bar focus ✅

#### Browser Features

- **F11** - Fullscreen toggle ✅
- **F12** - DevTools ✅
- **Ctrl+Shift+I** - DevTools ✅
- **Ctrl+Shift+J** - DevTools console ✅
- **Ctrl+Shift+C** - DevTools inspect ✅
- **Ctrl+U** - View source ✅
- **Ctrl+P** - Print dialog ✅
- **Ctrl+S** - Save page ✅
- **Ctrl+O** - Open file ✅
- **Ctrl+F** - Find in page ✅
- **Ctrl+G** - Find next ✅
- **Ctrl+J** - Downloads ✅
- **Ctrl+Shift+Delete** - Clear browsing data ✅
- **Escape** - Escape key (prevents fullscreen exit) ✅

### ❌ Cannot Be Blocked (OS-Level)

These shortcuts are handled by the operating system and **cannot** be blocked by web applications:

- ❌ **Alt+Tab** - Window switching (OS-level)
- ❌ **Alt+F4** - Close window (OS-level)
- ❌ **Windows Key** - Start menu (OS-level)
- ❌ **Ctrl+Alt+Delete** - Security screen (OS-level)
- ❌ **Cmd+Tab** - App switching on macOS (OS-level)
- ❌ **Cmd+Q** - Quit app on macOS (OS-level)

**Solution**: Configure these at the OS level using Group Policy (Windows), window manager settings (Linux), or Guided Access (macOS).

### Browser Navigation

- **Alt+Left/Right** - Browser back/forward (blocked)
- **Backspace** - Browser back (blocked, except in input fields)
- **Ctrl+H** - History (blocked)
- **Ctrl+L** - Address bar focus (blocked)
- **Ctrl+K** - Search bar focus (blocked)

### Browser Features

- **F11** - Fullscreen toggle (blocked)
- **F12** - DevTools (blocked)
- **Ctrl+Shift+I** - DevTools (blocked)
- **Ctrl+Shift+J** - DevTools console (blocked)
- **Ctrl+Shift+C** - DevTools inspect (blocked)
- **Ctrl+U** - View source (blocked)
- **Ctrl+P** - Print dialog (blocked)
- **Ctrl+S** - Save page (blocked)
- **Ctrl+O** - Open file (blocked)
- **Ctrl+F** - Find in page (blocked)
- **Ctrl+G** - Find next (blocked)
- **Ctrl+J** - Downloads (blocked)
- **Ctrl+Shift+Delete** - Clear browsing data (blocked)

### System Keys

- **Escape** - Escape key (blocked)
- **Windows/Meta key** - Start menu/Spotlight (blocked)

### ✅ Allowed Shortcuts

- **Alt+F4** - Close application (ALLOWED - proper exit mechanism)

## Blocked Mouse/Touch Actions

- **Right-click** - Context menu is completely disabled
- **Drag & Drop** - File dragging is prevented
- **Image Dragging** - Images cannot be dragged
- **Link Dragging** - Links cannot be dragged

## CSS-Based Restrictions

The application applies CSS rules to further restrict user interactions:

```css
/* Prevent text selection outside input fields */
body {
  user-select: none;
}

/* Allow selection in input fields */
input,
textarea,
[contenteditable="true"] {
  user-select: text;
}

/* Prevent dragging images and links */
img {
  -webkit-user-drag: none;
  pointer-events: none;
}

a {
  -webkit-user-drag: none;
}
```

## Implementation Details

### Core Security Functions

The kiosk mode security is implemented in `/src/utils/kioskMode.ts`:

1. **`blockKioskEscapeInputs()`** - Sets up keyboard and mouse event listeners to block escape attempts
2. **`applyKioskStyles()`** - Applies CSS rules to prevent user interactions

### Initialization

The security features are automatically enabled when the application starts in `/src/main.tsx`:

```typescript
import { blockKioskEscapeInputs, applyKioskStyles } from "./utils/kioskMode";

// Enable kiosk mode security on app startup
blockKioskEscapeInputs();
applyKioskStyles();
```

### Event Capture

All event listeners use `{ capture: true }` to ensure they intercept events before they reach any other handlers in the application.

## Browser Kiosk Mode

For maximum security, the application should be launched in the browser's native kiosk mode:

### Firefox Kiosk Mode

```bash
firefox --kiosk https://your-kiosk-url.com --private-window
```

### Chrome Kiosk Mode

```bash
chrome --kiosk https://your-kiosk-url.com --incognito
```

### Windows Batch Script

The included `windows_kiosk.bat` script automatically launches Firefox in kiosk mode.

## Security Considerations

1. **Browser Kiosk Mode**: Always run in browser kiosk mode for proper fullscreen and OS-level restrictions
2. **Network Access**: Restrict network access to only necessary endpoints
3. **Physical Security**: Ensure physical access to the kiosk machine is controlled
4. **Regular Updates**: Keep the browser and operating system updated
5. **Monitoring**: Log blocked attempts for security auditing

## Testing

To test the kiosk security:

1. Try various keyboard shortcuts listed above - they should all be blocked
2. Try right-clicking - context menu should not appear
3. Try dragging elements - should not work
4. Try Alt+F4 - should close the application (normal behavior)
5. Check browser console for "🚫 Blocked:" messages when shortcuts are attempted

## Debugging

When running in development mode, blocked actions are logged to the console with the format:

```
🚫 Blocked: [Action Name]
```

You can see these messages in the browser DevTools (accessible before enabling kiosk mode).

## Disabling Security (Development Only)

If you need to disable kiosk security during development, comment out the security initialization in `/src/main.tsx`:

```typescript
// blockKioskEscapeInputs()
// applyKioskStyles()
```

**⚠️ WARNING**: Never disable security in production!

## Future Enhancements

Potential future security improvements:

- Idle timeout with automatic logout
- Screen recording detection
- USB device monitoring
- Network traffic monitoring
- Biometric authentication
- Hardware token support
