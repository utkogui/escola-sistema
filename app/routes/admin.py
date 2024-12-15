from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from models.escola import Escola
from models.professor import Professor
from models.turma import Turma
from models.aluno import Aluno
from extensions import db

admin = Blueprint('admin', __name__)

# ==================== View Routes ====================

@admin.route('/escolas/view')
def view_escolas():
    escolas = Escola.query.all()
    return render_template('escolas.html', escolas=escolas)

@admin.route('/professores/view')
def view_professores():
    professores = Professor.query.all()
    escolas = Escola.query.all()  # Mostra todas as escolas
    return render_template('professores.html', professores=professores, escolas=escolas)

@admin.route('/turmas/view')
def view_turmas():
    turmas = Turma.query.all()
    escolas = Escola.query.all()  # Mostra todas as escolas
    return render_template('turmas.html', turmas=turmas, escolas=escolas)

@admin.route('/alunos/view')
def view_alunos():
    alunos = Aluno.query.all()
    turmas = Turma.query.all()
    return render_template('alunos.html', alunos=alunos, turmas=turmas)

# ==================== Escola Routes ====================

@admin.route('/escola', methods=['POST'])
def criar_escola():
    try:
        if request.is_json:
            data = request.json
            if not data or 'nome' not in data:
                return jsonify({'erro': 'Nome da escola é obrigatório'}), 400
            
            escola_existente = Escola.query.filter_by(nome=data['nome']).first()
            if escola_existente:
                return jsonify({'erro': 'Já existe uma escola com esse nome'}), 400

            nova_escola = Escola(nome=data['nome'])
        else:
            nome = request.form['nome']
            escola_existente = Escola.query.filter_by(nome=nome).first()
            if escola_existente:
                return 'Já existe uma escola com esse nome', 400
            nova_escola = Escola(nome=nome)

        db.session.add(nova_escola)
        db.session.commit()
        
        if request.is_json:
            return jsonify(nova_escola.to_dict()), 201
        return redirect(url_for('admin.view_escolas'))

    except Exception as e:
        db.session.rollback()
        return str(e), 500

@admin.route('/escolas', methods=['GET'])
def listar_escolas():
    try:
        escolas = Escola.query.filter_by(ativo=True).all()
        return jsonify([escola.to_dict() for escola in escolas])
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@admin.route('/escola/<int:escola_id>', methods=['PUT'])
def atualizar_escola(escola_id):
    try:
        escola = Escola.query.get_or_404(escola_id)
        data = request.json
        
        if 'nome' in data:
            escola.nome = data['nome']
        
        db.session.commit()
        return jsonify(escola.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@admin.route('/escola/<int:escola_id>/delete', methods=['GET', 'DELETE'])
def deletar_escola(escola_id):
    try:
        escola = Escola.query.get_or_404(escola_id)
        escola.ativo = False
        db.session.commit()
        
        if request.method == 'DELETE':
            return jsonify({'mensagem': 'Escola desativada com sucesso'})
        return redirect(url_for('admin.view_escolas'))
    except Exception as e:
        db.session.rollback()
        if request.method == 'DELETE':
            return jsonify({'erro': str(e)}), 500
        return str(e), 400

# ==================== Professor Routes ====================

@admin.route('/professor', methods=['POST'])
def criar_professor():
    try:
        if request.is_json:
            data = request.json
            if not data or not all(k in data for k in ['nome', 'email', 'escola_id']):
                return jsonify({'erro': 'Nome, email e escola_id são obrigatórios'}), 400
        else:
            data = request.form

        escola = Escola.query.get(data['escola_id'])
        if not escola:
            return 'Escola não encontrada', 404

        professor_existente = Professor.query.filter_by(email=data['email']).first()
        if professor_existente:
            return 'Já existe um professor com esse email', 400

        novo_professor = Professor(
            nome=data['nome'],
            email=data['email'],
            escola_id=data['escola_id']
        )
        db.session.add(novo_professor)
        db.session.commit()
        
        if request.is_json:
            return jsonify(novo_professor.to_dict()), 201
        return redirect(url_for('admin.view_professores'))

    except Exception as e:
        db.session.rollback()
        return str(e), 500

@admin.route('/escola/<int:escola_id>/professores', methods=['GET'])
def listar_professores_escola(escola_id):
    try:
        escola = Escola.query.get_or_404(escola_id)
        professores = Professor.query.filter_by(escola_id=escola_id, ativo=True).all()
        return jsonify([professor.to_dict() for professor in professores])
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@admin.route('/professor/<int:professor_id>', methods=['PUT'])
def atualizar_professor(professor_id):
    try:
        professor = Professor.query.get_or_404(professor_id)
        data = request.json
        
        if 'nome' in data:
            professor.nome = data['nome']
        if 'email' in data:
            email_existente = Professor.query.filter(
                Professor.id != professor_id,
                Professor.email == data['email']
            ).first()
            if email_existente:
                return jsonify({'erro': 'Email já está em uso'}), 400
            professor.email = data['email']
        if 'escola_id' in data:
            escola = Escola.query.get(data['escola_id'])
            if not escola:
                return jsonify({'erro': 'Escola não encontrada'}), 404
            professor.escola_id = data['escola_id']
        
        db.session.commit()
        return jsonify(professor.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@admin.route('/professor/<int:professor_id>/delete', methods=['GET', 'DELETE'])
def deletar_professor(professor_id):
    try:
        professor = Professor.query.get_or_404(professor_id)
        professor.ativo = False
        db.session.commit()
        
        if request.method == 'DELETE':
            return jsonify({'mensagem': 'Professor desativado com sucesso'})
        return redirect(url_for('admin.view_professores'))
    except Exception as e:
        db.session.rollback()
        if request.method == 'DELETE':
            return jsonify({'erro': str(e)}), 500
        return str(e), 400

# ==================== Turma Routes ====================

@admin.route('/turma', methods=['POST'])
def criar_turma():
    try:
        if request.is_json:
            data = request.json
        else:
            data = request.form

        if not all(k in data for k in ['nome', 'periodo', 'escola_id']):
            return 'Nome, período e escola são obrigatórios', 400
        
        escola = Escola.query.get(data['escola_id'])
        if not escola:
            return 'Escola não encontrada', 404

        nova_turma = Turma(
            nome=data['nome'],
            periodo=data['periodo'],
            escola_id=data['escola_id']
        )
        db.session.add(nova_turma)
        db.session.commit()
        
        if request.is_json:
            return jsonify(nova_turma.to_dict()), 201
        return redirect(url_for('admin.view_turmas'))

    except Exception as e:
        db.session.rollback()
        return str(e), 500

@admin.route('/escola/<int:escola_id>/turmas', methods=['GET'])
def listar_turmas_escola(escola_id):
    try:
        escola = Escola.query.get_or_404(escola_id)
        turmas = Turma.query.filter_by(escola_id=escola_id, ativo=True).all()
        return jsonify([turma.to_dict() for turma in turmas])
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@admin.route('/turma/<int:turma_id>', methods=['PUT'])
def atualizar_turma(turma_id):
    try:
        turma = Turma.query.get_or_404(turma_id)
        data = request.json
        
        if 'nome' in data:
            turma.nome = data['nome']
        if 'periodo' in data:
            turma.periodo = data['periodo']
        if 'escola_id' in data:
            escola = Escola.query.get(data['escola_id'])
            if not escola:
                return jsonify({'erro': 'Escola não encontrada'}), 404
            turma.escola_id = data['escola_id']
        
        db.session.commit()
        return jsonify(turma.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@admin.route('/turma/<int:turma_id>/delete', methods=['GET', 'DELETE'])
def deletar_turma(turma_id):
    try:
        turma = Turma.query.get_or_404(turma_id)
        turma.ativo = False
        db.session.commit()
        
        if request.method == 'DELETE':
            return jsonify({'mensagem': 'Turma desativada com sucesso'})
        return redirect(url_for('admin.view_turmas'))
    except Exception as e:
        db.session.rollback()
        if request.method == 'DELETE':
            return jsonify({'erro': str(e)}), 500
        return str(e), 400

# ==================== Aluno Routes ====================

@admin.route('/alunos', methods=['POST'])
def criar_alunos():
    try:
        if request.is_json:
            data = request.json
            alunos_data = data.get('alunos', [])
            turma_id = data.get('turma_id')
        else:
            turma_id = request.form.get('turma_id')
            nomes = request.form.getlist('nomes[]')
            emails = request.form.getlist('emails[]')
            matriculas = request.form.getlist('matriculas[]')
            
            alunos_data = [
                {'nome': nome, 'email': email, 'matricula': matricula}
                for nome, email, matricula in zip(nomes, emails, matriculas)
            ]

        if not turma_id:
            return 'Turma é obrigatória', 400

        turma = Turma.query.get(turma_id)
        if not turma:
            return 'Turma não encontrada', 404

        alunos_criados = []
        for aluno_data in alunos_data:
            # Verifica se já existe aluno com mesmo email ou matrícula
            aluno_existente = Aluno.query.filter(
                (Aluno.email == aluno_data['email']) |
                (Aluno.matricula == aluno_data['matricula'])
            ).first()
            
            if aluno_existente:
                continue  # Pula este aluno e continua com o próximo

            novo_aluno = Aluno(
                nome=aluno_data['nome'],
                email=aluno_data['email'],
                matricula=aluno_data['matricula'],
                turma_id=turma_id
            )
            db.session.add(novo_aluno)
            alunos_criados.append(novo_aluno)

        db.session.commit()
        
        if request.is_json:
            return jsonify([aluno.to_dict() for aluno in alunos_criados]), 201
        return redirect(url_for('admin.view_alunos'))

    except Exception as e:
        db.session.rollback()
        return str(e), 500

@admin.route('/turma/<int:turma_id>/alunos', methods=['GET'])
def listar_alunos_turma(turma_id):
    try:
        turma = Turma.query.get_or_404(turma_id)
        alunos = Aluno.query.filter_by(turma_id=turma_id, ativo=True).all()
        return jsonify([aluno.to_dict() for aluno in alunos])
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@admin.route('/aluno/<int:aluno_id>', methods=['PUT'])
def atualizar_aluno(aluno_id):
    try:
        aluno = Aluno.query.get_or_404(aluno_id)
        data = request.json
        
        if 'nome' in data:
            aluno.nome = data['nome']
        if 'email' in data:
            email_existente = Aluno.query.filter(
                Aluno.id != aluno_id,
                Aluno.email == data['email']
            ).first()
            if email_existente:
                return jsonify({'erro': 'Email já está em uso'}), 400
            aluno.email = data['email']
        if 'matricula' in data:
            matricula_existente = Aluno.query.filter(
                Aluno.id != aluno_id,
                Aluno.matricula == data['matricula']
            ).first()
            if matricula_existente:
                return jsonify({'erro': 'Matrícula já está em uso'}), 400
            aluno.matricula = data['matricula']
        if 'turma_id' in data:
            turma = Turma.query.get(data['turma_id'])
            if not turma:
                return jsonify({'erro': 'Turma não encontrada'}), 404
            aluno.turma_id = data['turma_id']
        
        db.session.commit()
        return jsonify(aluno.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@admin.route('/aluno/<int:aluno_id>/delete', methods=['GET', 'DELETE'])
def deletar_aluno(aluno_id):
    try:
        aluno = Aluno.query.get_or_404(aluno_id)
        aluno.ativo = False
        db.session.commit()
        
        if request.method == 'DELETE':
            return jsonify({'mensagem': 'Aluno desativado com sucesso'})
        return redirect(url_for('admin.view_alunos'))
    except Exception as e:
        db.session.rollback()
        if request.method == 'DELETE':
            return jsonify({'erro': str(e)}), 500
        return str(e), 400