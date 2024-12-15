# Sistema Escolar

Sistema de gerenciamento escolar com módulos para administração, professores e alunos.

## Funcionalidades

- Módulo Administrativo
  - Gestão de Escolas
  - Gestão de Professores
  - Gestão de Turmas
  - Gestão de Alunos

- Módulo do Professor
  - Criação de Exercícios
  - Correção de Respostas
  - Dashboard com Visão Geral

- Módulo do Aluno
  - Visualização de Exercícios
  - Envio de Respostas
  - Acompanhamento de Notas

## Instalação

1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/escola-sistema.git
cd escola-sistema
```

2. Crie um ambiente virtual e ative-o
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
```

3. Instale as dependências
```bash
pip install -r requirements.txt
```

4. Execute a aplicação
```bash
cd app
python app.py
```

## Desenvolvimento

O projeto usa:
- Flask para o backend
- SQLite para desenvolvimento local
- PostgreSQL para produção