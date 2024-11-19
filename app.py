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
        self.set_font("Arial", "", 10)
        self.cell(0, 10, f"Documento gerado em: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align="C")
        self.cell(0, 10, "Validade do orçamento: 15 dias a partir da data de emissão.", ln=True, align="C")

    def add_signature(self, signature_path):
        self.set_y(-80)
        self.image(signature_path, x=70, w=70)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in USERS_DB and check_password_hash(USERS_DB[username], password):
            user = User(username)
            login_user(user)
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("index"))
        else:
            flash("Usuário ou senha inválidos.", "danger")

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    return render_template("index.html", username=current_user.id)

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

        # Informações do cliente
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Cliente: {client_name}", ln=True)
        pdf.cell(0, 10, f"CNPJ/CPF: {client_cnpj}", ln=True)
        pdf.cell(0, 10, f"Endereço: {client_address}", ln=True)
        pdf.cell(0, 10, f"E-mail: {client_email}", ln=True)
        pdf.cell(0, 10, f"Telefone: {client_phone}", ln=True)
        pdf.ln(10)

        # Tabela de serviços
        pdf.set_font("Arial", "B", 12)
        pdf.cell(80, 10, "Descrição", border=1)
        pdf.cell(30, 10, "Quantidade", border=1, align="C")
        pdf.cell(40, 10, "Valor Unitário", border=1, align="R")
        pdf.cell(40, 10, "Total", border=1, align="R")
        pdf.ln()

        pdf.set_font("Arial", "", 12)
        for service in services:
            pdf.cell(80, 10, service["description"], border=1)
            pdf.cell(30, 10, str(service["quantity"]), border=1, align="C")
            pdf.cell(40, 10, f"R$ {service['unit_value']:.2f}", border=1, align="R")
            pdf.cell(40, 10, f"R$ {service['total']:.2f}", border=1, align="R")
            pdf.ln()

        # Total da mão de obra
        pdf.ln(10)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(150, 10, "VALOR TOTAL DA MÃO DE OBRA:", border=0, align="R")
        pdf.cell(40, 10, f"R$ {total_value:.2f}", border=1, align="R")

        # Assinatura (se existir)
        signature_path = os.path.join("static", "assinatura.jpg")
        if os.path.exists(signature_path):
            pdf.add_signature(signature_path)

        # Salvar PDF
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
