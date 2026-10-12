import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ children, roles = ["chofer", "mecanico", "operador"] }) {
  const { token, usuario } = useAuth();
  if (!token) return <Navigate to="/login" replace />;
  if (!["chofer", "mecanico", "operador"].includes(usuario?.rol)) return <Navigate to="/login?rolInvalido=true" replace />;
  if (!roles.includes(usuario?.rol)) return <Navigate to="/" replace />;
  return children;
}
