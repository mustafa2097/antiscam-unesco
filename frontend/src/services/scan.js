import { apiFetch, parseJsonSafe } from "./api";

async function scanRequest(path, { json, formData } = {}) {
  const headers = new Headers();
  let body;
  if (formData) {
    body = formData;
  } else if (json !== undefined) {
    headers.set("Content-Type", "application/json");
    body = JSON.stringify(json);
  }

  const response = await apiFetch(path, { method: "POST", headers, body });
  const data = await parseJsonSafe(response);
  if (!response.ok) {
    const detail = data?.detail ?? "scan_failed";
    throw new Error(typeof detail === "string" ? detail : "scan_failed");
  }
  return data;
}

export function scanText(content) {
  return scanRequest("/api/scan/text", { json: { content } });
}

export function scanImage(file) {
  const formData = new FormData();
  formData.append("file", file);
  return scanRequest("/api/scan/image", { formData });
}

export function scanLink(url) {
  return scanRequest("/api/scan/link", { json: { url } });
}
