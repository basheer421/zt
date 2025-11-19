interface BlockedScreenProps {
  riskScore?: number;
  username?: string;
  reason?: string;
}

const BlockedScreen = ({
  riskScore = 87,
  username,
  reason = "Suspicious Activity Detected",
}: BlockedScreenProps) => {
  // Determine risk level
  const getRiskLevel = (score: number) => {
    if (score >= 80)
      return {
        level: "CRITICAL",
        color: "text-red-600",
        bgColor: "bg-red-50",
        borderColor: "border-red-300",
      };
    if (score >= 60)
      return {
        level: "HIGH",
        color: "text-orange-600",
        bgColor: "bg-orange-50",
        borderColor: "border-orange-300",
      };
    if (score >= 40)
      return {
        level: "MEDIUM",
        color: "text-yellow-600",
        bgColor: "bg-yellow-50",
        borderColor: "border-yellow-300",
      };
    return {
      level: "LOW",
      color: "text-blue-600",
      bgColor: "bg-blue-50",
      borderColor: "border-blue-300",
    };
  };

  const riskInfo = getRiskLevel(riskScore);

  return (
    <div className="h-screen w-full flex items-center justify-center bg-gradient-to-br from-red-700 via-red-800 to-red-900 relative overflow-hidden">
      {/* Animated background pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.1)_1px,transparent_1px)] bg-[length:50px_50px]"></div>
      </div>

      <div className="w-full max-w-2xl px-6 relative z-10">
        <div className="bg-white rounded-3xl shadow-2xl overflow-hidden">
          {/* Red Alert Header */}
          <div className="bg-gradient-to-r from-red-600 to-red-700 px-6 py-4">
            <div className="flex items-center justify-center">
              <div className="relative">
                <div className="absolute inset-0 animate-ping opacity-75">
                  <div className="w-16 h-16 bg-white rounded-full"></div>
                </div>
                <div className="relative inline-flex items-center justify-center w-16 h-16 bg-white rounded-full">
                  <svg
                    className="w-10 h-10 text-red-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2.5}
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                    />
                  </svg>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="px-6 py-5">
            {/* Access Denied Title */}
            <div className="text-center mb-4">
              <h1 className="text-2xl font-black text-gray-900 mb-1 tracking-tight">
                🚫 ACCESS DENIED
              </h1>
              <p className="text-sm text-gray-600 font-medium">
                Security Protocol Activated
              </p>
            </div>

            {/* Risk Score Display */}
            <div
              className={`${riskInfo.bgColor} ${riskInfo.borderColor} border-2 rounded-xl p-4 mb-4`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Threat Assessment
                </span>
                <span
                  className={`${riskInfo.color} text-xs font-bold px-2 py-1 bg-white rounded-full`}
                >
                  {riskInfo.level}
                </span>
              </div>

              {/* Risk Score Bar */}
              <div className="mb-2">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-lg font-bold text-gray-900">
                    Risk Score: {riskScore}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                  <div
                    className={`h-3 ${
                      riskScore >= 80
                        ? "bg-red-600"
                        : riskScore >= 60
                        ? "bg-orange-500"
                        : "bg-yellow-500"
                    } transition-all duration-1000 ease-out`}
                    style={{ width: `${riskScore}%` }}
                  ></div>
                </div>
              </div>

              <p className={`text-xs font-medium ${riskInfo.color}`}>
                ⚠️ {reason}
              </p>
            </div>

            {/* User Info (if provided) */}
            {username && (
              <div className="bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 mb-3">
                <p className="text-xs text-gray-600">
                  <span className="font-semibold">Account:</span>{" "}
                  <span className="font-mono">{username}</span>
                </p>
              </div>
            )}

            {/* Main Message */}
            <div className="bg-red-50 border-l-4 border-red-600 rounded-r-lg p-3 mb-3">
              <p className="text-sm text-gray-800 font-medium leading-relaxed">
                Your login attempt has been{" "}
                <span className="font-bold text-red-700">blocked</span>. This
                incident has been logged and security has been notified.
              </p>
            </div>

            {/* IT Contact Information */}
            <div className="border-t-2 border-gray-200 pt-4">
              <h2 className="text-base font-bold text-gray-900 mb-3 text-center">
                📞 Contact IT Support
              </h2>

              <div className="grid grid-cols-2 gap-3 mb-3">
                {/* Email */}
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-3 border border-blue-200">
                  <div className="flex items-center mb-1">
                    <svg
                      className="w-4 h-4 text-blue-600 mr-1"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                      />
                    </svg>
                    <span className="text-xs font-semibold text-blue-700 uppercase">
                      Email
                    </span>
                  </div>
                  <p className="text-xs font-mono font-bold text-blue-900">
                    security@company.com
                  </p>
                </div>

                {/* Phone */}
                <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-3 border border-green-200">
                  <div className="flex items-center mb-1">
                    <svg
                      className="w-4 h-4 text-green-600 mr-1"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
                      />
                    </svg>
                    <span className="text-xs font-semibold text-green-700 uppercase">
                      Phone
                    </span>
                  </div>
                  <p className="text-xs font-mono font-bold text-green-900">
                    +1 (555) 123-4567
                  </p>
                </div>
              </div>
            </div>

            {/* Timestamp */}
            <div className="mt-3 pt-3 border-t border-gray-200">
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>
                  ID: {Math.random().toString(36).substr(2, 6).toUpperCase()}
                </span>
                <span>{new Date().toLocaleTimeString()}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BlockedScreen;
