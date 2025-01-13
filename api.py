from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///warehouse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the InboundDocument model
class InboundDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)

# Create the database and table
with app.app_context():
    db.create_all()

# API route to check inbound documents
@app.route('/api/inbound-documents', methods=['GET'])
def get_inbound_documents():
    documents = InboundDocument.query.all()
    if not documents:
        return jsonify({"message": "No inbound documents found."}), 200

    # Convert documents to list of dictionaries
    documents_list = [{"id": doc.id, "title": doc.title, "description": doc.description} for doc in documents]
    return jsonify(documents_list), 200

if __name__ == '__main__':
    app.run(debug=True)
