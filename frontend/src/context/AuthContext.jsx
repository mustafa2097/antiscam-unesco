import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import { apiFetch, parseJsonSafe } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errors, setErrors] = useState({});

  const refreshSession = useCallback(async () => {
    const refreshRes = await apiFetch("/api/auth/refresh", { method: "POST" });
    if (!refreshRes.ok) {
      setUser(null);
      return false;
    }
    const meRes = await apiFetch("/api/auth/me", { method: "GET" });
    if (!meRes.ok) {
      setUser(null);
      return false;
    }
    setUser(await parseJsonSafe(meRes));
    return true;
  }, []);

  const bootstrap = useCallback(async () => {
    setLoading(true);
    setErrors({});
    try {
      const meRes = await apiFetch("/api/auth/me", { method: "GET", timeoutMs: 12000 });
      if (meRes.ok) {
        setUser(await parseJsonSafe(meRes));
        return;
      }
      if (meRes.status === 401) {
        await refreshSession();
        return;
      }
      setUser(null);
    } catch {
      setUser(null);
      setErrors({ session: "session_unavailable" });
    } finally {
      setLoading(false);
    }
  }, [refreshSession]);

  useEffect(() => {
    bootstrap();
  }, [bootstrap]);

  const login = useCallback(async (username, password) => {
    setErrors({});
    const body = new URLSearchParams();
    body.set("username", username);
    body.set("password", password);
    body.set("grant_type", "password");

    const response = await apiFetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });

    if (!response.ok) {
      const payload = await parseJsonSafe(response);
      setErrors({ login: payload?.detail ?? "login_failed" });
      setUser(null);
      return false;
    }

    const meRes = await apiFetch("/api/auth/me", { method: "GET" });
    if (!meRes.ok) {
      setErrors({ login: "session_establish_failed" });
      setUser(null);
      return false;
    }

    setUser(await parseJsonSafe(meRes));
    return true;
  }, []);

  const logout = useCallback(async () => {
    setErrors({});
    try {
      await apiFetch("/api/auth/logout", { method: "POST" });
    } finally {
      setUser(null);
    }
  }, []);

  const value = useMemo(
    () => ({
      user,
      loading,
      errors,
      login,
      logout,
      refreshSession,
      bootstrap,
    }),
    [user, loading, errors, login, logout, refreshSession, bootstrap],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}

export default AuthContext;
