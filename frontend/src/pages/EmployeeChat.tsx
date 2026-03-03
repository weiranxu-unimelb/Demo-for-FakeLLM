import { useState } from "react";
import { askQuestion, Question } from "../api";
import { useNavigate } from "react-router-dom";

export default function EmployeeChat() {
  const [text, setText] = useState("");
  const [image, setImage] = useState<File | undefined>();
  const [history, setHistory] = useState<Question[]>([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    setLoading(true);
    try {
      const q = await askQuestion(text.trim(), image);
      setHistory((prev) => [...prev, q]);
      setText("");
      setImage(undefined);
    } catch (err) {
      console.error(err);
      alert("提问失败，请确认已登录并稍后重试。");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login", { replace: true });
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        员工问答
        <span className="top-right-link" onClick={handleLogout}>
          退出登录
        </span>
      </header>
      <main className="app-content">
        <div className="card" style={{ marginBottom: 16 }}>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">文字问题</label>
              <textarea
                className="text-area"
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="例如：这批货物应该如何摆放？"
              />
            </div>
            <div className="form-group">
              <label className="form-label">上传现场照片（可选，用于辅助理解）</label>
              <input
                className="input"
                type="file"
                accept="image/*"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  setImage(file ?? undefined);
                }}
              />
              {image && (
                <div style={{ marginTop: 8, fontSize: 13 }}>
                  <span>已选择：{image.name}</span>
                  <button
                    type="button"
                    style={{ marginLeft: 8, fontSize: 12, padding: "4px 8px" }}
                    onClick={() => setImage(undefined)}
                  >
                    取消图片
                  </button>
                </div>
              )}
            </div>
            <button className="button" disabled={loading}>
              {loading ? "思考中..." : "提交问题"}
            </button>
          </form>
        </div>

        <div className="card">
          <h2 style={{ marginTop: 0, marginBottom: 12 }}>历史回答（当前会话）</h2>
          <div className="chat-list">
            {history.map((q) => (
              <div key={q.id} style={{ marginBottom: 8 }}>
                <div className="chat-bubble user">Q：{q.question_text}</div>
                <div className="chat-bubble bot">
                  A：{q.answer_text ?? "（暂无回答）"}
                </div>
              </div>
            ))}
            {history.length === 0 && (
              <div style={{ fontSize: 13, color: "#888" }}>
                还没有问题，先在上方输入一条试试。
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

