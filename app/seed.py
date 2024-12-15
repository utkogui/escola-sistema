from app import create_app, db
from models.escola import Escola
from models.professor import Professor
from models.turma import Turma
from models.aluno import Aluno
from models.exercicio import Exercicio
from datetime import datetime, timedelta

def seed_database():
    app = create_app()
    
    with app.app_context():
        # Limpar banco de dados existente
        db.drop_all()
        db.create_all()

        # Criar escolas
        escolas = [
            Escola(nome="Colégio São José"),
            Escola(nome="Escola Santos Dumont"),
            Escola(nome="Instituto Maria Montessori"),
            Escola(nome="Colégio Dom Pedro")
        ]
        db.session.add_all(escolas)
        db.session.commit()

        # Criar professores
        professores = [
            Professor(
                nome="João Silva",
                email="joao.silva@escola.com",
                escola_id=escolas[0].id
            ),
            Professor(
                nome="Maria Santos",
                email="maria.santos@escola.com",
                escola_id=escolas[1].id
            ),
            Professor(
                nome="Pedro Almeida",
                email="pedro.almeida@escola.com",
                escola_id=escolas[2].id
            ),
            Professor(
                nome="Ana Beatriz Costa",
                email="ana.costa@escola.com",
                escola_id=escolas[3].id
            )
        ]
        db.session.add_all(professores)
        db.session.commit()

        # Criar turmas
        turmas = [
            Turma(
                nome="1º Ano A",
                periodo="Manhã",
                escola_id=escolas[0].id
            ),
            Turma(
                nome="2º Ano B",
                periodo="Tarde",
                escola_id=escolas[0].id
            ),
            Turma(
                nome="3º Ano A",
                periodo="Manhã",
                escola_id=escolas[1].id
            ),
            Turma(
                nome="9º Ano B",
                periodo="Tarde",
                escola_id=escolas[1].id
            )
        ]
        db.session.add_all(turmas)
        db.session.commit()

        # Criar alunos
        alunos = [
            Aluno(
                nome="Lucas Mendes",
                email="lucas.mendes@aluno.com",
                matricula="2024001",
                turma_id=turmas[0].id
            ),
            Aluno(
                nome="Julia Costa",
                email="julia.costa@aluno.com",
                matricula="2024002",
                turma_id=turmas[0].id
            ),
            Aluno(
                nome="Gabriel Santos",
                email="gabriel.santos@aluno.com",
                matricula="2024003",
                turma_id=turmas[1].id
            ),
            Aluno(
                nome="Mariana Oliveira",
                email="mariana.oliveira@aluno.com",
                matricula="2024004",
                turma_id=turmas[1].id
            )
        ]
        db.session.add_all(alunos)
        db.session.commit()

        # Criar exercícios
        data_atual = datetime.now()
        exercicios = [
            Exercicio(
                titulo="Introdução à Matemática Básica",
                descricao="Resolver problemas de adição e subtração com números naturais.",
                professor_id=professores[0].id,
                turma_id=turmas[0].id,
                data_entrega=data_atual + timedelta(days=7)
            ),
            Exercicio(
                titulo="Compreensão de Texto",
                descricao="Ler o texto fornecido e responder às questões interpretativas.",
                professor_id=professores[0].id,
                turma_id=turmas[0].id,
                data_entrega=data_atual + timedelta(days=5)
            ),
            Exercicio(
                titulo="Geografia: Países e Capitais",
                descricao="Identificar as capitais dos países da América do Sul.",
                professor_id=professores[1].id,
                turma_id=turmas[1].id,
                data_entrega=data_atual + timedelta(days=10)
            ),
            Exercicio(
                titulo="Ciências: Sistema Solar",
                descricao="Pesquisar e apresentar informações sobre os planetas do Sistema Solar.",
                professor_id=professores[1].id,
                turma_id=turmas[1].id,
                data_entrega=data_atual + timedelta(days=14)
            )
        ]
        db.session.add_all(exercicios)
        
        # Associar alunos aos exercícios
        exercicios[0].alunos_designados.extend([alunos[0], alunos[1]])
        exercicios[1].alunos_designados.extend([alunos[0], alunos[1]])
        exercicios[2].alunos_designados.extend([alunos[2], alunos[3]])
        exercicios[3].alunos_designados.extend([alunos[2], alunos[3]])
        
        db.session.commit()

        print("Banco de dados populado com sucesso!")
        print("\nDados criados:")
        print(f"- {len(escolas)} escolas")
        print(f"- {len(professores)} professores")
        print(f"- {len(turmas)} turmas")
        print(f"- {len(alunos)} alunos")
        print(f"- {len(exercicios)} exercícios")

if __name__ == "__main__":
    seed_database()