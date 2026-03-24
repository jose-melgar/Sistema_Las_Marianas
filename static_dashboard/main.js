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
    series: [{ type: "bar", data: values }]
  };
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

  document.getElementById("sumA").textContent = j.summaries.a || "";
  document.getElementById("sumB").textContent = j.summaries.b || "";
  document.getElementById("sumC1").textContent = j.summaries.c1 || "";
  document.getElementById("sumC2").textContent = j.summaries.c2 || "";
}

btnLoad.addEventListener("click", loadDashboard);

(async function init() {
  await loadObras();
  await loadDashboard();
})();