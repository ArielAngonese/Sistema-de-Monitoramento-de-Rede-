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
    """Captura pacotes por alguns segundos e retorna lista de dicionários."""
    pacotes = []

    def packet_callback(packet: Packet):
        try:
            src = packet["IP"].src if packet.haslayer("IP") else None
            dst = packet["IP"].dst if packet.haslayer("IP") else None

            if packet.haslayer("TCP"):
                proto = "TCP"
            elif packet.haslayer("UDP"):
                proto = "UDP"
            elif packet.haslayer("ICMP"):
                proto = "ICMP"
            else:
                proto = packet.lastlayer().name if hasattr(packet, "lastlayer") else "DESCONHECIDO"

            pacotes.append({
                "src": src,
                "dst": dst,
                "proto": proto,
                "summary": packet.summary()
            })
        except Exception as e:
            pacotes.append({"summary": f"Erro ao processar pacote: {e}"})

    try:
        sniff(prn=packet_callback, timeout=timeout, store=0)
        # retorna só os primeiros 100 para não sobrecarregar
        return pacotes[:100] if pacotes else [{"info": "Nenhum pacote capturado."}]
    except PermissionError:
        return [{"error": "Permissão negada: execute como administrador ou root."}]
    except Exception as e:
        return [{"error": f"Erro na captura: {str(e)}"}]


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
