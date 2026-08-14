export function getRoute() {
  const hash = window.location.hash.replace(/^#/, "") || "/";
  return hash.startsWith("/") ? hash : `/${hash}`;
}

export function navigateTo(path, { replace = false } = {}) {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  const hash = `#${normalized}`;

  if (replace) {
    const url = `${window.location.pathname}${window.location.search}${hash}`;
    history.replaceState(null, "", url);
    window.dispatchEvent(new HashChangeEvent("hashchange"));
    return;
  }

  if (window.location.hash !== hash) {
    window.location.hash = normalized;
  }
}
