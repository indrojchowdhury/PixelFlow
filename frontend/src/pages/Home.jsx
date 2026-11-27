import { Link } from "react-router-dom";

import SiteFooter from "../components/SiteFooter";
import SiteHeader from "../components/SiteHeader";
import { useAuth } from "../hooks/useAuth";

const FEATURES = [
  {
    number: "01",
    title: "Upload in batches",
    text: "Add multiple images at once and keep every upload organized in albums.",
  },
  {
    number: "02",
    title: "Optimize automatically",
    text: "Let background processing create optimized WebP versions while you keep working.",
  },
  {
    number: "03",
    title: "Download together",
    text: "Get your processed images in one convenient ZIP when they’re ready.",
  },
];

export default function Home() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen overflow-hidden bg-white text-slate-900">
      <SiteHeader />

      <main>
        <section className="relative">
          <div className="pointer-events-none absolute -right-36 -top-32 h-[34rem] w-[34rem] rounded-full bg-sky-100/70 blur-3xl" />
          <div className="relative mx-auto grid max-w-7xl items-center gap-6 px-4 pb-6 pt-5 sm:gap-8 sm:px-6 sm:py-6 md:min-h-[23rem] md:grid-cols-[1.05fr_0.95fr] lg:gap-10 lg:px-8">
            <div>
              <p className="inline-flex items-center gap-2 rounded-full border border-sky-100 bg-sky-50 px-3 py-1 text-xs font-medium text-sky-700">
                <span className="h-2 w-2 rounded-full bg-orange-400" />
                A simpler image workflow
              </p>
              <h1 className="mt-4 max-w-2xl text-3xl font-bold leading-tight tracking-tight text-slate-950 sm:text-4xl lg:text-4xl">
                Your images,
                <span className="block text-sky-700">ready for anything.</span>
              </h1>
              <p className="mt-4 max-w-xl text-sm leading-6 text-slate-600 sm:text-base sm:leading-7">
                Upload, organize, and optimize your photos in one place. PixelFlow handles
                the processing in the background, so you can focus on what comes next.
              </p>
              <div className="mt-6 flex flex-wrap items-center gap-3">
                <Link
                  to={isAuthenticated ? "/dashboard" : "/register"}
                  className="rounded-xl bg-sky-200 px-4 py-3 text-xs font-semibold text-slate-950 shadow-lg shadow-sky-700/15 transition hover:-translate-y-0.5 hover:bg-sky-300 sm:text-sm"
                >
                  {isAuthenticated ? "Open dashboard" : "Create account"}
                </Link>
                {!isAuthenticated && (
                  <Link
                    to="/login"
                    className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-xs font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50 sm:text-sm"
                  >
                    Sign in
                  </Link>
                )}
              </div>
              <p className="mt-3 text-xs text-slate-500">
                Simple to use. Built for your everyday image workflow.
              </p>
            </div>

            <div className="relative mx-auto hidden w-full max-w-md md:block">
              <div className="absolute -inset-5 rounded-[2rem] bg-sky-100/50 blur-xl" />
              <div className="relative rounded-[1.5rem] border border-slate-200/80 bg-white p-4 shadow-xl shadow-sky-900/10 sm:p-5">
                <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                  <div>
                    <p className="text-xs font-semibold text-slate-900">Your workspace</p>
                    <p className="mt-1 text-[11px] text-slate-500">A clear view of every batch</p>
                  </div>
                  <span className="rounded-full bg-sky-50 px-2.5 py-1 text-[10px] font-semibold text-sky-700">
                    All systems ready
                  </span>
                </div>

                <div className="mt-3 grid grid-cols-2 gap-2">
                  <div className="rounded-xl bg-sky-50 p-3">
                    <p className="text-[11px] font-medium text-sky-700">Organized</p>
                    <p className="mt-2 text-xl font-bold text-slate-900">Albums</p>
                    <p className="mt-1 text-[11px] text-slate-500">Keep projects together</p>
                  </div>
                  <div className="rounded-xl bg-orange-50 p-3">
                    <p className="text-[11px] font-medium text-orange-700">Optimized</p>
                    <p className="mt-2 text-xl font-bold text-slate-900">WebP</p>
                    <p className="mt-1 text-[11px] text-slate-500">Efficient image formats</p>
                  </div>
                </div>

                <div className="mt-3 rounded-xl border border-slate-100 p-3">
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-semibold text-slate-800">Background processing</p>
                    <span className="text-[11px] font-medium text-sky-700">Automatic</span>
                  </div>
                  <div className="mt-3 space-y-2">
                    {[
                      ["Thumbnails", "Fast previews"],
                      ["Optimized images", "Smaller file sizes"],
                      ["Batch downloads", "One tidy ZIP"],
                    ].map(([title, detail], index) => (
                      <div key={title} className="flex items-center gap-3">
                        <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-slate-50 text-[10px] font-bold text-sky-700">
                          0{index + 1}
                        </span>
                        <div className="flex-1">
                          <p className="text-xs font-medium text-slate-800">{title}</p>
                          <p className="text-[11px] text-slate-500">{detail}</p>
                        </div>
                        <span className="h-2 w-2 rounded-full bg-orange-300" />
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              <div className="absolute -bottom-5 -left-5 hidden rounded-2xl border border-slate-100 bg-white px-4 py-3 shadow-lg sm:block">
                <p className="text-xs font-medium text-slate-500">Your workflow</p>
                <p className="mt-1 text-sm font-semibold text-slate-800">Upload. Optimize. Done.</p>
              </div>
            </div>
          </div>
        </section>

        <section id="features" className="border-y border-slate-100 bg-slate-50/70">
          <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
            <h2 className="sr-only">PixelFlow features</h2>
            <div className="grid gap-2 sm:grid-cols-3">
              {FEATURES.map((feature) => (
                <article key={feature.number} className="flex items-start gap-3 rounded-xl bg-white p-4 shadow-sm ring-1 ring-slate-200/70">
                  <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-sky-100 text-xs font-bold text-sky-700">
                    {feature.number}
                  </span>
                  <div>
                    <h3 className="text-sm font-semibold text-slate-900">{feature.title}</h3>
                    <p className="mt-1 text-sm leading-5 text-slate-600">{feature.text}</p>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}
