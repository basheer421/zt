import { useEffect, useState } from "react";
import { loginAttemptsAPI } from "../utils/api";
import { LoginAttempt } from "../types";
import { format } from "date-fns";

export default function LoginAttempts() {
  const [attempts, setAttempts] = useState<LoginAttempt[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterUsername, setFilterUsername] = useState("");
  const [filterDays, setFilterDays] = useState(7);

  useEffect(() => {
    loadAttempts();
  }, [filterDays]);

  const loadAttempts = async () => {
    try {
      setLoading(true);
      const response = await loginAttemptsAPI.getAll({ days: filterDays });
      setAttempts(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error("Failed to load login attempts:", error);
      setAttempts([]);
    } finally {
      setLoading(false);
    }
  };

  const filteredAttempts = filterUsername
    ? attempts.filter((a) =>
        a.username.toLowerCase().includes(filterUsername.toLowerCase())
      )
    : attempts;

  const getActionColor = (action: string) => {
    const colors: Record<string, string> = {
      allow: "bg-green-100 text-green-800",
      deny: "bg-red-100 text-red-800",
      challenge: "bg-yellow-100 text-yellow-800",
      review: "bg-blue-100 text-blue-800",
    };
    return colors[action] || "bg-gray-100 text-gray-800";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading login attempts...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Login Attempts</h1>
          <p className="text-gray-500 mt-1">View all authentication attempts</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100">
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Filter by username..."
              value={filterUsername}
              onChange={(e) => setFilterUsername(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <select
            value={filterDays}
            onChange={(e) => setFilterDays(Number(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value={1}>Last 24 hours</option>
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Username
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Timestamp
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  IP Address
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Location
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Risk Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Action
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredAttempts.map((attempt) => (
                <tr key={attempt.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {attempt.username}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {format(
                      new Date(attempt.timestamp),
                      "MMM dd, yyyy HH:mm:ss"
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {attempt.ip_address}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {attempt.location || "Unknown"}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {attempt.risk_score !== null ? (
                      <span
                        className={`font-semibold ${
                          attempt.risk_score * 100 >= 70
                            ? "text-red-600"
                            : attempt.risk_score * 100 >= 30
                            ? "text-yellow-600"
                            : "text-green-600"
                        }`}
                      >
                        {(attempt.risk_score * 100).toFixed(0)}
                      </span>
                    ) : (
                      "N/A"
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 text-xs font-semibold rounded-full ${getActionColor(
                        attempt.action
                      )}`}
                    >
                      {attempt.action}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {attempt.success ? (
                      <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                        Success
                      </span>
                    ) : (
                      <span className="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                        Failed
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filteredAttempts.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              No login attempts found
            </div>
          )}
        </div>
      </div>

      <div className="text-sm text-gray-500">
        Showing {filteredAttempts.length} of {attempts.length} attempts
      </div>
    </div>
  );
}
