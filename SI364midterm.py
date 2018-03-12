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
    artist = db_session.query(User).filter_by(name=user_name).first()
    if user:
        return user
    else:
        user = User(name=user_name)
        db_session.add(user)
        db_session.commit()
        flash('User succesfully added')
        return user

def get_or_create_movie(db_session,movie_name):
    movie = db_session.query(Title).filter_by(title=movie_name).first()
    if movie:
        flash('Movie is already added')
        return movie
    else:
        baseurl = 'https://api.themoviedb.org/3/search/movie?api_key=4cf3715fe70bc590c1297a10298d4b6c&language=en-US&page=1&include_adult=false&'
        param_dict = {'query':movie_name}
        response = requests.get(baseurl, params = param_dict).json()
        result_name=response["results"]["title"]
        result_overview=response["results"]["overview"]
        result_releasedate=response["results"]["release_date"]
        if result_name:
            movie = Title(title=result_name)
            db_session.add(movie)
        else:
            flash('Movie does not exist')
            return 0
        if result_overview:
            overview = Overview(title=result_name,overview=result_overview)
            db_session.add(overview)
        if releasedate:
            releasedate = ReleaseDate(title=result_name,releasedate=result_releasedate)
            db_session.add(releasedate)
        db_session.commit()
        return movie


##################
##### MODELS #####
##################

class Name(db.Model):
    __tablename__ = "names"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64))
    
    def __repr__(self):
        return "{} (ID: {})".format(self.name, self.id)

class Title(db.Model):
    __tablename__ = "titles"
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(64))

    def __repr__(self):
        return "{} (Title: {})".format(self.id,self.title)

class Overview(db.Model):
    __tablename__ = "overviews"
    id = db.Column(db.Integer,primary_key=True)
    title =db.Column(db.String(64))
    overview = db.Column(db.String(64))
#
    def __repr__(self):
        return "{} (Overview: {})".format(self.id, self.overview)


class ReleaseDate(db.Model):
    __tablename__ = "releasedates"
    id = db.Column(db.Integer,primary_key=True)
    title =db.Column(db.String(64))
    releasedate = db.Column(db.String(64))
#
    def __repr__(self):
        return "{} (ReleaseDate: {})".format(self.id, self.releasedate)



###################
###### FORMS ######
###################
class NameForm(FlaskForm):
    name = StringField("Please enter your name.",validators=[Required()])
    submit = SubmitField()

class TitleForm(FlaskForm):
    name = StringField("Please enter a movie name.",validators=[Required()])
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
    form = NameForm() # User should be able to enter name after name and each one will be saved, even if it's a duplicate! Sends data with GET
    if form.validate_on_submit():
        name = form.name.data
        newname = Name(name)
        db.session.add(newname)
        db.session.commit()
        return redirect(url_for('all_names'))
    return render_template('base.html',form=form)

@app.route('/names')
def all_names():
    names = Name.query.all()
    return render_template('name_example.html',names=names)


@app.route('/addMovie')
def add_movies():
    form = TitleForm() # User should be able to enter name after name and each one will be saved, even if it's a duplicate! Sends data with GET
    if form.validate_on_submit():
        title = form.title.data
        newtitle = Title(title)
        db.session.add(newtitle)
        db.session.commit()
        return redirect(url_for('titles'))
    return render_template('addMovie.html',form=form)


@app.route('/titles')
def all_titles():
    titles = Title.query.all()
    return render_template('titles.html',titles=names)

@app.route('/overviews')
def all_overviews():
    names = Overview.query.all()
    return render_template('overviews.html',overviews=names)


@app.route('/releasedates')
def all_releasedates():
    names = ReleaseDate.query.all()
    return render_template('releasedates.html',releasedates=names)


## Code to run the application...

if __name__ == '__main__':
    db.create_all()
    app.run(use_reloader=True,debug=True)
# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!
