/**
 * api.js
 * ------
 * Same job as in the vanilla JS version: attach the JWT automatically,
 * normalize errors. In React we just import these functions directly
 * instead of relying on a global `api` object.
 */

const API_BASE_URL = "http://localhost:8000";

function getToken() {
  return localStorage.getItem("jwt_token");
}

export function setSession(token, user) {
  localStorage.setItem("jwt_token", token);
  localStorage.setItem("user", JSON.stringify(user));
}

export function clearSession() {
  localStorage.removeItem("jwt_token");
  localStorage.removeItem("user");
}

export function getStoredUser() {
  const raw = localStorage.getItem("user");
  return raw ? JSON.parse(raw) : null;
}

async function request(path, { method = "GET", body = null, isFormData = false } = {}) {
  const headers = {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let fetchBody;
  if (body !== null) {
    if (isFormData) {
      fetchBody = body;
    } else {
      headers["Content-Type"] = "application/json";
      fetchBody = JSON.stringify(body);
    }
  }

  const response = await fetch(`${API_BASE_URL}${path}`, { method, headers, body: fetchBody });

  if (response.status === 401) {
    clearSession();
    window.location.href = "/login";
    throw new Error("Session expired. Please log in again.");
  }

  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json") ? await response.json() : null;

  if (!response.ok) {
    throw new Error(data?.detail || "Something went wrong. Please try again.");
  }
  return data;
}

export const api = {
  get: (path) => request(path, { method: "GET" }),
  post: (path, body) => request(path, { method: "POST", body }),
  postForm: (path, formData) => request(path, { method: "POST", body: formData, isFormData: true }),
  put: (path, body) => request(path, { method: "PUT", body }),
};