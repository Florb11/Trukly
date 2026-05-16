import "./DashboardTruckerPage.css";

function DashboardTruckerPage({ title = "Panel del chofer" }) {
  return (
    <section className="chofer-page">
      <div className="chofer-page__header">
        <span>Dashboard</span>
        <h1>{title}</h1>
        <p>
          Esta vista usa el sidebar de chofer. Después podemos conectar cada
          sección con viajes, cargas, rutas y reportes reales.
        </p>
      </div>

      <div className="chofer-page__grid">
        <article>
          <span>Viajes activos</span>
          <strong>3</strong>
        </article>
        <article>
          <span>Cargas asignadas</span>
          <strong>8</strong>
        </article>
        <article>
          <span>Reportes pendientes</span>
          <strong>1</strong>
        </article>
      </div>
    </section>
  );
}

export default DashboardTruckerPage;