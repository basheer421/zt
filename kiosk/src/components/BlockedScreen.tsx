const BlockedScreen = () => {
  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-gradient-to-br from-red-600 via-red-700 to-red-800">
      <div className="w-full max-w-md px-8">
        <div className="bg-white rounded-2xl shadow-2xl p-8 text-center">
          {/* Error Icon */}
          <div className="inline-flex items-center justify-center w-20 h-20 bg-red-100 rounded-full mb-6">
            <svg
              className="w-12 h-12 text-red-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>

          {/* Header */}
          <h1 className="text-3xl font-bold text-gray-800 mb-4">
            Access Denied
          </h1>

          {/* Message */}
          <p className="text-gray-600 mb-6">
            Your login attempt has been blocked due to suspicious activity.
          </p>

          {/* Details */}
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-red-800 font-medium">
              This incident has been logged and the security team has been
              notified.
            </p>
          </div>

          {/* Contact Information */}
          <div className="space-y-2 text-sm text-gray-600">
            <p>If you believe this is an error, please contact:</p>
            <p className="font-semibold text-gray-800">IT Support</p>
            <p>support@company.com</p>
            <p>+1 (555) 123-4567</p>
          </div>

          {/* Timestamp */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <p className="text-xs text-gray-500">
              Timestamp: {new Date().toLocaleString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BlockedScreen;
