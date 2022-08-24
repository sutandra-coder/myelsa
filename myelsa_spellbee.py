from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests
import pymysql

app = Flask(__name__)
cors = CORS(app)
spellbee = Blueprint('spellbee_api', __name__)
api = Api(spellbee, version='1.0', title='MyElsa API',
    description='MyElsa API')
name_space = api.namespace('myELSASpellBee', description='myELSA SpellBee')

def mysql_connection():
    connection = pymysql.connect(host='creamsonservices.com',
                                 user='creamson_langlab',
                                 password='Langlab@123',
                                 db='creamson_logindb',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

app.config['CORS_HEADERS'] = 'Content-Type'


spelling_model = api.model('spellbee', {
    "word_id":fields.Integer(required=True),
    "answer":fields.String(required=True),
    "correct":fields.String(required=True),
    "score":fields.Integer(required=True)
    })

spellbee_model = api.model('SpellBee Model', {
    "user_id":fields.Integer(required=True),
    "spelling_dtls":fields.List(fields.Nested(spelling_model))
    })

@name_space.route("/getWord/<int:user_id>")
class getWord(Resource):
    def get(self,user_id):
        connection = mysql_connection()
        cursor = connection.cursor()
        word_id = []
        cursor.execute("""SELECT `word_id` FROM `spellbee_tracking` WHERE `user_id` = %s""",(user_id))

        spelled_words = cursor.fetchall()
        if spelled_words:
            for idx, x in enumerate(spelled_words):
                word_id.append(x['word_id'])
                
        word_id = tuple(word_id)
        print(word_id)

        if word_id:
            cursor.execute("""SELECT `word_id`,`word`,`hint`,`synonym` FROM `spellbee_master` 
                WHERE `word_id` NOT in %s order by rand() limit 10""",(word_id,))
            spell = cursor.fetchall()
        else:
            cursor.execute("""SELECT `word_id`,`word`,`hint`,`synonym` FROM `spellbee_master` 
                order by rand() limit 10""")
            spell = cursor.fetchall()
        # print(spell)

        return ({"attributes": { 
                            "status_desc": "Spell Bee Details",
                            "status": "success"
                            },
                            "responseList":spell}), status.HTTP_200_OK



@name_space.route("/postUserSpelling")
class postUserSpelling(Resource):
    @api.expect(spellbee_model)
    def post(self):
        connection = mysql_connection()
        cursor = connection.cursor()
        details = request.get_json()
        user_id  = details['user_id']
        spelling_dtls = details['spelling_dtls']
        for i, j in enumerate(spelling_dtls):
            word_id = spelling_dtls[i]['word_id']
            answer = spelling_dtls[i]['answer']
            correct = spelling_dtls[i]['correct']
            score = spelling_dtls[i]['score']

            spelling_track_insert_query = ("""INSERT INTO `spellbee_tracking`(`word_id`, `user_id`, `answer`, 
                `correct`, `score`) VALUES (%s,%s,%s,%s,%s)""")

            track_data = (word_id,user_id,answer,correct,score)

            cursor.execute(spelling_track_insert_query,track_data)

        return ({"attributes": { 
                            "status_desc": "Spell Bee Details",
                            "status": "success"
                            }}), status.HTTP_200_OK