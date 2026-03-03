import { useEffect } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import LoginPage from "./pages/Login";
import AdminDashboard from "./pages/AdminDashboard";
import EmployeeChat from "./pages/EmployeeChat";
import { setAuthToken } from "./api";

function RequireAuth({ children }: { children: JSX.Element }) {
  const token = localStorage.getItem("token");
  const location = useLocation();

  useEffect(() => {
    setAuthToken(token);
  }, [token]);

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/admin"
        element={
          <RequireAuth>
            <AdminDashboard />
          </RequireAuth>
        }
      />
      <Route
        path="/chat"
        element={
          <RequireAuth>
            <EmployeeChat />
          </RequireAuth>
        }
      />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

