from flask import Flask, request,jsonify
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os
from bson.objectid import ObjectId
import pymongo
from datetime import datetime, timedelta

load_dotenv('.cred')
app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)


@app.route('/usuarios', methods=['POST'])
def post_user():
    
    data = request.json

    if "cpf" not in data or data["cpf"].strip() == "":
        return {"erro": "CPF incompleto"}, 400
    if "nome" not in data:
        return {"erro": "nome é obrigatório"}, 400
    if "data_nascimento" not in data:
        return {"erro": "data_nascimento é obrigatório"}, 400
    
    if mongo.db.usuarios.find_one({"cpf": data["cpf"]}):
        return {"erro": "CPF já cadastrado"}, 400
    
    if mongo.db.usuarios.find_one({"cpf":""}):
        return {"erro": "CPF incompleto"}, 400

    result = mongo.db.usuarios.insert_one(data)

    return {"id": str(result.inserted_id)}, 201


@app.route('/usuarios', methods=['GET'])
def get_all_users():

    filtro = {}
    projecao = {"_id" : 0}
    dados_usuarios = mongo.db.usuarios.find(filtro, projecao)

    resp = {
        "usuarios": list( dados_usuarios )
    }

    return resp, 200


@app.route('/usuarios/<string:id>', methods=['GET'])
def get_user_by_id(id):

    try:
        usuario = mongo.db.usuarios.find_one({"_id": ObjectId(id)})
        
        if usuario:
            usuario['_id'] = str(usuario['_id'])
            return jsonify(usuario), 200
        else:
            return {"erro": "Usuário não encontrado"}, 404
    except Exception as e:
        return {"erro": "ID inválido"}, 400


@app.route('/usuarios/<string:id>', methods=['DELETE'])
def delete_user_by_id(id):

    try:
        result = mongo.db.usuarios.delete_one({"_id": ObjectId(id)})
        
        if result.deleted_count == 1:
            return {"message": "Usuário deletado com sucesso"}, 200
        else: 
            return {"erro": "Usuário não encontrado"}, 404
    except Exception as e:
        return {"erro": "ID inválido"}, 400


@app.route('/usuarios/<string:id>/', methods=['PUT'])
def update_by_id_user(id):
    data = request.json
    
    if "nome" not in data:
        return {"erro": "nome é obrigatório"}, 400
    if "cpf" not in data:
        return {"erro": "cpf é obrigatório"}, 400
    if "data_nascimento" not in data:
        return {"erro": "data de nascimento é obrigatória"}, 400
    
    try:
        result = mongo.db.usuarios.update_one(
            {"_id": ObjectId(id)},  
            {"$set": {
                "nome": data["nome"],
                "cpf": data["cpf"],
                "data_nascimento": data["data_nascimento"]
            }}  
        )
        
        if result.matched_count == 1:
            return {"message": "Atualização realizada com sucesso"}, 200
        else:
            return {"erro": "Erro ao atualizar dados"}, 404
    except Exception as e:
        return {"erro": "ID inválido"}, 400


@app.route('/bikes', methods=['POST'])
def post_bici():

    data = request.json


    if "marca" not in data:
        return {"erro": "marca é obrigatório"}, 400
    if "modelo" not in data:
        return {"erro": "modelo é obrigatório"}, 400
    if "cidade_alocada" not in data:
        return {"erro": "cidade alocada é obrigatório"}, 400


    data["status"] = "disponível"



    result = mongo.db.bicicletas.insert_one(data)

    return {"id": str(result.inserted_id)}, 201



@app.route('/bikes', methods=['GET'])
def get_all_bici():
    filtro = {}
    dados_bicicletas = mongo.db.bicicletas.find(filtro)

    resp = {
        "bicicletas": [
            {
                "_id": str(bici["_id"]),
                "marca": bici["marca"],
                "modelo": bici["modelo"],
                "cidade_alocada": bici["cidade_alocada"],
                "status": bici["status"]
            } for bici in dados_bicicletas
        ]
    }

    return resp, 200


@app.route('/bikes/<string:id>', methods=['GET'])
def get_bici_by_id(id):

    try:
        bicicleta = mongo.db.bicicletas.find_one({"_id": ObjectId(id)})
        
        if bicicleta:
            bicicleta['_id'] = str(bicicleta['_id'])
            return jsonify(bicicleta), 200
        else:
            return {"erro": "Usuário não encontrado"}, 404
    except Exception as e:
        return {"erro": "ID inválido"}, 400

@app.route('/bikes/<string:id>', methods=['DELETE'])
def delete_bici_by_id(id):

    try:
        result = mongo.db.bicicletas.delete_one({"_id": ObjectId(id)})
        
        if result.deleted_count == 1:
            return {"message": "Bicicleta deletado com sucesso"}, 200
        else: 
            return {"erro": "Bicicleta não encontrado"}, 404
    except Exception as e:
        return {"erro": "ID inválido"}, 400


@app.route('/bikes/<string:id>/', methods=['PUT'])
def update_by_id_bici(id):
    data = request.json
    
    if "marca" not in data:
        return {"erro": "marca é obrigatório"}, 400
    if "modelo" not in data:
        return {"erro": "modelo é obrigatório"}, 400
    if "cidade_alocada" not in data:
        return {"erro": "cidade alocada é obrigatória"}, 400
    
    try:
        result = mongo.db.usuarios.update_one(
            {"_id": ObjectId(id)},  
            {"$set": {
                "marca": data["marca"],
                "modelo": data["modelo"],
                "cidade_alocada": data["cidade_alocada"]
            }}  
        )
        
        if result.matched_count == 1:
            return {"message": "Atualização realizada com sucesso"}, 200
        else:
            return {"erro": "Erro ao atualizar dados"}, 404
    except Exception as e:
        return {"erro": "ID inválido"}, 400



@app.route('/emprestimos/usuarios/<string:id_usuario>/bikes/<string:id_bike>', methods=['POST'])
def realizar_emprestimo(id_usuario, id_bike):

    usuario = mongo.db.usuarios.find_one({"_id": ObjectId(id_usuario)})
    if not usuario:
        return {"erro": "Usuário não encontrado."}, 404
    bicicleta = mongo.db.bicicletas.find_one({"_id": ObjectId(id_bike)})
    if not bicicleta:
        return {"erro": "Bicicleta não encontrada."}, 404

    emprestimo_ativo = mongo.db.emprestimos.find_one({"id_bike": ObjectId(id_bike), "status": "ativo"})

    if emprestimo_ativo:
        data_emprestimo = emprestimo_ativo['data_emprestimo']
        prazo_emprestimo = data_emprestimo + timedelta(days=30)

        if datetime.now() > prazo_emprestimo:
            mongo.db.bicicletas.update_one({"_id": ObjectId(id_bike)}, {"$set": {"status": "disponível"}})
            mongo.db.emprestimos.update_one({"_id": emprestimo_ativo['_id']}, {"$set": {"status": "expirado"}})
        else:
            return {"message": "Bicicleta já está em uso."}, 400
    else:
        data_emprestimo = datetime.now()
        prazo_emprestimo = data_emprestimo + timedelta(days=30)

    novo_emprestimo = {
        "id_bike": ObjectId(id_bike),
        "id_usuario": ObjectId(id_usuario),
        "status": "ativo",  
        "data_emprestimo": data_emprestimo,
        "data_entrega": prazo_emprestimo  
    }

    result = mongo.db.emprestimos.insert_one(novo_emprestimo)


    mongo.db.bicicletas.update_one({"_id": ObjectId(id_bike)}, {"$set": {"status": "em uso"}})

    return {
        "id": str(result.inserted_id),
        "message": "Empréstimo realizado com sucesso!",
        "data_entrega": prazo_emprestimo.strftime('%Y-%m-%d %H:%M:%S')  
    }, 201




@app.route('/emprestimos', methods=['GET'])
def listar_emprestimos():
    emprestimos = mongo.db.emprestimos.find()
    resultado = []

    for emprestimo in emprestimos:
        resultado.append({
            "id": str(emprestimo["_id"]),
            "id_usuario": str(emprestimo["id_usuario"]),
            "bike_id": str(emprestimo["id_bike"]),
            "data_emprestimo": emprestimo["data_emprestimo"]
        })

    return jsonify(resultado), 200



@app.route('/emprestimos/<string:id_emprestimo>', methods=['DELETE'])
def deletar_emprestimo(id_emprestimo):
    emprestimo = mongo.db.emprestimos.find_one({"_id": ObjectId(id_emprestimo)})
    
    if not emprestimo:
        return {"erro": "Empréstimo não encontrado."}, 404
    
    id_bike = emprestimo.get("id_bike")
    if not id_bike:
        return {"erro": "Bicicleta associada não encontrada."}, 404
    
    mongo.db.bicicletas.update_one({"_id": id_bike}, {"$set": {"status": "disponível"}})
    
    mongo.db.emprestimos.delete_one({"_id": ObjectId(id_emprestimo)})
    
    return {"message": "Empréstimo deletado e bicicleta liberada com sucesso!"}, 200




if __name__ == "__main__":
    app.run(debug=True)