from extensions import db
from datetime import datetime

class Exercicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'), nullable=False)
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_entrega = db.Column(db.DateTime, nullable=False)
    ativo = db.Column(db.Boolean, default=True)

    # Relacionamentos
    professor = db.relationship('Professor', backref=db.backref('exercicios', lazy=True))
    turma = db.relationship('Turma', backref=db.backref('exercicios', lazy=True))
    
    # Relacionamento com alunos designados para este exercício
    alunos_designados = db.relationship('Aluno', 
                                      secondary='exercicio_aluno',
                                      backref=db.backref('exercicios', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'professor_id': self.professor_id,
            'professor_nome': self.professor.nome,
            'turma_id': self.turma_id,
            'turma_nome': self.turma.nome,
            'data_criacao': self.data_criacao.isoformat(),
            'data_entrega': self.data_entrega.isoformat(),
            'ativo': self.ativo,
            'alunos_designados': [aluno.to_dict() for aluno in self.alunos_designados]
        }

# Tabela de associação entre Exercício e Aluno
exercicio_aluno = db.Table('exercicio_aluno',
    db.Column('exercicio_id', db.Integer, db.ForeignKey('exercicio.id'), primary_key=True),
    db.Column('aluno_id', db.Integer, db.ForeignKey('aluno.id'), primary_key=True),
    db.Column('data_designacao', db.DateTime, default=datetime.utcnow)
)