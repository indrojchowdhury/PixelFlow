export default function ProgressBar({ value }) {
  const safe = Math.max(0, Math.min(100, value));
  return (
    <div className="h-3 w-full overflow-hidden rounded-full bg-slate-200">
      <div
        className="h-full rounded-full bg-sky-400 transition-all duration-500"
        style={{ width: `${safe}%` }}
      />
    </div>
  );
}