import { Routes, Route } from "react-router-dom";
import { LoginForm } from "./components";
import Inventory from "./pages/Inventory";

/**
 * Main App Component
 *
 * Test credentials: All users have password "Test123!"
 * Usernames: john_doe, jane_smith, bob_jones, alice_admin, test_user
 */
function App() {
  return (
    <Routes>
      <Route path="/" element={<LoginForm />} />
      <Route path="/inventory" element={<Inventory />} />
    </Routes>
  );
}

export default App;
