import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";

import { CATEGORIES } from "../constants/opportunities";

function Chevron({ open }) {
  return (
    <svg
      viewBox="0 0 12 12"
      className={`h-2.5 w-2.5 transition-transform ${open ? "rotate-180" : ""}`}
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      aria-hidden
    >
      <path d="M2 4l4 4 4-4" />
    </svg>
  );
}

export default function CategoryFilterBar({ category, sub, onChange, vertical = false }) {
  const { t } = useTranslation();
  const [openMenu, setOpenMenu] = useState(null);
  const barRef = useRef(null);

  useEffect(() => {
    const close = (event) => {
      if (barRef.current && !barRef.current.contains(event.target)) {
        setOpenMenu(null);
      }
    };
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, []);

  const selectCategory = (id) => {
    if (category === id) {
      onChange({ category: null, sub: null });
      setOpenMenu(null);
      return;
    }
    onChange({ category: id, sub: null });
    setOpenMenu((current) => (current === id ? null : id));
  };

  const selectSub = (catId, subId) => {
    onChange({ category: catId, sub: subId });
    setOpenMenu(null);
  };

  const activeSubLabel = (cat) => {
    if (category !== cat.id || !sub) return null;
    const found = cat.subs?.find((s) => s.id === sub);
    return found ? t(found.labelKey) : null;
  };

  if (vertical) {
    return (
      <div ref={barRef} className="flex flex-col divide-y divide-ink/18 border border-ink/22">
        {CATEGORIES.map((cat) => {
          const active = category === cat.id;
          const subLabel = activeSubLabel(cat);
          const hasSubs = Boolean(cat.subs?.length);
          const menuOpen = openMenu === cat.id;

          return (
            <div key={cat.id} className={active ? "bg-ink text-paper-raised" : "bg-paper-raised"}>
              <div className="flex items-stretch">
                <button
                  type="button"
                  onClick={() => selectCategory(cat.id)}
                  className={`flex-1 px-4 py-3 text-start text-sm font-semibold transition ${
                    active ? "text-paper-raised" : "text-ink-soft hover:bg-paper"
                  }`}
                >
                  <span>{t(cat.labelKey)}</span>
                  {subLabel ? (
                    <span
                      className={`ms-2 text-xs font-normal ${
                        active ? "text-paper/80" : "text-ink-muted"
                      }`}
                    >
                      · {subLabel}
                    </span>
                  ) : null}
                </button>
                {hasSubs ? (
                  <button
                    type="button"
                    aria-expanded={menuOpen}
                    onClick={() => {
                      if (!active) onChange({ category: cat.id, sub: null });
                      setOpenMenu(menuOpen ? null : cat.id);
                    }}
                    className={`flex items-center border-s px-3 transition ${
                      active
                        ? "border-paper/25 text-paper-raised"
                        : "border-paper-line text-ink-muted hover:text-ink"
                    }`}
                    aria-label={`${t(cat.labelKey)} ${t("opportunities.subs.menu")}`}
                  >
                    <Chevron open={menuOpen} />
                  </button>
                ) : null}
              </div>

              {hasSubs && menuOpen ? (
                <ul role="menu" className="border-t border-paper-line bg-paper-raised text-ink">
                  <li role="none">
                    <button
                      type="button"
                      role="menuitem"
                      onClick={() => selectSub(cat.id, null)}
                      className={`block w-full px-6 py-2 text-start text-sm hover:bg-paper ${
                        category === cat.id && !sub ? "font-semibold text-ink" : "text-ink-soft"
                      }`}
                    >
                      {t("opportunities.subs.all")}
                    </button>
                  </li>
                  {cat.subs.map((item) => (
                    <li key={item.id} role="none">
                      <button
                        type="button"
                        role="menuitem"
                        onClick={() => selectSub(cat.id, item.id)}
                        className={`block w-full px-6 py-2 text-start text-sm hover:bg-paper ${
                          category === cat.id && sub === item.id
                            ? "font-semibold text-ink"
                            : "text-ink-soft"
                        }`}
                      >
                        {t(item.labelKey)}
                      </button>
                    </li>
                  ))}
                </ul>
              ) : null}
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <div ref={barRef} className="flex flex-wrap items-stretch gap-0 border border-paper-line bg-paper">
      {CATEGORIES.map((cat, index) => {
        const active = category === cat.id;
        const subLabel = activeSubLabel(cat);
        const hasSubs = Boolean(cat.subs?.length);
        const menuOpen = openMenu === cat.id;

        return (
          <div
            key={cat.id}
            className={`relative flex ${index > 0 ? "border-s border-paper-line" : ""}`}
          >
            <button
              type="button"
              onClick={() => selectCategory(cat.id)}
              className={`px-4 py-3 text-sm font-semibold transition ${
                active ? "bg-ink text-paper-raised" : "text-ink-soft hover:bg-paper-raised"
              }`}
            >
              {t(cat.labelKey)}
              {subLabel ? (
                <span className={`ms-2 text-xs font-normal ${active ? "text-paper/80" : "text-ink-muted"}`}>
                  · {subLabel}
                </span>
              ) : null}
            </button>

            {hasSubs ? (
              <button
                type="button"
                aria-expanded={menuOpen}
                aria-label={`${t(cat.labelKey)} ${t("opportunities.subs.menu")}`}
                onClick={() => {
                  if (!active) onChange({ category: cat.id, sub: null });
                  setOpenMenu(menuOpen ? null : cat.id);
                }}
                className={`flex items-center border-s border-paper-line px-2.5 transition ${
                  active ? "bg-ink text-paper-raised" : "text-ink-muted hover:bg-paper-raised hover:text-ink"
                }`}
              >
                <Chevron open={menuOpen} />
              </button>
            ) : null}

            {hasSubs && menuOpen ? (
              <ul
                role="menu"
                className="absolute inset-x-0 top-full z-20 border border-paper-line bg-paper-raised shadow-panel"
              >
                <li role="none">
                  <button
                    type="button"
                    role="menuitem"
                    onClick={() => selectSub(cat.id, null)}
                    className="block w-full px-4 py-2.5 text-start text-sm text-ink-soft hover:bg-paper"
                  >
                    {t("opportunities.subs.all")}
                  </button>
                </li>
                {cat.subs.map((item) => (
                  <li key={item.id} role="none">
                    <button
                      type="button"
                      role="menuitem"
                      onClick={() => selectSub(cat.id, item.id)}
                      className={`block w-full px-4 py-2.5 text-start text-sm hover:bg-paper ${
                        category === cat.id && sub === item.id
                          ? "font-semibold text-ink"
                          : "text-ink-soft"
                      }`}
                    >
                      {t(item.labelKey)}
                    </button>
                  </li>
                ))}
              </ul>
            ) : null}
          </div>
        );
      })}
    </div>
  );
}
