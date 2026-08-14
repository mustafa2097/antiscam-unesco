import { useEffect } from "react";

import { getRoute, navigateTo } from "../utils/navigation";

const SECTION_PATHS = {
  scanner: "/scanner",
  opportunities: "/opportunities",
};

const HOME_PATHS = new Set(["/", "/scanner"]);
const HEADER_OFFSET = 96;
const LINE_BUFFER = 70;
const SECTION_IDS = ["scanner", "opportunities"];

let programmaticScrollUntil = 0;

function sectionFromRoute(route) {
  if (route === SECTION_PATHS.opportunities) return "opportunities";
  if (HOME_PATHS.has(route)) return "scanner";
  return null;
}

function visibleArea(rect) {
  const top = Math.max(rect.top, HEADER_OFFSET);
  const bottom = Math.min(rect.bottom, window.innerHeight);
  return Math.max(0, bottom - top);
}

function resolveSection() {
  const scanner = document.getElementById("scanner");
  const opportunities = document.getElementById("opportunities");
  if (!scanner || !opportunities) return "scanner";

  // Keep the verification form first after login / page entry.
  if (window.scrollY < 140) {
    return "scanner";
  }

  const scrollLine = window.scrollY + HEADER_OFFSET + LINE_BUFFER;
  const oppStart = opportunities.offsetTop;

  if (scrollLine < oppStart) {
    return "scanner";
  }

  const scanArea = visibleArea(scanner.getBoundingClientRect());
  const oppArea = visibleArea(opportunities.getBoundingClientRect());
  const total = scanArea + oppArea;

  if (total > 0 && scanArea > 0 && oppArea > 0) {
    const oppShare = oppArea / total;
    if (oppShare >= 0.52) return "opportunities";
    if (oppShare <= 0.48) return "scanner";
  }

  return scrollLine >= oppStart ? "opportunities" : "scanner";
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

    const scanner = document.getElementById("scanner");
    const opportunities = document.getElementById("opportunities");
    if (!scanner || !opportunities) return;

    const visibility = { scanner: 0, opportunities: 0 };
    let frame = 0;

    const syncHash = () => {
      frame = 0;
      if (Date.now() < programmaticScrollUntil) return;

      const currentRoute = getRoute();
      if (
        currentRoute === "/login" ||
        currentRoute === "/register" ||
        currentRoute === "/guides"
      ) {
        return;
      }

      let section = resolveSection();

      const scanVis = visibility.scanner;
      const oppVis = visibility.opportunities;
      if (oppVis > scanVis + 0.08) {
        section = "opportunities";
      } else if (scanVis > oppVis + 0.08) {
        section = "scanner";
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
          if (entry.target.id === "scanner" || entry.target.id === "opportunities") {
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

    observer.observe(scanner);
    observer.observe(opportunities);

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

    const route = getRoute();
    const section = sectionFromRoute(route);

    // Fresh platform entry (login): always show scanner form, never jump to opportunities.
    if (!section || section === "scanner") {
      programmaticScrollUntil = Date.now() + 1800;
      navigateTo("/scanner", { replace: true });
      window.scrollTo({ top: 0, behavior: "auto" });
      const form = document.getElementById("scan-form");
      window.setTimeout(() => {
        form?.scrollIntoView({ behavior: "auto", block: "start" });
      }, 40);
      return undefined;
    }

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
