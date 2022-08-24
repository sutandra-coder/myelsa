from flask import Flask, request, jsonify, json
from flask_api import status
import datetime
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests

app = Flask(__name__)
cors = CORS(app)

class_manager_api = Blueprint('class_manager_api', __name__)
api = Api(class_manager_api,  title='Myelsa API',description='Myelsa API')
name_space = api.namespace('ClassManager',description='Class Manager')

#----------------------database-connection---------------------#
'''def connect_logindb():
    connection = pymysql.connect(host='creamsonservices.com',
                                user='creamson_langlab',
                                password='Langlab@123',
                                db='creamson_logindb',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
    return connection'''

def connect_logindb():
    connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
                                user='admin',
                                password='cbdHoRPQPRfTdC0uSPLt',
                                db='creamson_logindb',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
    return connection


def connect_lab_lang1():
    connection = pymysql.connect(host='creamsonservices.com',
                                user='creamson_langlab',
                                password='Langlab@123',
                                db='creamson_lab_lang1',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
    return connection

#----------------------database-connection---------------------#

create_assignment = api.model('create_assignment_model', {
	"assignmentType":fields.String(),
	"contentFileType":fields.String(),
	"contentMasterId":fields.Integer(),
	"contentPath":fields.String(),
	"remarks":fields.Integer(),
	"teacherId":fields.Integer(),
	"title":fields.String()
	})

create_group = api.model('create_group_model', {
	"groupDescription":fields.String(),
	"institutionId":fields.Integer(),
	"teacherId":fields.Integer()
	})


assigment_marks_model = api.model('assigment_marks_model', {
	"assignmentId":fields.Integer(),
	"remarks":fields.String(),
	"result":fields.Integer(),
	"teacherId":fields.Integer(),
	"studentId":fields.Integer()
	})

@name_space.route("/getStudentListByInstitutionId/<int:institution_id>")
class getStudentListByInstitutionId(Resource):
	def get(self,institution_id):
		connection = connect_logindb()
		cursor = connection.cursor()

		cursor.execute("""SELECT icm.`INSTITUTION_USER_ID`,`SEC`,`Board`,`STUDENT_ROLL_NUM`,`CLASS`,`STUDENT_NAME`,
			`STUDENT_TYPE`,`Fathers_Name`,ic.`Image_URL`,`EMAIL_ID`,`PRIMARY_CONTACT_NUMBER` FROM 
			`institution_user_credential_master` icm INNER JOIN `student_dtls` sd 
			on icm.`INSTITUTION_USER_ID` = sd.`INSTITUTION_USER_ID_STUDENT` 
			and icm.`INSTITUTION_ID` = sd.`INSTITUTION_ID` INNER JOIN `institution_user_credential` ic 
			on icm.`INSTITUTION_USER_ID` = ic.`INSTITUTION_USER_ID` WHERE icm.`INSTITUTION_ID` = %s 
			and `INSTITUTION_USER_ROLE` = 'S1'""",(institution_id))


		studentListDtls = cursor.fetchall()
		cursor.close()
		return ({"attributes": {"status_desc": "Student List Details",
								"status": "success"},
				"responseList": studentListDtls}), status.HTTP_200_OK



@name_space.route("/createAssignment")
class createAssignment(Resource):
	@api.expect(create_assignment)
	def post(self):

		connection = connect_lab_lang1()
		curlog = connection.cursor()

		details = request.get_json()
		
		assignmentType = details.get('assignmentType')
		contentFileType = details.get('contentFileType')
		contentMasterId = details.get('contentMasterId')
		contentPath = details.get('contentPath')
		remarks = details.get('remarks')
		teacherId = details.get('teacherId')
		title = details.get('title')

		assignmentInsertQuery = ("""INSERT INTO `assignment`(`Teacher_ID`, `Assignment_Type`, 
			`Content_Master_ID`, `Content_path`, `Remarks`, `Content_File_Type`, `Title`, 
			`Last_Update_ID`,`Last_Update_TS`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
		lastUpdateTS = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
		assignmentData = (teacherId,assignmentType,contentMasterId,contentPath,remarks,contentFileType,
			title,teacherId,lastUpdateTS)

		curlog.execute(assignmentInsertQuery,assignmentData)
		assignment_id = curlog.lastrowid

		connection.commit()
		curlog.close()

		return {"STATUS":"SUCCESS","AssignmentId":assignment_id}



@name_space.route("/createGroup")
class createGroup(Resource):
	@api.expect(create_group)
	def post(self):

		connection = connect_logindb()
		curlog = connection.cursor()

		details = request.get_json()

		groupDescription = details.get('groupDescription')
		institutionId = details.get('institutionId')
		teacherId = details.get('teacherId')

		groupInsertQuery = ("""INSERT INTO `group_master`(`Institution_ID`, `Group_Description`, 
			`Last_Update_ID`) VALUES (%s,%s,%s)""")

		groupData = (institutionId,groupDescription,teacherId)

		curlog.execute(groupInsertQuery,groupData)
		groupId = curlog.lastrowid
		details['groupId'] = groupId

		connection.commit()
		curlog.close()

		return ({"attributes": {"status_desc": "Group Details",
								"status": "success"},
				"responseList": details}), status.HTTP_200_OK


@name_space.route("/InsertMarksWithStudentIdAndAssignmentId")
class InsertMarksWithStudentIdAndAssignmentId(Resource):
	@api.expect(assigment_marks_model)
	def post(self):

		connection = connect_lab_lang1()
		curlang = connection.cursor()

		details = request.get_json()

		assignmentId = details.get('assignmentId')
		remarks = details.get('remarks')
		result = details.get('result')
		teacherId = details.get('teacherId')
		studentId = details.get('studentId')


		curlang.execute("""INSERT INTO `assigment_result`(`Student_ID`, `Assignment_ID`, 
			`Result`, `Remarks`, `Last_update_Id`) 
			VALUES (%s,%s,%s,%s,%s)""",(studentId,assignmentId,result,remarks,teacherId))

		marksid = curlang.lastrowid
		details['marksid'] = marksid
		
		connection.commit()
		curlang.close()

		return ({"attributes": {"status_desc": "Assignment marks Details",
								"status": "success"},
				"responseList": details}), status.HTTP_200_OK