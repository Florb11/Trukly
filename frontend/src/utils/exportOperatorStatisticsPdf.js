import pdfMake from "pdfmake/build/pdfmake.js";
import fonts from "pdfmake/build/vfs_fonts.js";

pdfMake.vfs = fonts;

const texto = (valor) => String(valor ?? "-");

const agregarTabla = (contenido, titulo, columnas, filas, anchos) => {
  contenido.push({ text: titulo, style: "seccion" });
  if (filas.length === 0) {
    contenido.push({ text: "Sin registros en este mes.", style: "vacio" });
    return;
  }
  contenido.push({
    table: {
      headerRows: 1,
      widths: anchos,
      body: [columnas.map((columna) => ({ text: columna, style: "cabecera" })), ...filas.map((fila) => fila.map(texto))],
    },
    layout: "lightHorizontalLines",
    margin: [0, 0, 0, 18],
  });
};

export const exportarEstadisticasOperadorPdf = async (estadisticas, mes) => {
  const [anio, numeroMes] = mes.split("-").map(Number);
  const nombreMes = new Intl.DateTimeFormat("es-AR", { month: "long", year: "numeric" }).format(new Date(anio, numeroMes - 1, 1));
  const resumen = estadisticas.resumen || {};
  const contenido = [
    { text: "Trukly", style: "marca" },
    { text: `Informe del operador · ${nombreMes}`, style: "titulo" },
    { text: `Generado el ${new Date().toLocaleString("es-AR")}`, style: "fecha" },
    { text: "Viajes con salida y reportes creados en el mes. Los reportes son de camiones vinculados a tus viajes. Los estados reflejan la situación actual, no el cierre histórico.", style: "nota" },
  ];

  agregarTabla(contenido, "Resumen", ["Indicador", "Cantidad"], [
    ["Viajes con salida", resumen.total_viajes ?? 0],
    ["En curso (estado actual)", resumen.viajes_en_curso ?? 0],
    ["Pendientes (estado actual)", resumen.viajes_pendientes ?? 0],
    ["Finalizados (estado actual)", resumen.viajes_finalizados ?? 0],
    ["Cancelados (estado actual)", resumen.viajes_cancelados ?? 0],
    ["Reportes pendientes", resumen.reportes_pendientes ?? 0],
    ["Reportes en revisión", resumen.reportes_en_revision ?? 0],
    ["Reportes resueltos", resumen.reportes_resueltos ?? 0],
  ], ["*", 65]);

  agregarTabla(contenido, "Choferes más usados", ["Chofer", "Viajes"],
    (estadisticas.choferes_mas_usados || []).map((fila) => [`${fila.nombre} ${fila.apellido}`, fila.total_viajes]), ["*", 70]);
  agregarTabla(contenido, "Camiones más usados", ["Matrícula", "Camión", "Viajes"],
    (estadisticas.camiones_mas_usados || []).map((fila) => [fila.matricula, `${fila.marca} ${fila.modelo}`, fila.total_viajes]), [85, "*", 70]);
  agregarTabla(contenido, "Viajes del mes", ["Salida", "Origen → destino", "Estado"],
    (estadisticas.ultimos_viajes || []).map((viaje) => [viaje.fecha_salida, `${viaje.origen} → ${viaje.destino}`, viaje.estado]), [70, "*", 75]);
  agregarTabla(contenido, "Reportes del mes", ["Fecha", "Reporte", "Estado"],
    (estadisticas.ultimos_reportes || []).map((reporte) => [reporte.fecha_hora?.slice(0, 16), `#${reporte.id_reporte} · Camión #${reporte.Camion_id_camion}: ${reporte.descripcion}`, reporte.estado]), [90, "*", 75]);

  const documento = {
    pageSize: "A4",
    pageMargins: [36, 40, 36, 42],
    content: contenido,
    defaultStyle: { font: "Roboto", fontSize: 9, color: "#172033" },
    styles: {
      marca: { fontSize: 11, bold: true, color: "#5b61dc", margin: [0, 0, 0, 6] },
      titulo: { fontSize: 18, bold: true, margin: [0, 0, 0, 4] },
      fecha: { fontSize: 8, color: "#64748b", margin: [0, 0, 0, 12] },
      nota: { fontSize: 9, color: "#475569", margin: [0, 0, 0, 14] },
      seccion: { fontSize: 12, bold: true, color: "#243b53", margin: [0, 12, 0, 8] },
      cabecera: { bold: true, color: "#243b53", fillColor: "#eef0ff" },
      vacio: { color: "#64748b", margin: [0, 0, 0, 12] },
    },
    footer: (pagina, total) => ({ text: `${pagina} / ${total}`, alignment: "right", margin: [0, 0, 36, 0], color: "#64748b", fontSize: 8 }),
  };

  await new Promise((resolve) => pdfMake.createPdf(documento).download(`trukly-operador-estadisticas-${mes}.pdf`, resolve));
};
