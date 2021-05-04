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

from py4web import action, request, abort, redirect, URL
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
    form = Form([Field('department', requires=IS_NOT_EMPTY()),
                Field('class_number',  'integer', requires=IS_NOT_EMPTY()),
                Field('class_name', requires=IS_NOT_EMPTY()),
                Field('teacher',),
                Field('rating', 'integer',IS_INT_IN_RANGE(0, 5)),
                Field('review', 'text')],
                csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        if db((db.courses.department == form.vars["department"]) &
              (db.courses.class_number == form.vars["class_number"]) &
              (db.courses.class_name == form.vars["class_name"])).select().first() == None:
              print("this is the if")
              db.courses.insert(department = form.vars["department"],
                                class_number = form.vars["class_number"],
                                class_name = form.vars["class_name"])
        
        course = db((db.courses.department == form.vars["department"]) &
              (db.courses.class_number == form.vars["class_number"]) &
              (db.courses.class_name == form.vars["class_name"])).select().first()
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
    form = Form([Field('department', requires=IS_NOT_EMPTY()),Field('class_number', 'integer'),],
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
    rows = db((db.courses.department == major_id) & 
            (db.courses.class_number == course_num) & 
            (db.courses.id == db.reviews.course_id)).select()
    return dict(rows=rows, url_signer=url_signer) 
  
  
@action('users_reviews')
@action.uses(db, auth, 'users_reviews.html')
def users_reviews():
#TODO if args eq none then do something
    rows = db((db.reviews.created_by == get_user_email()) &
                (db.courses.id == db.reviews.course_id)).select()
    return dict(rows=rows, url_signer=url_signer) 