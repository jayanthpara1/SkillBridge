from flask import Flask, render_template, request, redirect, session, flash
import csv
import os
from pdfrw import PdfReader, PdfWriter, PageMerge
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATA_DIR = 'data/'

# Load users from CSV
def load_users():
    if not os.path.exists(DATA_DIR + 'users.csv'):
        return []
    with open(DATA_DIR + 'users.csv', mode='r') as file:
        return [row for row in csv.reader(file) if row]  # Skip empty rows

# Save user to CSV
def save_user(username, email, password):
    with open(DATA_DIR + 'users.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([username, email, password])

# Save application to CSV
def save_application(name, email, phone, college, branch, internship_id):
    with open(DATA_DIR + 'applications.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([timestamp, name, email, phone, college, branch, internship_id])

# Function to fill a PDF template
def fill_pdf_template(name, internship_id, college):
    template_path = "C:\\Users\\91934\\Downloads\\template.pdf"
    output_path = os.path.join(os.path.expanduser("~"), "Downloads", f"{name}_offer_letter.pdf")

    # Read the template PDF
    template_pdf = PdfReader(template_path)
    
    # This assumes you have a text field in your template for name, internship_id, and college
    for page in template_pdf.pages:
        # Modify this part to replace specific placeholders in the PDF
        # You may need to adjust the logic based on your PDF's content structure
        text = f"Dear {name},\n\nWe are pleased to inform you that you have been selected for an internship at SkillBridge for the position of Internship ID: {internship_id}.\n\nCollege: {college}\n\nBest Regards,\nSkillBridge Team"
        
        # Here you would need to add text to the PDF (This is pseudo-code)
        # Replace with actual text-adding code depending on your PDF structure
        page.contents = PageMerge(page).add(text).render()  # Pseudo-code; adjust as needed

    PdfWriter().write(output_path, template_pdf)
    print(f"Offer letter PDF has been created: {output_path}")

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
    user_phone = current_user[2]  # Assuming phone is the third column in users.csv

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
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    college = request.form['college']
    branch = request.form['branch']
    internship_id = request.form['internship_id']

    # Save the application details
    save_application(name, email, phone, college, branch, internship_id)

    # Generate the offer letter PDF
    fill_pdf_template(name, internship_id, college)

    # Temporarily disable email sending
    # send_email(email, 'Internship Application Received', offer_letter)

    return render_template('celebration.html', name=name)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
