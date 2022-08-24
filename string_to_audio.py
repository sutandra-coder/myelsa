from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests
import os
import io
from pydub import AudioSegment
import base64
import speech_recognition as sr
# import urllib2
import wave
credential_path = "home/ubuntu/flaskproject/myElsa-1da1068500ff.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

app = Flask(__name__)
cors = CORS(app)
mysql = MySQL()
UPLOAD_FOLDER = '/home/ubuntu/tally/uploadfolder'
SERVER_PATH = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/tally/uploadfolder/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
string_to_audio = Blueprint('string_to_audio_api', __name__)
api = Api(string_to_audio, version='1.0', title='MyElsa API',
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
    "base64_audio_string":fields.String(required=True),
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
        original_text = details['original_text'].strip()
        base64_audio_string = details['base64_audio_string'].strip()
        last_update_ts = datetime.now().strftime('%Y-%m-%d%H%M%S')
        response = ''
        # read_file = urllib2.urlopen(file_path)
        # audio_string = base64_audio_string
        # read_file.read().encode('utf-8',errors='ignore')
        decoded = base64.decodestring(bytes(base64_audio_string))
        s = io.BytesIO(decoded)
        filename = str(user_id)+'_'+str(last_update_ts) + '.wav'
        audio_path = os.path.join(UPLOAD_FOLDER,filename)
        abs_audio_path = SERVER_PATH+filename
        details['audio_path'] = abs_audio_path
        AudioSegment.from_raw(s,sample_width=2, frame_rate=192000, channels=1).set_frame_rate(48000).export(audio_path, format='wav')
        # obj = wave.open(audio_path,'r')
        # sample_rate = obj.getframerate()
        # n_frames = obj.getnframes()
        # data = obj.readframes(n_frames)
        with open(credential_path,'r') as f:
            GOOGLE_CLOUD_SPEECH_CREDENTIALS = f.read()
        r = sr.Recognizer()
        # if sample_rate > 48000:
        # 	last_update_ts2 = datetime.now().strftime('%Y-%m-%d%H%M%S')
        # 	filename2 = str(user_id)+'_'+str(last_update_ts2) + '.wav'
        # 	audio_path2 = os.path.join(UPLOAD_FOLDER,filename2)
        # 	abs_audio_path = SERVER_PATH+filename
        # 	details['audio_path'] = abs_audio_path
        # 	AudioSegment.from_wav(audio_path).set_frame_rate(48000).export(audio_path2, format='wav')
        # 	audiofile = sr.AudioFile(audio_path2)
        # 	with audiofile as source:
        # 		audio = r.record(source)
        # 	response = r.recognize_google_cloud(audio_data = audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS,
        #         language='en-GB',show_all=True)
        # else:
        # 	audiofile = sr.AudioFile(audio_path)
        # 	with audiofile as source:
        # 		audio = r.record(source)
        # 	response = r.recognize_google_cloud(audio_data = audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS,
        #         language='en-GB',show_all=True)
        with open(credential_path,'r') as f:
            GOOGLE_CLOUD_SPEECH_CREDENTIALS = f.read()
        # print(GOOGLE_CLOUD_SPEECH_CREDENTIALS)
        audiofile = sr.AudioFile(audio_path)
        with audiofile as source:
            audio = r.record(source)
        try:
            response = r.recognize_google_cloud(audio_data = audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS,
                language='en-GB',show_all=True)
            print(response)
        except:
            pass
        if response:
            pass
            # print(response)
        else:
            # print('in else')
            s = io.BytesIO(decoded)
            # xx = 'sound.wav'
            last_update_ts2 = datetime.now().strftime('%Y-%m-%d%H%M%S')
            filename2 = str(user_id)+'_'+str(last_update_ts2) + '.wav'
            audio_path2 = os.path.join(UPLOAD_FOLDER,filename2)
            abs_audio_path = SERVER_PATH+filename2
            details['audio_path'] = abs_audio_path
            AudioSegment.from_raw(s,sample_width=2,frame_rate=48000,channels=1).export(audio_path2, format='wav')
            # obj3 = wave.open(xx,'r')
            # print( "Number of channels",obj3.getnchannels())
            # print ( "Sample width",obj3.getsampwidth())
            # print ( "Frame rate.",obj3.getframerate())
            # print ("Number of frames",obj3.getnframes())
            # print ( "parameters:",obj3.getparams())
            # obj3.close()
            r = sr.Recognizer()
            # print(GOOGLE_CLOUD_SPEECH_CREDENTIALS)
            audiofile = sr.AudioFile(audio_path2)
            with audiofile as source:
                audio = r.record(source)
            try:
                response = r.recognize_google_cloud(audio_data = audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS,
                    language='en-GB',show_all=True)
                print(response)
            except:
                pass
            # print('last else')
        
        # audiofile = sr.AudioFile(audio_path)
        # with audiofile as source:
        #     audio = r.record(source)

        # response = r.recognize_google_cloud(audio_data = audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS,
        #     language='en-GB',show_all=True)
        # print(response)
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
            correct = []
            try:
                if len(snt1) == len(snt2):
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
                else:
                    for i in range(len(snt2)):
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
        details.pop('base64_audio_string')
        cursor.close()
        # message = 'Unable to convert speech to text'
        
        return ({"attributes": {
                        "status_desc": "Reading Match Details",
                        "status": "success",
                        "message":message
                        },
                        "responseList":{"AnswerDtls":details}}), status.HTTP_200_OK
if __name__ == '__main__':
    app.run(host='0.0.0.0')