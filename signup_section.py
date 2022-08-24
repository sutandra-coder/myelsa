from flask import Flask, request, jsonify, json
from flask_api import status
import datetime
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests
from database_connections import connect_logindb,connect_lab_lang1

app = Flask(__name__)
cors = CORS(app)

signup_section = Blueprint('signup_section_api', __name__)
api = Api(signup_section,  title='Myelsa API',description='Myelsa API')
name_space = api.namespace('SignUpController',description='Sign Up')

addUser = api.model('addUserDto', {
					"address": fields.String(),
					"city": fields.String(),
					"dateOfBirth": fields.String(),
					"emailId": fields.String(),
					"firstName": fields.String(),
					"gender": fields.String(),
					"institutionUserName": fields.String(),
					"institutionUserPassword": fields.String(),
					"institutionUserRole": fields.String(),
					"institutionUserStatus": fields.String(),
					"lastName": fields.String(),
					"middleName": fields.String(),
					"pincode": fields.String(),
					"primaryContactNumber": fields.String(),
					"secondaryContactNumber": fields.String(),
					"state": fields.String(),
					"streetAddress": fields.String(),
					"userEndDate": fields.String(),
					"userEnrollDate": fields.String(),
					"userTaxId": fields.String(),
					"userUniqueId": fields.String(),
					"board": fields.String(),
					"studentname": fields.String(),
					"class": fields.String(),
					"institutionName": fields.String(),
					"institutionId": fields.Integer(),
					"licenseKey": fields.String(),
					"fathers_Name":fields.String()
					})


updateUser = api.model('updateUserDto', {
					"address": fields.String(),
					"city": fields.String(),
					"dateOfBirth": fields.String(),
					"emailId": fields.String(),
					"firstName": fields.String(),
					"gender": fields.String(),
					"institutionUserName": fields.String(),
					"institutionUserPassword": fields.String(),
					"institutionUserRole": fields.String(),
					"institutionUserStatus": fields.String(),
					"lastName": fields.String(),
					"middleName": fields.String(),
					"pincode": fields.String(),
					"primaryContactNumber": fields.String(),
					"secondaryContactNumber": fields.String(),
					"state": fields.String(),
					"streetAddress": fields.String(),
					"userEndDate": fields.String(),
					"userEnrollDate": fields.String(),
					"userTaxId": fields.String(),
					"userUniqueId": fields.String(),
					"board": fields.String(),
					"studentname": fields.String(),
					"class": fields.String(),
					"institutionName": fields.String(),
					"institutionId": fields.Integer(),
					"licenseKey": fields.String(),
					"fathers_Name":fields.String(),
					"image_url":fields.String(),
					"user_id":fields.Integer(),
					"section":fields.String(),
					"studentrollnum":fields.String(),
					"student_type":fields.String(),
					"subscriptiontype":fields.String(),
					})

validateUser = api.model('validateUserDto', {
					"institutionUserName": fields.String(),
					"institutionUserPassword": fields.String()
					})


udpate_password_model = api.model('udpate_password_model', {
					"reset": fields.Integer(),
					"institutionUserPassword": fields.String()
					})

@name_space.route("/userRegistration")
class userRegistration(Resource):
	@api.expect(addUser)
	def post(self):

		connection = connect_logindb()
		cursor = connection.cursor()

		conn = connect_lab_lang1()
		curlang = conn.cursor()

		details = request.get_json()
		address = details.get('address')
		city = details.get('city')
		dateOfBirth = details.get('dateOfBirth')
		emailId = details.get('emailId')
		firstName = details.get('firstName')
		gender = details.get('gender')
		institutionUserName = details.get('institutionUserName')
		institutionUserPassword = details.get('institutionUserPassword')
		institutionUserRole = details.get('institutionUserRole')
		institutionUserStatus = details.get('institutionUserStatus')
		lastName = details.get('lastName')
		middleName = details.get('middleName')
		pincode = details.get('pincode')
		primaryContactNumber = details.get('primaryContactNumber')
		secondaryContactNumber = details.get('secondaryContactNumber')
		state = details.get('state')
		streetAddress = details.get('streetAddress')
		userTaxId = details.get('userTaxId')
		userUniqueId = details.get('userUniqueId')
		board = details.get('board')
		studentname = details.get('studentname')
		clss = details.get('class')
		institutionName = details.get('institutionName')
		institutionId = details.get('institutionId')
		licenseKey = details.get('licenseKey')
		fathers_Name = details.get('fathers_Name')

		current_date = date.today()
		userEnrollDate = str(current_date)
		nextyear_date = current_date.replace(year=current_date.year + 1)
		userEndDate = str(nextyear_date)

		msg = None

		res_dtls = {"STATUS": "",
					"user_id": 0,
					"RESPONSE": ""
					}

		cursor.execute("""SELECT `INSTITUTION_USER_ID` FROM `institution_user_credential` 
			WHERE `INSTITUTION_USER_NAME` = %s""",(details.get('institutionUserName')))


		useridDetails = cursor.fetchone()
		print(useridDetails)
		if institutionUserRole in ['S1','T1','TA','A1','G1']:
			if not useridDetails:

				res_dtls = {"STATUS": "User Added",
							"user_id": 0,
								"Response": {
								"status": "Success",
								"UserId": 0
								}
							}

				credentialInsertQuery = ("""INSERT INTO `institution_user_credential`(`CITY`, 
					`DATE_OF_BIRTH`, `EMAIL_ID`, `FIRST_NAME`, `GENDER`, 
					`INSTITUTION_USER_NAME`, `INSTITUTION_USER_PASSWORD`, `LAST_NAME`, `MIDDLE_NAME`, 
					`PINCODE`, `PRIMARY_CONTACT_NUMBER`, `SECONDARY_CONTACT_NUMBER`, `STATE`, 
					`STREET_ADDRESS`, `USER_TAX_ID`, `USER_UNIQUE_ID`, 
					`address`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")


				credentialData = (city,dateOfBirth,emailId,firstName,gender,institutionUserName,institutionUserPassword,
					lastName,middleName,pincode,primaryContactNumber,secondaryContactNumber,state,streetAddress,
					userTaxId,userUniqueId,address)


				cursor.execute(credentialInsertQuery,credentialData)

				InstiUserID = cursor.lastrowid
				details['institution_user_id'] = InstiUserID

				res_dtls['user_id'] = InstiUserID
				res_dtls['Response']['UserId'] = InstiUserID

				credentialMasterQuery = ("""INSERT INTO `institution_user_credential_master`(`INSTITUTION_ID`, 
					`INSTITUTION_USER_ID`, `INSTITUTION_USER_ROLE`, `INSTITUTION_USER_STATUS`, 
					`INSTITUTION_NAME`, `USER_ENROLL_DATE`, 
					`USER_END_DATE`) VALUES (%s,%s,%s,%s,%s,%s,%s)""")


				masterData = (institutionId,InstiUserID,institutionUserRole,institutionUserStatus,institutionName,
					userEnrollDate,userEndDate)

				cursor.execute(credentialMasterQuery,masterData)

				lastUpdateTS = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
				curlang.execute("""INSERT INTO `student`(`Student_ID`, `Student_UserID`, `Class`, 
					`Level`, `Student_Addition_TS`, `Status`, `Last_Update_ID`, `Last_Update_TS`, 
					`Board`) VALUES 
					(%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(InstiUserID,InstiUserID,clss,0,lastUpdateTS,
						0,None,lastUpdateTS,board))

				if institutionUserRole == 'S1':
					studentInsertQuery = ("""INSERT INTO `student_dtls`(`INSTITUTION_ID`, 
						`INSTITUTION_USER_ID_STUDENT`, `CLASS`, 
						`CLASS_START_DATE`, `CLASS_END_DATE`,`STUDENT_NAME`, 
						`Fathers_Name`, `Board`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""")

					studentData = (institutionId,InstiUserID,clss,userEnrollDate,userEndDate,
						firstName+' '+lastName,fathers_Name,board)


					cursor.execute(studentInsertQuery,studentData)


				elif institutionUserRole == 'T1' or institutionUserRole == 'TA':

					teacherInsertQuery = ("""INSERT INTO `teacher_dtls`(`INSTITUTION_ID`, 
						`INSTITUTION_USER_ID_TEACHER`) VALUES (%s,%s)""")

					teacherData = (institutionId,InstiUserID)

					cursor.execute(teacherInsertQuery,teacherData)

				elif institutionUserRole == 'A1':
					adminInsertQuery = ("""INSERT INTO `admin_dtls`(`INSTITUTION_ID`, 
						`INSTITUTION_USER_ID_ADMIN`, `ADMIN_TYPE`) VALUES (%s,%s,%s)""")

					adminData = (institutionId,InstiUserID,'A1')

					cursor.execute(adminInsertQuery,adminData)

			else:
				msg = 'User Already exists'
				res_dtls = {"STATUS": "failure",
					"user_id": useridDetails['INSTITUTION_USER_ID'],
					"RESPONSE": msg
					}

		else:
			msg = 'Invalid user role'
			res_dtls = {"STATUS": "failure",
					"user_id": 0,
					"RESPONSE": msg
					}

		connection.commit()
		cursor.close()

		conn.commit()
		curlang.close()
		return ({"attributes": {"status_desc": "Registration Details",
								"status": "success"
								},
				"responseList": res_dtls}), status.HTTP_200_OK



@name_space.route("/ProfileUpdate")
class ProfileUpdate(Resource):
	@api.expect(updateUser)
	def put(self):

		connection = connect_logindb()
		cursor = connection.cursor()
		
		conn = connect_lab_lang1()
		curlang = conn.cursor()

		details = request.get_json()
		user_id = details.get('user_id')

		institutionId = details.get('institutionId')
		
		address = details.get('address')
		if address is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `address` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(address,user_id))
		city = details.get('city')
		if city is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `CITY` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(city,user_id))
		dateOfBirth = details.get('dateOfBirth')
		if dateOfBirth is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `DATE_OF_BIRTH` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(dateOfBirth,user_id))
		emailId = details.get('emailId')
		if emailId is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `EMAIL_ID` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(emailId,user_id))
		firstName = details.get('firstName')
		if firstName is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `FIRST_NAME` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(firstName,user_id))
		gender = details.get('gender')
		if gender is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `GENDER` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(gender,user_id))
		institutionUserName = details.get('institutionUserName')
		if institutionUserName is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `INSTITUTION_USER_NAME` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(institutionUserName,user_id))
		# institutionUserPassword = details.get('institutionUserPassword')
		# if institutionUserPassword is not None:
		# 	cursor.execute("""UPDATE `institution_user_credential` SET `INSTITUTION_USER_PASSWORD` = %s 
		# 		WHERE `INSTITUTION_USER_ID` = %s""",(institutionUserPassword,user_id))
		institutionUserRole = details.get('institutionUserRole')
		if institutionUserRole is not None:
			cursor.execute("""UPDATE `institution_user_credential_master` SET `INSTITUTION_USER_ROLE` = %s 
				where `INSTITUTION_ID` = %s and `INSTITUTION_USER_ID` = %s""",(institutionUserRole,
					institutionId,user_id))
		institutionUserStatus = details.get('institutionUserStatus')
		if institutionUserStatus is not None:
			cursor.execute("""UPDATE `institution_user_credential_master` SET `INSTITUTION_USER_STATUS` = %s 
				where `INSTITUTION_ID` = %s and `INSTITUTION_USER_ID` = %s""",(institutionUserStatus,
					institutionId,user_id))
		lastName = details.get('lastName')
		if lastName is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `LAST_NAME` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(lastName,user_id))
		middleName = details.get('middleName')
		if middleName is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `MIDDLE_NAME` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(middleName,user_id))
		pincode = details.get('pincode')
		if pincode is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `PINCODE` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(pincode,user_id))
		primaryContactNumber = details.get('primaryContactNumber')
		if primaryContactNumber is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `PRIMARY_CONTACT_NUMBER` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(primaryContactNumber,user_id))
		secondaryContactNumber = details.get('secondaryContactNumber')
		if secondaryContactNumber is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `SECONDARY_CONTACT_NUMBER` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(secondaryContactNumber,user_id))
		state = details.get('state')
		if state is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `STATE` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(state,user_id))
		streetAddress = details.get('streetAddress')
		if streetAddress is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `STREET_ADDRESS` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(streetAddress,user_id))
		userTaxId = details.get('userTaxId')
		if userTaxId is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `USER_TAX_ID` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(userTaxId,user_id))
		userUniqueId = details.get('userUniqueId')
		if userUniqueId is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `USER_UNIQUE_ID` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(userUniqueId,user_id))
		board = details.get('board')
		if board is not None:
			cursor.execute("""UPDATE `student_dtls` SET `Board` = %s WHERE `INSTITUTION_ID` = %s 
				and `INSTITUTION_USER_ID_STUDENT` = %s""",(board,institutionId,user_id))
			curlang.execute("""UPDATE `student` SET `Board` = %s WHERE `Student_UserID` = %s""",(board,user_id))
		studentname = details.get('studentname')
		if studentname is not None:
			cursor.execute("""UPDATE `student_dtls` SET `STUDENT_NAME` = %s WHERE `INSTITUTION_ID` = %s 
				and `INSTITUTION_USER_ID_STUDENT` = %s""",(studentname,institutionId,user_id))
		clss = details.get('class')
		if clss is not None:
			cursor.execute("""UPDATE `student_dtls` SET `CLASS` = %s WHERE `INSTITUTION_ID` = %s 
				and `INSTITUTION_USER_ID_STUDENT` = %s""",(clss,institutionId,user_id))
			curlang.execute("""UPDATE `student` SET `Class` = %s WHERE `Student_UserID` = %s""",(clss,user_id))
		institutionName = details.get('institutionName')
		if institutionName is not None:
			cursor.execute("""UPDATE `institution_user_credential_master` SET `INSTITUTION_NAME` = %s 
				where `INSTITUTION_ID` = %s and `INSTITUTION_USER_ID` = %s""",(institutionName,
					institutionId,user_id))
		
		# licenseKey = details.get('licenseKey')
		# if licenseKey is not None:
		# 	cursor.execute("""UPDATE `institution_user_credential` SET `address` = %s 
		# 		WHERE `INSTITUTION_USER_ID` = %s""",(licenseKey,user_id))
		fathers_Name = details.get('fathers_Name')
		if fathers_Name is not None:
			cursor.execute("""UPDATE `student_dtls` SET `Fathers_Name` = %s WHERE `INSTITUTION_ID` = %s 
				and `INSTITUTION_USER_ID_STUDENT` = %s""",(fathers_Name,institutionId,user_id))
		image_url = details.get('image_url')
		if image_url is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `IMAGE_URL` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(image_url,user_id))
			cursor.execute("""UPDATE `student_dtls` SET `Image_URL` = %s WHERE `INSTITUTION_ID` = %s 
				and `INSTITUTION_USER_ID_STUDENT` = %s""",(image_url,institutionId,user_id))
		section = details.get('section')
		if section is not None:
			cursor.execute("""UPDATE `student_dtls` SET `SEC` = %s WHERE `INSTITUTION_ID` = %s 
				and `INSTITUTION_USER_ID_STUDENT` = %s""",(section,institutionId,user_id))
		studentrollnum = details.get('studentrollnum')
		if studentrollnum is not None:
			cursor.execute("""UPDATE `student_dtls` SET `STUDENT_ROLL_NUM` = %s WHERE `INSTITUTION_ID` = %s 
				and `INSTITUTION_USER_ID_STUDENT` = %s""",(studentrollnum,institutionId,user_id))
		student_type = details.get('student_type')
		if student_type is not None:
			cursor.execute("""UPDATE `student_dtls` SET `STUDENT_TYPE` = %s WHERE `INSTITUTION_ID` = %s 
				and `INSTITUTION_USER_ID_STUDENT` = %s""",(student_type,institutionId,user_id))
		subscriptiontype = details.get('subscriptiontype')
		if subscriptiontype is not None:
			cursor.execute("""UPDATE `student_dtls` SET `SUBCRIPTION_TYPE` = %s WHERE `INSTITUTION_ID` = %s 
				and `INSTITUTION_USER_ID_STUDENT` = %s""",(subscriptiontype,institutionId,user_id))
		
		connection.commit()
		conn.commit()
		cursor.close()
		curlang.close()

		return ({"attributes": {"status_desc": "Profile Update Details",
								"status": "success"
								},
				"responseList": details}), status.HTTP_200_OK



@name_space.route("/validateUserPassword")
class validateUserPassword(Resource):
	@api.expect(validateUser)
	def post(self):

		connection = connect_logindb()
		cursor = connection.cursor()

		details = request.get_json()
		username = details.get('institutionUserName')
		password = details.get('institutionUserPassword')
		userInstiDtls = []
		fullUserDtls = {}
		cursor.execute("""SELECT `INSTITUTION_USER_ID` FROM `institution_user_credential` WHERE 
			`INSTITUTION_USER_NAME` = %s and `INSTITUTION_USER_PASSWORD` = %s""",(username,password))


		userDtls = cursor.fetchone()

		if not userDtls:
			msg = 'UserId/Password not validated'
		else:
			msg = 'User Exists and Pasword Validated'

			cursor.execute("""SELECT `CITY` as 'city',`DATE_OF_BIRTH` as 'dateOfBirth',`EMAIL_ID` as 'emailId',
				`FIRST_NAME` as 'firstName',`GENDER` as 'gender',`IMAGE_URL` as 'imageUrl',
				`INSTITUTION_USER_PASSWORD` as 'institutionUserPassword',`RESET` as 'reset',`LAST_NAME` as 'lastName',
				`LAST_UPDATE_ID` as 'lastUpdateId',`LAST_UPDATE_TIMESTAMP` as 'lastUpdateTimestamp',
				`MIDDLE_NAME` as 'middleName',`PINCODE` as 'pincode',`PRIMARY_CONTACT_NUMBER` as 'primaryContactNumber',
				`SECONDARY_CONTACT_NUMBER` as 'secondaryContactNumber',`STATE` as 'state',
				`STREET_ADDRESS` as 'streetAddress',`USER_TAX_ID` as 'userTaxId',
				`USER_UNIQUE_ID` as 'userUniqueId',`address`,`INSTITUTION_USER_ID` as 'institutionUserId',
				`INSTITUTION_USER_NAME` as 'institutionUserName'
				FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(userDtls.get('INSTITUTION_USER_ID')))

			fullUserDtls = cursor.fetchone()
			fullUserDtls['lastUpdateTimestamp'] = fullUserDtls['lastUpdateTimestamp'].isoformat()
			if isinstance(fullUserDtls['dateOfBirth'], date):
				fullUserDtls['dateOfBirth'] = fullUserDtls['dateOfBirth'].isoformat()
			fullUserDtls['institutionUserRoles'] = []
			cursor.execute("""SELECT `INSTITUTION_ID` as 'institutionId',`INSTITUTION_USER_ROLE` as 'roleId',
				`INSTITUTION_NAME` as 'institutionName'	FROM `institution_user_credential_master` 
				WHERE `INSTITUTION_USER_ID` = %s""",(userDtls.get('INSTITUTION_USER_ID')))


			userInstiDtls = cursor.fetchall()

			for uid, insti in enumerate(userInstiDtls):
				cursor.execute("""SELECT `INSTITUTION_NAME`,`INSTITUTION_LOGO` FROM
				 `institution_dtls` WHERE `INSTITUTION_ID` = %s""",insti.get('institutionId',1))
				instiNameLogoDtls = cursor.fetchone()

				if instiNameLogoDtls:
					insti['main_institute_name'] = instiNameLogoDtls.get('INSTITUTION_NAME','')
					insti['main_institute_logo'] = instiNameLogoDtls.get('INSTITUTION_LOGO','')

				if insti.get('roleId') == 'S1':
					cursor.execute("""SELECT STUDENT_TYPE,`CLASS` as 'studentClass',`Fathers_Name` as 'fathersName',
						`Board` as 'board' FROM `student_dtls` WHERE `INSTITUTION_USER_ID_STUDENT` = %s 
						and `INSTITUTION_ID` = %s""",(userDtls.get('INSTITUTION_USER_ID'),insti.get('institutionId')))
					studentdtls = cursor.fetchone()
					if studentdtls['STUDENT_TYPE'] != None:
						insti['student_type'] = studentdtls['STUDENT_TYPE']
					else:
						insti['student_type'] = ""

					insti['studentClass'] = studentdtls.get('studentClass')
					insti['fathersName'] = studentdtls.get('fathersName')
					insti['board'] = studentdtls.get('board')
					insti['description'] = 'Student'
				elif insti.get('roleId') == 'TA':
					
					cursor.execute("""SELECT `INSTITUTION_USER_ID_TEACHER` FROM `teacher_dtls` WHERE 
						`INSTITUTION_USER_ID_TEACHER` = %s 
						AND `INSTITUTION_ID` = %s""",(userDtls.get('INSTITUTION_USER_ID'),insti.get('institutionId')))
					
					teacherDtls = cursor.fetchone()
					insti['studentClass'] = None
					insti['fathersName'] = None
					insti['board'] = None
					insti['description'] = None
			fullUserDtls['institutionUserRoles'] = userInstiDtls
			fullUserDtls['avatar'] = None
		return ({"attributes": {"status_desc": msg,
								"student_details":fullUserDtls,
								"status": "success"
								},
				"responseDataTO": {}}), status.HTTP_200_OK


@name_space.route("/updatePassword/<int:user_id>")
class updatePassword(Resource):
	@api.expect(udpate_password_model)
	def put(self,user_id):

		connection = connect_logindb()
		cursor = connection.cursor()

		details = request.get_json()
		# reset = details.get('reset')
		institutionUserPassword = details.get('institutionUserPassword')

		# cursor.execute("""SELECT `RESET` FROM `institution_user_credential` WHERE 
		# 	`INSTITUTION_USER_ID` = %s""",(user_id))

		# resetDtls = cursor.fetchone()

		# reset = int(resetDtls.get('RESET',0)) + 1

		cursor.execute("""UPDATE `institution_user_credential` SET `RESET` = %s, INSTITUTION_USER_PASSWORD = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(1,institutionUserPassword,user_id))

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Password Update Details",
								"status": "success"
								},
				"responseList": 'Password updated'}), status.HTTP_200_OK