# 🖥️ Sistema de Monitoramento de Rede

Projeto desenvolvido para fins educacionais na área de **Segurança da Informação**, com o objetivo de **facilitar o estudo e a compreensão de conceitos fundamentais em Redes de Computadores**, protocolos e ferramentas de análise de tráfego, por meio de exemplos práticos e uma interface interativa baseada em Flask.

---

## 📌 Objetivos
- Explorar conceitos fundamentais de **Redes de Computadores**.  
- Compreender princípios básicos de **Segurança da Informação**.  
- Demonstrar o funcionamento de **protocolos e portas de rede**.  
- Implementar ferramentas práticas como **varredura de portas** e **análise de pacotes**.

---

## 🛠 Tecnologias Utilizadas
- **Python 3.13.7**
- **Flask** – Backend web e API
- **psutil** – Coleta de métricas do sistema (CPU, memória, rede)
- **scapy** – Captura e análise de pacotes
- **Nmap** – Ferramenta de varredura de portas (requer instalação separada)
- **Chart.js** – Gráficos dinâmicos no frontend
- **HTML5 / CSS3 / JavaScript**

---

## 📂 Estrutura do Projeto

Sistema-de-Monitoramento-de-Rede/
│
├── app.py # Servidor Flask (backend principal)
├── scanner.py # Lógica de análise e monitoramento
├── requirements.txt # Dependências Python
│
├── templates/
│ ├── index.html # Página inicial (dashboard)
│ └── ports.html # Página explicativa sobre portas e protocolos
│
├── static/
│ ├── css/
│ │ ├── style.css # Estilo do dashboard
│ │ └── ports.css # Estilo da página de portas
│ └── js/
│ └── script.js # Lógica do frontend e gráficos
│
└── README.md

## 🚀 Como Executar o Projeto

### 1️⃣ Clonar o repositório
```bash
git clone https://github.com/ArielAngonese/Sistema-de-Monitoramento-de-Rede-.git
cd Sistema-de-Monitoramento-de-Rede-

### 2️⃣ Instalar dependências Python
pip install -r requirements.txt

### 3️⃣ Instalar o Nmap (necessário para varredura de portas)

O Nmap não é instalado via pip. É um programa externo que precisa estar disponível no sistema.

- Windows:
Baixe e instale manualmente:
👉 https://nmap.org/download.html

Ou via Chocolatey:
choco install nmap

- Linux (Debian/Ubuntu):
sudo apt update
sudo apt install nmap

- macOS (com Homebrew):
brew install nmap

- Verifique se está instalado corretamente:
nmap -v

### 4️⃣ Executar o servidor Flask
python app.py

O sistema ficará disponível em:
🔗 http://127.0.0.1:5000

## 🧠 Funcionalidades Principais

- Monitoramento em tempo real de CPU, memória e tráfego de rede (gráficos interativos com Chart.js);
- Varredura de portas usando Nmap diretamente pela interface web;
- Captura de pacotes de rede com Scapy (modo educacional);
- Alertas dinâmicos de uso excessivo de CPU/memória;
- Página explicativa sobre funcionamento de IPs, portas e protocolos.

## 👾 Funcionalidades Futuras

- Adição de outas páginas explicativas sobre conceitos fundamentais de Redes de Computadores e Segurança da Informação;
- Novos meios de testar na prática os conceitos apresnetados;
- Melhoria do dicionário;
- Outras melhorias gerais e de usabilidade.

## ⚠️ Observações

- Para a captura de pacotes (Scapy), pode ser necessário executar o servidor como administrador ou com sudo;
- A varredura de portas depende do Nmap — se ele não estiver instalado, a funcionalidade exibirá uma mensagem de aviso.

## 🧩 Erros Comuns e Soluções

Mensagem: Erro ao buscar dados do servidor   
Causa Provável: O Flask não está rodando ou foi iniciado na porta errada
Solução Recomendada: Verifique se o Flask está em execução (python app.py) e se a porta é 5000

Mensagem: nmap: command not found
Causa Provável: O Nmap não está instalado no sistema
Solução Recomendada: Instale o Nmap conforme descrito acima e verifique com nmap -v

Mensagem: Permissão negada (Scapy)
Causa Provável: O Scapy precisa de privilégios elevados para capturar pacotes
Solução: Execute com sudo python app.py (Linux/Mac) ou como administrador (Windows)

Erro: Gráficos não aparecem no Dashboard
Causa Provável: Falha no carregamento do JavaScript ou erro de rota no backend
Solução: Verifique se o Flask está servindo /system_data corretamente e abra o console (F12 → Console)

👨‍💻 Autores

Projeto Integrador II — 2025
- Ariel Liotto Angonese
- Emanuel Júlio Solivo
- Vítor Luis Andreolla

