/* =========================
   Configurações e constantes
   ========================= */
const UPDATE_INTERVAL_MS = 2000;        // intervalo padrão (2s)
let updateIntervalId = null;           // id do setInterval
let paused = false;                    // estado pausado
let prevBytesSent = null;              // leitura anterior (bytes enviados)
let prevBytesRecv = null;              // leitura anterior (bytes recebidos)

/* Thresholds (padrão) — podem ser alterados via input na UI */
let THRESHOLD_CPU = parseInt(document?.getElementById?.('thrCpu')?.value || 80);
let THRESHOLD_MEM = parseInt(document?.getElementById?.('thrMem')?.value || 80);

/* Armazena cores padrão para restaurar depois do alerta */
const defaultCpuColor = '#00bfff';
const defaultMemColor = '#00ff88';

/* =========================
   Inicialização dos gráficos
   ========================= */
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
        { label: 'Bytes Enviados (KB/s)', data: [], borderColor: '#ffaa00', tension: 0.3 },
        { label: 'Bytes Recebidos (KB/s)', data: [], borderColor: '#ff0055', tension: 0.3 }
    ]},
    options: { responsive: true, scales: { y: { beginAtZero: true } } }
});

/* =========================
   Funções de controle (pause / resume / reset)
   ========================= */
function startUpdating() {
    // garante que não duplique intervalos
    if (updateIntervalId) return;
    // atualiza thresholds a partir dos inputs (caso usuário altere)
    THRESHOLD_CPU = parseInt(document.getElementById('thrCpu').value) || THRESHOLD_CPU;
    THRESHOLD_MEM = parseInt(document.getElementById('thrMem').value) || THRESHOLD_MEM;

    // chamada imediata para não esperar o primeiro intervalo
    atualizarDados();
    updateIntervalId = setInterval(atualizarDados, UPDATE_INTERVAL_MS);
    paused = false;
    document.getElementById('btnPause').textContent = 'Pausar';
}

function stopUpdating() {
    if (updateIntervalId) {
        clearInterval(updateIntervalId);
        updateIntervalId = null;
    }
    paused = true;
    document.getElementById('btnPause').textContent = 'Retomar';
}

function togglePause() {
    if (paused) startUpdating(); else stopUpdating();
}

function resetCharts() {
    // limpa labels e dados de cada gráfico
    [cpuChart, memChart, netChart].forEach(chart => {
        chart.data.labels = [];
        chart.data.datasets.forEach(ds => ds.data = []);
        chart.update();
    });

    // reseta contadores de bytes anteriores
    prevBytesSent = null;
    prevBytesRecv = null;

    hideBanner();
}

/* =========================
   Banner de alerta
   ========================= */
function showBanner(message, level='warn') {
    const el = document.getElementById('alertBanner');
    el.textContent = message;
    el.className = `alert-banner visible ${level}`;
}

function hideBanner() {
    const el = document.getElementById('alertBanner');
    el.textContent = '';
    el.className = 'alert-banner';
}

/* =========================
   CÁLCULO E ATUALIZAÇÃO DOS DADOS
   ========================= */
async function atualizarDados() {
    try {
        const resp = await fetch('/dados_sistema');
        if (!resp.ok) throw new Error('Resposta não OK');
        const dados = await resp.json();

        const now = new Date().toLocaleTimeString();

        // ---------------------------
        // CPU e Memória (simples)
        // ---------------------------
        cpuChart.data.labels.push(now);
        cpuChart.data.datasets[0].data.push(dados.cpu);

        memChart.data.labels.push(now);
        memChart.data.datasets[0].data.push(dados.memoria);

        // Atualiza cores e banner de alerta conforme thresholds
        handleAlerts(dados);

        // ---------------------------
        // Rede: converte contador cumulativo em taxa (KB/s)
        // psutil/net_io_counters retorna contadores cumulativos (bytes totais).
        // Calculamos a diferença entre leituras consecutivas e dividimos pelo tempo (s).
        // ---------------------------
        const sent = Number(dados.bytes_enviados);
        const recv = Number(dados.bytes_recebidos);

        if (prevBytesSent === null) {
            // primeira leitura: mostra 0 KB/s para evitar picos artificiais
            netChart.data.labels.push(now);
            netChart.data.datasets[0].data.push(0);
            netChart.data.datasets[1].data.push(0);
        } else {
            const deltaSent = Math.max(0, sent - prevBytesSent);
            const deltaRecv = Math.max(0, recv - prevBytesRecv);
            const seconds = UPDATE_INTERVAL_MS / 1000;
            const kbPerSecSent = (deltaSent / seconds) / 1024;
            const kbPerSecRecv = (deltaRecv / seconds) / 1024;

            netChart.data.labels.push(now);
            netChart.data.datasets[0].data.push(Number(kbPerSecSent.toFixed(2)));
            netChart.data.datasets[1].data.push(Number(kbPerSecRecv.toFixed(2)));
        }

        prevBytesSent = sent;
        prevBytesRecv = recv;

        // Mantém somente últimos 12 pontos para visualização
        [cpuChart, memChart, netChart].forEach(chart => {
            if (chart.data.labels.length > 12) {
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

// ALERTAS: muda cor do gráfico + banner
function handleAlerts(dados) {
    // atualiza thresholds a partir dos inputs em tempo real
    THRESHOLD_CPU = parseInt(document.getElementById('thrCpu').value) || THRESHOLD_CPU;
    THRESHOLD_MEM = parseInt(document.getElementById('thrMem').value) || THRESHOLD_MEM;

    const cpu = Number(dados.cpu);
    const mem = Number(dados.memoria);

    // CPU
    if (cpu >= THRESHOLD_CPU) {
        cpuChart.data.datasets[0].borderColor = '#ff4c4c'; // vermelho
        showBanner(`ALERTA: CPU alta — ${cpu}% (limite ${THRESHOLD_CPU}%)`, 'crit');
    } else {
        cpuChart.data.datasets[0].borderColor = defaultCpuColor;
        // Se memória também estiver em critério, mantemos banner; caso contrário, escondemos
        if (mem < THRESHOLD_MEM) hideBanner();
    }

    // Memória
    if (mem >= THRESHOLD_MEM) {
        memChart.data.datasets[0].borderColor = '#ff4c4c';
        showBanner(`ALERTA: Memória alta — ${mem}% (limite ${THRESHOLD_MEM}%)`, 'crit');
    } else {
        memChart.data.datasets[0].borderColor = defaultMemColor;
        if (cpu < THRESHOLD_CPU) hideBanner();
    }
}

//VARREDURA E PACOTES 
async function fazerScan() {
    const alvo = document.getElementById('alvo').value || 'localhost';
    const resultadoElem = document.getElementById('resultadoScan');
    resultadoElem.textContent = "Executando scan...";
    try {
        const resp = await fetch(`/scan?alvo=${encodeURIComponent(alvo)}`);
        const dados = await resp.json();
        resultadoElem.textContent = dados.status === "ok" ? dados.saida : "Erro: " + dados.mensagem;
    } catch (err) {
        resultadoElem.textContent = 'Erro ao executar scan.';
        console.error(err);
    }
}

async function analisarPacotes() {
    const elem = document.getElementById('resultadoPacotes');
    elem.textContent = "Capturando pacotes por 10 segundos...";
    try {
        const resp = await fetch('/pacotes');
        const dados = await resp.json();
        elem.textContent = dados.pacotes && dados.pacotes.length ? dados.pacotes.join("\n") : "Nenhum pacote capturado.";
    } catch (err) {
        elem.textContent = 'Erro ao capturar pacotes.';
        console.error(err);
    }
}

//Inicializa atualização automática ao carregar o script
startUpdating();
