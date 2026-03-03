import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login, setAuthToken } from "../api";

function decodeRoleFromToken(token: string): string | null {
  try {
    const [, payload] = token.split(".");
    const json = JSON.parse(atob(payload));
    return json.role ?? null;
  } catch {
    return null;
  }
}

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await login(username, password);
      setAuthToken(res.access_token);
      localStorage.setItem("token", res.access_token);
      const role = decodeRoleFromToken(res.access_token);
      if (role === "admin") {
        navigate("/admin", { replace: true });
      } else {
        navigate("/chat", { replace: true });
      }
    } catch (err) {
      console.error(err);
      setError("登录失败，请检查账号密码。");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="app-header">员工智能助手</header>
      <main className="app-content">
        <div className="card">
          <h2 style={{ marginTop: 0, marginBottom: 16 }}>登录</h2>
          <form onSubmit={handleSubmit}>
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
              <label className="form-label">密码</label>
              <input
                className="input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            {error && (
              <div style={{ color: "red", fontSize: 13, marginBottom: 8 }}>
                {error}
              </div>
            )}
            <button className="button" disabled={loading}>
              {loading ? "登录中..." : "登录"}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}

