import { useTranslation } from "react-i18next";

export const GUIDE_ARTICLES = [
  {
    id: "ftc-job-scams",
    source: "FTC",
    href: "https://consumer.ftc.gov/articles/job-scams",
    titleKey: "guides.items.ftcJobScams.title",
    image: "/guides/ftc-job-scams.png",
    imageAlt: "FTC job scams article graphic",
  },
  {
    id: "ftc-recruiters",
    source: "FTC",
    href: "https://consumer.ftc.gov/consumer-alerts/2025/07/job-scammers-are-looking-hire-you",
    titleKey: "guides.items.ftcRecruiters.title",
    image: "/guides/ftc-recruiters.jpg",
    imageAlt: "FTC job scammer recruiters alert graphic",
  },
  {
    id: "ftc-text-scam",
    source: "FTC",
    href: "https://consumer.ftc.gov/consumer-alerts/2026/04/job-offer-text-probably-scam",
    titleKey: "guides.items.ftcTextScam.title",
    image: "/guides/ftc-text-scam.jpg",
    imageAlt: "FTC fake job offer text scam alert graphic",
  },
  {
    id: "interpol",
    source: "INTERPOL",
    href: "https://www.interpol.int/News-and-Events/News/2025/INTERPOL-releases-new-information-on-globalization-of-scam-centres",
    titleKey: "guides.items.interpol.title",
    image: "/guides/interpol-scam-centres.jpg",
    imageAlt: "INTERPOL scam centres crime trend update",
  },
  {
    id: "consumer-gov",
    source: "consumer.gov",
    href: "https://consumer.gov/scams-identity-theft/job-scams-explained",
    titleKey: "guides.items.consumerGov.title",
    image: "/guides/consumer-gov.jpg",
    imageAlt: "consumer.gov job scams explained",
  },
  {
    id: "scamlens",
    source: "ScamLens",
    href: "https://scamlens.org/ar/scams/job",
    titleKey: "guides.items.scamlens.title",
    image: "/guides/scamlens.png",
    imageAlt: "ScamLens job fraud guide",
  },
];

export default function GuidesArticles() {
  const { t, i18n } = useTranslation();
  const dir = i18n.language?.startsWith("ar") ? "rtl" : "ltr";

  return (
    <div dir={dir} className="relative overflow-hidden">
      <div className="mx-auto w-full max-w-5xl px-4 py-14 sm:px-6 sm:py-16">
        <div className="border-b border-ink/15 pb-4">
          <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-ink-muted">
            {t("guides.eyebrow")}
          </p>
          <h1 className="mt-3 font-display text-3xl font-semibold tracking-tight text-ink sm:text-4xl">
            {t("guides.title")}
          </h1>
        </div>

        <ul className="mt-10 grid gap-5 sm:grid-cols-2">
          {GUIDE_ARTICLES.map((article, index) => (
            <li key={article.id}>
              <a
                href={article.href}
                target="_blank"
                rel="noreferrer"
                className="group flex h-full flex-col overflow-hidden border border-ink/15 bg-paper-raised transition hover:border-ink/35"
              >
                <div className="relative aspect-[16/9] overflow-hidden border-b border-ink/10 bg-[#e8dfd0]">
                  <img
                    src={article.image}
                    alt={article.imageAlt}
                    loading="lazy"
                    className="h-full w-full object-cover transition duration-500 group-hover:scale-[1.03]"
                  />
                </div>
                <div className="flex flex-1 flex-col gap-3 p-4 sm:p-5">
                  <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-ink-muted">
                    <span className="metric-number text-ink/45">
                      {String(index + 1).padStart(2, "0")}
                    </span>
                    <span className="mx-2 text-ink/25">·</span>
                    {article.source}
                  </p>
                  <p className="font-display text-lg font-semibold leading-snug text-ink group-hover:text-[#21384c]">
                    {t(article.titleKey)}
                  </p>
                  <span className="mt-auto pt-2 text-[11px] font-semibold uppercase tracking-[0.16em] text-ink-muted transition group-hover:text-ink">
                    {t("guides.open")} ↗
                  </span>
                </div>
              </a>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
