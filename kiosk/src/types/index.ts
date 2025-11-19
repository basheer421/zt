// Core types for the Kiosk application

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  phoneNumber: string;
}

export interface Transaction {
  id: string;
  userId: string;
  amount: number;
  type: "deposit" | "withdrawal" | "transfer";
  status: "pending" | "completed" | "failed";
  timestamp: string;
}

export interface KioskSession {
  sessionId: string;
  userId?: string;
  startTime: string;
  lastActivity: string;
}
