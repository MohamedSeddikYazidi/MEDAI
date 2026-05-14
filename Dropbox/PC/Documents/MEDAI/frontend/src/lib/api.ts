const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface FetchOptions extends RequestInit {
  token?: string;
}

async function fetchAPI(endpoint: string, options: FetchOptions = {}) {
  const { token, ...fetchOpts } = options;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...fetchOpts,
    headers,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || "API request failed");
  }

  return res.json();
}

// Auth API
export const authAPI = {
  login: (username: string, password: string) =>
    fetchAPI("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username, password }).toString(),
    }),
  refresh: (refreshToken: string) =>
    fetchAPI("/api/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token: refreshToken }),
    }),
  getMe: (token: string) =>
    fetchAPI("/api/auth/me", { token }),
};

// Agent API
export const agentAPI = {
  analyze: (query: string, token: string, options = {}) =>
    fetchAPI("/api/agents/analyze", {
      method: "POST",
      token,
      body: JSON.stringify({ query, query_type: "full_analysis", ...options }),
    }),
  intake: (query: string, token: string) =>
    fetchAPI("/api/agents/intake", {
      method: "POST",
      token,
      body: JSON.stringify({ query }),
    }),
  diagnose: (query: string, token: string) =>
    fetchAPI("/api/agents/diagnose", {
      method: "POST",
      token,
      body: JSON.stringify({ query }),
    }),
  predictRisk: (features: Record<string, number>, token: string) =>
    fetchAPI("/api/agents/predict-risk", {
      method: "POST",
      token,
      body: JSON.stringify({ features }),
    }),
  searchKnowledge: (query: string, token: string) =>
    fetchAPI("/api/agents/search-knowledge", {
      method: "POST",
      token,
      body: JSON.stringify({ query }),
    }),
  recommendTreatment: (data: any, token: string) =>
    fetchAPI("/api/agents/recommend-treatment", {
      method: "POST",
      token,
      body: JSON.stringify(data),
    }),
};

// Analytics API
export const analyticsAPI = {
  getKPIs: (token: string) =>
    fetchAPI("/api/analytics/kpis", { token }),
  getDashboard: (type: string, token: string) =>
    fetchAPI(`/api/analytics/dashboard/${type}`, { token }),
  getModelMetrics: (token: string) =>
    fetchAPI("/api/analytics/model-metrics", { token }),
};

// Chat API
export const chatAPI = {
  send: (message: string, token: string, queryType = "auto") =>
    fetchAPI("/api/chat", {
      method: "POST",
      token,
      body: JSON.stringify({ message, query_type: queryType }),
    }),
};

// Patient API
export const patientAPI = {
  list: (token: string, page = 1, limit = 20) =>
    fetchAPI(`/api/patients?page=${page}&limit=${limit}`, { token }),
  get: (id: string, token: string) =>
    fetchAPI(`/api/patients/${id}`, { token }),
  stats: (token: string) =>
    fetchAPI("/api/patients/stats/summary", { token }),
};

// System API
export const systemAPI = {
  health: () => fetchAPI("/api/health"),
  info: (token: string) => fetchAPI("/api/system/info", { token }),
};
