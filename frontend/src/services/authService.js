import api from "./api";
import {
  clearTokens,
  getRefreshToken,
  setTokens,
  setUsername,
} from "./tokenStorage";

export async function login(username, password) {
  const { data } = await api.post("/auth/login/", { username, password });
  setTokens({ access: data.access, refresh: data.refresh });
  setUsername(username);
}

export async function register({ username, email, password }) {
  await api.post("/auth/register/", { username, email, password });
  // Log the user in right after a successful registration
  await login(username, password);
}

export async function logout() {
  const refresh = getRefreshToken();
  try {
    if (refresh) {
      await api.post("/auth/logout/", { refresh });
    }
  } catch {
    // Even if the server call fails, the local session must end
  } finally {
    clearTokens();
  }
}