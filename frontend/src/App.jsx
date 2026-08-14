import { useEffect, useState } from "react";

import { AuthProvider, useAuth } from "./context/AuthContext";
import { ScanProvider } from "./context/ScanContext";
import AuthPage from "./components/AuthPage";
import LandingHeader from "./components/LandingHeader";
import LandingHero from "./components/LandingHero";
import OpportunitiesGrid from "./components/OpportunitiesGrid";
import ScanResultDemo from "./components/ScanResultDemo";
import ScannerHero from "./components/ScannerHero";
import SiteHeader from "./components/SiteHeader";
import SiteFooter from "./components/SiteFooter";
import { useSectionHashSync } from "./hooks/useSectionHashSync";
import { getRoute, navigateTo } from "./utils/navigation";

function AppContent() {
  const [route, setRoute] = useState(getRoute);
  const { user, loading } = useAuth();

  useEffect(() => {
    const onHashChange = () => setRoute(getRoute());
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  const isAuthRoute = route === "/login" || route === "/register";
  const isPlatformRoute = route === "/scanner" || route === "/opportunities";

  useSectionHashSync(Boolean(user) && !isAuthRoute);

  useEffect(() => {
    if (!loading && !user && isPlatformRoute) {
      navigateTo("/", { replace: true });
    }
  }, [isPlatformRoute, loading, user]);

  const goPlatform = () => {
    navigateTo("/scanner", { replace: true });
    window.scrollTo({ top: 0, behavior: "auto" });
  };
  const goLanding = () => {
    navigateTo("/", { replace: true });
    window.scrollTo({ top: 0, behavior: "auto" });
  };
  const goLogin = () => navigateTo("/login", { replace: false });
  const goRegister = () => navigateTo("/register", { replace: false });

  if (loading) {
    return <div className="min-h-screen bg-white" aria-busy="true" />;
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
                <section className="section">
                  <ScannerHero />
                </section>
                <section className="section section--muted">
                  <OpportunitiesGrid />
                </section>
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
