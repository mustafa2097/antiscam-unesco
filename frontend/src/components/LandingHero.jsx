import { useTranslation } from "react-i18next";

const FLOW_KEYS = ["offer", "check", "result"];

export default function LandingHero({ onLogin, onRegister }) {
  const { t, i18n } = useTranslation();
  const dir = i18n.language?.startsWith("ar") ? "rtl" : "ltr";

  return (
    <section
      id="landing"
      dir={dir}
      className="relative overflow-hidden border-b border-black/15 bg-[#f4f0e8]"
    >
      <div className="landing-grid" aria-hidden="true" />
      <span className="office-accent office-accent--navy" aria-hidden="true" />
      <span className="office-accent office-accent--rust" aria-hidden="true" />

      <div className="relative mx-auto flex max-w-6xl flex-col items-center px-5 pb-20 pt-24 text-center sm:px-8 lg:pb-28 lg:pt-32">
        <p className="landing-reveal mb-8 text-[11px] font-bold uppercase tracking-[0.3em] text-black/55">
          {t("landing.eyebrow")}
        </p>

        <h1 className="landing-title landing-reveal landing-delay-1 max-w-5xl text-balance font-sans text-4xl font-black leading-[0.96] tracking-[-0.045em] text-black sm:text-6xl lg:text-[5.5rem]">
          {t("landing.title")}
        </h1>

        <p className="landing-reveal landing-delay-2 mt-8 max-w-2xl text-pretty text-base leading-7 text-black/62 sm:text-lg">
          {t("landing.subtitle")}
        </p>

        <div className="landing-reveal landing-delay-3 mt-10 flex w-full max-w-md flex-col gap-3 sm:flex-row sm:justify-center">
          <button
            type="button"
            onClick={onLogin}
            className="button-lift min-h-12 flex-1 bg-black px-7 py-3 text-xs font-bold uppercase tracking-[0.18em] text-white hover:bg-[#21384c] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-black"
          >
            {t("auth.submit")}
          </button>
          <button
            type="button"
            onClick={onRegister}
            className="button-lift min-h-12 flex-1 border border-black bg-white px-7 py-3 text-xs font-bold uppercase tracking-[0.18em] text-black hover:border-[#b45b3b] hover:bg-[#b45b3b] hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-black"
          >
            {t("landing.createAccount")}
          </button>
        </div>

        <div className="service-flow landing-reveal landing-delay-3 mt-12 grid w-full max-w-3xl grid-cols-3 border border-black/20 bg-[#fbfaf7] text-start">
          {FLOW_KEYS.map((key, index) => (
            <button
              key={key}
              type="button"
              className={`flow-item flow-item--${index % 2 === 0 ? "navy" : "rust"} flex items-center gap-3 border-e border-black/15 px-3 py-4 last:border-e-0 sm:px-5`}
            >
              <span className="flow-index font-mono text-[10px] font-bold text-[#b45b3b]">
                {String(index + 1).padStart(2, "0")}
              </span>
              <span className="flow-label text-[10px] font-bold uppercase tracking-[0.16em] text-black/70 sm:text-xs">
                {t(`landing.flow.${key}`)}
              </span>
            </button>
          ))}
        </div>

        <figure className="office-visual mt-10 w-full max-w-5xl overflow-hidden border border-black/20 bg-[#e8dfd0] p-2 text-start">
          <div className="relative overflow-hidden">
            <img
              src="/anti-scam-office-desk.png"
              alt={t("landing.imageAlt")}
              className="h-[260px] w-full object-cover grayscale-[18%] sm:h-[390px] lg:h-[470px]"
              loading="eager"
            />
            <div className="absolute bottom-4 end-4 flex border border-black/20 bg-[#fbfaf7]/95 text-[9px] font-bold uppercase tracking-[0.16em] text-black/65 backdrop-blur-sm">
              <span className="border-e border-black/15 px-3 py-2">{t("scanner.tabs.text")}</span>
              <span className="border-e border-black/15 px-3 py-2">{t("scanner.tabs.link")}</span>
              <span className="px-3 py-2">{t("scanner.tabs.image")}</span>
            </div>
          </div>
        </figure>
      </div>
    </section>
  );
}
