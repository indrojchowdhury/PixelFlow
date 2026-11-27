import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import EmptyState from "../components/EmptyState";
import Spinner from "../components/Spinner";
import StatCard from "../components/StatCard";
import StatusBadge from "../components/StatusBadge";
import { useToast } from "../hooks/useToast";
import { downloadBatchZip } from "../services/batchService";
import { getDashboard } from "../services/dashboardService";
import { getErrorMessage } from "../utils/errors";
import { formatBytes, formatDate } from "../utils/format";

function percent(part, total) {
  return total > 0 ? (part / total) * 100 : 0;
}

export default function Dashboard() {
  const toast = useToast();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getDashboard()
      .then(setData)
      .catch((err) => setError(getErrorMessage(err)));
  }, []);

  if (error) {
    return <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>;
  }
  if (!data) {
    return <Spinner />;
  }

  if (data.total_images === 0) {
    return (
      <div>
        <h1 className="text-xl font-bold text-slate-800">Dashboard</h1>
        <EmptyState
          title="No images yet"
          text="Create an album, then upload your first images."
        >
          <div className="flex justify-center gap-3">
            <Link
              to="/albums"
              className="rounded-lg border border-slate-300 px-4 py-2 text-sm hover:bg-slate-50"
            >
              Create album
            </Link>
            <Link
              to="/upload"
              className="rounded-lg bg-sky-200 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-sky-300"
            >
              Upload images
            </Link>
          </div>
        </EmptyState>
      </div>
    );
  }

  const total = data.total_images;
  const savedPercent = Math.round(percent(data.saved_bytes, data.original_bytes));
  const processedWidth = percent(data.processed_bytes, data.original_bytes);
  const average =
    data.average_processing_seconds !== null ? `${data.average_processing_seconds}s` : "-";

  const handleDownload = (id) =>
    downloadBatchZip(id)
      .then(() => toast.success("Download started"))
      .catch((err) => toast.error(getErrorMessage(err)));

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-xl font-bold text-slate-800">Dashboard</h1>
        <Link
          to="/upload"
          className="rounded-lg bg-sky-200 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-sky-300"
        >
          Upload images
        </Link>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Albums" value={data.total_albums} icon="📁" />
        <StatCard label="Total images" value={total} icon="🖼️" />
        <StatCard
          label="Processed"
          value={data.completed_images}
          icon="✅"
          accent="bg-sky-50 text-sky-700"
        />
        <StatCard
          label="Failed"
          value={data.failed_images}
          icon="⚠️"
          accent="bg-red-50 text-red-600"
        />
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <div className="rounded-2xl bg-white p-5 shadow">
          <h2 className="font-semibold text-slate-800">Image status</h2>
          <div className="mt-4 flex h-4 overflow-hidden rounded-full bg-slate-100">
            <div
              className="bg-sky-400"
              style={{ width: `${percent(data.completed_images, total)}%` }}
            />
            <div
              className="bg-amber-400"
              style={{ width: `${percent(data.in_progress_images, total)}%` }}
            />
            <div
              className="bg-red-500"
              style={{ width: `${percent(data.failed_images, total)}%` }}
            />
          </div>
          <div className="mt-3 flex flex-wrap gap-4 text-sm text-slate-600">
            <span>🟢 Completed {data.completed_images}</span>
            <span>🟡 In progress {data.in_progress_images}</span>
            <span>🔴 Failed {data.failed_images}</span>
          </div>
          <p className="mt-4 text-sm text-slate-500">
            Average processing time: <strong className="text-slate-700">{average}</strong>
          </p>
        </div>

        <div className="rounded-2xl bg-white p-5 shadow">
          <h2 className="font-semibold text-slate-800">Storage saved</h2>
          <p className="mt-2 text-2xl font-bold text-sky-700">
            {formatBytes(data.saved_bytes)}{" "}
            <span className="text-sm font-medium text-slate-400">({savedPercent}%)</span>
          </p>
          <div className="mt-4 space-y-2 text-xs text-slate-500">
            <div>
              <div className="mb-1 flex justify-between">
                <span>Original</span>
                <span>{formatBytes(data.original_bytes)}</span>
              </div>
              <div className="h-3 rounded-full bg-slate-400" />
            </div>
            <div>
              <div className="mb-1 flex justify-between">
                <span>Optimized (large WebP)</span>
                <span>{formatBytes(data.processed_bytes)}</span>
              </div>
              <div className="h-3 rounded-full bg-slate-100">
                <div
                  className="h-3 rounded-full bg-sky-400"
                  style={{ width: `${Math.min(100, processedWidth)}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <h2 className="mt-8 text-base font-semibold text-slate-800">Recent batches</h2>
      <div className="mt-3 overflow-x-auto rounded-2xl bg-white shadow">
        <table className="w-full min-w-[36rem] text-left text-sm">
          <thead className="border-b border-slate-200 text-slate-500">
            <tr>
              <th className="px-4 py-3">Batch</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Images</th>
              <th className="px-4 py-3">Created</th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            {data.recent_batches.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-slate-400">
                  No batches yet.
                </td>
              </tr>
            )}
            {data.recent_batches.map((batch) => (
              <tr key={batch.id} className="border-b border-slate-100 last:border-0">
                <td className="px-4 py-3">#{batch.id}</td>
                <td className="px-4 py-3">
                  <StatusBadge status={batch.status} />
                </td>
                <td className="px-4 py-3">
                  {batch.processed_images}/{batch.total_images}
                  {batch.failed_images > 0 && (
                    <span className="text-red-600"> ({batch.failed_images} failed)</span>
                  )}
                </td>
                <td className="px-4 py-3">{formatDate(batch.created_at)}</td>
                <td className="px-4 py-3 text-right">
                  {batch.download_available && (
                    <button
                      onClick={() => handleDownload(batch.id)}
                      className="text-sky-700 hover:underline"
                    >
                      Download ZIP
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}