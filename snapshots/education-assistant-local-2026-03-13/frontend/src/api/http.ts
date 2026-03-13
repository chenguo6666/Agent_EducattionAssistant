const rawApiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
const isLocalBrowser = ["127.0.0.1", "localhost"].includes(window.location.hostname);
const pointsToLocalBackend = Boolean(rawApiBaseUrl && /(127\.0\.0\.1|localhost)/.test(rawApiBaseUrl));

const API_BASE_URL = !rawApiBaseUrl || (!isLocalBrowser && pointsToLocalBackend) ? window.location.origin : rawApiBaseUrl;

type RequestMethod = "GET" | "POST";

function extractErrorMessage(payload: unknown): string {
  if (typeof payload === "string") {
    return payload;
  }

  if (payload && typeof payload === "object") {
    const detail = Reflect.get(payload, "detail");
    if (typeof detail === "string") {
      return detail;
    }
    if (Array.isArray(detail)) {
      return detail
        .map((item) => {
          if (typeof item === "string") {
            return item;
          }
          if (item && typeof item === "object") {
            return String(Reflect.get(item, "msg") ?? "请求失败");
          }
          return "请求失败";
        })
        .join("；");
    }
    const message = Reflect.get(payload, "message");
    if (typeof message === "string") {
      return message;
    }
  }

  return "请求失败";
}

export async function request<T>(path: string, method: RequestMethod, body?: unknown, token?: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  const contentType = response.headers.get("content-type") ?? "";
  const isJson = contentType.includes("application/json");
  const payload = isJson ? await response.json() : await response.text();

  if (!response.ok) {
    throw new Error(extractErrorMessage(payload));
  }

  return payload as T;
}
