from flask import Flask, render_template, request, redirect, session, flash
import csv
import os
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATA_DIR = 'data/'

# Load users from CSV
def load_users():
    if not os.path.exists(DATA_DIR + 'users.csv'):
        return []
    with open(DATA_DIR + 'users.csv', mode='r') as file:
        return list(csv.reader(file))

# Save user to CSV
def save_user(username, email, password):
    with open(DATA_DIR + 'users.csv', mode='a') as file:
        writer = csv.writer(file)
        writer.writerow([username, email, password])

# Email sending function
def send_email(to, subject, body):
    from_email = 'your_email@example.com'  # Replace with your email
    from_password = 'your_email_password'   # Replace with your email password
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(from_email, from_password)
        server.send_message(msg)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    users = load_users()
    for user in users:
        if user[0] == username:
            flash('Username already exists!')
            return redirect('/')

    save_user(username, email, password)
    flash('Signup successful!')
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check for admin login
        if username == 'admin':
            session['username'] = username
            return redirect('/dashboard')

        users = load_users()
        for user in users:
            if user[0] == username and user[2] == password:
                session['username'] = username
                return redirect('/dashboard')

        flash('Invalid credentials!')
        return redirect('/')

    # Render login page for GET request
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/')

    # Example internship opportunities
    internship_opportunities = [
        {"title": "Web Development Intern", "description": "Work on building web applications.", "id": 1},
        {"title": "Data Science Intern", "description": "Analyze data and build models.", "id": 2},
        {"title": "Graphic Design Intern", "description": "Create designs for various projects.", "id": 3},
    ]

    return render_template('dashboard.html', username=session['username'], opportunities=internship_opportunities)

@app.route('/apply', methods=['POST'])
def apply():
    if 'username' not in session:
        return redirect('/')

    internship_id = request.form['internship_id']
    user_email = next((user[1] for user in load_users() if user[0] == session['username']), None)

    # Send email using the internship ID for context
    send_email(user_email, 'Internship Application', f'Application received for internship ID: {internship_id}')
    flash('Application submitted!')
    return redirect('/dashboard')

@app.route('/signup')
def signup_page():
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
