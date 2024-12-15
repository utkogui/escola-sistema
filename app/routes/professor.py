from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from models.professor import Professor
from models.exercicio import Exercicio
from models.resposta import Resposta
from models.turma import Turma
from models.aluno import Aluno
from extensions import db
from datetime import datetime

professor_bp = Blueprint('professor', __name__, url_prefix='/professor')

# ==================== View Routes ====================

@professor_bp.route('/dashboard')
def dashboard():
    # Temporariamente usando o primeiro professor
    # Depois implementaremos autenticação
    professor = Professor.query.first()
    if not professor:
        return "Nenhum professor encontrado", 404
        
    exercicios = Exercicio.query.filter_by(
        professor_id=professor.id,
        ativo=True
    ).order_by(Exercicio.data_criacao.desc()).all()
    
    return render_template('professor/dashboard.html', 
                         professor=professor, 
                         exercicios=exercicios)

# ==================== Exercício Routes ====================

@professor_bp.route('/exercicios/novo', methods=['GET', 'POST'])
def novo_exercicio():
    professor = Professor.query.first()  # Temporário até implementar autenticação
    if not professor:
        return "Nenhum professor encontrado", 404

    if request.method == 'POST':
        try:
            data = request.form
            data_entrega = datetime.strptime(data['data_entrega'], '%Y-%m-%d')
            
            exercicio = Exercicio(
                titulo=data['titulo'],
                descricao=data['descricao'],
                professor_id=professor.id,
                turma_id=data['turma_id'],
                data_entrega=data_entrega
            )
            
            # Se alunos foram selecionados
            alunos_ids = request.form.getlist('alunos')
            if alunos_ids:
                alunos = Aluno.query.filter(Aluno.id.in_(alunos_ids)).all()
                exercicio.alunos_designados.extend(alunos)
            
            db.session.add(exercicio)
            db.session.commit()
            
            return redirect(url_for('professor.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            return str(e), 400

    # GET: Mostrar formulário
    turmas = Turma.query.filter_by(escola_id=professor.escola_id).all()
    return render_template('professor/novo_exercicio.html',
                         professor=professor,
                         turmas=turmas)

@professor_bp.route('/exercicio/<int:exercicio_id>')
def ver_exercicio(exercicio_id):
    exercicio = Exercicio.query.get_or_404(exercicio_id)
    respostas = Resposta.query.filter_by(exercicio_id=exercicio_id).all()
    return render_template('professor/ver_exercicio.html', 
                         exercicio=exercicio,
                         respostas=respostas)

@professor_bp.route('/exercicio/<int:exercicio_id>/editar', methods=['GET', 'POST'])
def editar_exercicio(exercicio_id):
    exercicio = Exercicio.query.get_or_404(exercicio_id)
    professor = Professor.query.first()  # Temporário
    
    if request.method == 'POST':
        try:
            data = request.form
            data_entrega = datetime.strptime(data['data_entrega'], '%Y-%m-%d')
            
            exercicio.titulo = data['titulo']
            exercicio.descricao = data['descricao']
            exercicio.turma_id = data['turma_id']
            exercicio.data_entrega = data_entrega
            
            # Atualizar alunos designados
            alunos_ids = request.form.getlist('alunos')
            alunos = Aluno.query.filter(Aluno.id.in_(alunos_ids)).all()
            exercicio.alunos_designados = alunos
            
            db.session.commit()
            return redirect(url_for('professor.ver_exercicio', exercicio_id=exercicio.id))
            
        except Exception as e:
            db.session.rollback()
            return str(e), 400

    turmas = Turma.query.filter_by(escola_id=professor.escola_id).all()
    return render_template('professor/editar_exercicio.html',
                         exercicio=exercicio,
                         turmas=turmas)

# ==================== Correção Routes ====================

@professor_bp.route('/resposta/<int:resposta_id>/corrigir', methods=['POST'])
def corrigir_resposta(resposta_id):
    try:
        resposta = Resposta.query.get_or_404(resposta_id)
        data = request.json
        
        if 'nota' in data:
            resposta.nota = float(data['nota'])
        if 'comentario' in data:
            resposta.comentario_professor = data['comentario']
            
        db.session.commit()
        return jsonify(resposta.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

# ==================== Helpers ====================

@professor_bp.route('/turma/<int:turma_id>/alunos')
def get_alunos_turma(turma_id):
    """Rota auxiliar para carregar alunos de uma turma via AJAX"""
    alunos = Aluno.query.filter_by(turma_id=turma_id, ativo=True).all()
    return jsonify([{
        'id': aluno.id,
        'nome': aluno.nome,
        'email': aluno.email
    } for aluno in alunos])

@professor_bp.route('/exercicio/<int:exercicio_id>/respostas')
def get_respostas_exercicio(exercicio_id):
    """Rota auxiliar para carregar respostas de um exercício via AJAX"""
    respostas = Resposta.query.filter_by(exercicio_id=exercicio_id).all()
    return jsonify([resp.to_dict() for resp in respostas])