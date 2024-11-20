from flask import Flask, render_template, request, jsonify
from hashlib import sha256
from database import Connection  # Assuming you have this module set up

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Auto-reload templates for development
db = Connection()  # Database connection

@app.route('/')
def index():
    # Serve the registration page
    return render_template('login.html')

# Route to serve the register page
@app.route('/register')
def register_page():
    return render_template('register.html')

# Route to serve the login page
@app.route('/login')
def login_page():
    return render_template('login.html')

# Route to serve the index page
@app.route('/index')
def index_page():
    return render_template('index.html')


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

def verify_password(email, password):
    # Hash the provided password
    hashed_password = sha256(password.encode()).hexdigest()
    print(f"Hashed input password: {hashed_password}")

    # SQL query to fetch the stored password for the given email
    query = "SELECT user_password FROM user WHERE email = %s"
    
    try:
        # Execute the query
        db.execute_query(query, (email,))
        
        # Fetch the result after executing the query
        result = db.cur.fetchone()  # Use fetchone() to get the first row
        
        print(f"Query result: {result}")

        # Extract the stored password from the result (assuming result is a tuple)
        if not result:
            return False  # No matching email found
        
        stored_password = result[0]  # The hashed password will be the first element

        # Compare the stored hashed password with the hashed input password
        return hashed_password == stored_password

    except Exception as e:
        print(f"An error occurred: {e}")
        return False


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    print(email)
    print(password)

    if not email or not password:
        return jsonify({"success": False, "error": "Email and password are required"}), 400

    if verify_password(email, password):
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Incorrect email or password"})
    

@app.route("/fetch_jobs", methods=["GET"])
def fetch_jobs():
    try:
        # Fetch job listings from the database
        query = "SELECT job_role, company, location FROM job_posting"
        jobs = db.fetch_all(query)  # Assuming this returns a list of jobs
        return jsonify(jobs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3000, debug=True)