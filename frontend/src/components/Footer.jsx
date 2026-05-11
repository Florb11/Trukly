import { FaGithub } from "react-icons/fa";
import "./Footer.css";

function Footer() {
  return (
    <footer className="trukly-footer">
      <div className="footer-brand">
        <h3>Trukly</h3>
        <p>Sistema de gestión logística para transporte y operaciones.</p>
      </div>

      <div className="footer-devs">
        <p>Desarrollado por</p>
        <span>Florencia Bergman y Juan Del Pozo</span>
      </div>

      <div className="footer-social">
        <a
          href="https://github.com/Florb11/Trukly"
          target="_blank"
          rel="noreferrer"
          aria-label="GitHub"
        >
          <FaGithub />
        </a>
      </div>
    </footer>
  );
}

export default Footer;