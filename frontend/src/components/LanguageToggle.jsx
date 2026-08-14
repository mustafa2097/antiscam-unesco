import { useTranslation } from "react-i18next";

export default function LanguageToggle() {
  const { i18n } = useTranslation();
  const isArabic = i18n.language?.startsWith("ar");

  return (
    <button
      type="button"
      onClick={() => i18n.changeLanguage(isArabic ? "en" : "ar")}
      className="button-lift border border-ink/25 px-2.5 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-ink hover:border-ink hover:bg-ink hover:text-paper-raised"
      aria-label="Language"
    >
      {isArabic ? "EN" : "ع"}
    </button>
  );
}
