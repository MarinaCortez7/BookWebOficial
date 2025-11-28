import io
from flask import Blueprint, session, redirect, render_template,g,request,send_file,send_from_directory,jsonify,app
import sqlite3

bp = Blueprint('contato',__name__)

def ligar_banco():
    banco = sqlite3.connect('bookWeb.db')
    return banco

@bp.route('/contato/<paginacontato>', methods=['GET'])
def listar_contato(paginacontato):
    banco = ligar_banco()
    cursor = banco.cursor()
    paginacontato=int(paginacontato)
    por_paginacontato=6
    offset = (paginacontato - 1) * por_paginacontato
    cursor.execute('SELECT * FROM contato LIMIT ? OFFSET ?;', (por_paginacontato, offset))
    contato = cursor.fetchall()
    cursor.execute('SELECT COUNT(*) FROM contato;')
    total_contato = cursor.fetchone()[0]
    total_paginascontato = (total_contato + por_paginacontato - 1) // por_paginacontato
    return render_template('contatoexibir.html', Listacontato=contato, Titulo="Contato",
                           paginacontato=paginacontato, total_paginascontato=total_paginascontato)


@bp.route('/cadastrarcontato', methods=['POST','GET'])
def cadastrarcontato():
    if request.method == 'POST':
        banco = ligar_banco()
        cursor = banco.cursor()
        nome = request.form['nome']
        sobrenome = request.form['sobrenome']
        email = request.form['email']
        assunto = request.form['assunto']
        mensagem = request.form['mensagem']
        cursor.execute('INSERT INTO contato'
                       '(nome,sobrenome,email,assunto,mensagem) '
                       'VALUES (?,?,?,?,?);',
                       (nome, sobrenome, email, assunto, mensagem))
        banco.commit()
        return redirect('/contato')
    return render_template('contatoexibir.html')



