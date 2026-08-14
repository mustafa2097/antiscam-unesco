import { useTranslation } from "react-i18next";

const ARTICLES = [
  {
    id: "ftc-job-scams",
    source: "FTC",
    href: "https://consumer.ftc.gov/articles/job-scams",
    titleKey: "guides.items.ftcJobScams.title",
  },
  {
    id: "ftc-recruiters",
    source: "FTC",
    href: "https://consumer.ftc.gov/consumer-alerts/2025/07/job-scammers-are-looking-hire-you",
    titleKey: "guides.items.ftcRecruiters.title",
  },
  {
    id: "consumer-gov",
    source: "consumer.gov",
    href: "https://consumer.gov/scams-identity-theft/job-scams-explained",
    titleKey: "guides.items.consumerGov.title",
  },
  {
    id: "indeed",
    source: "Indeed",
    href: "https://www.indeed.com/career-advice/finding-a-job/how-to-know-if-a-job-is-a-scam",
    titleKey: "guides.items.indeed.title",
  },
  {
    id: "scamlens",
    source: "ScamLens",
    href: "https://scamlens.org/ar/scams/job",
    titleKey: "guides.items.scamlens.title",
  },
];

export default function GuidesArticles() {
  const { t, i18n } = useTranslation();
  const dir = i18n.language?.startsWith("ar") ? "rtl" : "ltr";

  return (
    <div id="guides" dir={dir} className="relative overflow-hidden">
      <div className="mx-auto w-full max-w-5xl px-4 py-14 sm:px-6 sm:py-16">
        <div className="border-b border-ink/15 pb-4">
          <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-ink-muted">
            {t("guides.eyebrow")}
          </p>
          <h2 className="mt-3 font-display text-3xl font-semibold tracking-tight text-ink sm:text-4xl">
            {t("guides.title")}
          </h2>
        </div>

        <ul className="mt-8 divide-y divide-ink/12 border border-ink/15 bg-paper-raised">
          {ARTICLES.map((article, index) => (
            <li key={article.id}>
              <a
                href={article.href}
                target="_blank"
                rel="noreferrer"
                className="group flex items-baseline justify-between gap-4 px-4 py-4 transition hover:bg-[#f4f0e8] sm:px-5"
              >
                <div className="min-w-0">
                  <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-ink-muted">
                    <span className="metric-number text-ink/45">
                      {String(index + 1).padStart(2, "0")}
                    </span>
                    <span className="mx-2 text-ink/25">·</span>
                    {article.source}
                  </p>
                  <p className="mt-1.5 font-display text-base font-semibold text-ink group-hover:text-[#21384c] sm:text-lg">
                    {t(article.titleKey)}
                  </p>
                </div>
                <span
                  className="shrink-0 text-sm text-ink-muted transition group-hover:text-ink"
                  aria-hidden="true"
                >
                  ↗
                </span>
              </a>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
