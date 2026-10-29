import { FaUserCheck, FaUserSlash } from "react-icons/fa";
import ConfirmarAccionModal from "./ConfirmarAccionModal";

export default function ConfirmarEstadoUsuarioModal({ usuario, estadoDestino, onConfirm, onClose }) {
  const activar = estadoDestino === "activo";
  const pendiente = estadoDestino === "pendiente";
  const accion = activar ? "Activar usuario" : pendiente ? "Cambiar a pendiente" : "Desactivar usuario";
  return <ConfirmarAccionModal titulo={accion} textoConfirmar={accion} peligro={!activar}
    descripcion={<>¿Confirmás que querés {activar ? "activar" : pendiente ? "dejar pendiente" : "desactivar"} a <strong>{usuario.nombre} {usuario.apellido}</strong>?</>}
    identidad={<><span>@{usuario.username}</span><span>{usuario.rol}</span></>}
    detalle={activar ? "El usuario tendrá acceso al sistema con los permisos correspondientes a su rol." : "El usuario no podrá acceder al sistema mientras su cuenta no esté activa."}
    icono={activar ? <FaUserCheck aria-hidden="true" /> : <FaUserSlash aria-hidden="true" />}
    onConfirm={onConfirm} onClose={onClose} />;
}
