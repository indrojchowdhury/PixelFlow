import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import EmptyState from "../components/EmptyState";
import Spinner from "../components/Spinner";
import StatusBadge from "../components/StatusBadge";
import { useToast } from "../hooks/useToast";
import { deleteImage, listImages } from "../services/imageService";
import { getErrorMessage } from "../utils/errors";
import { formatBytes } from "../utils/format";

const VERSION_ORDER = ["thumbnail", "medium", "large"];

function orderedVersions(image) {
  return VERSION_ORDER.map((type) =>
    image.versions.find((v) => v.version_type === type)
  ).filter(Boolean);
}

export default function Gallery() {
  const { id } = useParams();
  const toast = useToast();
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState(null);

  const load = useCallback(async () => {
    try {
      setImages(await listImages(id));
      setError("");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load();
  }, [load]);

  // Keep refreshing while any image is still being processed
  const inProgress = images.some((i) => i.status === "pending" || i.status === "processing");
  useEffect(() => {
    if (!inProgress) return undefined;
    const timer = setInterval(load, 3000);
    return () => clearInterval(timer);
  }, [inProgress, load]);

  // Close the preview with the Escape key
  useEffect(() => {
    if (!selected) return undefined;
    const onKey = (event) => {
      if (event.key === "Escape") setSelected(null);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [selected]);

  const handleDelete = async (image) => {
    if (!window.confirm(`Delete "${image.original_name}"?`)) return;
    try {
      await deleteImage(image.id);
      toast.success("Image deleted");
      setSelected(null);
      await load();
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  };

  const selectedVersions = selected ? orderedVersions(selected) : [];
  const preview = selectedVersions[selectedVersions.length - 1];

  return (
    <div>
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <Link to="/albums" className="text-sm text-sky-700 hover:underline">
            ← Albums
          </Link>
          <h1 className="text-2xl font-bold text-slate-800">Gallery</h1>
        </div>
        <Link
          to={`/upload?album=${id}`}
          className="rounded-lg bg-sky-200 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-sky-300"
        >
          Upload images
        </Link>
      </div>

      {inProgress && (
        <p className="mt-4 rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-800">
          Some images are still being processed. This page updates automatically.
        </p>
      )}
      {error && (
        <p className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>
      )}

      {loading ? (
        <Spinner />
      ) : images.length === 0 ? (
        <EmptyState title="No images in this album yet" text="Upload some to get started.">
          <Link
            to={`/upload?album=${id}`}
            className="rounded-lg bg-sky-200 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-sky-300"
          >
            Upload images
          </Link>
        </EmptyState>
      ) : (
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {images.map((image) => {
            const versions = orderedVersions(image);
            const thumb = versions[0];
            return (
              <div
                key={image.id}
                className="overflow-hidden rounded-2xl bg-white shadow transition hover:shadow-lg"
              >
                <button
                  onClick={() => thumb && setSelected(image)}
                  className="flex h-44 w-full items-center justify-center bg-slate-100"
                  disabled={!thumb}
                >
                  {thumb ? (
                    <img
                      src={thumb.file}
                      alt={image.original_name}
                      className="h-full w-full object-cover"
                    />
                  ) : (
                    <span className="text-sm text-slate-400">
                      {image.status === "failed" ? "Failed" : "Processing..."}
                    </span>
                  )}
                </button>
                <div className="p-3">
                  <div className="flex items-center justify-between gap-2">
                    <p className="truncate text-sm font-medium text-slate-800">
                      {image.original_name}
                    </p>
                    <StatusBadge status={image.status} />
                  </div>
                  <p className="mt-1 text-xs text-slate-400">
                    {image.width}x{image.height}, {formatBytes(image.original_size)}
                  </p>
                  {image.status === "failed" && (
                    <p className="mt-1 text-xs text-red-600">{image.error_message}</p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {selected && preview && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
          onClick={() => setSelected(null)}
        >
          <div
            className="max-h-full w-full max-w-4xl overflow-auto rounded-2xl bg-white p-4"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="font-semibold text-slate-800">{selected.original_name}</p>
                <p className="text-xs text-slate-400">
                  Original {selected.width}x{selected.height}, {formatBytes(selected.original_size)}
                </p>
              </div>
              <button
                onClick={() => setSelected(null)}
                className="text-slate-400 hover:text-slate-700"
              >
                ✕
              </button>
            </div>

            <img
              src={preview.file}
              alt={selected.original_name}
              className="mx-auto mt-3 max-h-[60vh] rounded-lg object-contain"
            />

            <div className="mt-4 flex flex-wrap items-center gap-2">
              {selectedVersions.map((version) => (
                <a
                  key={version.id}
                  href={version.file}
                  target="_blank"
                  rel="noreferrer"
                  download
                  className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50"
                >
                  {version.version_type} · {version.width}x{version.height} ·{" "}
                  {formatBytes(version.file_size)}
                </a>
              ))}
              <button
                onClick={() => handleDelete(selected)}
                className="ml-auto rounded-lg border border-red-200 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}