// Type definitions for Electron API exposed via preload script

export interface ElectronAPI {
  isElectron: boolean;
  platform: "darwin" | "linux" | "win32";
  exitKiosk: () => void;
  isDev: boolean;
}

declare global {
  interface Window {
    electronAPI?: ElectronAPI;
  }
}

export {};
