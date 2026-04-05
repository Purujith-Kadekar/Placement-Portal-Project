from flask import Flask
from application.models import Admin
from werkzeug.security import generate_password_hash
app = None

from application.database import db
def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement.sqlite3'
    app.secret_key = "anyrandomstring123"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    app.app_context().push() # for the database connection to work without any error, to access things outside the request of the Flask
    return app

app = create_app()
from application.controllers import * #as controllers is inside the applications folder

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Admin creation
        admin_email = "admin@gmail.com"
        admin_password = "admin123"
        hashed_password = generate_password_hash(admin_password)
        admin = Admin.query.filter_by(email=admin_email).first()
        if admin: #update
            admin.email = admin_email 
            admin.password = hashed_password  
        else: #or create 
            admin = Admin(email=admin_email, password=hashed_password)
            db.session.add(admin)
        db.session.commit()
    app.run()