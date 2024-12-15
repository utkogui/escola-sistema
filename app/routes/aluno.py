from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from models.aluno import Aluno
from models.exercicio import Exercicio
from models.resposta import Resposta
from extensions import db
from datetime import datetime

aluno_bp = Blueprint('aluno', __name__, url_prefix='/aluno')

@aluno_bp.route('/')
def index():
    return redirect(url_for('aluno.dashboard'))

@aluno_bp.route('/dashboard')
def dashboard():
    # Temporariamente usando o primeiro aluno
    # Depois implementaremos autenticação
    aluno = Aluno.query.first()
    if not aluno:
        return "Nenhum aluno encontrado", 404

    # Buscar exercícios designados para este aluno
    exercicios_pendentes = []
    exercicios_entregues = []
    
    for exercicio in aluno.exercicios:
        if exercicio.ativo:
            resposta = Resposta.query.filter_by(
                aluno_id=aluno.id,
                exercicio_id=exercicio.id
            ).first()
            
            if resposta:
                exercicios_entregues.append({
                    'exercicio': exercicio,
                    'resposta': resposta
                })
            else:
                exercicios_pendentes.append(exercicio)

    return render_template(
        'aluno/dashboard.html',
        aluno=aluno,
        exercicios_pendentes=exercicios_pendentes,
        exercicios_entregues=exercicios_entregues,
        now=datetime.now
    )

@aluno_bp.route('/exercicio/<int:exercicio_id>')
def ver_exercicio(exercicio_id):
    aluno = Aluno.query.first()  # Temporário
    exercicio = Exercicio.query.get_or_404(exercicio_id)
    
    # Verificar se o aluno tem acesso a este exercício
    if aluno not in exercicio.alunos_designados:
        return "Acesso não autorizado", 403

    # Verificar se já existe resposta
    resposta = Resposta.query.filter_by(
        aluno_id=aluno.id,
        exercicio_id=exercicio.id
    ).first()

    return render_template(
        'aluno/exercicio.html',
        exercicio=exercicio,
        resposta=resposta,
        now=datetime.now
    )

@aluno_bp.route('/exercicio/<int:exercicio_id>/responder', methods=['POST'])
def responder_exercicio(exercicio_id):
    try:
        aluno = Aluno.query.first()  # Temporário
        exercicio = Exercicio.query.get_or_404(exercicio_id)
        
        if aluno not in exercicio.alunos_designados:
            return "Acesso não autorizado", 403

        # Verificar se já existe resposta
        resposta_existente = Resposta.query.filter_by(
            aluno_id=aluno.id,
            exercicio_id=exercicio.id
        ).first()
        
        if resposta_existente:
            return "Exercício já respondido", 400

        # Verificar se está dentro do prazo
        if datetime.now() > exercicio.data_entrega:
            return "Prazo de entrega expirado", 400

        # Criar nova resposta
        resposta = Resposta(
            conteudo=request.form['conteudo'],
            aluno_id=aluno.id,
            exercicio_id=exercicio.id
        )
        
        db.session.add(resposta)
        db.session.commit()
        
        return redirect(url_for('aluno.dashboard'))

    except Exception as e:
        db.session.rollback()
        return str(e), 500

@aluno_bp.route('/resposta/<int:resposta_id>')
def ver_resposta(resposta_id):
    aluno = Aluno.query.first()  # Temporário
    resposta = Resposta.query.get_or_404(resposta_id)
    
    if resposta.aluno_id != aluno.id:
        return "Acesso não autorizado", 403

    # Buscar todas as respostas do exercício para poder navegar entre elas
    respostas_exercicio = Resposta.query.filter_by(
        exercicio_id=resposta.exercicio_id
    ).order_by(Resposta.data_envio).all()

    # Encontrar índices para navegação
    atual_index = respostas_exercicio.index(resposta)
    tem_anterior = atual_index > 0
    tem_proxima = atual_index < len(respostas_exercicio) - 1

    return render_template(
        'aluno/resposta.html', 
        resposta=resposta,
        tem_anterior=tem_anterior,
        tem_proxima=tem_proxima,
        resposta_anterior_id=respostas_exercicio[atual_index - 1].id if tem_anterior else None,
        resposta_proxima_id=respostas_exercicio[atual_index + 1].id if tem_proxima else None,
        now=datetime.now
    )

@aluno_bp.route('/exercicios/pendentes')
def listar_exercicios_pendentes():
    aluno = Aluno.query.first()  # Temporário
    if not aluno:
        return jsonify([])

    # Buscar exercícios sem resposta
    exercicios_pendentes = []
    for exercicio in aluno.exercicios:
        if exercicio.ativo:
            resposta = Resposta.query.filter_by(
                aluno_id=aluno.id,
                exercicio_id=exercicio.id
            ).first()
            
            if not resposta and exercicio.data_entrega > datetime.now():
                exercicios_pendentes.append(exercicio)

    return jsonify([{
        'id': ex.id,
        'titulo': ex.titulo,
        'professor': ex.professor.nome,
        'data_entrega': ex.data_entrega.strftime('%d/%m/%Y'),
        'dias_restantes': (ex.data_entrega - datetime.now()).days
    } for ex in exercicios_pendentes])

@aluno_bp.route('/exercicios/corrigidos')
def listar_exercicios_corrigidos():
    aluno = Aluno.query.first()  # Temporário
    if not aluno:
        return jsonify([])

    # Buscar respostas corrigidas
    respostas_corrigidas = Resposta.query.filter(
        Resposta.aluno_id == aluno.id,
        Resposta.nota != None  # Apenas respostas já corrigidas
    ).all()

    return jsonify([{
        'id': resp.id,
        'exercicio': resp.exercicio.titulo,
        'professor': resp.exercicio.professor.nome,
        'data_entrega': resp.data_envio.strftime('%d/%m/%Y'),
        'nota': resp.nota,
        'comentario': resp.comentario_professor
    } for resp in respostas_corrigidas])

# Rota para ver estatísticas do aluno
@aluno_bp.route('/estatisticas')
def ver_estatisticas():
    aluno = Aluno.query.first()  # Temporário
    if not aluno:
        return "Nenhum aluno encontrado", 404

    respostas = Resposta.query.filter_by(aluno_id=aluno.id).all()
    total_exercicios = len(aluno.exercicios)
    exercicios_respondidos = len(respostas)
    exercicios_corrigidos = len([r for r in respostas if r.nota is not None])
    media_notas = sum([r.nota for r in respostas if r.nota is not None]) / exercicios_corrigidos if exercicios_corrigidos > 0 else 0

    return render_template(
        'aluno/estatisticas.html',
        aluno=aluno,
        total_exercicios=total_exercicios,
        exercicios_respondidos=exercicios_respondidos,
        exercicios_corrigidos=exercicios_corrigidos,
        media_notas=media_notas,
        now=datetime.now
    )