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

#TODO have a "your reviews page where users can mess with their own reviews only
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
@action('index')
@action.uses(db, auth, 'index.html')
def index():
#TODO how to grab all rows cleaner
    rows = db(db.reviews.major_iden != None).select()
    return dict(rows=rows, url_signer=url_signer)
    
    
@action('add_review', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'add_review.html')
def add_review():
    form = Form(db.reviews, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
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
def index():
    form = Form([Field('major_iden', requires=IS_NOT_EMPTY()),Field('class_number', 'integer'),],
                csrf_session=session, formstyle=FormStyleBulma
                )
    #TODO if it is not accepted
    if form.accepted:
        redirect(URL('display_course',form.vars["major_iden"] ,form.vars["class_number"] ))
        
    return dict(form=form)
  
@action('display_course/<major_id>/<course_num:int>')
@action.uses(db, auth, 'display_course.html')
def display_course(major_id=None, course_num=None):
#TODO if args eq none then do something
    rows = db((db.reviews.major_iden == major_id) & (db.reviews.class_number == course_num)).select()
    return dict(rows=rows, url_signer=url_signer) 
  
  
@action('users_reviews')
@action.uses(db, auth, 'users_reviews.html')
def users_reviews():
#TODO if args eq none then do something
    rows = db((db.reviews.created_by == get_user_email())).select()
    return dict(rows=rows, url_signer=url_signer) 