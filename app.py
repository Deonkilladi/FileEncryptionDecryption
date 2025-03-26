import os
from cryptography.fernet import Fernet
from flask import Flask, request, send_file, redirect, url_for, flash, render_template

app = Flask(__name__)
app.secret_key = os.urandom(24)

def generate_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)
    return key

def load_key():
    try:
        with open("key.key", "rb") as key_file:
            return key_file.read()
    except FileNotFoundError:
        print("Key file not found! Generate a key first.")
        return None

def encrypt_file(file_path, key, output_path):
    with open(file_path, "rb") as file:
        data = file.read()
    
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data)
    
    with open(output_path, "wb") as encrypted_file:
        encrypted_file.write(encrypted_data)

def decrypt_file(file_path, key, output_path):
    with open(file_path, "rb") as encrypted_file:
        encrypted_data = encrypted_file.read()
    
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data)
    
    with open(output_path, "wb") as decrypted_file:
        decrypted_file.write(decrypted_data)

@app.route('/encrypt', methods=['POST'])
def encrypt():
    if 'encrypt-file' not in request.files:
        flash('No file selected')
        return redirect(url_for('home'))
    
    file = request.files['encrypt-file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('home'))
    
    filename = file.filename
    file.save(filename)
    
    key = load_key()
    if not key:
        flash('Please generate a key first')
        return redirect(url_for('home'))
    
    output_path = f"encrypted_{filename}"
    encrypt_file(filename, key, output_path)
    os.remove(filename)
    
    return send_file(output_path, as_attachment=True)

@app.route('/decrypt', methods=['POST'])
def decrypt():
    if 'decrypt-file' not in request.files:
        flash('No file selected')
        return redirect(url_for('home'))
    
    file = request.files['decrypt-file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('home'))
    
    filename = file.filename
    file.save(filename)
    
    key = load_key()
    if not key:
        flash('Please generate a key first')
        return redirect(url_for('home'))
    
    output_path = filename.replace("encrypted_", "")
    decrypt_file(filename, key, output_path)
    os.remove(filename)
    
    return send_file(output_path, as_attachment=True)

@app.route('/generate_key', methods=['POST'])
def generate():
    generate_key()
    flash("Key generated!")
    return redirect(url_for('home'))

@app.route('/download_key')
def download_key():
    if os.path.exists("key.key"):
        return send_file("key.key", as_attachment=True)
    else:
        flash("Key file not found!")
        return redirect(url_for('home'))

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
