import { useState } from "react";
import { FaMoon, FaSun } from "react-icons/fa";

export default function ThemeToggle() {
  const [tema, setTema] = useState(() => document.documentElement.dataset.theme || "light");
  const cambiar = () => {
    const siguiente = tema === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = siguiente;
    document.querySelector('meta[name="theme-color"]').content = siguiente === "dark" ? "#101722" : "#f4f7fb";
    try { localStorage.setItem("trukly_mobile_theme", siguiente); } catch { /* El tema sigue funcionando sin almacenamiento. */ }
    setTema(siguiente);
  };
  const etiqueta = tema === "dark" ? "Activar modo claro" : "Activar modo oscuro";
  return <button type="button" className="theme-toggle" onClick={cambiar} title={etiqueta} aria-label={etiqueta}>{tema === "dark" ? <FaSun /> : <FaMoon />}</button>;
}
