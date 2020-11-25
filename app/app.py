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
            'database': 'FordEscortData'
        }
        self.connection = mysql.connector.connect(**config)

    def closeDb(self):
        self.connection.close()

    def get_alldata(self):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM ford_escort')
        return cursor.fetchall()

    def get_rating(self, rating_id):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM ford_escort WHERE id=%s', (rating_id,))
        result = cursor.fetchall()
        return result[0]

    def update_rating(self, inputData):
        cursor = self.connection.cursor(dictionary=True)
        sql_update_query = """UPDATE ford_escort t SET t.Year = %s, t.Score = %s, t.Title = %s WHERE t.id = %s """
        cursor.execute(sql_update_query, inputData)
        self.connection.commit()

    def insert_rating(self, inputData):
        cursor = self.connection.cursor(dictionary=True)
        sql_insert_query = """INSERT INTO ford_escort (`Year`,Score,Title) VALUES (%s, %s, %s) """
        cursor.execute(sql_insert_query, inputData)
        self.connection.commit()

    def delete_rating(self, rating_id):
        cursor = self.connection.cursor(dictionary=True)
        sql_delete_query = """DELETE FROM ford_escort WHERE id = %s """
        cursor.execute(sql_delete_query, (rating_id,))
        self.connection.commit()


db = MyDb()


@app.route('/')
def index():
    deniro = db.get_alldata()
    return render_template('index.html', title='Home', user=user, deniro=deniro)

@app.route('/view/<int:rating_id>', methods=['GET'])
def record_view(rating_id):
    rating = db.get_rating(rating_id)
    return render_template('view.html', title='View Form', user=user, rating=rating)


@app.route('/edit/<int:rating_id>', methods=['GET'])
def form_edit_get(rating_id):
    rating = db.get_rating(rating_id)
    return render_template('edit.html', title='Edit Form', user=user, rating=rating)


@app.route('/edit/<int:rating_id>', methods=['POST'])
def form_update_post(rating_id):
    inputData = (request.form.get('Year'), request.form.get('Score'), request.form.get('Title'), rating_id)
    db.update_rating(inputData)
    return redirect("/", code=302)

@app.route('/rating/new', methods=['GET'])
def form_insert_get():
    return render_template('new.html', title='New Rating Form', user=user)


@app.route('/rating/new', methods=['POST'])
def form_insert_post():
    inputData = (request.form.get('Year'), request.form.get('Score'), request.form.get('Title'))
    db.insert_rating(inputData)
    return redirect("/", code=302)

@app.route('/delete/<int:rating_id>', methods=['POST'])
def form_delete_post(rating_id):
    db.delete_rating(rating_id)
    return redirect("/", code=302)


# API v1

@app.route('/api/v1/ratings')
def api_ratings() -> str:
    js = json.dumps(db.get_alldata())
    resp = Response(js, status=200, mimetype='application/json')
    return resp

@app.route('/api/v1/ratings/<int:rating_id>', methods=['GET'])
def api_retrieve(rating_id) -> str:
    result = db.get_rating(rating_id)
    json_result = json.dumps(result)
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp

@app.route('/api/v1/ratings/', methods=['POST'])
def api_add() -> str:
    inputData = (request.form.get('Year'), request.form.get('Score'), request.form.get('Title'))
    db.insert_rating(inputData)
    resp = Response(status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/ratings/<int:rating_id>', methods=['PUT'])
def api_edit(rating_id) -> str:
    inputData = (request.form.get('Year'), request.form.get('Score'), request.form.get('Title'), rating_id)
    db.update_rating(inputData)
    resp = Response(status=201, mimetype='application/json')
    return resp


@app.route('/api/ratings/<int:rating_id>', methods=['DELETE'])
def api_delete(rating_id) -> str:
    db.delete_rating(rating_id)
    resp = Response(status=210, mimetype='application/json')
    return resp




if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True) # set debug=False on deployment