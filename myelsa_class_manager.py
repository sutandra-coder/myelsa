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
import time
from threading import Thread

app = Flask(__name__)
cors = CORS(app)


def mysql_connection():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='creamson_logindb',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

def library_connection():
	connection = pymysql.connect(host='creamsonservices.com',
									user='creamson_langlab',
									password='Langlab@123',
									db='creamson_user_library',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor)
	return connection

myelsa = Blueprint('myelsa_api', __name__)
api = Api(myelsa,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('myelsa',description='myelsa')

updateinsid = api.model('updateinsid', {
	"student_id": fields.Integer(),
    "code": fields.String()
    })

forgotpsw = api.model('forgotpsw', {
	  "phone_no": fields.Integer()
	})

addstudentgroup = api.model('addstudentgroup', {
	"groupDescription": fields.String(),
    "groupID": fields.Integer(),
    "lASTUPDATEID": fields.Integer(),
    "lASTUPDATETIMESTAMP":fields.String(),
    "mappingID": fields.Integer(),
    "studentId": fields.Integer(),
    "teacherId": fields.Integer()
    })

addstudentgroupDtls = api.model('addstudentgroupDtls', {
	"addstudentgroup":fields.List(fields.Nested(addstudentgroup))
	})

logout_track = api.model('logout_track', {
	"INSTITUTION_USER_ID": fields.Integer(),
    "Device_id": fields.String(),
    "Version_Desc":fields.String(),
    "Application_type": fields.String(),
    "Model_Id": fields.String(),
    "Last_updated_ID": fields.Integer()
    })

updateStudentName = api.model('updateStudentName', {
	"studentid": fields.Integer(),
    "studentname": fields.String(),
    "teacherid": fields.Integer()
    })
#-----------------------forgot-psw-myelsa------------------------------------#
@name_space.route("/forgotpasswordByPhoneNumber")
class forgotpasswordByPhoneNumber(Resource):
	@api.expect(forgotpsw)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		
		res = {}
		Phone_no = details.get('phone_no')
		
		cursor.execute("""SELECT `INSTITUTION_USER_ID`,`FIRST_NAME`,`LAST_NAME` FROM 
			`institution_user_credential` WHERE `PRIMARY_CONTACT_NUMBER`=%s""",(Phone_no))

		userdtls = cursor.fetchall()
		if userdtls:
			for j in range(len(userdtls)):
				userid = userdtls[j]['INSTITUTION_USER_ID']
				firstname = userdtls[j]['FIRST_NAME']
				lastname = userdtls[j]['LAST_NAME']
				cursor.execute("""SELECT `INSTITUTION_ID`,`INSTITUTION_USER_ROLE`  FROM 
					`institution_user_credential_master` WHERE `INSTITUTION_USER_ID`=%s""",
					(userid))

				institutiondtls = cursor.fetchall()
				for j in range(len(userdtls)):
					institutionid = institutiondtls[j]['INSTITUTION_ID']
					userrole = institutiondtls[j]['INSTITUTION_USER_ROLE']

					url = 'http://creamsonservices.com:8080/NewSignUpService/postInstitutionUserOtp'
					headers = {'Content-type':'application/json', 'Accept':'application/json'}
					data ={
				            "firstName": firstname,
							"generatedBy": "System",
							"institutionId": institutionid,
							"institutionUserId": userid,
							"institutionUserRole": userrole,
							"lastName": lastname,
							"mailId": "",
							"otp": 0,
							"phoneNumber": Phone_no
				            }
					response = requests.post(url, data=json.dumps(data), headers=headers).json()
					# print(response)
					respon = response['responseList'][0]
					resp = respon['InstitutionUserOtp ']['otp']
					
					res = {'INSTITUTION_USER_ID':userid,
							'phoneNumber':Phone_no,
							'otp':resp
							}

					return ({"attributes": {"status_desc": "Forgot password Details",
	                                "status": "success"
	                                },
							"responseList":res}), status.HTTP_200_OK
		else:
			return ({"attributes": {"status_desc": "Forgot password Details",
	                                "status": "Not Exists"
	                                }
	                 }), status.HTTP_200_OK

#-----------------------forgot-psw-myelsa------------------------------------#

#-----------------------add-student-to-group---------------------------------#
def addStudentgrp(stuList,teacherId,lASTUPDATETIMESTAMP,groupDescription):
	connection = mysql_connection()
	cursor = connection.cursor()
	# current_date = datetime.now()
	for j in lASTUPDATETIMESTAMP:
		lastUpdatets = lASTUPDATETIMESTAMP[0]
		
	for j in groupDescription:
		groupDes= groupDescription[0]
	
	url = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/app_notify/AppCommunicationAPI/appMessage'
	headers = {'Content-type':'application/json', 'Accept':'application/json'}
	
	cursor.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`)as
        teachername FROM `institution_user_credential` WHERE 
        `INSTITUTION_USER_ID` =%s""",(teacherId))
	teacher_name = cursor.fetchone()
	if teacher_name :
		teachername = teacher_name['teachername']
	
	for i in range(len(stuList)):
		studentid = stuList[i]
		stuid = studentid[0]
		
		cursor.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`)as
        student_name FROM `institution_user_credential` WHERE 
        `INSTITUTION_USER_ID` =%s""",(stuid))

		studentnames = cursor.fetchone()
		if studentnames :
			studentname = studentnames['student_name']
		data = {
		        "appParams": {},
		        "userId": stuid,
		        "sourceapp": "GRP003S",
		        "toMail": "",
		        "role": "S1",
		        "toNumber": 0,
		        "mailParams": {"student":studentname,
		        			   "groupname":groupDes,
		        			   "startdate":lastUpdatets,
		        			   "teacher":teachername}
		        }
		response = requests.post(url, data=json.dumps(data), headers=headers).json()
		# print(response)
	cursor.close()
	return 'success'


class Compute(Thread):
	def __init__(self, request, funcname):
		Thread.__init__(self)
		self.request = request
		self.funcname = funcname

	def run(self):
		time.sleep(5)
		if self.funcname == 'addStudentGroup':
			stuList = self.request[0]
			teacherId = self.request[1]
			lASTUPDATETIMESTAMP = self.request[2]
			groupDescription = self.request[3]
			addStudentgrp(stuList,teacherId,lASTUPDATETIMESTAMP,groupDescription)
		else:
			pass 

@name_space.route("/addStudentGroup")
class addStudentGroup(Resource):
	@api.expect(addstudentgroupDtls)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		
		addstugroup = details['addstudentgroup']
		stuList = []
		for add in addstugroup:
			groupDescription = add.get('groupDescription'),
			groupID = add.get('groupID'),
			lASTUPDATEID = add.get('lASTUPDATEID'),
			lASTUPDATETIMESTAMP = add.get('lASTUPDATETIMESTAMP'),
			mappingID = add.get('mappingID'),
			studentId = add.get('studentId'),
			teacherId = add.get('teacherId')
			# print (studentId)
			addgroup_query = ("""INSERT INTO `group_student_mapping`(`Group_ID`, 
				`Student_Id`, `LAST_UPDATE_ID`,`LAST_UPDATE_TIMESTAMP`) 
				VALUES (%s,%s,%s,%s)""")
			mappdata = (groupID,studentId,teacherId,lASTUPDATETIMESTAMP)

			cursor.execute(addgroup_query,mappdata)
			stuList.append(studentId)
		connection.commit()
		cursor.close()
		
		sendrReq = (stuList,teacherId,lASTUPDATETIMESTAMP,groupDescription)
		thread_a = Compute(sendrReq,'addStudentGroup')
		thread_a.start()
		
		return ({"attributes": {"status_desc": "Student Added to Group",
								"status": "success"},
				"responseList":'success'}), status.HTTP_200_OK
	    
#-----------------------add-student-to-group---------------------------------#
		
#------------------------delete-user-registration----------------------------#
def deleteCredentialDtls(userid):
	connection = mysql_connection()
	cursor = connection.cursor()

	try:
		delcredentialDtls = ("""DELETE FROM `institution_user_credential` 
			WHERE `INSTITUTION_USER_ID` = %s""")

		delcredentialdata = (userid)
		cursor.execute(delcredentialDtls,delcredentialdata)
		connection.commit()
		cursor.close()
		
	except Exception as e:
		return e

	return 'updated'
def deleteStudentDtls(userid):
	connection = mysql_connection()
	cursor = connection.cursor()

	try:
		delstudentDtls = ("""DELETE FROM `student_dtls` WHERE 
			`INSTITUTION_USER_ID_STUDENT`=%s""")

		delstudentdata = (userid)
		cursor.execute(delstudentDtls,delstudentdata)

		delcredentialmasterDtls = ("""DELETE FROM `institution_user_credential_master` 
			WHERE `INSTITUTION_USER_ID` = %s""")

		delcredentialmasterdata = (userid)
		cursor.execute(delcredentialmasterDtls,delcredentialmasterdata)

		delcredentialDtls = ("""DELETE FROM `institution_user_credential` 
			WHERE `INSTITUTION_USER_ID` = %s""")

		delcredentialdata = (userid)
		cursor.execute(delcredentialDtls,delcredentialdata)
		connection.commit()
		cursor.close()
		
	except Exception as e:
		return e

	return 'updated'

def deleteTeacherDtls(userid):
	connection = mysql_connection()
	cursor = connection.cursor()
        
	try:
		delteacherDtls = ("""DELETE FROM `teacher_dtls` WHERE 
			`INSTITUTION_USER_ID_TEACHER`=%s""")

		delteacherData = (userid)
		cursor.execute(delteacherDtls,delteacherData)
		
		delcredentialmasterDtls = ("""DELETE FROM `institution_user_credential_master` 
			WHERE `INSTITUTION_USER_ID` = %s""")

		delcredentialmasterdata = (userid)
		cursor.execute(delcredentialmasterDtls,delcredentialmasterdata)

		delcredentialDtls = ("""DELETE FROM `institution_user_credential` 
			WHERE `INSTITUTION_USER_ID` = %s""")

		delcredentialdata = (userid)
		cursor.execute(delcredentialDtls,delcredentialdata)
		connection.commit()
		cursor.close()
		
	except Exception as e:
		return e

	return 'updated'

def deleteGuardianDtls(userid):
	connection = mysql_connection()
	cursor = connection.cursor()

	try:
		delguardianDtls = ("""DELETE FROM `guardian_dtls` WHERE 
			`INSTITUTION_USER_ID_GUARDIAN`=%s""")

		delguardianData = (userid)
		cursor.execute(delguardianDtls,delguardianData)
		
		delcredentialmasterDtls = ("""DELETE FROM `institution_user_credential_master` 
			WHERE `INSTITUTION_USER_ID` = %s""")

		delcredentialmasterdata = (userid)
		cursor.execute(delcredentialmasterDtls,delcredentialmasterdata)

		delcredentialDtls = ("""DELETE FROM `institution_user_credential` 
			WHERE `INSTITUTION_USER_ID` = %s""")

		delcredentialdata = (userid)
		cursor.execute(delcredentialDtls,delcredentialdata)
		connection.commit()
		cursor.close()
		
	except Exception as e:
		return e

	return 'updated'

@name_space.route("/deleteUserRegistrationDtls/<int:username>")
class deleteUserRegistrationDtls(Resource):
	def put(self,username):
		connection = mysql_connection()
		cursor = connection.cursor()
		res = 'Not Exists!!!'
     
		cursor.execute("""SELECT `INSTITUTION_USER_ID` FROM `institution_user_credential` 
			WHERE `INSTITUTION_USER_NAME`= %s""",(username))

		Userid = cursor.fetchone()
		if Userid: 
			userid = Userid['INSTITUTION_USER_ID']
			# print(userid)
			cursor.execute("""SELECT `INSTITUTION_USER_ROLE` FROM 
			`institution_user_credential_master` WHERE `INSTITUTION_USER_ID`=%s""",(userid))
			
			Userrole= cursor.fetchone()
			userrole= Userrole['INSTITUTION_USER_ROLE']
			# print(userrole)

			if userrole !='':
				if userrole =='S1':
					delRes = deleteStudentDtls(userid)
					
					if delRes == 'updated':
						res = 'Student Registration Details Removed.'
				elif userrole =='TA':
					delRes = deleteTeacherDtls(userid)
					if delRes == 'updated':
						res = 'Teacher Registration Details Removed.'
				else :
					delRes = deleteGuardianDtls(userid)
					if delRes == 'updated':
						res = 'Guadian Registration Details Removed.'
			else:
				delRes = deleteCredentialDtls(userid)
				if delRes == 'updated':
					res = 'Registration Details Removed From Credential.'
		else:
			[]
		cursor.close()

		return ({"attributes": {"status_desc": "User Registration Details.",
									"status": "success"
									},
					"responseList": res}), status.HTTP_200_OK

#------------------------delete-user-registration----------------------------#
		
#-----------------------------user-logout-tracking---------------------------------#
@name_space.route("/userLogoutTracking")
class userLogoutTracking(Resource):
	@api.expect(logout_track)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		
		INSTITUTION_USER_ID = details['INSTITUTION_USER_ID']
		Device_id = details['Device_id']
		Version_Desc = details['Version_Desc']
		Application_type = details['Application_type']
		Model_Id = details['Model_Id']
		Last_updated_ID = details['Last_updated_ID']

		logouttrack_query = ("""INSERT INTO `logout_tracking`(`INSTITUTION_USER_ID`,
			`Device_id`,`Version_Desc`,`Application_type`,`Model_Id`,`Last_updated_ID`) 
			VALUES (%s,%s,%s,%s,%s,%s)""")
		logouttrackdata = (INSTITUTION_USER_ID,Device_id,Version_Desc,Application_type,
			Model_Id,INSTITUTION_USER_ID)

		cursor.execute(logouttrack_query,logouttrackdata)
		
		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "User Logout Details Added",
								"status": "success"},
				"responseList":details}), status.HTTP_200_OK

#-----------------------------user-logout-tracking---------------------------------#			

#---------------------------------------------------------------------------------#
@name_space.route("/updateInstitutionID")
class updateInstitutionID(Resource):
    @api.expect(updateinsid)
    def put(self):
        details = request.get_json()
        connection = mysql_connection()
        cursor = connection.cursor()
        
        student_id = details['student_id']
        code = details['code']
        
        cursor.execute("""SELECT `INSTITUTION_ID` FROM `institution_dtls_and_code_map` 
        	WHERE `CODE`=%s""",(code))
        institution_id = cursor.fetchone()
        
        if institution_id == None:
        	res ='Check Your institution code!!!'
        else:
        	insid = institution_id['INSTITUTION_ID']
	        cursor.execute("""SELECT `INSTITUTION_NAME` FROM `institution_dtls` WHERE 
	        	`INSTITUTION_ID`=%s""",(insid))
	        institution_name = cursor.fetchone()
	        if institution_name ==None:
	        	insname = ''
	        else:
	        	insname = institution_name['INSTITUTION_NAME']

	        cursor.execute("""SELECT `INSTITUTION_ID` FROM `institution_user_credential_master` 
	        	WHERE `INSTITUTION_USER_ID`=%s and `INSTITUTION_USER_ROLE`='S1'""",(student_id))
	        institutionid = cursor.fetchone()
	        instid = institutionid['INSTITUTION_ID']

	        cursor.execute("""SELECT `INSTITUTION_ID` FROM `student_dtls` WHERE 
		        	`INSTITUTION_USER_ID_STUDENT`=%s""",(student_id))
	        stuinstitutionid = cursor.fetchone()
	        stuinstid = stuinstitutionid['INSTITUTION_ID']

	        res = {'INSTITUTION_ID':insid,
					'INSTITUTION_Name':insname
					}
					
	        if insid != instid and insid != stuinstid:
	        	
		        update_credendential_master = ("""UPDATE `institution_user_credential_master` SET 
		        	`INSTITUTION_ID`=%s WHERE `INSTITUTION_USER_ID`=%s and `INSTITUTION_ID`=%s and 
		        	`INSTITUTION_USER_ROLE`='S1'""")
		        update_credendential_master_data = (insid,student_id,instid)
		        cursor.execute(update_credendential_master,update_credendential_master_data)

		        update_student_dtls = ("""UPDATE `student_dtls` SET `INSTITUTION_ID`=%s WHERE 
		        	`INSTITUTION_USER_ID_STUDENT`=%s and `INSTITUTION_ID`=%s""")
		        update_student_dtls_data = (insid,student_id,stuinstid)
		        cursor.execute(update_student_dtls,update_student_dtls_data)
		        connection.commit()
	        	cursor.close()
	        else:
	        	res

        return ({"attributes": {"status_desc": "Update Institution Id.",
                            "status": "success"
                            },
                            "responseList":res}), status.HTTP_200_OK

#---------------------------------------------------------------------------------#

#---------------------------------------------------------------------------------#
@name_space.route("/getInstitutionCodeByInstitutionId/<int:institution_id>")
class getInstitutionFeeByClass(Resource):
	def get(self,institution_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		

		cursor.execute("""SELECT `CODE` FROM `institution_dtls_and_code_map` WHERE 
			`INSTITUTION_ID`=%s""",(institution_id))
		codedtl = cursor.fetchone()
		if codedtl == None:
			code = ''
		else:
			code = codedtl['CODE']

		cursor.execute("""SELECT `institution_id`,`institution_app_link` FROM
			`institution_firebase_mapping` WHERE `institution_id`=%s""",(institution_id))
		applinkdtl = cursor.fetchone()
		if applinkdtl == None:
			applink =''
		else:
			applink = applinkdtl['institution_app_link']
		res =[{
				'CODE':code,
				'applink':applink
		 }]

		return ({"attributes": {"status_desc": "Institution Code Details",
								"status": "success"
								},
				"responseList": res}), status.HTTP_200_OK



#---------------------------------------------------------------------------------#

#---------------------------------------------------------------------------------#
@name_space.route("/getAttendanceReportByStudentId/<int:student_id>/<string:start_date>/<string:end_date>")
class getAttendanceReportByStudentId(Resource):
	def get(self,student_id,start_date,end_date):

		connection = mysql_connection()
		cursor = connection.cursor()
		

		cursor.execute("""SELECT `ATTENDANCE_ID`,`MEETING_ID`,`INSTITUTION_USER_ID`,
			`STATUS`,`batch_start_time`,`batch_end_time`,`LAST_UPDATE_TIMESTAMP` FROM 
			`attendance` WHERE `INSTITUTION_USER_ID`=%s and date(`batch_start_time`)
			BETWEEN %s and %s""",(student_id,start_date,end_date))
		attendanceDtls = cursor.fetchall()
		
		for i in range(len(attendanceDtls)):
			if attendanceDtls[i]['STATUS'] == '1':
				attendanceDtls[i]['STATUS'] = 'Present' 
			else:
				attendanceDtls[i]['STATUS'] = 'Absent' 
			attendanceDtls[i]['batch_start_time'] = attendanceDtls[i]['batch_start_time'].isoformat()
			attendanceDtls[i]['batch_end_time'] = attendanceDtls[i]['batch_end_time'].isoformat()
			attendanceDtls[i]['LAST_UPDATE_TIMESTAMP'] = attendanceDtls[i]['LAST_UPDATE_TIMESTAMP'].isoformat()
		
		return ({"attributes": {"status_desc": "Attendance Report Details",
								"status": "success"
								},
				"responseList": attendanceDtls}), status.HTTP_200_OK


#---------------------------------------------------------------------#
@name_space.route("/getAttendanceReportByClass/<int:clss>/<string:date>")
class getAttendanceReportByStudentId(Resource):
	def get(self,clss,date):

		connection = mysql_connection()
		cursor = connection.cursor()
		

		cursor.execute("""SELECT `ATTENDANCE_ID`,`MEETING_ID`,`INSTITUTION_USER_ID`,`STATUS`,
			`batch_start_time`,`batch_end_time`,attendance.`LAST_UPDATE_TIMESTAMP` FROM `attendance` 
			INNER JOIN `group_student_mapping` on `attendance`.`INSTITUTION_USER_ID` = 
			`group_student_mapping`.`Student_Id` WHERE `Group_ID`=%s and 
			date(`batch_start_time`)=%s""",(clss,date))
		attendanceDtls = cursor.fetchall()
		
		for i in range(len(attendanceDtls)):
			if attendanceDtls[i]['STATUS'] == '1':
				attendanceDtls[i]['STATUS'] = 'Present' 
			else:
				attendanceDtls[i]['STATUS'] = 'Absent' 
			attendanceDtls[i]['batch_start_time'] = attendanceDtls[i]['batch_start_time'].isoformat()
			attendanceDtls[i]['batch_end_time'] = attendanceDtls[i]['batch_end_time'].isoformat()
			attendanceDtls[i]['LAST_UPDATE_TIMESTAMP'] = attendanceDtls[i]['LAST_UPDATE_TIMESTAMP'].isoformat()
		
		return ({"attributes": {"status_desc": "Attendance Report Details",
								"status": "success"
								},
				"responseList": attendanceDtls}), status.HTTP_200_OK


#---------------------------------------------------------------#
@name_space.route("/getStudentLiveClassAttendanceByDate/<string:start_date>/<string:end_date>/<int:student_id>")
class getStudentLiveClassAttendanceByDate(Resource):
	def get(self,start_date,end_date,student_id):

		connection = library_connection()
		cursor = connection.cursor()
		conn = mysql_connection()
		cur = conn.cursor()

		livelist = []
		cursor.execute("""SELECT `liveclass_id` FROM 
			`liveclass_mapping` WHERE date(`start_date`) between %s 
			and %s""",(start_date,end_date))
		scheduledlist = cursor.fetchall()
		# print(scheduledlist)
		for sid,sche in enumerate(scheduledlist):
			cursor.execute("""SELECT slt.`student_id`,
				`STATUS`,`subject` FROM `liveclass_mapping` lm 
				INNER join `liveclass_student_mapping` lsm on 
				lm.`liveclass_id`=lsm.`liveclass_id` INNER join 
				`student_liveclass_tracking` slt on 
				lsm.`student_id`=slt.`Student_ID` where 
				slt.`Student_ID`= %s and lm.`liveclass_id`=%s""",
				(student_id,sche.get('liveclass_id')))
			studentAttendanceDtls = cursor.fetchone()
			
			if studentAttendanceDtls:
				cur.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`)as name 
					FROM `institution_user_credential` WHERE 
					`INSTITUTION_USER_ID` = %s""",(student_id))
				student_name = cur.fetchone()
				if student_name:
					studentname = student_name['name']
				else:
					studentname = ''
				sche['student_name'] = studentname
				sche['STATUS'] = studentAttendanceDtls.get('STATUS')
				sche['subject'] = studentAttendanceDtls.get('subject')

				livelist.append(sche)
		connection.commit()
		cursor.close()
		conn.commit()
		cur.close()

		return ({"attributes": {"status_desc": "Student Attendance Details",
                                "status": "success"
                                },
                 "responseList": livelist}), status.HTTP_200_OK

#---------------------------------------------------------------------#
@name_space.route("/UpdateStudentName")
class UpdateStudentName(Resource):
	@api.expect(updateStudentName)
	def put(self):
		details = request.get_json()
		connection = mysql_connection()
		cursor = connection.cursor()
		
		studentid = details.get('studentid')
		studentname = details.get('studentname')
		teacherid = details.get('teacherid')

		if len(studentname.split(" ")) < 2:
			first_name = studentname
			middle_name = ''
			last_name = ''
			
		elif len(studentname.split(" ")) == 2:
			parsed_name = studentname.split(" ", 1)
			first_name = parsed_name[0]
			middle_name = ''
			last_name = parsed_name[1]
			
		else:
			parsed_name = studentname.split(" ", 2)
			first_name = parsed_name[0]
			middle_name = parsed_name[1]
			last_name = parsed_name[2]
		
		
		credentialData = cursor.execute("""UPDATE `institution_user_credential` SET `FIRST_NAME`=%s,`MIDDLE_NAME`=%s,
			`LAST_NAME`=%s WHERE `INSTITUTION_USER_ID`=%s""",(first_name,middle_name,last_name,studentid))
		
		studentData = cursor.execute("""UPDATE `student_dtls` SET `STUDENT_NAME`=%s,`INSTITUTION_USER_ID_TEACHER`=%s 
			WHERE `INSTITUTION_USER_ID_STUDENT`=%s""",(studentname,teacherid,studentid))
		
		if credentialData and studentData:
			msg = "Updated"

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Update Student Name",
								"status": "success",
								"msg": msg
								},
				"responseList": details}), status.HTTP_200_OK
