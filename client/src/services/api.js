const BASE = "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export const recommend = (profile, query = null, songs = null, mode = "balanced") =>
  request("/recommend", {
    method: "POST",
    body: JSON.stringify({ profile, query, songs, mode }),
  });

export const recommendRetry = (original_query, feedback, previous_prefs, mode = "balanced") =>
  request("/recommend/retry", {
    method: "POST",
    body: JSON.stringify({ original_query, feedback, previous_prefs, mode }),
  });

export const getRandomProfile = () => request("/random-profile");
