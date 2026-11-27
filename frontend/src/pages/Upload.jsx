import { useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import ProgressBar from "../components/ProgressBar";
import { listAlbums } from "../services/albumService";
import { downloadBatchZip, getBatch } from "../services/batchService";
import { uploadImages } from "../services/imageService";
import { getErrorMessage } from "../utils/errors";
import { formatBytes } from "../utils/format";

const MAX_FILES = 20;
const MAX_SIZE = 10 * 1024 * 1024;
const ALLOWED = ["image/jpeg", "image/png", "image/webp"];
const POLL_MS = 2500;

export default function Upload() {
  const [searchParams] = useSearchParams();
  const [albums, setAlbums] = useState([]);
  const [albumId, setAlbumId] = useState(searchParams.get("album") || "");
  const [files, setFiles] = useState([]);
  const [problems, setProblems] = useState([]);
  const [dragging, setDragging] = useState(false);
  const [uploadPercent, setUploadPercent] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [rejected, setRejected] = useState([]);
  const [batchId, setBatchId] = useState(null);
  const [batch, setBatch] = useState(null);
  const [error, setError] = useState("");
  const inputRef = useRef(null);

  useEffect(() => {
    listAlbums()
      .then(setAlbums)
      .catch((err) => setError(getErrorMessage(err)));
  }, []);

  // Poll the batch until it reaches a final state
  useEffect(() => {
    if (!batchId) return undefined;
    let stopped = false;
    let timer;

    const tick = async () => {
      try {
        const data = await getBatch(batchId);
        if (stopped) return;
        setBatch(data);
        if (data.status === "completed" || data.status === "failed") return;
      } catch (err) {
        if (stopped) return;
        setError(getErrorMessage(err));
      }
      timer = setTimeout(tick, POLL_MS);
    };

    tick();
    return () => {
      stopped = true;
      clearTimeout(timer);
    };
  }, [batchId]);

  const addFiles = (incoming) => {
    const accepted = [];
    const issues = [];
    [...files, ...Array.from(incoming)].forEach((file) => {
      if (!ALLOWED.includes(file.type)) {
        issues.push(`${file.name}: only JPEG, PNG and WEBP are allowed.`);
      } else if (file.size > MAX_SIZE) {
        issues.push(`${file.name}: larger than 10 MB.`);
      } else if (accepted.length >= MAX_FILES) {
        issues.push(`${file.name}: maximum ${MAX_FILES} files per upload.`);
      } else {
        accepted.push(file);
      }
    });
    setFiles(accepted);
    setProblems(issues);
  };

  const removeFile = (index) => setFiles(files.filter((_, i) => i !== index));

  const handleDrop = (event) => {
    event.preventDefault();
    setDragging(false);
    addFiles(event.dataTransfer.files);
  };

  const reset = () => {
    setFiles([]);
    setProblems([]);
    setRejected([]);
    setBatchId(null);
    setBatch(null);
    setUploadPercent(0);
    setError("");
  };

  const handleUpload = async () => {
    setError("");
    setUploading(true);
    setUploadPercent(0);
    try {
      const result = await uploadImages(albumId, files, setUploadPercent);
      setRejected(result.rejected || []);
      setBatch(null);
      setBatchId(result.batch_id);
      setFiles([]);
    } catch (err) {
      const data = err.response?.data;
      if (data?.rejected?.length) {
        setRejected(data.rejected);
        setError("None of the files were accepted.");
      } else {
        setError(getErrorMessage(err));
      }
    } finally {
      setUploading(false);
    }
  };

  const finished = batch && (batch.status === "completed" || batch.status === "failed");

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="text-2xl font-bold text-slate-800">Upload images</h1>

      {error && (
        <p className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>
      )}

      {!batchId && (
        <div className="mt-6 rounded-2xl bg-white p-4 shadow sm:p-6">
          <label className="block text-sm font-medium text-slate-700">
            Album
            <select
              value={albumId}
              onChange={(e) => setAlbumId(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
            >
              <option value="">Select an album</option>
              {albums.map((album) => (
                <option key={album.id} value={album.id}>
                  {album.name}
                </option>
              ))}
            </select>
          </label>
          {albums.length === 0 && (
            <p className="mt-2 text-sm text-slate-500">
              You need an album first.{" "}
              <Link to="/albums" className="text-sky-700 hover:underline">
                Create one
              </Link>
            </p>
          )}

          <div
            onDragOver={(e) => {
              e.preventDefault();
              setDragging(true);
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
            onClick={() => inputRef.current?.click()}
            className={`mt-4 cursor-pointer rounded-2xl border-2 border-dashed p-10 text-center ${
              dragging ? "border-sky-400 bg-sky-100" : "border-slate-300"
            }`}
          >
            <p className="text-slate-600">Drag and drop images here, or click to select</p>
            <p className="mt-1 text-xs text-slate-400">
              JPEG, PNG, WEBP. Up to 10 MB each, {MAX_FILES} files at once.
            </p>
            <input
              ref={inputRef}
              type="file"
              multiple
              accept="image/jpeg,image/png,image/webp"
              className="hidden"
              onChange={(e) => {
                addFiles(e.target.files);
                e.target.value = "";
              }}
            />
          </div>

          {problems.length > 0 && (
            <ul className="mt-3 space-y-1 text-sm text-red-600">
              {problems.map((text) => (
                <li key={text}>{text}</li>
              ))}
            </ul>
          )}

          {files.length > 0 && (
            <ul className="mt-4 divide-y divide-slate-100 rounded-lg border border-slate-200">
              {files.map((file, index) => (
                <li
                  key={`${file.name}-${index}`}
                  className="flex min-w-0 items-center justify-between gap-3 px-3 py-2 text-sm"
                >
                  <span className="truncate">
                    {file.name} <span className="text-slate-400">({formatBytes(file.size)})</span>
                  </span>
                  <button
                    onClick={() => removeFile(index)}
                    className="shrink-0 text-slate-400 hover:text-red-600"
                  >
                    ✕
                  </button>
                </li>
              ))}
            </ul>
          )}

          {uploading && (
            <div className="mt-4">
              <p className="mb-1 text-sm text-slate-500">Uploading... {uploadPercent}%</p>
              <ProgressBar value={uploadPercent} />
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={!albumId || files.length === 0 || uploading}
            className="mt-5 w-full rounded-lg bg-sky-200 py-2 font-semibold text-slate-950 hover:bg-sky-300 disabled:opacity-50"
          >
            {uploading ? "Uploading..." : `Upload ${files.length || ""} file(s)`}
          </button>
        </div>
      )}

      {batchId && (
        <div className="mt-6 rounded-2xl bg-white p-6 shadow">
          <h2 className="font-semibold text-slate-800">Processing batch #{batchId}</h2>
          <div className="mt-4">
            <ProgressBar value={batch?.progress ?? 0} />
            <p className="mt-2 text-sm text-slate-500">
              {batch
                ? `${batch.processed_images} done, ${batch.failed_images} failed, of ${batch.total_images} (${batch.progress}%)`
                : "Starting..."}
            </p>
          </div>

          {rejected.length > 0 && (
            <div className="mt-4 rounded-lg bg-amber-50 p-3 text-sm text-amber-800">
              <p className="font-medium">Some files were rejected:</p>
              <ul className="mt-1 list-disc pl-5">
                {rejected.map((item) => (
                  <li key={item.name}>
                    {item.name}: {item.error}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {finished && (
            <div className="mt-5 flex flex-wrap gap-3">
              {batch.status === "completed" && batch.download_available && (
                <button
                  onClick={() => downloadBatchZip(batchId).catch((e) => setError(getErrorMessage(e)))}
                  className="rounded-lg bg-sky-200 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-sky-300"
                >
                  Download ZIP
                </button>
              )}
              {batch.status === "failed" && (
                <p className="text-sm text-red-600">No image could be processed.</p>
              )}
              {batch.album && (
                <Link
                  to={`/albums/${batch.album}`}
                  className="rounded-lg border border-slate-300 px-4 py-2 text-sm hover:bg-slate-50"
                >
                  View album
                </Link>
              )}
              <button
                onClick={reset}
                className="rounded-lg border border-slate-300 px-4 py-2 text-sm hover:bg-slate-50"
              >
                Upload more
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}