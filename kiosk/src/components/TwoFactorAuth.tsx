import { useState } from "react";
import type { FormEvent } from "react";
import { Button } from "./Button";

interface TwoFactorAuthProps {
  username: string;
}

const TwoFactorAuth = ({ username }: TwoFactorAuthProps) => {
  const [otpCode, setOtpCode] = useState("");
  const [status, setStatus] = useState<{
    type: "idle" | "loading" | "success" | "error";
    message: string;
  }>({ type: "idle", message: "" });

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setStatus({ type: "loading", message: "Verifying OTP..." });

    // TODO: Implement OTP verification
    setTimeout(() => {
      setStatus({
        type: "error",
        message: "OTP verification not yet implemented",
      });
    }, 1000);
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500">
      <div className="w-full max-w-md px-8">
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full mb-4">
              <svg
                className="w-8 h-8 text-white"
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
            <h1 className="text-3xl font-bold text-gray-800 mb-2">
              Two-Factor Authentication
            </h1>
            <p className="text-gray-600">
              Enter the verification code sent to your device
            </p>
            <p className="text-sm text-indigo-600 font-medium mt-2">
              User: {username}
            </p>
          </div>

          {/* OTP Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label
                htmlFor="otp"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Verification Code
              </label>
              <input
                type="text"
                id="otp"
                value={otpCode}
                onChange={(e) => setOtpCode(e.target.value)}
                className="w-full px-4 py-3 text-center text-2xl tracking-widest border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none"
                placeholder="000000"
                maxLength={6}
                pattern="[0-9]{6}"
                required
                disabled={status.type === "loading"}
              />
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
            )}

            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600"
              disabled={status.type === "loading"}
            >
              {status.type === "loading" ? "Verifying..." : "Verify Code"}
            </Button>
          </form>

          {/* Resend Link */}
          <div className="mt-6 text-center">
            <button className="text-sm text-indigo-600 hover:text-indigo-800 font-medium">
              Resend Code
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TwoFactorAuth;
