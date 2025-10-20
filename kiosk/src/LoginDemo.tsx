import { LoginForm } from "./components";

/**
 * LoginDemo - Demonstrates the LoginForm component
 *
 * To use this as your main app, update main.tsx to import this instead of App.tsx
 *
 * Test credentials (from backend seed_data.py):
 * All users have password: Test123!
 *
 * Usernames:
 * - john_doe (Regular 9-5 worker)
 * - jane_smith (Shift worker)
 * - bob_jones (Frequent traveler)
 * - alice_admin (Admin user)
 * - test_user (Test account)
 */
function LoginDemo() {
  return <LoginForm />;
}

export default LoginDemo;
