from flask import Flask, jsonify
from extensions import db, migrate, cors
import os

def create_app():
    app = Flask(__name__)
    
    # Configuração
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'escola.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    # Registrar blueprints
    from routes.admin import admin
    app.register_blueprint(admin, url_prefix='/admin')

    @app.route('/')
    def hello():
        return jsonify({"message": "Bem-vindo ao Sistema Escolar!"})

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)