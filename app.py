from flask import Flask, request, jsonify, send_file, render_template
from fpdf import FPDF
import os
from datetime import datetime

app = Flask(__name__, template_folder="templates")

# Diretório estático para salvar os PDFs gerados
STATIC_DIR = "static"
os.makedirs(STATIC_DIR, exist_ok=True)

# Caminho para a imagem da assinatura
SIGNATURE_IMAGE_PATH = "static/assinatura.jpg"  # Certifique-se de que a imagem esteja nesta pasta

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "V.S. MANUTENÇÃO ELÉTRICA", ln=True, align="C")
        self.set_font("Arial", "", 10)
        self.cell(0, 5, "Instalação e Manutenção de Ar Condicionado Split", ln=True, align="C")
        self.cell(0, 5, "Profissionais de confiança em manutenção elétrica e ar-condicionado", ln=True, align="C")
        self.ln(10)
        self.set_font("Arial", "", 10)
        self.cell(0, 5, "CNPJ: 13.463.502/0001-09", ln=True, align="C")
        self.cell(0, 5, "Rua 36, Bairro Jd. Ouro Verde, Várzea Grande - MT", ln=True, align="C")
        self.cell(0, 5, "Tel: (65) 3692-3238 | Cel: (65) 99909-2153", ln=True, align="C")
        self.cell(0, 5, "E-mail: vsmanutencaoeletrica70@gmail.com", ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-30)
        self.set_font("Arial", "", 10)
        self.cell(0, 10, f"Documento gerado em: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align="C")
        self.cell(0, 10, "Validade do orçamento: 15 dias a partir da data de emissão.", ln=True, align="C")

    def add_signature(self):
        # Centraliza a assinatura no espaço entre o total e o rodapé
        self.set_y(-80)  # Ajuste a altura para centralizar no local desejado
        self.image(SIGNATURE_IMAGE_PATH, x=70, w=70)  # Aumenta o tamanho da assinatura (largura = 70)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate-pdf", methods=["POST"])
def generate_pdf():
    try:
        data = request.json
        client_name = data["client_name"]
        client_cnpj = data["client_cnpj"]
        client_address = data["client_address"]
        services = data["services"]
        total_value = data["total_value"]

        # Nome e caminho do arquivo gerado
        date_str = datetime.now().strftime("%Y-%m-%d")
        pdf_filename = f"orcamento_{client_name.replace(' ', '_').lower()}_{date_str}.pdf"
        pdf_filepath = os.path.join(STATIC_DIR, pdf_filename)

        # Gerando o PDF
        pdf = PDF()
        pdf.add_page()

        # Informações do cliente
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Para: {client_name}", ln=True)
        pdf.cell(0, 10, f"CNPJ/CPF: {client_cnpj}", ln=True)
        pdf.cell(0, 10, f"Endereço: {client_address}", ln=True)
        pdf.ln(10)

        # Tabela de serviços
        pdf.set_font("Arial", "B", 12)
        pdf.cell(80, 10, "Descrição", border=1)
        pdf.cell(30, 10, "Quantidade", border=1)
        pdf.cell(40, 10, "Valor Unitário", border=1)
        pdf.cell(40, 10, "Total", border=1)
        pdf.ln()

        pdf.set_font("Arial", "", 12)
        for service in services:
            pdf.cell(80, 10, service["description"], border=1)
            pdf.cell(30, 10, str(service["quantity"]), border=1, align="C")
            pdf.cell(40, 10, f"R$ {service['unit_value']:.2f}", border=1, align="R")
            pdf.cell(40, 10, f"R$ {service['total']:.2f}", border=1, align="R")
            pdf.ln()

        pdf.ln(10)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(150, 10, "VALOR TOTAL DA MÃO DE OBRA:", border=0, align="R")
        pdf.cell(40, 10, f"R$ {total_value:.2f}", border=1, align="R")

        # Adiciona a assinatura no local apropriado
        pdf.add_signature()

        pdf.output(pdf_filepath)

        return jsonify({"message": "PDF gerado com sucesso!", "pdf_url": f"/static/{pdf_filename}"})
    except Exception as e:
        return jsonify({"message": "Erro ao gerar PDF.", "error": str(e)}), 500

@app.route("/static/<filename>")
def serve_pdf(filename):
    return send_file(os.path.join(STATIC_DIR, filename))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
