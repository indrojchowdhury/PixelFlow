const STYLES = {
  pending: "bg-slate-100 text-slate-700",
  processing: "bg-amber-100 text-amber-700",
  completed: "bg-sky-100 text-sky-700",
  failed: "bg-red-100 text-red-700",
};

export default function StatusBadge({ status }) {
  return (
    <span
      className={`rounded-full px-2 py-0.5 text-xs font-medium ${
        STYLES[status] || STYLES.pending
      }`}
    >
      {status}
    </span>
  );
}