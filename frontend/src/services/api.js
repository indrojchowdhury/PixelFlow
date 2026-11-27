import axios from "axios";

import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  setTokens,
} from "./tokenStorage";

const baseURL = import.meta.env.VITE_API_URL;

const api = axios.create({ baseURL });

// Endpoints where a 401 means "wrong credentials", not "expired token"
const NO_REFRESH_URLS = ["/auth/login/", "/auth/register/", "/auth/refresh/"];

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// A single shared promise, so many parallel 401s trigger only one refresh call.
// This matters because the backend rotates and blacklists refresh tokens:
// a second refresh with the old token would fail.
let refreshPromise = null;

function refreshAccessToken() {
  if (!refreshPromise) {
    const refresh = getRefreshToken();
    if (!refresh) {
      return Promise.reject(new Error("No refresh token"));
    }

    // Plain axios (not `api`), so this call does not pass through the interceptors
    refreshPromise = axios
      .post(`${baseURL}/auth/refresh/`, { refresh })
      .then(({ data }) => {
        setTokens({ access: data.access, refresh: data.refresh ?? refresh });
        return data.access;
      })
      .finally(() => {
        refreshPromise = null;
      });
  }
  return refreshPromise;
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    const status = error.response?.status;
    const skipRefresh = NO_REFRESH_URLS.some((url) => original?.url?.startsWith(url));

    if (status === 401 && original && !original._retry && !skipRefresh) {
      original._retry = true;
      try {
        const access = await refreshAccessToken();
        original.headers.Authorization = `Bearer ${access}`;
        return api(original);
      } catch {
        // Refresh failed: the session is over
        clearTokens();
        window.dispatchEvent(new Event("auth:logout"));
        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  }
);

export default api;