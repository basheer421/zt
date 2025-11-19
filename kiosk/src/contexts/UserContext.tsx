import { createContext, useContext, useState, type ReactNode } from "react";

interface UserContextType {
  username: string | null;
  role: "admin" | "manager" | "viewer" | null;
  setUser: (username: string, role: "admin" | "manager" | "viewer") => void;
  clearUser: () => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: ReactNode }) {
  const [username, setUsername] = useState<string | null>(() => {
    return localStorage.getItem("username");
  });
  const [role, setRole] = useState<"admin" | "manager" | "viewer" | null>(
    () => {
      const storedRole = localStorage.getItem("role");
      return storedRole as "admin" | "manager" | "viewer" | null;
    }
  );

  const setUser = (
    newUsername: string,
    newRole: "admin" | "manager" | "viewer"
  ) => {
    setUsername(newUsername);
    setRole(newRole);
    localStorage.setItem("username", newUsername);
    localStorage.setItem("role", newRole);
  };

  const clearUser = () => {
    setUsername(null);
    setRole(null);
    localStorage.removeItem("username");
    localStorage.removeItem("role");
  };

  return (
    <UserContext.Provider value={{ username, role, setUser, clearUser }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error("useUser must be used within a UserProvider");
  }
  return context;
}
