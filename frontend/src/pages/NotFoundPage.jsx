import { Link } from "react-router-dom";

function NotFoundPage() {
  return (
    <section className="auth-page">
      <div className="auth-card">
        <h2>Página no encontrada</h2>
        <p>La ruta que intentaste abrir no existe.</p>
        <Link to="/">Volver al inicio</Link>
      </div>
    </section>
  );
}

export default NotFoundPage;