import axios from "axios";
import {
  User,
  CreateUserResponse,
  LoginAttempt,
  AdminUser,
  DashboardStats,
  RiskyUser,
} from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("admin_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth APIs
export const authAPI = {
  login: (username: string, password: string) =>
    api.post("/admin/login", { username, password }),

  logout: () => {
    localStorage.removeItem("admin_token");
    localStorage.removeItem("admin_username");
  },

  getCurrentUser: () => {
    return localStorage.getItem("admin_username");
  },
};

// Dashboard APIs
export const dashboardAPI = {
  getStats: (days: number = 7) =>
    api.get<DashboardStats>(`/admin/stats?days=${days}`),

  getRecentActivity: (limit: number = 10) =>
    api.get<LoginAttempt[]>(`/admin/recent-activity?limit=${limit}`),
};

// Users APIs
export const usersAPI = {
  getAll: () => api.get<User[]>("/admin/users"),

  getById: (id: number) => api.get<User>(`/admin/users/${id}`),

  create: (data: {
    username: string;
    password: string;
    email: string;
    role?: string;
  }) => api.post<CreateUserResponse>("/admin/users", data),

  update: (id: number, data: Partial<User>) =>
    api.put<User>(`/admin/users/${id}`, data),

  delete: (id: number) => api.delete(`/admin/users/${id}`),

  updateStatus: (id: number, status: string) =>
    api.patch(`/admin/users/${id}/status`, { status }),

  updateRole: (id: number, role: string) =>
    api.patch(`/admin/users/${id}/role`, { role }),
};

// Login Attempts APIs
export const loginAttemptsAPI = {
  getAll: (params?: { username?: string; days?: number; limit?: number }) =>
    api.get<LoginAttempt[]>("/admin/login-attempts", { params }),

  getByUsername: (username: string, days: number = 30) =>
    api.get<LoginAttempt[]>(`/admin/login-attempts/${username}?days=${days}`),
};

// Risk Analytics APIs
export const riskAnalyticsAPI = {
  getTopRiskyUsers: (limit: number = 10) =>
    api.get<RiskyUser[]>(`/admin/risky-users?limit=${limit}`),

  getRiskDistribution: (days: number = 7) =>
    api.get(`/admin/risk-distribution?days=${days}`),
};

// Admin Users APIs
export const adminUsersAPI = {
  getAll: () => api.get<AdminUser[]>("/admin/admin-users"),

  create: (data: { username: string; password: string }) =>
    api.post<AdminUser>("/admin/admin-users", data),

  delete: (username: string) => api.delete(`/admin/admin-users/${username}`),
};

export default api;
