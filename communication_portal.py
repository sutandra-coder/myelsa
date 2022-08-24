from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
import datetime
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests

app = Flask(__name__)
cors = CORS(app)

#-------------------------------database-connection-------------------------------------------------#
def connect_b2c():
	connection = pymysql.connect(host='creamsonservices.com',
									user='creamson_langlab',
									password='Langlab@123',
									db='creamson__lang_lab_b2c',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor)
	return connection

'''def nextmysql_connection():
	nextconnection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='creamson_logindb',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return nextconnection'''

def nextmysql_connection():
	nextconnection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
	                             user='admin',
	                             password='cbdHoRPQPRfTdC0uSPLt',
	                             db='creamson_logindb',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return nextconnection
#-------------------------------database-connection-------------------------------------------------#

mycommunication_controller = Blueprint('mycommunication_api', __name__)
api = Api(mycommunication_controller,  title='MyElsa API',description='MyElsa API')
name_space_get = api.namespace('GET',description='CCE-CEFR Controller')
name_space_post = api.namespace('POST',description='CCE-CEFR Controller')
BASE_URL = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/'


#------------------------------------------------Assessment Model-------------------------------------#

new_assessment = api.model('new_assessment', {
	"assessment_type_id":fields.Integer(),
	"act_map":fields.Integer(),
	"assessment_desc":fields.String(),
	"assessment_content_file_path":fields.String(),
	"assessment_content_filename":fields.String(),
	"assessment_filetype_id":fields.Integer(),
	"assessment_addition_ts":fields.String(),
	"assessment_status":fields.String(),
	"last_update_id":fields.Integer(),
	"last_update_ts" : fields.String()
	})

new_content_assessment= api.model('new_content_assessment', {
		"content_master_id":fields.Integer(),
		"assessment_id":fields.Integer(),
		"last_update_id":fields.Integer()
 		})
new_assessment_question= api.model('new_assessment_question', {
		"assessment_id":fields.Integer(),
		"question_id":fields.Integer(),
		"last_update_id":fields.Integer()
 		})
options=api.model('options', {
		"option_name":fields.String(),
		"option_sequence_id":fields.Integer(),
		"option_content_file_path":fields.String(),
		"option_content_filename":fields.String(),
		"option_filetype_id":fields.Integer()
		})
upload_question = api.model('upload_question', {
	"question_type":fields.String(),
	"question":fields.String(),
	"question_content_file_path":fields.String(),
	"question_content_filename":fields.String(),
	"question_filetype_id":fields.Integer(),
	"activity_id":fields.Integer(),
	"level":fields.Integer(),
	"last_update_id":fields.Integer(),
	"answer":fields.String(),
	"answer_additional_text":fields.String(),
	"options":fields.List(fields.Nested(options))
	
	})
#------------------------------------------------Assessment Model-------------------------------------#

#-------------------------------dashboard-activity,activity,level-------------------------------------------------#
@name_space_get.route("/getdashboardActivity")
class getdashboardActivity(Resource):
	def get(self):

		nextconnection = nextmysql_connection()
		nextcursor = nextconnection.cursor()

		nextcursor.execute("""SELECT `Activity_Id`,`Activity_Description` FROM `activity_table` where `Activity_type`
			='communication'""")
		
		dashboard_activityList = nextcursor.fetchall()

		nextcursor.close()
		return ({"attributes": {"status_desc": "DashboardActivity Details",
                                "status": "success"
                                },
                 "responseList":dashboard_activityList,
                 				  
                }), status.HTTP_200_OK
#-------------------------------dashboard-activity,activity,level-------------------------------------------#

#-------------------------------activity-mapping-------------------------------------------------------------#

@name_space_get.route("/getactivity_mapping_id/<int:dashboard_activity_id>")
class getactivity_mapping_id(Resource):
	def get(self,dashboard_activity_id):

		connection = connect_b2c()
		cursor = connection.cursor()

		cursor.execute("""SELECT `Activity_Mapping_ID`,`Activity_Desc` FROM `activity` INNER JOIN `activity_mapping` 
			on activity.`Activity_ID`= activity_mapping.`Activity_ID` where `Dashboard_Activity_Id`=%s""",(dashboard_activity_id))
		
		activityList = cursor.fetchall()

		return ({"attributes": {"status_desc": "Activity Mapping Details",
                                "status": "success"
                                },
                 "responseList": activityList}), status.HTTP_200_OK

#-------------------------------activity-mapping-----------------------------------------------------------#

#-------------------------------module-------------------------------------------------------------#

@name_space_get.route("/getlevel/<int:dashboard_activity_id>")
class getlevel(Resource):
	def get(self,dashboard_activity_id):

		connection = connect_b2c()
		cursor = connection.cursor()

		cursor.execute("""SELECT `Cefr_Level`,`Level` FROM `cefr_level` WHERE `Activity_ID`=%s""",(dashboard_activity_id))
		
		moduleList = cursor.fetchall()

		return ({"attributes": {"status_desc": "Module Details",
                                "status": "success"
                                },
                 "responseList": moduleList}), status.HTTP_200_OK

#-------------------------------module-----------------------------------------------------------#

#-------------------------------content-master--------------------------------------------------------------#

@name_space_get.route("/getcontentmaster/<int:activity_mapping_id>/<int:level>")
class getcontentmaster(Resource):
	def get(self,activity_mapping_id,level):

		connection = connect_b2c()
		cursor = connection.cursor()

		cursor.execute("""SELECT content_rule.`Content_Master_ID`,content_rule.`Activity_Mapping_ID`,
			`Content_Master_Name`,`Level` FROM `content_master` INNER JOIN `content_rule` ON content_rule.
			`Content_Master_ID`= content_master.`Content_Master_ID` WHERE content_rule.`Activity_Mapping_ID`=%s 
			and `Level`=%s""",(activity_mapping_id,level))


		content_masterList = cursor.fetchall()

		return ({"attributes": {"status_desc": "Content Master Details",
                                "status": "success"
                                },
                 "responseList": content_masterList}), status.HTTP_200_OK

#-------------------------------content-master-----------------------------------------------------#

#-------------------------------assessment-type-----------------------------------------------------#
@name_space_get.route("/getassessment_type")
class getassessment_type(Resource):
	def get(self):

		connection = connect_b2c()
		cursor = connection.cursor()

		cursor.execute("""SELECT `Assessment_Type_ID`,`Assessment_Type_Desc` FROM `assessment_type` """)
		
		assessment_typeList = cursor.fetchall()

		return ({"attributes": {"status_desc": "Assessment Type Details",
                                "status": "success"
                                },
                 "responseList": assessment_typeList}), status.HTTP_200_OK

#-------------------------------assessment-type-----------------------------------------------------#

#-------------------------------file-type-----------------------------------------------------------#
@name_space_get.route("/getfiletype")
class getfiletype(Resource):
	def get(self):

		connection = connect_b2c()
		cursor = connection.cursor()

		cursor.execute("""SELECT `FileType_ID`,`FileType_Desc`,`FileType_Extension` FROM `filetype`""")
		
		filetypeList = cursor.fetchall()

		cursor.close()
		return ({"attributes": {"status_desc": "FileType Details",
                                "status": "success"
                                },
                 "responseList":filetypeList,
                 				  
                }), status.HTTP_200_OK
#-------------------------------file-type-------------------------------------------------------------#

#-------------------------------create-assessment-----------------------------------------------------#
@name_space_post.route("/create_assessment")
class create_assessment(Resource):
	@api.expect(new_assessment)
	def post(self):
		details = request.get_json()
		connection = connect_b2c()
		cursor = connection.cursor()
		details = request.get_json()

		assessment_type_id = details['assessment_type_id']
		act_map = details['act_map']
		assessment_desc = details['assessment_desc']
		assessment_content_file_path = details['assessment_content_file_path']
		assessment_content_filename = details['assessment_content_filename']
		assessment_filetype_id = details['assessment_filetype_id']
		assessment_addition_ts = details['assessment_addition_ts']
		assessment_status = details['assessment_status']
		last_update_id = details['last_update_id']
		last_update_ts = details['last_update_ts']

		assessment_query = ("""INSERT INTO assessment (`Assessment_Type_ID`, `Activity_Mapping_ID`, `Assesment_Desc`,`Content_File_Path`, 
			`Content_FileName`, `FileType_Id`, `Assessment_Status`,`Last_Update_ID`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""")
		assessment_data = (assessment_type_id, act_map, assessment_desc, assessment_content_file_path, assessment_content_filename,
			assessment_filetype_id, assessment_status, last_update_id)

		cursor.execute(assessment_query, assessment_data)
		connection.commit()
		details['assessment_id'] = cursor.lastrowid
		assessment_id=details['assessment_id']
		print(assessment_id)
		return ({"attributes": {"status_desc": "Assessment Type Details",
                                "status": "success"
                                },
                 "responseList": {"assessment_id":assessment_id }        
                 }), status.HTTP_200_OK

#-------------------------------create-assessment-----------------------------------------------------#

#-------------------------------content-assessment-----------------------------------------------------#
@name_space_post.route("/content_assessment_mapping")
class content_assessment_mapping(Resource):
	@api.expect(new_content_assessment)
	def post(self):
		connection = connect_b2c()
		cursor = connection.cursor()
		details = request.get_json()

		content_master_id = details['content_master_id']
		assessment_id = details['assessment_id']
		last_update_id = details['last_update_id']

		assessment_content_query = (""" INSERT INTO content_assessment_mapping (Content_Master_ID, Assessment_ID,
 		 Last_Update_ID) values (%s,%s,%s)""")
		assessment_content_mapping_data = (content_master_id, assessment_id, last_update_id)
		cursor.execute(assessment_content_query, assessment_content_mapping_data)
		connection.commit()
		return ({"attributes": {"status_desc": "Content Assessment Details",
                                "status": "success"
                                },
                 }), status.HTTP_200_OK

#-------------------------------content-assessment-----------------------------------------------------#

#-------------------------------question-----------------------------------------------------#
@name_space_post.route("/upload_question")
class upload_question(Resource):
	@api.expect(upload_question)
	def post(self):
		connection = connect_b2c()
		cursor = connection.cursor()
		details = request.get_json()
		escape_text = [',',"'",'"']

		question_type = details['question_type']
		question = details['question']
		question_content_file_path = details['question_content_file_path']
		question_content_filename = details['question_content_filename']
		question_filetype_id = details['question_filetype_id']
		level = details['level']
		activity_id = details['activity_id']
		last_update_id = details['last_update_id']
		now = datetime.now()
		last_update_ts = now.strftime("%H:%M:%S")
			
		question_query = ("""INSERT INTO question (`Question_Type`, `Question`, `Content_file_path`, 
				`Content_FileName`, `File_Type_ID`, `Level`, `Activity_Id`, `Last_Update_ID`, `Last_Update_TS`) 
				VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) """)
		question_data = (question_type, question, question_content_file_path, 
				question_content_filename, question_filetype_id, level, activity_id, last_update_id, last_update_ts)
		cursor.execute(question_query, question_data)
		
		question_id = cursor.lastrowid

		options = details['options']
		option = options
		option_sequence_id = 1
		for ops in option:
			option_name = ops['option_name']
			ops['option_sequence_id'] = option_sequence_id
			option_content_file_path = ops['option_content_file_path']
			option_content_filename = ops['option_content_filename']
			option_filetype_id = ops['option_filetype_id']

			option_query = ("""INSERT INTO options ( `Question_ID`, `Option`, `Option_Sequence_ID`, `Content_file_path`, 
					`Content_FileName`, `File_Type_ID`) 
					VALUES (%s,%s,%s,%s,%s,%s)""")

			option_data = (question_id, option_name, option_sequence_id, option_content_file_path, option_content_filename,
					option_filetype_id)

			cursor.execute(option_query, option_data)
			option_sequence_id += 1
			# connection.commit()		
			answer = details['answer']
			answer_additional_text = details['answer_additional_text']
			cursor.execute("""SELECT `Option_ID` from options where `Question_ID` = %s 
				and `Option` = %s""",(question_id,answer))
			option_id = cursor.fetchone()
			print(option_id)
		if option_id != None:
			   option = option_id
			   x = option.get("Option_ID")
			   print(x)
			# print(option_id)
		answer_insert_query = ("""INSERT INTO `answer`(`Question_ID`, `Option_ID`, 
			`Additional_Text`) VALUES(%s,%s,%s)""")
		answer_data = (question_id,x,answer_additional_text)
		cursor.execute(answer_insert_query,answer_data)
		connection.commit()
		details['question_id'] = question_id
		questionid=details['question_id']
		print(questionid)

		return ({"attributes": {"status_desc": "Inserted successfully",
	                                "status": "success"
	                            },
                 "responseList": {"question_id":questionid }
	                 }), status.HTTP_200_OK

#-------------------------------question-----------------------------------------------------#

#-------------------------------assessment-question-------------------------------------------#
@name_space_post.route("/assessment_question_mapping")
class assessment_question_mapping(Resource):
	@api.expect(new_assessment_question)
	def post(self):
		connection = connect_b2c()
		cursor = connection.cursor()
		details = request.get_json()

		assessment_id = details['assessment_id']
		last_update_id = details['last_update_id']
		# last_update_ts = details['last_update_ts']
		question_id = details['question_id']

		assessment_question_query = ("""INSERT INTO assessment_question_mapping( Assessment_ID, Question_ID, 
					Last_Update_ID) VALUES(%s,%s,%s)""")

		assessment_question_mapping_data = (assessment_id, question_id, last_update_id)
		cursor.execute(assessment_question_query, assessment_question_mapping_data)
		connection.commit()

		return ({"attributes": {"status_desc": "Assessment Question Details",
                                "status": "success"
                                },
                 }), status.HTTP_200_OK
#-------------------------------assessment-question-------------------------------------------#