import sqlite3

from flask import Flask, abort, jsonify, request

app = Flask(__name__)
app.secret_key = b'\xc6M(\xfc\xbf\x9b\xce\xd5\x93\x18P\xbe\x97\xbdS\x15'


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404


@app.errorhandler(403)
def resource_not_found(e):
    return jsonify(error=str(e)), 403


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = dict_factory
    return conn


def get_empresa(empresa_id):
    conn = get_db_connection()
    empresa = conn.execute('SELECT * FROM empresas WHERE id = ?',
                           (empresa_id,)).fetchone()
    conn.close()
    if empresa is None:
        abort(404, "Empresa não encontrada")
    return empresa


def get_empresas():
    conn = get_db_connection()
    empresas = conn.execute('SELECT * FROM empresas').fetchall()
    conn.close()
    return empresas


def get_avaliacoes(empresa_id):
    conn = get_db_connection()
    avaliacoes = conn.execute('SELECT * FROM avaliacoes WHERE id_empresa = ?',
                              (empresa_id,)).fetchall()
    conn.close()
    return avaliacoes


def get_rank():
    conn = get_db_connection()
    rank = conn.execute(
        'select round(avg(avaliacao)) as avalicao, nome, industria from avaliacoes inner join empresas on empresas.id '
        '= id_empresa group by id_empresa').fetchall()
    conn.close()
    return rank


@app.route('/')
def index():
    return 'Autera API'


@app.route('/empresas', methods=('GET', 'POST'))
def empresas():
    if request.method == 'GET':
        return jsonify(get_empresas())
    elif request.method == 'POST':
        nome = request.form['nome']
        industria = request.form['industria']
        if not nome:
            return jsonify({"error": "nome é necessário"})
        elif not industria:
            return jsonify({"error": "industria é necessário"})
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO empresas (nome, industria) VALUES (?, ?)',
                         (nome, industria))
            conn.commit()
            conn.close()
            return jsonify({"ok": "Empresa cadastrada"})


@app.route('/empresas/<int:empresa_id>')
def empresa(empresa_id):
    return jsonify(get_empresa(empresa_id))


@app.route('/empresas/<int:empresa_id>/avaliacoes', methods=('GET', 'POST'))
def avaliacoes(empresa_id):
    if request.method == 'GET':
        return jsonify(get_avaliacoes(empresa_id))
    elif request.method == 'POST':
        if 'avaliacao' in request.form and 'descricao' in request.form:
            pass
        else:
            abort(403)
        avaliacao = request.form['avaliacao']
        descricao = request.form['descricao']
        if not get_empresa(empresa_id):
            return jsonify({"error": "empresa não encontrada"})
        elif not avaliacao:
            return jsonify({"error": "avaliacao é necessário"})
        elif not avaliacao.isdigit():
            return jsonify({"error": "avaliacao deve ser um numero inteiro de 1 a 5"})
        elif (int(avaliacao)) > 5 or (int(avaliacao) < 1):
            return jsonify({"error": "avaliacao deve ser um numero inteiro de 1 a 5"})
        elif not descricao:
            return jsonify({"error": "descricao é necessário"})
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO avaliacoes (avaliacao, descricao, id_empresa) VALUES (?, ?, ?)',
                         (avaliacao, descricao, empresa_id))
            conn.commit()
            conn.close()
            return jsonify({"ok": "Avaliação cadastrada"})


@app.route('/empresas/rank')
def rank():
    return jsonify(get_rank())


if __name__ == '__main__':
    app.run()
