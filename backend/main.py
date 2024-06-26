from flask import Flask, abort
from flask import jsonify
from flask_cors import CORS
from models import *
from database.DBConnector import * 

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return "<h1>Hello World - Welcome to our project</h1>"

@app.route("/medals", methods=["GET"])
def medals():
    endopointQuerySql = """SELECT noc.nome as pais,
                                noc.codigo as codigo,
                                SUM(CASE WHEN medalha.tipo = 'O' THEN 1 ELSE 0 END) as Ouro,
                                SUM(CASE WHEN medalha.tipo = 'P' THEN 1 ELSE 0 END) as Prata,
                                SUM(CASE WHEN medalha.tipo = 'B' THEN 1 ELSE 0 END) as Bronze
                            FROM noc
                            JOIN atleta ON noc.codigo = atleta.noc
                            JOIN medalha ON atleta.id = medalha.atleta
                            GROUP BY noc.codigo
                            ORDER BY Ouro DESC, Prata DESC, Bronze DESC"""

    db = DBConnect()
    results = db.runQuery(endopointQuerySql)
    result = {"table": []}
    for row in results:
        result["table"].append({
            "codigo": row[1],
            "nome": row[0],
            "ouro": row[2],
            "prata": row[3],
            "bronze": row[4],
        })
    return result

@app.route("/medals/<country>", methods=["GET"])
def medals_by_country(country):
    if len(country) != 3:
        return {"error": "Código de país deve ter 3 caracteres."}, 400
    endpointQuerySql = f"""SELECT noc.nome as NOC, 
                          SUM(CASE WHEN medalha.tipo = 'O' THEN 1 ELSE 0 END) as Ouro,
                          SUM(CASE WHEN medalha.tipo = 'P' THEN 1 ELSE 0 END) as Prata,
                          SUM(CASE WHEN medalha.tipo = 'B' THEN 1 ELSE 0 END) as Bronze
                   FROM noc
                   JOIN atleta ON noc.codigo = atleta.noc
                   JOIN medalha ON atleta.id = medalha.atleta
                   WHERE noc.codigo = ?
                   GROUP BY noc.nome
                   ORDER BY Ouro DESC, Prata DESC, Bronze DESC"""

    db = DBConnect()
    queryRes = db.runQuery(endpointQuerySql, [country])
    try:
        row = queryRes.pop(0)
        result = {
            "country": {
                "nome": row[0],
                "ouro": row[1],
                "prata": row[2],
                "bronze": row[3],
            }
        }
    except Exception:
        result = {"error": f"NOC de código '{country}' não existe."}, 404

    return result

@app.route("/medals/top/<int:n>", methods=["GET"])
def medals_top(n):
    if n <= 0:
        return {"error": "Número de medalhas deve ser maior que 0"}, 400
    endpointQuerySql = f"""SELECT noc.nome as pais,
                            noc.codigo as codigo,
                            SUM(CASE WHEN medalha.tipo = 'O' THEN 1 ELSE 0 END) as Ouro,
                            SUM(CASE WHEN medalha.tipo = 'P' THEN 1 ELSE 0 END) as Prata,
                            SUM(CASE WHEN medalha.tipo = 'B' THEN 1 ELSE 0 END) as Bronze,
                            (SELECT COUNT(*) from atleta WHERE atleta.noc = noc.codigo) as totalAtletas
                        FROM noc
                        JOIN atleta ON noc.codigo = atleta.noc
                        JOIN medalha ON atleta.id = medalha.atleta
                        GROUP BY noc.nome, noc.codigo
                        ORDER BY Ouro DESC, Prata DESC, Bronze DESC
                        LIMIT ? """
    db = DBConnect()
    results = db.runQuery(endpointQuerySql, [n])
    result = {"table": []}
    for row in results:
        result["table"].append({
            "codigo": row[1],
            "nome": row[0],
            "ouro": row[2],
            "prata": row[3],
            "bronze": row[4],
            "totalAtletas": row[5]
        })
    return result

@app.route("/medals/ratio", methods=["GET"])
def medals_ratio():
    # Retorna os países ordenados pelo razão de ouro/total
    endpointQuerySql = """SELECT noc.nome as pais,
                                noc.codigo as codigo,
                                SUM(CASE WHEN medalha.tipo = 'O' THEN 1 ELSE 0 END) as Ouro,
                                SUM(CASE WHEN medalha.tipo = 'P' THEN 1 ELSE 0 END) as Prata,
                                SUM(CASE WHEN medalha.tipo = 'B' THEN 1 ELSE 0 END) as Bronze
                            FROM noc
                            JOIN atleta ON noc.codigo = atleta.noc
                            JOIN medalha ON atleta.id = medalha.atleta
                            GROUP BY noc.codigo
                            HAVING Ouro + Prata + Bronze > 10
                            ORDER BY Ouro/(Ouro + Prata + Bronze) DESC
                        """
    db = DBConnect()
    results = db.runQuery(endpointQuerySql)
    result = {"table": []}
    for row in results:
        result["table"].append({
            "codigo": row[1],
            "nome": row[0],
            "ouro": row[2],
            "prata": row[3],
            "bronze": row[4],
            "ratio": row[2] / (row[2] + row[3] + row[4])
        })
    result = sorted(result["table"], key= lambda result : result["ratio"], reverse=True)
    return {"table": result}

@app.route("/medals/category/<category>", methods=["GET"])
def medals_by_category(category):
    #treat input
    if(len(category) == 0):
        abort(400)

    # Retorna os países ordenados pelo número de medalhas em uma dada categoria(ex: basquete, basquete 3x3, atletismo)
    endpointQuerySql = f"""SELECT noc.nome as nome,
                            noc.codigo as codigo, 
                            SUM(CASE WHEN medalha.tipo = 'O' THEN 1 ELSE 0 END) as Ouro,
                            SUM(CASE WHEN medalha.tipo = 'P' THEN 1 ELSE 0 END) as Prata,
                            SUM(CASE WHEN medalha.tipo = 'B' THEN 1 ELSE 0 END) as Bronze
                        FROM noc
                        JOIN atleta ON noc.codigo = atleta.noc
                        JOIN medalha ON atleta.id = medalha.atleta
                        JOIN esporte ON evento.esporte = esporte.id
                        JOIN evento ON medalha.evento = evento.id
                        WHERE esporte.id = ?
                        GROUP BY noc.nome
                        ORDER BY Ouro DESC, Prata DESC, Bronze DESC
                    """
    db = DBConnect()
    results = db.runQuery(endpointQuerySql, [category])
    result = {"table": []}
    for row in results:
        result["table"].append({
           "codigo": row[1],
            "nome": row[0],
            "ouro": row[2],
            "prata": row[3],
            "bronze": row[4],
        })
    return result

@app.route("/categories", methods=["GET"])
def categories():
    # Retorna as categorias de esportes
    endpointQuerySql = """SELECT * FROM esporte"""
    db = DBConnect()
    results = db.runQuery(endpointQuerySql)
    result = {"table": []}
    for row in results:
        result["table"].append({
            "id": row[0],
            "nome": row[1],
        })
    return result

@app.route("/athlete/<country>", methods=["GET"])
def athlete_by_country(country):
    if len(country) != 3:
        return {"error": "Código de país deve ter 3 caracteres."}, 400
    endpointQuerySql = f"""
        SELECT *, 
        (SELECT COUNT(*) FROM atleta WHERE noc = "{str(country)}") as athletesCount
        FROM atleta WHERE noc = "{str(country)}"
        """

    db = DBConnect()
    queryRes = db.runQuery(endpointQuerySql)
    if(len(queryRes) == 0):
        return "country not found", 404
    try:
        results = {"table": []}
        for row in queryRes:
            results["table"].append({
                "id": row[0],
                "nome": row[1],
                "genero": row[2],
                "idade": row[3],
                "noc": row[4],
                "total_athletes": row[5],
            })
    except Exception:
        results = {"error": f"NOC de código '{country}' não existe."}, 404

    return results