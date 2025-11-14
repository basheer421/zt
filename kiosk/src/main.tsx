import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { HashRouter } from "react-router-dom";
import "./index.css";
import App from "./App.tsx";
import { UserProvider } from "./contexts/UserContext";
import { blockKioskEscapeInputs, applyKioskStyles } from "./utils/kioskMode";

// Enable kiosk mode security on app startup
blockKioskEscapeInputs();
applyKioskStyles();

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <HashRouter>
      <UserProvider>
        <App />
      </UserProvider>
    </HashRouter>
  </StrictMode>
);
