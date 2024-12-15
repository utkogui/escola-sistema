from extensions import db
from datetime import datetime

class Resposta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.Text, nullable=False)
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)
    exercicio_id = db.Column(db.Integer, db.ForeignKey('exercicio.id'), nullable=False)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)
    nota = db.Column(db.Float, nullable=True)
    comentario_professor = db.Column(db.Text, nullable=True)
    
    # Relacionamentos
    aluno = db.relationship('Aluno', backref=db.backref('respostas', lazy=True))
    exercicio = db.relationship('Exercicio', backref=db.backref('respostas', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'conteudo': self.conteudo,
            'aluno_id': self.aluno_id,
            'aluno_nome': self.aluno.nome,
            'exercicio_id': self.exercicio_id,
            'exercicio_titulo': self.exercicio.titulo,
            'data_envio': self.data_envio.isoformat(),
            'nota': self.nota,
            'comentario_professor': self.comentario_professor
        }