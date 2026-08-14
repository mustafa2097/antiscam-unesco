import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import ar from "./locales/ar.json";
import en from "./locales/en.json";

const LOCALE_KEY = "antiscam_locale";

function getStoredLocale() {
  try {
    const locale = window.localStorage.getItem(LOCALE_KEY);
    return locale === "ar" || locale === "en" ? locale : null;
  } catch {
    return null;
  }
}

const storedLocale = getStoredLocale();

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    ar: { translation: ar },
  },
  lng: storedLocale || "en",
  fallbackLng: "en",
  interpolation: { escapeValue: true },
  returnNull: false,
  returnEmptyString: false,
});

export function applyDocumentDirection(locale) {
  const dir = locale?.startsWith("ar") ? "rtl" : "ltr";
  document.documentElement.lang = locale || "en";
  document.documentElement.dir = dir;
}

applyDocumentDirection(i18n.language);

i18n.on("languageChanged", (locale) => {
  applyDocumentDirection(locale);
  try {
    window.localStorage.setItem(LOCALE_KEY, locale?.startsWith("ar") ? "ar" : "en");
  } catch {
    // Direction still updates when storage is unavailable.
  }
});

export default i18n;
