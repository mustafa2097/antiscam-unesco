import { useTranslation } from "react-i18next";

const FACTOR_KEYS = ["urgency", "payment", "identity"];
const SIGNALS = [
  { key: "language", score: 94, color: "bg-[#b45b3b]" },
  { key: "identity", score: 82, color: "bg-[#21384c]" },
  { key: "payment", score: 76, color: "bg-black/65" },
];

export default function ScanResultDemo() {
  const { t, i18n } = useTranslation();
  const dir = i18n.language?.startsWith("ar") ? "rtl" : "ltr";

  return (
    <section
      id="landing-demo"
      dir={dir}
      className="scroll-mt-16 border-b border-black/15 bg-[#fbfaf7]"
    >
      <div className="mx-auto max-w-6xl px-5 py-20 sm:px-8 lg:py-28">
        <div className="grid gap-10 lg:grid-cols-[0.75fr_1.25fr] lg:gap-20">
          <div>
            <h2 className="max-w-md text-4xl font-black leading-[0.98] tracking-[-0.04em] text-black sm:text-5xl">
              {t("demo.title")}
            </h2>
            <figure className="reveal-office mt-8 max-w-md border border-black/20 bg-[#e8dfd0] p-2">
              <img
                src="/anti-scam-document-analysis.png"
                alt={t("demo.imageAlt")}
                className="aspect-[4/3] w-full object-cover grayscale-[12%]"
                loading="lazy"
              />
            </figure>
          </div>

          <div className="result-sheet relative self-start border border-black bg-white">
            <div className="absolute -top-[7px] end-4 flex gap-1" aria-hidden="true">
              <span className="h-[6px] w-10 bg-[#21384c]" />
              <span className="h-[6px] w-6 bg-[#b45b3b]" />
            </div>
            <div className="border-b border-black px-5 py-4">
              <span className="text-[10px] font-bold uppercase tracking-[0.24em]">
                {t("demo.report")}
              </span>
            </div>

            <div className="grid sm:grid-cols-[0.8fr_1.2fr]">
              <div className="border-b border-black p-6 sm:border-b-0 sm:border-e">
                <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-black/50">
                  {t("demo.probability")}
                </p>
                <p
                  dir="ltr"
                  className="metric-number mt-5 inline-flex items-baseline text-7xl font-black leading-none tracking-[-0.07em] text-black"
                >
                  <span>89</span>
                  <span className="ms-1 text-3xl">%</span>
                </p>
                <div className="mt-6 h-2 bg-black/10">
                  <div className="metric-bar h-full w-[89%] bg-[#b45b3b]" />
                </div>
              </div>

              <div className="p-6">
                <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-black/50">
                  {t("demo.riskFactors")}
                </p>
                <ol className="mt-5 divide-y divide-black/15 border-y border-black/15">
                  {FACTOR_KEYS.map((key, index) => (
                    <li key={key} className="grid grid-cols-[2rem_1fr] gap-3 py-4">
                      <span className="font-mono text-xs text-black/40">
                        {String(index + 1).padStart(2, "0")}
                      </span>
                      <span className="text-sm font-semibold leading-5 text-black">
                        {t(`demo.factors.${key}`)}
                      </span>
                    </li>
                  ))}
                </ol>
              </div>
            </div>

            <div className="grid gap-px border-t border-black bg-black sm:grid-cols-3">
              {SIGNALS.map(({ key, score, color }, index) => (
                <div
                  key={key}
                  className="bg-[#f4f0e8] p-5"
                  style={{ "--metric-delay": `${index * 120}ms` }}
                >
                  <div className="flex items-baseline justify-between gap-4">
                    <span className="text-[10px] font-bold uppercase tracking-[0.18em] text-black/55">
                      {t(`demo.signals.${key}`)}
                    </span>
                    <span className="font-mono text-sm font-bold">{score}%</span>
                  </div>
                  <div className="mt-3 h-1 bg-black/10">
                    <div
                      className={`metric-bar h-full ${color}`}
                      style={{ width: `${score}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-2 border-t border-black text-[10px] font-bold uppercase tracking-[0.2em]">
              <span className="border-e border-black px-5 py-4 text-black/50">
                {t("demo.statusLabel")}
              </span>
              <span className="px-5 py-4">{t("demo.status")}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
