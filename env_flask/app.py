from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
import os


# Inicializar a aplicação
app = Flask(__name__)

# Configuração do banco de dados
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'expedicoes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar o banco de dados e o Marshmallow
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Missao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    data_lancamento = db.Column(db.Date, nullable=False)
    destino = db.Column(db.String(100), nullable=False)
    estado_missao = db.Column(db.String(50), nullable=False)
    tripulacao = db.Column(db.String(200), nullable=True)
    carga_util = db.Column(db.String(200), nullable=True)
    duracao = db.Column(db.String(50), nullable=True)
    custo = db.Column(db.Float, nullable=True)
    status_detalhado = db.Column(db.Text, nullable=True)

# Criar o banco de dados
with app.app_context():
    db.create_all()


class MissaoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Missao

missao_schema = MissaoSchema()
missoes_schema = MissaoSchema(many=True)    


@app.route('/missao', methods=['POST'])
def add_missao():
    try:
        nome = request.json['nome']
        # Converter a string de data para um objeto date
        data_lancamento = datetime.strptime(request.json['data_lancamento'], '%Y-%m-%d').date()
        destino = request.json['destino']
        estado_missao = request.json['estado_missao']
        tripulacao = request.json.get('tripulacao')
        carga_util = request.json.get('carga_util')
        duracao = request.json.get('duracao')
        custo = request.json.get('custo')
        status_detalhado = request.json.get('status_detalhado')

        nova_missao = Missao(
            nome=nome, data_lancamento=data_lancamento, destino=destino,
            estado_missao=estado_missao, tripulacao=tripulacao, carga_util=carga_util,
            duracao=duracao, custo=custo, status_detalhado=status_detalhado
        )
        db.session.add(nova_missao)
        db.session.commit()
        return missao_schema.jsonify(nova_missao)
    except Exception as e:
        print(f"Erro ao adicionar missão: {e}")
        return jsonify({"error": "Erro ao processar a requisição"}), 500


@app.route('/missoes', methods=['GET'])
def get_missoes():
    todas_missoes = Missao.query.order_by(Missao.data_lancamento.desc()).all()
    return missoes_schema.jsonify(todas_missoes)

@app.route('/missao/<int:id>', methods=['GET'])
def get_missao(id):
    missao = Missao.query.get(id)
    if not missao:
        return jsonify({"message": "Missão não encontrada"}), 404
    return missao_schema.jsonify(missao)    



@app.route('/missoes/pesquisa', methods=['GET'])
def pesquisar_missoes_por_data():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    # Verificar se ambas as datas foram fornecidas
    if not data_inicio or not data_fim:
        return jsonify({"message": "Por favor, forneça as datas de início e fim."}), 400

    try:
        # Converter as strings para objetos de data
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"message": "As datas devem estar no formato YYYY-MM-DD."}), 400

    # Filtrar as missões com base no intervalo de datas
    missoes = Missao.query.filter(Missao.data_lancamento >= data_inicio, Missao.data_lancamento <= data_fim).order_by(Missao.data_lancamento.desc()).all()
    return missoes_schema.jsonify(missoes)



@app.route('/missao/<id>', methods=['PUT'])
def update_missao(id):
    missao = Missao.query.get(id)
    if not missao:
        return jsonify({"message": "Missão não encontrada"}), 404

    # Verifica se o campo existe antes de tentar acessá-lo
    missao.nome = request.json.get('nome', missao.nome)
    missao.data_lancamento = datetime.strptime(request.json.get('data_lancamento', missao.data_lancamento.strftime('%Y-%m-%d')), '%Y-%m-%d').date()
    missao.destino = request.json.get('destino', missao.destino)
    missao.estado_missao = request.json.get('estado_missao', missao.estado_missao)
    missao.tripulacao = request.json.get('tripulacao', missao.tripulacao)
    missao.carga_util = request.json.get('carga_util', missao.carga_util)
    missao.duracao = request.json.get('duracao', missao.duracao)
    missao.custo = request.json.get('custo', missao.custo)
    missao.status_detalhado = request.json.get('status_detalhado', missao.status_detalhado)

    db.session.commit()
    return missao_schema.jsonify(missao)


@app.route('/missao/<id>', methods=['DELETE'])
def delete_missao(id):
    missao = Missao.query.get(id)
    if not missao:
        return jsonify({"message": "Missão não encontrada"}), 404

    db.session.delete(missao)
    db.session.commit()
    return jsonify({"message": "Missão excluída com sucesso"})


if __name__ == '__main__':
    app.run(debug=True)
