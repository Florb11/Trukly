import { Link } from "react-router-dom";

function NoAutorizadoPage() {
  return (
    <section className="auth-page">
      <div className="auth-card">
        <h2>No autorizado</h2>
        <p>No tenés permisos para acceder a esta sección.</p>
        <Link to="/">Volver al inicio</Link>
      </div>
    </section>
  );
}

export default NoAutorizadoPage;