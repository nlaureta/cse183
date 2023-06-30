import uuid

from py4web import URL, Field, abort, action, redirect, request
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.url_signer import URLSigner
from .models import get_user_email
from py4web.utils.form import SPAN, A
from .common import T, auth, cache, db, session, signed_url
from py4web.core import HTTP

url_signer = URLSigner(session)

# The auth.user below forces login.
@action("index")
@action.uses("index.html", auth.user)
def index():
    rows = db((db.contact.created_by == auth.user_id)).select()
    for row in rows:
        phone_numbers = db(db.phone.contact_id == row.id).select().as_list()

        # Format the phone numbers as a nice string and add them to the contact row
        s = []
        for phone_number in phone_numbers:
            s.append(f"{phone_number['phone']} ({phone_number['kind']})")
        row["phone_numbers"] = ", ".join(s)
    return dict(rows=rows)

#Uses form to add new entries   
@action('add_contact', method=["GET", "POST"])
@action.uses('add_contact.html', auth.user, db, session)
def add():
    # insert form. no record
    form = Form(db.contact, csrf_session=session, formstyle = FormStyleBulma) #if auth.user_id else None
    form.param.sidecar.append(SPAN(" ", A('Cancel', _class="button is-danger", _href=URL('index'))))
    if form.accepted:
        redirect (URL('index'))
    return dict(form=form)

#Uses form to edit a contact info. Checks that the entry belongs to the user editing it
@action('edit_contact/<contact_id:int>', method=["GET", "POST"])
@action.uses('editContact.html', auth.user, db, session)
def edit(contact_id=None):
    assert contact_id is not None
    b = db.contact[contact_id]
    if b is None:
        # No edits found
        redirect(URL('index'))

    #check if email matches
    if b.created_by != auth.user_id:
        #doesn't belong, redirects to index
        redirect(URL('index'))
    
    # edit form. has record
    form = Form(db.contact, record = b, csrf_session=session, deletable=False, formstyle = FormStyleBulma) #if auth.user_id else None
    form.param.sidecar.append(SPAN(" ", A('Cancel', _class="button is-danger", _href=URL('index'))))
    if form.accepted:
        #update happened
        redirect(URL('index'))
    return dict(form=form)

#deletes contact info an phone number
@action('delete_contact/<contact_id:int>')
@action.uses(db, session, auth.user)
def delete(contact_id=None):
    assert contact_id is not None 
    b = db.contact[contact_id]
    if b is None:
        # No edits found
        redirect(URL('index'))
    if b.created_by != auth.user_id:
        #doesn't belong, redirects to error 400 page
        raise HTTP(400)
    db(db.contact.id == contact_id).delete()
    redirect(URL('index'))

#adds new phone and queries it to the contact id
@action('add_phones/<contact_id:int>', method=["GET", "POST"])
@action.uses('add_phones.html', auth.user, db, session)
def add(contact_id=None):
    #rows = db(db.contact.created_by == auth.user_id).select()
    assert contact_id is not None
    b = db.contact[contact_id]
    if b is None:
        # No edits found
        redirect(URL('index'))
    print(contact_id)
  
    if b.created_by != auth.user_id:
        #doesn't belong, redirects to index
        redirect(URL('index'))

    # edit form. has record
    form = Form([Field('phone'), Field('kind')], csrf_session=session, formstyle=FormStyleBulma, deletable=False)
    form.param.sidecar.append(SPAN(" ", A('Cancel', _class="button is-danger", _href=URL('edit_phones', contact_id))))
    if form.accepted:
        #update happened
        db.phone.insert(
            contact_id = contact_id, 
            phone = form.vars['phone'],
            kind = form.vars['kind']
        )
        
        redirect(URL('edit_phones', contact_id))
    return dict(form=form, b=b)

#shows table of the contact's numbers based on contact id
@action('edit_phones/<contact_id:int>')
@action.uses('editPhone.html', auth.user, db, session)
def edit(contact_id=None):
    b = db.contact[contact_id]
    if b is None:
        # No edits found
        redirect(URL('index'))
    assert contact_id is not None

    #check if email matches
    if b.created_by != auth.user_id:
        #doesn't belong, redirects to index
        redirect(URL('index'))
    
    rows = db(db.phone.contact_id == contact_id).select()
    return dict(rows=rows, contact_id=contact_id, b=b)

#edits phone numbers based on contact id and phone id
@action('edit_phones/<contact_id:int>/<phone_id:int>', method=["GET", "POST"])
@action.uses('add_phones.html', auth.user, db, session)
def edit(contact_id=None, phone_id=None):
    assert contact_id is not None
    assert phone_id is not None
    b = db.contact[contact_id]
    if b is None:
        # No edits found
        redirect(URL('index'))
    phone = db((db.phone.contact_id == contact_id) & (db.phone.id == phone_id)).select().first()
    if phone is None:
        # No edits found
        redirect(URL('index'))

    #check if email matches
    if b.created_by != auth.user_id:
        #doesn't belong, redirects to index
        redirect(URL('index'))
    
    # edit form. has record
    form = Form(db.phone, record = phone, csrf_session=session, deletable=False, formstyle = FormStyleBulma) #if auth.user_id else None
    form.param.sidecar.append(SPAN(" ", A('Cancel', _class="button is-danger", _href=URL('edit_phones', contact_id))))
    if form.accepted:
        #update happened
        redirect(URL('edit_phones', contact_id))
    return dict(form=form, b=b)

@action('delete_phones/<phone_id:int>')
@action.uses(db, session, auth.user)
def delete(phone_id=None):
    assert phone_id is not None

    phone = db(db.phone.id == phone_id).select().first() #check if phone id exist
    if phone is None:
    # Phone record not found, redirect to index
        redirect(URL('index'))

    contact_id = phone.contact_id #gets contact id of phone
    if contact_id is None: 
        #contact id not found redirect to index
        redirect(URL('index'))

    b = db.contact[contact_id]
    if b is None:
        # No edits found
        redirect(URL('index'))

    #check if email matches
    if b.created_by != auth.user_id:
        #doesn't belong, redirects to error page
        raise HTTP(400)
    
    db(db.phone.id == phone_id).delete()
    redirect(URL('edit_phones', contact_id))
    