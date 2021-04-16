import os

import flask
import json
from flask import Flask, render_template,flash, request, redirect, redirect, url_for
from model import db
from flask import jsonify
from flask_cors import CORS
from flask_ngrok import run_with_ngrok
from functools import wraps
from datetime import datetime

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_jwt_extended import verify_jwt_in_request
import sqlalchemy as db
from sqlalchemy import Table, MetaData, Column, Integer,VARCHAR
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import SelectField
UPLOAD_FOLDER = 'D:/photo uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
CORS(app)
run_with_ngrok(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:sebastar13@127.0.0.1:3306/team_project'
app.config['SECRET_KEY'] = 'secret'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


Base = declarative_base()
engine = db.create_engine('mysql+mysqlconnector://root:sebastar13@127.0.0.1:3306/team_project')
connection = engine.connect()
metadata = MetaData()
session = sessionmaker()
session.configure(bind=engine)
my_session = session()

user = Table('user', metadata,
             Column('id', Integer, primary_key=True),
             Column('email', VARCHAR(255)),
             Column('password', VARCHAR(255)),
             Column('role', Integer),
             Column('student_id', Integer),
             Column('teacher_id', Integer)
             )

class User(Base):
  __tablename__ = 'user'

  Id = Column(db.Integer, primary_key=True)
  email =db.Column(db.VARCHAR(255))
  password = db.Column(db.VARCHAR(255))
  role = db.Column(db.Integer)
  student_id =db.Column(db.Integer)
  teacher_id = db.Column(db.Integer)

userid_table =my_session.query(User.Id).all()

def teacher_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims["is_teacher"]:
                return fn(*args, **kwargs)
            else:
                return jsonify(msg="teachers only!"), 403

        return decorator

    return wrapper

db = SQLAlchemy(app)

class Module(db.Model):
    __tablename__ = 'module'
    Id = db.Column(db.VARCHAR(10), primary_key=True)
    Name = db.Column(db.VARCHAR(255))
    start_date = db.Column(db.DATETIME)
    end_date = db.Column(db.DATETIME)
    teacher_id = db.Column(db.Integer)

class Course(db.Model):
    __tablename__ ='course'
    Id = db.Column(db.VARCHAR(10), primary_key=True)
    Name = db.Column(db.VARCHAR(255))
    Modules = db.Column(db.VARCHAR(255))
    start_date = db.Column(db.DATETIME)
    end_date = db.Column(db.DATETIME)

class Course_Module(db.Model):
    __tablename__ ='course'
    course_id = db.Column(db.VARCHAR(10), primary_key=True)
    module_id = db.Column(db.VARCHAR(10), primary_key=True)

class Teacher(db.Model):
    __tablename__ ='teacher'
    Id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(255))
class Room(db.Model):
    __tablename__ = 'room'
    id =db.Column(db.Integer, primary_key=True, default=0)
    name = db.Column(db.VARCHAR(255))
    date = db.Column(db.DATETIME)
    def __init__(self,id,name,date):
        self.id =id
        self.name = name
        self.date = date

class Room_User(db.Model):
    __tablename__ = 'room'
    room_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    def __init__(self, room_id, user_id):
        self.room_id = room_id
        self.user_id = user_id

class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True, default=0)
    room_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    text = db.Column(db.VARCHAR(255))
    date = db.Column(db.DATETIME)
    def __init__(self, id, room_id, user_id,text,date):
        self.id = id
        self.room_id = room_id
        self.user_id = user_id
        self.text = text
        self.date = date

class User(db.Model):
    __tablename__ = 'user'
    Id = db.Column(db.Integer, primary_key=True, default=0)
    email = db.Column(db.VARCHAR(255))
    password = db.Column(db.VARCHAR(255))
    role = db.Column(db.Integer)
    student_id = db.Column(db.Integer)
    teacher_id = db.Column(db.Integer, default=None)
    def __init__(self,id,email,password,role,student_id,teacher_id):
        self.id = id
        self.email = email
        self.password = password
        self.role = role
        self.student_id = student_id
        self.teacher_id = teacher_id


class Students(db.Model):
        __tablename__='students'
        Id = db.Column(db.Integer, primary_key=True, default=0)
        course_id = db.Column(db.VARCHAR(10), default='cor001')
        full_name = db.Column(db.VARCHAR(35))
        home_address = db.Column(db.VARCHAR(40))
        term_address = db.Column(db.VARCHAR(40))
        def __init__ (self,id,course_id,full_name,home_address,term_address):
            self.id = id
            self.course_id = course_id
            self.full_name = full_name
            self.home_address = home_address
            self.term_address = term_address

class Form(FlaskForm):
     courses = SelectField('course', choices=[])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/register', methods=["POST"])
def register():
        request_data = request.get_json(force=True)
        course_id = request_data['course_id']
        print(request_data['home_address'])
        student_id = len(Students.query.all())
        new_student = Students(student_id, course_id, request_data['full_name'], request_data['home_address'], request_data['term_address'])
        db.session.add(new_student)
        db.session.commit()
        new_user = User(5, request_data['email'], request_data['password'], 2, len(Students.query.all()), None)
        db.session.add(new_user)
        db.session.commit()
        return {"message": "Register successfully"}

@app.route('/upload_files', methods=["GET","POST"])
def upload_files():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        files = flask.request.files.getlist("file")
    # if user does not select file, browser also
    # submit an empty part without filename
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return render_template("registration_success.html")
    return render_template("upload_file.html")

@app.route('/courses', methods=["GET","POST"])
def courses():
    courses_list = []
    for courses in Course.query.all():
        courses_list.append({"id": courses.Id, "course": courses.Name})
    return json.dumps(courses_list)

@app.route("/login", methods=["GET","POST"])
def login():
      request_data = request.get_json(force=True)
      email = request_data['email']
      password = request_data['password']
      for row in my_session.query(User.password, User.role).filter(User.email==email):
          user_password= row.password
          user_role =row.role
      if password != user_password:
       return jsonify({"msg": "Wrong email or password"}), 401

      if user_role == 1:
          access_token = create_access_token(identity=email, additional_claims={"is_teacher": True})
      else:
          access_token = create_access_token(identity=email)
      return jsonify(access_token=access_token)

@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    student_id = User.query(User.student_id).filter(email =current_user).first()
    course_id = Students.query(Students.course_id).filter(student_id=student_id).first()
    module_id_list = []
    for row in Course_Module.query.filter_by(course_id =course_id).all():
        module_id_list.append(row.module_id)
    module_list = []
    for module_id in module_id_list:
        for row in Module.query.filter_by(id=module_id).all():
            module_list.append({"module_id": row.Id, "name": row.Name, "start_date": row.start_date, "end_date": row.end_date})
    return json.dumps(module_list)

@app.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    student_id = User.query(User.student_id_id).filter(email=current_user).first()
    student = []
    for row in Students.query.filter_by(id=student_id).all():
        student.append({"id": row.Id, "full_name": row.full_name, "home_address": row.home_address, "term_address": row.term_address})
    return json.dump(student, current_user)

@app.route("/create_module_room", methods=["GET"])
@jwt_required()
def create_module_room():
    request_data = request.get_json(force=True)
    room = Room(len(Room.query.all()), request_data['module_name'], datetime.now())
    db.session.add(room)
    db.session.commit()
    return json.dump({"room_id": room.Id, "name": room.name, "room_date": room.date})

@app.route("/create_private_room_student", methods=["GET"])
@jwt_required()
def create_private_room_student():
    request_data = request.get_json(force=True)
    student_name = request_data['full_name']
    room = Room(0, student_name, datetime.now())
    db.session.add(room)
    db.session.commit()
    return json.dump({"room_id": room.Id, "name": room.name, "room_date": room.date})

@app.route("/create_private_room_teacher", methods=["GET"])
@jwt_required()
def create_private_room_teacher():
    request_data = request.get_json(force=True)
    student_name = request_data['name']
    room = Room(0, student_name, datetime.now())
    db.session.add(room)
    db.session.commit()
    return json.dump({"room_id": room.Id, "name": room.name, "room_date": room.date})

@app.route("/display_message", methods=["GET"])

@app.route("/display_students", methods=["GET"])
@teacher_required()
def display_students():
    current_user = get_jwt_identity()
    teacher_id = User.query(User.teacher_id).filter(email=current_user).first()
    module_list = []
    for modules in Module.query.filter_by(teacher_id =teacher_id).all():
        module_list.append(modules.id)
    course_ids =[]
    for module in module_list:
        for course_module in Course_Module.query.filter_by(module_id = module).all():
            course_ids.append(course_module.course_id)
    student_list = []
    for course_id in course_ids:
        for row in Students.query.filter_by(course_id =course_id).all():
            student_list.append({"id": row.Id, "full_name": row.full_name, "home_address": row.home_address, "term_address": row.term_address})

    return json.dumps(student_list)

@app.route("/display_teachers", methods=["GET"])
@jwt_required()
def display_teachers():
    current_user = get_jwt_identity()
    student_id = User.query(User.student_id).filter(email=current_user).first()
    course_id = Students.query(Students.course_id).filter(Id=student_id).first()
    module_id_list= []
    for course_module in Course_Module.query(Course_Module.module_id).filter(course_id=course_id):
        module_id_list.append(course_module.course_id)
    teacher_id_list = []
    for modules_id in module_id_list:
        for teacher_id in Module.query(Module.teacher_id).filter(Id=modules_id):
            teacher_id_list.append(teacher_id)
    teacher_list = []
    for teacher_id in teacher_id_list:
        for row in Teacher.query.filter_by(Id=teacher_id).all():
            teacher_list.append({"id": row.Id, "name": row.name})

    return json.dumps(teacher_list)

if __name__ == "__main__":
    app.run()