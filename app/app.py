from flask import Flask, jsonify, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from extensions import db, migrate, cors
import os

def create_app():
    app = Flask(__name__)
    
    # Configuração
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'escola.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'  # Necessário para sessões

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

    # Importar modelos para criar as tabelas
    from models.escola import Escola
    from models.professor import Professor
    from models.turma import Turma
    from models.aluno import Aluno
    from models.exercicio import Exercicio
    from models.resposta import Resposta

    @app.route('/')
    def index():
        """Página inicial com as três opções de acesso"""
        return render_template('index.html')

    @app.route('/limpar-sessao')
    def limpar_sessao():
        """Limpa a sessão e redireciona para a página inicial"""
        session.clear()
        return redirect(url_for('index'))

    # Tratamento de erros
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
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

    # Verificar se usuário está logado
    @app.before_request
    def check_session():
        # Lista de rotas que não precisam de sessão
        public_routes = ['index', 'static', 'limpar_sessao']
        
        # Verificar se a rota atual precisa de sessão
        if request.endpoint and request.endpoint.split('.')[-1] not in public_routes:
            # Verificar tipo de usuário baseado na URL
            if '/admin/' in request.path and 'admin_active' not in session:
                return redirect(url_for('index'))
            elif '/professor/' in request.path and 'professor_id' not in session:
                return redirect(url_for('index'))
            elif '/aluno/' in request.path and 'aluno_id' not in session:
                return redirect(url_for('index'))

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
            
        except Exception as e:
            print(f"Erro ao inicializar o banco de dados: {e}")
    
    app.run(debug=True, port=5001)