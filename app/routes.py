from app import app
from flask import render_template,redirect,abort
from app.db import Database
from app.bitcoin import Bitcoin
from flask import request
from app import configuration
from flask import session
import re
import hashlib


@app.route('/')
def index():
    bitcoin=Bitcoin()
    return render_template('base.html', rate=bitcoin.btc_eur, header=configuration.Configuration.header)

@app.route('/products')
def list_items():
    database=Database()
    bitcoin=Bitcoin()
    database.db_cursor.execute('SELECT * FROM items WHERE visible!=0')
    items = database.db_cursor.fetchall()
    return render_template('products.html', items=items, rate=bitcoin.btc_eur, header=configuration.Configuration.header)

@app.route('/item/<index>')
def show_item(index):
    index=re.sub('[^0-9]', '', index)
    database=Database()
    bitcoin=Bitcoin()
    item=database.fetch_one_item(index)

    if item is None:
        abort(404)
    else:
        return  render_template('item.html',index=index,item=item,rate=bitcoin.btc_eur,header=configuration.Configuration.header)

@app.route('/empty')
def empty_cart():
    session.clear()
    return redirect('/')

@app.route('/add', methods=['POST'])
def add_product_to_cart():
    database=Database()
    quantity = int(request.form['quantity'])
    index = request.form['item']
    item_param = database.fetch_one_item(index)
    price = item_param.price
    itemArray =  {'name' : item_param.name, 'quantity': quantity, 'unit_price': price, 'total_price': quantity * price }
    if quantity and item_param and request.method == 'POST':
        all_total_price = 0
        all_total_quantity = 0
        session.modified = True
        if 'cart' in session:
            if index in session['cart']:
                session['cart'][index]['quantity'] += quantity
                session['cart'][index]['total_price'] += quantity * price
            else:
                session['cart'][index] = itemArray

            for key, item in session['cart'].items():
                all_total_quantity += int(item['quantity'])
                all_total_price += float(item['total_price'])
            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price
            return redirect('/cart')

        else:
            session['cart'] = {index : itemArray}
            session['all_total_price'] = quantity * price
            session['all_total_quantity'] = quantity
            return redirect('/cart')

    else:
        app.flash('Item not found','error')
        return redirect('/products')

@app.route('/delete/<index>')
def delete_product(index):
    app.flash('Item removed from cart','info')
    return redirect('/cart')

@app.route('/cart')
def get_cart():
    return render_template('cart.html', header=configuration.Configuration.header)

@app.route('/order/<index>/<amount>')
def order_item(index,amount):
    index=re.sub('[^0-9]', '', index)
    amount=re.sub('[^0-9]', '', amount)
    database=Database()
    bitcoin=Bitcoin()
    item=database.fetch_one_item(index)
    if item is None:
        return 'Error'
    else:
        from flask_wtf import FlaskForm
        from wtforms import TextAreaField,validators
        class OrderForm(FlaskForm):
            address=TextAreaField('Address', [validators.Length(min=10, max=200)])
        order_form=OrderForm()
        return render_template('order.html',item=item, index=index,rate=bitcoin.btc_eur, amount=int(amount),form=order_form,header=configuration.Configuration.header)

@app.route('/payment', methods=['POST'])
def pay_for_order ():
    data=request.form
    address=data['address']
    address=address[0:200]
    address=address.strip()
    if address=="":
        return "Error, empty address"
    bitcoin=Bitcoin()
    database=Database()
    #address=re.sub('[^A-Za-z0-9:_-]','',address)
    address_salt=address+configuration.Configuration.salt
    address_salt=address_salt.encode()
    address_hash=hashlib.sha224(address_salt).hexdigest()[0:9]
    address=address.replace('\n', '|')
    address = re.sub('[^A-Za-z0-9:_-|]', '', address)
    item_index=data['index']
    item_amount=data['amount']
    item_index=re.sub('[^0-9]', '', item_index)
    item_amount=re.sub('[^0-9]', '', item_amount)
    item=database.fetch_one_item(item_index)
    order_price=round(item.price/bitcoin.btc_eur*float(item_amount),6)
    #print (order_price)
    order=Bitcoin.order(item_index,address,address_hash,item_amount,order_price)
    #print (order.order_index)
    return redirect("/pay/"+str(order.btc_address))

@app.route('/pay/<btc_address>')
def present_payment(btc_address):
    btc_address=re.sub('[^A-Za-z0-9]','',btc_address)
    bitcoin=Bitcoin()
    database=Database()
    order=database.fetch_one_order(btc_address)
    if order is None:
        return 'Error'
    else:
        return  render_template('pay.html',order=order,rate=bitcoin.btc_eur,header=configuration.Configuration.header)

@app.route('/login', methods=['POST','GET'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    from flask_wtf import FlaskForm
    from wtforms import StringField, PasswordField, SubmitField

    class LoginForm(FlaskForm):
        username = StringField('Username')
        password = PasswordField('Password')
        submit = SubmitField('Submit')

    form = LoginForm()
    if form.validate_on_submit():
        import hashlib
        user=(request.form.get('username'))
        password=(request.form.get('password'))
        user=user.encode('utf-8')
        password=password.encode('utf-8')
        user=hashlib.sha224(user).hexdigest()
        password=hashlib.sha224(password).hexdigest()
        if((user==configuration.Configuration.user) and (password==configuration.Configuration.password)):
            session['adminkey']=hashlib.sha224(configuration.Configuration.secret_key.encode('utf-8')).hexdigest()
            #print (session)
            return redirect ('/c')
    return render_template('login.html', form=form,header=configuration.Configuration.header)

@app.route('/logout')
def logout():
    if 'adminkey' not in session:
        abort(404)
    elif (session['adminkey']!=hashlib.sha224(configuration.Configuration.secret_key.encode('utf-8')).hexdigest()):
        abort(404)
    session['adminkey']=''
    return redirect('/')
    abort(404)

@app.route('/c')
def console():
    if 'adminkey' not in session:
        return redirect('/login')
    elif (session['adminkey']!=hashlib.sha224(configuration.Configuration.secret_key.encode('utf-8')).hexdigest()):
        return redirect('/login')

    database=Database()
    orders=database.get_orders(0)
    orders_interest=[]
    for order in orders:
        if (order.paid>0) or (order.note is not None):
            item=database.fetch_one_item(order.item_index)
            order.item_name=item.name

            orders_interest.append(order)
    orders=orders_interest
    items=database.get_items()
    required_items=[]
    for item in items:
        item.pcs=",".join(str(x) for x in item.pcs)
        required_items.append(item)
    items=required_items
    return render_template('admin.html',orders=orders,items=items,header=configuration.Configuration.header)

@app.route('/admin_order', methods=['POST'])
def admin_order():
    if 'adminkey' not in session:
        abort(404)
    elif (session['adminkey']!=hashlib.sha224(configuration.Configuration.secret_key.encode('utf-8')).hexdigest()):
        abort(404)
    data = request.form
    database=Database()
    if 'note' not in data:
        database.delete_note(data['order_index'])
    else:
        database.create_note(data['order_index'],data['note'])

    return redirect('/c')

@app.route('/admin_item', methods=['POST'])
def admin_item():
    if 'adminkey' not in session:
        abort(404)
    elif (session['adminkey']!=hashlib.sha224(configuration.Configuration.secret_key.encode('utf-8')).hexdigest()):
        abort(404)
    data = request.form

    item_name=data['name']
    item_price=data['price']
    item_avail=data['avail']
    item_description=data['description']
    item_index=data['index']
    item_pcs=data['pcs']
    database=Database()
    database.update_item(item_index,item_price,item_name,item_avail,item_description,item_pcs)
    return redirect('/c')

@app.route('/delete_item/<item>')
def delete_item(item):
    if 'adminkey' not in session:
        abort(404)
    elif (session['adminkey']!=hashlib.sha224(configuration.Configuration.secret_key.encode('utf-8')).hexdigest()):
        abort(404)
    database=Database()
    database.delete_item(item)
    return redirect('/c')

@app.route('/add_item')
def add_item():
    if 'adminkey' not in session:
        abort(404)
    elif (session['adminkey']!=hashlib.sha224(configuration.Configuration.secret_key.encode('utf-8')).hexdigest()):
        abort(404)
    database=Database()
    database.add_item()
    return redirect('/c')
