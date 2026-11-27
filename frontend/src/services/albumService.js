import api from "./api";

export const listAlbums = async () => (await api.get("/albums/")).data.results;
export const createAlbum = async (payload) => (await api.post("/albums/", payload)).data;
export const updateAlbum = async (id, payload) =>
  (await api.patch(`/albums/${id}/`, payload)).data;
export const deleteAlbum = (id) => api.delete(`/albums/${id}/`);