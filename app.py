from flask import Flask,render_template,url_for,redirect,request,flash
from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField,IntegerField
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_required,current_user
from flask_login import LoginManager
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import date
from os import path



# Create INSTANCE IMPORTANT
app = Flask(__name__,template_folder='template',static_folder='static')
#add database
app.config['SQLALCHEMY_DATABASE_URI'] = ' postgres://cxmwucrantvgiz:8a85cc37b93c58e73cfa6622e2923bc9f84e50627293f45276728275cfa89f75@ec2-44-206-197-71.compute-1.amazonaws.com:5432/d7nbiqdijeilgf'
#secret key required  on flask forms
app.config['SECRET_KEY']='webdev'

#this is how to initialize the Dtabase
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




#CREATE GRADES DB--------------
class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Student_ID_Number = db.Column(db.String(8), nullable=False)
    subject = db.Column(db.String(200),nullable=False)
    instructor = db.Column(db.String(200), nullable=False)
    units = db.Column(db.String(200), nullable=False)
    grade = db.Column(db.String(200),nullable=False)
    date_added = db.Column(db.DateTime,default=datetime.utcnow)
    grade_id= db.Column(db.Integer, db.ForeignKey('user.id'))




#CREATE 1-4SECTIONS DB--------------
class Cor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Section = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(200),nullable=False)
    instructor = db.Column(db.String(200), nullable=False)
    units = db.Column(db.String(200), nullable=False)
    time = db.Column(db.String(200),nullable=False)
    location = db.Column(db.String(200), nullable=True)
    date_added = db.Column(db.DateTime,default=datetime.utcnow)
    fa_id= db.Column(db.Integer, db.ForeignKey('user.id'))



#CREATE REQUEST DB--------------
class Req(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cogcoe = db.Column(db.String(200),nullable=False)
    sem = db.Column(db.String(200), nullable=False)
    payment = db.Column(db.String(200),nullable=False)
    proof = db.Column(db.String(200), nullable=False)
    date_added = db.Column(db.DateTime,default=datetime.utcnow)
    re_id= db.Column(db.Integer, db.ForeignKey('user.id'))


#CREATE ANNOUNCEMENT DB--------------------------
class Ann(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250),nullable=False)
    content = db.Column(db.Text)
    slug = db.Column(db.String(200),nullable=False)
    date_added = db.Column(db.DateTime,default=datetime.utcnow)
    Ann_id= db.Column(db.Integer, db.ForeignKey('user.id'))

#create a model for DataBase------------------------
class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    ID_NUMBER = db.Column(db.String(8),nullable=False,unique=True )
    name = db.Column(db.String(200),nullable=False)
    year_section = db.Column(db.String(200),nullable=False)
    email = db.Column(db.String(200),nullable=False,unique=True)
    address = db.Column(db.String(200),nullable=False)
    phone_number = db.Column(db.Integer,nullable=False)
    gender = db.Column(db.String(200),nullable=False)
    password_hash = db.Column(db.String(200),nullable=False)
    date_added = db.Column(db.DateTime,default=datetime.utcnow)
    announcement = db.relationship('Ann',backref='Anner')
    request = db.relationship('Req', backref='re')
    Fa = db.relationship('Cor', backref='fa')
    grade = db.relationship('Grade', backref = 'gr')


    @property
    def password(self):
        raise AttributeError("password is not readable")

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def __repr__(self):
        return "<Name %r>" % self.name



#Create Forms
class UserForm(FlaskForm):
    idnumber = StringField("ID Number:", validators=[DataRequired()])
    name = StringField("Name:", validators=[DataRequired()])
    year_section = StringField("Year/Section:",validators=[DataRequired()])
    email = StringField("Email:", validators=[DataRequired()])
    address = StringField("Address:", validators=[DataRequired()])
    phone_number = StringField("Phone Number:", validators=[DataRequired()])
    gender = StringField("Gender:",validators=[DataRequired()])
    password_hash = PasswordField('Password:', validators=[DataRequired(),EqualTo('password_hash2', message='Passwords Must Match!')])
    password_hash2 = PasswordField('Confirm Password:', validators=[DataRequired()])
    submit = SubmitField("Submit")

@app.route('/sign-up', methods=['POST','GET'])
def signup():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        userid = User.query.filter_by(ID_NUMBER=form.idnumber.data).first()
        if user:
            flash('Email already exist')
            return redirect(url_for('signup'))
        if userid:
            flash('Idnumber already exist')
            return redirect(url_for('signup'))
        else:
            user = User(ID_NUMBER=form.idnumber.data, name=form.name.data, year_section=form.year_section.data,
                    email=form.email.data, address=form.address.data, phone_number=form.phone_number.data,
                    gender=form.gender.data, password_hash=generate_password_hash(form.password_hash.data, method="sha256"))
            db.session.add(user)
            db.session.commit()
            form.idnumber.data = ''
            form.name.data = ''
            form.year_section.data = ''
            form.address.data = ''
            form.phone_number.data = ''
            form.gender.data = ''
            form.password_hash.data = ''
            flash("Registered Successfully")
            return redirect(url_for('login'))
    return render_template('signup.html', form=form, name=name)

#Create Forms
class LogForm(FlaskForm):
    email = StringField("Email:", validators=[DataRequired()])
    password_hash = PasswordField('Password:', validators=[DataRequired()])
    submit = SubmitField("Submit")

@app.route('/', methods=['POST','GET'])
def login():
    form = LogForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data,).first()
        if user:
            if check_password_hash(user.password_hash, form.password_hash.data):
                login_user(user)
                flash("logged In")
                return redirect(url_for('homedash'))
            else:
                flash("Error Wrong password...")

    return render_template('Login.html',form=form, )


#Create Forms
class UpForm(FlaskForm):
    name = StringField("Name:")
    year_section = StringField("Year/Section:")
    email = StringField("Email:")
    address = StringField("Address:")
    phone_number = StringField("Phone Number:")
    gender = StringField("Gender:")
    submit = SubmitField("Submit")

@app.route('/userup',methods=['POST','GET'])
def userup():
    form = UpForm()
    id = current_user.id
    update = User.query.get_or_404(id)
    if form.validate_on_submit():
        update.name = form.name.data
        update.year_section = form.year_section.data
        update.email = form.email.data
        update.address = form.address.data
        update.phone_number = form.phone_number.data
        update.gender = form.gender.data
        try:
            db.session.commit()
            flash('Succesfull update')
            return redirect(url_for('account', form=form, update=update, id=id))
        except:
            flash('Error!')
            return render_template('userupdate.html', form=form, update=update,id=id)


    return render_template('userupdate.html', form=form, update=update,id=id)






@app.route('/logout',methods=['POST','GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

#create ROUTES
@app.route('/homedash')
@login_required
def homedash():
    return render_template('homedash.html',user=current_user)


@app.route('/account', methods=['POST','GET'])
@login_required
def account():
        return render_template('accountdash.html',user = current_user)


@app.route('/announcement', methods=['POST','GET'])
@login_required
def announcement():
    posts = Ann.query.order_by(Ann.date_added)
    return render_template('announcementdash.html',posts=posts)


#CREATE COURSE FORM
class SubjectForm(FlaskForm):
    section = StringField("SECTION:1A,2A,3A,4A", validators=[DataRequired()])
    submit = SubmitField("VIEW COURSES")

@app.route('/courses', methods=['POST','GET'])
@login_required
def courses():
    form= SubjectForm()
    look = Cor.query
    return render_template('courses.html', user=current_user,form=form,
                           look=look)

@app.route('/courses1', methods=['POST','GET'])
@login_required
def courses1():
    form = SubjectForm()
    look = Cor.query
    if form.section.data == current_user.year_section:
        if form.validate_on_submit():
            lookfor = form.section.data
            look = look.filter(Cor.Section.like('%' + lookfor + '%'))
            look = look.order_by(Cor.Section).all()
    else:
        flash('sorry you cant acces that')
        return redirect(url_for('courses'))

    return render_template('courses1.html', user=current_user, form=form,
                           look=look)

#CREATE COURSE FORM
class GForm(FlaskForm):
    Id_Number = StringField("")
    submit = SubmitField("VIEW GRADES")

@app.route('/grades', methods=['POST','GET'])
@login_required
def grades():
    form = GForm()
    look = Cor.query
    return render_template('grade.html', user=current_user, form=form,
                           look=look)

@app.route('/grades1', methods =['POST','GET'])
@login_required
def grades1():
    form = GForm()
    look = Grade.query
    if form.Id_Number.data == current_user.ID_NUMBER:
        if form.validate_on_submit():
            lookfor = form.Id_Number.data
            look = look.filter(Grade.Student_ID_Number.like('%' + lookfor + '%'))
            look = look.order_by(Grade.Student_ID_Number).all()

    else:
        flash('sorry you cant acces that')
        return redirect(url_for('grades'))


    return render_template('grade1.html', user=current_user, form=form,
                           look=look)


#Creat FORMS
class ReqForm(FlaskForm):
    cogcoe = StringField("Certificate: Certificate Of Grades/Certificate Of Enrollment ", validators=[DataRequired()])
    sem = StringField("Semester:", validators=[DataRequired()])
    payment = StringField("Mode Of Payment:", validators=[DataRequired()])
    reference = StringField("Enter reference number:", validators=[DataRequired()])
    submit = SubmitField("Send Request")


@app.route('/request', methods=['POST','GET'])
@login_required
def request():
    form = ReqForm()
    if form.validate_on_submit():
        re = current_user.id
        req = Req(cogcoe=form.cogcoe.data,sem=form.sem.data,payment=form.payment.data,proof=form.reference.data, re_id=re)
        form.cogcoe.data = ''
        form.sem.data = ''
        form.payment.data = ''
        form.reference.data = ''
        db.session.add(req)
        db.session.commit()
        flash("Request SUCCESSFULL!!")
        return redirect(url_for('request', form=form))
    return render_template('request.html', form=form)








####ERROR HANDLER-----------------------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

#error 500 Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'),500





#Admin AREa--------------------------------------------------------------------

##CREATE FORMS----
class AnnForm(FlaskForm):
    title = StringField("TITLE:", validators=[DataRequired()])
    content = CKEditorField("CONTENT:", validators=[DataRequired()])
    slug = StringField("TYPE:",validators=[DataRequired()])
    submit = SubmitField("Add Announcement")



@app.route('/Admin', methods=['POST','GET'])
@login_required
def admin():
    id = current_user.id
    if id==1:
        return render_template('ADMIN.html')
    else:
        flash('RESTRICTED ADMIN ONLY')
        return redirect(url_for('homedash'))


@app.route('/AdminAN', methods=['POST','GET'])
@login_required
def adminan():
    form = AnnForm()
    if form.validate_on_submit():
        Anner = current_user.id
        post = Ann(title=form.title.data, content=form.content.data,slug=form.slug.data,Ann_id =Anner)
        form.title.data = ''
        form.content.data = ''
        form.slug.data = ''

        db.session.add(post)
        db.session.commit()
        flash("POSTED SUCCESSFULLY!!")
        return redirect(url_for('adminan',form=form))
    return render_template('AdminANN.html',form=form)

@app.route('/deli',methods=['POST','GET'])
def deli():
    posts = Ann.query.order_by(Ann.date_added)
    return render_template('AdminDeletepost.html', posts=posts)

@app.route('/delete/<int:id>',methods = ['POST','GET'])
def delete(id):
    post_to_delete = Ann.query.get_or_404(id)
    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash("Deleted Successfully")
        return redirect(url_for('deli', user=current_user, post_to_delete=post_to_delete))

    except:
        flash('Error')
        return render_template('announcementdash.html', user=current_user, post_to_delete=post_to_delete)


#Create FORMS
class CourseForm(FlaskForm):
    section = StringField("SECTION:", validators=[DataRequired()])
    subject = StringField("SUBJECT:", validators=[DataRequired()])
    instructor = StringField("INSTRUCTOR:",validators=[DataRequired()])
    units = StringField("UNITS:", validators=[DataRequired()])
    time = StringField("TIME:", validators=[DataRequired()])
    location = StringField("LOCATION:", validators=[DataRequired()])
    submit = SubmitField("Add")

@app.route('/AdminCOUR', methods=['POST','GET'])
@login_required
def admincour():
    form = CourseForm()
    if form.validate_on_submit():
        fa = current_user.id
        post = Cor(Section=form.section.data, subject=form.subject.data, instructor=form.instructor.data,
                   units=form.units.data, time=form.time.data, location=form.location.data, fa_id=fa)
        form.section.data = ''
        form.subject.data = ''
        form.instructor.data = ''
        form.units.data = ''
        form.time.data = ''
        form.location.data = ''

        db.session.add(post)
        db.session.commit()
        flash("Created SUCCESSFULLY!!")
        return redirect(url_for('admincour', form=form))
    return render_template('AdminCOUR.html',form = form)

@app.route('/AdminCOUR1', methods=['POST','GET'])
@login_required
def admincour1():
    course =Cor.query.order_by(Cor.date_added)
    return render_template('AdminCOUR1.html',course=course)

@app.route('/deletec/<int:id>',methods = ['POST','GET'])
def deletec(id):
    post_to_delete = Cor.query.get_or_404(id)
    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash("Deleted Successfully")
        return redirect(url_for('admincour', post_to_delete=post_to_delete))

    except:
        flash('Error')
        return render_template('AdminCOUR1.html', post_to_delete=post_to_delete)

#Create FORMS
class upCourseForm(FlaskForm):
    section = StringField("SECTION:" )
    subject = StringField("SUBJECT:")
    instructor = StringField("INSTRUCTOR:")
    units = StringField("UNITS:")
    time = StringField("TIME:")
    location = StringField("LOCATION:")
    submit = SubmitField("UPDATE")

@app.route('/upcourse/<int:id>',methods=['POST','GET'])
def upcourse(id):
    form = upCourseForm()
    update = Cor.query.get_or_404(id)
    if form.validate_on_submit():
        update.Section = form.section.data
        update.subject = form.subject.data
        update.instructor = form.instructor.data
        update.units = form.units.data
        update.time = form.time.data
        update.location = form.location.data
        try:
            db.session.commit()
            flash('Succesfull update')
            return redirect(url_for('admincour', form=form, update=update, id=id))
        except:
            flash('Error!')
            return render_template('admincour', form=form, update=update,id=id)
    else:
        return render_template('courseupdate.html', form=form, update=update, id=id)



#Create FORMS
class GraForm(FlaskForm):
    studentidnumber = StringField("Student Id Number:", validators=[DataRequired()])
    subject = StringField("Subject:", validators=[DataRequired()])
    instructor = StringField("Instructor:",validators=[DataRequired()])
    units = StringField("Units:", validators=[DataRequired()])
    grade = StringField("Grade:", validators=[DataRequired()])
    submit = SubmitField("Add Grade")


@app.route('/AdminGRADE', methods=['POST','GET'])
@login_required
def admingrade():
    form = GraForm()
    if form.validate_on_submit():
        ga = current_user.id
        grade = Grade(Student_ID_Number=form.studentidnumber.data, subject=form.subject.data, instructor=form.instructor.data,
                   units=form.units.data, grade=form.grade.data, grade_id=ga)
        form.subject.data = ''
        form.instructor.data = ''
        form.units.data = ''
        form.grade.data = ''

        db.session.add(grade)
        db.session.commit()
        flash("Created SUCCESSFULLY!!")
        return redirect(url_for('admingrade', form=form))
    return render_template('AdminGRADE.html',form=form)




@app.route('/AdminREQ', methods=['POST','GET'])
@login_required
def adminreq():
    reqs = Req.query.order_by(Req.date_added)
    return render_template('AdminREQ.html', user=current_user, reqs=reqs)


@app.route('/deletes/<int:id>',methods = ['POST','GET'])
def deletes(id):
    req_to_delete = Req.query.get_or_404(id)
    try:
        db.session.delete(req_to_delete)
        db.session.commit()
        flash("Deleted Successfully")
        return redirect(url_for('adminreq', user=current_user, req_to_delete=req_to_delete))

    except:
        flash('Error')
        return redirect(url_for('adminreq', user=current_user, req_to_delete=req_to_delete))


if __name__ == '__main__':
    app.run(debug=True)
