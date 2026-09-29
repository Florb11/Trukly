import { Navigate, Route, Routes } from "react-router-dom";
import MobileShell from "./components/MobileShell";
import ProtectedRoute from "./components/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import HomePage from "./pages/HomePage";
import ViajesPage from "./pages/ViajesPage";
import ScannerPage from "./pages/ScannerPage";
import FallasPage from "./pages/FallasPage";
import PerfilPage from "./pages/PerfilPage";

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute><MobileShell /></ProtectedRoute>}>
        <Route index element={<HomePage />} />
        <Route path="viajes" element={<ViajesPage />} />
        <Route path="escanear" element={<ScannerPage />} />
        <Route path="fallas" element={<FallasPage />} />
        <Route path="perfil" element={<PerfilPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
