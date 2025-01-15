from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import uuid

# Initialize Flask app
app = Flask(__name__)

# Enable CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

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
    po_number = db.Column(db.String(100), nullable=False)
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

# Add sample data
with app.app_context():
    if not InboundDocument.query.first():
        # Create an InboundDocument and related data
        document = InboundDocument(po_number="PO12346", vendor="Vendor B", date="2025-01-14")
        db.session.add(document)
        db.session.commit()

        # Add OrderedItems
        item_1 = OrderedItem(
            product="Product B1",
            product_description="Description B1",
            qty=15,
            price=8.0,
            total_price=120.0,
            inbound_document_id=document.id
        )
        item_2 = OrderedItem(
            product="Product B2",
            product_description="Description B2",
            qty=10,
            price=12.0,
            total_price=120.0,
            inbound_document_id=document.id
        )
        db.session.add_all([item_1, item_2])
        db.session.commit()

        # Add a GoodsReceipt
        goods_receipt = GoodsReceipt(
            work_order=f"GR-{uuid.uuid4().hex[:8]}",
            status="not started",
            po_number=document.po_number,
            inbound_document_id=document.id
        )
        db.session.add(goods_receipt)
        db.session.commit()

        # Add GoodsReceiptItems
        gr_item_1 = GoodsReceiptItem(
            product=item_1.product,
            product_description=item_1.product_description,
            qty=item_1.qty,
            goods_receipt_id=goods_receipt.id
        )
        gr_item_2 = GoodsReceiptItem(
            product=item_2.product,
            product_description=item_2.product_description,
            qty=item_2.qty,
            goods_receipt_id=goods_receipt.id
        )
        db.session.add_all([gr_item_1, gr_item_2])
        db.session.commit()

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
