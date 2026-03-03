import { useEffect, useState } from "react";
import {
  createUser,
  fetchUsers,
  updateUser,
  User,
  listDocuments,
  uploadDocument,
  getDocument,
  deleteDocument,
  DocumentSummary,
  DocumentDetail,
} from "../api";
import { useNavigate } from "react-router-dom";

export default function AdminDashboard() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("employee");
  const [error, setError] = useState<string | null>(null);
  const [docs, setDocs] = useState<DocumentSummary[]>([]);
  const [docsLoading, setDocsLoading] = useState(true);
  const [docError, setDocError] = useState<string | null>(null);
  const [selectedDoc, setSelectedDoc] = useState<DocumentDetail | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login");
      return;
    }
    setLoading(true);
    setDocsLoading(true);
    fetchUsers()
      .then(setUsers)
      .catch((err) => {
        console.error(err);
        setError("获取用户列表失败，可能没有管理员权限。");
      })
      .finally(() => setLoading(false));

    listDocuments()
      .then(setDocs)
      .catch((err) => {
        console.error(err);
        setDocError("获取知识库列表失败。");
      })
      .finally(() => setDocsLoading(false));
  }, [navigate]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      const user = await createUser({ username, password, role });
      setUsers((prev) => [...prev, user]);
      setUsername("");
      setPassword("");
      setRole("employee");
    } catch (err) {
      console.error(err);
      setError("创建用户失败，用户名可能已存在。");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login", { replace: true });
  };

  const handleToggleActive = async (user: User) => {
    if (
      !window.confirm(
        user.is_active
          ? `确认要禁用账号「${user.username}」吗？`
          : `确认要重新启用账号「${user.username}」吗？`
      )
    ) {
      return;
    }
    try {
      const updated = await updateUser(user.id, { is_active: !user.is_active });
      setUsers((prev) => prev.map((u) => (u.id === updated.id ? updated : u)));
    } catch (err) {
      console.error(err);
      setError("更新用户状态失败。");
    }
  };

  const handleChangeRole = async (user: User, newRole: string) => {
    try {
      const updated = await updateUser(user.id, { role: newRole });
      setUsers((prev) => prev.map((u) => (u.id === updated.id ? updated : u)));
    } catch (err) {
      console.error(err);
      setError("更新用户角色失败。");
    }
  };

  const handleUploadDoc = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setDocError(null);
    try {
      const doc = await uploadDocument(file);
      setDocs((prev) => [doc, ...prev]);
      e.target.value = "";
    } catch (err) {
      console.error(err);
      setDocError("上传文档失败，请确认为 UTF-8 编码的 .txt 文件。");
    }
  };

  const handleViewDoc = async (id: number) => {
    setDocError(null);
    try {
      const doc = await getDocument(id);
      setSelectedDoc(doc);
    } catch (err) {
      console.error(err);
      setDocError("获取文档内容失败。");
    }
  };

  const handleDeleteDoc = async (id: number) => {
    if (!window.confirm("确认删除该文档吗？")) return;
    setDocError(null);
    try {
      await deleteDocument(id);
      setDocs((prev) => prev.filter((d) => d.id !== id));
      if (selectedDoc?.id === id) {
        setSelectedDoc(null);
      }
    } catch (err) {
      console.error(err);
      setDocError("删除文档失败。");
    }
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        管理员后台
        <span className="top-right-link" onClick={handleLogout}>
          退出登录
        </span>
      </header>
      <main className="app-content">
        <div className="card" style={{ marginBottom: 16 }}>
          <h2 style={{ marginTop: 0, marginBottom: 12 }}>分配账号</h2>
          <form onSubmit={handleCreate}>
            <div className="form-group">
              <label className="form-label">用户名</label>
              <input
                className="input"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="例如：worker001"
              />
            </div>
            <div className="form-group">
              <label className="form-label">初始密码</label>
              <input
                className="input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">角色</label>
              <select
                className="select"
                value={role}
                onChange={(e) => setRole(e.target.value)}
              >
                <option value="employee">员工</option>
                <option value="admin">管理员</option>
              </select>
            </div>
            {error && (
              <div style={{ color: "red", fontSize: 13, marginBottom: 8 }}>
                {error}
              </div>
            )}
            <button className="button" type="submit">
              创建账号
            </button>
          </form>
        </div>

        <div className="card" style={{ marginBottom: 16 }}>
          <h2 style={{ marginTop: 0, marginBottom: 12 }}>当前账号列表</h2>
          {loading ? (
            <div>加载中...</div>
          ) : (
            <ul style={{ paddingLeft: 0, margin: 0, listStyle: "none" }}>
              {users.map((u) => (
                <li
                  key={u.id}
                  style={{
                    marginBottom: 8,
                    fontSize: 14,
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <div>
                    <div>
                        {u.username}（{u.role}
                        {u.role === "superadmin" ? "，受保护" : ""}
                        ）
                    </div>
                    <div style={{ fontSize: 12, color: "#888" }}>
                      状态：{u.is_active ? "启用" : "已禁用"}
                    </div>
                  </div>
                  <div style={{ display: "flex", gap: 8 }}>
                    {u.role !== "superadmin" && (
                      <>
                        <select
                          className="select"
                          style={{
                            width: 96,
                            fontSize: 12,
                            padding: "4px 8px",
                          }}
                          value={u.role}
                          onChange={(e) => handleChangeRole(u, e.target.value)}
                        >
                          <option value="employee">员工</option>
                          <option value="admin">管理员</option>
                        </select>
                        <button
                          type="button"
                          className="button"
                          style={{ width: 80, fontSize: 12, padding: "4px 8px" }}
                          onClick={() => handleToggleActive(u)}
                        >
                          {u.is_active ? "禁用" : "启用"}
                        </button>
                      </>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="card">
          <h2 style={{ marginTop: 0, marginBottom: 12 }}>RAG 知识库管理（txt）</h2>
          <div className="form-group">
            <label className="form-label">
              上传新的知识库文本（UTF-8 .txt）
            </label>
            <input
              className="input"
              type="file"
              accept=".txt"
              onChange={handleUploadDoc}
            />
          </div>
          {docError && (
            <div style={{ color: "red", fontSize: 13, marginBottom: 8 }}>
              {docError}
            </div>
          )}
          <div style={{ marginTop: 8, maxHeight: 200, overflow: "auto" }}>
            {docsLoading ? (
              <div>知识库加载中...</div>
            ) : docs.length === 0 ? (
              <div style={{ fontSize: 13, color: "#888" }}>
                还没有上传任何知识库文本。
              </div>
            ) : (
              <ul style={{ paddingLeft: 16, margin: 0 }}>
                {docs.map((d) => (
                  <li key={d.id} style={{ marginBottom: 4, fontSize: 13 }}>
                    <span
                      style={{ cursor: "pointer", textDecoration: "underline" }}
                      onClick={() => handleViewDoc(d.id)}
                    >
                      {d.filename}
                    </span>
                    <button
                      type="button"
                      style={{
                        marginLeft: 8,
                        fontSize: 12,
                        padding: "2px 6px",
                      }}
                      onClick={() => handleDeleteDoc(d.id)}
                    >
                      删除
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
          {selectedDoc && (
            <div
              style={{
                marginTop: 12,
                padding: 8,
                borderRadius: 8,
                border: "1px solid #eee",
                maxHeight: 200,
                overflow: "auto",
                fontSize: 12,
                whiteSpace: "pre-wrap",
              }}
            >
              <div
                style={{
                  fontWeight: 600,
                  marginBottom: 4,
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <span>{selectedDoc.filename}</span>
                <button
                  type="button"
                  style={{
                    marginLeft: 8,
                    fontSize: 12,
                    padding: "2px 6px",
                  }}
                  onClick={() => setSelectedDoc(null)}
                >
                  关闭预览
                </button>
              </div>
              {selectedDoc.content}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

