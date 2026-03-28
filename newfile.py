from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "car_corals_9434" # Required for login sessions

# Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'inventory.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    custom_id = db.Column(db.String(10)) 
    brand = db.Column(db.String(50))
    car_brand = db.Column(db.String(50))
    car_name = db.Column(db.String(50))
    model = db.Column(db.String(50))
    fitment = db.Column(db.String(50))
    price = db.Column(db.String(20))
    stock = db.Column(db.Boolean, default=True)
    img1 = db.Column(db.String(500))
    img2 = db.Column(db.String(500))
    img3 = db.Column(db.String(500))

# Initialize Database
with app.app_context():
    db.create_all()

# --- ROUTES ---

@app.route('/')
def index():
    products = Product.query.order_by(Product.id.desc()).all()
    return render_template('index.html', products=products)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        user = request.form.get('user')
        pw = request.form.get('pass')
        
        # Check if the inputs match exactly
        if user == "admin" and pw == "9434":
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            # If login fails, send an error message to the frontend
            flash("Incorrect User ID or Password")
            return redirect(url_for('admin'))
    
    products = Product.query.order_by(Product.id.desc()).all()
    logged_in = session.get('admin_logged_in', False)
    return render_template('admin.html', products=products, logged_in=logged_in)

@app.route('/add', methods=['POST'])
def add_item():
    if not session.get('admin_logged_in'): return redirect(url_for('admin'))
    
    # Auto-generate Custom ID (#0001, #0002...)
    last_item = Product.query.order_by(Product.id.desc()).first()
    new_id_int = (last_item.id + 1) if last_item else 1
    formatted_id = f"{new_id_int:04d}"

    new_p = Product(
        custom_id=formatted_id,
        brand=request.form.get('brand'),
        car_brand=request.form.get('car_brand'),
        car_name=request.form.get('car_name'),
        model=request.form.get('model'),
        fitment="Custom Fit", # Default fitment
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
    return redíirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
