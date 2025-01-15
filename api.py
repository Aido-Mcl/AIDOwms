from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # Import flask-cors
import uuid

# Initialize Flask app
app = Flask(__name__)

# Enable CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow all origins to access /api/*

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///warehouse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the InboundDocument model
class InboundDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String(100), nullable=False)
    vendor = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    items = db.relationship('OrderedItem', backref='inbound_document', lazy=True)

# Define the OrderedItem model
class OrderedItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(100), nullable=False)
    product_description = db.Column(db.String(200), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    inbound_document_id = db.Column(db.Integer, db.ForeignKey('inbound_document.id'), nullable=False)

# Define the Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(100), nullable=False)
    product_description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=True)
    barcode = db.Column(db.String(100), nullable=True)
    height = db.Column(db.Float, nullable=True)
    width = db.Column(db.Float, nullable=True)
    length = db.Column(db.Float, nullable=True)

# Define the GoodsReceipt model
class GoodsReceipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    work_order = db.Column(db.String(100), nullable=False, unique=True)
    status = db.Column(db.String(50), nullable=False, default="not started")
    po_number = db.Column(db.String(100), nullable=False)  # Reference to the PO number
    inbound_document_id = db.Column(db.Integer, db.ForeignKey('inbound_document.id'), nullable=False)
    items = db.relationship('GoodsReceiptItem', backref='goods_receipt', lazy=True)

# Define the GoodsReceiptItem model
class GoodsReceiptItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(100), nullable=False)
    product_description = db.Column(db.String(200), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    goods_receipt_id = db.Column(db.Integer, db.ForeignKey('goods_receipt.id'), nullable=False)

# Create the database and tables
with app.app_context():
    db.create_all()

# Sample data addition omitted for brevity (same as before)

# API route to get inbound documents
@app.route('/api/inbound-documents', methods=['GET'])
def get_inbound_documents():
    documents = InboundDocument.query.all()
    if not documents:
        return jsonify({"message": "No inbound documents found."}), 200

    documents_list = []
    for doc in documents:
        items = OrderedItem.query.filter_by(inbound_document_id=doc.id).all()
        items_list = [
            {
                "product": item.product,
                "product_description": item.product_description,
                "qty": item.qty,
                "price": item.price,
                "total_price": item.total_price
            }
            for item in items
        ]
        documents_list.append({
            "id": doc.id,
            "po_number": doc.po_number,
            "vendor": doc.vendor,
            "date": doc.date,
            "items": items_list
        })

    return jsonify(documents_list), 200

# API route to get goods receipts
@app.route('/api/goods-receipts', methods=['GET'])
def get_goods_receipts():
    goods_receipts = GoodsReceipt.query.all()
    if not goods_receipts:
        return jsonify({"message": "No goods receipts found."}), 200

    receipts_list = []
    for receipt in goods_receipts:
        items = GoodsReceiptItem.query.filter_by(goods_receipt_id=receipt.id).all()
        items_list = [
            {
                "product": item.product,
                "product_description": item.product_description,
                "qty": item.qty
            }
            for item in items
        ]
        receipts_list.append({
            "id": receipt.id,
            "work_order": receipt.work_order,
            "status": receipt.status,
            "po_number": receipt.po_number,
            "items": items_list
        })

    return jsonify(receipts_list), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
