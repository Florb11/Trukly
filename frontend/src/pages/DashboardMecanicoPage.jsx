import "./DashboardMecanicoPage.css";

function DashboardMecanicoPage() {
  return (
    <section className="mecanico-dashboard">
      <div className="mecanico-dashboard__header">
        <span>Panel de mecánico</span>
        <h1>Mantenimiento</h1>
        <p>
          Desde acá el mecánico va a poder revisar reportes de fallas,
          controlar reparaciones pendientes y marcar trabajos como resueltos.
        </p>
      </div>

      <div className="mecanico-dashboard__cards">
        <article className="mecanico-card">
          <span>Reportes asignados</span>
          <strong>0</strong>
          <p>Fallas pendientes de revisión.</p>
        </article>

        <article className="mecanico-card">
          <span>En reparación</span>
          <strong>0</strong>
          <p>Trabajos que están en proceso.</p>
        </article>

        <article className="mecanico-card">
          <span>Resueltos</span>
          <strong>0</strong>
          <p>Reparaciones finalizadas.</p>
        </article>
      </div>
    </section>
  );
}

export default DashboardMecanicoPage;