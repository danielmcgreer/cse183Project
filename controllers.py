"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""
import uuid

from py4web import action, request, abort, redirect, URL, Field
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email
from py4web.utils.form import Form, FormStyleBulma
from .common import Field
from pydal.validators import *
from .models import get_user_email

url_signer = URLSigner(session)
#TODO make signing everywhere and make sure you can only mess with your own reviews
#TODO you can only write reviews for courses that exist, if course does not exist 
      #then they do a special form that creates the course and the review
@action('index')
@action.uses(db, auth, 'index.html')
def index():
    #Grabs reviews and associated courses
    reviews = db(db.reviews.course_id == db.courses.id).select()
    return dict(reviews=reviews, url_signer=url_signer)
    
    
@action('add_review', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'add_review.html')
def add_review():
    #Create a form for all fields for now
    form = Form([Field('department', requires=IS_NOT_EMPTY()),
                Field('class_number',  'integer', requires=IS_NOT_EMPTY()),
                Field('class_name', requires=IS_NOT_EMPTY()),
                Field('teacher',),
                Field('rating', 'integer',IS_INT_IN_RANGE(0, 5)),
                Field('review', 'text')],
                csrf_session=session, formstyle=FormStyleBulma)
    
    # if form is accepted
    if form.accepted:
        # Check if there is a course that already exists with the entered info
        if db((db.courses.department == form.vars["department"]) &
              (db.courses.class_number == form.vars["class_number"]) &
              (db.courses.class_name == form.vars["class_name"])).select().first() == None:
              # If there is no course with the inputted info then create the course by inserting its info into the courses table
              db.courses.insert(department = form.vars["department"],
                                class_number = form.vars["class_number"],
                                class_name = form.vars["class_name"])
        # Grab the course that matches the filled fileds (its Id is needed)
        course = db((db.courses.department == form.vars["department"]) &
              (db.courses.class_number == form.vars["class_number"]) &
              (db.courses.class_name == form.vars["class_name"])).select().first()
        # insert the review into the reviews table
        db.reviews.insert(teacher = form.vars["teacher"],
                         rating = form.vars["rating"],
                         review = form.vars["review"], 
                         course_id = course.id)
        redirect(URL('index'))
    return dict(form=form)
    
@action('edit_review/<review_id:int>', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'edit_review.html')
def edit(review_id=None):
    assert review_id is not None

    p = db.reviews[review_id]
    if p is None:
        redirect(URL('index'))
    if p.created_by == auth.current_user.get('email'):
        form = Form(db.reviews, record=p, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL('index'))
    return dict(form=form)
    
@action('delete_review/<review_id:int>')
@action.uses(db, session, auth.user)
def delete(review_id=None):
    assert review_id is not None
    db(db.reviews.id == review_id).delete()
    redirect(URL('users_reviews'))

@action('search_course', method=["GET", "POST"])
@action.uses(db, auth, 'search_course.html')
def search_course():
    form = Form([Field('department', requires=IS_NOT_EMPTY()),Field('class_number'),],
                csrf_session=session, formstyle=FormStyleBulma
                )
    #TODO if it is not accepted
    if form.accepted:
        redirect(URL('display_course',form.vars["department"] ,form.vars["class_number"] ))
        
    return dict(form=form)
    
@action('display_course/<major_id>/<course_num:int>')
@action.uses(db, auth, 'display_course.html')
def display_course(major_id=None, course_num=None):
#TODO if args eq none then do something
    if(course_num==None):
        course_num=0
    perfectMatches = db((db.courses.department == major_id) & 
                        (db.courses.class_number == course_num)).select()
    closeMatches1 = db((db.courses.department == major_id) & 
                        (db.courses.class_number != course_num)).select() 
    closeMatches2 = db((db.courses.department != major_id) & 
                        (db.courses.class_number == course_num)).select()
                        
    allMatches = perfectMatches+closeMatches1+closeMatches2
    # print(allMatches)
    return dict(allMatches=allMatches,  url_signer=url_signer) 

# show_reviews page with vue connecting controllers ####################################################
def get_name(email):
    user = db(db.auth_user.email == email).select().first()
    name = user.first_name + " " + user.last_name if user is not None else "Unknown"
    return name

def get_review_author(review_id):
    review = db.review[review_id]
    name = get_name(reviews.created_by)
    return name

def get_thumbs(review_id):
    thumbs = db(db.thumb.review_id == review_id).select().as_list()
    for thumb in thumbs:
        thumb["name"] = get_name(thumb["created_by"])
    return thumbs
  
def review_format(review_id):
    review = db.reviews[review_id].as_dict()
    review["author"] = get_review_author(review_id) 
    review["thumbs"] = get_thumbs(review_id)
    return review

@action('show_reviews/<major_id>/<course_num:int>/<course_id>')
@action.uses(db, auth.user, db, session, url_signer, 'show_reviews.html')
def show_reviews(major_id=None, course_num=None, course_id=None):
#TODO if args eq none then do something
    rows = db((db.courses.department == major_id) & 
            (db.courses.class_number == course_num) & 
            (db.courses.id == db.reviews.course_id)).select()
            
    for row in rows:
        department = row.courses.department
        class_number = row.courses.class_number
        class_name = row.courses.class_name
            
    return dict(
        rows=rows, 
        department=department, 
        class_number=class_number, 
        class_name=class_name, 
        url_signer=url_signer,
        get_reviews_url = URL('get_reviews', signer=url_signer),
        add_review_url = URL('add_review_text', signer=url_signer),
        delete_review_url = URL('delete_review', signer=url_signer),
        thumb_review_url = URL('thumb_review', signer=url_signer),
        user_email = get_user_email(),
        username = auth.current_user.get('first_name') + " " + auth.current_user.get("last_name")
    ) 

@action('get_reviews')
@action.uses(url_signer.verify(), auth.user, db) 
def get_reviews(major_id=None, course_id=None, review_id=None):
    reviews = db().select(db.reviews.course_id == course_id, orderby=~db.review.created_date).as_list() 
    print(reviews)
    formatted_reviews = []
    for review in reviews:
        formatted_reviews.append(review_format(review["id"]))
    return dict(reviews=formatted_reviews) 

@action('add_review_text', method=["GET", "POST"])
@action.uses(url_signer.verify(), auth.user, db)
def add_review_text():
    review_text = request.json.get('review') 
    new_id = db.reviews.insert(review_text=review_text) 
    review = db.reviews[new_id]
    review = review_format(reviews.id)
    return dict(review=review) 

@action('delete_review', method=["GET", "POST"])
@action.uses(url_signer.verify(), auth.user, db)
def delete_review():
    review_id = request.json.get('review_id') 
    if review_id is not None:
        db(db.reviews.id == review_id).delete()
    return dict()

@action('thumb_review', method=["GET", "POST"])
@action.uses(url_signer.verify(), auth.user, db)
def thumb_review():
    review_id = request.json.get('review_id') 
    rating = request.json.get('thumb_rating') 
    user_email = auth.current_user.get('email')


    db.thumb.update_or_insert(
        (db.thumb.review_id == review_id) & (db.thumb.user_email == user_email),
        rating=rating,
        review_id=review_id,
        user_email=user_email
    )

    # return review with thumbs filled in 
    review = review_format(review_id)
    return dict(review=review)
############################################################################################################
  
@action('users_reviews')
@action.uses(db, auth, 'users_reviews.html')
def users_reviews():
#TODO if args eq none then do something
    rows = db((db.reviews.created_by == get_user_email()) &
                (db.courses.id == db.reviews.course_id)).select()
    return dict(rows=rows, url_signer=url_signer) 