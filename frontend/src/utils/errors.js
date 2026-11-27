// Turns a DRF error response into one readable message
// Examples: {"email": ["..."]}, {"detail": "..."}, or a network failure
export function getErrorMessage(error) {
  const data = error.response?.data;

  if (!error.response) {
    return "Cannot reach the server. Please try again.";
  }
  if (typeof data === "string") {
    return "Something went wrong. Please try again.";
  }
  if (data?.detail) {
    return data.detail;
  }
  if (data && typeof data === "object") {
    const messages = Object.entries(data).flatMap(([field, value]) => {
      const list = Array.isArray(value) ? value : [String(value)];
      return list.map((text) => (field === "non_field_errors" ? text : `${field}: ${text}`));
    });
    if (messages.length) {
      return messages.join(" ");
    }
  }
  return "Something went wrong. Please try again.";
}