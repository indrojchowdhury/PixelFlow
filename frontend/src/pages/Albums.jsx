import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import Modal from "../components/Modal";
import {
  createAlbum,
  deleteAlbum,
  listAlbums,
  updateAlbum,
} from "../services/albumService";
import { getErrorMessage } from "../utils/errors";

export default function Albums() {
  const [albums, setAlbums] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pageError, setPageError] = useState("");
  // editing: null (closed), {} (create), or an album object (edit)
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ name: "", description: "" });
  const [formError, setFormError] = useState("");
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    try {
      setAlbums(await listAlbums());
      setPageError("");
    } catch (err) {
      setPageError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load();
  }, [load]);

  const openCreate = () => {
    setForm({ name: "", description: "" });
    setFormError("");
    setEditing({});
  };

  const openEdit = (album) => {
    setForm({ name: album.name, description: album.description });
    setFormError("");
    setEditing(album);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSaving(true);
    setFormError("");
    try {
      if (editing.id) {
        await updateAlbum(editing.id, form);
      } else {
        await createAlbum(form);
      }
      setEditing(null);
      await load();
    } catch (err) {
      setFormError(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (album) => {
    const ok = window.confirm(
      `Delete "${album.name}" and all ${album.image_count} image(s) inside it?`
    );
    if (!ok) return;
    try {
      await deleteAlbum(album.id);
      await load();
    } catch (err) {
      setPageError(getErrorMessage(err));
    }
  };

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-bold text-slate-800">Albums</h1>
        <button
          onClick={openCreate}
          className="rounded-lg bg-sky-200 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-sky-300"
        >
          New album
        </button>
      </div>

      {pageError && (
        <p className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{pageError}</p>
      )}

      {loading ? (
        <p className="mt-8 text-slate-500">Loading...</p>
      ) : albums.length === 0 ? (
        <div className="mt-8 rounded-2xl bg-white p-10 text-center shadow">
          <p className="text-slate-500">No albums yet. Create your first one.</p>
        </div>
      ) : (
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {albums.map((album) => (
            <div key={album.id} className="rounded-2xl bg-white p-5 shadow">
              <Link
                to={`/albums/${album.id}`}
                className="text-lg font-semibold text-sky-700 hover:underline"
              >
                {album.name}
              </Link>
              <p className="mt-1 line-clamp-2 text-sm text-slate-500">
                {album.description || "No description"}
              </p>
              <p className="mt-3 text-sm text-slate-700">{album.image_count} image(s)</p>
              <div className="mt-4 flex gap-2">
                <button
                  onClick={() => openEdit(album)}
                  className="rounded-lg border border-slate-300 px-3 py-1 text-sm hover:bg-slate-50"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(album)}
                  className="rounded-lg border border-red-200 px-3 py-1 text-sm text-red-600 hover:bg-red-50"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {editing && (
        <Modal title={editing.id ? "Edit album" : "New album"} onClose={() => setEditing(null)}>
          <form onSubmit={handleSubmit}>
            {formError && (
              <p className="mb-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
                {formError}
              </p>
            )}
            <label className="block text-sm font-medium text-slate-700">
              Name
              <input
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                required
                maxLength={100}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-sky-500"
              />
            </label>
            <label className="mt-4 block text-sm font-medium text-slate-700">
              Description
              <textarea
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                rows={3}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-sky-500"
              />
            </label>
            <button
              type="submit"
              disabled={saving}
              className="mt-5 w-full rounded-lg bg-sky-200 py-2 font-semibold text-slate-950 hover:bg-sky-300 disabled:opacity-60"
            >
              {saving ? "Saving..." : "Save"}
            </button>
          </form>
        </Modal>
      )}
    </div>
  );
}