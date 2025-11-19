const { contextBridge, ipcRenderer } = require("electron");

/**
 * Preload script - exposes safe APIs to the renderer process
 * This maintains security while allowing controlled communication
 */

contextBridge.exposeInMainWorld("electronAPI", {
  // Check if running in Electron
  isElectron: true,

  // Platform information
  platform: process.platform,

  // Safe exit function for kiosk
  exitKiosk: () => {
    ipcRenderer.send("exit-kiosk");
  },

  // Environment
  isDev: process.env.NODE_ENV === "development",
});

console.log("✅ Electron preload script loaded");
