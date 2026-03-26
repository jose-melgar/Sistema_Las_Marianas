const API = "http://127.0.0.1:8000/api";

const obraSelect = document.getElementById("obraSelect");
const yearInput = document.getElementById("yearInput");
const monthInput = document.getElementById("monthInput");
const btnLoad = document.getElementById("btnLoad");
const kpisEl = document.getElementById("kpis");

const chartA = echarts.init(document.getElementById("chartA"));
const chartB = echarts.init(document.getElementById("chartB"));
const chartC1 = echarts.init(document.getElementById("chartC1"));
const chartC2 = echarts.init(document.getElementById("chartC2"));
const chartD = echarts.init(document.getElementById("chartD"));
const chartE = echarts.init(document.getElementById("chartE"));
const chartF = echarts.init(document.getElementById("chartF"));

async function loadObras() {
  const r = await fetch(`${API}/options/obras`);
  const j = await r.json();
  obraSelect.innerHTML = "";
  (j.items || []).forEach(o => {
    const opt = document.createElement("option");
    opt.value = o; opt.textContent = o;
    obraSelect.appendChild(opt);
  });
}

function renderKpis(kpis) {
  const items = [
    ["Trabajadores", kpis.total_trabajadores],
    ["Activos", kpis.trabajadores_activos],
    ["Con EMO", kpis.con_emo],
    ["Sin EMO", kpis.sin_emo],
    ["Entregados Mes", kpis.emos_entregados_mes],
    ["Pendientes", kpis.emos_pendientes],
  ];
  kpisEl.innerHTML = items.map(([k,v]) => `<div class="kpi"><div>${k}</div><strong>${v ?? 0}</strong></div>`).join("");
}

function donutOption(title, labels, values) {
  const data = labels.map((l, i) => ({ name: l, value: values[i] || 0 }));
  return {
    tooltip: { trigger: "item" },
    legend: { bottom: 0 },
    series: [{
      type: "pie",
      radius: ["45%", "70%"],
      data
    }]
  };
}

function barOption(labels, values) {
  return {
    xAxis: { type: "value" },
    yAxis: { type: "category", data: labels },
    series: [{ type: "bar", data: values }],
    grid: {
      left: '8%',
      right: '8%',
      top: '10%',
      bottom: '15%'
    }
  };
}

// D: Perfiles de EMO
function renderChartD(labels, values) {
  chartD.setOption(donutOption("D", labels, values));
}

// E: Vigencia de EMOs
function renderChartE(labels, values) {
  chartE.setOption(barOption(labels, values));
}

// F: Triple dona
function renderChartF(fdata) {
  // Segmenta: mujeres (F), hombres (M), total
  const donutColors = [
    ["#4C78A8","#54A24B","#E45756","#F2CF5B"],
    ["#4C78A8","#54A24B","#E45756","#F2CF5B"],
    ["#4C78A8","#54A24B","#E45756","#F2CF5B"]
  ];
  chartF.clear();

  // Helper para mostrar datos o "Sin Datos"
  function completeData(labels, values) {
    if (!labels || labels.length === 0 || (values && values.every(v => v === 0))) {
      return [{value: 1, name: "Sin Datos"}];
    }
    return labels.map((l, i) => ({ value: values[i] || 0, name: l }));
  }

  chartF.setOption({
    // La leyenda interactiva de ECharts (solo aquí)
    legend: {
      bottom: 10,
      data: (fdata.labels_total || []),
      itemGap: 24,
      // Si quieres, puedes poner 'horizontal', 'vertical', palettes, etc.
    },
    tooltip: { trigger: "item" },
    series: [
      {
        name: "Mujeres",
        type: "pie",
        center: ["18%", "52%"],   // más a la izquierda
        radius: ["50%", "80%"],
        label: { show: false },
        data: completeData(fdata.labels_f, fdata.values_f),
        color: donutColors[0]
      },
      {
        name: "Total",
        type: "pie",
        center: ["50%", "50%"],   // central
        radius: ["50%", "80%"],
        label: { show: false },
        data: completeData(fdata.labels_total, fdata.values_total),
        color: donutColors[1]
      },
      {
        name: "Hombres",
        type: "pie",
        center: ["82%", "52%"],   // más a la derecha
        radius: ["50%", "80%"],
        label: { show: false },
        data: completeData(fdata.labels_m, fdata.values_m),
        color: donutColors[2]
      }
    ]
  });
}

async function loadDashboard() {
  const obra = obraSelect.value;
  const year = yearInput.value;
  const month = monthInput.value;

  const r = await fetch(`${API}/dashboard?report_type=standard&obra=${encodeURIComponent(obra)}&year=${year}&month=${month}`);
  const j = await r.json();

  renderKpis(j.kpis);

  chartA.setOption(donutOption("A", j.charts.a.labels, j.charts.a.values));
  chartB.setOption(barOption(j.charts.b.labels, j.charts.b.values));
  chartC1.setOption(donutOption("C1", j.charts.c1.labels, j.charts.c1.values));
  chartC2.setOption(donutOption("C2", j.charts.c2.labels, j.charts.c2.values));
  renderChartD(j.charts.d.labels, j.charts.d.values);
  renderChartE(j.charts.e.labels, j.charts.e.values);
  renderChartF(j.charts.f);

  document.getElementById("sumA").textContent = j.summaries.a || "";
  document.getElementById("sumB").textContent = j.summaries.b || "";
  document.getElementById("sumC1").textContent = j.summaries.c1 || "";
  document.getElementById("sumC2").textContent = j.summaries.c2 || "";
  document.getElementById("sumD").textContent = j.summaries.d || "";
  document.getElementById("sumE").textContent = j.summaries.e || "";
  document.getElementById("sumF").textContent = j.summaries.f || "";
}

btnLoad.addEventListener("click", loadDashboard);

(async function init() {
  await loadObras();
  await loadDashboard();
})();