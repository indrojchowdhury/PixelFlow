import { Link } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";

const PRIVATE_LINKS = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/albums", label: "Albums" },
  { to: "/upload", label: "Upload" },
];

export default function SiteFooter() {
  const { isAuthenticated } = useAuth();

  return (
    <footer className="border-t border-sky-100 bg-sky-50 text-slate-700">
      <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
        <div className="flex items-center justify-between gap-4">
          <Link to="/" className="inline-flex items-center">
            <img
              src="/pixelflow-logo.png"
              alt="PixelFlow Digital Solutions"
              className="h-10 w-28 rounded-lg object-cover sm:w-32"
            />
          </Link>
          <p className="hidden max-w-md text-xs leading-5 text-slate-600 md:block">
            Upload, organize, and optimize your images in one simple workspace.
          </p>
        </div>
        <nav aria-label="Footer navigation" className="flex flex-wrap gap-1">
          {isAuthenticated ? (
            PRIVATE_LINKS.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className="rounded-full px-2.5 py-1.5 text-xs transition hover:bg-white hover:text-sky-700 sm:px-3 sm:text-sm"
              >
                {link.label}
              </Link>
            ))
          ) : (
            <>
              <Link to="/login" className="rounded-full px-2.5 py-1.5 text-xs transition hover:bg-white hover:text-sky-700 sm:px-3 sm:text-sm">
                Sign in
              </Link>
              <Link to="/register" className="rounded-full px-2.5 py-1.5 text-xs transition hover:bg-white hover:text-sky-700 sm:px-3 sm:text-sm">
                Register
              </Link>
            </>
          )}
        </nav>
      </div>
      <div className="border-t border-sky-100">
        <div className="mx-auto flex max-w-7xl items-center px-4 py-2 text-[10px] text-slate-500 sm:px-6 lg:px-8">
          <span>© {new Date().getFullYear()} PixelFlow. All rights reserved.</span>
        </div>
      </div>
    </footer>
  );
}
