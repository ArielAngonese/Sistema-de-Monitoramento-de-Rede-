from flask import Flask, render_template, jsonify, request
import re
import subprocess
import scanner

app = Flask(__name__)

def traduzir(texto: str, traducoes: dict) -> str:
    """Aplica traduções simples ignorando maiúsculas/minúsculas."""
    for eng, pt in traducoes.items():
        texto = re.sub(rf"\b{re.escape(eng)}\b", pt, texto, flags=re.IGNORECASE)
    return texto

TRAD_NMAP = {
    "open": "Aberta",
    "closed": "Fechada",
    "filtered": "Filtrada",
    "tcp": "TCP",
    "udp": "UDP",
    "PORT": "PORTA",
    "STATE": "ESTADO",
    "SERVICE": "SERVIÇO",
    "Nmap scan report for": "Relatório de varredura Nmap para",
    "Host is up": "Host está ativo",
    "Not shown": "Não mostrado",
    "TCP ports": "Portas TCP",
    "All": "Todas",
    "scanned": "varridos",
    "Starting Nmap": "Iniciando Nmap",
    "at": "em",
    "latency": "latência",
    "Nmap done": "Nmap concluído",
    "IP address": "Endereço IP",
    "host up": "host(s) ativo(s)",
    "in": "em",
    "seconds": "segundos",
    "msrpc": "RPC da Microsoft",
    "netbios-ssn": "Sessão NetBIOS",
    "microsoft-ds": "Compartilhamento Microsoft",
    "unknown": "desconhecido",
    "conn-refused": "conexão recusada",
    "no-response": "sem resposta",
    "IP addresses": "Endereços IP",
    "hosts up": "host(s) ativo(s)",
    "Failed to fetch": "Falha ao buscar",
    "MAC Address": "Endereço MAC"
}

TRAD_PING = {
    "Pinging": "Pingando",
    "with 32 bytes of data": "com 32 bytes de dados",
    "Reply from": "Resposta de",
    "time": "tempo",
    "Ping statistics for": "Estatísticas de ping para",
    "Packets: Sent": "Pacotes: Enviados",
    "Received": "Recebidos",
    "Lost": "Perdidos",
    "Approximate round trip times in milli-seconds": "Tempos aproximados de ida e volta em milissegundos",
    "loss": "perda",
    "Minimum": "Mínimo",
    "Maximum": "Máximo",
    "Average": "Média",
    "Failed to fetch": "Falha ao buscar",
    "Ping request could not find host": "O pedido de ping não conseguiu encontrar o host",
    "Please check the name and try again": "Por favor, verifique o nome e tente novamente"
}

TRAD_ROUTE = {
    "Failed to fetch": "Falha ao buscar",
    "Tracing route to": "Rastreando rota para",
    "over a maximum of": "sobre um máximo de",
    "hops": "saltos",
    "Trace complete.": "Rastreamento completo.",
    "Request timed out": "Tempo de solicitação esgotado"
}

TRAD_DNS = {
    "Server": "Servidor",
    "Address": "Endereço",
    "Non-authoritative answer": "Resposta não autoritativa",
    "Name": "Nome",
    "Address": "Endereço",
    "can't find": "não pode encontrar",
    "try again": "tente novamente",
    "Unknown host": "Host desconhecido,",
    "Unknown server error": "Erro desconhecido do servidor",
    "Unknown query type": "Tipo de consulta desconhecido",
    "UnKnown": "Desconhecido",
    "Failed to fetch": "Falha ao buscar"
}
@app.route('/')
def inicial():
    return render_template('inicialPage.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/devices')
def devices():
    return render_template('devices.html')

@app.route('/ports')
def ports():
    return render_template('ports.html')

@app.route('/security')
def security():
    return render_template('security.html')


# Página Tools (Ferramentas)
@app.route('/tools')
def tools():
    return render_template('tools.html')

@app.route('/ping')
def ping():
    target = request.args.get('target', '')
    if not target:
        return jsonify({"status": "erro", "output": "Host não especificado."}), 400

    try:
        import platform
        system = platform.system().lower()
        # Usa -n no Windows, -c em outros
        count_flag = "-n" if system == "windows" else "-c"

        result = subprocess.run(
            ["ping", count_flag, "4", target],
            capture_output=True, text=True, timeout=10
        )

        output = result.stdout or result.stderr
        output = traduzir(output, TRAD_PING)

        return jsonify({
            "status": "ok" if result.returncode == 0 else "erro",
            "output": output
        })

    except Exception as e:
        return jsonify({"status": "erro", "output": str(e)}), 500

@app.route('/traceroute')
def traceroute():
    import platform, subprocess

    target = request.args.get('target', '').strip()
    if not target:
        return jsonify({"status": "erro", "output": "Host não especificado."}), 400

    system = platform.system().lower()
    command = ["tracert", target] if system == "windows" else ["traceroute", target]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120
        )

        output = result.stdout or result.stderr or "Nenhuma resposta retornada."
        output = traduzir(output, TRAD_ROUTE)

        return jsonify({
            "status": "ok" if result.returncode == 0 else "erro",
            "output": output
        })

    except subprocess.TimeoutExpired as e:
        partial_output = e.stdout or "O comando demorou demais e foi interrompido."
        return jsonify({
            "status": "erro",
            "output": f"Tempo limite excedido (timeout de 60s).\nSaída parcial:\n{partial_output}"
        })

    except Exception as e:
        return jsonify({
            "status": "erro",
            "output": f"Erro ao executar o traceroute: {str(e)}"
        }), 500

@app.route('/dns_lookup')
def dns_lookup():
    target = request.args.get('domain', '')
    if not target:
        return jsonify({"status": "erro", "output": "Domínio não especificado."}), 400

    try:
        # Usa o comando nslookup
        result = subprocess.run(
            ["nslookup", target],
            capture_output=True, text=True, timeout=10
        )

        output = result.stdout or result.stderr
        output = traduzir(output, TRAD_DNS)

        return jsonify({
            "status": "ok" if result.returncode == 0 else "erro",
            "output": output
        })
    except Exception as e:
        return jsonify({"status": "erro", "output": str(e)}), 500


@app.route('/security_simulate_ddos')
def security_simulate_ddos():
    # Simula um ataque DDoS com múltiplos IPs e protocolos
    ip_summary = [
        "192.168.0.101: 1200 pacotes",
        "192.168.0.102: 950 pacotes",
        "192.168.0.103: 870 pacotes",
        "192.168.0.104: 420 pacotes",
        "192.168.0.105: 210 pacotes"
    ]
    protocols = ["TCP", "UDP", "ICMP"]
    simulated_alerts = [
        "Tráfego suspeito detectado: 192.168.0.101 enviou 1200 pacotes.",
        "Tráfego suspeito detectado: 192.168.0.102 enviou 950 pacotes.",
        "Tráfego suspeito detectado: 192.168.0.103 enviou 870 pacotes.",
        "Possível ataque DDoS: múltiplos IPs excederam o limite de pacotes em curto intervalo."
    ]
    return jsonify({
        "status": "ok",
        "alerts": simulated_alerts,
        "ip_summary": ip_summary,
        "protocols": protocols
    })

@app.route('/security_capture')
def security_capture():
    try:
        packets = scanner.analyze_packets()  # Reutiliza função existente
        alerts = []
        ip_counts = {}
        proto_counts = {}

        # Extrai IPs e protocolos
        for p in packets:
            if isinstance(p, dict):
                src = p.get('src', '')
                proto = p.get('proto', '').upper()
            elif isinstance(p, str):
                src = p
                proto = ''
            else:
                src = ''
                proto = ''
            if src:
                ip_counts[src] = ip_counts.get(src, 0) + 1
            if proto:
                proto_counts[proto] = proto_counts.get(proto, 0) + 1

        # IPs mais frequentes (top 5)
        ip_summary = [f"{ip}: {count} pacotes" for ip, count in sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
        # Protocolos observados
        protocols = list(proto_counts.keys())

        # Alertas
        for ip, count in ip_counts.items():
            if count > 100:
                alerts.append(f"Tráfego suspeito detectado: {ip} enviou {count} pacotes.")
        if not alerts:
            alerts.append("Nenhum comportamento suspeito detectado.")

        return jsonify({
            "status": "ok",
            "alerts": alerts,
            "ip_summary": ip_summary,
            "protocols": protocols
        })
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)})

@app.route('/system_data')
def system_data():
    """Retorna uso de CPU, memória e rede em tempo real."""
    try:
        dados = scanner.get_system_usage()
        return jsonify({
            "cpu": dados.get("cpu", 0),
            "memory": dados.get("memoria", 0),
            "bytes_sent": dados.get("bytes_enviados", 0),
            "bytes_received": dados.get("bytes_recebidos", 0)
        })
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/scan')
def scan():
    """Executa varredura de portas usando módulo interno scanner."""
    try:
        target = request.args.get('target', 'localhost')
        if not re.match(r"^[a-zA-Z0-9\.\-]+$", target):
            return jsonify({"status": "erro", "output": "Alvo inválido."}), 400

        result = scanner.scan_ports(target)
        output = result.get("saida", result.get("mensagem", "Nenhum resultado."))

        if isinstance(output, str):
            output = traduzir(output, TRAD_NMAP)

        return jsonify({
            "status": result.get("status", "erro"),
            "output": output
        })
    except Exception as e:
        return jsonify({"status": "erro", "output": str(e)}), 500

@app.route('/scan_devices')
def scan_devices():
    """Executa varredura de rede para detectar dispositivos ativos."""
    network_range = request.args.get('range', '').strip()

    if not network_range:
        return jsonify({"status": "error", "mensagem": "Faixa de rede não informada."})

    try:
        # Executa nmap no modo de descoberta de hosts (-sn = ping scan)
        result = subprocess.run(
            ["nmap", "-sn", network_range],
            capture_output=True,
            text=True,
            timeout=25
        )

        if result.returncode != 0:
            return jsonify({
                "status": "error",
                "mensagem": result.stderr.strip() or "Falha ao executar o Nmap."
            })

        # Traduz a saída para português
        saida = traduzir(result.stdout, TRAD_NMAP)

        # Pequena formatação visual opcional
        saida_formatada = re.sub(r"(Nmap scan report for [^\n]+)", r"\n\033[1m\1\033[0m", saida)

        return jsonify({
            "status": "ok",
            "output": saida_formatada
        })

    except subprocess.TimeoutExpired:
        return jsonify({
            "status": "error",
            "mensagem": "Tempo limite de execução atingido (timeout)."
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "mensagem": f"Erro interno: {str(e)}"
        })

@app.route('/packets')
def packets():
    try:
        pacotes = scanner.analyze_packets()
        return jsonify({"packets": pacotes})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/sobre')
def sobre():
    info = scanner.show_about()
    return jsonify(info)

if __name__ == '__main__':
    app.run(debug=True)
