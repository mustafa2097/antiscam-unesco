import { useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";

import { useScan } from "../context/ScanContext";
import { roleLabel } from "../constants/opportunities";
import { goToSection } from "../hooks/useSectionHashSync";
import { scanImage, scanLink, scanText } from "../services/scan";
import Marquee from "./Marquee";

const MARQUEE_KEYS = [
  "opportunities.categories.job",
  "opportunities.subs.online",
  "opportunities.subs.onsite",
  "opportunities.categories.course",
  "opportunities.subs.paid",
  "opportunities.subs.free",
  "opportunities.categories.volunteer",
  "opportunities.meta.verified",
];

export { scanLink };

function mergeResults(results) {
  const valid = results.filter(Boolean);
  if (!valid.length) return null;

  const best = [...valid].sort(
    (a, b) => (Number(b.risk_score) || 0) - (Number(a.risk_score) || 0),
  )[0];

  const detected = valid
    .map((r) => r?.metadata?.detected_role)
    .find((r) => Boolean(r));

  const recommendations =
    valid.map((r) => r?.metadata?.recommendations).find(Boolean) ||
    best?.metadata?.recommendations ||
    null;

  return {
    ...best,
    matched_indicators: [
      ...new Set(valid.flatMap((r) => r.matched_indicators || [])),
    ].slice(0, 12),
    flags: [...new Set(valid.flatMap((r) => r.flags || []))],
    metadata: {
      ...(best.metadata || {}),
      detected_role: detected || null,
      recommendations,
    },
  };
}

function riskTone(level) {
  if (level === "high") return "text-signal";
  if (level === "medium") return "text-[#b45b3b]";
  if (level === "low") return "text-[#21384c]";
  return "text-ink";
}

export default function ScannerHero() {
  const { t, i18n } = useTranslation();
  const dir = i18n.language?.startsWith("ar") ? "rtl" : "ltr";
  const isArabic = i18n.language?.startsWith("ar");
  const { applyScanResult } = useScan();

  const [text, setText] = useState("");
  const [link, setLink] = useState("");
  const [file, setFile] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const resultRef = useRef(null);

  const canSubmit = useMemo(() => {
    if (submitting) return false;
    return text.trim().length > 0 || link.trim().length > 0 || Boolean(file);
  }, [text, link, file, submitting]);

  useEffect(() => {
    if (!result) return undefined;
    const timer = window.setTimeout(() => {
      resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 80);
    return () => window.clearTimeout(timer);
  }, [result]);

  const onSubmit = async (event) => {
    event.preventDefault();
    if (!canSubmit) return;

    setSubmitting(true);
    setError(null);
    setResult(null);

    try {
      const jobs = [];
      if (text.trim()) jobs.push(scanText(text.trim()));
      if (link.trim()) jobs.push(scanLink(link.trim()));
      if (file) jobs.push(scanImage(file));

      const results = await Promise.all(jobs);
      const merged = mergeResults(results);
      setResult(merged);
      if (merged) applyScanResult(merged);
    } catch (err) {
      setError(err instanceof Error ? err.message : "scan_failed");
    } finally {
      setSubmitting(false);
    }
  };

  const detectedRole = result?.metadata?.detected_role;
  const riskPct =
    result?.risk_score != null ? Math.round(Number(result.risk_score) * 100) : null;
  const riskLevel = result?.risk_level || null;
  const indicators = result?.matched_indicators || [];
  const recommendations = result?.metadata?.recommendations;
  const curatedCourses = recommendations?.curated_courses || [];
  const curatedJobs = recommendations?.curated_jobs || [];
  const dbCourses = recommendations?.courses || [];
  const dbJobs = recommendations?.jobs || [];
  const marqueeItems = MARQUEE_KEYS.map((k) => t(k));

  return (
    <div id="scanner" dir={dir} className="relative overflow-hidden">
      <span className="workspace-accent workspace-accent--navy" aria-hidden="true" />
      <span className="workspace-accent workspace-accent--rust" aria-hidden="true" />
      <div className="mx-auto w-full max-w-5xl px-4 pb-16 pt-14 sm:px-6 sm:pt-20">
        <div className="border-b border-ink/15 pb-4">
          <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-ink-muted">
            {t("scanner.eyebrow")}
          </p>
        </div>

        <div className="mt-12 grid gap-12 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.15fr)] lg:gap-16">
          <div className="flex flex-col anim-fade-up">
            <h1 className="font-display text-[3rem] font-semibold leading-[1] tracking-[-0.02em] text-ink sm:text-[4.25rem]">
              {t("scanner.title")}
            </h1>
            <div className="mt-8 flex items-center gap-3">
              <span className="h-px flex-1 max-w-[80px] bg-ink" />
              <span className="text-[10px] font-semibold uppercase tracking-[0.24em] text-ink-muted">
                {t("scanner.badge")}
              </span>
            </div>
            <figure className="workspace-preview mt-10 hidden overflow-hidden border border-ink/20 bg-[#e8dfd0] p-1.5 lg:block">
              <img
                src="/anti-scam-document-analysis.png"
                alt=""
                aria-hidden="true"
                className="h-28 w-full object-cover grayscale-[22%]"
              />
            </figure>
          </div>

          <form
            id="scan-form"
            onSubmit={onSubmit}
            className="panel workspace-panel relative anim-fade-up anim-delay-2"
          >
            <div className="absolute -top-[7px] end-4 flex gap-1" aria-hidden="true">
              <span className="h-[6px] w-10 bg-[#21384c]" />
              <span className="h-[6px] w-6 bg-[#b45b3b]" />
            </div>
            <div className="space-y-5 p-5 sm:p-6">
              <div className="space-y-2">
                <label className="text-[10px] font-semibold uppercase tracking-[0.2em] text-ink-muted">
                  {t("scanner.tabs.text")}
                </label>
                <textarea
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  rows={5}
                  maxLength={10000}
                  placeholder={t("scanner.form.textPlaceholder")}
                  className="w-full resize-y border border-ink/22 bg-paper-raised px-3.5 py-3 text-sm leading-relaxed text-ink outline-none transition placeholder:text-ink-muted/60 focus:border-ink"
                />
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <label className="text-[10px] font-semibold uppercase tracking-[0.2em] text-ink-muted">
                    {t("scanner.tabs.link")}
                  </label>
                  <input
                    type="url"
                    value={link}
                    onChange={(e) => setLink(e.target.value)}
                    placeholder={t("scanner.form.linkPlaceholder")}
                    maxLength={2048}
                    className="w-full border border-ink/22 bg-paper-raised px-3.5 py-2.5 text-sm text-ink outline-none transition placeholder:text-ink-muted/60 focus:border-ink"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-[10px] font-semibold uppercase tracking-[0.2em] text-ink-muted">
                    {t("scanner.tabs.image")}
                  </label>
                  <label className="flex h-[42px] cursor-pointer items-center justify-between border border-dashed border-ink/28 bg-paper-raised px-3.5 text-sm text-ink-muted transition hover:border-ink hover:text-ink">
                    <span className="truncate">
                      {file ? file.name : t("scanner.form.imageHint")}
                    </span>
                    <span className="font-display text-base text-ink">↑</span>
                    <input
                      type="file"
                      accept="image/jpeg,image/png,image/webp,image/gif,application/pdf"
                      onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                      className="hidden"
                    />
                  </label>
                </div>
              </div>

              {error ? (
                <p role="alert" className="border border-signal/30 bg-signal-soft px-3 py-2 text-sm text-signal">
                  {error}
                </p>
              ) : null}

              <button
                type="submit"
                disabled={!canSubmit}
                className="button-lift w-full bg-ink px-4 py-3.5 text-[11px] font-semibold uppercase tracking-[0.22em] text-paper-raised hover:bg-[#21384c] disabled:cursor-not-allowed disabled:opacity-35"
              >
                {submitting ? t("scanner.form.scanning") : t("scanner.form.submit")}
              </button>
            </div>

            {result ? (
              <div
                id="scan-result"
                ref={resultRef}
                className="space-y-4 border-t rule-strong bg-paper/70 px-5 py-4 sm:px-6 anim-fade-in"
              >
                {riskPct != null ? (
                  <div className="flex flex-wrap items-end justify-between gap-3">
                    <div>
                      <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-ink-muted">
                        {t("scanner.result.risk")}
                      </p>
                      <p className={`mt-1 font-display text-3xl font-semibold ${riskTone(riskLevel)}`}>
                        {riskPct}%
                        {riskLevel ? (
                          <span className="ms-2 text-sm font-semibold uppercase tracking-[0.14em]">
                            {t(`scanner.result.levels.${riskLevel}`)}
                          </span>
                        ) : null}
                      </p>
                    </div>
                    <div className="h-1.5 w-36 max-w-full bg-ink/10">
                      <div
                        className="h-full bg-[#b45b3b]"
                        style={{ width: `${Math.min(riskPct, 100)}%` }}
                      />
                    </div>
                  </div>
                ) : null}

                {indicators.length ? (
                  <ul className="flex flex-wrap gap-2">
                    {indicators.slice(0, 6).map((item) => (
                      <li
                        key={item}
                        className="border border-ink/15 bg-paper-raised px-2 py-1 text-[11px] text-ink-muted"
                      >
                        {item}
                      </li>
                    ))}
                  </ul>
                ) : null}

                {detectedRole ? (
                  <div>
                    <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-ink-muted">
                      {t("scanner.result.detected")}
                    </p>
                    <p className="mt-1 font-display text-lg font-semibold text-ink">
                      {roleLabel(detectedRole, isArabic)}
                    </p>
                  </div>
                ) : (
                  <p className="text-sm text-ink-muted">{t("scanner.result.noRole")}</p>
                )}

                {recommendations && (riskPct == null || riskPct >= 45) ? (
                  <div className="border border-ink/15 bg-paper-raised p-3">
                    <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-ink-muted">
                      {t("scanner.result.saferPaths")}
                    </p>
                    <p className="mt-2 text-sm text-ink">
                      {isArabic
                        ? recommendations.message_ar
                        : recommendations.message_en}
                    </p>
                    <div className="mt-3 grid gap-3 sm:grid-cols-2">
                      <div>
                        <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-ink-muted">
                          {t("scanner.result.courses")}
                        </p>
                        <ul className="mt-2 space-y-2">
                          {[...dbCourses, ...curatedCourses].slice(0, 4).map((item, idx) => {
                            const title = isArabic
                              ? item.title_ar || item.title_en
                              : item.title_en || item.title_ar;
                            const href = item.source_url || item.url || "#opportunities";
                            const org = item.organization || item.org || "";
                            return (
                              <li key={`c-${idx}`}>
                                <a
                                  href={href}
                                  target={href.startsWith("http") ? "_blank" : undefined}
                                  rel={href.startsWith("http") ? "noreferrer" : undefined}
                                  className="text-sm font-semibold text-ink underline-offset-2 hover:underline"
                                >
                                  {title}
                                </a>
                                {org ? (
                                  <span className="ms-1 text-xs text-ink-muted">· {org}</span>
                                ) : null}
                              </li>
                            );
                          })}
                        </ul>
                      </div>
                      <div>
                        <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-ink-muted">
                          {t("scanner.result.jobs")}
                        </p>
                        <ul className="mt-2 space-y-2">
                          {[...dbJobs, ...curatedJobs].slice(0, 4).map((item, idx) => {
                            const title = isArabic
                              ? item.title_ar || item.title_en
                              : item.title_en || item.title_ar;
                            const href = item.source_url || item.url || "#opportunities";
                            const org = item.organization || item.org || "";
                            return (
                              <li key={`j-${idx}`}>
                                <a
                                  href={href}
                                  target={href.startsWith("http") ? "_blank" : undefined}
                                  rel={href.startsWith("http") ? "noreferrer" : undefined}
                                  className="text-sm font-semibold text-ink underline-offset-2 hover:underline"
                                >
                                  {title}
                                </a>
                                {org ? (
                                  <span className="ms-1 text-xs text-ink-muted">· {org}</span>
                                ) : null}
                              </li>
                            );
                          })}
                        </ul>
                      </div>
                    </div>
                  </div>
                ) : null}

                <button
                  type="button"
                  onClick={() => goToSection("opportunities")}
                  className="opp-hint"
                >
                  <span className="opp-hint__label">{t("scanner.result.seeOpportunities")}</span>
                  <span className="opp-hint__arrow" aria-hidden="true">
                    ↓
                  </span>
                </button>
              </div>
            ) : null}
          </form>
        </div>
      </div>

      <Marquee items={marqueeItems} />
    </div>
  );
}
