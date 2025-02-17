from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import logging
from datetime import datetime
from dependency_check import check_dependencies, format_dependency_report

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Verificar dependências durante a inicialização
success, problems = check_dependencies()
if not success:
    logger.error(format_dependency_report(success, problems))
else:
    logger.info("✓ Verificação de dependências concluída com sucesso")

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")

# Caminho para o arquivo Excel
EXCEL_FILE = "dados.xlsx"

def criar_grafico_espessura(bobina, operacao, espessuras, nominal, minimo, maximo, analista,
                           data, serie_medidor, coordenador, produto, maquina, turno):
    # Configurar estilo
    plt.style.use('dark_background')

    # Estatísticas
    desvio_padrao = np.std(espessuras, ddof=1)
    media_espessura = np.mean(espessuras)

    # Criar ângulos para os pontos
    num_pontos = len(espessuras)
    angulos = np.linspace(0, 2 * np.pi, num_pontos, endpoint=False).tolist()
    espessuras_plot = espessuras + espessuras[:1]  # Fechar o gráfico
    angulos += angulos[:1]

    # Calcular limites do gráfico
    min_espessura = min(espessuras)
    max_espessura = max(espessuras)
    limite_inferior = min(minimo, min_espessura) - 0.002
    limite_superior = max(maximo, max_espessura) + 0.002

    # Criar o gráfico com tamanho maior
    fig, ax = plt.subplots(figsize=(18, 15), subplot_kw=dict(polar=True))
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # Ajustar limites e grid
    ax.set_ylim(limite_inferior, limite_superior)
    ax.grid(True, color='gray', alpha=0.3, linewidth=1)

    # Adicionar linhas de referência com cores mais vibrantes
    ax.plot(angulos, [nominal] * len(angulos), linestyle='solid', color='#00FF00', 
           linewidth=5, alpha=1, label=f"Nominal ({nominal:.5f} mm)")
    ax.plot(angulos, [minimo] * len(angulos), linestyle='solid', color='#FF0000', 
           linewidth=5, alpha=1, label=f"Mínimo ({minimo:.5f} mm)")
    ax.plot(angulos, [maximo] * len(angulos), linestyle='solid', color='#FFA500', 
           linewidth=5, alpha=1, label=f"Máximo ({maximo:.5f} mm)")

    # Plotar pontos medidos com marcadores maiores e mais destacados
    ax.plot(angulos, espessuras_plot, color='#00FFFF', linewidth=6, linestyle='solid',
           marker='o', markersize=15, markerfacecolor='#FF4500', label="Valores Medidos",
           markeredgecolor='white', markeredgewidth=2)
    ax.fill(angulos, espessuras_plot, color='#00FFFF', alpha=0.25)

    # Configurar rótulos com fonte maior
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels([f"P{i+1}" for i in range(num_pontos)], 
                       fontsize=18, fontweight='bold', color='white')

    # Adicionar valores aos pontos com fonte maior e melhor posicionamento
    for angulo, valor in zip(angulos[:-1], espessuras):
        valor_texto = f"{valor:.5f}"
        if valor < minimo or valor > maximo:
            valor_texto += " ⚠"
            cor_texto = '#FF3333'  # Vermelho mais brilhante
            fontweight = 'bold'
        else:
            cor_texto = '#FFFFFF'  # Branco puro
            fontweight = 'normal'

        # Ajustar posição do texto com mais espaço
        deslocamento = 0.003 if valor < limite_superior else -0.003
        ax.text(angulo, valor + deslocamento, valor_texto, 
                ha='center', va='center', fontsize=16, color=cor_texto, 
                fontweight=fontweight, bbox=dict(facecolor='black', alpha=0.7, pad=3))

    # Adicionar todas as informações do formulário com melhor formatação
    info_text = (
        f"OP: {operacao}\n"
        f"Bobina: {bobina}\n"
        f"Máquina: {maquina}\n"
        f"Produto: {produto}\n"
        f"Data: {data}\n"
        f"Turno: {turno}\n"
        f"Série do Medidor: {serie_medidor}\n"
        f"Analista: {analista}\n"
        f"Coordenador: {coordenador}"
    )
    plt.figtext(0.02, 0.02, info_text, fontsize=16, ha="left", 
                bbox={"facecolor": "black", "alpha": 0.9, "pad": 15, 
                      "edgecolor": "white", "boxstyle": "round,pad=1"}, 
                color='white')

    # Título maior e mais destacado
    plt.suptitle(f"Medição de Espessura - Bobina {bobina}", 
              fontsize=28, fontweight='bold', color='white', y=0.95)

    # Legenda maior e mais clara com borda
    legend = ax.legend(loc="upper left", bbox_to_anchor=(1.2, 1.1), fontsize=18, 
                      title="Referências e Medições", title_fontsize=20, 
                      frameon=True, framealpha=0.9, edgecolor='white')
    legend.get_frame().set_facecolor('black')
    for text in legend.get_texts():
        text.set_color('white')

    # Adicionar estatísticas com mais destaque e borda
    stats_text = (
        f"Média: {media_espessura:.5f} mm\n"
        f"Desvio Padrão: {desvio_padrao:.5f}\n"
        f"Mín: {min_espessura:.5f} mm\n"
        f"Máx: {max_espessura:.5f} mm"
    )
    plt.figtext(0.98, 0.02, stats_text, fontsize=16, ha="right",
                bbox={"facecolor": "black", "alpha": 0.9, "pad": 15, 
                      "edgecolor": "white", "boxstyle": "round,pad=1"}, 
                color='white')

    # Gerar nome único para o arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"grafico_bobina_{bobina}_{timestamp}.png"
    filepath = os.path.join("static", filename)

    # Salvar com qualidade maior e fundo preto
    plt.savefig(filepath, bbox_inches='tight', dpi=300, facecolor='black', 
                edgecolor='none', pad_inches=0.5)
    plt.close()

    return filename

@app.route("/import-excel", methods=["POST"])
def import_excel():
    try:
        if 'file' not in request.files:
            return {"error": "No file uploaded"}, 400

        file = request.files['file']
        if file.filename == '':
            return {"error": "No file selected"}, 400

        df = pd.read_excel(file, engine='openpyxl')
        points = df['Espessura'].tolist() if 'Espessura' in df.columns else []
        return {"points": points}, 200
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Collect form data
            data = request.form["data"]
            turno = request.form["turno"]  # New field
            serie_medidor = request.form["serie_medidor"]
            analista = request.form["analista"]
            coordenador = request.form["coordenador"]
            bobina = request.form["bobina"]
            maquina = request.form["maquina"]
            op = request.form["op"]
            produto = request.form["produto"]
            nominal = float(request.form["nominal"])
            minimo = float(request.form["minimo"])
            maximo = float(request.form["maximo"])

            # Get all measurement points dynamically
            espessuras = []
            point_num = 1
            while f"ponto{point_num}" in request.form:
                value = request.form[f"ponto{point_num}"]
                if value.strip():  # Only process non-empty values
                    espessuras.append(float(value))
                point_num += 1
            
            if not espessuras:
                flash("Por favor, insira pelo menos um ponto de medição.", "danger")
                return redirect(url_for("index"))

            # Create graph with all parameters including turno
            graph_filename = criar_grafico_espessura(
                bobina, op, espessuras, nominal, minimo, maximo, analista,
                data, serie_medidor, coordenador, produto, maquina, turno
            )

            # Save data to Excel with turno field
            dados = {
                "Data": [data],
                "Turno": [turno],  # New field
                "Série do Medidor": [serie_medidor],
                "Analista": [analista],
                "Coordenador": [coordenador],
                "Bobina": [bobina],
                "Máquina": [maquina],
                "OP": [op],
                "Produto": [produto],
                "Nominal": [nominal],
                "Mínimo": [minimo],
                "Máximo": [maximo],
                **{f"Ponto {i+1}": [espessuras[i]] for i in range(len(espessuras))}
            }
            df = pd.DataFrame(dados)

            if os.path.exists(EXCEL_FILE):
                with pd.ExcelWriter(EXCEL_FILE, mode="a", engine="openpyxl", if_sheet_exists="replace") as writer:
                    df.to_excel(writer, index=False, sheet_name=f"Bobina_{bobina}")
            else:
                df.to_excel(EXCEL_FILE, index=False, sheet_name=f"Bobina_{bobina}")

            flash("Dados salvos com sucesso!", "success")
            return redirect(url_for("resultado", graph_filename=graph_filename))

        except Exception as e:
            logging.error(f"Erro ao processar formulário: {str(e)}")
            flash(f"Erro ao processar dados: {str(e)}", "danger")
            return redirect(url_for("index"))

    return render_template("index.html")

@app.route("/resultado")
def resultado():
    graph_filename = request.args.get("graph_filename")
    if not graph_filename:
        flash("Erro: Gráfico não encontrado!", "danger")
        return redirect(url_for("index"))
    return render_template("resultado.html", graph_filename=graph_filename)