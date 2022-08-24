from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta,date
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests
#from textblob import TextBlob,Word
#import textblob.exceptions
from gtts import gTTS
import os
# import playsound
from werkzeug import secure_filename
# from PyDictionary import PyDictionary
# from vocabulary.vocabulary import Vocabulary as vb
# from nltk.corpus import wordnet
# from translate import Translator
from googletrans import Translator
# from nltk.corpus import wordnet
from importlib import reload as foo
import importlib as il
import sys
il.reload(sys)
from gingerit.gingerit import GingerIt
# reload(sys)
# sys.setdefaultencoding('utf-8')
app = Flask(__name__)
cors = CORS(app)
mysql = MySQL()
text_to_speech = Blueprint('text2speech_api', __name__)
api = Api(text_to_speech, version='1.0', title='MyElsa API',
    description='MyElsa API')
name_space = api.namespace('TranslationAndMeaning', description='Translation And Meaning')

app.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app.config['MYSQL_DATABASE_DB'] = 'creamson_angrez_dost'
app.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'

mysql.init_app(app)

app.config['CORS_HEADERS'] = 'Content-Type'
# UPLOAD_FOLDER = 'uploads'
UPLOAD_FOLDER = '/home/ubuntu/tally/uploadfolder'
SERVER_PATH = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/tally/uploadfolder/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
text2speech_post = api.model('Text_Translation', {
	"user_id":fields.Integer(required=True),
	"source_lang":fields.String(required=True),
	"source_text":fields.String(required=True),
	"target_lang":fields.String(required=True)})

@name_space.route("/translateText")
class translateText(Resource):
	@api.expect(text2speech_post)
	def post(self):
		connection = mysql.connect()
		cursor = connection.cursor()
		details = request.get_json()
		user_id = details['user_id']
		source_lang = details['source_lang']
		source_text = details['source_text']
		target_lang = details['target_lang']
		last_update_ts = datetime.now().strftime('%Y-%m-%d%H%M%S')
		print(last_update_ts)
		translator = Translator()
		translation = translator.translate(source_text, dest=target_lang)
		mytext = translation.text
		print(mytext)
		if translation:
			myobj = gTTS(text=mytext, lang=target_lang,slow=False)
			filename = str(user_id)+'_'+str(last_update_ts)+'.mp3'
			audio_file = os.path.join(UPLOAD_FOLDER,filename)
			# audio_path = os.path.abspath(audio_file).replace('\\','/')
			audio_path = SERVER_PATH+filename
			# print(audio_path)
			path = os.path.abspath(audio_file)
			myobj.save(audio_file)
			audio_insert_query = ("""INSERT INTO `translation`(`user_id`, `source_lang`, 
				`source_text`, `target_lang`, `target_text`, `audio_filepath`) 
				VALUES (%s,%s,%s,%s,%s,%s)""")
			translated_data = (user_id,source_lang,source_text,target_lang,mytext,audio_path)
			cursor.execute(audio_insert_query,translated_data)
			details['target_text'] = mytext
			details['audio_path'] = audio_path
			# audio = playsound.playsound(audio_file, True)
			cursor.close()
			return ({"attributes": {
		    				"status_desc": "Translation Details",
		    				"status": "success"
		    				},
		    				"responseList":{"TranslationDtls":details}}), status.HTTP_200_OK

dict_post = api.model('Dictionary', {
	"user_id":fields.Integer(required=True),
	"word":fields.String(required=True)})

@name_space.route("/findMeanings")
class findMeanings(Resource):
	@api.expect(dict_post)
	def post(self):
		connection = mysql.connect()
		cursor = connection.cursor()
		details = request.get_json()
		word = details['word']
		user_id = details['user_id']
		def find_meaning(word):
			url = 'https://googledictionaryapi.eu-gb.mybluemix.net/?define={}'.format(word)
			r = requests.get(url)
			code = r.status_code
			if code == 200:
				meaning = (r.content).decode('utf-8').replace('\n','')
				meaning = json.loads(meaning)
				meaning = meaning[0]
				findword = meaning['word']
				origin = meaning['origin']
				define = meaning['meaning']
				partsofspeech = {}
				definitions = {}
				
				mean_list = []
				for key, value in define.items():
					mean_list.append({"partsofspeech":key,
											"definitions":value})
				print(mean_list)

				meandict = {"word":findword,
							"origin":origin,
							"meaning":mean_list}

			else:
				meandict = json.dumps('Wrong Spelling')
			# synonyms = []
			# antonyms = []

			# for syn in wordnet.synsets(word):
			# 	for l in syn.lemmas():
			# 		synonyms.append(l.name())
			# 		if l.antonyms():
			# 			 antonyms.append(l.antonyms()[0].name())

			# syno = set(synonyms)
			# anto = set(antonyms)
			return meandict#,syno,anto
			

		# blob = TextBlob(word)
		# correct = blob.correct()
		# print(correct)
		
		dict_insert_quert = ("""INSERT INTO `dictionary`(`User_Id`, `word`) 
			VALUES(%s,%s)""")
		dict_data = (user_id,word)
		cursor.execute(dict_insert_quert,dict_data)
		cursor.close()
		
		# output,synonym,antonym = find_meaning(word)
		output = find_meaning(word)
		# return ({"attributes": {
		#     				"status_desc": "Definition Details",
		#     				"status": "success"
		#     				},
		#     	"responseList":{"DefinitionDtls":json.loads(output),
		#     					"synonyms":(list(synonym)),
		#     					"antonyms":(list(antonym))}}), status.HTTP_200_OK
		return ({"attributes": {
		    				"status_desc": "Definition Details",
		    				"status": "success"
		    				},
		    	"responseList":{"DefinitionDtls":output}}), status.HTTP_200_OK
		# else:
		# 	return ({"attributes": {
		# 	    				"status_desc": "Word Suggestions",
		# 	    				"status": "success"
		# 	    				},
		# 	    	"responseList":{"SuggestionDtls":[{"word":word,
		# 	    										"suggestion":'correct.__str__()'}]}}), status.HTTP_200_OK

pronunciation_post = api.model('Pronunciation', {
	"user_id":fields.Integer(required=True),
	"word":fields.String(required=True)})

@name_space.route("/getPronunciation")
class getPronunciation(Resource):
	@api.expect(pronunciation_post)
	def post(self):
		connection = mysql.connect()
		cursor = connection.cursor()
		details = request.get_json()
		word = details['word']
		user_id = details['user_id']
		last_update_ts = datetime.now().strftime('%Y-%m-%d%H%M%S')
		# blob = TextBlob(word)
		# correct = blob.correct()
		# print(correct)
		pro_insert_quert = ("""INSERT INTO `pronunciation`(`User_Id`, `word`) 
			VALUES(%s,%s)""")
		pro_data = (user_id,word)
		cursor.execute(pro_insert_quert,pro_data)
		cursor.close()
		
		myobj = gTTS(text=word, lang='en',slow=False)
		filename = str(user_id)+'_'+str(last_update_ts)+'.mp3'
		audio_file = os.path.join(UPLOAD_FOLDER,filename)
		audio_path = SERVER_PATH+filename
		myobj.save(audio_file)
		# audio = playsound.playsound(audio_file, True)
		details['audio_path'] = audio_path
		return ({"attributes": {
    				"status_desc": "Pronunciation Details",
    				"status": "success"
    				},
    				"responseList":{"PronunciationDtls":details}}), status.HTTP_200_OK

		# else:
		# 	return ({"attributes": {
		# 	    				"status_desc": "Word Suggestions",
		# 	    				"status": "success"
		# 	    				},
		# 	    	"responseList":{"SuggestionDtls":[{"word":word,
		# 	    										"suggestion":correct.__str__()}]}}), status.HTTP_200_OK

@name_space.route("/responseEngine/<topic_id>/<int:level>/<user_res>")
class responseEngine(Resource):
	def get(self,topic_id,level,user_res):
		connection = mysql.connect()
		cursor = connection.cursor()
		try:
			cursor.execute("""SELECT `Response`,`Ideal_Response` FROM `response` WHERE `Keyword_Id` 
				in (SELECT `Keyword_Id` FROM `keyword` WHERE `Topic_Id` 
				in (SELECT `Topic_Id` FROM `topic` WHERE `Level` = %s) and Keyword RLIKE %s) 
				ORDER BY RAND() LIMIT 1""",(level,user_res.strip()+'*'))
			res_desc = cursor.description
			desc_names = [col[0] for col in res_desc]
			res_data = [dict(izip(desc_names, row)) for row in cursor.fetchall()]
			print(res_data)
			if len(res_data) == 0:
				res_data = [{"Response":'Not a Proper Response. Try Again!',
							"Ideal_Response":""}]
			
		except:
			pass
		cursor.close()
		return ({"attributes": {
	    				"status_desc": "Response Engine Details.",
	    				"status": "success"
	    				},
	    				"responseList":{"ResponseDtls":res_data}}), status.HTTP_200_OK

grammarcheck_post = api.model('Grammar Check', {
	"user_id":fields.Integer(required=True),
	"sentence":fields.String(required=True),
	"content_file":fields.String()})

@name_space.route("/checkGrammar")
class checkGrammar(Resource):
	@api.expect(grammarcheck_post)
	def post(self):
		last_update_ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
		# paralleldots.get_api_key()
		connection = mysql.connect()
		cur = connection.cursor()
		details = request.get_json()
		student_answer = details['sentence']
		parser = GingerIt()
		correct_words = []
		incorrect_words = []
		result = parser.parse(student_answer)['result']
		print(result)
		
		user_input_insert_query = ("""INSERT INTO `user_input`(`user_id`, `sentence`, 
			`content_file`) VALUES(%s,%s,%s)""")
		user_data = (details['user_id'],details['sentence'],details['content_file'])
		cur.execute(user_input_insert_query,user_data)
		input_id = cur.lastrowid
		for i in range(len(parser.parse(student_answer)['corrections'])):
			correct_words.append(parser.parse(student_answer)['corrections'][i]['correct'])
			incorrect_words.append(parser.parse(student_answer)['corrections'][i]['text'])
			grammar_insert_query = ("""INSERT INTO `error`(`user_ID`, `input_id`, `error_word`, 
				`correct_word`) VALUES(%s,%s,%s,%s)""")
			grammar_data = (details['user_id'],input_id,incorrect_words[i],correct_words[i])
			cur.execute(grammar_insert_query,grammar_data)
		connection.commit()
		cur.close()
		print(correct_words,incorrect_words)
		details['result'] = result
		details['correct_words'] = correct_words
		details['incorrect_words'] = incorrect_words
		return ({"attributes": {
	    				"status_desc": "Grammar Check Details.",
	    				"status": "success"
	    				},
	    				"responseList":{"GrammarDtls":details}}), status.HTTP_200_OK


semantic_post = api.model('Semantic Analysis', {
	"user_id":fields.Integer(required=True),
	"user_input":fields.String(required=True),
	"system_input":fields.String(required=True),
	"assessment_id":fields.Integer(required=True),
	"content_file":fields.String()})

@name_space.route("/sematicAnalysis")
class sematicAnalysis(Resource):
	@api.expect(semantic_post)
	def post(self):
		connection = mysql.connect()
		cursor = connection.cursor()
		details = request.get_json()
		user_id = details['user_id']
		user_input = details['user_input']
		system_input = details['system_input']
		content_file = details['content_file']
		url = 'https://api.dandelion.eu/datatxt/sim/v1'
		payload = {'text1': user_input,
					'text2': system_input,
					'token':'79a0da5e32c74648aea5eead09f7fd56'}
		response = requests.get(url, params=payload)
		
		res = json.loads(response.text)
		score = (res['similarity'])*100
		details['score'] = res
		semantic_insert_query = ("""INSERT INTO `semantic_analysis`(`user_id`, `user_input`, 
			`content_file`, `similarity_percentage`) VALUES(%s,%s,%s,%s)""")
		semantic_data = (user_id,user_input,content_file,score)
		cursor.execute(semantic_insert_query,semantic_data)
		connection.commit()
		cursor.close()
		return ({"attributes": {
	    				"status_desc": "Semantic Analysis Details.",
	    				"status": "success"
	    				},
	    				"responseList":{"SemanticDtls":details}}), status.HTTP_200_OK

if __name__ == '__main__':
	# app = Flask(__name__)
	# app.register_blueprint(text2speech, url_prefix = '/text2speech')
	app.run(host='0.0.0.0',debug=True)
