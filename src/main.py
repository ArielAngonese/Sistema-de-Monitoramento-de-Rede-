# src/main.py
import subprocess
from scapy.all import sniff, Packet

def scan_ports():
    target = input("Digite o IP ou hostname para escanear: ")
    print(f"\n[+] Escaneando portas do host {target}...\n")
    
    try:
        # Usa Nmap via subprocess
        result = subprocess.run(['nmap', '-sT', target], capture_output=True, text=True)
        print(result.stdout)
    except FileNotFoundError:
        print("[!] Nmap não encontrado. Certifique-se de que está instalado.")

def analyze_packets():
    print("\n[+] Capturando pacotes por 10 segundos (exemplo simplificado)...\n")
    
    def packet_callback(packet: Packet):
        print(packet.summary())
    
    sniff(prn=packet_callback, timeout=10)

def show_about():
    print("""
Projeto Integrador – Segurança da Informação
--------------------------------------------
Este sistema tem como objetivo auxiliar no estudo de Redes de Computadores
e Segurança da Informação por meio de exemplos práticos.
""")

def main():
    while True:
        print("\n=== Projeto Integrador – Segurança da Informação ===")
        print("1. Varredura de Portas")
        print("2. Análise de Pacotes")
        print("3. Sobre")
        print("0. Sair")

        choice = input("\nEscolha uma opção: ")

        if choice == "1":
            scan_ports()
        elif choice == "2":
            analyze_packets()
        elif choice == "3":
            show_about()
        elif choice == "0":
            print("\n[+] Encerrando o programa. Até mais!")
            break
        else:
            print("\n[!] Opção inválida, tente novamente.")

if __name__ == "__main__":
    main()
