"""
This file defines the database models
"""

import datetime
import random
from py4web.utils.populate import FIRST_NAMES, LAST_NAMES, IUP
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_username():
    return auth.current_user.get('username') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later

db.define_table(
    'follow', 
    Field('follower', 'reference auth_user', default = get_username),
    Field('followed', 'reference auth_user'),
    Field('status', requires=IS_IN_SET(["follow", "unfollow"])),

)

db.define_table(
    'meow',
    Field('author'),
    Field('timestamp'),
    Field('content'),
    Field('reply_to', 'reference meow'),
    Field('num_replies', 'integer', default=0)
)


# db.define_table(
#     "bird", 
#     Field("bird"),
#     Field("weight", "integer", default = 0, requires=IS_INT_IN_RANGE(0,1e6)),
#     Field("diet"), 
#     Field("habitat"),
#     Field("n_sightings", "integer", default = 0, requires=IS_INT_IN_RANGE(0,1e6)),
#     Field("user_email", default=get_user_email, writable = False, readable = False),
#     #auth.signature
    
# )

db.commit()

def add_users_for_testing(num_users):
    # Test user names begin with "_".
    # Counts how many users we need to add.
    db(db.meow).delete()
    db(db.follow).delete()
    db(db.auth_user.username.startswith("_")).delete()
    num_test_users = db(db.auth_user.username.startswith("_")).count()
    num_new_users = num_users - num_test_users
    print("Adding", num_new_users, "users.")
    for k in range(num_test_users, num_users):
        first_name = random.choice(FIRST_NAMES)
        last_name = first_name = random.choice(LAST_NAMES)
        username = "_%s%.2i" % (first_name.lower(), k)
        user = dict(
            username=username,
            email=username + "@ucsc.edu",
            first_name=first_name,
            last_name=last_name,
            password=username,  # To facilitate testing.
        )
        auth.register(user, send=False)
        ts = datetime.datetime.utcnow()
        for n in range(1):
            ts -= datetime.timedelta(seconds=random.uniform(60, 1000))
            m = dict(
                author=username,
                timestamp = ts,
                content=" ".join(random.choices(list(IUP.keys()), k=20))
            )
            db.meow.insert(**m)
        print(m)
    db.commit()
    
# Comment out this line if you are not interested. 
add_users_for_testing(20)
