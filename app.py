from urllib import request

from flask import Flask, redirect, render_template, session
import sqlite3
from Rotas import livros,contato,emprestimo,login
app = Flask(__name__)
app.secret_key = "chave-super-secreta"

app.register_blueprint(livros.bp)
app.register_blueprint(contato.bp)
app.register_blueprint(emprestimo.bp)

app.register_blueprint(login.bp)

def ligar_banco():
    banco = sqlite3.connect('bookWeb.db')
    return banco
@app.route('/')
def home():
    return render_template('index2.html', Titulo="BookWeb")


@app.route('/admin')
def admin():
    return render_template('index.html', Titulo="BookWeb")
@app.get('/acervo')
def acervo():
    return render_template('acervo.html', Titulo="Acervo")

@app.get('/livros')
def livros():
    return render_template('livros.html', Titulo="Livros")


@app.get('/emprestimo')
def emprestimo():
    return render_template('emprestimo.html', Titulo="Empréstimo")


@app.get('/contato')
def contato():
    return render_template('contato.html', Titulo="Contato")

@app.get('/cadastrarlivros')
def cadastrarlivros():
    return render_template('cadastrolivros.html', Titulo="Cadastrar Livros")

@app.get('/cadastroemprestimo')
def cadastraremprestimo():
    return render_template('cadastroemprestimo.html', Titulo="Cadastrar emprestimo")

@app.get('/exibircontato')
def cadastrarcontato():
    banco = ligar_banco()
    cursor = banco.cursor()
    cursor.execute("SELECT * FROM contato")
    contato = cursor.fetchall()
    return render_template('contatoexibir.html',contato=contato)




if __name__ == '__main__':
    app.run()
