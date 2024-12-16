import os
from flask import Flask, jsonify, render_template, session, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from extensions import db, migrate, cors
from models.escola import Escola
from models.professor import Professor
from models.turma import Turma
from models.aluno import Aluno
from models.exercicio import Exercicio
from models.resposta import Resposta

def create_app():
    app = Flask(__name__)
    
    # Configuração do banco de dados
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    if DATABASE_URL:
        print(f"Usando banco de dados: {DATABASE_URL}")
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    else:
        print("DATABASE_URL não encontrada, usando SQLite")
        basedir = os.path.abspath(os.path.dirname(__file__))
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'escola.db')

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sua_chave_secreta_aqui')

    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    # Registrar blueprints
    from routes.admin import admin
    from routes.professor import professor_bp
    from routes.aluno import aluno_bp
    
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(professor_bp)
    app.register_blueprint(aluno_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/limpar-sessao')
    def limpar_sessao():
        session.clear()
        return redirect(url_for('index'))

    # Tratamento de erros
    @app.errorhandler(400)
    def bad_request_error(error):
        return render_template('errors/400.html'), 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        return render_template('errors/401.html'), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Erro 500: {str(error)}")
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Erro não tratado: {str(e)}")
        if db.session:
            db.session.rollback()
        return render_template('errors/500.html'), 500

    # Funções utilitárias para templates
    @app.context_processor
    def utility_processor():
        def format_date(date):
            if date:
                return date.strftime('%d/%m/%Y')
            return ''
        return dict(format_date=format_date)

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        try:
            # Criar todas as tabelas
            db.create_all()
            
            # Verificar se já existem dados no banco
            if not Escola.query.first():
                print("Banco de dados vazio. Executando seed...")
                from seed import seed_database
                seed_database()
                print("Seed executado com sucesso!")
            else:
                print("Banco de dados já contém dados. Pulando seed.")
        except Exception as e:
            print(f"Erro ao inicializar o banco de dados: {e}")
            if db.session:
                db.session.rollback()
    
    # Ajuste do host e porta para compatibilidade com Render.com
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
