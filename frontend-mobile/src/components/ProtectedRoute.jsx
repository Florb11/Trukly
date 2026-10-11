import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ children }) {
  const { token, usuario } = useAuth();
  if (!token) return <Navigate to="/login" replace />;
  if (usuario?.rol !== "chofer") return <Navigate to="/login?rolInvalido=true" replace />;
  return children;
}
