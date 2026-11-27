import SiteFooter from "./SiteFooter";
import SiteHeader from "./SiteHeader";

const FEATURES = [
  "Upload many images at once",
  "Processed in the background, no waiting",
  "Thumbnail, medium and large WebP versions",
  "Download everything as one ZIP",
];

export default function AuthShell({ title, subtitle, children }) {
  return (
    <div className="flex min-h-screen flex-col bg-slate-50">
      <SiteHeader />
      <main className="mx-auto grid w-full max-w-7xl flex-1 items-center gap-6 px-4 py-6 sm:px-6 lg:grid-cols-2 lg:px-8 lg:py-10">
        <section className="hidden min-h-[28rem] flex-col justify-between rounded-3xl bg-gradient-to-br from-sky-50 via-cyan-100 to-orange-100 p-8 text-slate-900 shadow-xl shadow-sky-900/10 lg:flex xl:p-10">
          <div className="flex items-center gap-3">
            <img
              src="/pixelflow-logo.png"
              alt="PixelFlow Digital Solutions"
              className="h-16 w-44 rounded-xl object-cover shadow-sm"
            />
          </div>
          <div>
            <h2 className="text-2xl font-bold leading-tight xl:text-3xl">
              Upload once.
              <br />
              Optimize in the background.
            </h2>
            <ul className="mt-8 space-y-4 text-slate-700">
              {FEATURES.map((feature) => (
                <li key={feature} className="flex items-center gap-3">
                  <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-white/70 text-sm font-semibold text-sky-700">
                    ✓
                  </span>
                  {feature}
                </li>
              ))}
            </ul>
          </div>
          <p className="text-sm font-medium text-slate-600">Your images, ready for anything.</p>
        </section>

        <section className="mx-auto w-full max-w-sm rounded-3xl border border-slate-200 bg-white p-5 shadow-xl shadow-slate-900/5 sm:p-6 lg:mx-0 lg:justify-self-center">
          <p className="text-sm font-semibold uppercase tracking-[0.16em] text-sky-700">
            Welcome to PixelFlow
          </p>
          <h1 className="mt-2 text-xl font-bold text-slate-800">{title}</h1>
          <p className="mt-1 text-sm text-slate-500">{subtitle}</p>
          <div className="mt-5">{children}</div>
        </section>
      </main>
      <SiteFooter />
    </div>
  );
}