import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { AuthProvider, useAuth } from "./context/AuthContext";
import { ScanProvider, useScan } from "./context/ScanContext";
import AuthPage from "./components/AuthPage";
import LandingHeader from "./components/LandingHeader";
import LandingHero from "./components/LandingHero";
import GuidesArticles from "./components/GuidesArticles";
import OpportunitiesGrid from "./components/OpportunitiesGrid";
import ScanResultDemo from "./components/ScanResultDemo";
import ScannerHero from "./components/ScannerHero";
import SiteHeader from "./components/SiteHeader";
import SiteFooter from "./components/SiteFooter";
import { useSectionHashSync } from "./hooks/useSectionHashSync";
import { getRoute, navigateTo } from "./utils/navigation";

function AppContent() {
  const { t } = useTranslation();
  const [route, setRoute] = useState(getRoute);
  const { user, loading } = useAuth();
  const { clearScan } = useScan();

  useEffect(() => {
    const onHashChange = () => setRoute(getRoute());
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  const isAuthRoute = route === "/login" || route === "/register";
  const isGuidesRoute = route === "/guides";
  const isPlatformRoute =
    route === "/scanner" || route === "/opportunities" || isGuidesRoute;

  useSectionHashSync(Boolean(user) && !isAuthRoute && !isGuidesRoute);

  useEffect(() => {
    if (!loading && !user && isPlatformRoute) {
      navigateTo("/", { replace: true });
    }
  }, [isPlatformRoute, loading, user]);

  useEffect(() => {
    if (isGuidesRoute) {
      window.scrollTo({ top: 0, behavior: "auto" });
    }
  }, [isGuidesRoute]);

  const goPlatform = () => {
    clearScan();
    navigateTo("/scanner", { replace: true });
    window.scrollTo({ top: 0, behavior: "auto" });
    window.setTimeout(() => {
      document.getElementById("scan-form")?.scrollIntoView({ behavior: "auto", block: "start" });
    }, 50);
  };
  const goLanding = () => {
    navigateTo("/", { replace: true });
    window.scrollTo({ top: 0, behavior: "auto" });
  };
  const goLogin = () => navigateTo("/login", { replace: false });
  const goRegister = () => navigateTo("/register", { replace: false });

  if (loading) {
    return (
      <div
        className="flex min-h-screen flex-col items-center justify-center gap-4 bg-paper"
        aria-busy="true"
      >
        <span className="h-9 w-9 animate-spin rounded-full border-2 border-ink/20 border-t-ink" />
        <p className="text-sm text-ink-muted">{t("common.loading")}</p>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen">
      <div className="grid-bg" aria-hidden="true" />
      {isAuthRoute ? (
        <AuthPage
          onBack={goLanding}
          onSuccess={goPlatform}
          initialMode={route === "/register" ? "register" : "login"}
        />
      ) : user ? (
        <>
          <SiteHeader onLoginClick={goLogin} />
          <main className="relative z-0">
            {isGuidesRoute ? (
              <section className="section">
                <GuidesArticles />
              </section>
            ) : (
              <>
                <section className="section">
                  <ScannerHero />
                </section>
                <section className="section section--muted">
                  <OpportunitiesGrid />
                </section>
              </>
            )}
          </main>
          <SiteFooter />
        </>
      ) : (
        <>
          <LandingHeader onLogin={goLogin} onRegister={goRegister} />
          <main>
            <LandingHero onLogin={goLogin} onRegister={goRegister} />
            <ScanResultDemo />
          </main>
          <SiteFooter />
        </>
      )}
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <ScanProvider>
        <AppContent />
      </ScanProvider>
    </AuthProvider>
  );
}
