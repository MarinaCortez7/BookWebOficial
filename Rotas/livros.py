import io
from flask import Blueprint, session, redirect, render_template,g,request,send_file,send_from_directory,jsonify,app
import sqlite3

bp = Blueprint('livros',__name__)

def ligar_banco():
    banco = sqlite3.connect('bookWeb.db')
    return banco

@bp.route('/livros/<paginalivros>', methods=['GET'])
def listar_livros(paginalivros):
    banco = ligar_banco()
    cursor = banco.cursor()
    paginalivros=int(paginalivros)
    por_paginalivros=8
    offset = (paginalivros - 1) * por_paginalivros
    cursor.execute('SELECT * FROM livros LIMIT ? OFFSET ?;', (por_paginalivros, offset))
    livros = cursor.fetchall()
    cursor.execute('SELECT COUNT(*) FROM livros;')
    total_livros = cursor.fetchone()[0]
    total_paginaslivros = (total_livros + por_paginalivros - 1) // por_paginalivros
    return render_template('exibirlivros.html', Listalivros=livros, Titulo="livros",
                           paginalivros=paginalivros, total_paginaslivros=total_paginaslivros)


def recuperar_foto(id_livro):
    banco=ligar_banco()
    cursor=banco.cursor()
    cursor.execute("SELECT foto_livro FROM livros WHERE id_livro=?", (id_livro,))
    imagem_blob=cursor.fetchone()
    return imagem_blob[0]

@bp.route('/imagemlivros/<id_livro>')
def imagem(id_livro):
    foto_blob=recuperar_foto(id_livro)
    if foto_blob:
        return send_file(
            io.BytesIO(foto_blob),
            mimetype='image/jpeg',
            download_name=f'imagem_{id_livro}.jpg'
        )
    else:
        return send_from_directory('static/img/','pessoa.png')


@bp.route('/cadastrarlivros', methods=['POST','GET'])
def cadastrarlivros():
    if request.method == 'POST':
        banco = ligar_banco()
        cursor = banco.cursor()
        titulo = request.form['titulo']
        genero = request.form['genero']
        autor = request.form['autor']
        foto_livro = request.files['foto_livro']
        foto_livro_blob = foto_livro.read()
        cursor.execute('INSERT INTO livros'
                       '(titulo,genero,autor,foto_livro) '
                       'VALUES (?,?,?,?);',
                       (titulo, genero, autor, foto_livro_blob))
        banco.commit()
        return redirect('/livros')
    return render_template('cadastrolivros.html')


@bp.route('/excluirlivros/<id_livro>/<paginalivros>', methods=['GET', 'DELETE'])
def deletarlivros(id_livro,paginalivros):
        banco = ligar_banco()
        cursor = banco.cursor()
        cursor.execute('DELETE FROM livros WHERE id_livro=?;', (id_livro,))
        banco.commit()
        return redirect(f'/livros/{paginalivros}')
#
@bp.route('/editarlivros/<id_livro>/<paginalivros>', methods=['GET', 'POST'])
def editarlivros(id_livro, paginalivros):
    banco = ligar_banco()
    cursor = banco.cursor()
    if request.method == 'POST':
        id_livro = request.form['id_livro']
        titulo = request.form['titulo']
        genero = request.form['genero']
        autor = request.form['autor']
        paginalivros = request.form.get('paginalivros', 1)
        # Verifica se foi enviada uma nova imagem
        foto_livro = request.files.get('foto_livro')
        if foto_livro and foto_livro.filename != '':
            foto_livro_blob = foto_livro.read()
            cursor.execute('UPDATE livros SET titulo=?, genero=?, autor=?, foto_livro=? WHERE id_livro=?;',
                           (titulo, genero, autor, foto_livro_blob, id_livro))
        else:
            cursor.execute('UPDATE livros SET titulo=?, genero=?, autor=? WHERE id_livro=?;',
                           (titulo, genero, autor, id_livro))
        banco.commit()
        banco.close()
        return redirect(f'/livros/{paginalivros}')
    cursor.execute('SELECT * FROM livros WHERE id_livro=?;', (id_livro,))
    encontrado = cursor.fetchone()
    banco.close()

    return render_template('editarlivros.html', livros=encontrado, Titulo="Editar livros", paginalivros=paginalivros)


@bp.route('/livrosprocurar/ordenar/<ordem>/<int:paginalivros>')
def ordenar_livros(ordem, paginalivros):
    por_pagina=6
    offset=(paginalivros-1) * por_pagina
    banco = ligar_banco()
    cursor = banco.cursor()
    if ordem=='crescente':
        comandosql='SELECT * FROM livros ORDER BY titulo ASC LIMIT ? OFFSET ?;'
    elif ordem=='decrescente':
        comandosql='SELECT * FROM livros ORDER BY titulo DESC LIMIT ? OFFSET ?;'
    cursor.execute(comandosql,(por_pagina,offset))
    livros = cursor.fetchall()
    cursor.execute('SELECT COUNT(*) FROM livros')
    total_livros = cursor.fetchone()[0]
    total_paginas=(total_livros + por_pagina -1) // por_pagina
    return render_template('exibirlivros.html', Listalivros=livros,
                           paginalivros=paginalivros,total_paginaslivros=total_paginas, Titulo='livros Ordenados', ordem=ordem)


@bp.route('/buscarlivros', methods=['POST'])
def buscar_livros():
    termo = request.form['termo']
    banco = ligar_banco()
    cursor = banco.cursor()
    cursor.execute('SELECT * FROM livros WHERE titulo LIKE ?;',
                   (f'%{termo}%',))
    livros = cursor.fetchall()
    qtd_livros = len(livros)
    return render_template('exibirlivros.html',
                           Listalivros=livros,
                           Titulo=f"Resultado da busca por '{termo}'"
                                  f'encontrou {qtd_livros} resultados',
                           busca=termo, paginalivros=1, total_paginaslivros=1)