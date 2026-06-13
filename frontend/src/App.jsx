import { useState } from "react";
import { BrowserRouter, Route, Routes, useLocation } from "react-router-dom";
import { FaBars } from "react-icons/fa";

import Footer from "./components/Footer";
import Navbar from "./components/Navbar";
import DashboardSidebar from "./components/DashboardSidebar";
import ProtectedRoute from "./components/ProtectedRoute";

import DashboardAdminPage from "./pages/DashboardAdminPage";
import DashboardTruckerPage from "./pages/DashboardTruckerPage";
import DashboardMecanicoPage from "./pages/DashboardMecanicoPage";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import RegistroPage from "./pages/RegistroPage";
import AdminUsuariosPage from "./pages/AdminUsuariosPage";
import NoAutorizadoPage from "./pages/NoAutorizadoPage";
import NotFoundPage from "./pages/NotFoundPage";
import AdminCamionesPage from "./pages/AdminCamionesPage";
import AdminReportesPage from "./pages/AdminReportesPage";
import DashboardOperatorPage from "./pages/DashboardOperatorPage";
import OperadorViajePage from "./pages/OperadorViajePage";
import ViajesTruckerPage from "./pages/ViajesTruckerPage";
import AdminViajesPage from "./pages/AdminViajesPage";
import AdminMantenimientoPage from "./pages/AdminMantenimientoPage";
import AdminEstadisticasPage from "./pages/AdminEstadisticasPage";
import PerfilPage from "./pages/PerfilPage";
import MecanicoReportesPage from "./pages/MecanicoReportesPage";
import NotificacionesPage from "./pages/NotificacionesPage";
import MecanicoMantenimientoPage from "./pages/MecanicoMantenimientoPage";
import ChoferReportesPage from "./pages/ChoferReportesPage";
import OperadorCamionesPage from "./pages/OperadorCamionesPage";

import "./App.css";
import "./styles/dashboard-unified.css";

function AppContent() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const esDashboardTrucker = location.pathname.startsWith("/dashboardTrucker");
  const esDashboardAdmin = location.pathname.startsWith("/dashboardAdmin");
  const esDashboardOperator = location.pathname.startsWith("/dashboardOperator");
  const esDashboardMechanic = location.pathname.startsWith("/dashboardMechanic");

  const esDashboard =
    esDashboardTrucker ||
    esDashboardAdmin ||
    esDashboardOperator ||
    esDashboardMechanic;

  const tituloPanel = esDashboardAdmin
    ? "Panel de administrador"
    : esDashboardOperator
      ? "Panel de operador logístico"
      : esDashboardMechanic
        ? "Panel de mecánico"
        : "Panel de chofer";

  const rolPermitido = esDashboardAdmin
    ? "admin"
    : esDashboardOperator
      ? "operador"
      : esDashboardMechanic
        ? "mecanico"
        : "chofer";

  if (esDashboard) {
    return (
      <ProtectedRoute rolPermitido={rolPermitido}>
        <div
          className={[
            "app-shell",
            "app-shell--dashboard",
            esDashboardAdmin ? "app-shell--admin" : "",
            esDashboardMechanic ? "app-shell--mechanic" : "",
          ].filter(Boolean).join(" ")}
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
                {/* CHOFER */}
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
                  element={<ChoferReportesPage title="Reportar falla" />}
                />

                <Route
                  path="/dashboardTrucker/estadisticas"
                  element={<DashboardTruckerPage title="Estadísticas" />}
                />

                <Route
                  path="/dashboardTrucker/perfil"
                  element={<PerfilPage />}
                />

                <Route
                  path="/dashboardTrucker/notificaciones"
                  element={<NotificacionesPage />}
                />

                {/* ADMIN */}
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
                  element={<AdminReportesPage />}
                />

                <Route
                  path="/dashboardAdmin/viajes"
                  element={<AdminViajesPage />}
                />

                <Route
                  path="/dashboardAdmin/mantenimiento"
                  element={<AdminMantenimientoPage />}
                />

                <Route
                  path="/dashboardAdmin/estadisticas"
                  element={<AdminEstadisticasPage />}
                />

                <Route
                  path="/dashboardAdmin/perfil"
                  element={<PerfilPage />}
                />

                <Route
                  path="/dashboardAdmin/notificaciones"
                  element={<NotificacionesPage />}
                />

                {/* OPERADOR */}
                <Route
                  path="/dashboardOperator"
                  element={<DashboardOperatorPage />}
                />

                <Route
                  path="/dashboardOperator/crear-viaje"
                  element={<OperadorViajePage />}
                />

                <Route
                  path="/dashboardOperator/perfil"
                  element={<PerfilPage />}
                />
                
                <Route
                  path="/dashboardOperator/camiones"
                  element={<OperadorCamionesPage />}
                  />

                <Route
                  path="/dashboardOperator/notificaciones"
                  element={<NotificacionesPage />}
                />
             

                {/* MECÁNICO */}
                <Route
                  path="/dashboardMechanic"
                  element={<DashboardMecanicoPage />}
                />

                <Route
                  path="/dashboardMechanic/reportes"
                  element={<MecanicoReportesPage />}
                />

                <Route
                  path="/dashboardMechanic/perfil"
                  element={<PerfilPage />}
                />

                <Route
                  path="/dashboardMechanic/notificaciones"
                  element={<NotificacionesPage />}
                />
                <Route
                  path="/dashboardMechanic/mantenimiento"
                  element={<MecanicoMantenimientoPage />}
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