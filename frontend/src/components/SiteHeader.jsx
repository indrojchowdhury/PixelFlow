import { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";
import { useToast } from "../hooks/useToast";
import { getErrorMessage } from "../utils/errors";
import ThemeToggle from "./ThemeToggle";

const LINKS = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/albums", label: "Albums" },
  { to: "/upload", label: "Upload" },
];

const linkClass = ({ isActive }) =>
  `rounded-full px-4 py-2 text-sm font-medium transition ${
    isActive
      ? "bg-sky-100 text-slate-950 shadow-sm shadow-sky-950/10"
      : "text-slate-700 hover:bg-white hover:text-sky-700"
  }`;

export default function SiteHeader() {
  const { isAuthenticated, username, logout } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = async () => {
    try {
      await logout();
      setMenuOpen(false);
      navigate("/login", { replace: true });
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const closeMenu = () => setMenuOpen(false);

  return (
    <header className="sticky top-0 z-40 border-b border-sky-100 bg-white/90 text-slate-900 shadow-sm shadow-sky-950/5 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-3 px-4 py-3 sm:px-6 lg:px-8">
        <Link
          to="/"
          onClick={closeMenu}
          className="flex shrink-0 items-center gap-2.5"
          aria-label="PixelFlow home"
        >
          <img
            src="/pixelflow-logo.png"
            alt=""
            className="h-10 w-28 rounded-lg object-cover shadow-sm shadow-sky-900/10 sm:h-12 sm:w-36"
          />
        </Link>

        <div className="flex shrink-0 items-center gap-2 sm:gap-3">
          {isAuthenticated && (
            <nav
              aria-label="Main navigation"
              className="hidden items-center gap-1 rounded-full border border-sky-100 bg-sky-50 p-1 lg:flex"
            >
              {LINKS.map((link) => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  className={linkClass}
                >
                  {link.label}
                </NavLink>
              ))}
            </nav>
          )}
          {isAuthenticated && (
            <span className="hidden max-w-32 truncate text-sm text-slate-600 xl:block">
              {username}
            </span>
          )}
          <ThemeToggle />
          <div className="hidden items-center gap-2 sm:flex">
            {isAuthenticated ? (
              <button
                type="button"
                onClick={handleLogout}
                className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-sky-300 hover:bg-sky-50"
              >
                Log out
              </button>
            ) : (
              <>
                <Link
                  to="/login"
                  className="rounded-full px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-sky-50 hover:text-sky-700"
                >
                  Sign in
                </Link>
                <Link
                  to="/register"
                  className="rounded-full bg-sky-200 px-4 py-2 text-sm font-bold text-slate-950 transition hover:bg-sky-300"
                >
                  Get started
                </Link>
              </>
            )}
          </div>
          <button
            type="button"
            onClick={() => setMenuOpen((open) => !open)}
            className="flex h-10 w-10 items-center justify-center rounded-lg border border-sky-200 text-slate-700 transition hover:bg-sky-50 lg:hidden"
            aria-label={menuOpen ? "Close navigation menu" : "Open navigation menu"}
            aria-expanded={menuOpen}
          >
            {menuOpen ? (
              <svg aria-hidden="true" className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" d="m6 6 12 12M18 6 6 18" />
              </svg>
            ) : (
              <svg aria-hidden="true" className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" d="M4 7h16M4 12h16M4 17h16" />
              </svg>
            )}
          </button>
        </div>
      </div>

      {menuOpen && (
        <nav
          aria-label="Mobile navigation"
          className="border-t border-sky-100 bg-white px-4 py-4 sm:px-6 lg:hidden"
        >
          <div className="mx-auto flex max-w-7xl flex-col gap-1">
            {isAuthenticated &&
              LINKS.map((link) => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  onClick={closeMenu}
                  className={linkClass}
                >
                  {link.label}
                </NavLink>
              ))}
            <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-sky-100 pt-4 sm:hidden">
              {isAuthenticated ? (
                <>
                  <span className="mr-auto max-w-40 truncate px-3 text-sm text-slate-600">
                    {username}
                  </span>
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700"
                  >
                    Log out
                  </button>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    onClick={closeMenu}
                    className="rounded-full px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-sky-50"
                  >
                    Sign in
                  </Link>
                  <Link
                    to="/register"
                    onClick={closeMenu}
                    className="rounded-full bg-sky-200 px-4 py-2 text-sm font-bold text-slate-950 hover:bg-sky-300"
                  >
                    Get started
                  </Link>
                </>
              )}
            </div>
          </div>
        </nav>
      )}
    </header>
  );
}
