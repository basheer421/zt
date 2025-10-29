import { useEffect, useState } from "react";
import { dashboardAPI } from "../utils/api";
import { DashboardStats, LoginAttempt } from "../types";
import { Users, CheckCircle, Activity, TrendingUp } from "lucide-react";
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  Tooltip,
} from "recharts";
import { format } from "date-fns";

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentActivity, setRecentActivity] = useState<LoginAttempt[]>([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(7);

  useEffect(() => {
    loadData();
  }, [days]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [statsRes, activityRes] = await Promise.all([
        dashboardAPI.getStats(days),
        dashboardAPI.getRecentActivity(10),
      ]);
      setStats(statsRes.data);
      setRecentActivity(activityRes.data);
    } catch (error) {
      console.error("Failed to load dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading dashboard...</div>
      </div>
    );
  }

  const statCards = [
    {
      title: "Total Users",
      value: stats?.total_users || 0,
      icon: Users,
      color: "bg-blue-500",
      change: null,
    },
    {
      title: "Active Users",
      value: stats?.active_users || 0,
      icon: CheckCircle,
      color: "bg-green-500",
      change: null,
    },
    {
      title: "Login Attempts",
      value: stats?.total_attempts || 0,
      icon: Activity,
      color: "bg-purple-500",
      change: null,
    },
    {
      title: "Success Rate",
      value: stats?.total_attempts
        ? `${Math.round(
            ((stats?.successful_logins || 0) / stats.total_attempts) * 100
          )}%`
        : "0%",
      icon: TrendingUp,
      color: "bg-orange-500",
      change: null,
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 mt-1">
            Overview of your ZT-Verify system
          </p>
        </div>
        <div>
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value={1}>Last 24 hours</option>
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, index) => {
          const Icon = card.icon;
          return (
            <div
              key={index}
              className="bg-white rounded-xl shadow-sm p-6 border border-gray-100"
            >
              <div className="flex items-center justify-between mb-4">
                <div
                  className={`${card.color} w-12 h-12 rounded-lg flex items-center justify-center`}
                >
                  <Icon className="text-white" size={24} />
                </div>
              </div>
              <h3 className="text-gray-500 text-sm font-medium">
                {card.title}
              </h3>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {card.value}
              </p>
            </div>
          );
        })}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Success vs Failure Pie Chart */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Login Success Rate
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={[
                  {
                    name: "Success",
                    value: stats?.successful_logins || 0,
                    color: "#10b981",
                  },
                  {
                    name: "Failed",
                    value: stats?.failed_logins || 0,
                    color: "#ef4444",
                  },
                ]}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) =>
                  `${name}: ${(percent * 100).toFixed(0)}%`
                }
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {[{ color: "#10b981" }, { color: "#ef4444" }].map(
                  (entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  )
                )}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Average Risk Score Gauge */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Average Risk Score
          </h2>
          <div className="flex items-center justify-center h-[300px]">
            <div className="text-center">
              <div className="relative inline-flex items-center justify-center">
                <svg className="transform -rotate-90 w-48 h-48">
                  <circle
                    cx="96"
                    cy="96"
                    r="80"
                    stroke="#e5e7eb"
                    strokeWidth="16"
                    fill="none"
                  />
                  <circle
                    cx="96"
                    cy="96"
                    r="80"
                    stroke={
                      (stats?.avg_risk_score || 0) * 100 >= 70
                        ? "#ef4444"
                        : (stats?.avg_risk_score || 0) * 100 >= 30
                        ? "#f59e0b"
                        : "#10b981"
                    }
                    strokeWidth="16"
                    fill="none"
                    strokeDasharray={`${
                      ((stats?.avg_risk_score || 0) * 100 * 502.4) / 100
                    } 502.4`}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute">
                  <div className="text-5xl font-bold text-gray-900">
                    {stats?.avg_risk_score
                      ? (stats.avg_risk_score * 100).toFixed(1)
                      : "0.0"}
                  </div>
                  <p className="text-sm text-gray-500 mt-1">Risk Score</p>
                </div>
              </div>
              <div className="mt-4 flex items-center justify-center space-x-4 text-sm">
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                  <span>Low (&lt;30)</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-yellow-500 rounded-full mr-2"></div>
                  <span>Med (30-70)</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
                  <span>High (&gt;70)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="p-6 border-b border-gray-100">
          <h2 className="text-xl font-semibold text-gray-900">
            Recent Login Attempts
          </h2>
        </div>
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
                  Risk Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {recentActivity.map((attempt) => (
                <tr key={attempt.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {attempt.username}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {format(new Date(attempt.timestamp), "MMM dd, yyyy HH:mm")}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {attempt.ip_address}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {attempt.risk_score
                      ? (attempt.risk_score * 100).toFixed(0)
                      : "N/A"}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {attempt.success ? (
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                        Success
                      </span>
                    ) : (
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                        Failed
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {recentActivity.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              No recent activity
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
