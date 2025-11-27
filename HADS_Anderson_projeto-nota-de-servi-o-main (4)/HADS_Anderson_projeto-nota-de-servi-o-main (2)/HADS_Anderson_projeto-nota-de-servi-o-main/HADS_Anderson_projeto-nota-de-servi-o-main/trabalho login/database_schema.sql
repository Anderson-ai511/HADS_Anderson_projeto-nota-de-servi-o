-- Script SQL para criar as tabelas no Supabase (PostgreSQL)

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user'
);

-- Tabela de clientes
CREATE TABLE IF NOT EXISTS clientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(100),
    endereco TEXT,
    cpf_cnpj VARCHAR(20),
    data_cadastro DATE DEFAULT CURRENT_DATE
);

-- Tabela de notas de serviço
CREATE TABLE IF NOT EXISTS notas_servico (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(id),
    nome_cliente VARCHAR(100) NOT NULL,
    local_atendimento VARCHAR(100) NOT NULL,
    dia DATE NOT NULL,
    tipo_servico VARCHAR(100) NOT NULL,
    observacao TEXT,
    valor DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'Aberta'
);


INSERT INTO usuarios (username, password, role) VALUES
('admin', 'admin123', 'admin')
ON CONFLICT (username) DO NOTHING;


INSERT INTO clientes (nome, telefone, email, endereco, cpf_cnpj) VALUES
('João Silva', '(11) 99999-9999', 'joao@email.com', 'Rua A, 123 - São Paulo', '123.456.789-00'),
('Maria Santos', '(21) 88888-8888', 'maria@email.com', 'Av. B, 456 - Rio de Janeiro', '987.654.321-00'),
('Empresa XYZ Ltda', '(31) 77777-7777', 'contato@empresa.com', 'Rua C, 789 - Belo Horizonte', '12.345.678/0001-90')
ON CONFLICT DO NOTHING;


INSERT INTO notas_servico (cliente_id, nome_cliente, local_atendimento, dia, tipo_servico, observacao, valor, status) VALUES
(1, 'João Silva', 'Local 1', '2024-01-15', 'Serviço A', 'Observação exemplo', 150.00, 'Aberta'),
(2, 'Maria Santos', 'Local 2', '2024-01-20', 'Serviço B', 'Outra observação', 200.00, 'Finalizada'),
(3, 'Empresa XYZ Ltda', 'Local 3', '2024-01-25', 'Serviço C', 'Serviço para empresa', 500.00, 'Aberta')
ON CONFLICT DO NOTHING;
