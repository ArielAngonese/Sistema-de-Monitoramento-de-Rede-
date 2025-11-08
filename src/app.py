from flask import Flask, render_template, jsonify, request
import re
import subprocess
import scanner

app = Flask(__name__)

# ===============================
# Páginas principais
# ===============================

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

# =============================
# Página de Segurança
# =============================
@app.route('/security')
def security():
    return render_template('security.html')

# =============================
# Captura de pacotes e detecção de anomalias
# =============================
@app.route('/security_capture')
def security_capture():
    try:
        packets = scanner.analyze_packets()  # reutiliza função existente
        alerts = []

        # Regra simples de detecção — IP repetido demais
        ip_counts = {}
        for p in packets:
            # Se p for dict, pega 'src'; se for str, usa diretamente
            if isinstance(p, dict):
                src = p.get('src', '')
            elif isinstance(p, str):
                src = p
            else:
                src = ''
            if src:
                ip_counts[src] = ip_counts.get(src, 0) + 1

        for ip, count in ip_counts.items():
            if count > 100:  # exemplo de “ataque” simulado
                alerts.append(f"Tráfego suspeito detectado: {ip} enviou {count} pacotes.")

        return jsonify({"status": "ok", "alerts": alerts})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)})

# ===============================
# Dados e funcionalidades
# ===============================

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


def traduzir_nmap(output: str) -> str:
    """Traduz termos técnicos do Nmap para português."""
    traducoes = {
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
        "scanned": "varridas",
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
        "microsoft-ds": "Compartilhamento Microsoft"
    }
    for eng, pt in traducoes.items():
        output = re.sub(rf"\b{re.escape(eng)}\b", pt, output, flags=re.IGNORECASE)
    return output


# ===============================
# Varredura de portas
# ===============================

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
            output = traduzir_nmap(output)

        return jsonify({
            "status": result.get("status", "erro"),
            "output": output
        })
    except Exception as e:
        return jsonify({"status": "erro", "output": str(e)}), 500


# ===============================
# Varredura de dispositivos
# ===============================

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
        saida = traduzir_nmap(result.stdout)

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


# ===============================
# Captura de pacotes
# ===============================

@app.route('/packets')
def packets():
    try:
        pacotes = scanner.analyze_packets()
        return jsonify({"packets": pacotes})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# ===============================
# Informações gerais
# ===============================

@app.route('/sobre')
def sobre():
    info = scanner.show_about()
    return jsonify(info)


# ===============================
# Execução
# ===============================

if __name__ == '__main__':
    app.run(debug=True)
