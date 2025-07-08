from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from fpdf import FPDF
import os
from datetime import datetime
import pytz

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
    "ADMIN": generate_password_hash("ADMIN123"),
}

# Banco de dados para clientes e orçamentos
CLIENTS_DB = {}

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
        logo_path = os.path.join("static", "logo.jpg")
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 33)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "V.S. MANUTENÇÃO ELÉTRICA", ln=True, align="C")
        self.set_font("Arial", "", 10)
        self.cell(0, 5, "Instalação e Manutenção de Ar-condicionado Split", ln=True, align="C")
        self.cell(0, 5, "CNPJ: 13.463.502/0001-09", ln=True, align="C")
        self.cell(0, 5, "Endereço: Rua 36, Bairro Jd. Ouro Verde, Várzea Grande - MT", ln=True, align="C")
        self.cell(0, 5, "Tel: (65) 3692-3238 | Cel: (65) 99909-2153", ln=True, align="C")
        self.cell(0, 5, "Responsável: Valdevino", ln=True, align="C")
        self.cell(0, 5, "E-mail: vsmanutencaoeletrica70@gmail.com", ln=True, align="C")
        self.ln(10)

    def footer(self):
        cuiaba_tz = pytz.timezone("America/Cuiaba")
        cuiaba_date = datetime.now(cuiaba_tz).strftime("%d/%m/%Y")
        
        self.set_y(-30)
        self.set_font("Arial", "", 10)
        self.cell(0, 10, f"Documento gerado em: {cuiaba_date}", ln=True, align="C")
        self.cell(0, 10, "Validade do orçamento: 15 dias a partir da data de emissão.", ln=True, align="C")

    def add_signature(self, signature_path):
        if os.path.exists(signature_path):
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
            return redirect(url_for("home"))
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
def home():
    return render_template("home.html", clients=CLIENTS_DB)

@app.route("/generate-budget")
@login_required
def generate_budget():
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

        # Salva os dados do cliente no banco de dados
        if client_name.lower() not in CLIENTS_DB:
            CLIENTS_DB[client_name.lower()] = {
                "name": client_name,
                "cnpj": client_cnpj,
                "address": client_address,
                "email": client_email,
                "phone": client_phone,
                "budgets": []
            }

        # Salva o orçamento no cliente
        cuiaba_tz = pytz.timezone("America/Cuiaba")
        current_date = datetime.now(cuiaba_tz).strftime("%d/%m/%Y")
        sanitized_client_name = client_name.replace(" ", "_")
        pdf_filename = f"{sanitized_client_name}_{current_date.replace('/', '-')}.pdf"
        pdf_filepath = os.path.join("static", pdf_filename)

        CLIENTS_DB[client_name.lower()]["budgets"].append({
            "date": current_date,
            "total_value": total_value,
            "link": f"/static/{pdf_filename}"
        })

        # Gerar PDF
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Cliente: {client_name}", ln=True)
        pdf.cell(0, 10, f"CNPJ/CPF: {client_cnpj}", ln=True)
        pdf.cell(0, 10, f"Endereço: {client_address}", ln=True)
        pdf.cell(0, 10, f"E-mail: {client_email}", ln=True)
        pdf.cell(0, 10, f"Telefone: {client_phone}", ln=True)
        pdf.ln(10)

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

        pdf.ln(10)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(150, 10, "VALOR TOTAL DA MÃO DE OBRA:", border=0, align="R")
        pdf.cell(40, 10, f"R$ {total_value:.2f}", border=1, align="R")

        signature_path = os.path.join("static", "assinatura.jpg")
        pdf.add_signature(signature_path)
        pdf.output(pdf_filepath)

        return jsonify({"message": "PDF gerado com sucesso!", "pdf_url": f"/static/{pdf_filename}"})
    except Exception as e:
        return jsonify({"message": "Erro ao gerar PDF.", "error": str(e)}), 500

@app.route("/get-client/<client_name>", methods=["GET"])
@login_required
def get_client(client_name):
    client_data = CLIENTS_DB.get(client_name.lower())
    if client_data:
        return jsonify(client_data)
    return jsonify({"message": "Cliente não encontrado"}), 404

if __name__ == "__main__":
    app.run(debug=True)
