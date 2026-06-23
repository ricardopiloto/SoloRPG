"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useRouter } from "next/navigation";
import { api, AuthUser } from "@/lib/api";
import { clearAuth, getStoredToken, getStoredUser, storeAuth } from "@/lib/auth-storage";

type AuthContextValue = {
  user: AuthUser | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, passwordConfirm: string) => Promise<void>;
  verifyEmail: (email: string, code: string) => Promise<void>;
  resendVerification: (email: string) => Promise<void>;
  logout: () => void;
  setSession: (token: string, user: AuthUser) => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const t = getStoredToken();
    const u = getStoredUser();
    if (t && u) {
      setToken(t);
      setUser(u);
      api.me().catch(() => {
        clearAuth();
        setToken(null);
        setUser(null);
      });
    }
    setLoading(false);
  }, []);

  const setSession = useCallback((accessToken: string, authUser: AuthUser) => {
    storeAuth(accessToken, authUser);
    setToken(accessToken);
    setUser(authUser);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const data = await api.login(email, password);
    setSession(data.access_token, data.user);
  }, [setSession]);

  const register = useCallback(async (email: string, password: string, passwordConfirm: string) => {
    await api.register(email, password, passwordConfirm);
  }, []);

  const verifyEmail = useCallback(async (email: string, code: string) => {
    const data = await api.verifyEmail(email, code);
    setSession(data.access_token, data.user);
  }, [setSession]);

  const resendVerification = useCallback(async (email: string) => {
    await api.resendVerification(email);
  }, []);

  const logout = useCallback(() => {
    clearAuth();
    setToken(null);
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({
      user,
      token,
      loading,
      login,
      register,
      verifyEmail,
      resendVerification,
      logout,
      setSession,
    }),
    [user, token, loading, login, register, verifyEmail, resendVerification, logout, setSession]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

export function RequireAuth({ children }: { children: ReactNode }) {
  const { user, token, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && (!token || !user)) {
      router.replace("/login");
    }
  }, [loading, token, user, router]);

  if (loading || !token || !user) {
    return (
      <div className="container-wfrp py-16 text-center text-wfrp-muted">
        Carregando…
      </div>
    );
  }

  return <>{children}</>;
}
