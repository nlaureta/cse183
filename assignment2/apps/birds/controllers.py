from py4web import action, request, abort, redirect, URL
from .common import db, session, T, cache, auth, logger
from .models import get_user_email
from .settings import APP_FOLDER

import os
import json

@action('index')
@action.uses('index.html', auth)
def index():
    ### You have to modify the code here as well.
    filename = os.path.join(APP_FOLDER, "data", "table.json")
    with open(filename) as f:
        data = json.load(f)
    return dict(data=data)

    #-------uses database-----------
    #birds = [] #array to store birds
    #for bird in data:
    #    birds.append(db.birds(bird=bird['bird'], weight=bird['weight'], diet=bird['diet'], habitat=bird['habitat'])) #insert data at end of array

    
    #     db.birds.insert(bird=bird['bird'], weight=bird['weight'], diet=bird['diet'], habitat=bird['habitat'])
    # birds = db().select(db.birds.ALL)

    # for bird in data:
    #     db.birds.update_or_insert(db.birds.bird == bird['bird'],bird=bird['bird'],weight=bird['weight'],diet=bird['diet'],habitat=bird['habitat'])
    # birds = db().select(db.birds.ALL, orderby=db.birds.id)
    #return dict(data=data)
