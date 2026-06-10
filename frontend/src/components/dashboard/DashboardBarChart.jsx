import "./DashboardBarChart.css";

function DashboardBarChart({ data = [] }) {
  const maxValue = Math.max(...data.map((item) => item.value), 1);

  return (
    <div className="dashboard-bar-chart" role="img" aria-label="Actividad operativa de los ultimos 7 dias">
      <div className="dashboard-bar-chart__plot">
        {data.map((item) => {
          const height = item.value === 0 ? 6 : Math.max((item.value / maxValue) * 100, 10);

          return (
            <div className="dashboard-bar-chart__item" key={item.label}>
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