import "./BannerSection.css";

function BannerSection() {
  return (
    <section id="roles" className="banner-section">
      <div className="banner-overlay">
        <span>Roles del sistema</span>
        <h2>Una plataforma pensada para cada parte de la operación.</h2>

        <div className="role-list">
          <p>Choferes</p>
          <p>Mecánicos</p>
          <p>Operadores logísticos</p>
          <p>Administradores</p>
        </div>
      </div>
    </section>
  );
}

export default BannerSection;