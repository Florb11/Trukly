import { Navigate, Route, Routes } from "react-router-dom";
import MobileShell from "./components/MobileShell";
import ProtectedRoute from "./components/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import HomePage from "./pages/HomePage";
import ViajesPage from "./pages/ViajesPage";
import ScannerPage from "./pages/ScannerPage";
import FallasPage from "./pages/FallasPage";
import PerfilPage from "./pages/PerfilPage";
import HistorialPage from "./pages/HistorialPage";
import NotificacionesPage from "./pages/NotificacionesPage";
import MecanicoPage from "./pages/MecanicoPage";
import { useAuth } from "./context/AuthContext";

function App() {
  const { usuario } = useAuth();
  const chofer = (page) => <ProtectedRoute roles={["chofer"]}>{page}</ProtectedRoute>;
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute><MobileShell /></ProtectedRoute>}>
        <Route index element={usuario?.rol === "mecanico" ? <MecanicoPage /> : <HomePage />} />
        <Route path="viajes" element={chofer(<ViajesPage />)} />
        <Route path="historial" element={chofer(<HistorialPage />)} />
        <Route path="notificaciones" element={<NotificacionesPage />} />
        <Route path="escanear" element={chofer(<ScannerPage />)} />
        <Route path="fallas" element={chofer(<FallasPage />)} />
        <Route path="perfil" element={<PerfilPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
