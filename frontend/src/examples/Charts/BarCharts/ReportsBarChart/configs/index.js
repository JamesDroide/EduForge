/**
=========================================================
* Material Dashboard 2  React - v2.2.0
=========================================================

* Product Page: https://www.creative-tim.com/product/material-dashboard-react
* Copyright 2023 Creative Tim (https://www.creative-tim.com)

Coded by www.creative-tim.com

 =========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*/

function configs(labels, datasets) {
  // Verificar si datasets es un array (múltiples meses) o un objeto (formato antiguo)
  const isMultipleDatasets = Array.isArray(datasets);

  let chartDatasets;

  if (isMultipleDatasets) {
    // Múltiples datasets (cada mes es una serie)
    chartDatasets = datasets.map((dataset) => ({
      label: dataset.label,
      tension: 0.4,
      borderWidth: 2,
      borderRadius: 6,
      borderSkipped: false,
      backgroundColor: dataset.backgroundColor || "rgba(255, 255, 255, 0.8)",
      borderColor: dataset.borderColor || dataset.backgroundColor || "rgba(255, 255, 255, 0.8)",
      data: dataset.data,
      maxBarThickness: 20,
      categoryPercentage: 0.6,
      barPercentage: 0.8,
    }));
  } else {
    // Dataset único (formato original)
    chartDatasets = [
      {
        label: datasets.label || "Datos",
        tension: 0.4,
        borderWidth: 0,
        borderRadius: 4,
        borderSkipped: false,
        backgroundColor: "rgba(255, 255, 255, 0.8)",
        data: datasets.data || [],
        maxBarThickness: 6,
      },
    ];
  }

  return {
    data: {
      labels,
      datasets: chartDatasets,
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: isMultipleDatasets,
          position: "top",
          labels: {
            color: "#fff",
            font: {
              size: 12,
              weight: "bold",
            },
            padding: 15,
            usePointStyle: true,
            pointStyle: "rect",
          },
        },
        tooltip: {
          mode: "point",
          intersect: true,
          backgroundColor: "rgba(0,0,0,0.8)",
          titleColor: "#fff",
          bodyColor: "#fff",
          borderColor: "rgba(255,255,255,0.3)",
          borderWidth: 1,
          displayColors: true,
          callbacks: {
            title: function (tooltipItems) {
              // Mostrar la fecha y el mes específico
              const datasetLabel = tooltipItems[0].dataset.label;
              const fecha = tooltipItems[0].label;
              return `${fecha} - ${datasetLabel}`;
            },
            label: function (context) {
              return `Asistencia: ${context.parsed.y}%`;
            },
            afterLabel: function (context) {
              // Información adicional opcional - detectar el día real de la fecha
              if (context.parsed.y > 0) {
                const fecha = context.label; // Obtener la fecha (ej: "09/02")
                const año = new Date().getFullYear(); // Usar el año actual

                try {
                  // Parsear la fecha en formato DD/MM
                  const [dia, mes] = fecha.split("/");
                  const fechaCompleta = new Date(año, parseInt(mes) - 1, parseInt(dia));

                  // Obtener el nombre del día en español
                  const diasSemana = [
                    "Domingo",
                    "Lunes",
                    "Martes",
                    "Miércoles",
                    "Jueves",
                    "Viernes",
                    "Sábado",
                  ];
                  const nombreDia = diasSemana[fechaCompleta.getDay()];

                  return `Día: ${nombreDia}`;
                } catch (error) {
                  return `Día: No disponible`;
                }
              }
              return null;
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
          beginAtZero: true,
          max: 100,
          grid: {
            drawBorder: false,
            display: true,
            drawOnChartArea: true,
            drawTicks: false,
            borderDash: [5, 5],
            color: "rgba(255, 255, 255, .2)",
          },
          ticks: {
            suggestedMin: 0,
            suggestedMax: 100,
            stepSize: 20,
            padding: 10,
            font: {
              size: 12,
              weight: 300,
              family: "Roboto",
              style: "normal",
              lineHeight: 2,
            },
            color: "#fff",
            callback: function (value) {
              return value + "%";
            },
          },
          title: {
            display: true,
            text: "Porcentaje de Asistencia",
            color: "#fff",
            font: {
              size: 14,
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
          },
          ticks: {
            display: true,
            color: "#f8f9fa",
            padding: 10,
            font: {
              size: 14,
              weight: "bold",
              family: "Roboto",
              style: "normal",
              lineHeight: 2,
            },
          },
          title: {
            display: true,
            text: "Días de la Semana",
            color: "#fff",
            font: {
              size: 14,
              weight: "bold",
            },
          },
        },
      },
    },
  };
}

export default configs;
