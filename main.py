from flask import Flask, jsonify, request, render_template, redirect
from flask_cors import CORS
# Menghubungkan perpustakaan database
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base


import json
Base = declarative_base()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
# Menghubungkan SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scomartfix.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Membuat sebuah DB
db = SQLAlchemy(app)


# In-memory storage (replace with database in production)
# Tugas #1. Membuat tabel Pengguna
class daftar(db.Model):
    # Membuat kolom
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # nama
    Nama = db.Column(db.String(100),  nullable=False)
    # kelas
    Kelas = db.Column(db.String(100), nullable=False)
    
    #Parameterized Constructor accepts additional arguments
    def __init__(self, Nama, Kelas):
        self.Nama = Nama
        self.Kelas = Kelas

class Pesanan(db.Model):
    __tablename__ = 'pesanan'

    id = db.Column(db.Integer, primary_key=True)
    order_items = db.Column(db.JSON, nullable=False)  # Store the order items as JSON
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(100), nullable=False)

products = [
    {"id": 1, "name": "Dasi Kelas 7", "price": 25000, "stok": 100, "category": "atribut"},
    {"id": 2, "name": "Dasi Kelas 9", "price": 25000, "stok": 100, "category": "atribut"},
    {"id": 3, "name": "Sabuk", "price": 30000, "stok": 80, "category": "atribut"},
    {"id": 4, "name": "Topi", "price": 25000, "stok": 70, "category": "atribut"},
    { "id": 5, "name": "Kaos Kaki Putih", "price":20000, "category" :"atribut"},
    { "id": 6, "name": "Kaos Kaki Hitam", "price": 20000, "category" :"atribut" },
    { "id": 7, "name": "Batik", "price": 250000, "category" :"atribut" } 
]


orders = []

@app.route('/', methods=['GET','POST'])
def reg():
    if request.method == 'POST':
        Nama= request.form['Nama']
        Kelas = request.form['Kelas']
        
        #Tugas #3. Buat agar data pengguna direkam ke dalam database
        daftarkan = daftar(Nama=Nama, Kelas=Kelas)
        db.session.add(daftarkan)
        db.session.commit()

        
        return redirect('/api/home')
    else:    
        return render_template('regform.html')

@app.route('/api/home')
def index():
    return render_template('index.html')

@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify(products)

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    print(f"Fetching product with ID: {product_id}")  # Debugging line
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        return jsonify(product)
    return jsonify({"error": "Product not found"}), 404

@app.route('/api/checkout', methods=['POST'])
def checkout():
    try:
        order_data = request.json
        
        # Validate order
        if not order_data.get('items'):
            return jsonify({"error": "No items in order"}), 400

        # Calculate total (server-side validation)
        total = sum(item['price'] for item in order_data['items'])
        if abs(total - order_data['total']) > 0.01:  # Allow for floating-point imprecision
            return jsonify({"error": "Invalid total price"}), 400

        # Check stock availability
        for item in order_data['items']:
            product = next((p for p in products if p['id'] == item['id']), None)
            if not product or product['stok'] <= 0:
                return jsonify({"error": f"Product {item['id']} out of stock"}), 400
            product['stok'] -= 1

        # Create order in the database
        order = Pesanan(
            order_items=order_data['items'],
            total=total,
            status="confirmed"
        )
        db.session.add(order)
        db.session.commit()

        return jsonify({
            "message": "Pesanan berhasil dibuat",
            "order_id": order.id  # Returning the actual order ID from the database
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/orders', methods=['GET'])
def get_orders():
    return jsonify(orders)

@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = next((o for o in orders if o['id'] == order_id), None)
    if order:
        return jsonify(order)
    return jsonify({"error": "Order not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)