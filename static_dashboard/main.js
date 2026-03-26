const API = "http://127.0.0.1:8000/api";
let currentReportType = "standard";

const obraSelect = document.getElementById("obraSelect");
const yearInput = document.getElementById("yearInput");
const monthInput = document.getElementById("monthInput");
const btnLoad = document.getElementById("btnLoad");
const kpisEl = document.getElementById("kpis");
const currentTitleEl = document.getElementById("currentTitle");

// Paleta de Colores Pasteles con Contraste
const pastelTheme = [
    '#90caf9', // Azul (Fresco)
    '#ffab91', // Coral (Cálido)
    '#a5d6a7', // Verde (Fresco)
    '#ce93d8', // Púrpura (Cálido/Fresco)
    '#ffe082', // Ámbar (Cálido)
    '#80cbc4', // Turquesa (Fresco)
    '#f48fb1', // Rosa (Cálido)
    '#9fa8da'  // Índigo (Fresco)
];

const charts = {
    a: echarts.init(document.getElementById("chartA")),
    b: echarts.init(document.getElementById("chartB")),
    c1: echarts.init(document.getElementById("chartC1")),
    c2: echarts.init(document.getElementById("chartC2")),
    d: echarts.init(document.getElementById("chartD")),
    e: echarts.init(document.getElementById("chartE")),
    f: echarts.init(document.getElementById("chartF"))
};

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
  // Nuevas etiquetas solicitadas por el usuario
  const labels = {
    total_trabajadores: "Total Trabajadores",
    trabajadores_activos: "Trabajadores Activos",
    con_emo: "T. con EMO",
    sin_emo: "T. sin EMO",
    emos_entregados_mes: "EMOs Entregados",
    emos_pendientes: "EMOs Pendientes"
  };

  kpisEl.innerHTML = Object.entries(labels).map(([key, label]) => `
    <div class="kpi">
        <span class="kpi-label">${label}</span>
        <div class="kpi-value">${kpis[key] ?? 0}</div>
    </div>
  `).join("");
}

function donutOption(labels, values) {
  return {
    color: pastelTheme,
    tooltip: { trigger: "item" },
    legend: { bottom: 0, padding: 10, textStyle: { fontSize: 11 } },
    series: [{
      type: "pie",
      radius: ["45%", "70%"],
      label: { show: false },
      data: labels.map((l, i) => ({ name: l, value: values[i] || 0 }))
    }]
  };
}

function barOption(labels, values) {
  return {
    tooltip: { trigger: "axis" },
    xAxis: { type: "value" },
    yAxis: { type: "category", data: labels },
    series: [{ 
      type: "bar", 
      data: values, 
      itemStyle: { color: pastelTheme[0] }, // Azul pastel para barras
      barWidth: '60%' 
    }],
    grid: { left: '3%', right: '5%', bottom: '5%', top: '5%', containLabel: true }
  };
}

async function loadDashboard() {
  const obra = obraSelect.value;
  const year = yearInput.value;
  const month = monthInput.value;

  const url = `${API}/dashboard?report_type=${currentReportType}&obra=${encodeURIComponent(obra)}&year=${year}&month=${month}`;
  const r = await fetch(url);
  const j = await r.json();

  renderKpis(j.kpis);

  charts.a.setOption(donutOption(j.charts.a.labels, j.charts.a.values));
  charts.b.setOption(barOption(j.charts.b.labels, j.charts.b.values));
  charts.c1.setOption(donutOption(j.charts.c1.labels, j.charts.c1.values));
  charts.c2.setOption(donutOption(j.charts.c2.labels, j.charts.c2.values));
  charts.d.setOption(donutOption(j.charts.d.labels, j.charts.d.values));
  charts.e.setOption(barOption(j.charts.e.labels, j.charts.e.values));

  const fData = j.charts.f;
  charts.f.setOption({
    color: pastelTheme,
    tooltip: { trigger: "item" },
    legend: { bottom: 0 },
    series: [
        { name: 'Mujeres', type: 'pie', center: ['18%', '50%'], radius: ['40%', '65%'], label: {show: false}, data: fData.labels_f.map((l,i)=>({name:l, value:fData.values_f[i]})) },
        { name: 'Total', type: 'pie', center: ['50%', '50%'], radius: ['40%', '65%'], label: {show: false}, data: fData.labels_total.map((l,i)=>({name:l, value:fData.values_total[i]})) },
        { name: 'Hombres', type: 'pie', center: ['82%', '50%'], radius: ['40%', '65%'], label: {show: false}, data: fData.labels_m.map((l,i)=>({name:l, value:fData.values_m[i]})) }
    ]
  });

  ["a","b","c1","c2","d","e","f"].forEach(k => {
    document.getElementById(`sum${k.toUpperCase()}`).textContent = j.summaries[k] || "";
  });
}

// Listeners de Sidebar Derecha
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        // Actualizar viñeta activa
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentReportType = btn.dataset.type;
        
        // Extraer texto del span.btn-text para el título central
        const fullText = btn.querySelector('.btn-text').textContent;
        currentTitleEl.textContent = fullText;
        
        loadDashboard();
    });
});

btnLoad.addEventListener("click", loadDashboard);
window.addEventListener('resize', () => Object.values(charts).forEach(c => c.resize()));

(async function init() {
  await loadObras();
  await loadDashboard();
})();