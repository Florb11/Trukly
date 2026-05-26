import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function ProtectedRoute({ children, rolPermitido }) {
  const { estaLogueado, usuario } = useAuth();

  if (!estaLogueado) {
    return <Navigate to="/login" replace />;
  }

  if (rolPermitido && usuario?.rol !== rolPermitido) {
    return <Navigate to="/no-autorizado" replace />;
  }

  return children;
}

export default ProtectedRoute;