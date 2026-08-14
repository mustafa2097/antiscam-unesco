import { useTranslation } from "react-i18next";

import LanguageToggle from "./LanguageToggle";

export default function LandingHeader({ onLogin, onRegister }) {
  const { t, i18n } = useTranslation();
  const dir = i18n.language?.startsWith("ar") ? "rtl" : "ltr";

  return (
    <header dir={dir} className="nav-glass sticky top-0 z-50">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-3 px-4 py-3 sm:px-8">
        <button
          type="button"
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
          className="brand-wordmark shrink-0 font-sans text-base font-bold text-black sm:text-lg"
        >
          {t("nav.brand")}
        </button>

        <nav className="flex items-center gap-2 sm:gap-3" aria-label={t("landing.navigation")}>
          <button
            type="button"
            onClick={onLogin}
            className="button-lift px-3 py-2 text-[10px] font-bold uppercase tracking-[0.18em] text-black hover:bg-black/5"
          >
            {t("auth.submit")}
          </button>
          <button
            type="button"
            onClick={onRegister}
            className="button-lift hidden border border-black bg-black px-3.5 py-2 text-[10px] font-bold uppercase tracking-[0.16em] text-white hover:border-[#21384c] hover:bg-[#21384c] sm:inline-flex"
          >
            {t("landing.createAccount")}
          </button>
          <LanguageToggle />
        </nav>
      </div>
    </header>
  );
}
