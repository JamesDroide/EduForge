/**
=========================================================
* Material Dashboard 2 React - v2.1.0
=========================================================

* Product Page: https://www.creative-tim.com/product/nextjs-material-dashboard-pro
* Copyright 2023 Creative Tim (https://www.creative-tim.com)

Coded by www.creative-tim.com

 =========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*/

function configs(labels, datasets) {
  return {
    data: {
      labels,
      datasets: [
        {
          label: datasets.label,
          tension: 0,
          pointRadius: 5,
          pointBorderColor: "transparent",
          pointBackgroundColor: "rgba(255, 255, 255, .8)",
          borderColor: "rgba(255, 255, 255, .8)",
          borderWidth: 4,
          backgroundColor: "transparent",
          fill: true,
          data: datasets.data,
          maxBarThickness: 6,
          // Agregar datos adicionales para tooltips
          counts: datasets.counts || [],
          totals: datasets.totals || [],
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          mode: "index",
          intersect: false,
          backgroundColor: "rgba(0,0,0,0.8)",
          titleColor: "#fff",
          bodyColor: "#fff",
          borderColor: "rgba(255,255,255,0.3)",
          borderWidth: 1,
          displayColors: true,
          callbacks: {
            title: function (tooltipItems) {
              return `${tooltipItems[0].label}`;
            },
            label: function (context) {
              const percentage = context.parsed.y;
              const counts = context.dataset.counts || [];
              const totals = context.dataset.totals || [];
              const studentsAtRisk = counts[context.dataIndex] || 0;
              const totalStudents = totals[context.dataIndex] || 0;

              return [
                `Riesgo: ${percentage}%`,
                `Estudiantes en riesgo: ${studentsAtRisk}`,
                `Total estudiantes: ${totalStudents}`,
              ];
            },
          },
        },
      },
      interaction: {
        intersect: false,
        mode: "index",
      },
      scales: {
        y: {
          grid: {
            drawBorder: false,
            display: true,
            drawOnChartArea: true,
            drawTicks: false,
            borderDash: [5, 5],
            color: "rgba(255, 255, 255, .2)",
          },
          ticks: {
            display: true,
            color: "#f8f9fa",
            padding: 10,
            font: {
              size: 14,
              weight: 300,
              family: "Roboto",
              style: "normal",
              lineHeight: 2,
            },
            callback: function (value) {
              return value + "%";
            },
          },
          title: {
            display: true,
            text: "Porcentaje de Riesgo",
            color: "#f8f9fa",
            font: {
              size: 12,
              weight: "bold",
            },
          },
        },
        x: {
          grid: {
            drawBorder: false,
            display: false,
            drawOnChartArea: false,
            drawTicks: false,
            borderDash: [5, 5],
          },
          ticks: {
            display: true,
            color: "#f8f9fa",
            padding: 10,
            font: {
              size: 14,
              weight: 300,
              family: "Roboto",
              style: "normal",
              lineHeight: 2,
            },
          },
          title: {
            display: true,
            text: "Meses",
            color: "#f8f9fa",
            font: {
              size: 12,
              weight: "bold",
            },
          },
        },
      },
    },
  };
}

export default configs;
