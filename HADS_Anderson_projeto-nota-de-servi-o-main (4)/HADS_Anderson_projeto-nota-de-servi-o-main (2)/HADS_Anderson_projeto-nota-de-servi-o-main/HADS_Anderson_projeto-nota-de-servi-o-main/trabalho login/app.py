from flask import Flask, render_template, request, redirect, url_for, flash
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()  # Carrega as variáveis do arquivo .env

app = Flask(__name__)
app.secret_key = 'chave_secreta_para_flash_messages'  # Chave secreta para mensagens flash (importante para segurança)

# Configuração do Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Lista de usuários para simulação (em produção, use banco de dados)
# Mantemos apenas um usuário de teste (admin) — as demais contas devem ser criadas via dashboard/DB
usuarios = [
    {'username': 'admin', 'password': 'admin123', 'role': 'admin'},
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
    # Primeiro tenta buscar no Supabase (persistente)
    try:
        resp = supabase.table('usuarios').select('*').eq('username', username).execute()
        if resp.data:
            db_user = resp.data[0]
            # Comparação simples por agora (plaintext). Considere hashing em produção.
            if db_user.get('password') == password:
                usuario_encontrado = db_user
    except Exception:
        # Falha na consulta Supabase — fallback para lista em memória
        usuario_encontrado = None

    # Se não encontrou no Supabase, usa a lista em memória (compatibilidade)
    if usuario_encontrado is None:
        for user in usuarios:
            if user['username'] == username and user['password'] == password:
                usuario_encontrado = user
                break

    if usuario_encontrado:
        flash('Login realizado com sucesso!', 'success')  # Mensagem de sucesso
        return redirect(url_for('notes'))  # Redireciona para notas
    else:
        flash('Credenciais inválidas. Tente novamente.', 'error')
        return redirect(url_for('login'))  # Redireciona de volta para login

@app.route('/dashboard')
def dashboard():
    # Rota do dashboard
    return render_template('dashboard.html')

@app.route('/create_note', methods=['GET', 'POST'])
def create_note():
    # Buscar clientes para o dropdown
    response_clientes = supabase.table('clientes').select('*').execute()
    clientes = response_clientes.data

    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id')
        local_atendimento = request.form.get('local_atendimento')
        dia = request.form.get('dia')
        tipo_servico = request.form.get('tipo_servico')
        observacao = request.form.get('observacao')
        valor_raw = request.form.get('valor')
        status = 'Aberta'  # Status inicial

        # Validations
        errors = []
        if not cliente_id:
            errors.append('Selecione um cliente antes de criar a nota.')
        try:
            valor = float(valor_raw)
        except (TypeError, ValueError):
            errors.append('Valor inválido.')

        # Se tiver erros, mostra mensagens e re-render
        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template('create_note.html', clientes=clientes)

        # Recupera o nome do cliente a partir do cliente selecionado
        nome_cliente = None
        try:
            resp = supabase.table('clientes').select('nome').eq('id', int(cliente_id)).execute()
            if resp.data and len(resp.data) > 0:
                nome_cliente = resp.data[0].get('nome')
            else:
                flash('Cliente não encontrado.', 'error')
                return render_template('create_note.html', clientes=clientes)
        except Exception as ex:
            flash('Erro ao buscar cliente: ' + str(ex), 'error')
            return render_template('create_note.html', clientes=clientes)

        nota = {
            'cliente_id': int(cliente_id),
            'nome_cliente': nome_cliente,
            'local_atendimento': local_atendimento,
            'dia': dia,
            'tipo_servico': tipo_servico,
            'observacao': observacao,
            'valor': valor,
            'status': status
        }
        try:
            supabase.table('notas_servico').insert(nota).execute()
            flash('Nota de serviço criada com sucesso!', 'success')
            return redirect(url_for('notes'))
        except Exception as ex:
            flash('Erro ao criar nota: ' + str(ex), 'error')
            return render_template('create_note.html', clientes=clientes)
    return render_template('create_note.html', clientes=clientes)

@app.route('/notes')
def notes():
    response = supabase.table('notas_servico').select('*').execute()
    notas_servico = response.data
    return render_template('notes.html', notas=notas_servico)

@app.route('/edit_note/<int:id>', methods=['GET', 'POST'])
def edit_note(id):
    response = supabase.table('notas_servico').select('*').eq('id', id).execute()
    nota = response.data[0] if response.data else None
    if not nota:
        flash('Nota não encontrada.', 'error')
        return redirect(url_for('notes'))

    if request.method == 'POST':
        updated_nota = {
            'nome_cliente': request.form.get('nome_cliente'),
            'local_atendimento': request.form.get('local_atendimento'),
            'dia': request.form.get('dia'),
            'tipo_servico': request.form.get('tipo_servico'),
            'observacao': request.form.get('observacao'),
            'valor': float(request.form.get('valor')),
            'status': request.form.get('status')
        }
        supabase.table('notas_servico').update(updated_nota).eq('id', id).execute()
        flash('Nota de serviço atualizada com sucesso!', 'success')
        return redirect(url_for('notes'))
    return render_template('edit_note.html', nota=nota)

@app.route('/delete_note/<int:id>', methods=['POST'])
def delete_note(id):
    supabase.table('notas_servico').delete().eq('id', id).execute()
    flash('Nota de serviço excluída com sucesso!', 'success')
    return redirect(url_for('notes'))

@app.route('/finalize_note/<int:id>', methods=['POST'])
def finalize_note(id):
    response = supabase.table('notas_servico').select('*').eq('id', id).execute()
    nota = response.data[0] if response.data else None
    if nota and nota['status'] == 'Aberta':
        supabase.table('notas_servico').update({'status': 'Finalizada'}).eq('id', id).execute()
        flash('Nota de serviço finalizada com sucesso!', 'success')
    else:
        flash('Nota não encontrada ou já finalizada.', 'error')
    return redirect(url_for('notes'))

# Rotas para gerenciamento de clientes
@app.route('/clients')
def clients():
    response = supabase.table('clientes').select('*').execute()
    clientes = response.data
    return render_template('clients.html', clientes=clientes)


@app.route('/users')
def users():
    # Lista todos os usuários registrados no Supabase
    try:
        response = supabase.table('usuarios').select('*').execute()
        usuarios_db = response.data or []
    except Exception:
        usuarios_db = []
    return render_template('users.html', usuarios=usuarios_db)


@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    # Criar novo usuário
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role') or 'user'

        user = {
            'username': username,
            'password': password,
            'role': role
        }
        supabase.table('usuarios').insert(user).execute()
        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('users'))
    return render_template('create_user.html')


@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    response = supabase.table('usuarios').select('*').eq('id', id).execute()
    usuario = response.data[0] if response.data else None
    if not usuario:
        flash('Usuário não encontrado.', 'error')
        return redirect(url_for('users'))

    if request.method == 'POST':
        updated = {
            'username': request.form.get('username'),
            'password': request.form.get('password'),
            'role': request.form.get('role')
        }
        supabase.table('usuarios').update(updated).eq('id', id).execute()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('users'))
    return render_template('edit_user.html', usuario=usuario)


@app.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    supabase.table('usuarios').delete().eq('id', id).execute()
    flash('Usuário excluído com sucesso!', 'success')
    return redirect(url_for('users'))

@app.route('/create_client', methods=['GET', 'POST'])
def create_client():
    if request.method == 'POST':
        nome = (request.form.get('nome') or '').strip()
        telefone = (request.form.get('telefone') or '').strip()
        email = (request.form.get('email') or '').strip()
        endereco = (request.form.get('endereco') or '').strip()
        cpf_cnpj = (request.form.get('cpf_cnpj') or '').strip()

        # Validação simples dos campos (pode ser expandida conforme necessário)
        errors = []
        if not nome:
            errors.append('O nome é obrigatório.')
        if not telefone:
            errors.append('Telefone é obrigatório.')
        if email and '@' not in email:
            errors.append('Email inválido.')
        if not cpf_cnpj:
            errors.append('CPF/CNPJ é obrigatório.')

        if errors:
            for e in errors:
                flash(e, 'error')
            # re-render com valores preenchidos para correção
            return render_template('create_client.html', nome=nome, telefone=telefone, email=email, endereco=endereco, cpf_cnpj=cpf_cnpj)

        cliente = {
            'nome': nome,
            'telefone': telefone,
            'email': email,
            'endereco': endereco,
            'cpf_cnpj': cpf_cnpj
        }
        try:
            supabase.table('clientes').insert(cliente).execute()
            flash('Cliente criado com sucesso!', 'success')
            return redirect(url_for('clients'))
        except Exception as ex:
            # Em caso de problema com a inserção no Supabase, mostra mensagem amigável
            flash('Erro ao salvar cliente: ' + str(ex), 'error')
            return render_template('create_client.html', nome=nome, telefone=telefone, email=email, endereco=endereco, cpf_cnpj=cpf_cnpj)
    return render_template('create_client.html')

@app.route('/edit_client/<int:id>', methods=['GET', 'POST'])
def edit_client(id):
    response = supabase.table('clientes').select('*').eq('id', id).execute()
    cliente = response.data[0] if response.data else None
    if not cliente:
        flash('Cliente não encontrado.', 'error')
        return redirect(url_for('clients'))

    if request.method == 'POST':
        updated_cliente = {
            'nome': request.form.get('nome'),
            'telefone': request.form.get('telefone'),
            'email': request.form.get('email'),
            'endereco': request.form.get('endereco'),
            'cpf_cnpj': request.form.get('cpf_cnpj')
        }
        supabase.table('clientes').update(updated_cliente).eq('id', id).execute()
        flash('Cliente atualizado com sucesso!', 'success')
        return redirect(url_for('clients'))
    return render_template('edit_client.html', cliente=cliente)

@app.route('/delete_client/<int:id>', methods=['POST'])
def delete_client(id):
    supabase.table('clientes').delete().eq('id', id).execute()
    flash('Cliente excluído com sucesso!', 'success')
    return redirect(url_for('clients'))

if __name__ == '__main__':
    # Para desenvolvimento: expor em todas as interfaces para permitir acesso pela rede local
    # Atenção: usar 0.0.0.0 expõe o servidor em toda a máquina. Não usar em produção sem um WSGI seguro.
    app.run(debug=True, host='0.0.0.0', port=5000)
