import axios from "axios";

// 强制使用 /api 相对路径
// 本地开发(npm run dev): 由 vite.config.ts 的 proxy 转发到后端
// 生产环境(docker): 由 nginx.conf 的 location /api/ 转发到后端
const API_BASE_URL = "/api";

const api = axios.create({
  baseURL: API_BASE_URL,
});

export function setAuthToken(token: string | null) {
  if (token) {
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common["Authorization"];
  }
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export async function login(username: string, password: string) {
  const form = new URLSearchParams();
  form.append("username", username);
  form.append("password", password);
  const res = await api.post<LoginResponse>("/auth/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return res.data;
}

export interface User {
  id: number;
  username: string;
  role: string;
  is_active: boolean;
}

export async function fetchUsers() {
  const res = await api.get<User[]>("/admin/users");
  return res.data;
}

export async function createUser(payload: {
  username: string;
  password: string;
  role: string;
}) {
  const res = await api.post<User>("/admin/users", payload);
  return res.data;
}

export async function updateUser(
  id: number,
  payload: Partial<Pick<User, "role" | "is_active">>
) {
  const res = await api.patch<User>(`/admin/users/${id}`, payload);
  return res.data;
}

export interface Question {
  id: number;
  question_text: string;
  answer_text: string | null;
  created_at: string;
}

export async function askQuestion(text: string, image?: File) {
  const formData = new FormData();
  formData.append("text", text);
  if (image) {
    formData.append("image", image);
  }
  const res = await api.post<Question>("/chat/query", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

export interface DocumentSummary {
  id: number;
  filename: string;
  created_at: string;
}

export interface DocumentDetail extends DocumentSummary {
  content: string;
}

export async function listDocuments() {
  const res = await api.get<DocumentSummary[]>("/admin/docs");
  return res.data;
}

export async function uploadDocument(file: File) {
  const form = new FormData();
  form.append("file", file);
  const res = await api.post<DocumentSummary>("/admin/docs", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

export async function getDocument(id: number) {
  const res = await api.get<DocumentDetail>(`/admin/docs/${id}`);
  return res.data;
}

export async function deleteDocument(id: number) {
  await api.delete(`/admin/docs/${id}`);
}

