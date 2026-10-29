import { useEffect, useState } from "react";
import { fetchConToken } from "../utils/fetchConToken";
import "./DetalleReporteModal.css";

function DetalleReporteModal({ reporte: reporteInicial, onClose }) {
    const [detalle, setDetalle] = useState(null);
    const [error, setError] = useState("");
    const idReporte = reporteInicial?.id_reporte;
    const faltanNombres = Boolean(reporteInicial && (!reporteInicial.camion_nombre || !reporteInicial.chofer_nombre || (reporteInicial.Mecanico_Usuario_idUsuario && !reporteInicial.mecanico_nombre)));
    useEffect(() => {
        if (!idReporte || !faltanNombres) return;
        const controlador = new AbortController();
        fetchConToken(`${import.meta.env.VITE_API_URL || "http://localhost:5000"}/api/reportes/${idReporte}`, {
            method: "GET", signal: controlador.signal,
        }).then((resultado) => {
            if (!resultado || controlador.signal.aborted) return;
            if (!resultado.respuesta.ok) throw new Error(resultado.data.mensaje || "No se pudo obtener el detalle del reporte.");
            if (!resultado.data.reporte) throw new Error("No se recibió el detalle del reporte.");
            setDetalle(resultado.data.reporte);
            setError("");
        }).catch((errorCarga) => {
            if (!controlador.signal.aborted) setError(errorCarga.message);
        });
        return () => controlador.abort();
    }, [idReporte, faltanNombres]);
    if (!reporteInicial) return null;
    const reporte = detalle?.id_reporte === idReporte ? { ...reporteInicial, ...detalle } : reporteInicial;
    const cargando = faltanNombres && detalle?.id_reporte !== idReporte && !error;

    return (
        <div className="detalle-reporte-backdrop">
            <div className="detalle-reporte-modal">
                <div className="detalle-reporte-header">
                    <div>
                        <span>Detalle de reporte</span>
                        <h2>Reporte #{reporte.id_reporte}</h2>
                        <p>{reporte.fecha_hora}</p>
                    </div>

                    <button
                        type="button"
                        className="detalle-reporte-close"
                        onClick={onClose}
                    >
                        ×
                    </button>
                </div>

                <div className="detalle-reporte-body">
                    <div className="detalle-reporte-section">
                        <h3>Datos del reporte</h3>
                        {error && <p role="alert">{error}</p>}

                        <div className="detalle-reporte-grid">
                            <div className="detalle-reporte-item">
                                <span>ID</span>
                                <p>#{reporte.id_reporte}</p>
                            </div>

                            <div className="detalle-reporte-item">
                                <span>Fecha y hora</span>
                                <p>{reporte.fecha_hora}</p>
                            </div>

                            <div className="detalle-reporte-item">
                                <span>Estado</span>
                                <p>{reporte.estado}</p>
                            </div>

                            <div className="detalle-reporte-item">
                                <span>Camión</span>
                                <p>{reporte.camion_nombre || (cargando ? "Cargando camión..." : "Camión sin datos")}</p>
                            </div>

                            <div className="detalle-reporte-item">
                                <span>Chofer</span>
                                <p>{reporte.chofer_nombre || (cargando ? "Cargando nombre..." : "Chofer sin datos")}</p>
                            </div>

                            <div className="detalle-reporte-item">
                                <span>Mecánico</span>
                                <p>
                                    {reporte.Mecanico_Usuario_idUsuario
                                        ? reporte.mecanico_nombre || (cargando ? "Cargando nombre..." : "Mecánico sin datos")
                                        : "Sin asignar"}
                                </p>
                            </div>
                        </div>
                    </div>

          {reporte.estado === "cancelado" && reporte.motivo_cancelacion && <div className="detalle-reporte-section"><h3>Motivo de cancelación</h3><p>{reporte.motivo_cancelacion}</p></div>}

                    <div className="detalle-reporte-section">
                        <h3>Descripción de la falla</h3>

                        <div className="detalle-reporte-description">
                            <p>{reporte.descripcion}</p>
                        </div>
                    </div>
                </div>

                <div className="detalle-reporte-footer">
                    <button
                        type="button"
                        className="detalle-reporte-btn"
                        onClick={onClose}
                    >
                        Cerrar
                    </button>
                </div>
            </div>
        </div>
    );
}

export default DetalleReporteModal;