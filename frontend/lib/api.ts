const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {"Content-Type": "application/json", ...(options?.headers || {})},
    cache: "no-store",
  });
  if (!response.ok) throw new Error(`API request failed: ${response.status}`);
  return response.json();
}

export const formatPlatform = (value: string) =>
  value === "imessage" ? "iMessage" : value.charAt(0).toUpperCase() + value.slice(1);

export const timeAgo = (date: string) => {
  const minutes = Math.max(1, Math.floor((Date.now() - new Date(date).getTime()) / 60000));
  if (minutes < 60) return `${minutes}m`;
  if (minutes < 1440) return `${Math.floor(minutes / 60)}h`;
  return `${Math.floor(minutes / 1440)}d`;
};

