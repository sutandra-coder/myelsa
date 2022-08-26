from flask import Flask, request, jsonify, json
from flask_api import status
import datetime
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests
import string
import random

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

istitution_user_otp_model = api.model('istitution_user_otp_model', {
	"firstName": fields.String(),
	"generatedBy": fields.String(),
	"institutionId": fields.Integer(),
	"institutionUserId": fields.Integer(),
	"institutionUserRole": fields.String(),
	"lastName": fields.String(),
	"mailId": fields.String(),
	"otp": fields.Integer(),
	"phoneNumber": fields.Integer()
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


@name_space.route("/allgroup/<int:institution_id>")
class allgroup(Resource):
	def get(self,institution_id):
		connection = connect_logindb()
		cursor = connection.cursor()

		cursor.execute("""SELECT `Group_ID` as `groupID`,`Institution_ID` as `institutionID`,`Group_Description` as `groupDescription`,`Last_Update_ID` as `lASTUPDATEID` FROM 
			`group_master` icm WHERE icm.`INSTITUTION_ID` = %s""",(institution_id))


		groupList = cursor.fetchall()
		for key,data in enumerate(groupList):	
			groupList[key]['lASTUPDATETIMESTAMP'] = 1
			groupList[key]['teacherId'] = 0

		cursor.close()
		return groupList



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

@name_space.route("/mobileNumberValidation/<string:mobile>")
class mobileNumberValidation(Resource):
	def get(self,mobile):
		connection = connect_logindb()
		curlang = connection.cursor()

		count_mobile = curlang.execute("""SELECT * FROM 
			`institution_user_credential` WHERE `INSTITUTION_USER_NAME` = %s""",(mobile))

		if count_mobile > 0:
			user_data = curlang.fetchone()
			return ({"attributes": {
				    		"phoneNumber": mobile,
				    		"status_desc": "Number fetched",
				    		"status":"success"
				    	},
				    	"responseList":{"PRIMARY_CONTACT_NUMBER":user_data['PRIMARY_CONTACT_NUMBER']},
				    	"responseList1":None,
				    	"responseDataTO":{"responseList1":None}
				    	 }), status.HTTP_200_OK
		else:
			return ({"attributes":{
						"phoneNumber":mobile,
						"status_desc":"Invalid Number",
						"status":"not-found"},
						"responseList1":None,
						"responseDataTO":{"responseList1":None}}), status.HTTP_200_OK


@name_space.route("/postInstitutionUserOtp")
class postInstitutionUserOtp(Resource):
	@api.expect(istitution_user_otp_model)
	def post(self):

		connection = connect_logindb()
		cursor = connection.cursor()			
		details = request.get_json()

		FIRST_NAME = details.get('firstName')
		LAST_NAME = details.get('lastName')
		MAIL_ID = details.get('mailId')		
		PHONE_NUMBER = details['phoneNumber']
		GENERATED_BY = details['generatedBy']
		INSTITUTION_ID = details['institutionId']
		INSTITUTION_USER_ID = details['institutionUserId']
		INSTITUTION_USER_ROLE = details['institutionUserRole']
		Address = ''

		def get_random_digits(stringLength=6):
		    Digits = string.digits
		    return ''.join((random.choice(Digits) for i in range(stringLength)))
		
		otp = get_random_digits()

		otp_query = ("""INSERT INTO `institution_user_otp`(`INSTITUTION_USER_ID`,
			`INSTITUTION_ID`,`OTP`,`INSTITUTION_USER_ROLE`,`FIRST_NAME`,`LAST_NAME`,
			`GENERATED_BY`, `MAIL_ID`, `Address`, `PHONE_NUMBER`)  
			VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
		otpdata = cursor.execute(otp_query,(INSTITUTION_USER_ID,INSTITUTION_ID,otp,INSTITUTION_USER_ROLE,
			FIRST_NAME,LAST_NAME,GENERATED_BY,MAIL_ID,Address,PHONE_NUMBER))

		get_query = ("""SELECT *
					FROM `institution_user_otp` WHERE `INSTITUTION_USER_ID` = %s and INSTITUTION_ID = %s and `OTP` = %s order by ID desc""")
		get_data = (INSTITUTION_USER_ID,INSTITUTION_ID,otp)
		count_otp = cursor.execute(get_query,get_data)
		otp_data = cursor.fetchone()

		connection.commit()
		cursor.close()

		return ({
		    "attributes": {
		        "otp_verfication_status": "N",
		        "status": "success"
		    },
		    "responseList": [
		        {
		            "InstitutionUserOtp ": {
		                "firstName": "",
		                "generatedBy": "System",
		                "institutionId": otp_data['INSTITUTION_ID'],
		                "institutionUserId": otp_data['INSTITUTION_USER_ID'],
		                "institutionUserRole": otp_data['INSTITUTION_USER_ROLE'],
		                "lastName": "",
		                "mailId": "",
		                "otp": int(otp_data['OTP']),
		                "phoneNumber": PHONE_NUMBER
		            }
		        }
		    ],
		    "responseDataTO": {}
		}), status.HTTP_200_OK


@name_space.route("/validateOtpByPhone/<int:oneTimePassword>/<int:phoneNumber>")
class validateOtpByPhone(Resource):
	def get(self,oneTimePassword,phoneNumber):
		connection = connect_logindb()
		curlang = connection.cursor()

		get_query = ("""SELECT *
					FROM `institution_user_otp` WHERE `OTP` = %s and PHONE_NUMBER = %s order by ID desc""")
		get_data = (oneTimePassword,phoneNumber)
		count_otp = curlang.execute(get_query,get_data)
		

		if count_otp > 0:
			otp_data = curlang.fetchone()

			return({"attributes":{"status":"success"},"responseList":[{"InstitutionUserOtp ":{"firstName":otp_data['FIRST_NAME'],
				"generatedBy":otp_data['GENERATED_BY'],"institutionId":otp_data['GENERATED_BY'],
				"institutionUserId":otp_data['INSTITUTION_USER_ID'],"institutionUserRole":otp_data['INSTITUTION_USER_ROLE']
				,"lastName":otp_data['LAST_NAME'],"mailId":otp_data['MAIL_ID'],"otp":otp_data['OTP'],"phoneNumber":otp_data['PHONE_NUMBER']}}],"responseDataTO":{}}),status.HTTP_200_OK
		else:
			return({"attributes":{"status_description":"Otp Not Validated","status":"Failed!!!"},"responseDataTO":{}}),status.HTTP_200_OK


