import io
from flask import Blueprint, session, redirect, render_template, g, request, send_file, send_from_directory, jsonify, app
import sqlite3

bp = Blueprint('emprestimo', __name__)

def ligar_banco():
    banco = sqlite3.connect('bookWeb.db')
    return banco


@bp.route('/emprestimo/<paginaemprestimo>', methods=['GET'])
def listar_emprestimo(paginaemprestimo):
    banco = ligar_banco()
    cursor = banco.cursor()
    paginaemprestimo = int(paginaemprestimo)
    por_paginaemprestimo = 8
    offset = (paginaemprestimo - 1) * por_paginaemprestimo
    cursor.execute('SELECT * FROM emprestimo LIMIT ? OFFSET ?;', (por_paginaemprestimo, offset))
    emprestimo = cursor.fetchall()
    cursor.execute('SELECT COUNT(*) FROM emprestimo;')
    total_emprestimo = cursor.fetchone()[0]
    total_paginasemprestimo = (total_emprestimo + por_paginaemprestimo - 1) // por_paginaemprestimo
    return render_template('exibiremprestimo.html', Listaemprestimo=emprestimo, Titulo="emprestimo",
                           paginaemprestimo=paginaemprestimo, total_paginasemprestimo=total_paginasemprestimo)


def recuperar_foto(id_emprestimo):
    banco = ligar_banco()
    cursor = banco.cursor()
    cursor.execute("SELECT foto_livro FROM emprestimo WHERE id_emprestimo=?", (id_emprestimo,))
    imagem_blob = cursor.fetchone()
    return imagem_blob[0]


@bp.route('/imagememprestimo/<id_emprestimo>')
def imagem(id_emprestimo):
    foto_blob = recuperar_foto(id_emprestimo)
    if foto_blob:
        return send_file(
            io.BytesIO(foto_blob),
            mimetype='image/jpeg',
            download_name=f'imagem_{id_emprestimo}.jpg'
        )
    else:
        return send_from_directory('static/img/', 'pessoa.png')


@bp.route('/cadastraremprestimo', methods=['POST', 'GET'])
def cadastraremprestimo():
    if request.method == 'POST':
        banco = ligar_banco()
        cursor = banco.cursor()
        titulo = request.form['titulo']
        nome_usuario = request.form['nome_usuario']
        data_emprestimo = request.form['data_emprestimo']
        prazo_devolucao = request.form['prazo_devolucao']
        foto_livro = request.files['foto_livro']
        foto_livro_blob = foto_livro.read()
        cursor.execute('INSERT INTO emprestimo '
                       '(titulo, nome_usuario, data_emprestimo, prazo_devolucao, foto_livro) '
                       'VALUES (?, ?, ?, ?, ?);',
                       (titulo, nome_usuario, data_emprestimo, prazo_devolucao, foto_livro_blob))
        banco.commit()
        return redirect('/emprestimo')
    return render_template('cadastroemprestimo.html')


@bp.route('/excluiremprestimo/<id_emprestimo>/<paginaemprestimo>', methods=['GET', 'DELETE'])
def deletaremprestimo(id_emprestimo, paginaemprestimo):
    banco = ligar_banco()
    cursor = banco.cursor()
    cursor.execute('DELETE FROM emprestimo WHERE id_emprestimo=?;', (id_emprestimo,))
    banco.commit()
    return redirect(f'/emprestimo/{paginaemprestimo}')


@bp.route('/editaremprestimo/<id_emprestimo>/<paginaemprestimo>', methods=['GET', 'POST'])
def editaremprestimo(id_emprestimo, paginaemprestimo):
    banco = ligar_banco()
    cursor = banco.cursor()

    if request.method == 'POST':
        id_emprestimo = request.form['id_emprestimo']
        titulo = request.form['titulo']
        nome_usuario = request.form['nome_usuario']
        data_emprestimo = request.form['data_emprestimo']
        prazo_devolucao = request.form['prazo_devolucao']
        paginaemprestimo = request.form.get('paginaemprestimo', 1)

        foto_livro = request.files.get('foto_livro')
        if foto_livro and foto_livro.filename != '':
            foto_livro_blob = foto_livro.read()
            cursor.execute('UPDATE emprestimo SET titulo=?, nome_usuario=?, data_emprestimo=?, '
                           'prazo_devolucao=?, foto_livro=? WHERE id_emprestimo=?;',
                           (titulo, nome_usuario, data_emprestimo, prazo_devolucao, foto_livro_blob, id_emprestimo))
        else:
            cursor.execute('UPDATE emprestimo SET titulo=?, nome_usuario=?, data_emprestimo=?, '
                           'prazo_devolucao=? WHERE id_emprestimo=?;',
                           (titulo, nome_usuario, data_emprestimo, prazo_devolucao, id_emprestimo))

        banco.commit()
        banco.close()
        return redirect(f'/emprestimo/{paginaemprestimo}')

    cursor.execute('SELECT * FROM emprestimo WHERE id_emprestimo=?;', (id_emprestimo,))
    encontrado = cursor.fetchone()
    banco.close()
    return render_template('editaremprestimo.html', emprestimo=encontrado,
                           Titulo="Editar emprestimo", paginaemprestimo=paginaemprestimo)


@bp.route('/emprestimoprocurar/ordenar/<ordem>/<int:paginaemprestimo>')
def ordenar_emprestimo(ordem, paginaemprestimo):
    por_pagina = 6
    offset = (paginaemprestimo - 1) * por_pagina
    banco = ligar_banco()
    cursor = banco.cursor()
    if ordem == 'crescente':
        comandosql = 'SELECT * FROM emprestimo ORDER BY titulo ASC LIMIT ? OFFSET ?;'
    elif ordem == 'decrescente':
        comandosql = 'SELECT * FROM emprestimo ORDER BY titulo DESC LIMIT ? OFFSET ?;'
    cursor.execute(comandosql, (por_pagina, offset))
    emprestimos = cursor.fetchall()
    cursor.execute('SELECT COUNT(*) FROM emprestimo')
    total_emprestimo = cursor.fetchone()[0]
    total_paginas = (total_emprestimo + por_pagina - 1) // por_pagina
    return render_template('exibiremprestimo.html', Listaemprestimo=emprestimos,
                           paginaemprestimo=paginaemprestimo, total_paginasemprestimo=total_paginas,
                           Titulo='emprestimo Ordenados', ordem=ordem)


@bp.route('/buscaremprestimo', methods=['POST'])
def buscar_emprestimo():
    termo = request.form['termo']
    banco = ligar_banco()
    cursor = banco.cursor()
    cursor.execute('SELECT * FROM emprestimo WHERE titulo LIKE ?;', (f'%{termo}%',))
    emprestimos = cursor.fetchall()
    qtd_emprestimos = len(emprestimos)
    return render_template('exibiremprestimo.html',
                           Listaemprestimo=emprestimos,
                           Titulo=f"Resultado da busca por '{termo}'"
                                  f'encontrou {qtd_emprestimos} resultados',
                           busca=termo, paginaemprestimo=1, total_paginasemprestimo=1)