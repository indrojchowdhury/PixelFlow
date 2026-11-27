import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";

// mode="private": only logged-in users. mode="public": only guests (login, register).
export default function ProtectedRoute({ mode = "private" }) {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  if (mode === "public") {
    return isAuthenticated ? <Navigate to="/dashboard" replace /> : <Outlet />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }
  return <Outlet />;
}