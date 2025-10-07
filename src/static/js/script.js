async function atualizar() {
    const resp = await fetch('/dados_rede');
    const data = await resp.json();
    document.getElementById('sent').textContent = data.bytes_enviados;
    document.getElementById('recv').textContent = data.bytes_recebidos;
}

setInterval(atualizar, 2000);
