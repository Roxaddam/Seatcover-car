from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "car_corals_9434" 

# Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'inventory.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    custom_id = db.Column(db.String(10)) 
    brand = db.Column(db.String(50)) # Seatcover Brand
    car_brand = db.Column(db.String(50))
    car_name = db.Column(db.String(50))
    model = db.Column(db.String(50))
    fitment = db.Column(db.String(50))
    price = db.Column(db.String(20))
    stock = db.Column(db.Boolean, default=True)
    img1 = db.Column(db.String(500))
    img2 = db.Column(db.String(500))
    img3 = db.Column(db.String(500))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    # 1. Capture Filter Arguments
    sc_brand = request.args.get('scBrand')
    car_brand = request.args.get('carBrand')
    car_name = request.args.get('carName')
    model_style = request.args.get('scModel')

    # 2. Build Filtered Query
    query = Product.query
    if sc_brand and sc_brand != 'all':
        query = query.filter(Product.brand == sc_brand)
    if car_brand and car_brand != 'all':
        query = query.filter(Product.car_brand == car_brand)
    if car_name and car_name != 'all':
        query = query.filter(Product.car_name == car_name)
    if model_style and model_style != 'all':
        query = query.filter(Product.model == model_style)

    products = query.order_by(Product.id.desc()).all()

    # 3. Fetch Unique values for Filter Sync
    db_sc_brands = db.session.query(Product.brand).distinct().all()
    db_car_brands = db.session.query(Product.car_brand).distinct().all()
    db_car_names = db.session.query(Product.car_name).distinct().all()
    db_models = db.session.query(Product.model).distinct().all()

    return render_template('index.html', 
                           products=products,
                           sc_brands=[r[0] for r in db_sc_brands if r[0]],
                           car_brands=[r[0] for r in db_car_brands if r[0]],
                           car_names=[r[0] for r in db_car_names if r[0]],
                           models=[r[0] for r in db_models if r[0]])

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        user = request.form.get('user')
        pw = request.form.get('pass')
        if user == "admin" and pw == "9434":
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash("Incorrect User ID or Password")
            return redirect(url_for('admin'))
    
    products = Product.query.order_by(Product.id.desc()).all()
    logged_in = session.get('admin_logged_in', False)
    return render_template('admin.html', products=products, logged_in=logged_in)

@app.route('/add', methods=['POST'])
def add_item():
    if not session.get('admin_logged_in'): return redirect(url_for('admin'))
    
    # Handle "Add New Brand" logic from admin panel
    selected_brand = request.form.get('brand')
    final_brand = request.form.get('custom_brand_name') if selected_brand == "NEW" else selected_brand

    last_item = Product.query.order_by(Product.id.desc()).first()
    new_id_int = (last_item.id + 1) if last_item else 1
    formatted_id = f"{new_id_int:04d}"

    new_p = Product(
        custom_id=formatted_id,
        brand=final_brand,
        car_brand=request.form.get('car_brand'),
        car_name=request.form.get('car_name'),
        model=request.form.get('model'),
        fitment="Custom Fit", 
        price=request.form.get('price'),
        stock=request.form.get('stock') == 'true',
        img1=request.form.get('img1'),
        img2=request.form.get('img2'),
        img3=request.form.get('img3')
    )
    db.session.add(new_p)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/delete/<int:id>')
def delete_item(id):
    if not session.get('admin_logged_in'): return redirect(url_for('admin'))
    item = Product.query.get(id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('admin'))
@app.route('/edit/<int:id>', methods=['POST'])
def edit_item(id):
    if not session.get('admin_logged_in'): return redirect(url_for('admin'))
    
    item = Product.query.get(id)
    if item:
        # Handle "New Brand" logic same as add route
        selected_brand = request.form.get('brand')
        final_brand = request.form.get('custom_brand_name') if selected_brand == "NEW" else selected_brand

        item.brand = final_brand
        item.car_brand = request.form.get('car_brand')
        item.car_name = request.form.get('car_name')
        item.model = request.form.get('model')
        item.price = request.form.get('price')
        item.stock = request.form.get('stock') == 'true'
        item.img1 = request.form.get('img1')
        item.img2 = request.form.get('img2')
        item.img3 = request.form.get('img3')
        
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)

