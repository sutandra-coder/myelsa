from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests
import io,os
# from google.cloud import speech
# from pydub import AudioSegment
# import wave
import speech_recognition as sr
# import urllib2

# credential_path = "C:/Users/Hetal/Downloads/myElsa-1da1068500ff.json"
credential_path = "home/ubuntu/flaskproject/myElsa-1da1068500ff.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
# os.environ['PATH'] = 'C:/Program Files (x86)/ffmpeg-20190621-18dab61-win64-static/bin/'
app = Flask(__name__)
cors = CORS(app)
mysql = MySQL()
speech_to_text = Blueprint('speech_to_text_api', __name__)
api = Api(speech_to_text, version='1.0', title='MyElsa API',
    description='MyElsa API')
name_space = api.namespace('SpeechToText', description='SpeechToText')

app.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app.config['MYSQL_DATABASE_DB'] = 'creamson__lang_lab_b2c'
app.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'
mysql.init_app(app)

app.config['CORS_HEADERS'] = 'Content-Type'


reading_model = api.model('Reading Model', {
	"user_id":fields.Integer(required=True),
	"user_audio_file":fields.String(required=True),
	"original_text":fields.String(required=True)
	
	})

@name_space.route("/readingAnswerCheck")
class readingAnswerCheck(Resource):
	@api.expect(reading_model)
	def post(self):
		connection = mysql.connect()
		cursor = connection.cursor()
		details = request.get_json()
		user_id = details['user_id']
		message = 'Unable to convert speech to text'
		original_text = details['original_text'].strip()
		audio_file = details['user_audio_file'].strip()
		audio_file = urllib2.urlopen(audio_file)
		print(type(audio_file))
		r = sr.Recognizer()
		with open(credential_path,'r') as f:
			GOOGLE_CLOUD_SPEECH_CREDENTIALS = f.read()
		# print(GOOGLE_CLOUD_SPEECH_CREDENTIALS)

		audiofile = sr.AudioFile(audio_file)
		with audiofile as source:
			audio = r.record(source)

		response = r.recognize_google_cloud(audio_data = audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS,
			language='en-GB',show_all=True)
		print(response)
		correct = []
		if response:
			text = response['results'][0]['alternatives'][0]['transcript']
			reading_answer_insert_query = ("""INSERT INTO `user_reading_answer`(`User_ID`, `Answer`) 
				VALUES (%s,%s)""")
			answer_data = (user_id,text)
			cursor.execute(reading_answer_insert_query,answer_data)
			track_id = cursor.lastrowid
			snt1 = original_text.split()
			snt2 = text.split()
			
			try:
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
				print(correct)
				message = 'Sucessfully Converted speech to text'
			except:
				pass

		else:
			text = ''
			message = 'Unable to convert speech to text'
		details['user_answer'] = text
		details['match_dtls'] = correct
		cursor.close()
		return ({"attributes": {
	    				"status_desc": "Reading Match Details",
	    				"status": "success",
	    				"message":message
	    				},
	    				"responseList":{"AnswerDtls":details}}), status.HTTP_200_OK
if __name__ == '__main__':
	app.run(host='0.0.0.0')