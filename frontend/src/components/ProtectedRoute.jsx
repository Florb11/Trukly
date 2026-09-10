import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function ProtectedRoute({ children, rolPermitido }) {
  const { estaLogueado, usuario } = useAuth();
  const location = useLocation();

  if (!estaLogueado) {
    return <Navigate to="/login" replace />;
  }

  if (rolPermitido && usuario?.rol !== rolPermitido) {
    return <Navigate to="/no-autorizado" replace />;
  }

  if (
    usuario?.rol === "chofer" &&
    usuario.perfil_completo === false &&
    location.pathname !== "/dashboardTrucker/perfil"
  ) {
    return <Navigate to="/dashboardTrucker/perfil" replace />;
  }

  return children;
}

export default ProtectedRoute;
