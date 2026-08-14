import { createContext, useCallback, useContext, useMemo, useState } from "react";

const ScanContext = createContext(null);

export function ScanProvider({ children }) {
  const [detectedRole, setDetectedRole] = useState(null);
  const [lastScan, setLastScan] = useState(null);

  const applyScanResult = useCallback((result) => {
    if (!result) return;
    setLastScan(result);
    const role = result?.metadata?.detected_role || null;
    if (role) {
      setDetectedRole(role);
      window.setTimeout(() => {
        const el = document.getElementById("opportunities");
        if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 100);
    }
  }, []);

  const clearRole = useCallback(() => setDetectedRole(null), []);

  const value = useMemo(
    () => ({ detectedRole, lastScan, applyScanResult, clearRole, setDetectedRole }),
    [detectedRole, lastScan, applyScanResult, clearRole],
  );

  return <ScanContext.Provider value={value}>{children}</ScanContext.Provider>;
}

export function useScan() {
  const ctx = useContext(ScanContext);
  if (!ctx) {
    throw new Error("useScan must be used within ScanProvider");
  }
  return ctx;
}
