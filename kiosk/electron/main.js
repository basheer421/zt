const { app, BrowserWindow, globalShortcut } = require("electron");
const path = require("path");

// ============================================================================
// CRITICAL ERROR HANDLING - Catch all uncaught exceptions
// ============================================================================
process.on("uncaughtException", function (err) {
  console.error("UNCAUGHT EXCEPTION:", err);
});

process.on("unhandledRejection", (reason, promise) => {
  console.error("UNHANDLED REJECTION:", reason);
});

// Disable GPU acceleration to fix graphics errors on Linux/VM
app.disableHardwareAcceleration();

// Environment detection
const isDev = false;
const PRODUCTION_URL = "https://zt-two.vercel.app";
const VITE_DEV_SERVER_URL = "http://localhost:5173";

let mainWindow = null;

/**
 * Block all escape shortcuts using Electron's globalShortcut API
 * This works at the OS level - unlike browser JavaScript
 */
function registerGlobalShortcuts() {
  // Block Alt+Tab (window switching)
  globalShortcut.register("Alt+Tab", () => false);

  // Block Alt+Shift+Tab (reverse window switching)
  globalShortcut.register("Alt+Shift+Tab", () => false);

  // Block Alt+F4 (close window)
  globalShortcut.register("Alt+F4", () => false);

  // Block Super/Windows key (Linux/Windows)
  try {
    globalShortcut.register("Meta", () => false);
  } catch (e) {
    // Meta key not supported on this platform
  }

  // Block Ctrl+Alt+Delete (security screen)
  globalShortcut.register("Ctrl+Alt+Delete", () => false);

  // Block Ctrl+Shift+Escape (task manager)
  globalShortcut.register("Ctrl+Shift+Escape", () => false);

  // Block F11 (fullscreen toggle)
  globalShortcut.register("F11", () => false);

  // Block Ctrl+Q (quit - common on Linux)
  globalShortcut.register("Ctrl+Q", () => false);

  // Block Ctrl+W (close window)
  globalShortcut.register("Ctrl+W", () => false);

  // Block Alt+F2 (run dialog on Linux)
  globalShortcut.register("Alt+F2", () => false);

  // Block Ctrl+Alt+T (terminal on Ubuntu)
  globalShortcut.register("Ctrl+Alt+T", () => false);
}

/**
 * Unregister all global shortcuts
 */
function unregisterGlobalShortcuts() {
  globalShortcut.unregisterAll();
}

/**
 * Create the main application window
 */
function createWindow() {
  try {
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

      // Show window to prevent white screen
      show: true,
      backgroundColor: "#ffffff",

      // Security settings
      webPreferences: {
        preload: path.join(__dirname, "preload.js"),
        nodeIntegration: false, // Security best practice
        contextIsolation: true, // Security best practice
        devTools: isDev, // Only enable in development
        webSecurity: false, // Disable to allow API calls
        allowRunningInsecureContent: true, // Allow HTTP API calls
        hardwareAcceleration: false, // Disabled for VM compatibility
      },
    });
  } catch (error) {
    console.error("ERROR creating BrowserWindow:", error);
    throw error;
  }

  // Prevent window from being closed
  mainWindow.on("close", (event) => {
    if (!app.isQuitting) {
      event.preventDefault();
    }
  });

  // Load the app
  try {
    if (isDev) {
      // Development: Load from Vite dev server
      mainWindow.loadURL(VITE_DEV_SERVER_URL);
      mainWindow.webContents.openDevTools(); // Open DevTools in dev mode
    } else {
      // Production: Load from deployed Vercel app
      mainWindow.loadURL(PRODUCTION_URL);
      // DevTools disabled in production
    }
  } catch (error) {
    console.error("ERROR loading URL:", error);
  }

  // Log failed loads
  mainWindow.webContents.on(
    "did-fail-load",
    (event, errorCode, errorDescription, validatedURL) => {
      console.error(
        "FAILED TO LOAD:",
        validatedURL,
        errorCode,
        errorDescription
      );
    }
  );

  // Prevent navigation away from the app
  // Allow AAU redirect after successful login
  mainWindow.webContents.on("will-navigate", (event, url) => {
    const allowedOrigins = [
      VITE_DEV_SERVER_URL,
      PRODUCTION_URL,
      "https://aau.ac.ae", // Allow AAU redirect after login
    ];

    let urlOrigin = "(invalid)";
    try {
      urlOrigin = new URL(url).origin;
    } catch (e) {
      // ignore
    }

    const allowed = allowedOrigins.some((origin) => url.startsWith(origin));

    if (!allowed) {
      event.preventDefault();
    }
  });

  // Prevent new windows
  mainWindow.webContents.setWindowOpenHandler(() => {
    return { action: "deny" };
  });

  // CRITICAL: Handle renderer process crashes - relaunch app automatically
  mainWindow.webContents.on("render-process-gone", (event, details) => {
    console.error("RENDERER CRASHED:", details.reason);

    if (details.reason === "crashed" || details.reason === "killed") {
      // Relaunch the app
      app.relaunch({ args: process.argv.slice(1).concat(["--relaunch"]) });
      app.exit(0);
    }
  });
}

/**
 * App lifecycle: Ready
 */
app
  .whenReady()
  .then(() => {
    try {
      createWindow();
      registerGlobalShortcuts();
    } catch (error) {
      console.error("ERROR during app initialization:", error);
    }

    // macOS: Re-create window when dock icon is clicked
    app.on("activate", () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        try {
          createWindow();
        } catch (error) {
          console.error("ERROR recreating window:", error);
        }
      }
    });
  })
  .catch((error) => {
    console.error("FATAL ERROR: App failed to initialize:", error);
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
    let parsedUrl;
    try {
      parsedUrl = new URL(navigationUrl);
    } catch (e) {
      return;
    }

    // Allow dev server, production URL, AAU, and file protocol
    const allowedOrigins = [
      VITE_DEV_SERVER_URL,
      PRODUCTION_URL,
      "https://aau.ac.ae", // Allow AAU redirect after login
    ];

    const isAllowed =
      allowedOrigins.some((origin) => navigationUrl.startsWith(origin)) ||
      parsedUrl.protocol.startsWith("file");

    if (!isAllowed) {
      event.preventDefault();
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
