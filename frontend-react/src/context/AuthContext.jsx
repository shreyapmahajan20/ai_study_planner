/**
 * AuthContext.jsx
 * ---------------
 * Holds the logged-in user's info in React state (mirrored to
 * localStorage so a page refresh doesn't lose it — this is the React
 * equivalent of what we discussed as a limitation in the Streamlit
 * version; here it's solved properly since localStorage persists
 * across reloads).
 */

import { createContext, useContext, useState } from "react";
import { api, setSession, clearSession, getStoredUser } from "../api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(getStoredUser());

  async function login(email, password) {
    const result = await api.post("/auth/login", { email, password });
    setSession(result.token, result.user);
    setUser(result.user);
  }

  async function signup(name, email, password) {
    const result = await api.post("/auth/signup", { name, email, password });
    setSession(result.token, result.user);
    setUser(result.user);
  }

  function logout() {
    clearSession();
    setUser(null);
  }

  function updateStoredUser(updates) {
    const merged = { ...user, ...updates };
    setSession(localStorage.getItem("jwt_token"), merged);
    setUser(merged);
  }

  return (
    <AuthContext.Provider value={{ user, login, signup, logout, updateStoredUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}