# Placement Portal

A web application built with Flask for managing campus placement drives. It supports three types of users — Admin, Company, and Student — each with their own dashboard and set of actions.

---

## Tech Stack

- **Backend:** Python 3, Flask
- **Database:** SQLite (via Flask-SQLAlchemy)
- **Frontend:** HTML, Jinja2 templates, Bootstrap 5.2.3
- **Password Hashing:** Werkzeug (PBKDF2)
- **Session Management:** Flask session (server-side)

---

## Project Structure

```
MAD1-project/
├── app.py                        # App factory, DB init, admin seed
├── application/
│   ├── database.py               # SQLAlchemy instance
│   ├── models.py                 # DB models (Admin, Student, Company, Drive, Application)
│   └── controllers.py            # All route handlers
├── templates/                    # Jinja2 HTML templates
│   ├── login.html
│   ├── register.html
│   ├── register_student.html
│   ├── register_comp.html
│   ├── admin_dash.html
│   ├── student_dash.html
│   ├── comp_dash.html
│   ├── drive_student.html
│   ├── drive_student_details.html
│   ├── drive_comp.html
│   ├── drive_update.html
│   ├── drive_admin.html
│   ├── drive_app.html
│   ├── comp_details.html
│   ├── comp_update.html
│   ├── sapp_admin.html
│   ├── sapp_comp.html
│   ├── Sapp_history.html
│   ├── Sapp_history_comp.html
│   ├── student_update.html
│   └── error.html
├── static/
│   ├── styles.css
│   ├── resumes/                  # Uploaded student resumes (.pdf)
│   ├── student-pfp/              # Student profile pictures (.jpg/.jpeg/.png)
│   └── comp-logo/                # Company logos (.jpg/.jpeg/.png)
└── instance/
    └── placement.sqlite3         # SQLite database file
```

---

## Database Models

### Admin
| Field    | Type    | Notes              |
|----------|---------|--------------------|
| id       | Integer | Primary key        |
| email    | String  | Unique, not null   |
| password | String  | Hashed, not null   |

### Student
| Field      | Type    | Notes                    |
|------------|---------|--------------------------|
| id         | Integer | Primary key              |
| name       | String  | Not null                 |
| email      | String  | Unique, not null         |
| password   | String  | Hashed, not null         |
| cgpa       | Float   | Not null                 |
| department | String  | Not null                 |
| blacklist  | Boolean | Default: False           |
| resume     | String  | Filename (stored in static/resumes/) |
| pfp        | String  | Filename (stored in static/student-pfp/) |

### Company
| Field     | Type   | Notes                                        |
|-----------|--------|----------------------------------------------|
| id        | Integer | Primary key                                 |
| name      | String  | Not null                                    |
| email     | String  | Unique, not null                            |
| password  | String  | Hashed, not null                            |
| contact   | String  | HR contact number, not null                 |
| website   | String  | Not null                                    |
| overview  | String  | Company description, not null               |
| status    | String  | pending / approved / rejected (default: pending) |
| blacklist | Boolean | Default: False                              |
| logo      | String  | Filename (stored in static/comp-logo/)      |

### Drive
| Field         | Type    | Notes                              |
|---------------|---------|------------------------------------|
| id            | Integer | Primary key                        |
| name          | String  | Drive name, not null               |
| company_id    | Integer | FK → Company (CASCADE delete)      |
| title         | String  | Job title, not null                |
| salary        | String  | Package offered, not null          |
| description   | String  | Job description, not null          |
| location      | String  | Job location, not null             |
| cgpa_criteria | Float   | Minimum CGPA required, not null    |
| deadline      | Date    | Application deadline, not null     |
| status        | String  | pending / approved / closed (default: pending) |

### Application
| Field       | Type    | Notes                                   |
|-------------|---------|------------------------------------------|
| id          | Integer | Primary key                              |
| student_id  | Integer | FK → Student (CASCADE delete)            |
| company_id  | Integer | FK → Company (CASCADE delete)            |
| drive_id    | Integer | FK → Drive (CASCADE delete)              |
| date_applied| Date    | Auto-set to today                        |
| status      | String  | applied / shortlisted / waiting / selected / rejected (default: applied) |
| interview   | String  | In-Person / Online (default: In-Person)  |
| remarks     | String  | Company remarks (default: None)          |

---

## User Roles and Features

### Admin
- Created automatically on first run with credentials `admin@gmail.com` / `admin123`
- Single admin account; no separate registration for admin
- **Dashboard shows:** total students, companies, applications, and active drives
- **Company management:** view all registered companies, approve or reject pending registrations, blacklist / unblacklist companies
- **Drive management:** view all placement drives, approve pending drives, mark drives as closed
- **Student management:** view all students, blacklist / unblacklist students
- **Search:** search students and companies by name using a live search bar
- **Detailed views:** view individual student application history, view drive details

### Company
- Registers via `/register/company` (status starts as `pending` until admin approves)
- Blocked from logging in if status is pending, rejected, or blacklisted
- **Dashboard:** view all drives created by that company with their current status
- **Create drive:** submit a new placement drive (goes to admin for approval)
- **Update drive:** edit drive details (title, description, CGPA criteria, salary, location, deadline)
- **Manage drive status:** mark a drive as closed or reactivate it to pending
- **View applications:** see all students who applied to a specific drive, with their details
- **Manage applicants:** update application status (shortlist, select, wait, reject), set interview mode (In-Person / Online), and add remarks
- **Profile update:** update company name, email, overview, password, and logo

### Student
- Registers via `/register/student`
- Cannot log in if blacklisted
- **Dashboard:** view list of approved, non-blacklisted companies
- **Browse companies:** view company details and their active drives
- **Apply to drives:** eligibility is checked at apply time — CGPA must meet the drive's criteria and the deadline must not have passed; duplicate applications are blocked
- **Application history:** view all applications across companies, with current status, interview mode, and company remarks
- **Profile update:** update name, email, CGPA, department, password, resume, and profile picture

---

## Routes

| Method | Route | Handler | Access |
|--------|-------|---------|--------|
| GET | `/` | Home | Redirects to `/login` |
| GET, POST | `/login` | Login | Public |
| GET | `/logout` | Logout | Any logged-in |
| GET | `/register` | Register | Public |
| GET, POST | `/register/student` | Register_Student | Public |
| GET, POST | `/register/company` | Register_Company | Public |
| GET, POST | `/admin` | admin_dashboard | Admin |
| GET | `/admin/search` | admin_search | Admin |
| GET, POST | `/admin/sapp_details/<student_id>` | Admin_Student_Details | Admin |
| GET, POST | `/admin/drive_details/<drive_id>` | Admin_Drive_Details | Admin |
| GET, POST | `/student/<student_id>` | Student_Home | Student (own ID) |
| GET, POST | `/student/<student_id>/comp_details/<company_id>` | Student_Apply | Student |
| GET, POST | `/student/<student_id>/drive_details/<drive_id>` | Student_Drive_Details | Student |
| GET, POST | `/student/<student_id>/student_drive/<drive_id>` | Drive_Details | Student |
| GET, POST | `/student/<student_id>/sapp_history` | Student_Application_History | Student |
| GET, POST | `/student/<student_id>/sapp_history_comp/<company_id>` | Student_Application_History_Company | Student |
| GET, POST | `/student/<student_id>/update` | Student_Update | Student |
| GET, POST | `/company/<company_id>` | Company_Home | Company (own ID) |
| GET, POST | `/company/<company_id>/drive_app/<drive_id>` | Drive_Applications | Company |
| GET, POST | `/company/<company_id>/create_drive` | Create_Drive | Company |
| GET, POST | `/company/<company_id>/update_drive/<drive_id>` | Update_Drive | Company |
| GET, POST | `/company/<company_id>/sapp_details/<application_id>` | Company_Student_Details | Company |
| GET, POST | `/company/<company_id>/update` | Company_Update | Company |

---

## Authentication and Session

- All passwords are hashed using Werkzeug's `generate_password_hash` before storing
- On login, `check_password_hash` is used to verify credentials
- Flask sessions store `role` (admin / student / company) and the user's ID
- Each route checks `session['role']` and the matching ID before serving any content
- Students and companies are restricted to their own IDs — a student cannot access another student's dashboard by changing the URL
- `session.clear()` is called on logout

---

## File Uploads

Student resumes and profile pictures, and company logos, are uploaded during registration and can be replaced via the profile update page.

- Resumes are stored as `<student_id>.pdf` in `static/resumes/`
- Profile pictures are stored as `<student_id>.<ext>` in `static/student-pfp/`
- Company logos are stored as `<company_id>.<ext>` in `static/comp-logo/`
- Accepted formats: PDF for resumes, JPG/JPEG/PNG for images
- The student ID is obtained by flushing the session before commit, so the file is named correctly before the record is fully written

---

## Error Handling

- A custom `404` error handler renders `error.html` and preserves the 404 status code
- Login errors (wrong password, blacklisted account, pending/rejected status) are passed back to the template as an `error` variable and shown inline
- Flash messages are used for validation errors during file upload and duplicate application attempts

---

## Setup and Running

1. Clone the repository
2. Install dependencies:
   ```
   pip install flask flask-sqlalchemy werkzeug
   ```
3. Run the app:
   ```
   python app.py
   ```
   On first run, the database is created and the admin account is seeded automatically.

4. Open `http://127.0.0.1:5000` in the browser

**Default Admin Credentials:**
- Email: `admin@gmail.com`
- Password: `admin123`

---

## Notes

- `db.session.flush()` is used during student and company registration to retrieve the auto-generated ID before the transaction is committed, so uploaded files can be named after the record ID
- `current_app` is used in `controllers.py` instead of importing `app` directly, to avoid a circular import between `app.py` and `controllers.py`
- `app.app_context().push()` is called in the app factory so the database can be accessed outside of a request context during initialization
- The `circular import` issue is handled by importing controllers after the app is created in `app.py`
