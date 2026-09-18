import "./DashboardBarChart.css";

function DashboardBarChart({ data = [] }) {
  const chartData = data.map((item) => ({
    ...item,
    value: Number(item.value) || 0,
  }));
  const maxValue = Math.max(...chartData.map((item) => item.value), 1);
  const hasActivity = chartData.some((item) => item.value > 0);

  return (
    <div className="dashboard-bar-chart" role="img" aria-label="Actividad operativa de los ultimos 7 dias">
      {!hasActivity && (
        <p className="dashboard-bar-chart__empty">Sin viajes en los últimos 7 días</p>
      )}
      <div className="dashboard-bar-chart__plot">
        {chartData.map((item) => {
          const height = item.value === 0 ? 0 : Math.max((item.value / maxValue) * 100, 10);

          return (
            <div className="dashboard-bar-chart__item" key={item.date || item.label}>
              <span className="dashboard-bar-chart__value">{item.value}</span>
              <div className="dashboard-bar-chart__track">
                <span className="dashboard-bar-chart__bar" style={{ height: `${height}%` }} />
              </div>
              <span className="dashboard-bar-chart__label">{item.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default DashboardBarChart;
