// ===========================
// Configurações e constantes
// ===========================
const UPDATE_INTERVAL_MS = 2000;   // Intervalo de atualização
const MAX_DATA_POINTS = 10;        // Máximo de pontos nos gráficos
const defaultCpuColor = '#00bfff';
const defaultMemColor = '#00ff88';
const netSentColor = '#ffaa00';
const netRecvColor = '#ff0055';

let updateIntervalId = null;       // ID do setInterval
let paused = false;                // Estado pausado
let prevBytesSent = null;          // Leitura anterior (bytes enviados)
let prevBytesRecv = null;          // Leitura anterior (bytes recebidos)

let CPU_THRESHOLD = 80;            // Inicial padrão
let MEM_THRESHOLD = 80;            // Inicial padrão

// ===========================
// Cache de elementos do DOM
// ===========================
const elThrCpu = document.getElementById('thrCpu');
const elThrMem = document.getElementById('thrMem');
const elBtnPause = document.getElementById('btnPause');
const elAlertBanner = document.getElementById('alertBanner');
const elScanResult = document.getElementById('scanResult');
const elPacketResult = document.getElementById('packetResult');

// ===========================
// Inicialização dos gráficos
// ===========================
const cpuChart = new Chart(document.getElementById('graficoCPU'), {
    type: 'line',
    data: { labels: [], datasets: [{ label: 'Uso de CPU (%)', data: [], borderColor: defaultCpuColor, tension: 0.3 }] },
    options: { responsive: true, scales: { y: { beginAtZero: true, max: 100 } } }
});

const memChart = new Chart(document.getElementById('graficoMemoria'), {
    type: 'line',
    data: { labels: [], datasets: [{ label: 'Uso de Memória (%)', data: [], borderColor: defaultMemColor, tension: 0.3 }] },
    options: { responsive: true, scales: { y: { beginAtZero: true, max: 100 } } }
});

const netChart = new Chart(document.getElementById('graficoRede'), {
    type: 'line',
    data: { labels: [], datasets: [
        { label: 'Bytes Enviados (KB/s)', data: [], borderColor: netSentColor, tension: 0.3 },
        { label: 'Bytes Recebidos (KB/s)', data: [], borderColor: netRecvColor, tension: 0.3 }
    ]},
    options: { responsive: true, scales: { y: { beginAtZero: true } } }
});

// ===========================
// Funções utilitárias
// ===========================
function showBanner(message, level='warn') {
    elAlertBanner.textContent = message;
    elAlertBanner.className = `alert-banner visible ${level}`;
}

function hideBanner() {
    elAlertBanner.textContent = '';
    elAlertBanner.className = 'alert-banner';
}

function getThresholds() {
    CPU_THRESHOLD = parseInt(elThrCpu.value) || CPU_THRESHOLD;
    MEM_THRESHOLD = parseInt(elThrMem.value) || MEM_THRESHOLD;
}

// ===========================
// Funções de alertas
// ===========================
function handleAlerts(data) {
    getThresholds();

    const cpu = Number(data.cpu);
    const mem = Number(data.memory);

    if (cpu >= CPU_THRESHOLD) {
        cpuChart.data.datasets[0].borderColor = '#ff4c4c';
        showBanner(`ALERTA: CPU alta — ${cpu}% (limite ${CPU_THRESHOLD}%)`, 'crit');
    } else {
        cpuChart.data.datasets[0].borderColor = defaultCpuColor;
        if (mem < MEM_THRESHOLD) hideBanner();
    }

    if (mem >= MEM_THRESHOLD) {
        memChart.data.datasets[0].borderColor = '#ff4c4c';
        showBanner(`ALERTA: Memória alta — ${mem}% (limite ${MEM_THRESHOLD}%)`, 'crit');
    } else {
        memChart.data.datasets[0].borderColor = defaultMemColor;
        if (cpu < CPU_THRESHOLD) hideBanner();
    }
}

// ===========================
// Funções de atualização de dados
// ===========================
async function updateData() {
    try {
        const resp = await fetch('/system_data');
        if (!resp.ok) throw new Error('Resposta não OK');
        const data = await resp.json();

        const now = new Date().toLocaleTimeString();

        // CPU e memória
        cpuChart.data.labels.push(now);
        cpuChart.data.datasets[0].data.push(data.cpu);
        memChart.data.labels.push(now);
        memChart.data.datasets[0].data.push(data.memory);

        handleAlerts(data);

        // Rede
        const sent = Number(data.bytes_sent);
        const recv = Number(data.bytes_received);

        netChart.data.labels.push(now);
        if (prevBytesSent === null) {
            netChart.data.datasets[0].data.push(0);
            netChart.data.datasets[1].data.push(0);
        } else {
            const deltaSent = Math.max(0, sent - prevBytesSent);
            const deltaRecv = Math.max(0, recv - prevBytesRecv);
            const seconds = UPDATE_INTERVAL_MS / 1000;
            netChart.data.datasets[0].data.push(Number((deltaSent / seconds / 1024).toFixed(2)));
            netChart.data.datasets[1].data.push(Number((deltaRecv / seconds / 1024).toFixed(2)));
        }

        prevBytesSent = sent;
        prevBytesRecv = recv;

        // Limitar histórico de pontos
        [cpuChart, memChart, netChart].forEach(chart => {
            if (chart.data.labels.length > MAX_DATA_POINTS) {
                chart.data.labels.shift();
                chart.data.datasets.forEach(ds => ds.data.shift());
            }
            chart.update();
        });

    } catch (err) {
        console.error('Erro ao atualizar dados:', err);
        showBanner('Erro ao buscar dados do servidor', 'crit');
    }
}

function resetCharts() {
    [cpuChart, memChart, netChart].forEach(chart => {
        chart.data.labels = [];
        chart.data.datasets.forEach(ds => ds.data = []);
        chart.update();
    });

    prevBytesSent = null;
    prevBytesRecv = null;
    hideBanner();
}

// ===========================
// Controle de atualização automática
// ===========================
function startUpdating() {
    if (updateIntervalId) return;

    getThresholds();
    updateData();
    updateIntervalId = setInterval(updateData, UPDATE_INTERVAL_MS);
    paused = false;
    elBtnPause.textContent = 'Pausar';
}

function stopUpdating() {
    if (updateIntervalId) clearInterval(updateIntervalId);
    updateIntervalId = null;
    paused = true;
    elBtnPause.textContent = 'Retomar';
}

function togglePause() {
    if (paused) startUpdating(); else stopUpdating();
}

// ===========================
// Funções de varredura e captura
// ===========================
async function runScan() {
    const target = document.getElementById('target').value || 'localhost';
    elScanResult.textContent = "Executando scan...";
    try {
        const resp = await fetch(`/scan?target=${encodeURIComponent(target)}`);
        const data = await resp.json();
        elScanResult.textContent = data.status === "ok" ? data.output : "Erro: " + data.message;
    } catch (err) {
        elScanResult.textContent = 'Erro ao executar scan.';
        console.error(err);
    }
}

async function capturePackets() {
    elPacketResult.textContent = "Capturando pacotes por 10 segundos...";
    try {
        const resp = await fetch('/packets');
        const data = await resp.json();
        elPacketResult.textContent = data.packets && data.packets.length ? data.packets.join("\n") : "Nenhum pacote capturado.";
    } catch (err) {
        elPacketResult.textContent = 'Erro ao capturar pacotes.';
        console.error(err);
    }
}

// ===========================
// Inicialização automática
// ===========================
startUpdating();
