from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from fpdf import FPDF
import os
from datetime import datetime

app = Flask(__name__, template_folder="templates")
app.secret_key = os.urandom(24)

# Configuração do LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = "info"

# Banco de dados simulado para usuários
USERS_DB = {
    "Valdevino": generate_password_hash("VS1401"),
}

# Classe User para autenticação
class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    if user_id in USERS_DB:
        return User(user_id)
    return None

# Classe para gerar PDFs
class PDF(FPDF):
    def header(self):
        # Adicionando logo
        logo_path = "static/logo.jpg"  # Altere para o caminho correto
        if os.path.exists(logo_path):
            self.image(logo_path, x=10, y=8, w=40)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "V.S. MANUTENÇÃO ELÉTRICA", ln=True, align="C")
        self.set_font("Arial", "", 10)
        self.cell(0, 5, "Instalação e Manutenção de Ar Condicionado Split", ln=True, align="C")
        self.cell(0, 5, "CNPJ: 13.463.502/0001-09", ln=True, align="C")
        self.cell(0, 5, "Rua 36, Bairro Jd. Ouro Verde, Várzea Grande - MT", ln=True, align="C")
        self.cell(0, 5, "Tel: (65) 3692-3238 | Cel: (65) 99909-2153", ln=True, align="C")
        self.cell(0, 5, "Responsável: Valdevino", ln=True, align="C")
        self.cell(0, 5, "E-mail: vsmanutencaoeletrica70@gmail.com", ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-30)
        self.set_font("Arial", "I", 10)
        self.cell(0, 10, f"Documento gerado em: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align="C")
        self.cell(0, 10, "Validade do orçamento: 15 dias a partir da data de emissão.", ln=True, align="C")
        self.cell(0, 10, "Várzea Grande - MT", ln=True, align="C")

    def generate_client_details(self, client_name, client_cnpj, client_address, client_email, client_phone):
        self.set_font("Arial", "", 12)
        self.cell(0, 10, f"Cliente: {client_name}", ln=True)
        self.cell(0, 10, f"CNPJ/CPF: {client_cnpj}", ln=True)
        self.cell(0, 10, f"Endereço: {client_address}", ln=True)
        if client_email:
            self.cell(0, 10, f"E-mail: {client_email}", ln=True)
        if client_phone:
            self.cell(0, 10, f"Telefone: {client_phone}", ln=True)
        self.ln(10)

    def generate_service_table(self, services):
        self.set_font("Arial", "B", 12)
        self.cell(10, 10, "Item", border=1, align="C")
        self.cell(80, 10, "Descrição", border=1, align="C")
        self.cell(30, 10, "Quantidade", border=1, align="C")
        self.cell(40, 10, "Valor Unitário", border=1, align="C")
        self.cell(40, 10, "Total", border=1, align="C")
        self.ln()

        self.set_font("Arial", "", 12)
        for idx, service in enumerate(services, 1):
            self.cell(10, 10, str(idx), border=1, align="C")
            self.cell(80, 10, service["description"], border=1)
            self.cell(30, 10, str(service["quantity"]), border=1, align="C")
            self.cell(40, 10, f"R$ {service['unit_value']:.2f}", border=1, align="R")
            self.cell(40, 10, f"R$ {service['total']:.2f}", border=1, align="R")
            self.ln()

    def generate_total(self, total_value):
        self.ln(10)
        self.set_font("Arial", "B", 14)
        self.cell(150, 10, "VALOR TOTAL DA MÃO DE OBRA:", border=0, align="R")
        self.cell(40, 10, f"R$ {total_value:.2f}", border=1, align="R")

    def add_signature(self, signature_path):
        self.ln(10)
        self.cell(0, 10, "Atenciosamente,", ln=True, align="L")
        self.ln(20)
        if os.path.exists(signature_path):
            self.image(signature_path, x=80, w=60)
        self.cell(0, 10, "Valdevino da Silva Arruda", ln=True, align="L")

@app.route("/generate-pdf", methods=["POST"])
@login_required
def generate_pdf():
    try:
        data = request.json
        client_name = data["client_name"]
        client_cnpj = data["client_cnpj"]
        client_address = data["client_address"]
        client_email = data.get("client_email", "Não informado")
        client_phone = data.get("client_phone", "Não informado")
        services = data["services"]
        total_value = data["total_value"]

        pdf = PDF()
        pdf.add_page()
        pdf.generate_client_details(client_name, client_cnpj, client_address, client_email, client_phone)
        pdf.generate_service_table(services)
        pdf.generate_total(total_value)

        signature_path = os.path.join("static", "assinatura.jpg")
        pdf.add_signature(signature_path)

        sanitized_client_name = client_name.replace(" ", "_")
        pdf_filepath = os.path.join("static", f"{sanitized_client_name}.pdf")
        pdf.output(pdf_filepath)

        return jsonify({"message": "PDF gerado com sucesso!", "pdf_url": f"/static/{sanitized_client_name}.pdf"})
    except Exception as e:
        return jsonify({"message": "Erro ao gerar PDF.", "error": str(e)}), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)
