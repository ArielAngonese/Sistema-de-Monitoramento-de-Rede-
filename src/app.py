from flask import Flask, render_template, jsonify, request
import scanner

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dados_sistema')
def dados_sistema():
    dados = scanner.get_system_usage()
    return jsonify(dados)

@app.route('/scan')
def scan():
    alvo = request.args.get('alvo', 'localhost')
    resultado = scanner.scan_ports(alvo)
    return jsonify(resultado)

@app.route('/pacotes')
def pacotes():
    pacotes = scanner.analyze_packets()
    return jsonify({"pacotes": pacotes})

@app.route('/sobre')
def sobre():
    info = scanner.show_about()
    return jsonify(info)

if __name__ == '__main__':
    app.run(debug=True)
