import api from "./api";

export const getBatch = async (id) => (await api.get(`/batches/${id}/`)).data;

// The ZIP endpoint needs the Authorization header, so a plain link cannot be used
export async function downloadBatchZip(id) {
  const response = await api.get(`/batches/${id}/download/`, { responseType: "blob" });
  const url = URL.createObjectURL(response.data);
  const link = document.createElement("a");
  link.href = url;
  link.download = `pixelflow-batch-${id}.zip`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}