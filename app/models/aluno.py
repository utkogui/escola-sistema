from extensions import db
from datetime import datetime

class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    matricula = db.Column(db.String(20), unique=True, nullable=False)
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    turma = db.relationship('Turma', backref=db.backref('alunos', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'matricula': self.matricula,
            'turma_id': self.turma_id,
            'turma': self.turma.nome,
            'escola': self.turma.escola.nome,
            'ativo': self.ativo,
            'criado_em': self.criado_em.isoformat(),
            'atualizado_em': self.atualizado_em.isoformat()
        }

    def __repr__(self):
        return f'<Aluno {self.nome}>'