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
    
def get_username():
    current_user_info = db(db.auth_user.email == get_user_email()).select().first()
    user_name = current_user_info.first_name + " " + current_user_info.last_name if current_user_info is not None else "Unknown"
    return user_name

    
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
    Field('created_by_username', default=get_username),
    Field('teacher', requires=IS_NOT_EMPTY()),
    Field('rating', 'integer',IS_INT_IN_RANGE(1, 5), requires=IS_NOT_EMPTY()),
    Field('workload', 'integer',IS_INT_IN_RANGE(1, 5), requires=IS_NOT_EMPTY()),
    Field('difficulty', 'integer',IS_INT_IN_RANGE(1, 5), requires=IS_NOT_EMPTY()),
    Field('review', 'text'),
    Field('created_time', default=get_time),

)

db.reviews.created_by.readable = db.reviews.created_by.writable = False
db.reviews.created_by_username.readable = db.reviews.created_by_username.writable = False
db.reviews.course_id.readable = db.reviews.course_id.writable = False
db.reviews.created_time.readable = db.reviews.created_time.writable = False
db.reviews.id.readable = db.reviews.id.writable = False

db.commit()
