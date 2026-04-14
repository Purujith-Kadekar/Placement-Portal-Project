from flask import Flask, render_template, request, redirect, url_for, flash
from flask import current_app as app #to avoid the circular import error, as we are importing app from app.py and app.py is importing controllers.py, so to avoid this we are using current_app which is a proxy for the application object, it allows us to access the application context without directly importing the app object from app.py
from .models import * #as models is inside the applications folder
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date

@app.errorhandler(404)
def page_not_found(_):
    return render_template("error.html"), 404 #this 404 keeps the status 404 only instead of changing the status to 200 as the page is rendered 

@app.route('/')
def Home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def Login():
    if request.method == 'POST':
        email = request.form['email']  
        password = request.form['pass']
        #Admin Login  
        admin = Admin.query.filter_by(email=email).first()
        if admin and check_password_hash(admin.password, password):
            session['role'] = 'admin'
            return redirect('/admin')
        #Student Login
        if not admin:
            student = Student.query.filter_by(email=email).first()
            if student:
                if not check_password_hash(student.password, password):
                    return render_template('login.html', error="Invalid email or password. Please try again.")
                if student.blacklist:
                    return render_template('login.html', error="Your account has been blacklisted. Please contact the administrator.")
                else:
                    if student and check_password_hash(student.password, password) and not student.blacklist:
                        session['role'] = 'student'
                        session['student_id'] = student.id
                        return redirect(f"/student/{student.id}")
            #Company Login
            company = Company.query.filter_by(email=email).first()
            if company:
                if not check_password_hash(company.password, password):
                    return render_template('login.html', error="Invalid email or password. Please try again.")
                if company.status == "pending":
                    return render_template('login.html', error="Your registration is pending approval. Please wait for the administrator to approve your account.")
                if company.status == "rejected":
                    return render_template('login.html', error="Your registration is rejected. Please contact the administrator.")
                if company.blacklist:
                    return render_template('login.html', error="Your account has been blacklisted. Please contact the administrator.")
                else:
                    if company and company.status == "approved" and check_password_hash(company.password, password):
                        session['role'] = 'company'
                        session['company_id'] = company.id
                        return redirect(f"/company/{company.id}")
            elif not (company or student):
                return render_template('login.html', error="User not found. Please register first.")
    return render_template('login.html')

@app.route('/logout')
def Logout():
    session.clear() #clears the session data, logs out the user
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def Register():
    return render_template('register.html')

@app.route('/register/student', methods=['GET', 'POST'])
def Register_Student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['pass']
        cgpa = request.form['cgpa']
        department = request.form['department']
        resume = request.files.get('resume')
        pfp = request.files.get('pfp')
        hashed_password = generate_password_hash(password)
        
        if not Student.query.filter_by(email=email).first():
            if not resume or resume.filename == '':
                flash("Resume is required. Please upload your resume in PDF format.")
                return render_template('register_student.html')
            if not pfp or pfp.filename == '':
                flash("Profile picture is required. Please upload a profile picture in jpg, jpeg, or png format.")
                return render_template('register_student.html')
            if not resume.filename.lower().endswith('.pdf'):
                flash("Invalid file format. Please upload a PDF file.")
                return render_template('register_student.html')
            if not pfp.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                flash("Invalid file format. Please upload a jpg, jpeg, or png file.")
                return render_template('register_student.html')

            student = Student(name=name, email=email, password=hashed_password, cgpa=cgpa, department=department)
            db.session.add(student)
            db.session.flush() # Flush to get the student ID before commit
            student.resume = f"{student.id}.pdf"
            resume.save('static/resumes/' + student.resume)

            if pfp.filename.lower().endswith('.jpg'):
                student.pfp = f"{student.id}.jpg"
            elif pfp.filename.lower().endswith('.jpeg'):
                student.pfp = f"{student.id}.jpeg"
            else:
                student.pfp = f"{student.id}.png"
            pfp.save('static/student-pfp/' + student.pfp)
            db.session.commit()
        else:
            return render_template('register_student.html', error="Email already registered. Please use a different email or login.")
        return render_template('login.html', success="Registration successful. Please login.")
    return render_template('register_student.html')

# @app.route('/register/error')
# def error():
#     return render_template('dbreg_error.html')

@app.route('/register/company', methods=['GET', 'POST'])
def Register_Company():
    if request.method == 'POST':
        name = request.form['company_name']
        email = request.form['email']
        password = request.form['pass']
        contact = request.form['hr_contact']
        website = request.form['website']
        overview = request.form['overview']
        logo = request.files.get('logo')
        hashed_password = generate_password_hash(password)
        # Create a new company
        if not Company.query.filter_by(email=email).first():
            company = Company(name=name, email=email, password=hashed_password, contact=contact, website=website, overview=overview)
            db.session.add(company)
            db.session.flush()
            if logo and logo.filename != '':
                logo_name = logo.filename.lower()
                if logo_name.endswith('.jpg'):
                    filename = f"{company.id}.jpg"
                elif logo_name.endswith('.jpeg'):
                    filename = f"{company.id}.jpeg"
                elif logo_name.endswith('.png'):
                    filename = f"{company.id}.png"
                else:
                    flash("Invalid file format. Please upload a jpg, jpeg, or png file.")
                    return render_template('register_comp.html')
                logo.save('static/comp-logo/' + filename)
                company.logo = filename
            db.session.commit()
        else:
            return render_template('register_comp.html', error="Email already registered. Please use a different email or login.")
        return render_template('login.html', success="Registration successful. Please login.")
    return render_template('register_comp.html')

# Admin
@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if 'role' in session and session['role'] == 'admin': #checks if the user is logged in and is an admin
        drives = Drive.query.all()
        applications = Application.query.all()
        companies = Company.query.filter(Company.status == "approved").all()
        students = Student.query.all()
        total_students = Student.query.count()
        total_companies = Company.query.filter_by(status="approved").count()
        total_applications = Application.query.count()
        total_drives = Drive.query.filter_by(status="approved").count()
        blacklistc = request.form.get('blacklistc')
        blacklists = request.form.get('blacklists')
        if blacklistc:
            company = Company.query.filter_by(id=blacklistc).first()
            if company:
                company.blacklist = True
                db.session.commit()
                return redirect('/admin')
        if blacklists:
            student = Student.query.filter_by(id=blacklists).first()
            if student:
                student.blacklist = True
                db.session.commit()
                return redirect('/admin')
        unblacklistc = request.form.get('unblacklistc')
        unblacklists = request.form.get('unblacklists')
        if unblacklistc:
            company = Company.query.filter_by(id=unblacklistc).first()
            if company:
                company.blacklist = False
                db.session.commit()
                return redirect('/admin')
        if unblacklists:
            student = Student.query.filter_by(id=unblacklists).first()
            if student:
                student.blacklist = False
                db.session.commit()
                return redirect('/admin')
        approve_out = Company.query.filter_by(status="pending").all()
        approval_in = request.form.get('approve')
        reject = request.form.get('reject')
        if approval_in:
            company = Company.query.filter_by(email=approval_in).first()
            if company:
                company.status = "approved"
                db.session.commit()
                return redirect('/admin')
        if reject:
            company = Company.query.filter_by(email=reject).first()
            if company:
                company.status = "rejected"
                db.session.commit()
                return redirect('/admin')
        dapprove_out = Drive.query.filter_by(status="pending").all() #for drive approval
        dapproval_in = request.form.get('dapprove')
        if dapproval_in:
            drive = Drive.query.filter_by(id=dapproval_in).first()
            if drive:
                drive.status = "approved"
                db.session.commit()
                return redirect('/admin')
        complete = request.form.get('complete')
        if complete:
            drive = Drive.query.filter_by(id=complete).first()
            if drive:
                drive.status = "closed"
                db.session.commit()
                return redirect('/admin')
        return render_template('admin/admin_dash.html', drives=drives, companies=companies, students=students, applications=applications, approve_out=approve_out, dapprove_out=dapprove_out, total_students=total_students, total_companies=total_companies, total_applications=total_applications, total_drives=total_drives)
    else:
        return redirect('/login')

@app.route('/admin/search', methods=['GET'])
def admin_search():
    if 'role' in session and session['role'] == 'admin':
        query = request.args.get('search', '')
        students = Student.query.filter(Student.name.ilike(f"%{query}%")).all() #using get request, which when using this mehtod return a string and we are using ilike to search for the name of the student in the database, and we are using % to search for the name that contains the query string
        companies = Company.query.filter(Company.status == "approved", Company.name.ilike(f"%{query}%")).all()
        return render_template('admin/admin_dash.html', students=students, companies=companies,
            drives=Drive.query.all(), applications=Application.query.all(),
            approve_out=Company.query.filter_by(status="pending").all(),
            dapprove_out=Drive.query.filter_by(status="pending").all(),
            total_students=Student.query.count(), total_companies=Company.query.filter_by(status="approved").count(),
            total_applications=Application.query.count(), total_drives=Drive.query.filter_by(status="approved").count())
    return redirect('/login')

@app.route('/admin/sapp_details/<int:student_id>', methods=['GET', 'POST'])
def Admin_Student_Details(student_id):
    if 'role' in session and session['role'] == 'admin':
        student = Student.query.get(student_id)
        if not student:
            return render_template('error.html'), 404
        applications = Application.query.filter_by(student_id=student_id).all()
        return render_template('admin/sapp_admin.html', student = student, student_name=student.name, applications=applications)
    else:
        return redirect('/login')

@app.route('/admin/drive_details/<int:drive_id>', methods=['GET', 'POST'])
def Admin_Drive_Details(drive_id):
    if 'role' in session and session['role'] == 'admin':
        drive = Drive.query.get(drive_id)
        if not drive:
            return render_template('error.html'), 404
        return render_template('admin/drive_admin.html', drive=drive)
    else:
        return redirect('/login')

# Student
@app.route('/student/<int:student_id>', methods=['GET', 'POST'])
def Student_Home(student_id):
    if 'role' in session and session['role'] == 'student' and session['student_id'] == student_id:
        student = Student.query.get(student_id)
        if not student:
            return redirect('/login')
        company = Company.query.filter(Company.blacklist==False, Company.status=="approved").all()
        applications = Application.query.filter_by(student_id=student_id).all()
        return render_template('student/student_dash.html', student_name=student.name, companies=company, student_id=student.id, applications=applications)
    else:
        return redirect('/login')

@app.route('/student/<int:student_id>/drive_details/<int:drive_id>', methods=['GET', 'POST'])
def Student_Drive_Details(student_id, drive_id):
    if 'role' in session and session['role'] == 'student' and session['student_id'] == student_id:
        drive = Drive.query.get(drive_id)
        if not drive:
            return render_template('error.html'), 404
        company = Company.query.get(drive.company_id)
        if not company:
            return render_template('error.html'), 404
        student = Student.query.filter_by(id=student_id).first()
        apply = request.form.get('apply')
        if apply:
            # check deadline
            if drive.deadline < date.today():
                flash("Application deadline has passed")
                return redirect(f'/student/{student.id}/comp_details/{company.id}')

            # check eligibility
            if student.cgpa < drive.cgpa_criteria:
                flash("You are not eligible for this drive")
                return redirect(f'/student/{student.id}/comp_details/{company.id}')

            if not Application.query.filter_by(student_id=student_id, drive_id=drive_id).first():
                application = Application(student_id=student_id, drive_id=drive_id, company_id=company.id)
                db.session.add(application)
                db.session.commit()
                return redirect(f'/student/{student.id}/comp_details/{company.id}')
            
            else:
                # return render_template('dbapply_error.html', student_id=student_id, company=company)
                flash("Already applied to this drive")
                return redirect(f'/student/{student.id}/comp_details/{company.id}')
        return render_template('student/drive_student.html', drive=drive, company=company , student_id=student_id, drive_id=drive_id)
    else:
        return redirect('/login')

@app.route('/student/<int:student_id>/student_drive/<int:drive_id>', methods=['GET', 'POST'])
def Drive_Details(student_id, drive_id):
    if 'role' in session and session['role'] == 'student' and session['student_id'] == student_id:
        drive = Drive.query.get(drive_id)
        if not drive:
            return render_template('error.html'), 404
        company = Company.query.get(drive.company_id)
        if not company:
            return render_template('error.html'), 404
        student = Student.query.filter_by(id=student_id).first()
        return render_template('student/drive_student_details.html', drive=drive, company=company , student_id=student_id, drive_id=drive_id)
    else:
        return redirect('/login')

@app.route('/student/<int:student_id>/comp_details/<int:company_id>', methods=['GET', 'POST'])
def Student_Apply(student_id, company_id):
    if 'role' in session and session['role'] == 'student' and session['student_id'] == student_id:
        company = Company.query.get(company_id)
        if not company:
            return render_template('error.html'), 404
        drives= Drive.query.filter(Drive.company_id==company_id, Drive.status=="approved").all()
        return render_template('student/comp_details.html', drives=drives, company_name=company.name, student_id=student_id, company=company)
    else:
        return redirect('/login')

@app.route('/student/<int:student_id>/sapp_history', methods=['GET', 'POST'])
def Student_Application_History(student_id):
    if 'role' in session and session['role'] == 'student' and session['student_id'] == student_id:
        student = Student.query.get(student_id)
        if not student:
            return redirect('/login')
        applications = Application.query.filter_by(student_id=student_id).all()
        return render_template('student/Sapp_history.html', student=student, applications=applications)
    else:
        return redirect('/login')

@app.route('/student/<int:student_id>/sapp_history_comp/<int:company_id>', methods=['GET', 'POST'])
def Student_Application_History_Company(student_id, company_id):
    if 'role' in session and session['role'] == 'student' and session['student_id'] == student_id:
        student = Student.query.get(student_id)
        if not student:
            return redirect('/login')
        applications = Application.query.filter_by(student_id=student_id).all()
        return render_template('student/Sapp_history_comp.html', student=student, applications=applications, company_id=company_id)
    else:
        return redirect('/login')

@app.route('/student/<int:student_id>/update', methods=['GET', 'POST'])
def Student_Update(student_id):
    if 'role' in session and session['role'] == 'student' and session['student_id'] == student_id:
        student = Student.query.get(student_id)
        if request.method == 'POST':
            student.name = request.form['name']
            student.email = request.form['email']
            student.cgpa = request.form['cgpa']
            student.department = request.form['department']  
            new_pass = request.form.get('pass')          
            if new_pass: 
                student.password = generate_password_hash(new_pass)
            resume = request.files.get('resume')
            pfp = request.files.get('pfp')
            if resume and resume.filename != '':
                if resume.filename.lower().endswith('.pdf'):
                    resume_filename = f"{student.id}.pdf"
                    resume.save('static/resumes/' + resume_filename)
                    student.resume = resume_filename
                else:
                    flash("Invalid file format. Please upload a PDF file.")
                    return render_template('student/student_update.html', student=student)
            if pfp and pfp.filename != '':
                pfp_name = pfp.filename.lower()
                if pfp_name.endswith('.jpg'):
                    pfp_filename = f"{student.id}.jpg"
                elif pfp_name.endswith('.jpeg'):
                    pfp_filename = f"{student.id}.jpeg"
                elif pfp_name.endswith('.png'):
                    pfp_filename = f"{student.id}.png"
                else:
                    flash("Invalid file format. Please upload a jpg, jpeg, or png file.")
                    return render_template('student/student_update.html', student=student)
                pfp.save('static/student-pfp/' + pfp_filename)
                student.pfp = pfp_filename
            db.session.commit()
            return redirect(f'/student/{student_id}')
        return render_template('student/student_update.html', student=student)
    else:
        return redirect('/login')

# Company
@app.route('/company/<int:company_id>', methods=['GET', 'POST'])
def Company_Home(company_id):
    if 'role' in session and session['role'] == 'company' and session['company_id'] == company_id:
        company = Company.query.get(company_id)
        if not company:
            return redirect('/login')
        drives =Drive.query.filter_by(company_id=company_id).all()
        complete = request.form.get('complete')
        active = request.form.get('active')
        if complete:
            drive = Drive.query.filter_by(id=complete).first()
            if drive:
                drive.status = "closed"
                db.session.commit()
                return redirect(f'/company/{company_id}')
        if active:
            drive = Drive.query.filter_by(id=active).first()
            if drive:
                drive.status = "pending"
                db.session.commit()
                return redirect(f'/company/{company_id}')
        return render_template('company/comp_dash.html', company_name=company.name, company_id=company_id, drives=drives)
    else:
        return redirect('/login')

@app.route('/company/<int:company_id>/drive_app/<int:drive_id>', methods=['GET', 'POST'])
def Drive_Applications(company_id, drive_id):
    if 'role' in session and session['role'] == 'company' and session['company_id'] == company_id:
        drive = Drive.query.get(drive_id)
        if not drive or drive.company_id != company_id:
            return redirect(f'/company/{company_id}')
        applications = Application.query.filter_by(drive_id=drive_id).all()
        student = Student.query.filter_by(id = drive_id).first()
        return render_template('company/drive_app.html', drive=drive, applications=applications, company_id=company_id, student=student)
    else:
        return redirect('/login')

@app.route('/company/<int:company_id>/create_drive', methods=['GET', 'POST'])
def Create_Drive(company_id):
    if 'role' in session and session['role'] == 'company' and session['company_id'] == company_id:
        if request.method == 'POST':
            title = request.form['title']
            name = request.form['name']
            description = request.form['description']
            eligibility = request.form['eligibility']
            deadline = request.form['deadline']
            salary = request.form['salary']
            location = request.form['location']
            deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date()
            drive = Drive(company_id=company_id, name=name, title=title, description=description, cgpa_criteria=eligibility, deadline=deadline_date, salary=salary, location=location)
            db.session.add(drive)
            db.session.commit()
            return redirect(f'/company/{company_id}')
        return render_template('company/drive_comp.html', company_id=company_id)
    else:
        return redirect('/login')

@app.route('/company/<int:company_id>/update_drive/<int:drive_id>', methods=['GET', 'POST'])
def Update_Drive(company_id, drive_id):
    if 'role' in session and session['role'] == 'company' and session['company_id'] == company_id:
        drive=Drive.query.get(drive_id)
        if not drive or drive.company_id != company_id:
            return redirect(f'/company/{company_id}')
        if request.method == 'POST':
            drive.title = request.form['title']
            drive.name = request.form['name']
            drive.description = request.form['description']
            drive.cgpa_criteria = request.form['eligibility']
            drive.deadline = request.form['deadline']
            drive.salary = request.form['salary']
            drive.location = request.form['location']
            deadline_date = datetime.strptime(drive.deadline, '%Y-%m-%d').date()
            drive.deadline = deadline_date
            db.session.commit()
            return redirect(f'/company/{company_id}')
        return render_template('company/drive_update.html', drive=drive, company_id=company_id)
    else:
        return redirect('/login')

@app.route('/company/<int:company_id>/sapp_details/<int:application_id>', methods=['GET', 'POST'])
def Company_Student_Details(application_id, company_id):
    if 'role' in session and session['role'] == 'company' and session['company_id'] == company_id:
        application = Application.query.get(application_id)
        if not application or application.company_id != company_id:
            return redirect(f'/company/{company_id}')
        student = Student.query.get(application.student_id)
        if not student:
            return redirect(f'/company/{company_id}')
        drive_id = application.drive_id
        status = request.form.get('status')
        interview = request.form.get('interview')
        remarks = request.form.get('remarks')
        if request.method == 'POST':
            application = Application.query.filter_by(student_id=student.id, drive_id=drive_id).first()
            if interview:
                application.interview = interview
            if remarks:
                application.remarks = remarks
            if status == "shortlist":
                application.status = "shortlisted"
            elif status == "select":
                application.status = "selected"
            elif status == "waiting":
                application.status = "waiting"
            elif status == "reject":
                application.status = "rejected"
            db.session.commit()
            return redirect(f'/company/{company_id}/drive_app/{drive_id}')
        return render_template('company/sapp_comp.html', student = student, student_name=student.name, application=application, company_id=company_id, drive_id=drive_id)
    else:
        return redirect('/login')

@app.route('/company/<int:company_id>/update', methods=['GET', 'POST'])
def Company_Update(company_id):
    if 'role' in session and session['role'] == 'company' and session['company_id'] == company_id:
        company = Company.query.get(company_id)
        if request.method == 'POST':
            company.name = request.form['name']
            company.email = request.form['email']
            company.overview = request.form['overview']
            new_pass = request.form.get('pass')
            if new_pass:
                company.password = generate_password_hash(new_pass)
            logo = request.files.get('logo')
            if logo and logo.filename != '':
                logo_name = logo.filename.lower()
                if logo_name.endswith('.jpg'):
                    filename = f"{company.id}.jpg"
                elif logo_name.endswith('.jpeg'):
                    filename = f"{company.id}.jpeg"
                elif logo_name.endswith('.png'):
                    filename = f"{company.id}.png"
                else:
                    flash("Invalid file format. Please upload a jpg, jpeg, or png file.")
                    return render_template('company/comp_update.html', company=company)
                logo.save('static/comp-logo/' + filename)
                company.logo = filename
            db.session.commit()
            return redirect(f'/company/{company_id}')
        return render_template('company/comp_update.html', company=company)
    else:
        return redirect('/login')
