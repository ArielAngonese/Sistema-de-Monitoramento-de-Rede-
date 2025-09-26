# src/main.py
# Projeto Integrador – Segurança da Informação
# Estrutura inicial com menu de opções

def scan_ports():
    print("\n[+] Função de varredura de portas (em desenvolvimento)\n")

def analyze_packets():
    print("\n[+] Função de análise de pacotes (em desenvolvimento)\n")

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
