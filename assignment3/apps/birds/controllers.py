from py4web import action, request, abort, redirect, URL
from .common import db, session, T, cache, auth, logger
from .models import get_user_email
from .settings import APP_FOLDER
from py4web.utils.form import Form, FormStyleBulma
#from py4web.utils.url_signer import URLSigner
from py4web.core import HTTP

#url_signer = URLSigner(session)

#displays the table
@action('index')
@action.uses('index.html', auth.user, db)
def index():
    rows = db(db.bird.user_email == get_user_email()).select()
    return dict(rows=rows) 

#Uses form to add new entries   
@action('add', method=["GET", "POST"])
@action.uses('add.html', auth.user, db, session)
def add():
    # insert form. no record
    form = Form(db.bird, csrf_session=session, formstyle = FormStyleBulma) #if auth.user_id else None
    if form.accepted:
        redirect (URL('index'))
    return dict(form=form)

#Uses form to edit an entry. Checks that the entry belongs to the user editing it
@action('edit/<bird_id:int>', method=["GET", "POST"])
@action.uses('edit.html', auth.user, db, session)
def edit(bird_id=None):
    assert bird_id is not None
    b = db.bird[bird_id]
    if b is None:
        # No edits found
        redirect(URL('index'))

    #check if email matches
    if b.user_email != get_user_email():
        #doesn't belong, redirects to error page
        raise HTTP(400)
    
    # edit form. has record
    form = Form(db.bird, record = b, csrf_session=session, deletable=False, formstyle = FormStyleBulma) #if auth.user_id else None
    if form.accepted:
        #update happened
        redirect(URL('index'))
    return dict(form=form)

#increment by 1 the sightings count
@action('inc/<bird_id:int>')
@action.uses(db, auth.user, session)
def inc(bird_id=None):
    assert bird_id is not None
    bird = db.bird(bird_id)

     #check if email matches
    if bird.user_email != get_user_email(): 
         #doesn't belong, redirects to error page
        raise HTTP(400)
    
    #print(bird)
    bird.update_record(n_sightings=bird.n_sightings + 1)
    redirect(URL('index'))