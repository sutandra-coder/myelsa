from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
import datetime
# from datetime import datetime
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests

app = Flask(__name__)
cors = CORS(app)
mysql = MySQL()
cur_pre_portal = Blueprint('cur_pre_portal_api', __name__)
api = Api(cur_pre_portal, version='1.0', title='MyElsa API',
    description='MyElsa API')
name_space = api.namespace('CurriculumPreviewPortal', description='Curriculum Preview Portal')

app.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app.config['MYSQL_DATABASE_DB'] = 'creamson_lab_lang1'
app.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'
mysql.init_app(app)
connection = mysql.connect()

update_options = api.model('options', 
						{"option_id":fields.Integer(),
						"option":fields.String()})

update_ques_model = api.model('updateQuestion', {
   "question": fields.String(),
   "last_update_id": fields.Integer(),
   "options": fields.List(fields.Nested(update_options)),
   "answer": fields.Integer(),
   "passage_id": fields.Integer(),
   "pass_desc": fields.String(),
   "full_passage": fields.String()
})

@name_space.route("/getActivity")
class getActivity(Resource):
	def get(self):
		connection = mysql.connect()
		cursor = connection.cursor()

		cursor.execute("""SELECT `Activity_ID`,`Activity_Category_Id`,`Activity_Desc`,
			`Activity_Image_URL` FROM `activity` where `Activity_ID`>32 and 
			`Activity_ID`<36""")


		get_activities = cursor.fetchall()
		if get_activities:
			desc = cursor.description
			col_names = [col[0] for col in desc]
			activity_details = [dict(izip(col_names, row)) for row in get_activities]

		else:
			activity_details = []
		cursor.close()
		return ({"attributes": {"status_desc": "Activity Details.",
		    				"status": "success"
		    				},
		    	"responseList":activity_details}), status.HTTP_200_OK


@name_space.route("/getQuestionsByLastID/<int:last_id>")
class getQuestionsByLastID(Resource):
	def get(self,last_id):
		connection = mysql.connect()
		cursor = connection.cursor()

		cursor.execute("""SELECT q.`Question_ID`,q.`Question`,
			(select op1.`option` from options op1 where op1.`option_ID` = ans.`Option_ID`) answer,
			cm.`Content_Master_Name`, ast.`Assessment_Type_Desc`,cr.`Class`,bo.`Board_Desc`,
			q.`Question_Addition_TS`, q.`passage_id`,q.`Last_Update_ID` FROM `question` q, `content_master` cm, `content_rule` cr, 
			`board` bo, `assessment_type` ast, `options` op, answer ans 
			WHERE q.`Last_Update_ID` = %s and q.`Content_Master_ID`=cm.`Content_Master_ID` 
			and q.`Content_Master_ID` = cr.`Content_Master_ID` and cr.`Board_ID` = bo.`Board_ID` 
			and q.`Question_Type` = ast.`Assessment_Type_ID` and q.`Question_ID` = op.`Question_ID` 
			and ans.`Question_ID` = q.`Question_ID` GROUP by q.`Question_ID`""",(last_id))


		get_questions = cursor.fetchall()
		if get_questions:
			desc = cursor.description
			col_names = [col[0] for col in desc]
			questions_details = [dict(izip(col_names, row)) for row in get_questions]


			for i in range(len(questions_details)):
				cursor.execute("""SELECT `Option_ID`, `Question_ID`, `Option`, `Option_Sequence_ID`, 
					`Content_file_path`, `Content_FileName`, `File_Type_ID` 
					FROM `options` WHERE `Question_ID` = %s""",(questions_details[i]['Question_ID']))
				options = cursor.fetchall()
				if options:
					op_desc = cursor.description
					op_col_names = [col[0] for col in op_desc]
					option_details = [dict(izip(op_col_names, row)) for row in options]
				# print(option_details)
				questions_details[i]['Question_Addition_TS'] = questions_details[i]['Question_Addition_TS'].isoformat()

				questions_details[i]['options'] = option_details

				cursor.execute("""SELECT `passage_desc`, `content_file_path`, 
					`content_master_id` FROM `passage_dtl` 
					WHERE `passage_id` = %s""",(questions_details[i]['passage_id']))
				passage = cursor.fetchall()
				if passage:
					pass_desc = passage[0][0]
					full_passage = passage[0][1]
					
					questions_details[i]['passage_description'] = pass_desc
					questions_details[i]['passage'] = full_passage
				else:
					questions_details[i]['passage_description'] = ''
					questions_details[i]['passage'] = ''


		else:
			questions_details = []
		cursor.close()
		return ({"attributes": {"status_desc": "Question Details.",
		    				"status": "success"
		    				},
		    				"responseList":questions_details}), status.HTTP_200_OK


@name_space.route("/getQuestionsByBoardID/<int:board_id>")
class getQuestionsByLastID(Resource):
	def get(self,board_id):
		connection = mysql.connect()
		cursor = connection.cursor()

		cursor.execute("""SELECT q.`Question_ID`,q.`Question`,
			(select op1.`option` from options op1 where op1.`option_ID` = ans.`Option_ID`) answer,
			cm.`Content_Master_Name`, ast.`Assessment_Type_Desc`,cr.`Class`,bo.`Board_Desc`,
			q.`Question_Addition_TS`, q.`passage_id`,q.`Last_Update_ID` FROM `question` q, `content_master` cm, `content_rule` cr, 
			`board` bo, `assessment_type` ast, `options` op, answer ans 
			WHERE bo.`board_id` = %s and q.`Content_Master_ID`=cm.`Content_Master_ID` 
			and q.`Content_Master_ID` = cr.`Content_Master_ID` and cr.`Board_ID` = bo.`Board_ID` 
			and q.`Question_Type` = ast.`Assessment_Type_ID` and q.`Question_ID` = op.`Question_ID` 
			and ans.`Question_ID` = q.`Question_ID` GROUP by q.`Question_ID`""",(board_id))


		get_questions = cursor.fetchall()
		if get_questions:
			desc = cursor.description
			col_names = [col[0] for col in desc]
			questions_details = [dict(izip(col_names, row)) for row in get_questions]

			for i in range(len(questions_details)):
				print(type(questions_details[i]['Question_Addition_TS']))
				print(isinstance(questions_details[i]['Question_Addition_TS'], datetime.datetime))
				if not isinstance(questions_details[i]['Question_Addition_TS'], datetime.datetime):
					pass
				else:
					questions_details[i]['Question_Addition_TS'] = questions_details[i]['Question_Addition_TS'].isoformat()
				cursor.execute("""SELECT `Option_ID`, `Question_ID`, `Option`, `Option_Sequence_ID`, 
					`Content_file_path`, `Content_FileName`, `File_Type_ID` 
					FROM `options` WHERE `Question_ID` = %s""",(questions_details[i]['Question_ID']))
				options = cursor.fetchall()
				if options:
					op_desc = cursor.description
					op_col_names = [col[0] for col in op_desc]
					option_details = [dict(izip(op_col_names, row)) for row in options]

				questions_details[i]['options'] = option_details

				cursor.execute("""SELECT `passage_desc`, `content_file_path`, 
					`content_master_id` FROM `passage_dtl` 
					WHERE `passage_id` = %s""",(questions_details[i]['passage_id']))
				passage = cursor.fetchall()
				if passage:
					pass_desc = passage[0][0]
					full_passage = passage[0][1]
					
					questions_details[i]['passage_description'] = pass_desc
					questions_details[i]['passage'] = full_passage
				else:
					questions_details[i]['passage_description'] = ''
					questions_details[i]['passage'] = ''
		else:
			questions_details = []
		cursor.close()			
		return ({"attributes": {"status_desc": "Question Details.",
		    				"status": "success"
		    				},
		    				"responseList":questions_details}), status.HTTP_200_OK


@name_space.route("/updateQuestionsByQuesID/<int:ques_id>")
class updateQuestionsByQuesID(Resource):
	@api.expect(update_ques_model)
	def put(self,ques_id):
		details = request.get_json()
		connection = mysql.connect()
		cursor = connection.cursor()
		question = details['question']
		login_id = details['last_update_id']
		answer = details['answer']
		optionsdtls = details['options']
		passage_id = details['passage_id']
		pass_desc = details['pass_desc']
		full_passage = details['full_passage']
		update_question_query = ("""UPDATE question SET Question = %s, `Last_Update_ID` = %s 
								WHERE Question_ID = %s""")
		ques_data = (question,login_id,ques_id)
		cursor.execute(update_question_query,ques_data)

		for op in range(len(optionsdtls)):
			option_id = optionsdtls[op]['option_id']
			option = optionsdtls[op]['option']
			update_option_query = ("""UPDATE `options` SET `Option`= %s 
										WHERE `Question_ID` = %s and `Option_ID` = %s""")
			option_data = (option,ques_id,option_id)
			cursor.execute(update_option_query,option_data)

		update_answer_query = ("""UPDATE `answer` SET `Option_ID`= %s
								WHERE `Question_ID` = %s""")
		answer_data = (answer,ques_id)

		cursor.execute(update_answer_query,answer_data)
		update_passage_query = ("""UPDATE passage_dtl SET passage_desc= %s, content_file_path= %s 
			WHERE passage_id = %s""")
		pass_data = (pass_desc, full_passage,passage_id)
		cursor.execute(update_passage_query, pass_data)
		connection.commit()

		cursor.close()

		return ({"attributes": {"status_desc": "Question Update Details.",
		    				"status": "success"
		    				},
		    				"responseList":details}), status.HTTP_200_OK


@name_space.route("/getQuestionsByQuesID/<int:ques_id>")
class getQuestionsByLastID(Resource):
	def get(self,ques_id):
		connection = mysql.connect()
		cursor = connection.cursor()

		cursor.execute("""SELECT q.`Question_ID`,q.`Question`,
			(select op1.`option` from options op1 where op1.`option_ID` = ans.`Option_ID`) answer,
			cm.`Content_Master_Name`, ast.`Assessment_Type_Desc`,cr.`Class`,bo.`Board_Desc`,
			q.`Question_Addition_TS`, q.`passage_id`,q.`Last_Update_ID` FROM `question` q, `content_master` cm, `content_rule` cr, 
			`board` bo, `assessment_type` ast, `options` op, answer ans 
			WHERE q.`Question_ID` = %s and q.`Content_Master_ID`=cm.`Content_Master_ID` 
			and q.`Content_Master_ID` = cr.`Content_Master_ID` and cr.`Board_ID` = bo.`Board_ID` 
			and q.`Question_Type` = ast.`Assessment_Type_ID` and q.`Question_ID` = op.`Question_ID` 
			and ans.`Question_ID` = q.`Question_ID` GROUP by q.`Question_ID`""",(ques_id))


		get_questions = cursor.fetchall()
		if get_questions:
			desc = cursor.description
			col_names = [col[0] for col in desc]
			questions_details = [dict(izip(col_names, row)) for row in get_questions]


			for i in range(len(questions_details)):
				cursor.execute("""SELECT `Option_ID`, `Question_ID`, `Option`, `Option_Sequence_ID`, 
					`Content_file_path`, `Content_FileName`, `File_Type_ID` 
					FROM `options` WHERE `Question_ID` = %s""",(questions_details[i]['Question_ID']))
				options = cursor.fetchall()
				if options:
					op_desc = cursor.description
					op_col_names = [col[0] for col in op_desc]
					option_details = [dict(izip(op_col_names, row)) for row in options]
				# print(option_details)
				questions_details[i]['Question_Addition_TS'] = questions_details[i]['Question_Addition_TS'].isoformat()

				questions_details[i]['options'] = option_details

				cursor.execute("""SELECT `passage_desc`, `content_file_path`, 
					`content_master_id` FROM `passage_dtl` 
					WHERE `passage_id` = %s""",(questions_details[i]['passage_id']))
				passage = cursor.fetchall()
				if passage:
					pass_desc = passage[0][0]
					full_passage = passage[0][1]
					
					questions_details[i]['passage_description'] = pass_desc
					questions_details[i]['passage'] = full_passage
				else:
					questions_details[i]['passage_description'] = ''
					questions_details[i]['passage'] = ''


		else:
			questions_details = []
		cursor.close()
		return ({"attributes": {"status_desc": "Question Details.",
		    				"status": "success"
		    				},
		    				"responseList":questions_details[0]}), status.HTTP_200_OK
		
@name_space.route("/getQuestionsByBoardID/<int:board_id>/<string:Classes>/<int:Content_master_Id>/<int:Activity_Mapping_ID>/<int:Last_Update_ID>")
class getQuestionsByLastID(Resource):
	def get(self,board_id,Classes,Content_master_Id,Activity_Mapping_ID,Last_Update_ID):
		connection = mysql.connect()
		cursor = connection.cursor()
		print(Classes)
		cursor.execute("""SELECT q.`Question_ID`,q.`Question`,
            (select op1.`option` from `options` op1 where op1.`option_ID` = ans.`Option_ID`) answer,
            cm.`Content_Master_Name`, ast.`Assessment_Type_Desc`,cr.`Class`,bo.`Board_Desc`,
            q.`Question_Addition_TS`, q.`passage_id`,q.`Last_Update_ID` FROM `question` q, `content_master` cm, `content_rule` cr,
            `board` bo, `assessment_type` ast, `options` op, `answer` ans
            WHERE bo.`board_id` = %s and locate(%s,cr.`Class`) and cm.`Content_master_Id`=%s and cr.`Activity_Mapping_ID`=%s and q.`Last_Update_ID`=%s
           and q.`Content_Master_ID`=cm.`Content_Master_ID`
            and q.`Content_Master_ID` = cr.`Content_Master_ID` and cr.`Board_ID` = bo.`Board_ID`
            and q.`Question_Type` = ast.`Assessment_Type_ID` and q.`Question_ID` = op.`Question_ID`
            and ans.`Question_ID` = q.`Question_ID` GROUP by q.`Question_ID`""",(board_id,Classes,Content_master_Id,Activity_Mapping_ID,Last_Update_ID))


		get_questions = cursor.fetchall()
		# print(get_questions)
		if get_questions:
			desc = cursor.description
			col_names = [col[0] for col in desc]
			questions_details = [dict(izip(col_names, row)) for row in get_questions]

			for i in range(len(questions_details)):
				print(type(questions_details[i]['Question_Addition_TS']))
				print(isinstance(questions_details[i]['Question_Addition_TS'], datetime.datetime))
				if not isinstance(questions_details[i]['Question_Addition_TS'], datetime.datetime):
					pass
				else:
					questions_details[i]['Question_Addition_TS'] = questions_details[i]['Question_Addition_TS'].isoformat()
				cursor.execute("""SELECT `Option_ID`, `Question_ID`, `Option`, `Option_Sequence_ID`, 
					`Content_file_path`, `Content_FileName`, `File_Type_ID` 
					FROM `options` WHERE `Question_ID` = %s""",(questions_details[i]['Question_ID']))
				options = cursor.fetchall()
				if options:
					op_desc = cursor.description
					op_col_names = [col[0] for col in op_desc]
					option_details = [dict(izip(op_col_names, row)) for row in options]

				questions_details[i]['options'] = option_details

				cursor.execute("""SELECT `passage_desc`, `content_file_path`, 
					`content_master_id` FROM `passage_dtl` 
					WHERE `passage_id` = %s""",(questions_details[i]['passage_id']))
				passage = cursor.fetchall()
				if passage:
					pass_desc = passage[0][0]
					full_passage = passage[0][1]
					
					questions_details[i]['passage_description'] = pass_desc
					questions_details[i]['passage'] = full_passage
				else:
					questions_details[i]['passage_description'] = ''
					questions_details[i]['passage'] = ''
		else:
			questions_details = []
		cursor.close()			
		return ({"attributes": {"status_desc": "Question Details.",
		    				"status": "success"
		    				},
		    				"responseList":questions_details}), status.HTTP_200_OK

@name_space.route("/getPassagedtls/<int:Content_master_Id>")
class getPassagedtls(Resource):
	def get(self,Content_master_Id):
		connection = mysql.connect()
		cursor = connection.cursor()

		cursor.execute("""SELECT `passage_id`,`passage_desc`,`content_file_path` as passage,`content_master_id` FROM `passage_dtl` where `content_master_id`= %s""",(Content_master_Id))
		get_passages = cursor.fetchall()
		print(get_passages)
		if get_passages:
			desc = cursor.description
			print(desc)
			col_names = [col[0] for col in desc]
			pass_details = [dict(izip(col_names, row)) for row in get_passages]
			print(pass_details)

		else:
			pass_details = []
		cursor.close()
		return ({"attributes": {"status_desc": "Passage Details.",
		    				"status": "success"
		    				},
		    				"responseList":pass_details}), status.HTTP_200_OK


if __name__ == '__main__':
	app.run(host='0.0.0.0',debug=True)