const ACCESS_KEY = "pf_access";
const REFRESH_KEY = "pf_refresh";
const USERNAME_KEY = "pf_username";

export const getAccessToken = () => localStorage.getItem(ACCESS_KEY);
export const getRefreshToken = () => localStorage.getItem(REFRESH_KEY);
export const getUsername = () => localStorage.getItem(USERNAME_KEY);

export function setTokens({ access, refresh }) {
  if (access) localStorage.setItem(ACCESS_KEY, access);
  if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
}

export function setUsername(username) {
  localStorage.setItem(USERNAME_KEY, username);
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(USERNAME_KEY);
}