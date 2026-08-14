import { useState } from "react";
import { useTranslation } from "react-i18next";

import { IRAQI_GOVERNORATES, roleLabel } from "../constants/opportunities";
import { useScan } from "../context/ScanContext";
import { useOpportunities } from "../hooks/useOpportunities";
import { useReveal } from "../hooks/useReveal";
import CategoryFilterBar from "./CategoryFilterBar";
import OpportunityCard from "./OpportunityCard";

function governorateLabel(gov, isArabic) {
  if (!gov) return "";
  return isArabic ? gov.nameAr : gov.nameEn;
}

export default function OpportunitiesGrid() {
  const { t, i18n } = useTranslation();
  const isArabic = i18n.language?.startsWith("ar");
  const { detectedRole, clearRole } = useScan();

  const [governorate, setGovernorate] = useState("all");
  const [category, setCategory] = useState(null);
  const [sub, setSub] = useState(null);

  const { items, loading, error } = useOpportunities({
    role: detectedRole || "",
    governorate,
    category,
    sub,
  });

  const headerRef = useReveal();
  const bodyRef = useReveal({ threshold: 0.05 });

  const onCategoryChange = ({ category: nextCategory, sub: nextSub }) => {
    setCategory(nextCategory);
    setSub(nextSub);
  };

  const currentGov = IRAQI_GOVERNORATES.find((g) => g.slug === governorate);

  return (
    <div id="opportunities" className="relative overflow-hidden">
      <span className="workspace-accent workspace-accent--navy workspace-accent--directory" aria-hidden="true" />
      <div className="mx-auto w-full max-w-5xl px-4 py-24 sm:px-6 sm:py-28">
        <div ref={headerRef} className="reveal">
          <div className="flex items-baseline justify-between border-b border-ink pb-4">
            <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-ink-muted">
              {t("opportunities.eyebrow")}
            </p>
            <span className="text-[11px] font-medium uppercase tracking-[0.18em] text-ink-muted">
              {loading ? t("opportunities.updating") : t("opportunities.count", { count: items.length })}
            </span>
          </div>

          <h2 className="mt-8 font-display text-4xl font-semibold text-ink sm:text-5xl">
            {t("opportunities.title")}
          </h2>

          {detectedRole ? (
            <div className="mt-6 inline-flex items-center gap-4 border border-ink bg-ink px-4 py-2 text-paper-raised anim-fade-in">
              <span className="text-[10px] font-semibold uppercase tracking-[0.2em] text-paper/70">
                {t("opportunities.aiFilter")}
              </span>
              <span className="font-display text-sm font-semibold">
                {roleLabel(detectedRole, isArabic)}
              </span>
              <button
                type="button"
                onClick={clearRole}
                className="text-[11px] font-semibold uppercase tracking-wider text-paper/80 transition hover:text-paper-raised"
                aria-label={t("opportunities.clear")}
              >
                ✕
              </button>
            </div>
          ) : null}
        </div>

        <div
          ref={bodyRef}
          className="reveal mt-10 grid gap-10 lg:grid-cols-[minmax(0,220px)_minmax(0,1fr)]"
        >
          <aside className="filter-drawer relative space-y-6 border border-ink/20 bg-paper-raised p-4 lg:sticky lg:top-24 lg:self-start">
            <div className="absolute -top-[6px] start-4 flex gap-1" aria-hidden="true">
              <span className="h-[5px] w-8 bg-[#b45b3b]" />
              <span className="h-[5px] w-5 bg-[#21384c]" />
            </div>
            <div className="space-y-2">
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-ink-muted">
                {t("opportunities.governorate")}
              </p>
              <select
                value={governorate}
                onChange={(e) => setGovernorate(e.target.value)}
                className="w-full border border-ink/25 bg-paper-raised px-3 py-2.5 text-sm text-ink outline-none transition focus:border-ink"
              >
                <option value="all">{t("opportunities.allIraq")}</option>
                {IRAQI_GOVERNORATES.map((gov) => (
                  <option key={gov.slug} value={gov.slug}>
                    {governorateLabel(gov, isArabic)}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-ink-muted">
                {t("opportunities.categories.label")}
              </p>
              <CategoryFilterBar category={category} sub={sub} onChange={onCategoryChange} vertical />
            </div>
          </aside>

          <div className="min-w-0">
            {error ? (
              <p role="alert" className="mb-6 border border-signal/30 bg-signal-soft px-4 py-3 text-sm text-signal">
                {error}
              </p>
            ) : null}

            {!loading && items.length === 0 ? (
              <div className="empty-workspace relative overflow-hidden border border-dashed border-ink/25 bg-paper-raised px-6 py-20 text-center anim-fade-in">
                <div className="absolute inset-x-0 top-0 flex h-1" aria-hidden="true">
                  <span className="w-1/3 bg-[#21384c]" />
                  <span className="w-1/6 bg-[#b45b3b]" />
                </div>
                <p className="font-display text-lg text-ink-soft">{t("opportunities.empty")}</p>
              </div>
            ) : (
              <ul className="grid gap-4 sm:grid-cols-2">
                {items.map((item, idx) => (
                  <li
                    key={item.id}
                    className="anim-fade-up"
                    style={{ animationDelay: `${Math.min(idx * 60, 360)}ms` }}
                  >
                    <OpportunityCard item={item} index={idx + 1} isArabic={isArabic} />
                  </li>
                ))}
              </ul>
            )}

            {governorate !== "all" && currentGov ? (
              <p className="mt-6 text-[11px] uppercase tracking-[0.18em] text-ink-muted">
                {t("opportunities.inGovernorate")} · {governorateLabel(currentGov, isArabic)}
              </p>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}
