from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'chave_secreta_para_flash_messages'  # Chave secreta para mensagens flash (importante para segurança)

# Lista de usuários para simulação (em produção, use banco de dados)
usuarios = [
    {'username': 'admin', 'password': 'admin123', 'role': 'admin'},  # Usuário admin criado
    {'username': 'user1', 'password': 'pass1', 'role': 'user'},  
    {'username': 'user2', 'password': 'pass2', 'role': 'user'}   
]

@app.route('/')
def login():
    # Rota principal: renderiza o template de login
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def fazer_login():
    # Rota para processar o login via POST
    username = request.form.get('username')  # Obtém o nome de usuário do formulário
    password = request.form.get('password')  # Obtém a senha do formulário

    # Verifica se as credenciais estão corretas
    usuario_encontrado = None
    for user in usuarios:
        if user['username'] == username and user['password'] == password:
            usuario_encontrado = user
            break
    if usuario_encontrado:
        flash('Login realizado com sucesso!', 'success')  # Mensagem de sucesso
        return redirect(url_for('dashboard'))  # Redireciona para dashboard
    else:
        flash('Credenciais inválidas. Tente novamente.', 'error')  # Mensagem de erro
        return redirect(url_for('login'))  # Redireciona de volta para login

@app.route('/dashboard')
def dashboard():
    # Rota do dashboard: exibe uma tela simples de boas-vindas
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)  # Executa o app em modo debug (facilita desenvolvimento)
