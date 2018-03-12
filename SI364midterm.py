###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import os
import requests
import json
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError # Note that you may need to import more here! Check out examples that do what you want to figure out what.
from wtforms.validators import Required, Length # Here, too
from flask_sqlalchemy import SQLAlchemy

## App setup code
app = Flask(__name__)
app.debug = True
app.use_reloader = True

## All app.config values
app.config['SECRET_KEY'] = 'si364randomsecretkeyhardtoguess'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/hongjisu364midterm"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

## Statements for db setup (and manager setup if using Manager)
db = SQLAlchemy(app)


######################################
######## HELPER FXNS (If any) ########
######################################

def get_or_create_user(db_session,user_name):
    tmp_user = db_session.query(User).filter_by(user=user_name).first()
    if tmp_user:
        flash('User already exists')
        return tmp_user
    else:
        tmp_user = User(user=user_name)
        db_session.add(tmp_user)
        db_session.commit()
        flash('User succesfully added')
        return tmp_user

def get_or_create_movie(db_session,movie_name):
    baseurl = 'https://api.themoviedb.org/3/search/movie?api_key=4cf3715fe70bc590c1297a10298d4b6c&language=en-US&page=1&include_adult=false&'
    param_dict = {'query':movie_name}
    response = requests.get(baseurl, params = param_dict).json()
    if len(response["results"]):
        result_name=response["results"][0]["original_title"]
        result_overview=response["results"][0]["overview"]
        result_releasedate=response["results"][0]["release_date"]
        movie = db_session.query(Title).filter_by(title=result_name).first()
        if movie:
            flash('Movie is already added')
            return movie
        if result_name:
            movie = Title(title=result_name)
            db_session.add(movie)
        if result_overview:
            overview = Overview(title=result_name,overview=result_overview)
            db_session.add(overview)
        if result_releasedate:
            releasedate = ReleaseDate(title=result_name,releasedate=result_releasedate)
            db_session.add(releasedate)
        db_session.commit()
        flash('Movie is added succesfully')
    else:
        flash('Movie does not exist')
    return movie


##################
##### MODELS #####
##################

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer,primary_key=True)
    user = db.Column(db.String(64), unique=True)
    
    def __repr__(self):
        return "{} {}".format(self.id, self.user)

class Title(db.Model):
    __tablename__ = "titles"
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(64))

    def __repr__(self):
        return "{} Title: {}".format(self.id,self.title)

class Overview(db.Model):
    __tablename__ = "overviews"
    id = db.Column(db.Integer,primary_key=True)
    title =db.Column(db.String(64))
    overview = db.Column(db.String(512))
#
    def __repr__(self):
        return "Title:{} Overview:{}".format(self.title, self.overview)


class ReleaseDate(db.Model):
    __tablename__ = "releasedates"
    id = db.Column(db.Integer,primary_key=True)
    title =db.Column(db.String(64))
    releasedate = db.Column(db.String(64))
#
    def __repr__(self):
        return "Title:{} ReleaseDate: {}".format(self.title, self.releasedate)



###################
###### FORMS ######
###################
class UserForm(FlaskForm):
    user = StringField("Please enter your username.",validators=[Required()])
    submit = SubmitField()

class TitleForm(FlaskForm):
    title = StringField("Please enter a movie name.",validators=[Required(),Length(max=64, message="Cannot be longer than 64 characters")]])
    submit = SubmitField()



#######################
###### VIEW FXNS ######
#######################


## Error handling routes
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

## Main route

@app.route('/')
def home():
    return render_template('base.html')



@app.route('/addUser', methods=['GET', 'POST'])
def add_users():
    form = UserForm() # User should be able to enter name after name and each one will be saved, even if it's a duplicate! Sends data with GET
    if form.validate_on_submit():
        user_in = form.user.data
        get_or_create_user(db.session,user_in)
        return redirect(url_for('all_users'))
    return render_template('add_users.html',form=form)

@app.route('/addMovie', methods=['GET', 'POST'])
def add_movies():
    form = TitleForm() # User should be able to enter name after name and each one will be saved, even if it's a duplicate! Sends data with GET
    if form.validate_on_submit():
        title_in = form.title.data
        get_or_create_movie(db.session,title_in)
        return redirect(url_for('all_titles'))
    return render_template('add_movies.html',form=form)

@app.route('/users')
def all_users():
    users_in = User.query.all()
    return render_template('users.html',users=users_in)

@app.route('/titles')
def all_titles():
    titles_in = Title.query.all()
    return render_template('titles.html',titles=titles_in)

@app.route('/overviews')
def all_overviews():
    overviews_in = Overview.query.all()
    return render_template('overviews.html',overviews=overviews_in)

@app.route('/releasedates')
def all_releasedates():
    releasedates_in = ReleaseDate.query.all()
    return render_template('releasedates.html',releasedates=releasedates_in)


## Code to run the application...

if __name__ == '__main__':
    db.create_all()
    app.run(use_reloader=True,debug=True)
# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!
