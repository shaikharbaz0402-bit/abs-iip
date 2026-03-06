export class ApiError extends Error {
  status: number;

  detail: unknown;

  constructor(status: number, detail: unknown, message?: string) {
    super(message ?? `API request failed with status ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

interface RequestOptions {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  query?: Record<string, string | number | boolean | null | undefined>;
  body?: unknown;
  signal?: AbortSignal;
  tenantId?: string;
  skipAuth?: boolean;
  retryCount?: number;
}

interface UploadOptions {
  path: string;
  formData: FormData;
  tenantId?: string;
  skipAuth?: boolean;
  onProgress?: (percent: number) => void;
}

type TokenGetter = () => string | null;
type RefreshTokenFn = () => Promise<string | null>;
type TenantGetter = () => string | null;
type UnauthorizedHandler = () => void;

const DEFAULT_RETRIES = 2;

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const buildQueryString = (query?: RequestOptions["query"]): string => {
  if (!query) return "";
  const params = new URLSearchParams();
  Object.entries(query).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      params.set(key, String(value));
    }
  });
  const encoded = params.toString();
  return encoded ? `?${encoded}` : "";
};

const parseBody = async (response: Response): Promise<unknown> => {
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return response.json();
  }
  return response.text();
};

class ApiClient {
  private readonly baseApiUrl: string;

  private tokenGetter: TokenGetter = () => null;

  private refreshTokenFn: RefreshTokenFn = async () => null;

  private tenantGetter: TenantGetter = () => null;

  private unauthorizedHandler: UnauthorizedHandler = () => {};

  constructor(baseUrl: string) {
    const normalized = baseUrl.replace(/\/$/, "");
    this.baseApiUrl = `${normalized}/api/v1`;
  }

  configureAuth(tokenGetter: TokenGetter, refreshTokenFn?: RefreshTokenFn, unauthorizedHandler?: UnauthorizedHandler): void {
    this.tokenGetter = tokenGetter;
    if (refreshTokenFn) {
      this.refreshTokenFn = refreshTokenFn;
    }
    if (unauthorizedHandler) {
      this.unauthorizedHandler = unauthorizedHandler;
    }
  }

  configureTenant(tenantGetter: TenantGetter): void {
    this.tenantGetter = tenantGetter;
  }

  async get<T>(path: string, options?: Omit<RequestOptions, "method" | "body">): Promise<T> {
    return this.request<T>(path, { ...options, method: "GET" });
  }

  async post<T>(path: string, body?: unknown, options?: Omit<RequestOptions, "method" | "body">): Promise<T> {
    return this.request<T>(path, { ...options, method: "POST", body });
  }

  async put<T>(path: string, body?: unknown, options?: Omit<RequestOptions, "method" | "body">): Promise<T> {
    return this.request<T>(path, { ...options, method: "PUT", body });
  }

  async patch<T>(path: string, body?: unknown, options?: Omit<RequestOptions, "method" | "body">): Promise<T> {
    return this.request<T>(path, { ...options, method: "PATCH", body });
  }

  async upload<T>(options: UploadOptions): Promise<T> {
    const token = this.tokenGetter();
    const activeTenantId = options.tenantId || this.tenantGetter();

    return new Promise<T>((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open("POST", `${this.baseApiUrl}${options.path}`);

      if (!options.skipAuth && token) {
        xhr.setRequestHeader("Authorization", `Bearer ${token}`);
      }

      if (activeTenantId) {
        xhr.setRequestHeader("X-Tenant-ID", activeTenantId);
      }

      xhr.upload.onprogress = (event) => {
        if (!event.lengthComputable || !options.onProgress) return;
        const percent = Math.round((event.loaded / event.total) * 100);
        options.onProgress(percent);
      };

      xhr.onerror = () => reject(new ApiError(0, null, "Network error during upload"));

      xhr.onload = () => {
        const contentType = xhr.getResponseHeader("content-type") || "";
        const raw = xhr.responseText;
        const payload = contentType.includes("application/json") && raw ? JSON.parse(raw) : raw;

        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(payload as T);
          return;
        }

        if (xhr.status === 401) {
          this.unauthorizedHandler();
        }

        reject(new ApiError(xhr.status, payload, "Upload failed"));
      };

      xhr.send(options.formData);
    });
  }

  private async request<T>(path: string, options: RequestOptions, retriedForAuth = false): Promise<T> {
    const {
      method = "GET",
      query,
      body,
      signal,
      tenantId,
      skipAuth = false,
      retryCount = DEFAULT_RETRIES,
    } = options;

    let attempt = 0;

    while (attempt <= retryCount) {
      try {
        const token = this.tokenGetter();
        const headers = new Headers();
        const activeTenantId = tenantId || this.tenantGetter();

        if (!skipAuth && token) {
          headers.set("Authorization", `Bearer ${token}`);
        }

        if (activeTenantId) {
          headers.set("X-Tenant-ID", activeTenantId);
        }

        if (body != null) {
          headers.set("Content-Type", "application/json");
        }

        const response = await fetch(`${this.baseApiUrl}${path}${buildQueryString(query)}`, {
          method,
          headers,
          body: body != null ? JSON.stringify(body) : undefined,
          signal,
        });

        if (response.status === 401 && !skipAuth && !retriedForAuth) {
          const newToken = await this.refreshTokenFn();
          if (newToken) {
            return this.request<T>(path, options, true);
          }
          this.unauthorizedHandler();
        }

        const payload = await parseBody(response);

        if (!response.ok) {
          throw new ApiError(response.status, payload, extractErrorMessage(payload, response.statusText));
        }

        return payload as T;
      } catch (error) {
        if (error instanceof ApiError) {
          if (error.status >= 500 && attempt < retryCount) {
            await delay(250 * (attempt + 1));
            attempt += 1;
            continue;
          }
          throw error;
        }

        if (attempt < retryCount) {
          await delay(250 * (attempt + 1));
          attempt += 1;
          continue;
        }

        throw error;
      }
    }

    throw new ApiError(0, null, "Request failed after retries");
  }
}

const extractErrorMessage = (payload: unknown, fallback: string): string => {
  if (typeof payload === "object" && payload !== null && "detail" in payload) {
    const detail = (payload as { detail?: unknown }).detail;
    if (typeof detail === "string") return detail;
  }
  if (typeof payload === "string" && payload.length > 0) {
    return payload;
  }
  return fallback || "Request failed";
};

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "https://abs-iip-production.up.railway.app";

export const apiClient = new ApiClient(apiBaseUrl);
