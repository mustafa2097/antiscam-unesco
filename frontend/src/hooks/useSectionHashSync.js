import { useEffect } from "react";

import { getRoute, navigateTo } from "../utils/navigation";

const SECTION_PATHS = {
  scanner: "/scanner",
  opportunities: "/opportunities",
  guides: "/guides",
};

const HOME_PATHS = new Set(["/", "/scanner"]);
const HEADER_OFFSET = 96;
const LINE_BUFFER = 70;
const SECTION_IDS = ["scanner", "opportunities", "guides"];

let programmaticScrollUntil = 0;

function sectionFromRoute(route) {
  if (route === SECTION_PATHS.opportunities) return "opportunities";
  if (route === SECTION_PATHS.guides) return "guides";
  if (HOME_PATHS.has(route)) return "scanner";
  return null;
}

function visibleArea(rect) {
  const top = Math.max(rect.top, HEADER_OFFSET);
  const bottom = Math.min(rect.bottom, window.innerHeight);
  return Math.max(0, bottom - top);
}

function resolveSection() {
  const elements = SECTION_IDS.map((id) => document.getElementById(id)).filter(Boolean);
  if (!elements.length) return "scanner";

  const scrollLine = window.scrollY + HEADER_OFFSET + LINE_BUFFER;
  let current = "scanner";

  for (const el of elements) {
    if (scrollLine >= el.offsetTop) current = el.id;
  }

  const areas = Object.fromEntries(
    SECTION_IDS.map((id) => {
      const el = document.getElementById(id);
      return [id, el ? visibleArea(el.getBoundingClientRect()) : 0];
    }),
  );

  const ranked = [...SECTION_IDS].sort((a, b) => areas[b] - areas[a]);
  if (areas[ranked[0]] > 0 && areas[ranked[0]] >= areas[ranked[1]] + 8) {
    return ranked[0];
  }

  return current;
}

function scrollToSection(section, behavior = "smooth") {
  const el = document.getElementById(section);
  if (!el) return;
  programmaticScrollUntil = Date.now() + 1000;
  el.scrollIntoView({ behavior, block: "start" });
}

export function useSectionHashSync(enabled) {
  useEffect(() => {
    if (!enabled) return;

    const elements = SECTION_IDS.map((id) => document.getElementById(id)).filter(Boolean);
    if (elements.length < 2) return;

    const visibility = Object.fromEntries(SECTION_IDS.map((id) => [id, 0]));
    let frame = 0;

    const syncHash = () => {
      frame = 0;
      if (Date.now() < programmaticScrollUntil) return;

      const currentRoute = getRoute();
      if (currentRoute === "/login" || currentRoute === "/register") return;

      let section = resolveSection();
      const ranked = [...SECTION_IDS].sort((a, b) => visibility[b] - visibility[a]);
      if (visibility[ranked[0]] > visibility[ranked[1]] + 0.08) {
        section = ranked[0];
      }

      const nextPath = SECTION_PATHS[section];
      const currentPath = HOME_PATHS.has(currentRoute) ? SECTION_PATHS.scanner : currentRoute;

      if (currentPath !== nextPath) {
        navigateTo(nextPath, { replace: true });
      }
    };

    const scheduleSync = () => {
      if (frame) return;
      frame = requestAnimationFrame(syncHash);
    };

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (SECTION_IDS.includes(entry.target.id)) {
            visibility[entry.target.id] = entry.intersectionRatio;
          }
        });
        scheduleSync();
      },
      {
        root: null,
        rootMargin: `-${HEADER_OFFSET}px 0px -40% 0px`,
        threshold: [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
      },
    );

    elements.forEach((el) => observer.observe(el));

    window.addEventListener("scroll", scheduleSync, { passive: true });
    window.addEventListener("resize", scheduleSync, { passive: true });
    syncHash();

    return () => {
      observer.disconnect();
      window.removeEventListener("scroll", scheduleSync);
      window.removeEventListener("resize", scheduleSync);
      if (frame) cancelAnimationFrame(frame);
    };
  }, [enabled]);

  useEffect(() => {
    if (!enabled) return;

    const section = sectionFromRoute(getRoute());
    if (!section || section === "scanner") return;

    const timer = window.setTimeout(() => {
      scrollToSection(section, "auto");
    }, 0);

    return () => window.clearTimeout(timer);
  }, [enabled]);
}

export function goToSection(section) {
  const path = SECTION_PATHS[section];
  if (!path) return;
  programmaticScrollUntil = Date.now() + 1000;
  navigateTo(path, { replace: false });
  scrollToSection(section);
}
