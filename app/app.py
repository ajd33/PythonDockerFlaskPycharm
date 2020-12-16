from typing import List, Dict
import simplejson as json
import mysql.connector
from flask import Flask, request, Response, redirect
from flask import render_template

app = Flask(__name__)
user = {'username': 'Andrew Drumm'}

class MyDb:
    def __init__(self):
        config = {
            'user': 'root',
            'password': 'root',
            'host': 'db',
            'port': '3306',
            'database': 'fordEscort'
        }
        self.connection = mysql.connector.connect(**config)

    def closeDb(self):
        self.connection.close()

    def get_alldata(self):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM escort')
        return cursor.fetchall()

    def get_mileage(self, mileage_id):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM escort WHERE id=%s', (mileage_id,))
        result = cursor.fetchall()
        return result[0]

    def update_mileage(self, inputData):
        cursor = self.connection.cursor(dictionary=True)
        sql_update_query = """UPDATE escort t SET t.Year = %s, t.Mileage = %s, t.Price = %s WHERE t.id = %s """
        cursor.execute(sql_update_query, inputData)
        self.connection.commit()

    def insert_mileage(self, inputData):
        cursor = self.connection.cursor(dictionary=True)
        sql_insert_query = """INSERT INTO escort (`Year`,Mileage,Price) VALUES (%s, %s, %s) """
        cursor.execute(sql_insert_query, inputData)
        self.connection.commit()

    def delete_mileage(self, mileage_id):
        cursor = self.connection.cursor(dictionary=True)
        sql_delete_query = """DELETE FROM escort WHERE id = %s """
        cursor.execute(sql_delete_query, (mileage_id,))
        self.connection.commit()


db = MyDb()


@app.route('/')
def index():
    escort = db.get_alldata()
    return render_template('index.html', Price='Home', user=user, escort=escort)

@app.route('/view/<int:mileage_id>', methods=['GET'])
def record_view(mileage_id):
    mileage = db.get_mileage(mileage_id)
    return render_template('view.html', Price='View Form', user=user, mileage=mileage)


@app.route('/edit/<int:mileage_id>', methods=['GET'])
def form_edit_get(mileage_id):
    mileage = db.get_mileage(mileage_id)
    return render_template('edit.html', Price='Edit Form', user=user, mileage=mileage)


@app.route('/edit/<int:mileage_id>', methods=['POST'])
def form_update_post(mileage_id):
    inputData = (request.form.get('Year'), request.form.get('Mileage'), request.form.get('Price'), mileage_id)
    db.update_mileage(inputData)
    return redirect("/", code=302)

@app.route('/mileage/new', methods=['GET'])
def form_insert_get():
    return render_template('new.html', Price='New Mileage Form', user=user)


@app.route('/mileage/new', methods=['POST'])
def form_insert_post():
    inputData = (request.form.get('Year'), request.form.get('Mileage'), request.form.get('Price'))
    db.insert_mileage(inputData)
    return redirect("/", code=302)

@app.route('/delete/<int:mileage_id>', methods=['POST'])
def form_delete_post(mileage_id):
    db.delete_mileage(mileage_id)
    return redirect("/", code=302)

# API version 1

@app.route('/api/v1/mileage')
def api_mileage() -> str:
    js = json.dumps(db.get_alldata())
    resp = Response(js, status=200, mimetype='application/json')
    return resp

@app.route('/api/v1/mileages/<int:mileage_id>', methods=['GET'])
def api_retrieve(mileage_id) -> str:
    result = db.get_mileage(mileage_id)
    json_result = json.dumps(result)
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp

@app.route('/api/v1/mileages/', methods=['POST'])
def api_add() -> str:
    inputData = (request.form.get('Year'), request.form.get('Mileage'), request.form.get('Price'))
    db.insert_mileage(inputData)
    resp = Response(status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/mileages/<int:mileage_id>', methods=['PUT'])
def api_edit(mileage_id) -> str:
    inputData = (request.form.get('Year'), request.form.get('Mileage'), request.form.get('Price'), mileage_id)
    db.update_mileage(inputData)
    resp = Response(status=201, mimetype='application/json')
    return resp


@app.route('/api/mileages/<int:mileage_id>', methods=['DELETE'])
def api_delete(mileage_id) -> str:
    db.delete_mileage(mileage_id)
    resp = Response(status=210, mimetype='application/json')
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True) # set debug=False on deployment