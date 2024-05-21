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

function configs(thresholdYValue) {
  return {
    initialData: {
      labels: [],
      datasets: [
        {
          label: "Crash probability",
          tension: 0,
          pointRadius: 2,
          borderColor: "transparent",
          borderWidth: 2,
          backgroundColor: "transparent",
          fill: true,
          data: [],
          maxBarThickness: 6,
          pointBackgroundColor: (ctx) => {
            const value = ctx.raw;
            return value < thresholdYValue ? 'green' : 'red';
          },
          segment: {
            borderColor: (ctx) => {
              const value = ctx.p0.parsed.y;
              return value < thresholdYValue ? 'green' : 'red';
            },
          },
        }
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            usePointStyle: true,
            boxWidth: 6,
            boxHeight: 6,
            generateLabels: function(chart) {
              return [
                {
                  text: 'Stable traffic',
                  fillStyle: 'green',
                  strokeStyle: 'green',
                  lineWidth: 2,
                  pointStyle: 'circle',
                  fontColor: 'white',
                },
                {
                  text: 'Car crash',
                  fillStyle: 'red',
                  strokeStyle: 'red',
                  lineWidth: 2,
                  pointStyle: 'circle',
                  fontColor: 'white',
                },
              ];
            },
          }
        },
      annotation: {
        annotations: {
          line1: {
            type: 'line',
            yMin: thresholdYValue,
            yMax: thresholdYValue,
            borderColor: 'white',
            borderWidth: 1,
            borderDash: [10, 5],
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
            drawTicks: true,
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
          },
          min: 0,  // Set minimum value for y-axis
          max: 1   // Set maximum value for y-axis
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
        },
      },
    },
  };
}

export default configs;
