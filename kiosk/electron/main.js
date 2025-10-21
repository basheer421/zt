const { app, BrowserWindow, globalShortcut } = require("electron");
const path = require("path");

// Environment detection
const isDev = process.env.NODE_ENV === "development";
const PRODUCTION_URL = "https://zt-two.vercel.app";
const VITE_DEV_SERVER_URL = PRODUCTION_URL; //'http://localhost:5173';

let mainWindow = null;

/**
 * Block all escape shortcuts using Electron's globalShortcut API
 * This works at the OS level - unlike browser JavaScript
 */
function registerGlobalShortcuts() {
  // Block Alt+Tab (window switching)
  globalShortcut.register("Alt+Tab", () => {
    console.log("🚫 Blocked: Alt+Tab");
    return false;
  });

  // Block Alt+Shift+Tab (reverse window switching)
  globalShortcut.register("Alt+Shift+Tab", () => {
    console.log("🚫 Blocked: Alt+Shift+Tab");
    return false;
  });

  // Block Alt+F4 (close window)
  globalShortcut.register("Alt+F4", () => {
    console.log("🚫 Blocked: Alt+F4");
    return false;
  });

  // Block Super/Windows key (Linux/Windows)
  globalShortcut.register("Super", () => {
    console.log("🚫 Blocked: Super/Windows key");
    return false;
  });

  // Block Ctrl+Alt+Delete (security screen)
  globalShortcut.register("Ctrl+Alt+Delete", () => {
    console.log("🚫 Blocked: Ctrl+Alt+Delete");
    return false;
  });

  // Block Ctrl+Shift+Escape (task manager)
  globalShortcut.register("Ctrl+Shift+Escape", () => {
    console.log("🚫 Blocked: Ctrl+Shift+Escape");
    return false;
  });

  // Block F11 (fullscreen toggle)
  globalShortcut.register("F11", () => {
    console.log("🚫 Blocked: F11");
    return false;
  });

  // Block Ctrl+Q (quit - common on Linux)
  globalShortcut.register("Ctrl+Q", () => {
    console.log("🚫 Blocked: Ctrl+Q");
    return false;
  });

  // Block Ctrl+W (close window)
  globalShortcut.register("Ctrl+W", () => {
    console.log("🚫 Blocked: Ctrl+W");
    return false;
  });

  // Block Alt+F2 (run dialog on Linux)
  globalShortcut.register("Alt+F2", () => {
    console.log("🚫 Blocked: Alt+F2");
    return false;
  });

  // Block Ctrl+Alt+T (terminal on Ubuntu)
  globalShortcut.register("Ctrl+Alt+T", () => {
    console.log("🚫 Blocked: Ctrl+Alt+T");
    return false;
  });

  console.log("🔒 Global shortcuts registered - kiosk mode active");
}

/**
 * Unregister all global shortcuts
 */
function unregisterGlobalShortcuts() {
  globalShortcut.unregisterAll();
  console.log("🔓 Global shortcuts unregistered");
}

/**
 * Create the main application window
 */
function createWindow() {
  mainWindow = new BrowserWindow({
    // Kiosk mode configuration
    fullscreen: true,
    kiosk: true, // True kiosk mode
    alwaysOnTop: true,
    frame: false, // No window frame

    // Window properties
    width: 1920,
    height: 1080,

    // Hide menu bar
    autoHideMenuBar: true,

    // Security settings
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      nodeIntegration: false, // Security best practice
      contextIsolation: true, // Security best practice
      devTools: isDev, // Only allow DevTools in development
    },
  });

  // Prevent window from being closed
  mainWindow.on("close", (event) => {
    if (!app.isQuitting) {
      event.preventDefault();
      console.log("🚫 Window close prevented - use designated exit method");
    }
  });

  // Load the app
  if (isDev) {
    // Development: Load from Vite dev server
    mainWindow.loadURL(VITE_DEV_SERVER_URL);
    mainWindow.webContents.openDevTools(); // Open DevTools in dev mode
  } else {
    // Production: Load from deployed Vercel app
    mainWindow.loadURL(PRODUCTION_URL);
  }

  // Prevent navigation away from the app
  mainWindow.webContents.on("will-navigate", (event, url) => {
    const allowedOrigins = isDev
      ? [VITE_DEV_SERVER_URL, PRODUCTION_URL]
      : [PRODUCTION_URL];

    const urlOrigin = new URL(url).origin;
    if (!allowedOrigins.some((origin) => url.startsWith(origin))) {
      event.preventDefault();
      console.log("🚫 Navigation blocked:", url);
    }
  });

  // Prevent new windows
  mainWindow.webContents.setWindowOpenHandler(() => {
    console.log("🚫 New window blocked");
    return { action: "deny" };
  });

  console.log("✅ Kiosk window created");
}

/**
 * App lifecycle: Ready
 */
app.whenReady().then(() => {
  createWindow();
  registerGlobalShortcuts();

  // macOS: Re-create window when dock icon is clicked
  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

/**
 * App lifecycle: All windows closed
 */
app.on("window-all-closed", () => {
  // On macOS, apps typically stay active until Cmd+Q
  // But for kiosk, we want to quit
  unregisterGlobalShortcuts();
  app.quit();
});

/**
 * App lifecycle: Before quit
 */
app.on("will-quit", () => {
  unregisterGlobalShortcuts();
});

/**
 * Security: Prevent unauthorized remote content
 */
app.on("web-contents-created", (event, contents) => {
  contents.on("will-navigate", (event, navigationUrl) => {
    const parsedUrl = new URL(navigationUrl);

    // Allow dev server, production URL, and file protocol
    const allowedOrigins = isDev
      ? [VITE_DEV_SERVER_URL, PRODUCTION_URL]
      : [PRODUCTION_URL];

    const isAllowed =
      allowedOrigins.some((origin) => navigationUrl.startsWith(origin)) ||
      parsedUrl.protocol.startsWith("file");

    if (!isAllowed) {
      event.preventDefault();
      console.log("🚫 Remote navigation blocked:", navigationUrl);
    }
  });
});

/**
 * Designated exit function (can be called from renderer via IPC)
 * This is the ONLY way to properly exit the kiosk
 */
const { ipcMain } = require("electron");
ipcMain.on("exit-kiosk", () => {
  console.log("✅ Authorized exit requested");
  app.isQuitting = true;
  unregisterGlobalShortcuts();
  app.quit();
});
