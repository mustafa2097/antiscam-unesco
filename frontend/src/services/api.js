const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

export async function apiFetch(path, options = {}) {
  const headers = new Headers(options.headers ?? {});
  if (options.body && !(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  return fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    credentials: "include",
    cache: "no-store",
  });
}

export async function parseJsonSafe(response) {
  const text = await response.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

export async function fetchOpportunities({
  role = "",
  governorate = "all",
  category = null,
  sub = null,
} = {}) {
  const params = new URLSearchParams();
  if (role.trim()) params.set("role", role.trim());
  if (governorate) params.set("governorate", governorate);
  if (category) params.set("category", category);
  if (sub) params.set("sub", sub);

  const query = params.toString();
  const path = query ? `/api/opportunities?${query}` : "/api/opportunities";
  const response = await apiFetch(path, { method: "GET" });
  const data = await parseJsonSafe(response);
  if (!response.ok) {
    throw new Error(data?.detail ?? "opportunities_fetch_failed");
  }
  return Array.isArray(data) ? data : [];
}
