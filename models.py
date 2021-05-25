"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()
    
db.define_table(
    'courses',
    Field('department', requires=IS_NOT_EMPTY()),
    Field('class_number', requires=IS_NOT_EMPTY()),
    Field('class_name', requires=IS_NOT_EMPTY()),
    Field('class_description'),
) 

#TODO make a class reference to a different table instead
#TODO make department like "CSE" one of those enums likes hes shown
#TODO allow some null inputs?
#TODO added a created date
db.define_table(
    'reviews',
    Field('course_id', 'reference_courses'),
    Field('created_by', default=get_user_email),
    Field('teacher',),
    Field('rating', 'integer', requires=IS_INT_IN_RANGE(0, 5)),
    Field('review_id', 'reference reviews'),
    Field('review', 'text'),
    #Field('created_date', 'datetime', default=get_time),
    #Field('post_id', 'reference_reviews'),
    #Field('user_email', default=get_user_email),
    #Field('post_text', 'text'),
    #Field('created_date', 'datetime', default=get_time),

)

db.define_table(
    'post',
    # Field('post_id', 'reference_post'),
    Field('review_id', 'reference reviews'),
    Field('user_email', default=get_user_email),
    Field('post_text', 'text', requires=IS_NOT_EMPTY()),
    Field('post_teacher', 'text', requires=IS_NOT_EMPTY()),
    Field('post_rating', 'integer', requires=IS_NOT_EMPTY()),
    Field('created_date', 'datetime', default=get_time),
)

db.define_table(
    'thumb',
    Field('user_email', default=get_user_email()),
    # Field('review_id', 'reference reviews'),
    Field('post_id', 'reference post'),
    Field('thumb_rating', 'integer', default=0)
)

db.reviews.created_by.readable = db.reviews.created_by.writable = False

db.commit()
