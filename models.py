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
    Field('class_number',  'integer', requires=IS_NOT_EMPTY()),
    Field('class_name', requires=IS_NOT_EMPTY()),
    Field('class_description', 'text', requires=IS_NOT_EMPTY()),
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
    Field('rating', 'integer',IS_INT_IN_RANGE(0, 5)),
    Field('review', 'text'),

)

db.reviews.created_by.readable = db.reviews.created_by.writable = False
db.reviews.course_id.readable = db.reviews.course_id.writable = False
db.reviews.id.readable = db.reviews.id.writable = False

db.commit()
