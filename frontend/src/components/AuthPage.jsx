import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";

import { apiFetch, parseJsonSafe } from "../services/api";
import { useAuth } from "../context/AuthContext";
import LanguageToggle from "./LanguageToggle";

function formatError(detail) {
  if (!detail) return null;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || String(item)).join(" · ");
  }
  return String(detail);
}

export default function AuthPage({ onBack, onSuccess, initialMode = "login" }) {
  const { t, i18n } = useTranslation();
  const dir = i18n.language?.startsWith("ar") ? "rtl" : "ltr";
  const { login } = useAuth();
  const [mode, setMode] = useState(initialMode);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [busy, setBusy] = useState(false);
  const [localError, setLocalError] = useState(null);

  const isRegister = mode === "register";
  const title = isRegister ? t("auth.registerTitle") : t("auth.title");

  const canSubmit = useMemo(() => {
    if (busy) return false;
    if (!email.trim() || password.length < 10) return false;
    if (isRegister) {
      if (fullName.trim().length < 2) return false;
      if (password !== confirm) return false;
    }
    return true;
  }, [busy, email, password, confirm, fullName, isRegister]);

  const switchMode = (next) => {
    setMode(next);
    setLocalError(null);
    setConfirm("");
  };

  const onSubmit = async (event) => {
    event.preventDefault();
    if (!canSubmit) return;

    setBusy(true);
    setLocalError(null);

    try {
      if (isRegister) {
        if (password !== confirm) {
          setLocalError(t("auth.passwordMismatch"));
          return;
        }
        const response = await apiFetch("/api/auth/register", {
          method: "POST",
          body: JSON.stringify({
            email: email.trim(),
            full_name: fullName.trim(),
            password,
            locale: i18n.language?.startsWith("ar") ? "ar" : "en",
          }),
        });
        const payload = await parseJsonSafe(response);
        if (!response.ok) {
          setLocalError(formatError(payload?.detail) || t("auth.registerFailed"));
          return;
        }
      }

      const ok = await login(email.trim(), password);
      if (ok) {
        onSuccess();
        return;
      }
      setLocalError(t("auth.loginFailed"));
    } catch {
      setLocalError(t("auth.requestFailed"));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div dir={dir} className="relative flex min-h-screen flex-col">
      <header className="nav-glass sticky top-0 z-10">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-3.5 sm:px-6">
          <button
            type="button"
            onClick={onBack}
            className="flex items-baseline gap-3 text-ink"
          >
            <span className="font-display text-lg font-semibold tracking-tight">
              {t("nav.brand")}
            </span>
          </button>
          <div className="flex items-center gap-2 sm:gap-3">
            <LanguageToggle />
            <button
              type="button"
              onClick={onBack}
              className="border border-ink/25 px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-ink transition hover:border-ink hover:bg-ink hover:text-paper-raised"
            >
              ← {t("auth.back")}
            </button>
          </div>
        </div>
      </header>

      <main className="flex flex-1 items-center justify-center px-4 py-14 sm:px-6">
        <div className="w-full max-w-md">
          <div className="mb-6 flex items-center justify-between border-b border-ink/15 pb-3">
            <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-ink-muted">
              § 00 · {isRegister ? t("auth.register") : t("auth.submit")}
            </p>
            <span className="text-[10px] uppercase tracking-[0.2em] text-ink-muted">
              Anti Scam
            </span>
          </div>

          <h1 className="font-display text-[2.5rem] font-semibold leading-[1.05] tracking-[-0.02em] text-ink sm:text-[3rem]">
            {title}
          </h1>

          <div className="panel mt-8">
            <div
              role="tablist"
              aria-label={t("auth.tabsLabel")}
              className="flex justify-center gap-3 border-b rule-strong px-4 py-3 sm:px-5"
            >
              <button
                type="button"
                role="tab"
                aria-selected={!isRegister}
                onClick={() => switchMode("login")}
                className={`px-5 py-2 text-[11px] font-semibold uppercase tracking-[0.2em] transition duration-200 ${
                  !isRegister
                    ? "border border-ink/28 text-ink"
                    : "border border-transparent text-ink-muted hover:text-ink"
                }`}
              >
                {t("auth.submit")}
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={isRegister}
                onClick={() => switchMode("register")}
                className={`px-5 py-2 text-[11px] font-semibold uppercase tracking-[0.2em] transition duration-200 ${
                  isRegister
                    ? "border border-ink/28 text-ink"
                    : "border border-transparent text-ink-muted hover:text-ink"
                }`}
              >
                {t("auth.register")}
              </button>
            </div>

            <form onSubmit={onSubmit} className="space-y-4 p-5 sm:p-6" autoComplete="on">
              {!isRegister ? (
                <button
                  type="button"
                  onClick={() => {
                    setEmail("mustafa@antiscam.local");
                    setPassword("Mustafa#M2026");
                    setLocalError(null);
                  }}
                  className="w-full border border-ink/15 bg-paper px-3 py-2 text-start text-xs text-ink-muted transition hover:border-ink hover:text-ink"
                >
                  <span className="font-semibold text-ink">{t("auth.demoFill")}</span>
                  <span className="mt-1 block font-mono text-[11px]">
                    mustafa@antiscam.local · Mustafa#M2026
                  </span>
                </button>
              ) : null}
              {isRegister && (
                <label className="block space-y-1.5">
                  <span className="text-[11px] font-semibold uppercase tracking-[0.16em] text-ink-muted">
                    {t("auth.fullName")}
                  </span>
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    required
                    maxLength={120}
                    autoComplete="name"
                    className="w-full border border-ink/22 bg-paper-raised px-3.5 py-2.5 text-sm text-ink outline-none focus:border-ink"
                  />
                </label>
              )}

              <label className="block space-y-1.5">
                <span className="text-[11px] font-semibold uppercase tracking-[0.16em] text-ink-muted">
                  {t("auth.email")}
                </span>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                  className="w-full border border-ink/22 bg-paper-raised px-3.5 py-2.5 text-sm text-ink outline-none focus:border-ink"
                />
              </label>

              <label className="block space-y-1.5">
                <span className="text-[11px] font-semibold uppercase tracking-[0.16em] text-ink-muted">
                  {t("auth.password")}
                </span>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={10}
                  maxLength={128}
                  autoComplete={isRegister ? "new-password" : "current-password"}
                  className="w-full border border-ink/22 bg-paper-raised px-3.5 py-2.5 text-sm text-ink outline-none focus:border-ink"
                />
                {isRegister && (
                  <span className="block text-[11px] text-ink-muted">{t("auth.passwordHint")}</span>
                )}
              </label>

              {isRegister && (
                <label className="block space-y-1.5">
                  <span className="text-[11px] font-semibold uppercase tracking-[0.16em] text-ink-muted">
                    {t("auth.confirmPassword")}
                  </span>
                  <input
                    type="password"
                    value={confirm}
                    onChange={(e) => setConfirm(e.target.value)}
                    required
                    minLength={10}
                    maxLength={128}
                    autoComplete="new-password"
                    className="w-full border border-ink/22 bg-paper-raised px-3.5 py-2.5 text-sm text-ink outline-none focus:border-ink"
                  />
                </label>
              )}

              {localError ? (
                <p role="alert" className="border border-signal/30 bg-signal-soft px-3 py-2 text-sm text-signal">
                  {localError}
                </p>
              ) : null}

              <button
                type="submit"
                disabled={!canSubmit}
                className="button-lift w-full bg-ink px-4 py-3.5 text-[11px] font-semibold uppercase tracking-[0.22em] text-paper-raised hover:bg-ink-soft disabled:cursor-not-allowed disabled:opacity-35"
              >
                {busy ? t("auth.working") : isRegister ? t("auth.register") : t("auth.submit")}
              </button>
            </form>
          </div>

          <p className="mt-6 text-center text-xs text-ink-muted">
            {isRegister ? (
              <>
                {t("auth.haveAccount")}{" "}
                <button
                  type="button"
                  onClick={() => switchMode("login")}
                  className="font-semibold text-ink underline-offset-4 hover:underline"
                >
                  {t("auth.submit")}
                </button>
              </>
            ) : (
              <>
                {t("auth.noAccount")}{" "}
                <button
                  type="button"
                  onClick={() => switchMode("register")}
                  className="font-semibold text-ink underline-offset-4 hover:underline"
                >
                  {t("auth.register")}
                </button>
              </>
            )}
          </p>
        </div>
      </main>
    </div>
  );
}
