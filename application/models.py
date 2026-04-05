from .database import db
from datetime import date

class Admin(db.Model):
    id = db.Column(db.Integer(),primary_key = True)
    email = db.Column(db.String(),unique = True, nullable = False)
    password = db.Column(db.String(),nullable= False)

class Student(db.Model):
    id = db.Column(db.Integer(),primary_key = True)
    name = db.Column(db.String(),nullable = False)
    email = db.Column(db.String(),unique = True, nullable = False)
    password = db.Column(db.String(),nullable= False)
    cgpa = db.Column(db.Float(),nullable = False)
    department = db.Column(db.String(),nullable = False)
    blacklist = db.Column(db.Boolean(),default = False)
    resume = db.Column(db.String()) 
    pfp = db.Column(db.String())

class Company(db.Model):
    id = db.Column(db.Integer(),primary_key = True)
    name = db.Column(db.String(),nullable = False)
    email = db.Column(db.String(),unique = True, nullable = False)
    password = db.Column(db.String(),nullable= False)
    contact = db.Column(db.String(),nullable = False)
    website = db.Column(db.String(),nullable = False)
    overview = db.Column(db.String(),nullable = False)
    status = db.Column(db.String(),default = "pending") #pending, approved, rejected
    blacklist = db.Column(db.Boolean(),default = False)
    logo = db.Column(db.String())

class Drive(db.Model):
    id = db.Column(db.Integer(),primary_key = True)
    name = db.Column(db.String(),nullable = False)
    company_id = db.Column(db.Integer(),db.ForeignKey("company.id", ondelete="CASCADE"),nullable = False)
    title = db.Column(db.String(),nullable = False)
    salary = db.Column(db.String(50), nullable=False)      
    description = db.Column(db.String(),nullable = False)
    location = db.Column(db.String(100), nullable=False)
    cgpa_criteria = db.Column(db.Float(),nullable = False)
    deadline = db.Column(db.Date(),nullable = False)
    status = db.Column(db.String(),default = "pending") #pending, approved, closed
    company =db.relationship('Company', backref='drives')

class Application(db.Model):
    id = db.Column(db.Integer(),primary_key = True)
    # student_name = db.Column(db.String(), db.ForeignKey("student.name"), nullable=False)
    student_id = db.Column(db.Integer(),db.ForeignKey("student.id",ondelete="CASCADE") ,nullable = False)
    company_id = db.Column(db.Integer(),db.ForeignKey("company.id", ondelete="CASCADE"),nullable = False)
    drive_id = db.Column(db.Integer(),db.ForeignKey("drive.id", ondelete="CASCADE"), nullable = False)
    date_applied = db.Column(db.Date(), default=date.today)
    status = db.Column(db.String(),default = "applied") #applied, shortlisted, rejected, selected
    interview = db.Column(db.String(),default = "In-Person") #In-Person, Online
    remarks = db.Column(db.String(),default = "None")
    drive = db.relationship('Drive', backref='applications')
    company = db.relationship('Company', backref='applications')
    student = db.relationship('Student', backref='applications')