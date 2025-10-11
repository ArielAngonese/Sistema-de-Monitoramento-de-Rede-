import subprocess
from scapy.all import sniff, Packet
import psutil

def scan_ports(target: str):
    try:
        result = subprocess.run(['nmap', '-sT', target], capture_output=True, text=True)
        return {"status": "ok", "saida": result.stdout}
    except FileNotFoundError:
        return {"status": "erro", "mensagem": "Nmap não encontrado. Instale-o e tente novamente."}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

def analyze_packets():
    pacotes = []
    def packet_callback(packet: Packet):
        pacotes.append(packet.summary())
    sniff(prn=packet_callback, timeout=10)
    return pacotes

def show_about():
    return {
        "titulo": "Projeto Integrador – Segurança da Informação",
        "descricao": (
            "Sistema educacional de monitoramento de rede e segurança, "
            "desenvolvido em Python, utilizando Nmap e Scapy."
        )
    }

def get_system_usage():
    """Retorna dados em tempo real de CPU, memória e rede."""
    net_io = psutil.net_io_counters()
    return {
        "cpu": psutil.cpu_percent(interval=0.5),
        "memoria": psutil.virtual_memory().percent,
        "bytes_enviados": net_io.bytes_sent,
        "bytes_recebidos": net_io.bytes_recv
    }
