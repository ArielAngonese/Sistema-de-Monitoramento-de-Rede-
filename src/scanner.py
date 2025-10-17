import subprocess
import platform
from shutil import which
import psutil
import scapy
from scapy.all import sniff, Packet


def check_nmap():
    from shutil import which
    return which("nmap") is not None

def scan_ports(target: str):
    if not target or not isinstance(target, str):
        return {"status": "erro", "mensagem": "Alvo inválido."}
    try:
        result = subprocess.run(
            ['nmap', '-sT', target],
            capture_output=True,
            text=True,
            timeout=15
        )
        return {"status": "ok", "saida": result.stdout}
    except FileNotFoundError:
        return {"status": "erro", "mensagem": "Nmap não encontrado. Instale-o e tente novamente."}
    except subprocess.TimeoutExpired:
        return {"status": "erro", "mensagem": "A varredura demorou demais."}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

def analyze_packets(timeout=5):
    pacotes = []

    def packet_callback(packet: Packet):
        pacotes.append(packet.summary())

    try:
        sniff(prn=packet_callback, timeout=timeout)
        return pacotes[:50]
    except PermissionError:
        return ["Permissão negada: execute como administrador."]
    except Exception as e:
        return [f"Erro na captura: {str(e)}"]

def show_about():
    return {
        "titulo": "Projeto Integrador – Segurança da Informação",
        "descricao": (
            "Sistema educacional de monitoramento de rede e segurança, "
            "desenvolvido em Python, utilizando Nmap e Scapy."
        ),
        "versao_python": platform.python_version(),
        "versao_scapy": scapy.__version__,
        "versao_psutil": psutil.__version__
    }


def get_system_usage():
    net_io = psutil.net_io_counters()
    return {
        "cpu": psutil.cpu_percent(interval=0.5),
        "memoria": psutil.virtual_memory().percent,
        "nucleos": psutil.cpu_count(logical=True),
        "bytes_enviados": net_io.bytes_sent,
        "bytes_recebidos": net_io.bytes_recv
    }

