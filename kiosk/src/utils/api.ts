// API utility functions for backend communication

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const api = {
  async get<T>(endpoint: string): Promise<T> {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
      }

      return response.json();
    } catch (error) {
      console.error(`GET ${endpoint} failed:`, error);
      console.error(`API Base URL: ${API_BASE_URL}`);
      throw new Error(
        `Failed to connect to backend at ${API_BASE_URL}. Please ensure the backend server is running.`
      );
    }
  },

  async post<T>(endpoint: string, data: unknown): Promise<T> {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
      }

      return response.json();
    } catch (error) {
      console.error(`POST ${endpoint} failed:`, error);
      console.error(`API Base URL: ${API_BASE_URL}`);
      console.error(`Request data:`, data);
      throw new Error(
        `Failed to connect to backend at ${API_BASE_URL}. Please ensure the backend server is running.`
      );
    }
  },

  async put<T>(endpoint: string, data: unknown): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  },

  async delete<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  },
};
