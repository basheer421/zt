const { app, BrowserWindow, globalShortcut } = require("electron");
const path = require("path");

// ============================================================================
// CRITICAL ERROR HANDLING - Catch all uncaught exceptions
// ============================================================================
process.on("uncaughtException", function (err) {
  console.error("💥 UNCAUGHT EXCEPTION IN MAIN PROCESS:");
  console.error("Error:", err);
  console.error("Stack:", err.stack);
});

process.on("unhandledRejection", (reason, promise) => {
  console.error("💥 UNHANDLED PROMISE REJECTION IN MAIN PROCESS:");
  console.error("Promise:", promise);
  console.error("Reason:", reason);
});

// Disable GPU acceleration to fix graphics errors on Linux/VM
app.disableHardwareAcceleration();

// Additional flags for VM/X11 compatibility
app.commandLine.appendSwitch("disable-software-rasterizer");
app.commandLine.appendSwitch("disable-gpu-compositing");
app.commandLine.appendSwitch("no-sandbox");

// Environment detection
const isDev = false;
const PRODUCTION_URL = "https://zt-two.vercel.app";
const VITE_DEV_SERVER_URL = "http://localhost:5173";

let mainWindow = null;

console.log("🚀 Starting Electron app...");
console.log("📍 Environment:", isDev ? "DEVELOPMENT" : "PRODUCTION");
console.log("🌐 Will load from:", isDev ? VITE_DEV_SERVER_URL : PRODUCTION_URL);

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
  // Note: "Super" doesn't work on all platforms, try "Meta" or skip
  try {
    globalShortcut.register("Meta", () => {
      console.log("🚫 Blocked: Meta/Super key");
      return false;
    });
  } catch (e) {
    console.log("⚠️  Could not register Meta/Super key:", e.message);
  }

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
        devTools: true, // Always enable for debugging (was: isDev)
        webSecurity: false, // Disable to allow API calls (was: true)
        allowRunningInsecureContent: true, // Allow HTTP API calls (was: false)
        hardwareAcceleration: false, // Explicitly disable in webPreferences too
      },
    });
    console.log("✅ BrowserWindow created successfully");
  } catch (error) {
    console.error("💥 ERROR creating BrowserWindow:");
    console.error("Error:", error);
    console.error("Stack:", error.stack);
    throw error; // Re-throw to be caught by caller
  }

  // Prevent window from being closed
  mainWindow.on("close", (event) => {
    if (!app.isQuitting) {
      event.preventDefault();
      console.log("🚫 Window close prevented - use designated exit method");
    }
  });

  // Load the app
  try {
    if (isDev) {
      // Development: Load from Vite dev server
      console.log("📡 Loading development server:", VITE_DEV_SERVER_URL);
      mainWindow.loadURL(VITE_DEV_SERVER_URL);
      mainWindow.webContents.openDevTools(); // Open DevTools in dev mode
    } else {
      // Production: Load from deployed Vercel app
      console.log("📡 Loading production URL:", PRODUCTION_URL);
      mainWindow.loadURL(PRODUCTION_URL);
      mainWindow.webContents.openDevTools(); // Enable DevTools in production for debugging
    }
  } catch (error) {
    console.error("💥 ERROR loading URL:");
    console.error("Error:", error);
    console.error("Stack:", error.stack);
  }

  // Log finished loads (URL) for debugging
  mainWindow.webContents.on("did-finish-load", () => {
    try {
      const loadedUrl = mainWindow.webContents.getURL();
      console.log("✅ Renderer finished loading URL:", loadedUrl);
    } catch (err) {
      console.error("💥 Error getting loaded URL:", err);
    }
  });

  // Log failed loads
  mainWindow.webContents.on(
    "did-fail-load",
    (event, errorCode, errorDescription, validatedURL) => {
      console.error("💥 FAILED TO LOAD URL:", validatedURL);
      console.error("Error code:", errorCode);
      console.error("Error description:", errorDescription);
    }
  );

  // Prevent navigation away from the app (and log details)
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
    console.log("🔍 will-navigate -> url:", url);
    console.log("🔍 will-navigate -> origin:", urlOrigin);
    console.log("🔍 allowedOrigins:", allowedOrigins, "allowed:", allowed);

    if (!allowed) {
      event.preventDefault();
      console.log("🚫 Navigation blocked:", url);
    } else {
      console.log("✅ Navigation allowed:", url);
    }
  });

  // Prevent new windows
  mainWindow.webContents.setWindowOpenHandler(() => {
    console.log("🚫 New window blocked");
    return { action: "deny" };
  });

  // Add error logging for debugging
  mainWindow.webContents.on(
    "did-fail-load",
    (event, errorCode, errorDescription) => {
      console.error("❌ Failed to load:", errorCode, errorDescription);
    }
  );

  mainWindow.webContents.on(
    "console-message",
    (event, level, message, line, sourceId) => {
      console.log("📝 Console:", message);
    }
  );

  // CRITICAL: Handle renderer process crashes - relaunch app automatically
  mainWindow.webContents.on("render-process-gone", (event, details) => {
    console.error("💥 RENDERER PROCESS CRASHED!");
    console.error("Reason:", details.reason);
    console.error("Exit code:", details.exitCode);

    if (details.reason === "crashed") {
      console.error("🔄 Renderer crashed - relaunching app...");
      // Relaunch the app
      app.relaunch({ args: process.argv.slice(1).concat(["--relaunch"]) });
      app.exit(0);
    } else {
      console.error(
        "⚠️  Renderer process gone for unknown reason:",
        details.reason
      );
    }
  });

  console.log("✅ Kiosk window created");
}

/**
 * App lifecycle: Ready
 */
app
  .whenReady()
  .then(() => {
    try {
      console.log("📦 App is ready, creating window...");
      createWindow();
      console.log("🔐 Registering global shortcuts...");
      registerGlobalShortcuts();
    } catch (error) {
      console.error("💥 ERROR during app initialization:");
      console.error("Error:", error);
      console.error("Stack:", error.stack);
      // Don't exit - try to continue
    }

    // macOS: Re-create window when dock icon is clicked
    app.on("activate", () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        try {
          createWindow();
        } catch (error) {
          console.error("💥 ERROR recreating window:", error);
        }
      }
    });
  })
  .catch((error) => {
    console.error("💥 FATAL ERROR: App failed to initialize:");
    console.error("Error:", error);
    console.error("Stack:", error.stack);
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
      console.error("Invalid URL in will-navigate:", navigationUrl);
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

    console.log(
      "🔍 web-contents will-navigate:",
      navigationUrl,
      "allowed:",
      isAllowed
    );

    if (!isAllowed) {
      event.preventDefault();
      console.log("🚫 Remote navigation blocked:", navigationUrl);
    } else {
      console.log("✅ Remote navigation allowed:", navigationUrl);
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
