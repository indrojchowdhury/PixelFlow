export default function Spinner({ label = "Loading" }) {
  return (
    <div className="flex min-h-40 items-center justify-center" role="status" aria-label={label}>
      <span className="h-8 w-8 animate-spin rounded-full border-4 border-sky-100 border-t-sky-500" />
      <span className="sr-only">{label}...</span>
    </div>
  );
}