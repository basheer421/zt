// Kiosk Mode Security - Block user inputs that can escape the kiosk

/**
 * Blocks keyboard shortcuts and inputs that could allow users to exit kiosk mode
 * Keeps Alt+F4 functional as it's handled by the OS/browser kiosk mode
 */
export const blockKioskEscapeInputs = () => {
  // Prevent keyboard shortcuts
  const handleKeyDown = (e: KeyboardEvent) => {
    const key = e.key.toLowerCase();
    const ctrl = e.ctrlKey;
    const alt = e.altKey;
    const meta = e.metaKey; // Command key on Mac
    const shift = e.shiftKey;

    // Block Alt+Tab (window switching)
    if (alt && key === "tab") {
      e.preventDefault();
      console.log("🚫 Blocked: Alt+Tab");
      return false;
    }

    // Block Ctrl+N (new window)
    if (ctrl && key === "n") {
      e.preventDefault();
      console.log("🚫 Blocked: Ctrl+N");
      return false;
    }

    // Block Ctrl+T (new tab)
    if (ctrl && key === "t") {
      e.preventDefault();
      console.log("🚫 Blocked: Ctrl+T");
      return false;
    }

    // Block Ctrl+W (close tab)
    if (ctrl && key === "w") {
      e.preventDefault();
      console.log("🚫 Blocked: Ctrl+W");
      return false;
    }

    // Block Ctrl+Shift+T (reopen closed tab)
    if (ctrl && shift && key === "t") {
      e.preventDefault();
      console.log("🚫 Blocked: Ctrl+Shift+T");
      return false;
    }

    // Block Ctrl+Shift+N (new incognito/private window)
    if (ctrl && shift && key === "n") {
      e.preventDefault();
      console.log("🚫 Blocked: Ctrl+Shift+N");
      return false;
    }

    // Block Ctrl+L (focus address bar)
    if (ctrl && key === "l") {
      e.preventDefault();
      console.log("🚫 Blocked: Ctrl+L");
      return false;
    }

    // Block Ctrl+K (focus search bar)
    if (ctrl && key === "k") {
      e.preventDefault();
      console.log("🚫 Blocked: Ctrl+K");
      return false;
    }

    // Block F11 (fullscreen toggle)
    if (key === "f11") {
      e.preventDefault();
      console.log("🚫 Blocked: F11");
      return false;
    }

    // Block Ctrl+Shift+I (DevTools)
    if (ctrl && shift && key === "i") {
      e.preventDefault();
      console.log("🚫 Blocked: Ctrl+Shift+I");
      return false;
    }

    // Block Ctrl+Shift+J (DevTools console)
    if (ctrl && shift && key === "j") {
      e.preventDefault();
      console.log("🚫 Blocked: Ctrl+Shift+J");
      return false;
    }

    // Block Ctrl+Shift+C (DevTools inspect element)
    if (ctrl && shift && key === "c") {
      e.preventDefault();
      console.log("🚫 Blocked: Ctrl+Shift+C");
      return false;
    }

    // Block F12 (DevTools)
    if (key === "f12") {
      e.preventDefault();
      console.log("🚫 Blocked: F12");
      return false;
    }

    // Block Ctrl+U (view source)
    if (ctrl && key === "u") {
      e.preventDefault();
      console.log("🚫 Blocked: Ctrl+U");
      return false;
    }

    // Block Ctrl+H (history)
    if (ctrl && key === "h") {
      e.preventDefault();
      console.log("🚫 Blocked: Ctrl+H");
      return false;
    }

    // Block Ctrl+J (downloads)
    if (ctrl && key === "j") {
      e.preventDefault();
      console.log("🚫 Blocked: Ctrl+J");
      return false;
    }

    // Block Ctrl+Shift+Delete (clear browsing data)
    if (ctrl && shift && key === "delete") {
      e.preventDefault();
      console.log("🚫 Blocked: Ctrl+Shift+Delete");
      return false;
    }

    // Block Ctrl+P (print)
    if (ctrl && key === "p") {
      e.preventDefault();
      console.log("🚫 Blocked: Ctrl+P");
      return false;
    }

    // Block Ctrl+S (save page)
    if (ctrl && key === "s") {
      e.preventDefault();
      console.log("🚫 Blocked: Ctrl+S");
      return false;
    }

    // Block Ctrl+O (open file)
    if (ctrl && key === "o") {
      e.preventDefault();
      console.log("🚫 Blocked: Ctrl+O");
      return false;
    }

    // Block Ctrl+F (find in page) - optional, comment out if users need to search
    if (ctrl && key === "f") {
      e.preventDefault();
      console.log("🚫 Blocked: Ctrl+F");
      return false;
    }

    // Block Ctrl+G (find next) - optional
    if (ctrl && key === "g") {
      e.preventDefault();
      console.log("🚫 Blocked: Ctrl+G");
      return false;
    }

    // Block Escape key (might exit fullscreen in some browsers)
    if (key === "escape") {
      e.preventDefault();
      console.log("🚫 Blocked: Escape");
      return false;
    }

    // Block Meta/Windows key combinations (Mac Command / Windows key)
    if (meta && key === "tab") {
      e.preventDefault();
      console.log("🚫 Blocked: Meta+Tab");
      return false;
    }

    // Block Windows key alone (prevents start menu on Windows)
    if (key === "meta" || key === "os") {
      e.preventDefault();
      console.log("🚫 Blocked: Windows/Meta key");
      return false;
    }

    // Block Ctrl+Tab (switch tabs)
    if (ctrl && key === "tab") {
      e.preventDefault();
      console.log("🚫 Blocked: Ctrl+Tab");
      return false;
    }

    // Block Ctrl+Shift+Tab (switch tabs backwards)
    if (ctrl && shift && key === "tab") {
      e.preventDefault();
      console.log("🚫 Blocked: Ctrl+Shift+Tab");
      return false;
    }

    // Block Alt+Left/Right (browser back/forward)
    if (alt && (key === "arrowleft" || key === "arrowright")) {
      e.preventDefault();
      console.log("🚫 Blocked: Alt+Arrow (browser navigation)");
      return false;
    }

    // Block Backspace (browser back)
    const target = e.target as HTMLElement;
    const isInput =
      target.tagName === "INPUT" ||
      target.tagName === "TEXTAREA" ||
      target.isContentEditable;

    if (key === "backspace" && !isInput) {
      e.preventDefault();
      console.log("🚫 Blocked: Backspace (browser back)");
      return false;
    }

    // NOTE: Alt+F4 is NOT blocked - it's handled by OS/browser kiosk mode
    // This allows proper exit mechanism

    return true;
  };

  // Prevent context menu (right-click)
  const handleContextMenu = (e: MouseEvent) => {
    e.preventDefault();
    console.log("🚫 Blocked: Context menu (right-click)");
    return false;
  };

  // Prevent drag and drop (could be used to open files)
  const handleDragOver = (e: DragEvent) => {
    e.preventDefault();
    console.log("🚫 Blocked: Drag over");
    return false;
  };

  const handleDrop = (e: DragEvent) => {
    e.preventDefault();
    console.log("🚫 Blocked: Drop");
    return false;
  };

  // Prevent selection (optional - might interfere with input fields)
  // Uncomment if you want to prevent text selection entirely
  /*
  const handleSelectStart = (e: Event) => {
    const target = e.target as HTMLElement;
    const isInput =
      target.tagName === "INPUT" ||
      target.tagName === "TEXTAREA" ||
      target.isContentEditable;
    
    if (!isInput) {
      e.preventDefault();
      return false;
    }
    return true;
  };
  */

  // Add event listeners
  document.addEventListener("keydown", handleKeyDown, { capture: true });
  document.addEventListener("contextmenu", handleContextMenu, {
    capture: true,
  });
  document.addEventListener("dragover", handleDragOver, { capture: true });
  document.addEventListener("drop", handleDrop, { capture: true });
  // document.addEventListener("selectstart", handleSelectStart, { capture: true });

  console.log("🔒 Kiosk mode security enabled");
  console.log("✅ Alt+F4 remains functional for exit");

  // Return cleanup function to remove event listeners
  return () => {
    document.removeEventListener("keydown", handleKeyDown, { capture: true });
    document.removeEventListener("contextmenu", handleContextMenu, {
      capture: true,
    });
    document.removeEventListener("dragover", handleDragOver, { capture: true });
    document.removeEventListener("drop", handleDrop, { capture: true });
    // document.removeEventListener("selectstart", handleSelectStart, { capture: true });
    console.log("🔓 Kiosk mode security disabled");
  };
};

/**
 * Additional function to disable browser features via CSS
 * Call this to add CSS rules that prevent user selection and other UI interactions
 */
export const applyKioskStyles = () => {
  const style = document.createElement("style");
  style.id = "kiosk-mode-styles";
  style.textContent = `
    /* Prevent text selection outside of input fields */
    body {
      user-select: none;
      -webkit-user-select: none;
      -moz-user-select: none;
      -ms-user-select: none;
    }
    
    /* Allow selection in input fields */
    input, textarea, [contenteditable="true"] {
      user-select: text;
      -webkit-user-select: text;
      -moz-user-select: text;
      -ms-user-select: text;
    }
    
    /* Prevent dragging images */
    img {
      -webkit-user-drag: none;
      user-drag: none;
      pointer-events: none;
    }
    
    /* Prevent dragging links */
    a {
      -webkit-user-drag: none;
      user-drag: none;
    }
  `;
  document.head.appendChild(style);

  return () => {
    const styleElement = document.getElementById("kiosk-mode-styles");
    if (styleElement) {
      styleElement.remove();
    }
  };
};
