from flask import Flask, request, jsonify, send_from_directory, current_app
from werkzeug.utils import secure_filename
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"

app.config['UPLOAD_FOLDER'] = 'uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
db = SQLAlchemy(app)

app.app_context().push()

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    versions = db.relationship('DocumentVersion', backref='document', lazy=True)

class DocumentVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    type = db.Column(db.String(32), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    file_path = db.Column(db.String(128), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)






@app.route('/documents', methods=['POST'])
def upload_document():
    data = request.form
    file = request.files['file']
    if not file:
        return jsonify({'message': 'No file uploaded'}), 400

    document_name = data.get('name')
    document_type = data.get('type')

    if not document_name or not document_type:
        return jsonify({'message': 'Missing required fields'}), 400

    document = Document.query.filter_by(name=document_name).first()
    if document:
        return jsonify({'message': 'Document name should be unique'}), 401
   
    document = Document(name=document_name)
    db.session.add(document)
    db.session.commit()

    version_number = len(document.versions) + 1
    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{filename}")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file.save(file_path)

    document_version = DocumentVersion(document_id=document.id, type=document_type, version_number=version_number, file_path=file_path)
    db.session.add(document_version)
    db.session.commit()

    return jsonify({'message': 'Document uploaded successfully'}), 201






@app.route('/documents/addMore/<int:id>', methods=['POST'])
def add_document(id):
    data = request.form
    file = request.files['file']
    if not file:
        return jsonify({'message': 'No file uploaded'}), 400

    document_type = data.get('type')

    if not document_type:
        return jsonify({'message': 'Missing required fields'}), 400

    document = Document.query.filter_by(id=id).first()
    if not document:
        return jsonify({'message': 'User is incorrect'}), 400

    version_number = len(document.versions) + 1
    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{filename}")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file.save(file_path)

    document_version = DocumentVersion(document_id=document.id, type=document_type, version_number=version_number, file_path=file_path)
    db.session.add(document_version)
    db.session.commit()

    return jsonify({'message': 'Document uploaded successfully'}), 201

@app.route('/documents/get', methods=['GET'])
def get_documents():
    documents = Document.query.order_by(Document.created_at.desc())
    return jsonify([{
        'id': doc.id,
        'name': doc.name,
        'created_at': doc.created_at,
        'versions': [{'version': v.version_number, "type": v.type ,'uploaded_at': v.uploaded_at, 'file_path': f"{v.file_path[8:len(v.file_path)+ 1]}"} for v in doc.versions]
    } for doc in documents]), 200



@app.route("/documents/getbyid/<int:id>")
def get_by_id(id):
    user = Document.query.filter_by(id=id).first()
    return jsonify([{
        "name":user.name,
    }])


# @app.route('/documents/delete/<int:id>', methods=['DELETE'])      It is not in use just created to see the working.
# def delete_document(id):
#     document = Document.query.get(id)
#     if not document:
#         return jsonify({'message': 'Document not found'}), 404
    
#     for version in document.versions:
#         if os.path.exists(version.file_path):
#             os.remove(version.file_path)
#         db.session.delete(version)

#     db.session.delete(document)
#     db.session.commit()

#     return jsonify({'message': 'Document deleted successfully'}), 200





if __name__ == "__main__":
     app.run(debug=True)