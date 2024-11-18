
# Sistema de Geração de Orçamentos

Este é um sistema completo para gerar orçamentos em PDF, com suporte para assinatura digital. Ele está pronto para uso localmente e preparado para hospedagem em serviços como Oracle, Heroku ou outros.

## Funcionalidades
1. Formulário simples para preencher os dados do cliente e serviços.
2. Geração de PDF com design moderno e campo para assinatura.
3. Suporte para desenhar ou carregar assinatura no sistema.
4. Pronto para deploy com `requirements.txt` incluso.

## Como Rodar Localmente
1. Certifique-se de ter o Python instalado (>=3.7).
2. Instale as dependências com o comando:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute o servidor Flask:
   ```bash
   python app.py
   ```
4. Acesse o sistema no navegador em `http://127.0.0.1:5000`.

## Como Hospedar no Oracle ou Heroku
1. Suba todos os arquivos deste projeto para um repositório no GitHub.
2. Configure o ambiente no Oracle ou Heroku e use o comando:
   ```bash
   pip install -r requirements.txt
   ```
3. Defina a variável de ambiente `FLASK_APP` como `app.py`.
4. Inicie o aplicativo no Oracle ou Heroku.

## Estrutura de Arquivos
```
orcamento_sistema/
│
├── app.py               # Código do back-end Flask
├── requirements.txt     # Dependências para instalação
├── templates/
│   └── index.html       # Interface do sistema
└── static/
    └── (Assinaturas e PDFs gerados serão salvos aqui)
```

## Personalizações
- Para alterar o design do PDF, modifique o arquivo `app.py` na função `generate_pdf`.
- Para ajustar o front-end, edite o arquivo `templates/index.html`.

## Suporte
Entre em contato para suporte adicional ou personalizações.
