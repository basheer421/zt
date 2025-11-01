export interface User {
  id: number;
  username: string;
  email: string;
  status: "active" | "inactive" | "locked" | "suspended";
  created_at: string;
}

export interface CreateUserResponse extends User {
  password: string; // Only returned when creating a new user
  message: string;
}

export interface LoginAttempt {
  id: number;
  username: string;
  timestamp: string;
  ip_address: string;
  device_fingerprint: string;
  location: string | null;
  risk_score: number | null;
  action: "allow" | "deny" | "challenge" | "review";
  success: boolean;
}

export interface AdminUser {
  id: number;
  username: string;
  created_at: string;
}

export interface DashboardStats {
  total_users: number;
  active_users: number;
  total_attempts: number;
  successful_logins: number;
  failed_logins: number;
  unique_users: number;
  avg_risk_score: number;
}

export interface RiskyUser {
  username: string;
  attempt_count: number;
  avg_risk_score: number;
  last_attempt: string;
}
