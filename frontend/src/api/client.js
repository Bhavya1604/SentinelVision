/**
 * API client for SentinelVision backend.
 * Uses relative /api so Vite proxy forwards to backend.
 */

const API_BASE = "";

export async function analyzeImage(file, imageId = null) {
  const formData = new FormData();
  formData.append("file", file);
  if (imageId != null) {
    formData.append("image_id", imageId);
  }
  const res = await fetch(`${API_BASE}/api/analyze-image`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export async function health() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error("Health check failed");
  return res.json();
}
