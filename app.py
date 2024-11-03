from flask import Flask, render_template, request, redirect, session, flash
import csv
import os
from datetime import datetime
from letter import replace_placeholders, convert_pptx_to_pdf  # Import your PDF generation functions

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATA_DIR = 'data/'
TEMPLATE_PATH = 'C:\\new_projectr\\internships_portal\\template_letter.pptx'  # Update this to your template path
OUTPUT_DIR = 'C:\\new_projectr\\internships_portal\\'  # Ensure this directory exists


# Load users from CSV
def load_users():
    if not os.path.exists(DATA_DIR + 'users.csv'):
        return []
    with open(DATA_DIR + 'users.csv', mode='r') as file:
        return [row for row in csv.reader(file) if row]

# Save user to CSV
def save_user(username, email, password):
    with open(DATA_DIR + 'users.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([username, email, password])

# Save application to CSV
def save_application(name, email, phone, college, branch, internship_id):
    with open(DATA_DIR + 'requests.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([timestamp, name, email, phone, college, branch, internship_id])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            flash('All fields are required!')
            return redirect('/signup')

        users = load_users()
        for user in users:
            if len(user) > 0 and user[0] == username:
                flash('Username already exists!')
                return redirect('/signup')

        save_user(username, email, password)
        flash('Signup successful!')
        return redirect('/')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_users()
        for user in users:
            if len(user) > 2 and user[0] == username and user[2] == password:
                session['username'] = username
                return redirect('/dashboard')

        flash('Invalid credentials!')
        return redirect('/')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/')

    internship_opportunities = [
        {"title": "Web Development Intern", "description": "Work on building web applications.", "id": 1},
        {"title": "Data Science Intern", "description": "Analyze data and build models.", "id": 2},
        {"title": "Graphic Design Intern", "description": "Create designs for various projects.", "id": 3},
    ]

    return render_template('dashboard.html', username=session['username'], opportunities=internship_opportunities)

@app.route('/apply/<int:internship_id>', methods=['GET'])
def apply_page(internship_id):
    if 'username' not in session:
        return redirect('/')

    users = load_users()
    current_user = next((user for user in users if user[0] == session['username']), None)

    if current_user is None or len(current_user) < 3:
        flash("User not found!")
        return redirect('/dashboard')

    user_email = current_user[1]
    user_phone = current_user[2]  # Assuming phone is available in users.csv

    internship = next((opp for opp in [
        {"title": "Web Development Intern", "description": "Work on building web applications.", "id": 1},
        {"title": "Data Science Intern", "description": "Analyze data and build models.", "id": 2},
        {"title": "Graphic Design Intern", "description": "Create designs for various projects.", "id": 3},
    ] if opp["id"] == internship_id), None)

    if internship is None:
        flash("Internship not found!")
        return redirect('/dashboard')

    return render_template('apply.html', internship=internship, email=user_email, phone=user_phone)

@app.route('/submit_application', methods=['POST'])
def submit_application():
    # Get form data with defaults
    name = request.form.get('name', '<name>')
    email = request.form.get('email', '<email>')
    phone = request.form.get('phone', '<phone>')
    college = request.form.get('college', '<college>')
    branch = request.form.get('branch', '<branch>')
    internship_name = request.form.get('internship_name', '<internship_name>')

    # Save the application details
    save_application(name, email, phone, college, branch, internship_name)

    # Generate PDF
    output_pdf = os.path.join(OUTPUT_DIR, f"application_{name.replace(' ', '_')}.pdf")

    # Replace placeholders and convert to PDF
    replace_placeholders(TEMPLATE_PATH, 'temp_letter.pptx', name, internship_name)
    convert_pptx_to_pdf('temp_letter.pptx', output_pdf)

    # Optionally, delete the temporary PPTX file
    os.remove('temp_letter.pptx')

    flash('Application submitted successfully and PDF generated!')
    return redirect('/congrats')

@app.route('/congrats')
def congrats():
    return render_template('celebration.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
