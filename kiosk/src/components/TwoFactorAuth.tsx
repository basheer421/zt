import { useState, useEffect } from "react";
import type { FormEvent } from "react";
import { Button } from "./Button";
import { api } from "../utils/api";

interface TwoFactorAuthProps {
  username: string;
  onBack?: () => void;
  onSuccess?: () => void;
  onBlocked?: (riskScore: number, reason: string) => void;
}

interface OTPRequestResponse {
  success: boolean;
  message: string;
  expires_in_minutes?: number;
  remaining_seconds?: number; // For cooldown when OTP already exists
  error?: string;
}

interface OTPVerifyResponse {
  valid: boolean;
  message: string;
  attempts_remaining?: number;
}

// Placeholder function - implement actual desktop unlock functionality
const unlockDesktop = () => {
  console.log("🔓 Desktop unlocked!");
  alert("Desktop unlocked successfully!");
};

// Helper function to mask email
const maskEmail = (email: string): string => {
  const [localPart, domain] = email.split("@");
  if (!localPart || !domain) return email;

  const visibleChars = Math.min(2, Math.floor(localPart.length / 2));
  const masked = localPart.slice(0, visibleChars) + "***";
  return `${masked}@${domain}`;
};

const TwoFactorAuth = ({
  username,
  onBack,
  onSuccess,
  onBlocked,
}: TwoFactorAuthProps) => {
  const [otpCode, setOtpCode] = useState("");
  const [maskedEmail, setMaskedEmail] = useState<string>("");
  const [status, setStatus] = useState<{
    type: "idle" | "loading" | "success" | "error";
    message: string;
  }>({ type: "idle", message: "" });
  const [attemptsRemaining, setAttemptsRemaining] = useState<number | null>(
    null
  );

  // Request OTP on component mount
  useEffect(() => {
    requestOTP();
  }, []);

  const requestOTP = async () => {
    try {
      setStatus({ type: "loading", message: "Sending verification code..." });

      const response = await api.post<OTPRequestResponse>("/api/otp/request", {
        username,
      });

      if (response.success) {
        // Extract email from message if available (backend sends it)
        // Example: "OTP sent to user@example.com"
        const emailMatch = response.message.match(/[\w.-]+@[\w.-]+\.\w+/);
        if (emailMatch) {
          setMaskedEmail(maskEmail(emailMatch[0]));
        }

        setStatus({
          type: "success",
          message: `Code sent! Expires in ${
            response.expires_in_minutes || 5
          } minutes.`,
        });
        setAttemptsRemaining(3); // Reset attempts
      } else {
        // Check if there's a remaining_seconds field (OTP already exists)
        if (response.remaining_seconds && response.remaining_seconds > 0) {
          // Just show success message, no cooldown
          setStatus({
            type: "success",
            message: "A code was recently sent. Check your email.",
          });
        } else {
          // Show error for other failures
          setStatus({
            type: "error",
            message:
              response.error ||
              response.message ||
              "Failed to send verification code",
          });
        }
      }
    } catch (error) {
      console.error("OTP request error:", error);
      setStatus({
        type: "error",
        message:
          error instanceof Error
            ? error.message
            : "Failed to send verification code",
      });
    }
  };

  const handleResend = async () => {
    setOtpCode(""); // Clear the OTP input
    await requestOTP();
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (otpCode.length !== 6) {
      setStatus({
        type: "error",
        message: "Please enter a 6-digit code",
      });
      return;
    }

    setStatus({ type: "loading", message: "Verifying code..." });

    try {
      const response = await api.post<OTPVerifyResponse>("/api/otp/verify", {
        username,
        otp_code: otpCode,
      });

      if (response.valid) {
        setStatus({
          type: "success",
          message: "Verification successful! Unlocking desktop...",
        });

        // Call unlock after 2 seconds
        setTimeout(() => {
          unlockDesktop();
          if (onSuccess) {
            onSuccess();
          }
        }, 2000);
      } else {
        // Update attempts remaining
        if (response.attempts_remaining !== undefined) {
          setAttemptsRemaining(response.attempts_remaining);

          // Check if user is blocked (0 attempts remaining)
          if (response.attempts_remaining === 0) {
            setStatus({
              type: "error",
              message: "Too many failed attempts. Access blocked.",
            });

            // Trigger blocked state after a short delay
            setTimeout(() => {
              if (onBlocked) {
                onBlocked(85, "Multiple failed OTP verification attempts");
              }
            }, 2000);
            return;
          }
        }

        setStatus({
          type: "error",
          message: response.message || "Invalid verification code",
        });

        // Clear OTP input on error
        setOtpCode("");
      }
    } catch (error) {
      console.error("OTP verification error:", error);
      setStatus({
        type: "error",
        message:
          error instanceof Error
            ? error.message
            : "Failed to verify code. Please try again.",
      });
      setOtpCode("");
    }
  };

  const handleOtpChange = (value: string) => {
    // Only allow numbers
    const numbersOnly = value.replace(/\D/g, "");
    setOtpCode(numbersOnly.slice(0, 6));
  };

  return (
    <div className="h-screen w-full flex items-center justify-center bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 overflow-hidden">
      <div className="w-full max-w-md px-8">
        <div className="bg-white rounded-2xl shadow-2xl p-6">
          {/* Header */}
          <div className="text-center mb-5">
            <div className="inline-flex items-center justify-center w-14 h-14 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full mb-3">
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
              Two-Factor Authentication
            </h1>
            <p className="text-sm text-gray-600 mb-1">
              Enter the verification code sent to your email
            </p>
            {maskedEmail && (
              <p className="text-xs text-indigo-600 font-medium">
                {maskedEmail}
              </p>
            )}
            <p className="text-xs text-gray-500 mt-1">User: {username}</p>
          </div>

          {/* OTP Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="otp"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Verification Code
              </label>
              <input
                type="text"
                id="otp"
                value={otpCode}
                onChange={(e) => handleOtpChange(e.target.value)}
                className="w-full px-3 py-2 text-center text-xl tracking-[0.5em] font-mono border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent transition-all outline-none"
                placeholder="000000"
                maxLength={6}
                inputMode="numeric"
                autoComplete="one-time-code"
                required
                disabled={status.type === "loading"}
                autoFocus
              />
              {attemptsRemaining !== null && attemptsRemaining < 3 && (
                <p className="text-sm text-orange-600 mt-2">
                  {attemptsRemaining} attempt
                  {attemptsRemaining !== 1 ? "s" : ""} remaining
                </p>
              )}
            </div>

            {/* Status Message */}
            {status.message && (
              <div
                className={`p-4 rounded-lg ${
                  status.type === "success"
                    ? "bg-green-50 border border-green-200"
                    : status.type === "error"
                    ? "bg-red-50 border border-red-200"
                    : "bg-blue-50 border border-blue-200"
                }`}
              >
                <div className="flex items-start">
                  {status.type === "loading" && (
                    <svg
                      className="animate-spin h-5 w-5 text-blue-600 mr-3 mt-0.5"
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
                      className="h-5 w-5 text-green-600 mr-3 mt-0.5"
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
                      className="h-5 w-5 text-red-600 mr-3 mt-0.5"
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

            {/* Action Buttons */}
            <div className="space-y-2">
              <Button
                type="submit"
                variant="primary"
                size="md"
                className="w-full bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600"
                disabled={status.type === "loading" || otpCode.length !== 6}
              >
                {status.type === "loading" ? "Verifying..." : "Verify Code"}
              </Button>

              {onBack && (
                <Button
                  type="button"
                  variant="secondary"
                  size="md"
                  className="w-full"
                  onClick={onBack}
                  disabled={status.type === "loading"}
                >
                  Back to Login
                </Button>
              )}
            </div>
          </form>

          {/* Resend Code Section */}
          <div className="mt-4 text-center">
            <p className="text-xs text-gray-600 mb-1">Didn't receive a code?</p>
            <button
              onClick={handleResend}
              disabled={status.type === "loading"}
              className={`text-xs font-medium transition-colors ${
                status.type === "loading"
                  ? "text-gray-400 cursor-not-allowed"
                  : "text-indigo-600 hover:text-indigo-800 cursor-pointer"
              }`}
            >
              Resend Code
            </button>
          </div>

          {/* Footer */}
          <div className="mt-4 pt-4 border-t border-gray-200 text-center">
            <p className="text-xs text-gray-500">Code expires in 5 minutes</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TwoFactorAuth;
