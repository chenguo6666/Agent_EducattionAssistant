const rawApiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
const isLocalBrowser = ["127.0.0.1", "localhost"].includes(window.location.hostname);
const pointsToLocalBackend = Boolean(rawApiBaseUrl && /(127\.0\.0\.1|localhost)/.test(rawApiBaseUrl));

const API_BASE_URL = !rawApiBaseUrl || (!isLocalBrowser && pointsToLocalBackend) ? window.location.origin : rawApiBaseUrl;

type RequestMethod = "GET" | "POST";

interface RequestOptions {
  timeoutMs?: number;
}

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

export async function request<T>(
  path: string,
  method: RequestMethod,
  body?: unknown,
  token?: string,
  options?: RequestOptions,
): Promise<T> {
  const isFormData = typeof FormData !== "undefined" && body instanceof FormData;
  const controller = new AbortController();
  const timeoutMs = options?.timeoutMs ?? 30000;
  const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers: {
        ...(isFormData ? {} : { "Content-Type": "application/json" }),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: body ? (isFormData ? body : JSON.stringify(body)) : undefined,
      signal: controller.signal,
    });
  } catch (error) {
    window.clearTimeout(timeoutId);
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error("请求超时，请稍后重试");
    }
    throw error;
  }

  window.clearTimeout(timeoutId);

  const contentType = response.headers.get("content-type") ?? "";
  const isJson = contentType.includes("application/json");
  const payload = isJson ? await response.json() : await response.text();

  if (!response.ok) {
    throw new Error(extractErrorMessage(payload));
  }

  return payload as T;
}
