from workspace import database
from flask import Flask, request, render_template, send_from_directory, jsonify, redirect, url_for
import json

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

host = "https://extra-snickdx.c9users.io:8080"

# When the Flask app is shutting down, close the database session
@app.teardown_appcontext
def shutdown_session(exception=None):
    database.db_session.remove()

database.init_db()
from workspace.models import Person



def createPerson(new_person):
    if 'name' in new_person:
        p = Person(new_person['name'])
    else:
        return {"message":"Invalid fields given", "code":400}
    if 'country' in new_person:
        p.country = new_person["country"]
    try:
        database.db_session.add(p)
        database.db_session.commit()
    except error:
        return {"message":"Database error "+error, "code":500}
    finally:
        return {"message":jsonify(p.toDict()), "code":201}
        
def updatePerson(new_person, id):
    p = Person.query.get(id)
    try:
        if 'name' in new_person:
            p.name = new_person['name']
        else:
            return {"message":"Invalid fields given", "code":400}
        if 'country' in new_person:
            p.country = new_person["country"]
        database.db_session.commit()
    except error:
        return {"message":"Error "+error, "code":500}
    finally:
        return {"message":jsonify(p.toDict()), "code":202}

def deletePerson(id):
    try:
        p = Person.query.get(id)
        database.db_session.delete(p)
        database.db_session.commit()
    except error:
        return {"message":"Database error"+error, "code":500}
    finally:
        return {"message": "Record Deleted", "code": 204}

# *********************************APP1 ROUTES**********************************

@app.route("/")
def index():
    records = Person.query.all()
    records = list(map(lambda object: object.toDict(), records))
    response = jsonify(records)
    return render_template("app1.html", person=None, records=records, host=host)
    
@app.route("/update/<id>")
def update(id):
    p = Person.query.get(id)
    records = Person.query.all()
    records = list(map(lambda object: object.toDict(), records))
    response = jsonify(records)
    return render_template("app1.html", person=p, host=host, records=records)
    
@app.route('/js/<path>')
def send_js(path):
    return send_from_directory('templates/js', path)

@app.route('/persons', methods=['GET'])
def show_all_persons():
    records = Person.query.all()
    records = list(map(lambda object: object.toDict(), records))
    response = jsonify(records)
    response.status_code = 200
    return response

@app.route('/persons/<id>', methods=['GET'])
def show_person(id):
    return jsonify(Person.query.get(id).toDict())

@app.route('/persons', methods=['POST'])
def save_person():
    if request.content_type  == 'application/x-www-form-urlencoded':
        result = createPerson(request.form)
        if result['code'] == 201:
             return index()
        else:
            return render_template('error.html', result=result)
    render_template('error.html', result={"message":"Invliad data format", code:500})

@app.route('/persons/update/<id>', methods=['POST'])
def udpate_person(id):
    result = updatePerson(request.form, id)
    if result['code'] == 202:
        return index()
    else:
        return render_template('error.html', result=result)

@app.route('/persons/delete/<id>', methods=['GET'])
def remove_person(id):
    result = deletePerson(id)
    if result['code'] == 204:
        return index()
    else:
        return render_template('error.html', result=result)

    
# ******************************* APP2 Routes **********************************