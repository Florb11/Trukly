import { useEffect, useRef, useState } from "react";
import {
  FaCamera,
  FaEnvelope,
  FaIdBadge,
  FaLock,
  FaSave,
  FaUser,
} from "react-icons/fa";
import { fetchConToken } from "../utils/fetchConToken";
import "./AdminPerfilPage.css";

function AdminPerfilPage() {
  const [perfil, setPerfil] = useState(null);
  const [formPerfil, setFormPerfil] = useState({
    nombre: "",
    apellido: "",
    email: "",
  });
  const [formPassword, setFormPassword] = useState({
    password_actual: "",
    password_nueva: "",
    confirmar_password: "",
  });
  const [cargando, setCargando] = useState(true);
  const [guardandoPerfil, setGuardandoPerfil] = useState(false);
  const [guardandoPassword, setGuardandoPassword] = useState(false);
  const [subiendoFoto, setSubiendoFoto] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");

  const inputFotoRef = useRef(null);

  const cargarPerfil = async () => {
    try {
      setCargando(true);
      setError("");

      const resultado = await fetchConToken(
        "http://localhost:5000/api/perfil",
        {
          method: "GET",
        }
      );

      if (!resultado) return;

      const { respuesta, data } = resultado;

      if (!respuesta.ok) {
        throw new Error(
          data.mensaje || data.msg || "Error al cargar el perfil"
        );
      }

      setPerfil(data.perfil);

      setFormPerfil({
        nombre: data.perfil.nombre || "",
        apellido: data.perfil.apellido || "",
        email: data.perfil.email || "",
      });
    } catch (error) {
      setError(error.message);
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarPerfil();
  }, []);

  const handlePerfilChange = (e) => {
    const { name, value } = e.target;

    setFormPerfil((formActual) => ({
      ...formActual,
      [name]: value,
    }));
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;

    setFormPassword((formActual) => ({
      ...formActual,
      [name]: value,
    }));
  };

  const guardarPerfil = async (e) => {
    e.preventDefault();

    try {
      setGuardandoPerfil(true);
      setMensaje("");
      setError("");

      const resultado = await fetchConToken(
        "http://localhost:5000/api/perfil",
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formPerfil),
        }
      );

      if (!resultado) return;

      const { respuesta, data } = resultado;

      if (!respuesta.ok) {
        throw new Error(
          data.mensaje || data.msg || "Error al actualizar el perfil"
        );
      }

      setPerfil(data.perfil);
      setMensaje(data.mensaje || "Perfil actualizado correctamente");
    } catch (error) {
      setError(error.message);
    } finally {
      setGuardandoPerfil(false);
    }
  };

  const cambiarPassword = async (e) => {
    e.preventDefault();

    try {
      setGuardandoPassword(true);
      setMensaje("");
      setError("");

      const resultado = await fetchConToken(
        "http://localhost:5000/api/perfil/password",
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formPassword),
        }
      );

      if (!resultado) return;

      const { respuesta, data } = resultado;

      if (!respuesta.ok) {
        throw new Error(
          data.mensaje || data.msg || "Error al cambiar la contraseña"
        );
      }

      setMensaje(data.mensaje || "Contraseña actualizada correctamente");

      setFormPassword({
        password_actual: "",
        password_nueva: "",
        confirmar_password: "",
      });
    } catch (error) {
      setError(error.message);
    } finally {
      setGuardandoPassword(false);
    }
  };

  const seleccionarFoto = () => {
    inputFotoRef.current?.click();
  };

  const subirFoto = async (e) => {
    const archivo = e.target.files?.[0];

    if (!archivo) return;

    const formData = new FormData();
    formData.append("foto", archivo);

    try {
      setSubiendoFoto(true);
      setMensaje("");
      setError("");

      const token = localStorage.getItem("token");

      const respuesta = await fetch(
        "http://localhost:5000/api/perfil/foto",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        }
      );

      const data = await respuesta.json();

      if (!respuesta.ok) {
        throw new Error(
          data.mensaje || data.msg || "Error al subir la foto"
        );
      }

      setPerfil((perfilActual) => ({
        ...perfilActual,
        foto_perfil: data.foto_perfil,
      }));

      setMensaje(data.mensaje || "Foto actualizada correctamente");
    } catch (error) {
      setError(error.message);
    } finally {
      setSubiendoFoto(false);
      e.target.value = "";
    }
  };

  const obtenerFotoPerfil = () => {
    if (!perfil?.foto_perfil) return null;

    return `http://localhost:5000${perfil.foto_perfil}`;
  };

  if (cargando) {
    return (
      <section className="admin-perfil-page">
        <p className="admin-message">Cargando perfil...</p>
      </section>
    );
  }

  if (!perfil) {
    return (
      <section className="admin-perfil-page">
        <p className="admin-message admin-message--error">
          No se pudo cargar el perfil.
        </p>
      </section>
    );
  }

  return (
    <section className="admin-perfil-page">
      <div className="admin-perfil-header">
        <div>
          <span>Cuenta</span>
          <h1>Mi perfil</h1>
          <p>
            Consultá y actualizá tus datos personales y la seguridad de tu
            cuenta.
          </p>
        </div>

        <div className="admin-perfil-header__icon">
          <FaUser />
        </div>
      </div>

      {mensaje && (
        <p className="admin-message admin-message--ok">{mensaje}</p>
      )}

      {error && (
        <p className="admin-message admin-message--error">{error}</p>
      )}

      <div className="admin-perfil-grid">
        <article className="admin-perfil-card admin-perfil-card--identity">
          <div className="admin-perfil-avatar-wrap">
            <div className="admin-perfil-avatar">
              {obtenerFotoPerfil() ? (
                <img
                  src={obtenerFotoPerfil()}
                  alt="Foto de perfil"
                />
              ) : (
                <span>
                  {perfil.nombre?.charAt(0).toUpperCase() || "A"}
                </span>
              )}
            </div>

            <button
              type="button"
              className="admin-perfil-photo-button"
              onClick={seleccionarFoto}
              disabled={subiendoFoto}
            >
              <FaCamera />
              {subiendoFoto ? "Subiendo..." : "Cambiar foto"}
            </button>

            <input
              ref={inputFotoRef}
              type="file"
              accept=".png,.jpg,.jpeg,.webp"
              onChange={subirFoto}
              hidden
            />
          </div>

          <h2>
            {perfil.nombre} {perfil.apellido}
          </h2>

          <span className="admin-perfil-role">{perfil.rol}</span>

          <div className="admin-perfil-account-data">
            <div>
              <FaUser />
              <span>Usuario</span>
              <strong>{perfil.username}</strong>
            </div>

            <div>
              <FaIdBadge />
              <span>Legajo</span>
              <strong>{perfil.legajo || "-"}</strong>
            </div>

            <div>
              <FaEnvelope />
              <span>Email</span>
              <strong>{perfil.email}</strong>
            </div>
          </div>
        </article>

        <div className="admin-perfil-column">
          <article className="admin-perfil-card">
            <div className="admin-perfil-card__header">
              <div>
                <h2>Datos personales</h2>
                <span>Actualizá tu información de contacto</span>
              </div>

              <FaUser />
            </div>

            <form
              className="admin-perfil-form"
              onSubmit={guardarPerfil}
            >
              <div className="admin-perfil-form__row">
                <label>
                  <span>Nombre</span>
                  <input
                    type="text"
                    name="nombre"
                    value={formPerfil.nombre}
                    onChange={handlePerfilChange}
                  />
                </label>

                <label>
                  <span>Apellido</span>
                  <input
                    type="text"
                    name="apellido"
                    value={formPerfil.apellido}
                    onChange={handlePerfilChange}
                  />
                </label>
              </div>

              <label>
                <span>Email</span>
                <input
                  type="email"
                  name="email"
                  value={formPerfil.email}
                  onChange={handlePerfilChange}
                />
              </label>

              <div className="admin-perfil-form__footer">
                <button
                  type="submit"
                  disabled={guardandoPerfil}
                >
                  <FaSave />
                  {guardandoPerfil
                    ? "Guardando..."
                    : "Guardar cambios"}
                </button>
              </div>
            </form>
          </article>

          <article className="admin-perfil-card">
            <div className="admin-perfil-card__header">
              <div>
                <h2>Seguridad</h2>
                <span>Cambiá la contraseña de tu cuenta</span>
              </div>

              <FaLock />
            </div>

            <form
              className="admin-perfil-form"
              onSubmit={cambiarPassword}
            >
              <label>
                <span>Contraseña actual</span>
                <input
                  type="password"
                  name="password_actual"
                  value={formPassword.password_actual}
                  onChange={handlePasswordChange}
                />
              </label>

              <div className="admin-perfil-form__row">
                <label>
                  <span>Nueva contraseña</span>
                  <input
                    type="password"
                    name="password_nueva"
                    value={formPassword.password_nueva}
                    onChange={handlePasswordChange}
                  />
                </label>

                <label>
                  <span>Confirmar contraseña</span>
                  <input
                    type="password"
                    name="confirmar_password"
                    value={formPassword.confirmar_password}
                    onChange={handlePasswordChange}
                  />
                </label>
              </div>

              <div className="admin-perfil-form__footer">
                <button
                  type="submit"
                  disabled={guardandoPassword}
                >
                  <FaLock />
                  {guardandoPassword
                    ? "Actualizando..."
                    : "Cambiar contraseña"}
                </button>
              </div>
            </form>
          </article>
        </div>
      </div>
    </section>
  );
}

export default AdminPerfilPage;