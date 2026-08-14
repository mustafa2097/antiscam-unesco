import { useTranslation } from "react-i18next";

import { IRAQI_GOVERNORATES } from "../constants/opportunities";

function governorateLabel(gov, isArabic) {
  if (!gov) return "";
  return isArabic ? gov.nameAr : gov.nameEn;
}

function categoryLabel(item, t) {
  const key = `opportunities.categories.${item.category}`;
  const translated = t(key);
  return translated !== key ? translated : item.category;
}

function modeLabel(item, t) {
  if (item.category === "job" || item.category === "internship") {
    return item.mode === "online" ? t("opportunities.subs.online") : t("opportunities.subs.onsite");
  }
  if (item.category === "course" || item.category === "scholarship") {
    return item.is_free ? t("opportunities.subs.free") : t("opportunities.subs.paid");
  }
  return null;
}

export default function OpportunityCard({ item, index, isArabic }) {
  const { t } = useTranslation();
  const title = isArabic && item.title_ar ? item.title_ar : item.title_en;
  const gov = IRAQI_GOVERNORATES.find((g) => g.slug === item.governorate);
  const govName = gov ? governorateLabel(gov, isArabic) : item.governorate;
  const cat = categoryLabel(item, t);
  const mode = modeLabel(item, t);
  const accent = index % 2 === 0 ? "bg-[#b45b3b]" : "bg-[#21384c]";

  return (
    <article className="hover-lift group relative flex h-full flex-col border border-ink/20 bg-paper-raised">
      <span className={`absolute inset-x-0 top-0 h-1 origin-left scale-x-0 transition-transform duration-300 group-hover:scale-x-100 ${accent}`} />
      <header className="flex items-center justify-between border-b border-ink/18 bg-paper/60 px-5 py-3">
        <span className="font-display text-xs font-semibold tracking-[0.2em] text-ink-muted">
          {String(index).padStart(2, "0")}
        </span>
        <span className="text-[10px] font-semibold uppercase tracking-[0.16em] text-ink">
          {cat}
          {mode ? <span className="text-ink-muted"> · {mode}</span> : null}
        </span>
      </header>

      <div className="flex flex-1 flex-col p-5">
        <h3 className="font-display text-lg font-semibold leading-snug text-ink">{title}</h3>
        {item.organization ? (
          <p className="mt-1 text-sm text-ink-muted">{item.organization}</p>
        ) : null}

        <div className="mt-auto space-y-2 pt-6">
          <div className="flex items-center justify-between gap-2">
            <span className="text-[11px] font-medium uppercase tracking-[0.14em] text-ink-muted">
              {govName || "—"}
            </span>
            {item.deadline ? (
              <span className="text-[10px] font-medium uppercase tracking-[0.12em] text-ink-muted">
                {t("opportunities.meta.deadline")}: {item.deadline}
              </span>
            ) : null}
          </div>
          <div className="flex flex-wrap items-center gap-3">
            {item.source_url ? (
              <a
                href={item.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-[11px] font-semibold uppercase tracking-[0.16em] text-ink underline-offset-4 hover:underline"
              >
                {t("opportunities.meta.openDirect")} →
              </a>
            ) : null}
            {item.fallback_url ? (
              <a
                href={item.fallback_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-[11px] font-medium uppercase tracking-[0.14em] text-ink-muted underline-offset-4 hover:text-ink hover:underline"
              >
                {t("opportunities.meta.fallback")} ↗
              </a>
            ) : null}
          </div>
        </div>
      </div>
    </article>
  );
}
