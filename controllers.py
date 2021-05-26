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
    return dict(search_url=URL('search', signer=url_signer), reviews=reviews, url_signer=url_signer)

@action('add_course', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'add_course.html')
def add_course():
    #Create a form for all fields for now
    form = Form([Field('department', requires=IS_NOT_EMPTY()),
                Field('class_number',  'integer', requires=IS_NOT_EMPTY()),
                Field('class_name', requires=IS_NOT_EMPTY()),
                Field('class_description', 'text', requires=IS_NOT_EMPTY())],
                csrf_session=session, formstyle=FormStyleBulma)
    
    # if form is accepted
    if form.accepted:
        # Check if there is a course that already exists with the entered info
        if db((db.courses.department == form.vars["department"]) &
              (db.courses.class_number == form.vars["class_number"]) &
              (db.courses.class_name == form.vars["class_name"]) &
              (db.courses.class_description == form.vars["class_description"])).select().first() == None:
              # If there is no course with the inputted info then create the course by inserting its info into the courses table
              db.courses.insert(department = form.vars["department"],
                                class_number = form.vars["class_number"],
                                class_name = form.vars["class_name"],
                                class_description = form.vars["class_description"])
        redirect(URL('index'))
    return dict(form=form)
  
    
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
    
@action('delete_review')
@action.uses(url_signer.verify(), db, session, auth.user)
def delete():
    review_id = request.params.get('id')
    assert review_id is not None
    db(db.reviews.id == review_id).delete()
    redirect(URL('users_reviews'))

@action('search_course', method=["GET", "POST"])
@action.uses(db, auth, 'search_course.html')
def search_course():
    form = Form([Field('department', default=""),Field('class_number', 'integer', default=None),],
                csrf_session=session, formstyle=FormStyleBulma
                )
    #TODO if it is not accepted
    if form.accepted:
        redirect(URL('display_courses',form.vars["department"] ,form.vars["class_number"] ))

    return dict(form=form)

@action('display_courses/<major_id>/<course_num:int>')
@action.uses(db, auth, 'display_courses.html')
def display_courses(major_id=None, course_num=None):
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
    return dict(allMatches=allMatches, url_signer=url_signer)


@action('display_course/<major_id>/<course_num:int>')
@action.uses(db, auth, 'display_course.html')
def display_course(major_id=None, course_num=None):
#TODO if args eq none then do something
    if(course_num==None):
        course_num=0

    #grab matching course
    course_info = db((db.courses.department == major_id) & (db.courses.class_number == course_num)).select().first()

    #grab all reviews with that course
    reviews = db((db.reviews.course_id == course_info.id)).select()

    return dict(get_reviews_url = URL('get_reviews'),
                submit_review_url = URL('submit_review'),
                delete_review_url = URL('delete_review', signer=url_signer),
                course_info=course_info, course_id=course_info.id, reviews=reviews, url_signer=url_signer)


@action('submit_review/<course_id:int>', method="POST")
@action.uses(auth, db)
def submit_review(course_id):
    db.reviews.insert(
        course_id=course_id,
        teacher=request.json.get('teacher'),
        rating = request.json.get('rating'),
        review=request.json.get('review'),
    )
    created_by=get_user_email()
    return dict(created_by=created_by)


@action('get_reviews/<course_id:int>')
@action.uses(db)
def get_reviews(course_id):
    name=get_user_email()
    print(name)
    the_reviews = db(db.reviews.course_id == course_id).select().as_list()
    return dict(the_reviews=the_reviews, name=name)

 
@action('users_reviews')
@action.uses(db, auth, 'users_reviews.html')
def users_reviews():
#TODO if args eq none then do something
    rows = db((db.reviews.created_by == get_user_email()) &
                (db.courses.id == db.reviews.course_id)).select()
    return dict(rows=rows, url_signer=url_signer) 
    
@action('search')
@action.uses()
def search():
    q = request.params.get("q")
    query = q +"%"

    numbers = []

    for word in q.split():
        if word.isdigit():
            numbers.append(int(word))
    # TODO: do something with numbers so you can have a better search system

    results = db((db.courses.class_name.like(query)) |
                 (db.courses.department.like(query)) |
                 (db.courses.class_number.like(query))).select().as_list()

    return dict(results=results)


@action('write_review/<course_id>', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'add_review.html')
def write_review(course_id):
    #Create a form for all fields for now
    form = Form([Field('teacher',),
                Field('rating', 'integer',IS_INT_IN_RANGE(0, 5)),
                Field('review', 'text')],
                csrf_session=session, formstyle=FormStyleBulma)
                
    course_info = db(db.courses.id == course_id).select().first()
    
    # if form is accepted
    if form.accepted:
        # Check if there is a course that already exists with the entered info
        if db((db.courses.department == course_info.department) &
              (db.courses.class_number == course_info.class_number) &
              (db.courses.class_name == course_info.class_name)).select().first() == None:
              # If there is no course with the inputted info then create the course by inserting its info into the courses table
              db.courses.insert(department = course_info.department,
                                class_number = course_info.class_number,
                                class_name = course_info.class_name)
        # Grab the course that matches the filled fileds (its Id is needed)
        course = db((db.courses.department == course_info.department) &
              (db.courses.class_number == course_info.class_number) &
              (db.courses.class_name == course_info.class_name)).select().first()
        # insert the review into the reviews table
        db.reviews.insert(teacher = form.vars["teacher"],
                         rating = form.vars["rating"],
                         review = form.vars["review"], 
                         course_id = course.id)
        redirect(URL('index'))
    return dict(form=form)
    
    