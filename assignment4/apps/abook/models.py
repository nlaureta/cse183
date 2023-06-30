"""
This file defines the database models
"""
import datetime

from pydal.validators import *

from .common import Field, auth, db, session

def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()

### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later
#
# db.commit()
#

db.define_table(
    "contact", 
    Field("first_name"),
    Field("last_name"),
    Field('created_by', 'reference auth_user', default=lambda: auth.user_id, readable = False, writable = False)
    #Field("user_email", default=get_user_email, writable = False, readable = False)
    #auth.signature
    
)



db.define_table(
    "phone", 
    Field('contact_id', 'reference contact', readable=False,writable=False), # ondelete="CASCADE" is default which delete contact as well
    Field('phone'),
    Field('kind')
    #Field("user_email", default=get_user_email, writable = False, readable = False)
    #auth.signature
    
)
db.contact.id.readable = False
db.contact.id.writable = False
db.phone.id.readable = False
db.phone.id.writable = False

db.commit()
