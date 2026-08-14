import { useTranslation } from "react-i18next";

import { useAuth } from "../context/AuthContext";
import { goToSection } from "../hooks/useSectionHashSync";
import { navigateTo } from "../utils/navigation";
import LanguageToggle from "./LanguageToggle";

export default function SiteHeader({ onLoginClick }) {
  const { t } = useTranslation();
  const { user, loading, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigateTo("/", { replace: true });
    window.scrollTo({ top: 0, behavior: "auto" });
  };

  return (
    <header className="nav-glass sticky top-0 z-40">
      <div className="mx-auto flex max-w-5xl items-center justify-between gap-3 px-4 py-3.5 sm:px-6 md:grid md:grid-cols-[1fr_auto_1fr]">
        <div className="flex min-w-0 items-center gap-3 sm:gap-4 md:justify-self-start">
          <button
            type="button"
            onClick={() => {
              navigateTo("/scanner", { replace: true });
              document.getElementById("scanner")?.scrollIntoView({ behavior: "smooth", block: "start" });
            }}
            className="flex shrink-0 items-baseline gap-3 text-ink"
          >
            <span className="font-display text-lg font-semibold tracking-tight">
              {t("nav.brand")}
            </span>
            <span className="hidden text-[10px] font-medium uppercase tracking-[0.24em] text-ink-muted sm:inline">
              · IQ
            </span>
          </button>
        </div>

        <nav className="hidden items-center justify-center gap-6 text-[11px] font-semibold uppercase tracking-[0.18em] text-ink-muted md:flex">
          <button
            type="button"
            onClick={() => goToSection("scanner")}
            className="transition hover:text-ink"
          >
            {t("scanner.tabs.label")}
          </button>
          <button
            type="button"
            onClick={() => goToSection("opportunities")}
            className="transition hover:text-ink"
          >
            {t("opportunities.title")}
          </button>
          <button
            type="button"
            onClick={() => {
              navigateTo("/guides", { replace: false });
              window.scrollTo({ top: 0, behavior: "auto" });
            }}
            className="transition hover:text-ink"
          >
            {t("guides.title")}
          </button>
        </nav>

        <div className="flex shrink-0 items-center gap-2 sm:gap-3 md:justify-self-end">
          {!loading && user ? (
            <>
              <span className="hidden max-w-[140px] truncate text-[11px] uppercase tracking-wider text-ink-muted sm:inline">
                {user.full_name || user.email}
              </span>
              <button
                type="button"
                onClick={handleLogout}
                className="border border-ink/25 px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-ink transition hover:border-ink hover:bg-ink hover:text-paper-raised"
              >
                {t("nav.logout")}
              </button>
              <LanguageToggle />
            </>
          ) : (
            <>
              <button
                type="button"
                onClick={onLoginClick}
                className="bg-ink px-3.5 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-paper-raised transition hover:bg-ink-soft"
              >
                {t("nav.login")}
              </button>
              <LanguageToggle />
            </>
          )}
        </div>
      </div>
    </header>
  );
}
