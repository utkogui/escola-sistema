from extensions import db
from datetime import datetime

class Turma(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    periodo = db.Column(db.String(20), nullable=False)  # Manhã, Tarde, Noite
    escola_id = db.Column(db.Integer, db.ForeignKey('escola.id'), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    escola = db.relationship('Escola', backref=db.backref('turmas', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'periodo': self.periodo,
            'escola_id': self.escola_id,
            'escola': self.escola.nome,
            'ativo': self.ativo,
            'criado_em': self.criado_em.isoformat(),
            'atualizado_em': self.atualizado_em.isoformat()
        }

    def __repr__(self):
        return f'<Turma {self.nome} - {self.escola.nome}>'