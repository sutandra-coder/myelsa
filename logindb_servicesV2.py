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
import utils
from threading import Thread
import time
from database_connections import connect_logindb,connect_lab_lang1,connect_userLibrary

app = Flask(__name__)
cors = CORS(app)


logindb_controllerV2 = Blueprint('logindb_controllerV2_api', __name__)
api = Api(logindb_controllerV2,  title='Myelsa API',description='Myelsa API')
name_space = api.namespace('logindbControllerV2',description='Logindb ControllerV2')

BASE_URL_AWS = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/'
BASE_URL_JAVA = 'http://creamsonservices.com:8080/'

@name_space.route("/getStudentListByInstitutionIdAndClass/<int:institution_id>/<string:clss>")
class studentListByInstitutionIdAndClass(Resource):
	def get(self,institution_id,clss):
		connection = connect_logindb()
		cursor = connection.cursor()
		cursor.execute("""SELECT institution_user_credential.`INSTITUTION_USER_ID`,concat(`FIRST_NAME`,
        ' ',`LAST_NAME`) as name,`PRIMARY_CONTACT_NUMBER`, `INSTITUTION_NAME`,`INSTITUTION_USER_ROLE`,
        `CLASS` as classs,`Board`,`institution_user_credential`. `LAST_UPDATE_TIMESTAMP` FROM 
        `institution_user_credential`,`institution_user_credential_master`,student_dtls WHERE 
        institution_user_credential_master.`INSTITUTION_USER_ID` in(SELECT `INSTITUTION_USER_ID` 
        FROM `institution_user_credential`) and institution_user_credential.`INSTITUTION_USER_ID`
        =institution_user_credential_master.`INSTITUTION_USER_ID` and 
        institution_user_credential_master.`INSTITUTION_USER_ID`=student_dtls.
        INSTITUTION_USER_ID_STUDENT and institution_user_credential_master.
        `INSTITUTION_ID`=%s and `INSTITUTION_USER_ROLE`='S1' and student_dtls.CLASS=%s""",
           (institution_id,clss))
        
		student_list = cursor.fetchall()
      
		for i in range(len(student_list)):
			student_list[i]['LAST_UPDATE_TIMESTAMP'] = student_list[i]['LAST_UPDATE_TIMESTAMP'].isoformat()
            

		cursor.close()
		return ({"attributes": {"status_desc": "Student Details.",
								"status": "success"
								},
				"responseList": student_list}), status.HTTP_200_OK


@name_space.route("/getGroupById/<int:group_id>")
class GetgroupbyId(Resource):
	def get(self,group_id):
		connection = connect_logindb()
		cursor = connection.cursor()

		cursor.execute("""SELECT gsm.`Student_Id`,gsm.`LAST_UPDATE_ID`,gm.`Group_ID`,gm.`Group_Description`,
			sd.`STUDENT_NAME`,sd.`Image_URL`,sd.`CLASS`,sd.`Board`
			FROM group_master gm LEFT JOIN group_student_mapping gsm ON gm.`Group_ID` = gsm.`Group_ID`
			LEFT JOIN student_dtls sd ON gsm.`Student_Id` = sd.`INSTITUTION_USER_ID_STUDENT` 
			AND sd.`Institution_ID` = gm.`INSTITUTION_ID`
			WHERE gm.`Group_ID` = %s ORDER BY gm.`Group_ID`""",(group_id))

		group_dtls = cursor.fetchall()
		cursor.close()
		return ({"attributes":{"status_desc": "Group Details.",
							"status": "success"
						},
			"responseList": group_dtls}), status.HTTP_200_OK

@name_space.route("/getStudentListByInstitutionIdAndClassAndBoard/<int:institution_id>/<string:clss>/<string:board>")
class getStudentListByInstitutionIdAndClassAndBoard(Resource):
	def get(self,institution_id,clss,board):
		connection = connect_logindb()
		cursor = connection.cursor()
		cursor.execute("""SELECT institution_user_credential.`INSTITUTION_USER_ID`,
			concat(`FIRST_NAME`,' ',`LAST_NAME`) as name,`PRIMARY_CONTACT_NUMBER`,
			`INSTITUTION_NAME`,`INSTITUTION_USER_ROLE`,`CLASS` as class,`Board`,
			student_dtls.`Image_URL` FROM `institution_user_credential`
			INNER JOIN `institution_user_credential_master` ON 
			institution_user_credential.`INSTITUTION_USER_ID`= institution_user_credential_master.`INSTITUTION_USER_ID` 
			INNER JOIN student_dtls ON 
			institution_user_credential_master.`INSTITUTION_USER_ID`= student_dtls.`INSTITUTION_USER_ID_STUDENT` 
			AND institution_user_credential_master.`INSTITUTION_ID` = student_dtls.`INSTITUTION_ID` 
			WHERE `INSTITUTION_USER_ROLE` = 'S1' and student_dtls.`CLASS`= %s 
			AND student_dtls.`INSTITUTION_ID`= %s AND student_dtls.`Board` = %s """,(clss,institution_id,board))
        
		student_list = cursor.fetchall()

		cursor.close()
		return ({"attributes": {"status_desc": "Student Details.",
								"status": "success"
								},
				"responseList": student_list}), status.HTTP_200_OK

def delStudentFromGroup(institution_id,student_id):
	connection = connect_logindb()
	cursor = connection.cursor()
	try:
		delSidFromGroup = ("""DELETE FROM `group_student_mapping` WHERE `Group_ID` in 
			(SELECT `Group_ID` FROM `group_master` WHERE `Institution_ID` = %s) 
			and `Student_Id` = %s""")

		delData = (institution_id,student_id)
		cursor.execute(delSidFromGroup,delData)
		connection.commit()
		cursor.close()
	except Exception as e:
		return e

	return 'updated'

def delStudentInstitutionID(institution_id,student_id):
	connection = connect_logindb()
	cursor = connection.cursor()
	try:
		delStudentDtls = ("""DELETE FROM `student_dtls` WHERE `INSTITUTION_ID` = %s 
			and `INSTITUTION_USER_ID_STUDENT` = %s""")

		delInstitutionMaster = ("""DELETE FROM `institution_user_credential_master` WHERE 
			`INSTITUTION_ID` = %s and `INSTITUTION_USER_ID` = %s""")

		delData = (institution_id,student_id)
		cursor.execute(delStudentDtls,delData)
		cursor.execute(delInstitutionMaster,delData)
		connection.commit()
		cursor.close()
		# groupRes = delStudentFromGroup(institution_id,student_id)
	except Exception as e:
		return e

	return 'updated'

@name_space.route("/deleteStudentfromInstitution/<int:institution_id>/<int:student_id>")
class deleteStudentfromInstitution(Resource):
	def put(self,institution_id,student_id):
		connection = connect_logindb()
		cursor = connection.cursor()

		cursor.execute("""SELECT icm.`INSTITUTION_ID` FROM `institution_user_credential_master` icm
			INNER JOIN `student_dtls` sd on icm.`INSTITUTION_USER_ID` = sd.`INSTITUTION_USER_ID_STUDENT`
			and icm.`INSTITUTION_ID` = sd.`INSTITUTION_ID`
			WHERE icm.`INSTITUTION_USER_ID` = %s and icm.`INSTITUTION_ID` = 1""",(student_id))

		studentDtls = cursor.fetchall()
		res = 'Student could not be removed.'

		if not studentDtls:
			updateInstitutionMaster = ("""UPDATE `institution_user_credential_master` SET 
				`INSTITUTION_ID` = %s,`LAST_UPDT_ID` = %s where 
				`INSTITUTION_USER_ID` = %s and `INSTITUTION_ID` = %s""")

			updateStudentDtls = ("""UPDATE `student_dtls` SET `INSTITUTION_ID`= %s,`LAST_UPDATE_ID` = %s 
				WHERE `INSTITUTION_USER_ID_STUDENT` = %s and `INSTITUTION_ID` = %s""")


			updateData = (1,institution_id,student_id,institution_id)

			cursor.execute(updateInstitutionMaster,updateData)
			cursor.execute(updateStudentDtls,updateData)
			connection.commit()
			# groupRes = delStudentFromGroup(institution_id,student_id)
			res = 'Student Removed.'
		else:
			delRes = delStudentInstitutionID(institution_id,student_id)
			
			if delRes == 'updated':
				res = 'Student Removed.'

		cursor.close()

		return ({"attributes": {"status_desc": "Student Details.",
								"status": "success"
								},
				"responseList": res}), status.HTTP_200_OK


def syncingLiveClass(request):
	institution_id,teacher_id = request
	conn = connect_userLibrary()
	curLib = conn.cursor()
	
	liveId, meetId,platform = utils.getLiveClassIdByTeacherId(teacher_id)
	classStudentMapInsertQuery = ("""INSERT INTO `liveclass_student_mapping`(`liveclass_id`, 
		`student_id`,`platform`) VALUES (%s,%s,%s)""")
		
	for mid in range(len(meetId)):

		groupList = utils.getAssignedGroupsByMeetingId(meetId[mid])
		studentList = utils.getStudentListFromGroupid(groupList)
		sList = utils.getStudentListByLiveClassId(liveId[mid])
		unsyncList = set(studentList).difference(set(sList))
		unsyncList = list(unsyncList)
		if unsyncList:
			for i in unsyncList:
				classStudentData = (liveId[mid],i,platform[mid])
				curLib.execute(classStudentMapInsertQuery,classStudentData)

	conn.commit()
	curLib.close()


def syncingAssignment(request):
	institution_id,teacher_id = request
	conn = connect_lab_lang1()
	curLib = conn.cursor()
	
	assignmentList = utils.getAssignmentIdByTeacherId(teacher_id)
	assignStudentMapInsertQuery = ("""INSERT INTO `assignment_mapping`(`Assignment_ID`, 
		`Student_UserID`, `Status`, `DUE_DATE`) VALUES (%s,%s,%s,%s)""")
		
	for aid in range(len(assignmentList)):

		groupList = utils.getAssignedGroupsByAssignmentId(assignmentList[aid])
		studentList = utils.getStudentListFromGroupid(groupList)
		sList = utils.getStudentListByAssigmentId(assignmentList[aid])
		unsyncList = set(studentList).difference(set(sList))
		unsyncList = list(unsyncList)
		if unsyncList:
			for i in unsyncList:
				assignStudentData = (assignmentList[aid],i,'w',None)
				curLib.execute(assignStudentMapInsertQuery,assignStudentData)

	conn.commit()
	curLib.close()
	
class Compute(Thread):
	def __init__(self, request, funcname):
		Thread.__init__(self)
		self.request = request
		self.funcname = funcname

	def run(self):
		time.sleep(5)
		if self.funcname == 'syncLiveClass':
			syncingLiveClass(self.request)
		elif self.funcname == 'syncAssignment':
			syncingAssignment(self.request)
		else:
			pass


@name_space.route("/syncLiveClass/<int:institution_id>/<int:teacher_id>")
class syncLiveClass(Resource):
	def post(self,institution_id,teacher_id):
		sendrReq = (institution_id,teacher_id)
		thread_a = Compute(sendrReq,'syncLiveClass')
		thread_a.start()
		return ({"attributes": {"status_desc": "Sync Details.",
								"status": "success"
								},
				"responseList": 'Sync process started'}), status.HTTP_200_OK

@name_space.route("/syncAssignment/<int:institution_id>/<int:teacher_id>")
class syncAssignment(Resource):
	def post(self,institution_id,teacher_id):
		sendrReq = (institution_id,teacher_id)
		thread_a = Compute(sendrReq,'syncAssignment')
		thread_a.start()
		return ({"attributes": {"status_desc": "Sync Details.",
								"status": "success"
								},
				"responseList": 'Sync process started'}), status.HTTP_200_OK


@name_space.route("/syncAll/<int:institution_id>/<int:teacher_id>")
class syncAll(Resource):
	def post(self,institution_id,teacher_id):
		liveclassUrl = BASE_URL_AWS + 'logindb_section/logindbController/syncLiveClass/{}/{}'.format(institution_id,teacher_id)
		assignmentURL = BASE_URL_AWS + 'logindb_section/logindbController/syncAssignment/{}/{}'.format(institution_id,teacher_id)
		
		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		r1 = requests.post(liveclassUrl, headers=headers)
		r2 = requests.post(assignmentURL, headers=headers)

		return ({"attributes": {"status_desc": "Sync Details.",
								"status": "success"
								},
				"responseList": 'Sync process started'}), status.HTTP_200_OK


@name_space.route("/createInstitute/<int:teacher_id>/<string:institution_name>")
class createInstitute(Resource):
	def post(self,teacher_id,institution_name):
		connection = connect_logindb()
		cursor = connection.cursor()

		updateName = ("""UPDATE `institution_user_credential_master` SET `INSTITUTION_NAME` = %s 
			WHERE `INSTITUTION_USER_ID` = %s""")

		cursor.execute(updateName,(institution_name,teacher_id))
		connection.commit()

		insti_post_url = BASE_URL_AWS+'onboarding_teachers/OnboardTeacher/createInstitute'
		insti_post_data = {"institution_user_id":teacher_id}
		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		insti_post_res = requests.post(insti_post_url, data=json.dumps(insti_post_data),headers=headers)
		res = insti_post_res.json()
		product_code = 'MEI12'
		cursor.execute("""SELECT `Product_CODE`,`Product_Desc`,`Dashboard_ID`,
				`Activity_ID`,`Activity_Type`,`Product_Image_Path`,`Product_Price`, 
				`GST_Value`,`SGST_Value`,`CGST_Value`,`Delivery_Charges`, 
				`Delivery_Charges_Waived_Flag`,`Period_Type`,`Period_Duration` 
				FROM `product` WHERE `Product_CODE` = %s""",(product_code))

		productDtls = cursor.fetchone()
		# print(productDtls)
		# if productDtls:

		cursor.execute("""SELECT `FIRST_NAME` FROM `institution_user_credential` 
			WHERE `INSTITUTION_USER_ID` =%s""",(teacher_id))
		username = cursor.fetchone()

		productDtls['Delivery_Charges'] = productDtls.get('Delivery_Charges',0)
		# print(productDtls['Delivery_Charges'])

		post_url = BASE_URL_JAVA+'CreamsonWorksheetServices/InsertTransactionPayment'
		post_data = {
				  "addressId": 0,
				  "bankTransactionID": "",
				  "invoiceDetail": {
				    "addressLine1": "Cash Transaction",
				    "addressLine2": "",
				    "addressLine3": "",
				    "amount": productDtls.get('Product_Price',0),
				    "amountInwords": "",
				    "buyersAddressLine1": "",
				    "buyersAddressLine2": "",
				    "buyersCode": "",
				    "buyersCompanyName": "",
				    "buyersGstinOrUin": "",
				    "buyersStateName": "",
				    "cgstAmount": productDtls.get('CGST_Value',0),
				    "cgstRate": "",
				    "companyCode": "",
				    "companyGstin": "",
				    "companyGstinOrUin": "",
				    "companyName": "myElsa",
				    "companyStatename": "",
				    "companysPan": "",
				    "dated": "",
				    "descriptionOfGoods": productDtls.get('Product_Desc'),
				    "descriptionSerial": "",
				    "invoiceNo": "",
				    "sgstAmount": productDtls.get('SGST_Value',0),
				    "sgstRate": "",
				    "supplierRef": "",
				    "taxAmountInWords": "",
				    "total": "",
				    "totalTaxAmount": int(productDtls.get('SGST_Value')) + int(productDtls.get('CGST_Value'))
				  },
				  "paymentMode": "Cash",
				  "productCODE": productDtls.get('Product_CODE'),
				  "productDetails": productDtls.get('Product_Desc'),
				  "transactionAmount": productDtls.get('Product_Price'),
				  "userId": teacher_id
				}
		
		post_response = requests.post(post_url, data=json.dumps(post_data), headers=headers)
		r = post_response.json()
		print(r)
		payment_transaction_id = r['TransactionId']
		order_id = r['OrderId']
		# print(payment_transaction_id,order_id)
		update_url = BASE_URL_JAVA+'CreamsonWorksheetServices/updatePaymentTransaction/{}/{}'.format(payment_transaction_id,order_id)
		update_data = {"bankTransactionID": 'Cash',
						"remarks": "Txn Success",
						"transactionStatus": "C"
						}
		update_params = {'paymentTrnsactionId': payment_transaction_id,
						'orderId':order_id}
		update_response = requests.put(update_url,data = json.dumps(update_data),headers = headers)
		r1 = update_response.json()
		print(r1)
		try:
			sourceApp = 'ELSATUTOR'
			url = BASE_URL_JAVA+'CommunicationModule2/sendMailMessage'
			msgdata = {
					  'mailDetails': [
					    {
					      'appParams': {},
					      'mailParams': {"username":username.get('FIRST_NAME')},
					      'role': 's1',
					      'toMail': '',
					      'toNumber': '',
					      'userId': teacher_id
					    }
					  ],
					  'sourceApp': sourceApp
					}
			response = requests.post(url, data=json.dumps(msgdata), headers=headers)
		except:
			pass
		return res


def delTeacherInstitutionID(institution_id,teacher_id):
	connection = connect_logindb()
	cursor = connection.cursor()
	try:
		delTeacherDtls = ("""DELETE FROM `teacher_dtls` WHERE `INSTITUTION_ID` = %s 
			and `INSTITUTION_USER_ID_TEACHER` = %s""")

		delInstitutionMaster = ("""DELETE FROM `institution_user_credential_master` WHERE 
			`INSTITUTION_ID` = %s and `INSTITUTION_USER_ID` = %s""")

		delData = (institution_id,teacher_id)
		cursor.execute(delTeacherDtls,delData)
		cursor.execute(delInstitutionMaster,delData)
		connection.commit()
		cursor.close()
	except Exception as e:
		return e

	return 'updated'


@name_space.route("/deleteTeacherfromInstitution/<int:institution_id>/<int:teacher_id>")
class deleteTeacherfromInstitution(Resource):
	def put(self,institution_id,teacher_id):
		connection = connect_logindb()
		cursor = connection.cursor()

		cursor.execute("""SELECT icm.`INSTITUTION_ID` FROM `institution_user_credential_master` icm 
			INNER JOIN `teacher_dtls` td on icm.`INSTITUTION_USER_ID` = td.`INSTITUTION_USER_ID_TEACHER` 
			and icm.`INSTITUTION_ID` = td.`INSTITUTION_ID` WHERE icm.`INSTITUTION_USER_ID` = %s 
			and icm.`INSTITUTION_ID` = 1""",(teacher_id))

		teacherDtls = cursor.fetchall()
		res = 'Teacher could not be removed.'

		if not teacherDtls:
			updateInstitutionMaster = ("""UPDATE `institution_user_credential_master` SET 
				`INSTITUTION_ID` = %s,`LAST_UPDT_ID` = %s where 
				`INSTITUTION_USER_ID` = %s and `INSTITUTION_ID` = %s""")

			updateTeacherDtls = ("""UPDATE `teacher_dtls` SET `INSTITUTION_ID`= %s,`LAST_UPDATE_ID` = %s 
				WHERE `INSTITUTION_USER_ID_TEACHER` = %s and `INSTITUTION_ID` = %s""")


			updateData = (1,institution_id,teacher_id,institution_id)

			cursor.execute(updateInstitutionMaster,updateData)
			cursor.execute(updateTeacherDtls,updateData)
			connection.commit()
			res = 'Teacher Removed.'
		else:
			delRes = delTeacherInstitutionID(institution_id,teacher_id)
			
			if delRes == 'updated':
				res = 'Teacher Removed.'

		cursor.close()

		return ({"attributes": {"status_desc": "Teacher Details.",
								"status": "success"
								},
				"responseList": res}), status.HTTP_200_OK


@name_space.route("/approveTeacherIntoInstitution/<int:institution_id>/<int:teacher_id>")
class approveTeacherIntoInstitution(Resource):
	def post(self,institution_id,teacher_id):

		connection = connect_logindb()
		cursor = connection.cursor()
		productCodes = []
		resp = []
		msg = 'Product Subscription Unsuccessful'
		cursor.execute("""SELECT icm.`INSTITUTION_ID` FROM `institution_user_credential_master` icm 
			INNER JOIN `teacher_dtls` td on icm.`INSTITUTION_USER_ID` = td.`INSTITUTION_USER_ID_TEACHER` 
			and icm.`INSTITUTION_ID` = td.`INSTITUTION_ID` 
			WHERE icm.`INSTITUTION_USER_ID` = %s""",(teacher_id))

		teacherDtlsList = cursor.fetchall()

		teacherInstiID = next((item['INSTITUTION_ID'] for item in teacherDtlsList if item["INSTITUTION_ID"] == institution_id),None)

		if teacherInstiID == institution_id:
			cursor.execute("""SELECT `ADMIN_ID` FROM `institution_dtls` 
				WHERE `INSTITUTION_ID` = %s""",(institution_id))

			userID = cursor.fetchone()
			if userID:
				adminId = userID.get('ADMIN_ID')
				
				cursor.execute("""SELECT `Product_CODE` FROM `user_subscription` 
					WHERE `User_Id` = %s""",(adminId))

				adminSubDtls = cursor.fetchall()
				if adminSubDtls:
					productCodes = [code.get('Product_CODE') for code in adminSubDtls]

					headers = {'Content-type':'application/json', 'Accept':'application/json'}
					for code in productCodes:
						subUrl = BASE_URL_AWS+'cash_transaction/cashTransactionController/cashTransactionsForProducts/{}/{}'.format(teacher_id,code)
						subResponse = requests.post(subUrl, headers=headers).json()
						subResponse['responseList']['productCode'] = code 
						resp.append(subResponse.get('responseList'))

					msg = 'Product Subscription Successful'
			else:
				msg = 'Admin not Found for the Institution'
		else:
			msg = 'Teacher not Registered in the institution'
		cursor.close()

		return ({"attributes": {"status_desc": "Cash Transaction Details.",
									"status": "success",
									"msg":msg
									},
					"responseList":resp}), status.HTTP_200_OK


@name_space.route("/getTeacherListForApproval/<int:institution_id>/<int:admin_id>")
class getTeacherListForApproval(Resource):
	def get(self,institution_id,admin_id):

		connection = connect_logindb()
		cursor = connection.cursor()

		teacherList = []

		cursor.execute("""SELECT icm.`INSTITUTION_USER_ID` FROM `institution_user_credential_master` icm 
			INNER JOIN `teacher_dtls` td on icm.`INSTITUTION_USER_ID` = td.`INSTITUTION_USER_ID_TEACHER` 
			WHERE icm.`INSTITUTION_ID` = %s AND icm.`INSTITUTION_USER_ID` <> (SELECT `ADMIN_ID` 
			FROM `institution_dtls` WHERE `INSTITUTION_ID` = %s)""",(institution_id,institution_id))


		userListDtls = cursor.fetchall()

		for uid, user in enumerate(userListDtls):

			cursor.execute("""SELECT distinct `User_Id` FROM `user_subscription` WHERE 
				`Product_CODE` in ('MEI3','MEI6','MEI12') and `User_Id` = %s""",(user.get('INSTITUTION_USER_ID')))

			productDtls = cursor.fetchone()

			if not productDtls:
				cursor.execute("""SELECT icm.`INSTITUTION_ID`,icm.`INSTITUTION_USER_ID`, concat(`FIRST_NAME`,' ',`LAST_NAME`) as 'name',
					`PRIMARY_CONTACT_NUMBER`,`IMAGE_URL` FROM `institution_user_credential_master` icm 
					INNER JOIN `teacher_dtls` td on icm.`INSTITUTION_USER_ID` = td.`INSTITUTION_USER_ID_TEACHER` 
					INNER JOIN `institution_user_credential` iuc on icm.`INSTITUTION_USER_ID` = iuc.`INSTITUTION_USER_ID` 
					WHERE icm.`INSTITUTION_USER_ID` = %s""",(user.get('INSTITUTION_USER_ID')))

				teacherDtls = cursor.fetchone()
				teacherList.append(teacherDtls)

		return ({"attributes": {"status_desc": "Approval List of Teacher Details.",
									"status": "success"
									},
					"responseList":teacherList}), status.HTTP_200_OK


@name_space.route("/getDashboardItems/<int:institution_id>/<int:user_id>/<string:role>/<string:start_date>/<string:app_name>")
class getDashboardItems(Resource):
	def get(self,institution_id,user_id,role,start_date,app_name):
		connection = connect_logindb()
		cursor = connection.cursor()

		cursor.execute("""SELECT d.`Dashboard_Id`,d.`Banner_desc`,d.`Banner_Img_Path`,d.`Dashboard_Img_Path`, 
			d.`App_name`,d.`Start_Date`,d.`End_Date`,d.`Last_updated_Ts`,d.`Class`,d.`Board`,d.`Dashboard_Desc`,
			d.`sequence_id` FROM `dashboard` d WHERE (d.`INSTITUTION_USER_ID` = 0 OR d.`INSTITUTION_USER_ID` = %s) 
			AND d.`Start_Date` <= %s AND d.`End_Date` >= %s AND 
			d.`INSTITUTION_USER_ROLE` = %s AND d.`App_name` = %s AND d.`Institution_Id` = 0 
			or d.`Institution_Id` = %s AND(d.`Pincode` IN(SELECT `pincode` FROM `institution_user_credential` 
			WHERE `INSTITUTION_USER_ID` = d.`INSTITUTION_USER_ID`) 
			OR d.`Pincode` = 0) 
			order by d.`sequence_id`""",(user_id,start_date,start_date,role,app_name,institution_id))

		dashboardDtls = cursor.fetchall()

		cursor.execute("""SELECT date(`LAST_UPDATE_TIMESTAMP`) as'user_registration' 
			FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(user_id))

		userResgistrationDate = cursor.fetchone()

		cursor.execute("""SELECT `Coupon_Name` FROM `coupon_dtls` WHERE `Last_update_Id` = %s""",(user_id))

		referralDtls = cursor.fetchone()
		if referralDtls:
			referral = referralDtls.get('Coupon_Name')
		else:
			referral = ''
		for did, dash in enumerate(dashboardDtls):
			dash['Start_Date'] = dash.get('Start_Date').isoformat()
			dash['End_Date'] = dash.get('End_Date').isoformat()
			dash['Last_updated_Ts'] = dash.get('Last_updated_Ts').isoformat()

			cursor.execute("""SELECT `Product_ID`, `Product_CODE`, `Product_Desc`, `Dashboard_ID`, 
				`Activity_ID`, `Activity_Type`, `Product_Image_Path`, `Product_Price`, `GST_Value`, 
				`SGST_Value`, `CGST_Value`, `Discount`, `Delivery_Charges`, 
				`Delivery_Charges_Waived_Flag`, `Start_Date`, `End_Date`, `Period_Type`, 
				`Period_Duration`, `Last_Update_TS`, `Last_Updated_ID` FROM `product` 
				WHERE `Dashboard_ID` = %s""",(dash.get('Dashboard_Id')))

			productDtls = cursor.fetchall()
			for pid, prod in enumerate(productDtls):
				prod['Start_Date'] = prod.get('Start_Date').isoformat()
				prod['End_Date'] = prod.get('End_Date').isoformat()
				prod['Last_Update_TS'] = prod.get('Last_Update_TS').isoformat()
			dash['Product'] = productDtls

			cursor.execute("""SELECT dam.`Mapping_ID`, dam.`Dashboard_ID`, dam.`Activity_ID`, 
				dam.`Activity_Type`, dam.`last_updated_ID`, dam.`Last_updated_TS`, 
				act.`Activity_Description` FROM `dashboard_activity_mapping` dam 
				INNER JOIN `activity_table` act on dam.`Activity_ID` = act.`Activity_ID` 
				AND act.`Activity_Type` = dam.`Activity_Type` 
				WHERE `Dashboard_ID` =  %s""",(dash.get('Dashboard_Id')))

			activityDtls = cursor.fetchall()
			for aid, acti in enumerate(activityDtls):
				acti['Last_updated_TS'] = acti.get('Last_updated_TS').isoformat()
			dash['Activity'] = activityDtls

			dash['user_registration'] = userResgistrationDate['user_registration'].isoformat()


		return ({"attributes": {"status_desc": "Fetched DashBoard",
									"Referral_Code": referral,
									"status": "success"
									},
					"responseList":dashboardDtls}), status.HTTP_200_OK


@name_space.route("/getAppVersion/<int:institution_id>")
class getAppVersion(Resource):
	def get(self,institution_id):

		connection = connect_logindb()
		cursor = connection.cursor()

		cursor.execute("""SELECT `Letsest_Version` FROM `forced_update` 
			WHERE `institution_id` = %s or `institution_id` = 1 order by `institution_id` desc""",(institution_id))

		versionDtls = cursor.fetchone()

		return ({"attributes": {"status_desc": "App version Details",
								"status": "success"
									},
					"responseList":versionDtls}), status.HTTP_200_OK


@name_space.route("/updateUserTaxId/<int:user_id>/<string:tax_id>")
class updateUserTaxId(Resource):
	def put(self,user_id,tax_id):

		connection = connect_logindb()
		cursor = connection.cursor()

		updateTaxId = ("""UPDATE `institution_user_credential` SET `USER_TAX_ID` = %s 
			WHERE `INSTITUTION_USER_ID` = %s""")

		cursor.execute(updateTaxId,(tax_id,user_id))
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Tax Id udpate",
								"status": "success"
									},
					"responseList":'Tax Id updated'}), status.HTTP_200_OK


@name_space.route("/getUserDetails/<int:userId>")
class getUserDetails(Resource):
	def get(self,userId):

		connection = connect_logindb()
		cursor = connection.cursor()
		userInstiDtls = []
		fullUserDtls = {}
		

		cursor.execute("""SELECT `CITY` as 'city',`DATE_OF_BIRTH` as 'dateOfBirth',`EMAIL_ID` as 'emailId',
			`FIRST_NAME` as 'firstName',`GENDER` as 'gender',`IMAGE_URL` as 'imageUrl',
			`INSTITUTION_USER_PASSWORD` as 'institutionUserPassword',`RESET` as 'reset',`LAST_NAME` as 'lastName',
			`LAST_UPDATE_ID` as 'lastUpdateId',`LAST_UPDATE_TIMESTAMP` as 'lastUpdateTimestamp',
			`MIDDLE_NAME` as 'middleName',`PINCODE` as 'pincode',`PRIMARY_CONTACT_NUMBER` as 'primaryContactNumber',
			`SECONDARY_CONTACT_NUMBER` as 'secondaryContactNumber',`STATE` as 'state',
			`STREET_ADDRESS` as 'streetAddress',`USER_TAX_ID` as 'userTaxId',
			`USER_UNIQUE_ID` as 'userUniqueId',`address`,`INSTITUTION_USER_ID` as 'institutionUserId',
			`INSTITUTION_USER_NAME` as 'institutionUserName'
			FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(userId))

		fullUserDtls = cursor.fetchone()
		fullUserDtls['lastUpdateTimestamp'] = fullUserDtls['lastUpdateTimestamp'].isoformat()
		if isinstance(fullUserDtls['dateOfBirth'], date):
				fullUserDtls['dateOfBirth'] = fullUserDtls['dateOfBirth'].isoformat()
		fullUserDtls['institutionUserRoles'] = []
		cursor.execute("""SELECT `INSTITUTION_ID` as 'institutionId',`INSTITUTION_USER_ROLE` as 'roleId',
			`INSTITUTION_NAME` as 'institutionName'	FROM `institution_user_credential_master` 
			WHERE `INSTITUTION_USER_ID` = %s""",(userId))


		userInstiDtls = cursor.fetchall()

		for uid, insti in enumerate(userInstiDtls):
			if insti.get('roleId') == 'S1':
				print('if')
				cursor.execute("""SELECT `CLASS` as 'studentClass',`Fathers_Name` as 'fathersName',
					`Board` as 'board' FROM `student_dtls` WHERE `INSTITUTION_USER_ID_STUDENT` = %s 
					and `INSTITUTION_ID` = %s""",(userId,insti.get('institutionId')))
				studentdtls = cursor.fetchone()
				insti['studentClass'] = studentdtls.get('studentClass')
				insti['fathersName'] = studentdtls.get('fathersName')
				insti['board'] = studentdtls.get('board')
				insti['description'] = 'Student'
			elif insti.get('roleId') == 'TA':
				print('elif')
				cursor.execute("""SELECT `INSTITUTION_USER_ID_TEACHER` FROM `teacher_dtls` WHERE 
					`INSTITUTION_USER_ID_TEACHER` = %s 
					AND `INSTITUTION_ID` = %s""",(userId,insti.get('institutionId')))
				
				teacherDtls = cursor.fetchone()
				insti['studentClass'] = None
				insti['fathersName'] = None
				insti['board'] = None
				insti['description'] = None
		fullUserDtls['institutionUserRoles'] = userInstiDtls
		fullUserDtls['applicationCode'] = None
		return ({"attributes": {"status_desc": 'User Details fetched.',
								"student_details":fullUserDtls,
								"status": "success"
								},
				"responseDataTO": {}}), status.HTTP_200_OK