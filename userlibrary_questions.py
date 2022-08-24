import pymysql
import configparser
from flask import Flask, request, jsonify, json
from flask_api import status
from datetime import datetime,timedelta,date
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests

app = Flask(__name__)
cors = CORS(app)

user_library_questions = Blueprint('user_library_questionss_api', __name__)
api = Api(user_library_questions,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('questionsController',description='User Library')

update_ques_model = api.model('updateQuestion', {
   "Question": fields.String(),
   "Content_file_path":fields.String(),
   "Content_FileName":fields.String(),
   "File_Type_ID":fields.String(),
   "Last_Update_ID": fields.Integer()
})

update_options = api.model('options',{
	"Option_ID":fields.Integer(),
	"Option":fields.String(),
	"Content_file_path":fields.String(),
	"Content_FileName":fields.String(),
	"File_Type_ID":fields.String()
	})

update_opt_model = api.model('opt',{
	"options": fields.List(fields.Nested(update_options))
	})

update_answer = api.model('answer',{
	"Option_ID":fields.Integer()
	})

update_ans_model = api.model('ans',{
	"answer": fields.List(fields.Nested(update_answer))
	})



'''def connnect_userLibrary():
	connection = pymysql.connect(host='creamsonservices.com',
									user='creamson_langlab',
									password='Langlab@123',
									db='creamson_user_library',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor)
	return connection


def connect_logindb():
	connection = pymysql.connect(host='creamsonservices.com',
									user='creamson_langlab',
									password='Langlab@123',
									db='creamson_logindb',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor)
	return connection'''


def connnect_userLibrary():
	connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
									user='admin',
									password='cbdHoRPQPRfTdC0uSPLt',
									db='creamson_user_library',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor)
	return connection


def connect_logindb():
	connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
									user='admin',
									password='cbdHoRPQPRfTdC0uSPLt',
									db='creamson_logindb',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor)
	return connection


@name_space.route("/updateQuestionsByQuesID/<int:ques_id>")
class updateQuestionsByQuesID(Resource):
	@api.expect(update_ques_model)
	def put(self,ques_id):
		connection = connnect_userLibrary()
		cursor = connection.cursor()

		details = request.get_json()
		question = details.get('Question')
		content_file_path = details.get('Content_file_path')
		content_FileName = details.get('Content_FileName')
		file_Type_ID = details.get('File_Type_ID')
		login_id = details.get('Last_Update_ID')

		cursor.execute("""SELECT `Question_ID`,`Question`,`Content_file_path`,
			`Content_FileName`,`File_Type_ID`,`Last_Update_ID` FROM `question` 
			WHERE `Question_ID`=%s""",
			(ques_id))
		question_dtls = cursor.fetchone()
		
		if question_dtls:
        
			if not question:
			    question = question_dtls.get('Question')
			    
			if not content_file_path:
			    content_file_path = question_dtls.get('Content_file_path')
			    
			if not content_FileName:
			    content_FileName = question_dtls.get('Content_FileName')
			    
			if not file_Type_ID:
			    file_Type_ID = question_dtls.get('File_Type_ID')
			
			if not login_id:
			    login_id = question_dtls.get('Last_Update_ID')

		update_question_query = ("""UPDATE `question` SET `Question`=%s,
			`Content_file_path`=%s,`Content_FileName`=%s,`File_Type_ID`=%s,
			`Last_Update_ID`= %s WHERE Question_ID = %s""")
		ques_data = (question,content_file_path,content_FileName,file_Type_ID,
			login_id,ques_id)
		cursor.execute(update_question_query,ques_data)
		connection.commit()

		cursor.close()

		return ({"attributes": {"status_desc": "Question Update Details.",
		    				"status": "success"
		    				},
		    				"responseList":details}), status.HTTP_200_OK



@name_space.route("/updateOptionsByQuesID/<int:ques_id>")
class updateOptionsByQuesID(Resource):
	@api.expect(update_opt_model)
	def put(self,ques_id):
		connection = connnect_userLibrary()
		cursor = connection.cursor()

		details = request.get_json()
		optionsdtls = details['options']

		for op in range(len(optionsdtls)):
			option_id = optionsdtls[op].get('Option_ID')
			option = optionsdtls[op].get('Option')
			Content_file_path = optionsdtls[op].get('Content_file_path')
			Content_FileName = optionsdtls[op].get('Content_FileName')
			File_Type_ID = optionsdtls[op].get('File_Type_ID')

			cursor.execute("""SELECT `Option_ID`,`Option`,`Content_file_path`,
				`Content_FileName`,`File_Type_ID` FROM `options` WHERE `Question_ID`=%s 
				and `Option_ID`=%s""",(ques_id,option_id))
			option_dtls = cursor.fetchone()
			
			if option_dtls:
            
				if not option:
				    option = option_dtls.get('option')
				    
				if not Content_file_path:
				    Content_file_path = option_dtls.get('Content_file_path')
				    
				if not Content_FileName:
				    Content_FileName = option_dtls.get('Content_FileName')
				    
				if not File_Type_ID:
				    File_Type_ID = option_dtls.get('File_Type_ID')
				    
			update_option_query = ("""UPDATE `options` SET `Option`= %s,
				`Content_file_path`= %s,`Content_FileName`= %s,`File_Type_ID`= %s
				WHERE `Question_ID` = %s and `Option_ID` = %s""")
			option_data = (option,Content_file_path,Content_FileName,File_Type_ID,
				ques_id,option_id)
			cursor.execute(update_option_query,option_data)
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Option Update Details.",
		    				"status": "success"
		    				},
		    				"responseList":details}), status.HTTP_200_OK



@name_space.route("/updateAnswerByQuesID/<int:ques_id>")
class updateAnswerByQuesID(Resource):
	@api.expect(update_ans_model)
	def put(self,ques_id):
		connection = connnect_userLibrary()
		cursor = connection.cursor()

		details = request.get_json()
		answerdtls = details['answer']
		prevoptList = []
		cursor.execute("""SELECT `Option_ID` FROM `answer` WHERE `Question_ID` =%s""",
			(ques_id))
		answer = cursor.fetchall()
		for opid in range(len(answer)):
			optionid = answer[opid]['Option_ID']
			prevoptList.append(optionid)
			
		for ans in range(len(answerdtls)):
			option_id = answerdtls[ans]['Option_ID']
			
			update_answer_query = ("""UPDATE `answer` SET `Option_ID`= %s
								WHERE `Question_ID` = %s and `Option_ID`=%s""")
			answer_data = (option_id,ques_id,prevoptList[ans])
			
			cursor.execute(update_answer_query,answer_data)

		connection.commit()

		cursor.close()

		return ({"attributes": {"status_desc": "Answer Update Details.",
		    				"status": "success"
		    				},
		    				"responseList":details}), status.HTTP_200_OK



def deleteQueOptAns(QuestionId):
	connection = connnect_userLibrary()
	cursor = connection.cursor()
        
	try:
		delQue = ("""DELETE FROM `question` WHERE `Question_ID`=%s""")
		delQueData = (QuestionId)
		cursor.execute(delQue,delQueData)

		delOption = ("""DELETE FROM `options` WHERE `Question_ID`=%s""")
		delOptionData = (QuestionId)
		cursor.execute(delOption,delOptionData)

		delAnswer = ("""DELETE FROM `answer` WHERE `Question_ID`=%s""")
		delAnswerData = (QuestionId)
		cursor.execute(delAnswer,delAnswerData)

		delMap = ("""DELETE FROM `assessment_question_mapping` WHERE `Question_ID` = %s""")
		cursor.execute(delMap,(QuestionId))
		
		connection.commit()
		cursor.close()
		
	except Exception as e:
		return e

	return 'updated'

@name_space.route("/deleteQuestionOptionAnswerByQuestionId/<int:QuestionId>")
class deleteQuestionOptionAnswerByQuestionId(Resource):
	def put(self,QuestionId):
		connection = connnect_userLibrary()
		cursor = connection.cursor()
		res = 'Question Removed.'
     
		cursor.execute("""SELECT * FROM `question` WHERE `Question_ID`=%s""",(QuestionId))
		questionDtls = cursor.fetchall()

		cursor.execute("""SELECT * FROM `options` WHERE `Question_ID`=%s""",(QuestionId))
		optionDtls = cursor.fetchall()

		cursor.execute("""SELECT * FROM `answer` WHERE `Question_ID`=%s""",(QuestionId))
		answerDtls = cursor.fetchall()

		if questionDtls or optionDtls or answerDtls:
			delRes = deleteQueOptAns(QuestionId)
				
			if delRes == 'updated':
				res = 'Question Removed.'
		else:
			[]
		cursor.close()

		return ({"attributes": {"status_desc": "Question Details.",
									"status": "success"
									},
					"responseList": res}), status.HTTP_200_OK




@name_space.route("/deleteQuestionOptionByQuestionId/<int:QuestionId>")
class deleteQuestionOptionByQuestionId(Resource):
	def put(self,QuestionId):
		connection = connnect_userLibrary()
		cursor = connection.cursor()
		res = 'Question Removed.'
        
		cursor.execute("""SELECT * FROM `question` WHERE `Question_ID`=%s""",(QuestionId))
		questionDtls = cursor.fetchall()

		cursor.execute("""SELECT * FROM `options` WHERE `Question_ID`=%s""",(QuestionId))
		optionDtls = cursor.fetchall()

		cursor.execute("""SELECT * FROM `answer` WHERE `Question_ID`=%s""",(QuestionId))
		answerDtls = cursor.fetchall()

		if questionDtls or optionDtls or answerDtls:
			que = "http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/userlibrary_questions/questionsController/deleteQuestionByQuestionId/{}".format(QuestionId)
			opt = "http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/userlibrary_questions/questionsController/deleteOptionByQuestionId/{}".format(QuestionId)
			ans = "http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/userlibrary_questions/questionsController/deleteAnswerByQuestionId/{}".format(QuestionId)
			headers = {'Content-type':'application/json', 'Accept':'application/json'}

			delque = requests.put(que, headers=headers)
			rque = delque.json()
			delopt = requests.put(opt, headers=headers)
			ropt = delopt.json()
			delans = requests.put(ans, headers=headers)
			rans = delans.json()

			if delque and delopt and delans == 'updated':
				res = 'Question Removed.'
		else:
			[]
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Question Details.",
									"status": "success"
									},
					"responseList": res}), status.HTTP_200_OK



def deleteQue(QuestionId):
	connection = connnect_userLibrary()
	cursor = connection.cursor()
        
	try:
		delQue = ("""DELETE FROM `question` WHERE `Question_ID`=%s""")
		delQueData = (QuestionId)
		cursor.execute(delQue,delQueData)
		
		connection.commit()
		cursor.close()
		
	except Exception as e:
		return e

	return 'updated'

@name_space.route("/deleteQuestionByQuestionId/<int:QuestionId>")
class deleteQuestionByQuestionId(Resource):
	def put(self,QuestionId):
		connection = connnect_userLibrary()
		cursor = connection.cursor()
		res = 'Question Removed.'
     
		cursor.execute("""SELECT * FROM `question` WHERE `Question_ID`=%s""",(QuestionId))
		questionDtls = cursor.fetchall()

		if questionDtls:
			delRes = deleteQue(QuestionId)
				
			if delRes == 'updated':
				res = 'Question Removed.'
		else:
			[]
		cursor.close()

		return ({"attributes": {"status_desc": "Question Details.",
									"status": "success"
									},
					"responseList": res}), status.HTTP_200_OK



def deleteOpt(QuestionId):
	connection = connnect_userLibrary()
	cursor = connection.cursor()
        
	try:
		delOption = ("""DELETE FROM `options` WHERE `Question_ID`=%s""")
		delOptionData = (QuestionId)
		
		cursor.execute(delOption,delOptionData)

		connection.commit()
		cursor.close()
		
	except Exception as e:
		return e

	return 'updated'

@name_space.route("/deleteOptionByQuestionId/<int:QuestionId>")
class deleteOptionByQuestionId(Resource):
	def put(self,QuestionId):
		connection = connnect_userLibrary()
		cursor = connection.cursor()
		res = 'Option Removed.'
     
		cursor.execute("""SELECT * FROM `options` WHERE `Question_ID`=%s""",(QuestionId))
		optionDtls = cursor.fetchall()

		if optionDtls:
			delRes = deleteOpt(QuestionId)
				
			if delRes == 'updated':
				res = 'Option Removed.'
		else:
			[]
		cursor.close()

		return ({"attributes": {"status_desc": "Option Details.",
									"status": "success"
									},
					"responseList": res}), status.HTTP_200_OK


def deleteAns(QuestionId):
	connection = connnect_userLibrary()
	cursor = connection.cursor()
        
	try:
		delAnswer = ("""DELETE FROM `answer` WHERE `Question_ID`=%s""")
		delAnswerData = (QuestionId)
		cursor.execute(delAnswer,delAnswerData)

		connection.commit()
		cursor.close()
		
	except Exception as e:
		return e

	return 'updated'

@name_space.route("/deleteAnswerByQuestionId/<int:QuestionId>")
class deleteAnswerByQuestionId(Resource):
	def put(self,QuestionId):
		connection = connnect_userLibrary()
		cursor = connection.cursor()
		res = 'Answer Removed.'
     
		cursor.execute("""SELECT * FROM `answer` WHERE `Question_ID`=%s""",(QuestionId))
		answerDtls = cursor.fetchall()

		if answerDtls:
			delRes = deleteAns(QuestionId)
				
			if delRes == 'updated':
				res = 'Answer Removed.'
		else:
			[]
		cursor.close()

		return ({"attributes": {"status_desc": "Answer Details.",
									"status": "success"
									},
					"responseList": res}), status.HTTP_200_OK