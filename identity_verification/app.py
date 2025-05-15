import os
from flask import Flask, request, jsonify, render_template
from the_code import Identity_Verification  # Your verification class
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Set the folder to store uploaded files
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create folder if it doesn't exist

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "pdf"}  # Allowed file types

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/verify_identity', methods=['POST'])
def verify_identity():
    try:
        # Check if files are in request
        if "passport_image" not in request.files or "nin_image" not in request.files:
            return jsonify({"error": "Please upload both passport and NIN images"}), 400
        
        passport_file = request.files["passport_image"]
        nin_file = request.files["nin_image"]

        # Check if files have valid names and extensions
        if passport_file.filename == "" or nin_file.filename == "":
            return jsonify({"error": "Invalid file name"}), 400

        if not allowed_file(passport_file.filename) or not allowed_file(nin_file.filename):
            return jsonify({"error": "Unsupported file format"}), 400
        
        # Securely save the files to the upload folder
        passport_path = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(passport_file.filename))
        nin_path = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(nin_file.filename))

        passport_file.save(passport_path)
        nin_file.save(nin_path)

        # Run the verification process
        verifier = Identity_Verification(passport_path, nin_path)
        mrz_data = verifier.extract_passport(passport_path)
        nin_data = verifier.ocr_core(nin_path)
        similarity, diff = verifier.compare_data()

        return jsonify({
            "mrz_data": mrz_data,
            "nin_data": nin_data,
            "similarity": similarity,
            "diff": diff if similarity == 'NO MATCH' else "No differences found"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
