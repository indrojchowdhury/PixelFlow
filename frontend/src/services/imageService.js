import api from "./api";

export const listImages = async (albumId) =>
  (await api.get("/images/", { params: { album: albumId } })).data.results;

export const deleteImage = (id) => api.delete(`/images/${id}/`);

export async function uploadImages(albumId, files, onProgress) {
  const form = new FormData();
  form.append("album", albumId);
  files.forEach((file) => form.append("files", file));

  const { data } = await api.post("/images/upload/", form, {
    onUploadProgress: (event) => {
      if (event.total && onProgress) {
        onProgress(Math.round((event.loaded / event.total) * 100));
      }
    },
  });
  return data;
}