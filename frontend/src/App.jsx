import { useState } from "react";
import { BrowserRouter, Route, Routes, useLocation } from "react-router-dom";
import { FaBars } from "react-icons/fa";

import Footer from "./components/Footer";
import Navbar from "./components/Navbar";
import DashboardSidebar from "./components/DashboardSidebar";
import ProtectedRoute from "./components/ProtectedRoute";

import DashboardAdminPage from "./pages/DashboardAdminPage";
import DashboardTruckerPage from "./pages/DashboardTruckerPage";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import RegistroPage from "./pages/RegistroPage";
import AdminUsuariosPage from "./pages/AdminUsuariosPage";
import NoAutorizadoPage from "./pages/NoAutorizadoPage";
import NotFoundPage from "./pages/NotFoundPage";
import AdminCamionesPage from "./pages/AdminCamionesPage";
import DashboardOperatorPage from "./pages/DashboardOperatorPage";
import OperadorViajePage from "./pages/OperadorViajePage";
import ViajesTruckerPage from "./pages/ViajesTruckerPage";

import "./App.css";

function AppContent() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const esDashboardTrucker = location.pathname.startsWith("/dashboardTrucker");
  const esDashboardAdmin = location.pathname.startsWith("/dashboardAdmin");
  const esDashboardOperator =location.pathname.startsWith("/dashboardOperator");

  const esDashboard =
    esDashboardTrucker || esDashboardAdmin || esDashboardOperator;

  const tituloPanel = esDashboardAdmin
    ? "Panel de administrador"
    : esDashboardOperator
      ? "Panel de operador logístico"
      : "Panel de chofer";

  const rolPermitido = esDashboardAdmin
    ? "admin"
    : esDashboardOperator
      ? "operador"
      : "chofer";

  if (esDashboard) {
    return (
      <ProtectedRoute rolPermitido={rolPermitido}>
        <div
          className={`app-shell app-shell--dashboard ${
            esDashboardAdmin ? "app-shell--admin" : ""
          }`}
        >
          <DashboardSidebar
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
          />

          <div className="dashboard-area">
            <header className="dashboard-topbar">
              <button
                className="dashboard-menu-btn"
                type="button"
                onClick={() => setSidebarOpen(true)}
                aria-label="Abrir menú"
              >
                <FaBars />
              </button>

              <div>
                <span>Trukly</span>
                <strong>{tituloPanel}</strong>
              </div>
            </header>

            <main className="dashboard-content">
              <Routes>
                <Route
                  path="/dashboardTrucker"
                  element={<DashboardTruckerPage />}
                />

                <Route
                  path="/dashboardTrucker/viajes"
                  element={<ViajesTruckerPage title="Mis viajes" />}
                />

                <Route
                  path="/dashboardTrucker/rutas"
                  element={<DashboardTruckerPage title="Rutas asignadas" />}
                />

                <Route
                  path="/dashboardTrucker/fallas"
                  element={<DashboardTruckerPage title="Reportar falla" />}
                />

                <Route
                  path="/dashboardTrucker/estadisticas"
                  element={<DashboardTruckerPage title="Estadísticas" />}
                />

                <Route
                  path="/dashboardTrucker/perfil"
                  element={<DashboardTruckerPage title="Perfil" />}
                />

                <Route
                  path="/dashboardTrucker/configuracion"
                  element={<DashboardTruckerPage title="Configuración" />}
                />

                <Route
                  path="/dashboardAdmin"
                  element={<DashboardAdminPage />}
                />

                <Route
                  path="/dashboardAdmin/usuarios"
                  element={<AdminUsuariosPage />}
                />

                <Route
                  path="/dashboardAdmin/camiones"
                  element={<AdminCamionesPage />}
                />

                <Route
                  path="/dashboardAdmin/reportes"
                  element={<DashboardAdminPage title="Reportes del sistema" />}
                />

                <Route
                  path="/dashboardAdmin/mantenimiento"
                  element={<DashboardAdminPage title="Mantenimiento" />}
                />

                <Route
                  path="/dashboardAdmin/estadisticas"
                  element={<DashboardAdminPage title="Estadísticas" />}
                />

                <Route
                  path="/dashboardAdmin/perfil"
                  element={<DashboardAdminPage title="Perfil administrador" />}
                />

                <Route
                  path="/dashboardAdmin/configuracion"
                  element={<DashboardAdminPage title="Configuración" />}
                />

                <Route
                  path="/dashboardOperator"
                  element={<DashboardOperatorPage />}
                />

              
                <Route
                  path="/dashboardOperator/crear-viaje"
                  element={<OperadorViajePage />}
                />

                <Route path="*" element={<NotFoundPage />} />
              </Routes>
            </main>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <div className="app-shell">
      <Navbar />

      <main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/registro" element={<RegistroPage />} />
          <Route path="/no-autorizado" element={<NoAutorizadoPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </main>

      <Footer />
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;
