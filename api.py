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

    # Add sample data if database is empty
    if not InboundDocument.query.first():
        # InboundDocument and OrderedItems
        inbound_doc = InboundDocument(po_number="PO12345", vendor="Vendor A", date="2025-01-01")
        ordered_item_1 = OrderedItem(
            product="Product A1",
            product_description="Description A1",
            qty=10,
            price=15.0,
            total_price=150.0,
            inbound_document=inbound_doc
        )
        ordered_item_2 = OrderedItem(
            product="Product A2",
            product_description="Description A2",
            qty=5,
            price=20.0,
            total_price=100.0,
            inbound_document=inbound_doc
        )
        db.session.add(inbound_doc)
        db.session.add(ordered_item_1)
        db.session.add(ordered_item_2)

        # GoodsReceipt and GoodsReceiptItems
        goods_receipt = GoodsReceipt(
            work_order=f"GR-{uuid.uuid4().hex[:8]}",
            status="in progress",
            po_number="PO12345",
            inbound_document_id=inbound_doc.id
        )
        gr_item_1 = GoodsReceiptItem(
            product="Product A1",
            product_description="Description A1",
            qty=10,
            goods_receipt=goods_receipt
        )
        gr_item_2 = GoodsReceiptItem(
            product="Product A2",
            product_description="Description A2",
            qty=5,
            goods_receipt=goods_receipt
        )
        db.session.add(goods_receipt)
        db.session.add(gr_item_1)
        db.session.add(gr_item_2)
        db.session.commit()

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

# API route to get goods receipts test
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
