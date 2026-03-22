/**
 * HTTP 请求封装模块
 * 
 * 功能说明：
 * - 提供统一的 request() 函数封装 fetch API
 * - 智能判断 API 地址
 * - 自动处理 JWT 认证
 * - 支持请求超时
 * - 统一的错误处理
 */

// 从环境变量读取 API 基础地址配置
const rawApiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();

// 判断当前页面是否运行在本地浏览器
const isLocalBrowser = ["127.0.0.1", "localhost"].includes(window.location.hostname);

// 判断配置的 API 地址是否指向本地后端
const pointsToLocalBackend = Boolean(rawApiBaseUrl && /(127\.0\.0\.1|localhost)/.test(rawApiBaseUrl));

/**
 * 智能选择 API 地址
 * 
 * 逻辑：
 * - 如果没有配置 VITE_API_BASE_URL → 使用当前域名（同源请求）
 * - 如果配置了但当前页面不是本地浏览器 → 使用配置的地址
 * - 如果配置了且当前页面是本地浏览器，但配置的是远程地址 → 使用配置的远程地址
 * - 如果配置了且当前页面是本地浏览器，但配置的是本地地址 → 使用当前域名（同源优先）
 */
const API_BASE_URL = !rawApiBaseUrl || (!isLocalBrowser && pointsToLocalBackend) ? window.location.origin : rawApiBaseUrl;

/** HTTP 请求方法类型 */
type RequestMethod = "GET" | "POST";

<<<<<<< HEAD
=======
/** 请求配置选项 */
interface RequestOptions {
  /** 请求超时时间（毫秒），默认 30000（30秒） */
  timeoutMs?: number;
}

/**
 * 从响应 payload 中提取友好的错误消息
 * 
 * FastAPI 错误响应格式：
 * - { detail: "错误信息" } → 直接返回
 * - { detail: [{ msg: "...", type: "..." }, ...] } → 提取所有 msg
 * - { message: "错误信息" } → 返回 message 字段
 * - 纯文本 → 直接返回
 * 
 * @param payload - 响应体（可能是对象或字符串）
 * @returns 提取的错误消息文本
 */
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
function extractErrorMessage(payload: unknown): string {
  // 字符串直接返回
  if (typeof payload === "string") {
    return payload;
  }

  // 对象类型尝试提取 detail 或 message
  if (payload && typeof payload === "object") {
    // 尝试获取 detail 字段
    const detail = Reflect.get(payload, "detail");
    
    // detail 是字符串
    if (typeof detail === "string") {
      return detail;
    }
    
    // detail 是数组（FastAPI 验证错误格式）
    if (Array.isArray(detail)) {
      return detail
        .map((item) => {
          if (typeof item === "string") {
            return item;
          }
          if (item && typeof item === "object") {
            // 提取 msg 字段
            return String(Reflect.get(item, "msg") ?? "请求失败");
          }
          return "请求失败";
        })
        .join("；");
    }
    
    // 尝试获取 message 字段
    const message = Reflect.get(payload, "message");
    if (typeof message === "string") {
      return message;
    }
  }

  // 默认错误消息
  return "请求失败";
}

<<<<<<< HEAD
export async function request<T>(path: string, method: RequestMethod, body?: unknown, token?: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
=======
/**
 * 通用 HTTP 请求函数
 * 
 * @template T - 响应数据类型
 * @param path - API 路径（不含 base URL）
 * @param method - HTTP 方法（GET 或 POST）
 * @param body - 请求体数据（可选）
 * @param token - JWT 认证令牌（可选）
 * @param options - 请求配置（可选）
 * @returns Promise<T> 响应数据
 * 
 * @example
 * // GET 请求
 * const user = await request<UserProfile>("/api/auth/me", "GET", undefined, token);
 * 
 * // POST 请求
 * const response = await request<LoginResponse>("/api/auth/login", "POST", { account, password });
 */
export async function request<T>(
  path: string,
  method: RequestMethod,
  body?: unknown,
  token?: string,
  options?: RequestOptions,
): Promise<T> {
  // 判断是否为 FormData（需要特殊处理 Content-Type）
  const isFormData = typeof FormData !== "undefined" && body instanceof FormData;
  
  // 创建 AbortController 用于超时控制
  const controller = new AbortController();
  const timeoutMs = options?.timeoutMs ?? 30000;
  const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);

  let response: Response;
  try {
    // 发起 fetch 请求
    response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers: {
        // FormData 不设置 Content-Type，让浏览器自动添加 multipart/form-data
        ...(isFormData ? {} : { "Content-Type": "application/json" }),
        // 添加 JWT 认证令牌
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      // body: JSON 序列化或直接使用 FormData
      body: body ? (isFormData ? body : JSON.stringify(body)) : undefined,
      // 绑定 abort 信号用于超时取消
      signal: controller.signal,
    });
  } catch (error) {
    // 清除超时计时器
    window.clearTimeout(timeoutId);
    
    // 处理超时错误
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error("请求超时，请稍后重试");
    }
    throw error;
  }

  // 清除超时计时器
  window.clearTimeout(timeoutId);
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)

  // 解析响应体
  const contentType = response.headers.get("content-type") ?? "";
  const isJson = contentType.includes("application/json");
  const payload = isJson ? await response.json() : await response.text();

  // 处理 HTTP 错误状态码
  if (!response.ok) {
    throw new Error(extractErrorMessage(payload));
  }

  // 返回解析后的数据
  return payload as T;
}
