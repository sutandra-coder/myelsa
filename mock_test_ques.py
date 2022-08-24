from flask import Flask, request, jsonify, json,render_template,make_response
# from flask_weasyprint import HTML, render_pdf
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests,os
import pymysql
app = Flask(__name__)
cors = CORS(app)
mysql = MySQL()
app1 = Flask(__name__)
mysql1 = MySQL()
UPLOAD_FOLDER = '/home/ubuntu/tally/uploadfolder'
SERVER_PATH = 'http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com/tally/uploadfolder/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mock_ques = Blueprint('mock_ques_api', __name__)
api = Api(mock_ques, version='1.0', title='MyElsa API',
    description='MyElsa API')
name_space = api.namespace('MockTestQuestions', description=':Mock Test Questions')

app.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app.config['MYSQL_DATABASE_DB'] = 'creamson_lab_lang1'
app.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'
mysql.init_app(app)


app1.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app1.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app1.config['MYSQL_DATABASE_DB'] = 'creamson_logindb'
app1.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'
mysql1.init_app(app1)

def mysql_connection_lab_lang():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='creamson_lab_lang1',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

def mysql_connection_logindb():
	connection = pymysql.connect(host='creamsonservices.com',
									user='creamson_langlab',
									password='Langlab@123',
									db='creamson_logindb',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor)
	return connection

app.config['CORS_HEADERS'] = 'Content-Type'

content_fields = api.model('content_id', {"content_master_id":fields.Integer})
# content_list_fields = {
#     fields.List(fields.Nested(content_fields)),
# }

activity_dtls = api.model('activity_dlts', {"activity_id":fields.Integer,
					"content_master_id":fields.List(fields.Nested(content_fields))})

mocktest_model = api.model('Mock Test', {
	"user_id":fields.Integer(required=True),
	"user_class":fields.Integer(required=True),
	"board_desc":fields.String(required=True),
	"activity_dtls":fields.List(fields.Nested(activity_dtls))
	})

assgin_model = api.model('Assign Mock Test', {
	"teacher_id":fields.Integer(required=True),
	"download_id":fields.Integer(required=True),
	"group_id":fields.List(fields.Integer()),
	"student_id":fields.List(fields.Integer()),
	"is_group":fields.String(required=True)
	})

addmarks = api.model('addmarks', {
	"question_id":fields.Integer(required=True),
	"marks":fields.Integer(required=True),
	"remarks":fields.String(),
	})

submit_marks = api.model('Submit Marks', {
	"marks_details":fields.List(fields.Nested(addmarks))
	})


feedback = api.model('Mock Test Feedback', {
	"feedback":fields.String(required=True),
	"additional_feedback":fields.String()
	})

answer_details = api.model('answer_details', {
	"question_id":fields.Integer(required=True),
	"option_id":fields.Integer(),
	"answer":fields.String(),
	"answer_filepath":fields.String(),
	"filetype":fields.String()
	})

submit_answers = api.model('Submit Answers', {
	"answer_details":fields.List(fields.Nested(answer_details)),
	"status":fields.String(required=True)
	})

assgin_model_update = api.model('Assign Mock Test Update', {
	"group_id":fields.List(fields.Integer()),
	"student_id":fields.List(fields.Integer()),
	"is_group":fields.String(required=True)
	})
assign_individual = api.model('Assign Individual Mock Test', {
	"teacher_id":fields.Integer(required=True),
	"download_id":fields.Integer(required=True),
	"student_id":fields.Integer(),
	})
create_mock = api.model('Mock Test Model', {
	"teacher_id":fields.Integer(required=True),
	"includeAsnwerFlag":fields.Integer(),
	"activity_dtls":fields.List(fields.Nested(activity_dtls))
	})

assign_and_create = api.model('Assign And Create', {
	"assignDtls":fields.Nested(assgin_model_update),
	"createDtls":fields.Nested(create_mock),
	"personalizedFlag":fields.Integer()
	})

def getboard(board_desc):
	connection = mysql.connect()
	cursor = connection.cursor()
	desc = board_desc
	cursor.execute("""SELECT `Board_ID` FROM `board` WHERE `Board_Desc` = %s""",(desc))
	board = cursor.fetchone()
	if board:
		board = board[0]
	return board

def getmockID(board,user_class,includeAsnwerFlag):
	connection = mysql.connect()
	cursor = connection.cursor()
	cursor.execute("""SELECT `Mock_ID`,`Template_path` FROM `mock_tbl`  
		WHERE `Board_Id` = %s and `Class` = %s""",(board,user_class))
	mock_id = cursor.fetchone()
	if mock_id:
		mock_idx = mock_id[0]
		template_path = mock_id[1]
		if includeAsnwerFlag == 1: 
			cursor.execute("""SELECT `template_path` FROM `mocktest_templates` 
				WHERE `mock_id` = %s and `answer_filter` = %s""",(mock_idx,includeAsnwerFlag))
			tempDtls = cursor.fetchone()
			if tempDtls:
				template_path = tempDtls[0]
	return mock_idx,template_path

def getAssessmemtTypes(activity_id,mock_id):
	connection = mysql.connect()
	cursor = connection.cursor()
	assessment_dtls = []
	try:
		cursor.execute("""SELECT `Activity_Mapping_ID` FROM `activity_mapping` 
			WHERE `Activity_ID` = %s""",(activity_id))
		activity_mapping_id = cursor.fetchone()
		if activity_mapping_id:
			activity_mapping_id = activity_mapping_id[0]
		cursor.execute("""SELECT `Assessment_Type_Id`,`No.Question`,`Marks`,`passage_flag`, `Last_Id`,`Master_Desc`
			FROM `mock_master_copy` WHERE `Activity_mapping_Id` = %s 
			and `Mock_ID` = %s""",(activity_mapping_id,mock_id))
		assessment_dtls = cursor.fetchall()
	except:
		pass
	print(assessment_dtls)
	return assessment_dtls


# def getAssessmemts(assessment_type_id,noofques,activity_mapping_id):
# 	connection = mysql.connect()
# 	cursor = connection.cursor()
# 	assessment_dtls = []
# 	try:
# 		cursor.execute("""SELECT `Assessment_ID`,`Assesment_Desc`,`Content_File_Path`,
# 			`Content_FileName`,`FileType_Id`,`Assessment_Status` FROM `assessment` 
# 			WHERE `Assessment_Type_ID` = %s and `Activity_Mapping_ID` = %s 
# 			order by rand() limit %s""",(assessment_type_id,activity_mapping_id,noofques))
# 		assessment_dtls = cursor.fetchall()
# 	except:
# 		pass
	
# 	return assessment_dtls


def getquestions(question_type,noofques,content_master_id,passage_id,user_id):
	content_master_id = tuple(content_master_id)
	print(question_type,noofques,content_master_id,passage_id,user_id)
	connection = mysql.connect()
	cursor = connection.cursor()
	question_details = []
	try:
		if passage_id != 0:
			cursor.execute("""SELECT `Question_ID`, `Question`, `Content_file_path`, `Content_FileName`, `File_Type_ID`,  `Content_master_Id` 
				FROM `question` WHERE `Question_Type` = %s and `Content_master_Id` in %s and passage_id = %s
				order by rand() LIMIT %s""",(question_type,content_master_id,passage_id,int(noofques)))
			details = cursor.fetchall()
			if details:
				desc = cursor.description
				column_names = [col[0] for col in desc]
				question_details = [dict(izip(column_names, row)) for row in details]
		else:
			cursor.execute("""SELECT `Question_ID`, `Question`, `Content_file_path`, `Content_FileName`, `File_Type_ID`,  `Content_master_Id` 
				FROM `question` WHERE `Question_Type` = %s and `Content_master_Id` in %s and passage_id = 0
				order by rand() LIMIT %s""",(question_type,content_master_id,int(noofques)))
			details = cursor.fetchall()
			if details:
				desc = cursor.description
				column_names = [col[0] for col in desc]
				question_details = [dict(izip(column_names, row)) for row in details]
	except Exception as e:
		print(e)
	# if question_details:
	# 	for i, qid in enumerate(question_details):
	# 		history_insert_query = ("""INSERT INTO `mock_test_question_history`
	# 			(`user_id`, `question_id`) VALUES (%s,%s)""")
	# 		history_data = (user_id,question_details[i]['Question_ID'])
	# 		cursor.execute(history_insert_query,history_data)
	# connection.commit()
	cursor.close()
	return question_details

def getoptions(question_id):
	connection = mysql.connect()
	cursor = connection.cursor()
	option_details = []
	try:
		cursor.execute("""SELECT `Option_ID`, `Option`, `Option_Sequence_ID`, `Content_file_path`, 
			`Content_FileName`,`File_Type_ID` FROM `options` WHERE `Question_ID` = %s""",(question_id))
		desc = cursor.description
		column_names = [col[0] for col in desc]
		option_details = [dict(izip(column_names, row)) for row in cursor.fetchall()]
	except:
		pass
	return option_details


def getanswer(question_id):
	connection = mysql.connect()
	cursor = connection.cursor()
	answer_details = []
	try:
		cursor.execute("""SELECT o.`Option` as answer, a.`Additional_Text`,a.`Option_ID`, a.`Question_ID`
			FROM `options` o, `answer` a WHERE o.`Option_ID` = a.`Option_ID` 
			and a.`Question_ID` = %s""",(question_id))
		desc = cursor.description
		column_names = [col[0] for col in desc]
		answer_details = [dict(izip(column_names, row)) for row in cursor.fetchall()]
	except:
		pass
	return answer_details

def mockqueshist(out_json):
	connection = mysql.connect()
	cursor = connection.cursor()
	u_id = out_json['user_id']
	abs_html_path=out_json['html_filepath']
	dw_id = out_json['download_id']
	if dw_id != 0:
		for a in out_json['activity_dtls']:
			actv_id = a['activity_id']
			for ass in a['assessments']:
				passage_id = ass['passage_id']
				for q in ass['question_details']:
					questions = q['questions']
					assessment_type_id = q['question_type']
					if questions:
						for ques in q['questions']:
							marks = ques['mark']
							con_master_id = ques['Content_master_Id']
							que_id = ques['Question_ID']
							history_insert_query = ("""INSERT INTO `mock_test_question_history` (`user_id`,
								`activity_id`, `content_master_id`, `assessment_type_id`,`passage_id`, `question_id`,
								`download_id`,`marks`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""")
							history_data = (u_id,actv_id,con_master_id,assessment_type_id,
								passage_id,que_id,dw_id,marks)
							cursor.execute(history_insert_query, history_data)
					else:
						con_master_id = None
						que_id = None
						history_insert_query = ("""INSERT INTO `mock_test_question_history` (`user_id`,
							`activity_id`, `content_master_id`,`assessment_type_id`,
							`passage_id`, `question_id`,`download_id`) 
							VALUES (%s,%s,%s,%s,%s,%s,%s)""")
						history_data = (u_id,actv_id,con_master_id,assessment_type_id,
							passage_id,que_id,dw_id)
						cursor.execute(history_insert_query, history_data)

	connection.commit()
	cursor.close()

@name_space.route("/getMockTest")
class getMockTest(Resource):
	@api.expect(mocktest_model)
	def post(self):
		details = request.get_json()
		connection = mysql.connect()
		cursor = connection.cursor()
		conn = mysql1.connect()
		cur = conn.cursor()
		out_json = {}
		user_id = details['user_id']
		user_class = details['user_class']
		board_desc = details['board_desc']
		activity_dtls = details['activity_dtls']
		out_json['user_id'] = user_id
		out_json['activity_dtls'] = []
		dw_id = 0
		board = getboard(board_desc)
		includeAsnwerFlag = details.get('includeAsnwerFlag',0)
		mock_id,template_path = getmockID(board,user_class,includeAsnwerFlag)
		template_name = template_path.split('/')[-1]
		pid = 0
		for i in range(len(activity_dtls)):
			activity_id = activity_dtls[i]['activity_id']
			cursor.execute("""SELECT `Activity_Desc` FROM `activity` 
				WHERE `Activity_ID` = %s""",(activity_id))

			activity_desc = cursor.fetchone()

			if activity_desc:
				activity_desc = activity_desc[0]

			out_json['activity_dtls'].append({'activity_id':activity_id,
												'activity_desc':activity_desc,
												'assessments':[]})

			content_id = activity_dtls[i]['content_master_id']
			content_master_id = []
			for con in content_id:
				content_master_id.append(con['content_master_id'])
			# print(content_master_id)
			assessment_dtls = getAssessmemtTypes(activity_id,mock_id)
			flag = 0
			
			for e,a in enumerate(assessment_dtls):
				question_type = a[0].split(',')
				noofques = a[1].split(',')
				ques_marks = a[2].split(',')
				assess_desc = a[5].split('|')
				marks_of_each_ques = 0
				# print(pid)
				# print(question_type)
				# print(noofques)
				if a[3] == 1:
					is_passage = 'Y'
					content_master_id = tuple(content_master_id)

					if len(content_master_id) == 1:
						cursor.execute("""SELECT `passage_id`, `passage_desc`, `content_file_path` 
							FROM `passage_dtl` WHERE `content_master_id` = %s and `passage_id` != %s
							order by rand() LIMIT 1""",(content_master_id[0],pid))
					else:
						# print(content_master_id)
						cursor.execute("""SELECT `passage_id`, `passage_desc`, `content_file_path` 
							FROM `passage_dtl` WHERE `content_master_id` in %s and `passage_id` != %s
							order by rand() LIMIT 1""",(content_master_id,pid))

					passage_dtl = cursor.fetchone()
					if passage_dtl:
						passage_id = passage_dtl[0]
						# print(passage_id)
						passage_desc = passage_dtl[1]
						full_passage = passage_dtl[2]
						pid = passage_id
					out_json['activity_dtls'][i]['assessments'].append({"is_passage":is_passage,
																			"passage_id":passage_id,
																			"passage_desc":passage_desc,
																			"passage":full_passage,
																			"question_details":[]})
				else:
					is_passage = 'N'
					passage_id = 0
					passage_desc = ""
					full_passage = ""
					content_master_id = tuple(content_master_id)
					out_json['activity_dtls'][i]['assessments'].append({"is_passage":is_passage,
																			"passage_id":passage_id,
																			"passage_desc":passage_desc,
																			"passage":full_passage,
																			"question_details":[]})

				# elif flag_change == 1:
				# 	# passage_id = 0
				for z in range(len(question_type)):
					# print(question_type[z],noofques[z])
					cursor.execute("""SELECT `Assessment_Type_Desc` FROM `assessment_type` 
								WHERE `Assessment_Type_ID` = %s""",(question_type[z]))
					question_type_desc = cursor.fetchone()
							
					if question_type_desc:
						question_type_desc = question_type_desc[0]
					out_json['activity_dtls'][i]['assessments'][e]['question_details'].append({"question_type":question_type[z],
																					"question_type_desc":question_type_desc,
																					"assess_desc":assess_desc[z],
																					"marks":ques_marks[z],
																					"questions":""})
					question_details = getquestions(question_type[z],noofques[z],content_master_id,passage_id,user_id)

					out_json['activity_dtls'][i]['assessments'][e]['question_details'][z]['questions'] = question_details
					marks_of_each_ques = int(ques_marks[z])/int(noofques[z])
					for q in range(len(question_details)):
						question_details[q]['mark'] = marks_of_each_ques
						question_id = question_details[q]['Question_ID']
						option_details = getoptions(question_id)
						# print(option_details)
						out_json['activity_dtls'][i]['assessments'][e]['question_details'][z]['questions'][q]['options'] = option_details
						answer_details = getanswer(question_id)
						if answer_details:
							out_json['activity_dtls'][i]['assessments'][e]['question_details'][z]['questions'][q]['answer'] = answer_details[0]
						else:
							out_json['activity_dtls'][i]['assessments'][e]['question_details'][z]['questions'][q]['answer'] = []
		
		abs_html_path = ''
		if assessment_dtls:
			last_update_ts = datetime.now().strftime('%Y-%m-%d%H%M%S')
			cur.execute("""SELECT `FIRST_NAME`,`INSTITUTION_ID` FROM `institution_user_credential` ic, 
				`institution_user_credential_master` icm WHERE ic.`INSTITUTION_USER_ID` = %s 
				and ic.`INSTITUTION_USER_ID` = icm.`INSTITUTION_USER_ID`""",(user_id))
			tchr_dtls = cur.fetchone()
			u_name = tchr_dtls[0]
			instiID = tchr_dtls[1]
			cur.execute("""SELECT `institution_logo` FROM `institution_firebase_mapping` 
				WHERE `institution_id` = %s""",(instiID))
			logo = cur.fetchone()
			if logo:
				instiLogo = logo[0]
			else:
				instiLogo = 'http://creamsonservices.com/Image/institution_logos/myelsa.png'
			html = render_template(template_name, activity_dtls=out_json,image_path = instiLogo)
			template_name = template_name.split('.')[0]
			filename = u_name+'_'+template_name+'_'+str(last_update_ts) + '.html'
			html_path = os.path.join(UPLOAD_FOLDER,filename)
			open(html_path,'w').write(html.encode('utf-8'))
			abs_html_path = SERVER_PATH+filename
		out_json['html_filepath'] = abs_html_path
		out_json['download_id'] = ''
		if abs_html_path != '':
			download_insert_query = ("""INSERT INTO `mock_test_download_history`
				(`user_id`, `content_filepath`) VALUES (%s,%s)""")
			download_data = (user_id,abs_html_path)
			cursor.execute(download_insert_query,download_data)
			dw_id = cursor.lastrowid
			out_json['download_id'] = dw_id
		mockqueshist(out_json)
		# if ques_id:
		# 	for q in ques_id:
		# 		history_insert_query = ("""INSERT INTO `mock_test_question_history`
		# 		(`user_id`, `question_id`,`download_id`) VALUES (%s,%s,%s)""")
		# 		history_data = (user_id,q,dw_id)
		# 		cursor.execute(history_insert_query, history_data)
		connection.commit()
		cursor.close()
		return ({"attributes": {
		    				"status_desc": "Mock Test Details.",
		    				"status": "success"
		    				},
		    				"responseList":out_json}), status.HTTP_200_OK


@name_space.route("/getMockTestDownloadHistoryByUserId/<int:user_id>")
class getMockTestDownloadHistoryByUserId(Resource):
	def get(self, user_id):
		connection = mysql.connect()
		cursor = connection.cursor()
		content_filepath_list = []
		content_file_id = []
		cursor.execute("""SELECT `id`,`content_filepath`  FROM `mock_test_download_history` 
			WHERE `user_id` = %s order by `last_update_ts` desc""", (user_id))
		getdownloadhistory = cursor.fetchall()
		if getdownloadhistory:
			desc = cursor.description
			col_names = [col[0] for col in desc]
			content_filepath_list = [dict(izip(col_names, row)) for row in getdownloadhistory]
		for i in range(len(content_filepath_list)):
			file_path = content_filepath_list[i]['content_filepath'].split("/")
			if len(file_path) > 4:
				file_name = file_path[5].split(".")[0]
				content_filepath_list[i]['file_name'] = file_name
				content_filepath_list[i]['board'] = ''
				content_filepath_list[i]['s_class'] = ''
				content_filepath_list[i]['creation_date'] = file_name.split('_')[-1][:10]
				if len(file_name.split("_")) > 2:
					board = file_name.split("_")[1]
					content_filepath_list[i]['board'] = board
					file_name = file_path[-1].split('.')[0]
					s_class = file_name.split('_')[2][5:]
					content_filepath_list[i]['s_class'] = s_class
					creation_date = file_name.split("_")[-1][:10]
					content_filepath_list[i]['creation_date'] = creation_date
				elif len(file_path) == 2:
					file_name = file_path[1].split(".")[0]
					content_filepath_list[i]['file_name']=file_name
					board = file_name.split("_")[1]
					content_filepath_list[i]['board'] = board
					s_class = file_name.split('_')[2][5:]
					content_filepath_list[i]['s_class'] = s_class
					creation_date = file_name.split("_")[3][:10]
					content_filepath_list[i]['creation_date'] = creation_date
			else:
				content_filepath_list[i]['file_name'] = file_name
				content_filepath_list[i]['board'] = ''
				content_filepath_list[i]['s_class'] = ''
				content_filepath_list[i]['creation_date'] = file_name.split('_')[-1][:10]
				
		return ({"attributes": {"status_desc": "Mock Test Download Details.",
								"status": "success"},
					"responseList": content_filepath_list}), status.HTTP_200_OK


@name_space.route("/assignMockTest")
class assignMockTest(Resource):
	@api.expect(assgin_model)
	def post(self):
		details = request.get_json()
		connection = mysql.connect()
		cursor = connection.cursor()
		conn = mysql1.connect()
		cur = conn.cursor()
		is_group = details['is_group']
		res = 'Something went wrong!'
		if is_group.lower() == 'y':
			groups = details['group_id']
			group_desc = []
			for i, grp in enumerate(groups):
				cur.execute("""SELECT `Student_Id` FROM `group_student_mapping` 
					WHERE `Group_ID` = %s""",(grp))

				students = cur.fetchall()

				if students:
					for s in students:
						cursor.execute("""SELECT `mapping_id` FROM `mocktest_student_mapping` 
							WHERE `teacher_id` = %s and `student_id` = %s 
							and `download_id` = %s""",(details['teacher_id'],s,details['download_id']))
						dwnld_id = cursor.fetchone()
						if dwnld_id:
							continue
						else:
							mapping_insert_query = ("""INSERT INTO `mocktest_student_mapping`( `teacher_id`, 
								`student_id`, `download_id`) VALUES (%s,%s,%s)""")

							mapping_data = (details['teacher_id'],s,details['download_id'])

							cursor.execute(mapping_insert_query,mapping_data)

				cur.execute("""SELECT `Group_Description` FROM `group_master` 
					WHERE `Group_ID` = %s""",(grp))
				desc = cur.fetchone()
				group_desc.append(desc[0].encode('utf-8'))
			res = 'Mock Test Assigned to {}'.format(group_desc)
		elif is_group.lower() == 'n':
			students = details['student_id']
			s_name = []
			for s in students:
				cur.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) FROM 
					`institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(s))
				name = cur.fetchone()
				s_name.append(name[0].encode('utf-8'))
				cursor.execute("""SELECT `mapping_id` FROM `mocktest_student_mapping` 
					WHERE `teacher_id` = %s and `student_id` = %s 
					and `download_id` = %s""",(details['teacher_id'],s,details['download_id']))
				dwnld_id = cursor.fetchone()
				if dwnld_id:
					continue
				else:
					mapping_insert_query = ("""INSERT INTO `mocktest_student_mapping`( `teacher_id`, 
						`student_id`, `download_id`) VALUES (%s,%s,%s)""")

					mapping_data = (details['teacher_id'],s,details['download_id'])

					cursor.execute(mapping_insert_query,mapping_data)
			res = 'Mock Test Assigned to {}'.format(s_name)
		else:
			res = 'Something went wrong!'
		connection.commit()
		cur.close()
		cursor.close()

		return ({"attributes": {"status_desc": "Mock Test Mapping Details.",
								"status": "success"},
				"responseList": res}), status.HTTP_200_OK


@name_space.route("/getAssignedStudentsByDownloadId/<int:download_id>")
class getAssignedStudentsByDownloadId(Resource):
	def get(self,download_id):
		connection = mysql.connect()
		cursor = connection.cursor()
		conn = mysql1.connect()
		cur = conn.cursor()
		student_details = []
		cursor.execute("""SELECT `student_id`,`completion_status`,concat(`teacher_feedback`,', ',`addition_feedback`) feedback
		 FROM `mocktest_student_mapping` WHERE `download_id` = %s""",(download_id))

		students = cursor.fetchall()

		print(students)
		for s in students:
			cur.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`), `INSTITUTION_USER_NAME` FROM 
					`institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(s[0]))
			name = cur.fetchone()
			if not s[2]:
				feedback = ''
			else:
				feedback = s[2]
			student_details.append({"student_id":s[0],
									"feedback":feedback,
									"student_name":name[0],
									"student_phoneno":name[1],
									"status":s[1]}) 
		cursor.close()
		return ({"attributes": {"status_desc": "Mock Test Assignee Details.",
								"status": "success"},
				"responseList": student_details}), status.HTTP_200_OK




@name_space.route("/mockTestGetStudentAnswers/<int:download_id>/<int:student_id>")
class mockTestGetStudentAnswers(Resource):
	def get(self, student_id, download_id):
		connection = mysql_connection_lab_lang()
		cursor = connection.cursor()
		activity = []
		full_marks = 0
		cursor.execute("""SELECT `activity_id` from mock_test_question_history
			WHERE `download_id` = %s GROUP by `activity_id`""",(download_id))
		activity = cursor.fetchall()

		cursor.execute("""SELECT `activity_id`,`assessment_type_id` from mock_test_question_history
			WHERE `download_id` = %s GROUP by `activity_id`,`assessment_type_id`""",(download_id))
		assessment_tyepid = cursor.fetchall()

		cursor.execute("""SELECT `activity_id`,`assessment_type_id`,`passage_id` from mock_test_question_history 
			WHERE `download_id` = %s GROUP by `assessment_type_id`, `activity_id`,`passage_id`""",(download_id))
		passage_id = cursor.fetchall()

		cursor.execute("""SELECT `activity_id`,`assessment_type_id`,`passage_id`,`question_id`,`marks`
			from mock_test_question_history WHERE `download_id` = %s 
			GROUP by `assessment_type_id`, `activity_id`,`passage_id`,`question_id`""",(download_id))

		questions = cursor.fetchall()

		for i, act in enumerate(activity):
			activity[i]['assessment_type_id'] = []
			for j, ass in enumerate(assessment_tyepid):
				if assessment_tyepid[j]['activity_id'] == activity[i]['activity_id']:
					cursor.execute("""SELECT `Assessment_Type_Desc` FROM `assessment_type` 
						WHERE `Assessment_Type_ID`= %s""",(assessment_tyepid[j]['assessment_type_id']))
					assess_desc = cursor.fetchone()
					activity[i]['assessment_type_id'].append({'assessment_desc':assess_desc['Assessment_Type_Desc'],
																'assessment_desc_id':assessment_tyepid[j]['assessment_type_id'],
																'question_details':[]})
			for p, psg in enumerate(passage_id):
				if passage_id[p]['activity_id'] == activity[i]['activity_id']:
					for a, ass in enumerate(activity[i]['assessment_type_id']):
						if passage_id[p]['assessment_type_id'] == activity[i]['assessment_type_id'][a]['assessment_desc_id']:
							is_passage = 'n'
							passage_desc = ''
							passage = ''
							if passage_id[p]['passage_id'] != 0:
								is_passage = 'y'
								cursor.execute("""SELECT `passage_desc`,`content_file_path` as 'passage' 
									FROM `passage_dtl` WHERE `passage_id` = %s""",(passage_id[p]['passage_id']))
								psg_dtls = cursor.fetchone()
								passage_desc = psg_dtls['passage_desc']
								passage  = psg_dtls['passage']
							activity[i]['assessment_type_id'][a]['question_details'].append({'passage_id':passage_id[p]['passage_id'],
																								'is_passage':is_passage,
																								'passage':passage,
																								'passage_desc':passage_desc,
																								'questions':[]})
    		
			for q, ques in enumerate(questions):
				full_marks += questions[q]['marks']
				if questions[q]['activity_id'] == activity[i]['activity_id']:
					for a, ass in enumerate(activity[i]['assessment_type_id']):
						if questions[q]['assessment_type_id'] == activity[i]['assessment_type_id'][a]['assessment_desc_id']:
							for qd in range(len(activity[i]['assessment_type_id'][a]['question_details'])):
								if questions[q]['passage_id'] == activity[i]['assessment_type_id'][a]['question_details'][qd]['passage_id']:
									print(questions[q]['question_id'])
									if questions[q]['question_id'] != None:
										cursor.execute("""SELECT ques.`Question`,ques.`Content_master_Id`,ques.`passage_id`,ques.`Content_file_path`,
															ques.`Content_FileName`,ques.`File_Type_ID`,ques.`Question_Type`,ans.`Option_ID`,
															ans.`Additional_Text`,op.`Option`,op.`Content_file_path`,op.`Content_FileName`,
															op.`File_Type_ID` FROM `question` ques,`answer` ans,`options` op
															WHERE ques.`Question_ID` = ans.`Question_ID` AND ans.`Option_ID` = op.`Option_ID` 
															AND ques.`Question_ID` = %s""",(questions[q]['question_id']))
										answers = cursor.fetchone()

										cursor.execute("""SELECT `question_id`,`option_id`,`answer`,`answer_filepath`,`marks`,`remark`,`filetype`
											FROM `user_mock_test_answer_mapping` WHERE `download_id` = %s
											and `student_id` = %s and `question_id` = %s
											and `status` = 'c' """,(download_id,student_id,questions[q]['question_id']))
										std_ans = cursor.fetchone()
										
										if std_ans:
											option_id = std_ans['option_id']
											answer = std_ans['answer']
											answer_filepath = std_ans['answer_filepath']
											marks = std_ans['marks']
											if marks == None:
												marks = ''
											remark = std_ans['remark']
											filetype = std_ans['filetype']
										else:
											option_id = ''
											answer = ''
											answer_filepath = ''
											marks = ''
											remark = ''
											filetype = ''
										activity[i]['assessment_type_id'][a]['question_details'][qd]['questions'].append({'question_id':questions[q]['question_id'],
																														'Question':answers['Question'],
																														'Content_master_Id':answers['Content_master_Id'],
																														'passage_id':answers['passage_id'],
																														'Content_file_path':answers['Content_file_path'],
																														'Content_FileName':answers['Content_FileName'],
																														'File_Type_ID':answers['File_Type_ID'],
																														'Question_Type':answers['Question_Type'],
																														'marks':questions[q]['marks'],
																														'correctAnswer':{'Option_ID':answers['Option_ID'],
																																			'Option':answers['Option'],
																																			'Additional_Text':answers['Additional_Text'],
																																			'Content_file_path':answers['Content_file_path'],
																																			'Content_FileName':answers['Content_FileName'],
																																			'File_Type_ID':answers['File_Type_ID']},
																														'student_answer':{'option_id':option_id,
																																			'answer':answer,
																																			'answer_filepath':answer_filepath,
																																			'marks':marks,
																																			'remark':remark,
																																			'filetype':filetype
																														}})
		cursor.close()
		return ({"attributes": {"status_desc": "Mock Test Student Answers.",
								"status": "success",
								"full_marks":full_marks},
				"responseList": activity}), status.HTTP_200_OK


@name_space.route("/getMockTestListForStudents/<int:student_id>")
class getMockTestListForStudents(Resource):
	def get(self, student_id):
		connection = mysql_connection_lab_lang()
		cursor = connection.cursor()

		conn = mysql1.connect()
		cur = conn.cursor()
		assigned_test = []
		cursor.execute("""SELECT msm.`teacher_id`,msm.`download_id`,mtdh.`content_filepath`,date(msm.`last_update_ts`) as assigned_on, 
			msm.`completion_status` FROM `mocktest_student_mapping` msm, `mock_test_download_history` mtdh 
			WHERE mtdh.`id` = msm.`download_id` and `student_id` = %s order by date(msm.`last_update_ts`) desc""",(student_id))

		assigned_test = cursor.fetchall()

		cur.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`) FROM `institution_user_credential` 
				WHERE `INSTITUTION_USER_ID` = %s""",(assigned_test[0]['teacher_id']))
		teacher_name = cur.fetchone()[0]
		
		for i in range(len(assigned_test)):
			assigned_test[i]['assigned_on'] = assigned_test[i]['assigned_on'].isoformat()
			assigned_test[i]['teacher_name'] = teacher_name
			assigned_test[i]['filename'] = assigned_test[i]['content_filepath'].split('/')[-1].split('.')[0]
		
		cursor.close()
		cur.close()

		return ({"attributes": {"status_desc": "Mock Test List For Students.",
								"status": "success"},
				"responseList": assigned_test}), status.HTTP_200_OK



@name_space.route("/getMockTestQuestionForStudents/<int:download_id>")
class getMockTestQuestionForStudents(Resource):
	def get(self, download_id):
		connection = mysql_connection_lab_lang()
		cursor = connection.cursor()
		activity = []
		cursor.execute("""SELECT `activity_id` from mock_test_question_history
			WHERE `download_id` = %s GROUP by `activity_id`""",(download_id))
		activity = cursor.fetchall()

		cursor.execute("""SELECT `activity_id`,`assessment_type_id` from mock_test_question_history
			WHERE `download_id` = %s GROUP by `activity_id`,`assessment_type_id`""",(download_id))
		assessment_tyepid = cursor.fetchall()

		cursor.execute("""SELECT `activity_id`,`assessment_type_id`,`passage_id` from mock_test_question_history 
			WHERE `download_id` = %s GROUP by `assessment_type_id`, `activity_id`,`passage_id`""",(download_id))
		passage_id = cursor.fetchall()

		cursor.execute("""SELECT `activity_id`,`assessment_type_id`,`passage_id`,`question_id` 
			from mock_test_question_history WHERE `download_id` = %s 
			GROUP by `assessment_type_id`, `activity_id`,`passage_id`,`question_id`""",(download_id))

		questions = cursor.fetchall()
		try:
			for i, act in enumerate(activity):
				activity[i]['assessment_type_id'] = []
				for j, ass in enumerate(assessment_tyepid):
					if assessment_tyepid[j]['activity_id'] == activity[i]['activity_id']:
						cursor.execute("""SELECT `Assessment_Type_Desc` FROM `assessment_type` 
							WHERE `Assessment_Type_ID`= %s""",(assessment_tyepid[j]['assessment_type_id']))
						assess_desc = cursor.fetchone()
						activity[i]['assessment_type_id'].append({'assessment_desc':assess_desc['Assessment_Type_Desc'],
																	'assessment_desc_id':assessment_tyepid[j]['assessment_type_id'],
																	'question_details':[]})
				for p, psg in enumerate(passage_id):
					if passage_id[p]['activity_id'] == activity[i]['activity_id']:
						for a, ass in enumerate(activity[i]['assessment_type_id']):
							if passage_id[p]['assessment_type_id'] == activity[i]['assessment_type_id'][a]['assessment_desc_id']:
								is_passage = 'n'
								passage_desc = ''
								passage = ''
								if passage_id[p]['passage_id'] != 0:
									is_passage = 'y'
									cursor.execute("""SELECT `passage_desc`,`content_file_path` as 'passage' 
										FROM `passage_dtl` WHERE `passage_id` = %s""",(passage_id[p]['passage_id']))
									psg_dtls = cursor.fetchone()
									passage_desc = psg_dtls['passage_desc']
									passage  = psg_dtls['passage']
								activity[i]['assessment_type_id'][a]['question_details'].append({'passage_id':passage_id[p]['passage_id'],
																									'is_passage':is_passage,
																									'passage':passage,
																									'passage_desc':passage_desc,
																									'questions':[]})
	    		
				for q, ques in enumerate(questions):
					if questions[q]['activity_id'] == activity[i]['activity_id']:
						for a, ass in enumerate(activity[i]['assessment_type_id']):
							if questions[q]['assessment_type_id'] == activity[i]['assessment_type_id'][a]['assessment_desc_id']:
								for qd in range(len(activity[i]['assessment_type_id'][a]['question_details'])):
									if questions[q]['passage_id'] == activity[i]['assessment_type_id'][a]['question_details'][qd]['passage_id']:
										print(questions[q]['question_id'])
										if questions[q]['question_id'] != None:
											cursor.execute("""SELECT ques.`Question`,ques.`Content_master_Id`,ques.`passage_id`,ques.`Content_file_path`,
																ques.`Content_FileName`,ques.`File_Type_ID`,ques.`Question_Type`,ans.`Option_ID`,
																ans.`Additional_Text`,op.`Option`,op.`Content_file_path`,op.`Content_FileName`,
																op.`File_Type_ID` FROM `question` ques,`answer` ans,`options` op
																WHERE ques.`Question_ID` = ans.`Question_ID` AND ans.`Option_ID` = op.`Option_ID` 
																AND ques.`Question_ID` = %s""",(questions[q]['question_id']))
											
											quesDtls = cursor.fetchone()

											cursor.execute("""SELECT `Option_ID`,`Option`,`Option_Sequence_ID`,`Content_file_path`,
												`Content_FileName`,`File_Type_ID` 
												FROM `options` WHERE `Question_ID` = %s""",(questions[q]['question_id']))

											options = cursor.fetchall()

											activity[i]['assessment_type_id'][a]['question_details'][qd]['questions'].append({'question_id':questions[q]['question_id'],
																															'Question':quesDtls['Question'],
																															'Content_master_Id':quesDtls['Content_master_Id'],
																															'passage_id':quesDtls['passage_id'],
																															'Content_file_path':quesDtls['Content_file_path'],
																															'Content_FileName':quesDtls['Content_FileName'],
																															'File_Type_ID':quesDtls['File_Type_ID'],
																															'Question_Type':quesDtls['Question_Type'],
																															'answer':{'Option_ID':quesDtls['Option_ID'],
																																				'Option':quesDtls['Option'],
																																				'Additional_Text':quesDtls['Additional_Text'],
																																				'Content_file_path':quesDtls['Content_file_path'],
																																				'Content_FileName':quesDtls['Content_FileName'],
																																				'File_Type_ID':quesDtls['File_Type_ID']},
																															'options':options})
		except:
			pass


		cursor.close()
		return ({"attributes": {"status_desc": "Mock Test Questions",
								"status": "success"},
				"responseList": activity}), status.HTTP_200_OK



@name_space.route("/mockTestSubmitMarksbyPut/<int:student_id>/<int:download_id>")
class mockTestSubmitMarksbyPut(Resource):
	@api.expect(submit_marks)
	def put(self, student_id, download_id):
		connection = mysql_connection_lab_lang()
		cursor = connection.cursor()

		details = request.get_json()

		marks_details = details['marks_details']

		for m, mrksDtls in enumerate(marks_details):
			question_id = mrksDtls['question_id']
			marks = mrksDtls['marks']
			remarks = mrksDtls['remarks']
			marks_update_query = ("""UPDATE `user_mock_test_answer_mapping` SET `marks` = %s,`remark` = %s 
				WHERE `download_id` = %s and `student_id` = %s and `question_id` = %s""")

			update_data = (marks,remarks,download_id,student_id,question_id)

			cursor.execute(marks_update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Submit Marks",
								"status": "success"},
				"responseList": 'Marks Submitted Successfully'}), status.HTTP_200_OK


@name_space.route("/mockTestTeacherFeedbackByPut/<int:student_id>/<int:download_id>")
class mockTestTeacherFeedbackByPut(Resource):
	@api.expect(feedback)
	def put(self, student_id, download_id):
		connection = mysql_connection_lab_lang()
		cursor = connection.cursor()

		details = request.get_json()

		feedback = details['feedback']
		additional_feedback = details['additional_feedback']

		marks_update_query = ("""UPDATE `mocktest_student_mapping` SET `teacher_feedback` = %s,`addition_feedback` = %s 
				WHERE `download_id` = %s and `student_id` = %s""")

		update_data = (feedback,additional_feedback,download_id,student_id)

		cursor.execute(marks_update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Submit Feedback",
								"status": "success"},
				"responseList": 'Feedback Submitted Successfully'}), status.HTTP_200_OK


@name_space.route("/mockTestSubmitStudentAnswersByPost/<int:student_id>/<int:download_id>")
class mockTestSubmitStudentAnswersByPost(Resource):
	@api.expect(submit_answers)
	def post(self, student_id, download_id):
		connection = mysql_connection_lab_lang()
		cursor = connection.cursor()

		details = request.get_json()

		answer_details = details['answer_details']
		completion_status = details['status']
		for a, ans in enumerate(answer_details):
			question_id = ans['question_id']
			option_id = ans['option_id']
			answer = ans['answer']
			answer_filepath = ans['answer_filepath']
			filetype = ans['filetype']
			submit_answer_insert_query = ("""INSERT INTO `user_mock_test_answer_mapping`(`download_id`,`student_id`,
				`question_id`,`option_id`,`answer`,`answer_filepath`,`status`,`filetype`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""")

			submit_data = (download_id,student_id,question_id,option_id,answer,answer_filepath,completion_status,filetype)

			cursor.execute(submit_answer_insert_query,submit_data)


		mocttest_std_mapping_update = ("""UPDATE `mocktest_student_mapping` SET `completion_status` = %s 
			WHERE `student_id` = %s and `download_id` =%s""")

		maping_data = (completion_status,student_id,download_id)

		cursor.execute(mocttest_std_mapping_update,maping_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Submit Answer",
								"status": "success"},
				"responseList": 'Answers Submitted Successfully'}), status.HTTP_200_OK


@name_space.route("/mockTestViewResultAndFeedback/<int:student_id>/<int:download_id>")
class mockTestViewResultAndFeedback(Resource):
	def get(self, student_id, download_id):
		connection = mysql_connection_lab_lang()
		cursor = connection.cursor()
		activity = []
		question_details = []
		total_marks = 0
		full_marks = 0
		# cursor.execute("""SELECT `activity_id` from mock_test_question_history
		# 	WHERE `download_id` = %s GROUP by `activity_id`""",(download_id))
		# activity = cursor.fetchall()

		# cursor.execute("""SELECT `activity_id`,`assessment_type_id` from mock_test_question_history
		# 	WHERE `download_id` = %s GROUP by `activity_id`,`assessment_type_id`""",(download_id))
		# assessment_tyepid = cursor.fetchall()

		# cursor.execute("""SELECT `activity_id`,`assessment_type_id`,`passage_id` from mock_test_question_history 
		# 	WHERE `download_id` = %s GROUP by `assessment_type_id`, `activity_id`,`passage_id`""",(download_id))
		# passage_id = cursor.fetchall()

		cursor.execute("""SELECT `activity_id`,`assessment_type_id`,`passage_id`,`question_id`,`marks` 
			from mock_test_question_history WHERE `download_id` = %s 
			GROUP by `assessment_type_id`, `activity_id`,`passage_id`,`question_id`""",(download_id))

		questions = cursor.fetchall()

		cursor.execute("""SELECT concat(`teacher_feedback`,', ',`addition_feedback`) feedback 
			FROM `mocktest_student_mapping` WHERE `student_id` = %s and `download_id` = %s""",(student_id,download_id))

		teacherfeedback = cursor.fetchone()
		if teacherfeedback['feedback'] == None:
			feedback = ""
		else:
			feedback = teacherfeedback['feedback']

		cursor.execute("""SELECT sum(`marks`) as full_marks from `mock_test_question_history` 
			WHERE `download_id` = %s""",(download_id))

		qMarks = cursor.fetchone()
		full_marks = int(qMarks['full_marks'])

		# for i, act in enumerate(activity):
		# 	activity[i]['assessment_type_id'] = []
		# 	for j, ass in enumerate(assessment_tyepid):
		# 		if assessment_tyepid[j]['activity_id'] == activity[i]['activity_id']:
		# 			cursor.execute("""SELECT `Assessment_Type_Desc` FROM `assessment_type` 
		# 				WHERE `Assessment_Type_ID`= %s""",(assessment_tyepid[j]['assessment_type_id']))
		# 			assess_desc = cursor.fetchone()
		# 			activity[i]['assessment_type_id'].append({'assessment_desc':assess_desc['Assessment_Type_Desc'],
		# 														'assessment_desc_id':assessment_tyepid[j]['assessment_type_id'],
		# 														'question_details':[]})
		# 	for p, psg in enumerate(passage_id):
		# 		if passage_id[p]['activity_id'] == activity[i]['activity_id']:
		# 			for a, ass in enumerate(activity[i]['assessment_type_id']):
		# 				if passage_id[p]['assessment_type_id'] == activity[i]['assessment_type_id'][a]['assessment_desc_id']:
		# 					is_passage = 'n'
		# 					passage_desc = ''
		# 					passage = ''
		# 					if passage_id[p]['passage_id'] != 0:
		# 						is_passage = 'y'
		# 						cursor.execute("""SELECT `passage_desc`,`content_file_path` as 'passage' 
		# 							FROM `passage_dtl` WHERE `passage_id` = %s""",(passage_id[p]['passage_id']))
		# 						psg_dtls = cursor.fetchone()
		# 						passage_desc = psg_dtls['passage_desc']
		# 						passage  = psg_dtls['passage']
		# 					activity[i]['assessment_type_id'][a]['question_details'].append({'passage_id':passage_id[p]['passage_id'],
		# 																						'is_passage':is_passage,
		# 																						'passage':passage,
		# 																						'passage_desc':passage_desc,
		# 																						'questions':[]})
    		
		# 	for q, ques in enumerate(questions):
		# 		if questions[q]['activity_id'] == activity[i]['activity_id']:
		# 			for a, ass in enumerate(activity[i]['assessment_type_id']):
		# 				if questions[q]['assessment_type_id'] == activity[i]['assessment_type_id'][a]['assessment_desc_id']:
		# 					for qd in range(len(activity[i]['assessment_type_id'][a]['question_details'])):
		# 						if questions[q]['passage_id'] == activity[i]['assessment_type_id'][a]['question_details'][qd]['passage_id']:
		# 							print(questions[q]['question_id'])
		# 							if questions[q]['question_id'] != None:
		# 								cursor.execute("""SELECT ques.`Question`,ques.`Content_master_Id`,ques.`passage_id`,ques.`Content_file_path`,
		# 													ques.`Content_FileName`,ques.`File_Type_ID`,ques.`Question_Type`,ans.`Option_ID`,
		# 													ans.`Additional_Text`,op.`Option`,op.`Content_file_path`,op.`Content_FileName`,
		# 													op.`File_Type_ID` FROM `question` ques,`answer` ans,`options` op
		# 													WHERE ques.`Question_ID` = ans.`Question_ID` AND ans.`Option_ID` = op.`Option_ID` 
		# 													AND ques.`Question_ID` = %s""",(questions[q]['question_id']))
		# 								answers = cursor.fetchone()
		# 								cursor.execute("""SELECT `Assessment_Type_Desc` FROM `assessment_type` 
		# 									WHERE `Assessment_Type_ID`= %s""",(answers['Question_Type']))
		# 								ques_type_desc = cursor.fetchone()
		# 								cursor.execute("""SELECT `question_id`,`option_id`,`answer`,`answer_filepath`,`marks`,`remark` 
		# 									FROM `user_mock_test_answer_mapping` WHERE `download_id` = %s
		# 									and `student_id` = %s and `question_id` = %s
		# 									and `status` = 'c' """,(download_id,student_id,questions[q]['question_id']))
		# 								std_ans = cursor.fetchone()
		# 								option_id = ''
		# 								answer = ''
		# 								answer_filepath = ''
		# 								marks = 0
		# 								remark = ''
		# 								if std_ans:
		# 									option_id = std_ans['option_id']
		# 									answer = std_ans['answer']
		# 									answer_filepath = std_ans['answer_filepath']
		# 									marks = std_ans['marks']
		# 									remark = std_ans['remark']
		# 									total_marks += marks
		# 								activity[i]['assessment_type_id'][a]['question_details'][qd]['questions'].append({'question_id':questions[q]['question_id'],
		# 																												'Question':answers['Question'],
		# 																												'Content_master_Id':answers['Content_master_Id'],
		# 																												'passage_id':answers['passage_id'],
		# 																												'Content_file_path':answers['Content_file_path'],
		# 																												'Content_FileName':answers['Content_FileName'],
		# 																												'File_Type_ID':answers['File_Type_ID'],
		# 																												'Assessment_Desc':ques_type_desc['Assessment_Type_Desc'],
		# 																												'correctAnswer':{'Option_ID':answers['Option_ID'],
		# 																																	'Option':answers['Option'],
		# 																																	'Additional_Text':answers['Additional_Text'],
		# 																																	'Content_file_path':answers['Content_file_path'],
		# 																																	'Content_FileName':answers['Content_FileName'],
		# 																																	'File_Type_ID':answers['File_Type_ID']},
		# 																												'student_answer':{'option_id':option_id,
		# 																																	'answer':answer,
		# 																																	'answer_filepath':answer_filepath,
		# 																																	'marks':marks,
		# 																																	'remark':remark
		# 																												}})
		# 								question_details.append(activity[i]['assessment_type_id'][a]['question_details'])																						
		

		for q, ques in enumerate(questions):
			if questions[q]['question_id'] != None:
				cursor.execute("""SELECT ques.`Question`,ques.`Content_master_Id`,ques.`passage_id`,ques.`Content_file_path`,
					ques.`Content_FileName`,ques.`File_Type_ID`,ques.`Question_Type`,ans.`Option_ID`,
					ans.`Additional_Text`,op.`Option`,op.`Content_file_path`,op.`Content_FileName`,
					op.`File_Type_ID` FROM `question` ques,`answer` ans,`options` op
					WHERE ques.`Question_ID` = ans.`Question_ID` AND ans.`Option_ID` = op.`Option_ID` 
					AND ques.`Question_ID` = %s""",(questions[q]['question_id']))
				answers = cursor.fetchone()
				cursor.execute("""SELECT `Assessment_Type_Desc` FROM `assessment_type` 
					WHERE `Assessment_Type_ID`= %s""",(answers['Question_Type']))
				ques_type_desc = cursor.fetchone()
				if answers['passage_id'] != 0:
					cursor.execute("""SELECT `passage_desc`,`content_file_path` as 'passage' 
						FROM `passage_dtl` WHERE `passage_id` = %s""",(answers['passage_id']))
					psg_dtls = cursor.fetchone()
					passage_desc = psg_dtls['passage_desc']
					passage  = psg_dtls['passage']
				else:
					passage_desc = ''
					passage  = ''
				cursor.execute("""SELECT `question_id`,`option_id`,`answer`,`answer_filepath`,`marks`,`remark` 
					FROM `user_mock_test_answer_mapping` WHERE `download_id` = %s
					and `student_id` = %s and `question_id` = %s
					and `status` = 'c' """,(download_id,student_id,questions[q]['question_id']))
				std_ans = cursor.fetchone()
				option_id = ''
				answer = ''
				answer_filepath = ''
				marks = 0
				remark = ''
				add_marks = 0
				if std_ans:
					option_id = std_ans['option_id']
					answer = std_ans['answer']
					answer_filepath = std_ans['answer_filepath']
					if std_ans['marks'] == None:
						add_marks = 0
						marks = ""
					else:
						add_marks = std_ans['marks']
						marks = std_ans['marks']
					remark = std_ans['remark']
					total_marks += add_marks
				question_details.append({'question_id':questions[q]['question_id'],
											'Question':answers['Question'],
											'Content_master_Id':answers['Content_master_Id'],
											'passage_id':answers['passage_id'],
											'passage_desc':passage_desc,
											'passage':passage,
											'Content_file_path':answers['Content_file_path'],
											'Content_FileName':answers['Content_FileName'],
											'File_Type_ID':answers['File_Type_ID'],
											'Assessment_Desc':ques_type_desc['Assessment_Type_Desc'],
											'marks':questions[q]['marks'],
											'correctAnswer':{'Option_ID':answers['Option_ID'],
																'Option':answers['Option'],
																'Additional_Text':answers['Additional_Text'],
																'Content_file_path':answers['Content_file_path'],
																'Content_FileName':answers['Content_FileName'],
																'File_Type_ID':answers['File_Type_ID']},
											'student_answer':{'option_id':option_id,
																'answer':answer,
																'answer_filepath':answer_filepath,
																'marks':marks,
																'remark':remark
											}})


		cursor.close()
		return ({"attributes": {"status_desc": "Mock Test Marks and Feedback Details.",
								"status": "success",
								"feedback":feedback,
								"total_marks":total_marks,
								"full_marks":full_marks},
				"responseList": question_details}), status.HTTP_200_OK



@name_space.route("/AssignPersonalizedMockTest")
class AssignPersonalizedMockTest(Resource):
	@api.expect(assign_individual)
	def post(self):
		details = request.get_json()

		connection = mysql.connect()
		cursor = connection.cursor()
		
		conn = mysql1.connect()
		cur = conn.cursor()
		
		s = details['student_id']
		s_name = ''
		
		if s > 0:
			
			cur.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) FROM 
				`institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(s))
			name = cur.fetchone()
			s_name = name[0]
			cursor.execute("""SELECT `mapping_id` FROM `mocktest_student_mapping` 
				WHERE `teacher_id` = %s and `student_id` = %s 
				and `download_id` = %s""",(details['teacher_id'],s,details['download_id']))
			dwnld_id = cursor.fetchone()
			
			if not dwnld_id:
				mapping_insert_query = ("""INSERT INTO `mocktest_student_mapping`( `teacher_id`, 
					`student_id`, `download_id`) VALUES (%s,%s,%s)""")

				mapping_data = (details['teacher_id'],s,details['download_id'])

				cursor.execute(mapping_insert_query,mapping_data)
				assign_id = cursor.lastrowid

				res = {"student_id":s,
						"student_name":s_name,
						"download_id":details['download_id'],
						"assign_id":assign_id}
		else:
			res = 'No Student Selected'

		connection.commit()
		cur.close()
		cursor.close()

		return ({"attributes": {"status_desc": "Mock Test Mapping Details.",
								"status": "success"},
				"responseList": res}), status.HTTP_200_OK


@name_space.route("/assignAndCreateMockTest")
class assignAndCreateMockTest(Resource):
	@api.expect(assign_and_create)
	def post(self):
		details = request.get_json()
		assign_json = details['assignDtls']
		create_json = details['createDtls']
		create_json['user_id'] = create_json['teacher_id']
		create_json.pop('teacher_id')
		login_connect = mysql_connection_logindb()
		cur_login = login_connect.cursor()
		langlab_connect = mysql_connection_lab_lang()
		cur_lang = langlab_connect.cursor()

		studentList = []
		outJson = []
		is_group = assign_json['is_group']
		if is_group.lower() == 'y':
			groupList = assign_json['group_id']
			group_desc = []
			for i, grp in enumerate(groupList):
				cur_login.execute("""SELECT `Student_Id` FROM `group_student_mapping` 
					WHERE `Group_ID` = %s""",(grp))

				students = cur_login.fetchall()

				if students:
					for j,s in enumerate(students):
						studentList.append(students[j]['Student_Id'])
		else:
			studentList = assign_json['student_id']
		if studentList:
			for i, sid in enumerate(studentList):
				cur_lang.execute("""SELECT `Class`,`Board` FROM `student` 
					WHERE `Student_UserID` = %s""",(sid))

				student_details = cur_lang.fetchone()

				s_cls = student_details['Class']
				board = student_details['Board']

				create_json['user_class'] = s_cls
				create_json['board_desc'] = board 
				mocktest_url = 'http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com/flaskapp/mock_test/MockTestQuestions/getMockTest'
				
				mocktest_payload = json.dumps(create_json)

				headers = {'Content-type':'application/json', 'Accept':'application/json'}
				mockPost = requests.post(mocktest_url, data=mocktest_payload, headers=headers)
				mockRes = mockPost.json()
				assign_payload = {"teacher_id": mockRes.get('responseList').get('user_id'),
									"download_id": mockRes.get('responseList').get('download_id'),
									"student_id": sid
								}
				assignUrl = 'http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com/flaskapp/mock_test/MockTestQuestions/AssignPersonalizedMockTest'
				assignPost = requests.post(assignUrl, data=json.dumps(assign_payload), headers=headers)
				assignRes = assignPost.json()
				assignRes.get('responseList')['filename'] = mockRes.get('responseList').get('html_filepath')
				outJson.append({"mockRes":mockRes.get('responseList'),
 							"assignRes":assignRes.get('responseList')})

		return ({"attributes": {"status_desc": "Mock Test Details.",
								"status": "success"
								},
				"responseList":outJson}), status.HTTP_200_OK

if __name__ == '__main__':
	app.run(host='0.0.0.0')
