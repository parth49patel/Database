from flask import Flask, render_template, request, jsonify
from hashlib import sha256
from database import Connection  # Assuming you have this module set up

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Auto-reload templates for development
db = Connection()  # Database connection

@app.route('/')
def index():
    # Serve the registration page
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.json  # Expecting JSON data
        fname = data['fname']
        lname = data['lname']
        email = data['email']
        password = data['password']

        # Hash the password using SHA-256
        hashed_password = sha256(password.encode()).hexdigest()

        # Insert user into the database with parameterized query
        query = """
        INSERT INTO user (email, fname, lname, user_password)
        VALUES (%s, %s, %s, %s)
        """
        db.execute_query(query, (email, fname, lname, hashed_password))

        return jsonify({'message': 'User registered successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3000, debug=True)
