# app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

# --- Configuración Inicial (Esto ya lo tienes bien) ---
app = Flask(__name__)
CORS(app) 

# --- Configuración de la Base de Datos (Esto ya lo tienes bien) ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///facturacion.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Modelos de la Base de Datos ---

# Modelo para los Proveedores (Esto ya lo tienes bien)
class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    cuit = db.Column(db.String(20), unique=True, nullable=False)

    def to_json(self):
        return { "id": self.id, "name": self.name, "cuit": self.cuit }

# ✅ **PASO 1: COMPLETAR ESTE MODELO**
# Modelo para las Facturas
class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), nullable=False)
    invoice_date = db.Column(db.Date, nullable=False)
    classification = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    supplier = db.relationship('Supplier', backref=db.backref('bills', lazy=True))

# ✅ **PASO 2: AÑADIR ESTE BLOQUE**
# Crea el archivo de la base de datos y las tablas si no existen
with app.app_context():
    db.create_all()

# ✅ **PASO 3: AÑADIR LAS RUTAS DE LA API**
# --- Rutas de la API ---

@app.route("/api/suppliers", methods=["GET"])
def get_suppliers():
    suppliers = Supplier.query.order_by(Supplier.name).all()
    return jsonify({"suppliers": [s.to_json() for s in suppliers]})

@app.route("/api/suppliers", methods=["POST"])
def create_supplier():
    data = request.get_json()
    new_supplier = Supplier(name=data.get("name"), cuit=data.get("cuit"))
    try:
        db.session.add(new_supplier)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": f"Error al guardar proveedor: {e}"}), 400
    return jsonify(new_supplier.to_json()), 201

@app.route("/api/bills", methods=["GET"])
def get_bills():
    bills = Bill.query.order_by(Bill.invoice_date.desc()).all()
    results = []
    for bill in bills:
        results.append({
            "id": bill.id,
            "invoice_number": bill.invoice_number,
            "invoice_date": bill.invoice_date.strftime('%Y-%m-%d'),
            "classification": bill.classification,
            "description": bill.description,
            "supplier_name": bill.supplier.name
        })
    return jsonify({"bills": results})

@app.route("/api/bills", methods=["POST"])
def create_bill():
    data = request.get_json()
    try:
        invoice_date_obj = datetime.strptime(data.get("invoiceDate"), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return jsonify({"message": "Formato de fecha inválido."}), 400

    new_bill = Bill(
        supplier_id=data.get("supplierId"),
        classification=data.get("classification"),
        invoice_number=data.get("invoiceNumber"),
        invoice_date=invoice_date_obj,
        description=data.get("description")
    )
    db.session.add(new_bill)
    db.session.commit()
    return jsonify({"message": "Factura registrada exitosamente"}), 201

# ✅ **PASO 4: AÑADIR ESTO AL FINAL**
# --- Iniciar el servidor ---
if __name__ == "__main__":
    app.run(debug=True)