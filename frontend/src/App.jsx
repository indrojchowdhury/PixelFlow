import { Route, Routes } from "react-router-dom";

import ProtectedRoute from "./components/ProtectedRoute";
import SiteFooter from "./components/SiteFooter";
import SiteHeader from "./components/SiteHeader";
import AppLayout from "./layouts/AppLayout";
import Albums from "./pages/Albums";
import Dashboard from "./pages/Dashboard";
import Gallery from "./pages/Gallery";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Upload from "./pages/Upload";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />

      <Route element={<ProtectedRoute mode="public" />}>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Route>

      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/albums" element={<Albums />} />
          <Route path="/albums/:id" element={<Gallery />} />
          <Route path="/upload" element={<Upload />} />
        </Route>
      </Route>

      <Route
        path="*"
        element={
          <div className="flex min-h-screen flex-col bg-slate-50">
            <SiteHeader />
            <main className="flex flex-1 flex-col items-center justify-center px-4 py-16 text-center">
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-sky-700">
                PixelFlow
              </p>
              <h1 className="mt-4 text-3xl font-bold text-slate-900">Page not found</h1>
              <p className="mt-2 text-slate-600">The page you’re looking for doesn’t exist.</p>
              <a
                href="/"
                className="mt-6 rounded-lg bg-sky-200 px-5 py-3 text-sm font-semibold text-slate-950 hover:bg-sky-300"
              >
                Back to home
              </a>
            </main>
            <SiteFooter />
          </div>
        }
      />
    </Routes>
  );
}