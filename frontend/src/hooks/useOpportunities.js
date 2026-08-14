import { useEffect, useRef, useState } from "react";

import { fetchOpportunities } from "../services/api";

export function useOpportunities({ role, governorate, category, sub }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const requestId = useRef(0);

  useEffect(() => {
    const id = ++requestId.current;
    setLoading(true);
    setError(null);

    fetchOpportunities({ role, governorate, category, sub })
      .then((data) => {
        if (id !== requestId.current) return;
        setItems(Array.isArray(data) ? data : []);
      })
      .catch((err) => {
        if (id !== requestId.current) return;
        setItems([]);
        setError(err instanceof Error ? err.message : "opportunities_fetch_failed");
      })
      .finally(() => {
        if (id === requestId.current) setLoading(false);
      });
  }, [role, governorate, category, sub]);

  return { items, loading, error };
}
