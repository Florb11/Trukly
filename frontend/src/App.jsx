import { useState } from "react";
import { BrowserRouter, Route, Routes, useLocation } from "react-router-dom";
import { FaBars } from "react-icons/fa";

import Footer from "./components/Footer";
import Navbar from "./components/Navbar";
import SidebarNav from "./components/SidebarNav";

import DashboardTruckerPage from "./pages/DashboardTruckerPage";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import RegistroPage from "./pages/RegistroPage";
import "./App.css";

function AppContent() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const esdashboardTruckerDashboard = location.pathname.startsWith("/dashboardTrucker");

  if (esdashboardTruckerDashboard) {
    return (
      <div className="app-shell app-shell--dashboard">
        <SidebarNav
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
              <strong>Panel de dashboardTrucker</strong>
            </div>
          </header>

          <main className="dashboard-content">
            <Routes>
              <Route path="/dashboardTrucker" element={<DashboardTruckerPage />} />
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