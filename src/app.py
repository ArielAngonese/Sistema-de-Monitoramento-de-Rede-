from flask import Flask, render_template, jsonify, request
import re
import scanner 

app = Flask(__name__)

# Página principal
@app.route('/')
def index():
    return render_template('index.html')

# Dados do sistema (CPU, Memória, Rede)
@app.route('/system_data')
def system_data():
    try:
        dados = scanner.get_system_usage()
        return jsonify({
            "cpu": dados.get("cpu", 0),
            "memory": dados.get("memoria", 0),                # converte 'memoria' -> 'memory'
            "bytes_sent": dados.get("bytes_enviados", 0),     # 'bytes_enviados' -> 'bytes_sent'
            "bytes_received": dados.get("bytes_recebidos", 0) # 'bytes_recebidos' -> 'bytes_received'
        })
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

def traduzir_nmap(output: str) -> str:
    # Dicionário de tradução simples
    traducoes = {
        "open": "aberta",
        "closed": "fechadas",
        "filtered": "filtrada",
        "tcp": "TCP",
        "udp": "UDP",
        "PORT": "PORTA",
        "STATE": "ESTADO",
        "SERVICE": "SERVIÇO",
        "Nmap scan report for": "Relatório de varredura Nmap para",
        "Host is up": "Host está ativo",
        "Not shown": "Não mostrado",
        "TCP ports": "| Portas TCP",
        "All": "Todas",
        "scanned": "varrido(s)",
        "conn-refused": "conexão recusada",
        "no-response": "sem resposta",
        "Starting Nmap": "Iniciando Nmap",
        "at": "em",
        "latency": "latência",
        "Nmap done": "Nmap concluído",
        "IP address": "Endereço IP",
        "host up": "host(s) ativo(s)",
        "in": "em",
        "seconds": "segundos",

        # Serviços comuns
        "msrpc": "RPC da Microsoft",
        "netbios-ssn": "Sessão NetBIOS",
        "microsoft-ds": "Compartilhamento Microsoft"
    }

    # Substituição case-insensitive usando regex com bordas de palavra
    for eng, pt in traducoes.items():
        output = re.sub(rf"\b{re.escape(eng)}\b", pt, output, flags=re.IGNORECASE)

    return output

# Varredura de portas 
@app.route('/scan')
def scan():
    try:
        target = request.args.get('target', 'localhost')
        if not re.match(r"^[a-zA-Z0-9\.\-]+$", target):
            return jsonify({"status": "erro", "output": "Alvo inválido"}), 400

        result = scanner.scan_ports(target)
        output = result.get("saida", result.get("mensagem", ""))

        # Traduz o texto
        if isinstance(output, str) and output:
            output_translated = traduzir_nmap(output)
        else:
            output_translated = output or "Nenhum resultado."

        return jsonify({
            "status": result.get("status", "erro"),
            "output": output_translated
        })
    except Exception as e:
        return jsonify({"status": "erro", "output": str(e)}), 500

# Captura de pacotes
@app.route('/packets')
def packets():
    try:
        pacotes = scanner.analyze_packets()
        return jsonify({"packets": pacotes})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# Sobre
@app.route('/sobre')
def sobre():
    info = scanner.show_about()
    return jsonify(info)

# Página de portas e protocolos
@app.route('/ports')
def ports():
    return render_template('ports.html')


if __name__ == '__main__':
    app.run(debug=True)
