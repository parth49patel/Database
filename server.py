from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from hashlib import sha256
from database import Connection  # Assuming you have this module set up
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import date
from flask_cors import CORS
import os
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.config["TEMPLATES_AUTO_RELOAD"] = True  # Auto-reload templates for development
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_page"
db = Connection()  # Database connection

class User(UserMixin):
    def __init__(self, email):
        self.email = email

    def get_id(self):
        return self.email

@login_manager.user_loader
def load_user(email):
    query = "SELECT email FROM user WHERE email = %s"
    db.execute_query(query, (email,))
    result = db.cur.fetchone()
    if result:
        return User(result[0])
    return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register")
def register_page():
    return render_template("register.html")


@app.route("/courseFinder")
@login_required
def courseFinder_page():
    allow_access()  # Check if the user is authenticated
    return render_template("courseFinder.html")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/index")
def index_page():
    return render_template("index.html")


@app.route("/resume")
@login_required
def resume_page():
    allow_access()  # Check if the user is authenticated
    return render_template("resume.html")


@app.route("/profile")
@login_required
def profile_page():
    allow_access()  # Check if the user is authenticated
    return render_template("profile.html")


@app.route("/register", methods=["POST"])
def register_user():
    try:
        data = request.json
        fname = data["fname"]
        lname = data["lname"]
        email = data["email"]
        password = data["password"]

        hashed_password = sha256(password.encode()).hexdigest()

        query = """
        INSERT INTO user (email, fname, lname, user_password)
        VALUES (%s, %s, %s, %s)
        """
        db.execute_query(query, (email, fname, lname, hashed_password))

        user = User(email)
        login_user(user)
        session["email"] = email

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400


def allow_access():
    """Ensure the user is logged in before granting access."""
    if not current_user.is_authenticated:
        return redirect(url_for("login_page"))
    else:
        return  # Allow access


def verify_password(email, password):
    hashed_password = sha256(password.encode()).hexdigest()
    query = "SELECT user_password FROM user WHERE email = %s"
    try:
        db.execute_query(query, (email,))
        result = db.cur.fetchone()
        if not result:
            return False
        stored_password = result[0]
        return hashed_password == stored_password
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"success": False, "error": "Email and password are required"}), 400

    if verify_password(email, password):
        user = User(email)
        login_user(user)
        session["email"] = email  # Store email in session
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Incorrect email or password"})


@app.route("/fetch_jobs", methods=["GET"])
def fetch_jobs():
    try:
        query = """
            SELECT 
                jp.job_id,
                jp.job_role,
                c.company_name,
                jp.location
            FROM job_posting jp
            JOIN companies c ON jp.company = c.company_id
        """
        jobs = db.fetch_all(query)
        return jsonify(jobs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/fetch_job_details", methods=["POST"])
def fetch_job_details():
    try:
        data = request.get_json()
        job_id = data.get("jobId")

        if not isinstance(job_id, int):
            return jsonify({"error": "Invalid jobId; must be an integer"}), 400

        query = """
            SELECT 
                jp.job_role,
                jp.job_description,
                c.company_name,
                jp.location,
                jp.salary,
                jp.application_deadline,
                jp.employment_type,
                jp.remote_option,
                jp.industry,
                jp.company
            FROM job_posting jp
            JOIN companies c ON jp.company = c.company_id
            WHERE jp.job_id = %s
        """
        result = db.fetch_all(query, job_id)

        if result:
            job = result[0]
            job_details = {
                "job_role": job[0],
                "job_description": job[1],
                "company_name": job[2],
                "location": job[3],
                "salary": str(job[4]),
                "application_deadline": job[5].isoformat(),
                "employment_type": job[6],
                "remote_option": bool(job[7]),
                "industry": job[8],
            }

            skills_query = """
                SELECT s.skill_name, js.proficiency_required, js.num_years_required
                FROM job_skills js
                JOIN skills s ON js.skill = s.skill_id
                WHERE js.job_id = %s
            """
            skills_result = db.fetch_all(skills_query, job_id)
            job_skills = [
                {
                    "skill_name": skill[0],
                    "proficiency_required": skill[1],
                    "num_years_required": skill[2],
                }
                for skill in skills_result
            ]
            job_details["skills"] = job_skills

            contacts_query = """
                SELECT c.fname, c.lname, c.contact_role, c.linkedIn, c.location
                FROM contacts c
                WHERE c.company = %s
                LIMIT 3
            """
            contacts_result = db.fetch_all(contacts_query, job[9])
            contacts = [
                {
                    "fname": contact[0],
                    "lname": contact[1],
                    "contact_role": contact[2],
                    "linkedIn": contact[3],
                    "location": contact[4],
                }
                for contact in contacts_result
            ]
            job_details["contacts"] = contacts

            return jsonify(job_details)
        else:
            return jsonify({"error": "Job not found"}), 404

    except Exception as e:
        print("Error fetching job details:", e)
        return jsonify({"error": "Internal server error"}), 500


@app.route("/fetch_courses", methods=["GET"])
def fetch_courses():
    allow_access()  # Check if the user is authenticated
    try:
        query = """SELECT c.course_id, c.course_name, c.instructor, c.cost, c.course_description, s.skill_name, s.category 
        FROM course_rec c
        LEFT JOIN skills s ON c.skill = s.skill_id"""
        courses = db.fetch_all(query)
        return jsonify(courses)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/fetch_skills", methods=["GET"])
def fetch_skills():
    try:
        query = "SELECT category FROM skills"
        skills = db.fetch_all(query)
        return jsonify([skill[0] for skill in skills])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route("/get-user-skills", methods=["GET"])
def get_user_skills():
    try:
        user_email = current_user.email
        print(user_email)

        if not user_email:
            return jsonify({"error": "Missing user_email parameter"}), 400

        query = """
            SELECT 
                user_email,
                skill_name,
                proficiency,
                num_years
            FROM user_skill_summary
            WHERE user_email = %s
        """
        skills = db.fetch_all(query, user_email)
        
        query = """
            SELECT fname, lname
            FROM user
            WHERE email = %s
        """

        # Fetch the user info
        user_info = db.fetch_all(query, user_email)

        query = """
            SELECT user_email, job_role, company, status, date_applied
            FROM application_summary
            WHERE user_email = %s
        """
        
        # Fetch data for the user_email
        result = db.fetch_all(query, user_email)


        print(skills, user_info, result)
        return jsonify(skills, user_info, result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-application-summary", methods=["GET"])
def get_application_summary():
    try:
        # Get the user_email from the query parameters
        user_email = current_user.email
        print(user_email)
        
        # Check if user_email is provided
        if not user_email:
            return jsonify({"error": "Missing user_email parameter"}), 400
        
        # Define the SQL query to get data from the application_summary view
        query = """
            SELECT user_email, job_role, company, status, date_applied
            FROM application_summary
            WHERE user_email = %s
        """
        
        # Fetch data for the user_email
        result = db.fetch_all(query, user_email)
        
        # Check if data exists
        if not result:
            return jsonify({"message": "No applications found for this user."}), 404
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete-application', methods=['POST'])
def delete_application():
    job_id = request.json.get('id')  # ID of the application to delete
    query = "DELETE FROM application_tracker WHERE user_email = %s AND job_id = %s"
    try:
        db.execute_query(query, (current_user.email, job_id))
        return jsonify({"success": True, "message": "Application deleted successfully."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    
@app.route('/update_status', methods=['POST'])
def update_status():
    job_id = request.json.get('job_id')
    new_status = request.json.get('status')
    if not job_id or not new_status:
        return jsonify({'error': 'Missing application ID or status'}), 400

    try:
        query = "UPDATE application_tracker SET status = %s WHERE job_id = %s AND user_email = %s"
        db.execute_query(query, (new_status, job_id, current_user.email))
        return jsonify({'message': 'Status updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/logout")
@login_required
def logout():
    logout_user()  # Logs the user out via Flask-Login
    session.pop("email", None)  # Ensure email is cleared from the session
    return redirect(url_for("login_page"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3000, debug=True)
