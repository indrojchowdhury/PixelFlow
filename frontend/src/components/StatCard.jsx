export default function StatCard({ label, value, icon, accent = "bg-sky-100 text-sky-700" }) {
  return (
    <div className="flex items-center gap-4 rounded-2xl bg-white p-5 shadow">
      {icon && (
        <div className={`flex h-12 w-12 items-center justify-center rounded-xl text-xl ${accent}`}>
          {icon}
        </div>
      )}
      <div>
        <p className="text-sm text-slate-500">{label}</p>
        <p className="text-xl font-bold text-slate-800">{value}</p>
      </div>
    </div>
  );
}