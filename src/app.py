from flask import Flask, render_template, jsonify
import psutil

app = Flask(__name__)

@app.route('/')
def index():
    # Abre a página principal (HTML)
    return render_template('index.html')

@app.route('/dados_rede')
def dados_rede():
    # Coleta algumas métricas simples do sistema
    net_io = psutil.net_io_counters()
    return jsonify({
        'bytes_enviados': net_io.bytes_sent,
        'bytes_recebidos': net_io.bytes_recv
    })

if __name__ == '__main__':
    app.run(debug=True)
