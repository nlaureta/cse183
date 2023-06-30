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

import datetime
import random

from py4web import action, request, abort, redirect, URL, HTTP
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_username

url_signer = URLSigner(session)

# Some constants.
MAX_RETURNED_USERS = 20 # Our searches do not return more than 20 users.
MAX_RESULTS = 20 # Maximum number of returned meows. 

@action('index')
@action.uses('index.html', db, auth.user)
def index():
    return dict(
        # COMPLETE: return here any signed URLs you need.
        get_users_url = URL('get_users'),
        follow_url=URL('set_follow'),
        get_post_url = URL('get_post'),
    )

#gets users and follow status
@action("get_users")
@action.uses(db, auth.user)
def get_users():
    #Implement
    users = db(db.auth_user.username != get_username).select(db.auth_user.ALL)
    follower = db(db.auth_user.username == get_username()).select().first()
    follow_status = []
    if follower:
        for user in users:
            follow = db((db.follow.follower == follower) & (db.follow.followed == user)).select().first()
            status = "follow" if follow else "unfollow"
            follow_status.append({"username": user.username, "status": status})
    return dict(users=users, follow_status=follow_status) 

#sets follow status based on usernames
@action("set_follow", method="POST")
@action.uses(db, auth.user)
def set_follow():
    # Implement. 
    username = request.json.get('username')
    status = request.json.get('status')
    follower = db(db.auth_user.username == get_username()).select().first()
    followed = db(db.auth_user.username == username).select().first()
    
    if follower and followed:
        # Check if the follow relationship already exists
        follow = db((db.follow.follower == follower) & (db.follow.followed == followed)).select().first()
        if status == "follow":
            if not follow:
                # Create follow relationship if it doesn't exist
                db.follow.insert(follower=follower, followed=followed, status="follow")
        elif status == "unfollow":
            if follow:
                # Delete follow relationship if it exists
                follow.delete_record()
        
        db.commit()  # Commit the changes to the database
        
        return "ok"
    else:
        redirect("https://http.cat/403")


#gets post based on usernames
@action("get_posts")
@action.uses(db, auth.user)
def get_posts():
    # Get posts for each username
    users = db(db.auth_user.username != get_username()).select(db.auth_user.ALL)
    follower = db(db.auth_user.username == get_username()).select().first()
    follow_status = []
    if follower:
        for user in users:
            follow = db((db.follow.follower == follower) & (db.follow.followed == user)).select().first()
            status = "follow" if follow else "unfollow"
            follow_status.append({"username": user.username, "status": status})
            # print(follow_status)
    posts = db().select(db.meow.ALL)
    return dict(users=users,follow_status=follow_status,posts=posts)

# adds post to database
@action("add_post", method="POST")
@action.uses(db, auth.user)
def add_post():
    content = request.json.get("content")
    author = get_username()
    timestamp = datetime.datetime.utcnow()
    iso_timestamp = timestamp.isoformat()  # iso format

    db.meow.insert(author=author, timestamp=timestamp, content=content) #saves to database for other accounts to see
    
    return dict(content=content, author=author, timestamp=iso_timestamp)