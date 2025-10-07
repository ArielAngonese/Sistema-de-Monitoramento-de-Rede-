# src/scanner.py
import subprocess
from scapy.all import sniff, Packet

def scan_ports(target: str):
    """Executa varredura de portas usando Nmap e retorna a saída como texto."""
    try:
        result = subprocess.run(['nmap', '-sT', target], capture_output=True, text=True)
        return {"status": "ok", "saida": result.stdout}
    except FileNotFoundError:
        return {"status": "erro", "mensagem": "Nmap não encontrado. Instale-o e tente novamente."}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

def analyze_packets():
    """Captura pacotes por 10 segundos e retorna o resumo."""
    pacotes = []

    def packet_callback(packet: Packet):
        pacotes.append(packet.summary())

    sniff(prn=packet_callback, timeout=10)
    return pacotes

def show_about():
    """Retorna a descrição do projeto (em vez de imprimir)."""
    return {
        "titulo": "Projeto Integrador – Segurança da Informação",
        "descricao": (
            "Este sistema tem como objetivo auxiliar no estudo de Redes de Computadores "
            "e Segurança da Informação por meio de exemplos práticos."
        )
    }
