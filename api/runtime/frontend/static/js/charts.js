/**
 * SkillPulse Bharat - Chart.js Visualizations
 * Team: Syntax Society
 */

const chartRegistry = {};

function destroyChartIfExists(canvasId) {
  if (chartRegistry[canvasId]) {
    chartRegistry[canvasId].destroy();
    delete chartRegistry[canvasId];
  }
}

/**
 * Top in-demand skills bar chart
 */
function renderTopSkillsChart(canvasId, dataItems) {
  destroyChartIfExists(canvasId);
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  const labels = dataItems.map(d => d.skill);
  const values = dataItems.map(d => d.percentage);

  chartRegistry[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Job Postings Demand (%)',
        data: values,
        backgroundColor: 'rgba(99, 102, 241, 0.75)',
        hoverBackgroundColor: 'rgba(99, 102, 241, 1)',
        borderColor: '#6366f1',
        borderWidth: 1,
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#182235',
          titleColor: '#ffffff',
          bodyColor: '#a5b4fc',
          borderColor: 'rgba(255, 255, 255, 0.1)',
          borderWidth: 1,
          callbacks: {
            label: (ctx) => ` Demand: ${ctx.raw}% of Indian tech jobs`
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', size: 11 } }
        },
        y: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: {
            color: '#94a3b8',
            font: { family: 'Plus Jakarta Sans', size: 11 },
            callback: (v) => v + '%'
          }
        }
      }
    }
  });
}

/**
 * Industry Distribution Doughnut Chart
 */
function renderIndustrySpreadChart(canvasId, industryData) {
  destroyChartIfExists(canvasId);
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  const labels = industryData.slice(0, 6).map(d => d.industry);
  const values = industryData.slice(0, 6).map(d => d.percentage);

  const colors = [
    '#6366f1', '#06b6d4', '#10b981', '#f59e0b', '#a855f7', '#ec4899'
  ];

  chartRegistry[canvasId] = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: colors,
        borderColor: '#111827',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '68%',
      plugins: {
        legend: {
          position: 'right',
          labels: {
            color: '#cbd5e1',
            font: { family: 'Plus Jakarta Sans', size: 11 },
            boxWidth: 12,
            padding: 10
          }
        },
        tooltip: {
          backgroundColor: '#182235',
          borderColor: 'rgba(255, 255, 255, 0.1)',
          borderWidth: 1,
          callbacks: {
            label: (ctx) => ` ${ctx.label}: ${ctx.raw}%`
          }
        }
      }
    }
  });
}

/**
 * Skill Demand Trend Line Chart (Separates Observed vs Forecasted)
 */
function renderSkillTrendChart(canvasId, historicalPoints, forecastPoints) {
  destroyChartIfExists(canvasId);
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  // Combine quarters
  const quarters = [];
  const histData = [];
  const foreData = [];

  historicalPoints.forEach(p => {
    quarters.push(p.quarter);
    histData.push(p.count);
    foreData.push(null);
  });

  // Connect last historical point to forecast line
  if (historicalPoints.length > 0 && forecastPoints.length > 0) {
    const lastHist = historicalPoints[historicalPoints.length - 1];
    foreData[foreData.length - 1] = lastHist.count;
  }

  forecastPoints.forEach(p => {
    quarters.push(p.quarter + " (Forecast)");
    histData.push(null);
    foreData.push(p.count);
  });

  chartRegistry[canvasId] = new Chart(ctx, {
    type: 'line',
    data: {
      labels: quarters,
      datasets: [
        {
          label: 'Observed Historical Demand',
          data: histData,
          borderColor: '#6366f1',
          backgroundColor: 'rgba(99, 102, 241, 0.1)',
          fill: true,
          tension: 0.35,
          borderWidth: 3,
          pointBackgroundColor: '#6366f1',
          pointRadius: 5
        },
        {
          label: 'Estimated Future Forecast',
          data: foreData,
          borderColor: '#06b6d4',
          borderDash: [6, 4],
          backgroundColor: 'rgba(6, 182, 212, 0.08)',
          fill: true,
          tension: 0.35,
          borderWidth: 3,
          pointBackgroundColor: '#06b6d4',
          pointRadius: 5
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            color: '#cbd5e1',
            font: { family: 'Plus Jakarta Sans', size: 12 },
            usePointStyle: true
          }
        },
        tooltip: {
          backgroundColor: '#182235',
          titleColor: '#ffffff',
          borderColor: 'rgba(255, 255, 255, 0.1)',
          borderWidth: 1,
          callbacks: {
            label: (ctx) => ` ${ctx.dataset.label}: ${ctx.raw} mentions`
          }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', size: 11 } }
        },
        y: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', size: 11 } }
        }
      }
    }
  });
}

/**
 * Skill Gap Radar Chart
 */
function renderSkillGapRadarChart(canvasId, pillars, benchmarkScores, userScores) {
  destroyChartIfExists(canvasId);
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  chartRegistry[canvasId] = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: pillars,
      datasets: [
        {
          label: 'Market Role Benchmark',
          data: benchmarkScores,
          borderColor: 'rgba(255, 255, 255, 0.4)',
          backgroundColor: 'rgba(255, 255, 255, 0.05)',
          borderWidth: 1.5,
          pointRadius: 3
        },
        {
          label: 'Your Current Profile',
          data: userScores,
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.25)',
          borderWidth: 2.5,
          pointBackgroundColor: '#10b981',
          pointRadius: 5
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'bottom',
          labels: { color: '#cbd5e1', font: { family: 'Plus Jakarta Sans', size: 11 } }
        }
      },
      scales: {
        r: {
          angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
          grid: { color: 'rgba(255, 255, 255, 0.08)' },
          pointLabels: {
            color: '#cbd5e1',
            font: { family: 'Plus Jakarta Sans', size: 11, weight: 'bold' }
          },
          ticks: { display: false, max: 100, min: 0 }
        }
      }
    }
  });
}
