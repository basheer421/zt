import { useEffect, useState } from "react";
import { riskAnalyticsAPI } from "../utils/api";
import { RiskyUser } from "../types";
import { AlertTriangle, TrendingUp, Shield } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { format } from "date-fns";

export default function RiskAnalytics() {
  const [riskyUsers, setRiskyUsers] = useState<RiskyUser[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const response = await riskAnalyticsAPI.getTopRiskyUsers(20);
      setRiskyUsers(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error("Failed to load risk analytics:", error);
      setRiskyUsers([]);
    } finally {
      setLoading(false);
    }
  };

  const getRiskLevel = (score: number) => {
    if (score >= 70) return { label: "High", color: "bg-red-100 text-red-800" };
    if (score >= 30)
      return { label: "Medium", color: "bg-yellow-100 text-yellow-800" };
    return { label: "Low", color: "bg-green-100 text-green-800" };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading risk analytics...</div>
      </div>
    );
  }

  // Calculate summary stats
  const highRiskCount = riskyUsers.filter((u) => u.avg_risk_score >= 70).length;
  const mediumRiskCount = riskyUsers.filter(
    (u) => u.avg_risk_score >= 30 && u.avg_risk_score < 70
  ).length;
  const lowRiskCount = riskyUsers.filter((u) => u.avg_risk_score < 30).length;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Risk Analytics</h1>
        <p className="text-gray-500 mt-1">
          Analyze risk patterns and high-risk users
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-red-500 rounded-lg flex items-center justify-center">
              <AlertTriangle className="text-white" size={24} />
            </div>
          </div>
          <h3 className="text-gray-500 text-sm font-medium">High Risk Users</h3>
          <p className="text-3xl font-bold text-gray-900 mt-2">
            {highRiskCount}
          </p>
          <p className="text-xs text-gray-500 mt-1">Risk score ≥ 70</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-yellow-500 rounded-lg flex items-center justify-center">
              <TrendingUp className="text-white" size={24} />
            </div>
          </div>
          <h3 className="text-gray-500 text-sm font-medium">
            Medium Risk Users
          </h3>
          <p className="text-3xl font-bold text-gray-900 mt-2">
            {mediumRiskCount}
          </p>
          <p className="text-xs text-gray-500 mt-1">Risk score 30-69</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center">
              <Shield className="text-white" size={24} />
            </div>
          </div>
          <h3 className="text-gray-500 text-sm font-medium">Low Risk Users</h3>
          <p className="text-3xl font-bold text-gray-900 mt-2">
            {lowRiskCount}
          </p>
          <p className="text-xs text-gray-500 mt-1">Risk score &lt; 30</p>
        </div>
      </div>

      {/* Risk Distribution Bar Chart */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Risk Distribution
        </h2>
        <p className="text-sm text-gray-500 mb-6">
          Number of users by risk level
        </p>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={[
              { name: "Low Risk", count: lowRiskCount, color: "#10b981" },
              { name: "Medium Risk", count: mediumRiskCount, color: "#f59e0b" },
              { name: "High Risk", count: highRiskCount, color: "#ef4444" },
            ]}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" radius={[8, 8, 0, 0]}>
              {[
                { color: "#10b981" },
                { color: "#f59e0b" },
                { color: "#ef4444" },
              ].map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Top Risky Users Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="p-6 border-b border-gray-100">
          <h2 className="text-xl font-semibold text-gray-900">
            Top Risky Users
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Users with highest average risk scores
          </p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rank
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Username
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg Risk Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Risk Level
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Login Attempts
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Attempt
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {riskyUsers.map((user, index) => {
                const riskLevel = getRiskLevel(user.avg_risk_score);
                return (
                  <tr key={user.username} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      #{index + 1}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {user.username}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">
                      {(user.avg_risk_score * 100).toFixed(1)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 py-1 text-xs font-semibold rounded-full ${riskLevel.color}`}
                      >
                        {riskLevel.label}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {user.attempt_count}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {format(
                        new Date(user.last_attempt),
                        "MMM dd, yyyy HH:mm"
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {riskyUsers.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              No risk data available
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
