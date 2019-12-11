from flask import Flask, request, render_template, make_response, g
import sqlite3
from datetime import datetime

app = Flask(__name__)

lista_carrinho = []
soma=0

###########

@app.route('/irprafazerpedido', methods=['POST', 'GET'])
def irprafazerpedido():
    if request.method=='POST':
        conn = sqlite3.connect('pizatteca.db')
        cursor = conn.cursor()
        
        lista_carrinho=[]
        for i in request.cookies:
            cursor.execute("SELECT nome FROM pizzas WHERE id=?",(i,))
            x = str(cursor.fetchone())
            x = x[3:-3]
            lista_carrinho.append(x)

        print(lista_carrinho)

        lista_qnd=[]
        lista_prices=[]
        global soma
        soma=0
        
        for i in range(0,len(lista_carrinho)):
            z = str(lista_carrinho[i])+'-30'
            w = str(lista_carrinho[i])+'-40'
            print(z)
            print(type(z))
            print(w)
            print(type(w))
            valor_form1=request.form[z]
            if valor_form1=='':
                valor_form1=0
            
            valor_form2=request.form[w]
            if valor_form2=='':
                valor_form2=0

            lista_qnd.append(int(valor_form1))
            lista_qnd.append(int(valor_form2))
            print(2)
            x=lista_carrinho[i]
            cursor.execute("SELECT preco30 from pizzas where nome=(?)",(x,))
            p1=str(cursor.fetchall())
            print(p1)
            print(type(p1))
            p1 = int(p1[2:-3])
            cursor.execute("SELECT preco40 from pizzas where nome=(?)",(x,))
            p2=str(cursor.fetchall())
            p2 = int(p2[2:-3])

            lista_prices.append(p1)
            lista_prices.append(p2)
        print(lista_prices)

        for i in range(0,len(lista_prices)):
            soma = soma + lista_prices[i]*lista_qnd[i]

        soma = int(soma)

        des = 'Pedido:  '
        for i in range(0,len(lista_carrinho)):
            if lista_qnd[i]>0:
                des= des + str(lista_qnd[i]) + ' x ' + str(lista_carrinho[i]) + "\n"

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                    id  INTEGER PRIMARY KEY,
                    descricao TEXT, 
                    preco REAL,
                    CEP TEXT,
                    rua TEXT,
                    num TEXT, 
                    complemento TEXT,
                    bairro TEXT,
                    nome TEXT,
                    CPF TEXT, 
                    tel TEXT,
                    pag TEXT

            );      
                """)
        cursor.execute("""
            INSERT INTO pedidos (descricao, preco)
            VALUES (?,?)
            """, (des, soma))
        conn.commit()

        cursor.execute("""
            SELECT preco FROM pedidos WHERE id=(SELECT MAX(id) FROM pedidos)
            """)
        preco = cursor.fetchall()
        preco=str(preco)
        preco = preco[2:-3]

        return render_template('fazerpedido.html', preco=preco)

    if request.method=='GET':
        return "Este metodo nao eh permitido"
        


@app.route('/')
def index():
    return render_template('home.html')

@app.route('/fazerpedido/', methods=['POST', 'GET'])
def fazerpedido():

    if datetime.now().hour>0 and datetime.now().hour<6:  #RESTRICAO DE HORA
        return "Nao estamos entregando!"
    else:
        conn = sqlite3.connect('pizatteca.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pizzas")

        pizzas = cursor.fetchall()

        lista_carrinho=[]
        for i in request.cookies:
            cursor.execute("SELECT nome FROM pizzas WHERE id=?",(i,))
            x = str(cursor.fetchone())
            x = x[3:-3]
            lista_carrinho.append(x)
        print(lista_carrinho)


        return render_template('fazerpedido2.html', pizzas=pizzas,carrinho=lista_carrinho)


@app.route('/addpizzacarrinho/<idpizza>', methods=['POST', 'GET'])
def addpizzacarrinho(idpizza):

    conn = sqlite3.connect('pizatteca.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pizzas")
    pizzas = cursor.fetchall()

    global lista_carrinho
    lista_carrinho = []
    

    for i in request.cookies:
        cursor.execute("SELECT nome FROM pizzas WHERE id=?",(i,))
        x = str(cursor.fetchone())
        x = x[3:-3]
        lista_carrinho.append(x)

    resp = make_response(render_template('fazerpedido2.html', pizzas=pizzas, carrinho=lista_carrinho))
    resp.set_cookie(idpizza, '1')

    return resp


@app.route('/sucesso', methods=['POST'])
def sucesso():

    nome = str(request.form['nome']).upper()
    rua = str(request.form['rua']).upper()
    tel = str(request.form['tel'])
    pag = str(request.form['forma'])
    num = str(request.form['num']).upper()
    bairro = str(request.form['bairro']).upper()
    CPF = str(request.form['CPF'])
    CEP = str(request.form['CEP'])
    complemento = str(request.form['complemento'])


    conn = sqlite3.connect('pizatteca.db')
    cursor = conn.cursor()

    cursor.execute("""UPDATE pedidos
            SET CEP = ?,
                rua = ?,
                num = ?,
                complemento = ?,
                bairro = ?,
                nome = ?,
                CPF = ?,
                tel = ?,
                pag = ?

                    
            WHERE id = (SELECT MAX(id) FROM pedidos);""", (CEP,rua,num,complemento,bairro,nome,CPF,tel,pag))
    conn.commit()

    return render_template("sucesso.html")  


@app.route('/admin_conclui_pedido', methods=['POST'])
def admin_conclui_pedido():

    conn = sqlite3.connect('pizatteca.db')
    cursor = conn.cursor()

    id_pedido = request.form['concluirpedido']
    
    cursor.execute("""
        DELETE FROM pedidos
        WHERE id = (?)
    """,(id_pedido,))
    conn.commit()

    cursor.execute("SELECT * FROM pedidos")
    pedidos = cursor.fetchall()

    return render_template('admin.html', pedidos=pedidos) 


@app.route('/admin', methods=['GET'])
def admin():

    return render_template('login.html')

@app.route('/echo', methods=['POST'])
def echo():
    ide = (request.form['psw'])

    if ide== 'abelha':
        conn = sqlite3.connect('pizatteca.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM pedidos")
        pedidos = cursor.fetchall()
        return render_template('admin.html', pedidos=pedidos) 
    else:
        return render_template('erro.html' ) 

    
@app.route('/deletarpizza', methods=['GET', 'POST'])
def deletarpizza():

    conn = sqlite3.connect('pizatteca.db')
    cursor = conn.cursor()

    idpizza = request.form['idpizza']

    cursor.execute("""

        DELETE FROM pizzas
        WHERE id = ?; 

        """, (idpizza,))
    conn.commit()
    
    cursor.execute("SELECT * FROM pizzas")

    dados = cursor.fetchall()

    return(render_template('admin.html', dados=dados))

@app.route('/postarpizza', methods=['GET', 'POST'])
def postarpizza():

    conn = sqlite3.connect('pizatteca.db')
    cursor = conn.cursor()

    nome = request.form['nome']
    preco30 = request.form['preco30']
    preco40 = request.form['preco40']



    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pizzas (
        
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                
                
                nome TEXT,
                preco30 INTEGER,
                preco40 INTEGER
        );      
        """)

    cursor.execute("""
        INSERT INTO pizzas (nome, preco30,preco40)
        VALUES (?,?,?)
        """, (nome,preco30,preco40)) 
    conn.commit()

    cursor.execute("SELECT * FROM pedidos")
    pedidos = cursor.fetchall()

    return(render_template('admin.html', pedidos=pedidos))

@app.route('/verpedidos', methods=['GET', 'POST'])
def verpedidos():
    pass


@app.route('/home', methods=['GET'])
def echohome():
    return render_template('home.html')

@app.route('/paesrecheados', methods=['GET'])
def homel():
    return render_template('cardapio2.html')
'''
@app.route('/pizzas', methods=['GET'])
def pizzas():
    return render_template('cardapio3.html')
'''
@app.route('/cardapio', methods=['GET'])
def cardapio():
    return render_template('cardapio.html')


@app.route('/bebidas', methods=['GET'])
def bebidas():
    return render_template('cardapio4.html')

@app.route('/pizzas', methods=['GET'])
def pizzas():
    conn = sqlite3.connect('pizatteca.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pizzas")

    pizzas = cursor.fetchall()
    return render_template('cardapio3.html', pizzas=pizzas)



if __name__ == "__main__":
    app.run()
