import { useState } from "react";
import { BrowserRouter, Route, Routes, useLocation } from "react-router-dom";
import { FaBars } from "react-icons/fa";

import AdminSidebarNav from "./components/AdminSidebarNav";
import Footer from "./components/Footer";
import Navbar from "./components/Navbar";
import SidebarNav from "./components/SidebarNav";

import DashboardAdminPage from "./pages/DashboardAdminPage";
import DashboardTruckerPage from "./pages/DashboardTruckerPage";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import RegistroPage from "./pages/RegistroPage";
import "./App.css";

function AppContent() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const esDashboardTrucker = location.pathname.startsWith("/dashboardTrucker");
  const esDashboardAdmin = location.pathname.startsWith("/dashboardAdmin");
  const esDashboard = esDashboardTrucker || esDashboardAdmin;

  if (esDashboard) {
    const SidebarComponent = esDashboardAdmin ? AdminSidebarNav : SidebarNav;
    const tituloPanel = esDashboardAdmin
      ? "Panel de administrador"
      : "Panel de chofer";

    return (
      <div
        className={`app-shell app-shell--dashboard ${
          esDashboardAdmin ? "app-shell--admin" : ""
        }`}
      >
        <SidebarComponent
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
                element={<DashboardTruckerPage title="Mis viajes" />}
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

              <Route path="/dashboardAdmin" element={<DashboardAdminPage />} />
              <Route
                path="/dashboardAdmin/usuarios"
                element={<DashboardAdminPage title="Gestión de usuarios" />}
              />
              <Route
                path="/dashboardAdmin/camiones"
                element={<DashboardAdminPage title="Gestión de camiones" />}
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
            </Routes>
          </main>
        </div>
      </div>
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