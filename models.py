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

#TODO make a class reference to a different table instead
#TODO make major_iden like "CSE" one of those enums likes hes shown
#TODO allow some null inputs?
db.define_table(
    'reviews',
    Field('major_iden', requires=IS_NOT_EMPTY()),
    Field('class_number', 'integer'),
    Field('created_by', default=get_user_email),
    Field('class_name', requires=IS_NOT_EMPTY()),
    Field('teacher',),
    Field('rating', 'integer',IS_INT_IN_RANGE(0, 5)),
    Field('review', 'text'),

)

db.reviews.created_by.readable = db.reviews.created_by.writable = False

db.commit()
