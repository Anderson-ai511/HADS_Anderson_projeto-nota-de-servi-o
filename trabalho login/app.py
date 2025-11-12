from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'chave_secreta_para_flash_messages'  # Chave secreta para mensagens flash (importante para segurança)

# Lista de usuários para simulação (em produção, use banco de dados)
usuarios = [
    {'username': 'admin', 'password': 'admin123', 'role': 'admin'},  # Usuário admin criado
    {'username': 'user1', 'password': 'pass1', 'role': 'user'},
    {'username': 'user2', 'password': 'pass2', 'role': 'user'}
]

# Lista de notas de serviço (em memória, para simulação)
notas_servico = []

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
        return redirect(url_for('notes'))  # Redireciona para notas
    else:
        flash('Credenciais inválidas. Tente novamente.', 'error')  # Mensagem de erro
        return redirect(url_for('login'))  # Redireciona de volta para login

@app.route('/dashboard')
def dashboard():
    # Rota do dashboard: exibe uma tela simples de boas-vindas
    return render_template('dashboard.html')

@app.route('/create_note', methods=['GET', 'POST'])
def create_note():
    if request.method == 'POST':
        nome_cliente = request.form.get('nome_cliente')
        local_atendimento = request.form.get('local_atendimento')
        dia = request.form.get('dia')
        tipo_servico = request.form.get('tipo_servico')
        observacao = request.form.get('observacao')
        valor = float(request.form.get('valor'))
        status = 'Aberta'  # Status inicial

        nota = {
            'id': len(notas_servico) + 1,
            'nome_cliente': nome_cliente,
            'local_atendimento': local_atendimento,
            'dia': dia,
            'tipo_servico': tipo_servico,
            'observacao': observacao,
            'valor': valor,
            'status': status
        }
        notas_servico.append(nota)
        flash('Nota de serviço criada com sucesso!', 'success')
        return redirect(url_for('notes'))
    return render_template('create_note.html')

@app.route('/notes')
def notes():
    return render_template('notes.html', notas=notas_servico)

@app.route('/edit_note/<int:id>', methods=['GET', 'POST'])
def edit_note(id):
    nota = next((n for n in notas_servico if n['id'] == id), None)
    if not nota:
        flash('Nota não encontrada.', 'error')
        return redirect(url_for('notes'))

    if request.method == 'POST':
        nota['nome_cliente'] = request.form.get('nome_cliente')
        nota['local_atendimento'] = request.form.get('local_atendimento')
        nota['dia'] = request.form.get('dia')
        nota['tipo_servico'] = request.form.get('tipo_servico')
        nota['observacao'] = request.form.get('observacao')
        nota['valor'] = float(request.form.get('valor'))
        nota['status'] = request.form.get('status')
        flash('Nota de serviço atualizada com sucesso!', 'success')
        return redirect(url_for('notes'))
    return render_template('edit_note.html', nota=nota)

@app.route('/delete_note/<int:id>', methods=['POST'])
def delete_note(id):
    global notas_servico
    notas_servico = [n for n in notas_servico if n['id'] != id]
    flash('Nota de serviço excluída com sucesso!', 'success')
    return redirect(url_for('notes'))

@app.route('/finalize_note/<int:id>', methods=['POST'])
def finalize_note(id):
    nota = next((n for n in notas_servico if n['id'] == id), None)
    if nota and nota['status'] == 'Aberta':
        nota['status'] = 'Finalizada'
        flash('Nota de serviço finalizada com sucesso!', 'success')
    else:
        flash('Nota não encontrada ou já finalizada.', 'error')
    return redirect(url_for('notes'))

if __name__ == '__main__':
    app.run(debug=True)  # Executa o app em modo debug (facilita desenvolvimento)
