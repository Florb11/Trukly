const ESTADOS_REPORTE = {
  pendiente: { label: "Pendiente", clase: "pendiente" },
  "en revision": { label: "En revisión", clase: "en-reparacion" },
  resuelto: { label: "Resuelto", clase: "resuelto" },
  cancelado: { label: "Cancelado", clase: "cancelado" },
};

export function estadoReporte(valor) {
  const normalizado = String(valor || "").trim().toLowerCase();
  const estado = normalizado === "en_reparacion" ? "en revision" : normalizado;
  return { valor: estado, ...(ESTADOS_REPORTE[estado] || { label: "Estado desconocido", clase: "desconocido" }) };
}
