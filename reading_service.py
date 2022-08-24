from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests, re

app = Flask(__name__)
cors = CORS(app)
mysql = MySQL()
reading_service = Blueprint('reading_api', __name__)
api = Api(reading_service, version='1.0', title='myElsa Analytics',
    description='myElsa Analytics')
name_space = api.namespace('CommunicationReading', description=':Communication Reading')

app.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app.config['MYSQL_DATABASE_DB'] = 'creamson__lang_lab_b2c'
app.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'
mysql.init_app(app)

app.config['CORS_HEADERS'] = 'Content-Type'

reading_model = api.model('Reading Model', {
	"user_id":fields.Integer(required=True),
	"original_text":fields.String(required=True),
	"user_answer":fields.String(required=True)
	})

@name_space.route("/readingAnswerCheck")
class readingAnswerCheck(Resource):
	@api.expect(reading_model)
	def post(self):
		details = request.get_json()
		original_text = details['original_text'].strip()
		user_answer = details['user_answer'].strip()
		rep_dict = {"Mrs.":"Mrs",
					"Mr.":"Mr"}
		connection = mysql.connect()
		cursor = connection.cursor()
		try:
			reading_answer_insert_query = ("""INSERT INTO `user_reading_answer`(`User_ID`, `Answer`, 
				`Last_ID`) VALUES (%s,%s,%s)""")
			answer_data = (details['user_id'],user_answer,details['user_id'])
			cursor.execute(reading_answer_insert_query,answer_data)
			track_id = cursor.lastrowid
			snt1 = original_text.split()
			for s in range(len(snt1)):
				print(snt1[s])
				for key, values in rep_dict.items():
					if snt1[s] == key:
						original_text = original_text.replace(snt1[s],values)
						print(original_text)
			snt1 = original_text.split()
			snt2 = user_answer.split()
			correct = []
			for i in range(len(snt1)):
				if snt1[i] == snt2[i]:
					correct.append(snt2[i])
				else:
					wrong_word = snt2[i]
					correct.append('#'+snt2[i])
					error_insert_query = ("""INSERT INTO `user_reading_error_track`(`Track_Id`, 
						`Error_word`, `Last_Id`) VALUES (%s,%s,%s)""")
					error_data = (track_id,wrong_word,i)
					cursor.execute(error_insert_query,error_data)
			connection.commit()
			details['match_dtls'] = correct
		except:
			pass
		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Reading Match Details",
	    				"status": "success"
	    				},
	    				"responseList":{"AnswerDtls":details}}), status.HTTP_200_OK

if __name__ == '__main__':
	app.run(host='0.0.0.0')


 