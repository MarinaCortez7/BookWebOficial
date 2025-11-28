from flask import Flask,render_template,request,redirect,g,session,flash,url_for,Blueprint
import sqlite3

bp = Blueprint('Login',__name__)

def ligar_banco():
    banco = sqlite3.connect('bookWeb.db')
    return banco
@bp.route('/login')
def login():
    return render_template('login.html', Titulo = "Faça seu Login")

@bp.route('/autenticar', methods =["POST"])
def autenticar():
    nome = request.form['login']
    senha = request.form['senha']
    banco = ligar_banco()
    cursor = banco.cursor()
    cursor.execute("SELECT * FROM login WHERE nome=? AND senha=?", (nome, senha))
    usuario = cursor.fetchone()
    print(usuario)
    if usuario:
        session['Usuario_Logado'] = nome
        return redirect('/admin')
    else:
        return redirect('/login')

@bp.route('/deslogar')
def deslogar():
    session.clear()
    return redirect('/login')