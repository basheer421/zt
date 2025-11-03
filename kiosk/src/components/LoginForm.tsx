import { useState } from "react";
import type { FormEvent } from "react";
import { Button } from "./Button";
import { api } from "../utils/api";
import TwoFactorAuth from "./TwoFactorAuth.js";
import BlockedScreen from "./BlockedScreen.js";

interface AuthResponse {
  status: string;
  message: string;
  username?: string;
  risk_score?: number;
}

// Redirect to AAU website after successful authentication
const unlockDesktop = () => {
  console.log("🔓 Desktop unlocked! Redirecting to AAU website...");
  // Redirect to AAU website
  window.location.href = "https://aau.ac.ae";
};

type AuthState = "login" | "otp" | "blocked" | "success";

const LoginForm = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState<{
    type: "idle" | "loading" | "success" | "error";
    message: string;
  }>({ type: "idle", message: "" });
  const [authState, setAuthState] = useState<AuthState>("login");
  const [riskScore, setRiskScore] = useState<number>(0);
  const [blockReason, setBlockReason] = useState<string>("");

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // Form validation
    if (!username.trim() || !password.trim()) {
      setStatus({
        type: "error",
        message: "Username and password are required",
      });
      return;
    }

    setStatus({ type: "loading", message: "Authenticating..." });

    try {
      // Collect device fingerprint
      const deviceFingerprint = navigator.userAgent;

      // Get current timestamp
      const timestamp = new Date().toISOString();

      // Prepare authentication request
      const authData = {
        username,
        password,
        timestamp,
        device_fingerprint: deviceFingerprint,
        ip_address: "192.168.1.1", // Hardcoded for now
        location: "New York", // Hardcoded for now
      };

      // POST to backend
      const response = await api.post<AuthResponse>(
        "/api/authenticate",
        authData
      );

      // Handle responses based on status
      switch (response.status) {
        case "success":
        case "allow":
          setStatus({
            type: "success",
            message: "Login successful! Redirecting to AAU website...",
          });
          setAuthState("success");

          // Redirect to AAU website after 2 seconds
          setTimeout(() => {
            unlockDesktop();
          }, 2000);
          break;

        case "otp":
          setStatus({
            type: "success",
            message: "Two-factor authentication required",
          });
          setAuthState("otp");
          break;

        case "deny":
          // Store risk score for blocked screen
          if (response.risk_score !== undefined) {
            setRiskScore(Math.round(response.risk_score * 100));
          }
          setBlockReason(response.message || "Suspicious Activity Detected");
          setStatus({
            type: "error",
            message: "Access denied",
          });
          setAuthState("blocked");
          break;

        case "invalid_credentials":
          setStatus({
            type: "error",
            message: response.message || "Invalid username or password",
          });
          break;

        default:
          setStatus({
            type: "error",
            message: "Unexpected response from server",
          });
      }
    } catch (error) {
      console.error("Authentication error:", error);
      setStatus({
        type: "error",
        message:
          error instanceof Error
            ? error.message
            : "Failed to connect to authentication server",
      });
    }
  };

  // Render different screens based on auth state
  if (authState === "otp") {
    return (
      <TwoFactorAuth
        username={username}
        onBack={() => setAuthState("login")}
        onSuccess={() => {
          setAuthState("success");
          unlockDesktop();
        }}
        onBlocked={(score, reason) => {
          setRiskScore(score);
          setBlockReason(reason);
          setAuthState("blocked");
        }}
      />
    );
  }

  if (authState === "blocked") {
    return (
      <BlockedScreen
        riskScore={riskScore}
        username={username}
        reason={blockReason}
      />
    );
  }

  // Main login form
  return (
    <div className="h-screen w-full flex items-center justify-center bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 overflow-hidden">
      <div className="w-full max-w-md px-8">
        <div className="bg-white rounded-2xl shadow-2xl p-6">
          {/* Header */}
          <div className="text-center mb-5">
            <div className="inline-flex items-center justify-center w-14 h-14 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full mb-3">
              <svg
                className="w-7 h-7 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-gray-800 mb-1">
              Welcome Back
            </h1>
            <p className="text-sm text-gray-600">
              Sign in to access your desktop
            </p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Username Input */}
            <div>
              <label
                htmlFor="username"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Username
              </label>
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none"
                placeholder="Enter your username"
                required
                disabled={status.type === "loading"}
              />
            </div>

            {/* Password Input */}
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Password
              </label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none"
                placeholder="Enter your password"
                required
                disabled={status.type === "loading"}
              />
            </div>

            {/* Status Message Area */}
            {status.message && (
              <div
                className={`p-4 rounded-lg ${
                  status.type === "success"
                    ? "bg-green-50 border border-green-200"
                    : status.type === "error"
                    ? "bg-red-50 border border-red-200"
                    : status.type === "loading"
                    ? "bg-blue-50 border border-blue-200"
                    : ""
                }`}
              >
                <div className="flex items-center">
                  {status.type === "loading" && (
                    <svg
                      className="animate-spin h-5 w-5 text-blue-600 mr-3"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                  )}
                  {status.type === "success" && (
                    <svg
                      className="h-5 w-5 text-green-600 mr-3"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  )}
                  {status.type === "error" && (
                    <svg
                      className="h-5 w-5 text-red-600 mr-3"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  )}
                  <p
                    className={`text-sm font-medium ${
                      status.type === "success"
                        ? "text-green-800"
                        : status.type === "error"
                        ? "text-red-800"
                        : "text-blue-800"
                    }`}
                  >
                    {status.message}
                  </p>
                </div>
              </div>
            )}

            {/* Login Button */}
            <Button
              type="submit"
              variant="primary"
              size="md"
              className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700"
              disabled={status.type === "loading"}
            >
              {status.type === "loading" ? "Authenticating..." : "Sign In"}
            </Button>
          </form>

          {/* Footer */}
          <div className="mt-4 text-center">
            <p className="text-xs text-gray-500">
              Secured by Zero-Trust Authentication
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;
