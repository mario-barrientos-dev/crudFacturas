from ast import dump
from distutils.log import error
from flask import Flask
from flask import render_template, request, redirect, url_for, flash
from flaskext.mysql import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_wtf.csrf import CSRFProtect


#Modelos
from models.ModelUser import ModelUser

#entities
from models.entities.user import User

app=Flask(__name__)
SECRET_KEY="haku"

csrf=CSRFProtect()
mysql=MySQL()
login_manager_app=LoginManager(app)

app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='facturacion'
mysql.init_app(app)



#Autenticacion login y logout
@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(mysql, id)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if request.method=='POST':
        #print(request.form['username'])
        #print(request.form['password'])
        user=User(0, request.form['username'], request.form['password'])
        logged_user=ModelUser.login(mysql, user)
        if logged_user != None:
            if logged_user.password:
                login_user(logged_user)
                return redirect(url_for('index_clientes'))
            else:
                flash('Password no encontrado')
                return render_template('auth/login.html')
                
        else:
            flash('Usuario no encontrado')
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')
    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

#CRUD y conexion a tabla clientes

@app.route('/clientes')
@login_required
def index_clientes():
    
    sql="SELECT * FROM clientes;"
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    
    clientes=cursor.fetchall()
    
    conn.commit()
    
    
    
    return render_template('clientes/index.html', clientes=clientes)

@app.route('/create')
@login_required
def create():
    return render_template('clientes/create.html')

@app.route('/store', methods=['POST'])
@login_required
def storage():
    
    _nombre=request.form['txtNombre']
    _email=request.form['txtCorreo']
    _phone=request.form['intPhone']
    
    if _nombre=='' or _email=='' or _phone=='':
        flash('Recuerda diligenciar todos los datos')
        return redirect(url_for('create'))
    
    sql="INSERT INTO clientes (id_customer, name, email, phone) VALUES (NULL, %s, %s, %s);"
    
    datos=(_nombre,_email,_phone)
    
    
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()
    return redirect('/clientes')

@app.route('/destroy/<int:id_customer>')
@login_required
def destroy(id_customer):
    
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id_customer=%s", (id_customer))
    
    conn.commit()
    
    return redirect('/clientes')

@app.route('/edit/<int:id_customer>')
@login_required
def see_customer_edit(id_customer):
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE id_customer=%s;", (id_customer))
    clientes=cursor.fetchall()
    conn.commit()
    
    return render_template('clientes/edit.html', clientes=clientes)

@app.route('/update', methods=['POST'])
@login_required
def update():
    
    _nombre=request.form['txtNombre']
    _email=request.form['txtCorreo']
    _phone=request.form['intPhone']
    id=request.form['txtID']
    
    sql="UPDATE clientes SET name=%s, email=%s, phone=%s WHERE id_customer=%s;"
    
    datos=(_nombre,_email,_phone,id)
    
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()
    
    
    return redirect('/clientes')

#CRUD para facturas

@app.route('/facturas')
@login_required
def index_facturas():
    
    sql="SELECT * FROM facturas;"
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    
    facturas=cursor.fetchall()
    
    conn.commit()
    
    return render_template('facturas/index.html', facturas=facturas)

@app.route('/facturas/create')
@login_required
def create_facturas():
    
    sql="SELECT * FROM clientes;"
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    
    clientes=cursor.fetchall()
    
    conn.commit()
    
    return render_template('facturas/create.html', clientes=clientes)

@app.route('/facturas/store', methods=['POST'])
@login_required
def storage_facturas():  
    
    _idCustomer=request.form['id_customertxt']
    _precio=request.form['txtPrecio']
    _detalle=request.form['txtDetalle']
    
    if _idCustomer=='' or _precio=='' or _detalle=='':
        flash('Recuerda diligenciar todos los datos')
        return redirect(url_for('create'))
    
    sql="INSERT INTO facturas (id_customer, precio, detalle) VALUES (%s, %s, %s);"
    
    datos=(_idCustomer,_precio,_detalle)
    
    
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()
    return redirect('/facturas')

@app.route('/facturas/destroy/<int:id_factura>')
@login_required
def destroy_facturas(id_factura):
    
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute("DELETE FROM facturas WHERE id_factura=%s", (id_factura))
    
    conn.commit()
    
    return redirect('/facturas')

@app.route('/facturas/edit/<int:id_factura>')
@login_required
def see_facturas_edit(id_factura):
        
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM facturas WHERE id_factura=%s;", (id_factura))
    facturas=cursor.fetchall()
    conn.commit()
    
    return render_template('facturas/edit.html', facturas=facturas)

@app.route('/facturas/update', methods=['POST'])
@login_required
def update_facturas():
    
    _precio=request.form['txtPrecio']
    _detalle=request.form['txtDetalle']
    id=request.form['id_facturatxt']
    
    sql="UPDATE facturas SET precio=%s, detalle=%s WHERE id_factura=%s;"
    
    datos=(_precio, _detalle,id)
    
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()
    
    
    return redirect('/facturas')

#Caculo de totales
@app.route('/totales/<int:id_customer>')
@login_required
def see_facturas_totales(id_customer):
        
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM facturas WHERE id_customer=%s;", (id_customer))
    facturas=cursor.fetchall()
    conn.commit()
    total=0
    for factura in facturas:
        total += factura[2]
    
    
    return render_template('totales/index.html', facturas=facturas, total=total)




if __name__ == '__main__':
    app.secret_key = SECRET_KEY
    csrf.init_app(app)
    app.run(debug=True)


