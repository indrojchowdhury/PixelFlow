import { Outlet } from "react-router-dom";

import SiteFooter from "../components/SiteFooter";
import SiteHeader from "../components/SiteHeader";

export default function AppLayout() {
  return (
    <div className="flex min-h-screen flex-col bg-slate-50">
      <SiteHeader />
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8">
        <Outlet />
      </main>
      <SiteFooter />
    </div>
  );
}