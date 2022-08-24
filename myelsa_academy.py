from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from werkzeug.utils import cached_property
import requests
import calendar
import json
from threading import Thread
import time

app = Flask(__name__)
cors = CORS(app)

#----------------------database-connection---------------------#
'''def mysql_connection():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='creamson_logindb',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

def user_library():
    connection = pymysql.connect(host='creamsonservices.com',
                                 user='creamson_langlab',
                                 password='Langlab@123',
                                 db='creamson_user_library',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection'''


def mysql_connection():
	connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
	                             user='admin',
	                             password='cbdHoRPQPRfTdC0uSPLt',
	                             db='creamson_logindb',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

def user_library():
    connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
                                 user='admin',
                                 password='cbdHoRPQPRfTdC0uSPLt',
                                 db='creamson_user_library',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

#----------------------database-connection-loginDb---------------------#

myelsa_academy = Blueprint('myelsa_academy_api', __name__)
api = Api(myelsa_academy,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('MyelsaAcademy',description='Myelsa Academy')

BASE_URL = 'http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com/flaskapp/'

addImageUrl = api.model('addImageUrl', {
    "institution_user_id":fields.Integer(),
    "IMAGE_URL":fields.String()
    })

applicantno = api.model('applicantno', {
    "institution_user_id":fields.Integer(),
    "institution_id":fields.Integer()
    })

CourseFolderMapping = api.model('CourseFolderMapping', {
    "teacher_id":fields.Integer(),
    "course_id":fields.Integer(),
    "institution_id":fields.Integer(),
    "folder_id":fields.Integer(),
    "folder_name":fields.String()
    })

admissionfee = api.model('admissionfee', {
    "institution_id":fields.Integer(),
    "user_id":fields.Integer(),
    "payment_mood":fields.String(),
    "actual_amount":fields.Integer(),
    "payment_amount":fields.Integer(),
    "is_pending":fields.String()
    })

examfee = api.model('examfee', {
    "institution_id":fields.Integer(),
    "user_id":fields.Integer(),
    "payment_mood":fields.String(),
    "actual_amount":fields.Integer(),
    "payment_amount":fields.Integer(),
    "is_pending":fields.String()
    })

update_admissionfee = api.model('update_admissionfee', {
	"payment_mood":fields.String(),
    "actual_amount":fields.Integer(),
    "payment_amount":fields.Integer(),
    "is_pending":fields.String()
    })
update_examfee = api.model('update_examfee', {
	"payment_mood":fields.String(),
    "actual_amount":fields.Integer(),
    "payment_amount":fields.Integer(),
    "is_pending":fields.String()
    })

userresult = api.model('userresult', {
	"institution_id":fields.Integer(),
	"institution_user_id":fields.List(fields.Integer()),
	"content_filepath":fields.String(),
	"content_filetype":fields.String(),
	"remarks":fields.String()
	})

uploadresult = api.model('uploadresult', {
	"institution_id":fields.Integer(),
	"institution_user_id":fields.Integer(),
	"title":fields.String(),
	"content_filepath":fields.String()
	})

update_path = api.model('update_path', {
	"title":fields.String(),
	"content_filepath":fields.String()
	})

payumoney_payment = api.model('payumoney_payment', {
	"student_id":fields.Integer(),
	"teacher_id":fields.Integer(),
	"Institution_ID":fields.Integer(),
	"product_desc_id":fields.Integer(),
	"payment_status":fields.String(),
	"payment_Id":fields.Integer(),
	"mode":fields.String(),
	"amount":fields.Integer(),
	"payuMoneyId":fields.Integer(),
	"productinfo":fields.String(),
	"product_desc":fields.String(),
	"postUrl":fields.String(),
	"addedon":fields.String()
	})

payumoney_fee = api.model('payumoney_fee', {
	"student_id":fields.Integer(),
	"teacher_id":fields.Integer(),
	"Institution_ID":fields.Integer(),
	"product_desc_id":fields.Integer(),
	"payment_status":fields.String(),
	"payment_Id":fields.Integer(),
	"mode":fields.String(),
	"amount":fields.Integer(),
	"payuMoneyId":fields.Integer(),
	"product_desc":fields.String(),
	"actual_amount":fields.Integer(),
	"postUrl":fields.String(),
	"addedon":fields.String()
	})

studentdocument = api.model('studentdocument', {
    "group_id":fields.Integer(),
    "document_label":fields.String(), 
    "document_filepath":fields.String(),
    "document_filetype":fields.String(),
    "last_upadte_id":fields.Integer()
    })

online_test_student_model = api.model('SelectOnlineTestStudent', {
	"online_test_id":fields.Integer(),
	"Institution_ID":fields.Integer(),
	"start_time":fields.String(),
	"end_time":fields.String(),
	"teacher_id":fields.Integer()
	})

#---------------------------------------------------------------------------#
@name_space.route("/VerifyFranchaiseUsernamePassword/<string:username>/<string:password>")
class VerifyFranchaiseUsernamePassword(Resource):
	def get(self,username,password):

		connection = mysql_connection()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT franchaise_master.`franchaise_id`,`institution_id`,
			`franchaise_role`,`franchisee_code`,
			`franchaise_username`,`franchaise_password` FROM `franchaise_master` inner join 
			`franchaise_institution_mapping` on franchaise_master.`franchaise_id`=
			franchaise_institution_mapping.`franchaise_id` WHERE `franchaise_username`=%s 
			and `franchaise_password`=%s""",(username,password))
		franchaiseDtls = cursor.fetchone()
		if franchaiseDtls:
			return ({"attributes": {"status_desc": "Verify Franchaise Details",
								"status": "success"
								},
				"responseList": franchaiseDtls}), status.HTTP_200_OK
			
		else:
			return ({"attributes": {"status_desc": "Verify Franchaise Details",
								"status": "success"
								},
				"responseList": "Invalid Username or Password"}), status.HTTP_200_OK
		

#---------------------------------------------------------------------------#

#---------------------------------------------------------------------------#
@name_space.route("/FranchaiseInstitutionDtls/<int:institution_id>")
class FranchaiseInstitutionDtls(Resource):
	def get(self,institution_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT `INSTITUTION_ID`,`INSTITUTION_TYPE`,`INSTITUTION_NAME`,
			`INSTITUTION_PHONE_NUMBER`,`LAST_UPDATE_TIMESTAMP` FROM `institution_dtls` 
			WHERE `INSTITUTION_ID`=%s""",(institution_id))
		franchaiseInstDtls = cursor.fetchone()
		
		franchaiseInstDtls['LAST_UPDATE_TIMESTAMP'] = franchaiseInstDtls['LAST_UPDATE_TIMESTAMP'].isoformat()
		cursor.execute("""SELECT count(`INSTITUTION_USER_ID`)as total FROM 
			`institution_user_credential_master` WHERE `INSTITUTION_ID`=%s
			and `INSTITUTION_USER_ROLE`='TA'""",(institution_id))
		totalteacher = cursor.fetchone()
		if 	totalteacher:
			totalteacher = totalteacher['total']
		else:
			totalteacher = 0

		cursor.execute("""SELECT count(`INSTITUTION_USER_ID`)as total FROM 
			`institution_user_credential_master` WHERE `INSTITUTION_ID`=%s
			and `INSTITUTION_USER_ROLE`='S1'""",(institution_id))
		totalstudent = cursor.fetchone()
		if 	totalstudent:
			totalstudent = totalstudent['total']
		else:
			totalstudent = 0
		franchaiseInstDtls['totalteacher'] = totalteacher
		franchaiseInstDtls['totalstudent'] = totalstudent

		return ({"attributes": {"status_desc": "Franchaise Institution Details",
								"status": "success"
								},
				"responseList": franchaiseInstDtls}), status.HTTP_200_OK
			
#---------------------------------------------------------------------------#

#---------------------------------------------------------------------------#
@name_space.route("/FranchaiseDtls")
class FranchaiseDtls(Resource):
	def get(self):

		connection = mysql_connection()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT franchaise_master.`franchaise_id`,`institution_id`,
			`franchaise_role`,`franchisee_code`,
			`franchaise_username`,`franchaise_password` FROM `franchaise_master` inner join 
			`franchaise_institution_mapping` on franchaise_master.`franchaise_id`=
			franchaise_institution_mapping.`franchaise_id`""")
		franchaiseInstDtls = cursor.fetchall()
		
		return ({"attributes": {"status_desc": "Franchaise Details",
								"status": "success"
								},
				"responseList": franchaiseInstDtls}), status.HTTP_200_OK
			
#---------------------------------------------------------------------------#

#---------------------------------------------------------------------------#

@name_space.route("/addImageUrl")
class addImageUrl(Resource):
    @api.expect(addImageUrl)
    def put(self):
        details = request.get_json()
        connection = mysql_connection()
        cursor = connection.cursor()
        
        institution_user_id = details['institution_user_id']
        IMAGE_URL = details['IMAGE_URL']

        updateimage_query = ("""UPDATE `institution_user_credential` SET `IMAGE_URL`=%s WHERE
         `INSTITUTION_USER_ID`=%s""")
        image_data = (IMAGE_URL,institution_user_id)

        cursor.execute(updateimage_query,image_data)
        connection.commit()

        return ({"attributes": {"status_desc": "Added Image Url",
                                    "status": "success"
                                    },
				"responseList": details}), status.HTTP_200_OK
#---------------------------------------------------------------------------#

#---------------------------------------------------------------------------#
@name_space.route("/ApplicantNumberForDenovo")
class ApplicantNumberForDenovo(Resource):
	@api.expect(applicantno)
	def put(self):
		details = request.get_json()
		connection = mysql_connection()
		cursor = connection.cursor()
		current_year = date.today().year

		user_id = details['institution_user_id']
		institution_id = details['institution_id']

		cursor.execute("""SELECT `USER_UNIQUE_ID` FROM `institution_user_credential` 
			WHERE `INSTITUTION_USER_ID`=%s""",(user_id))
		userapp_no = cursor.fetchone()
		# print(userapp_no)
		
		if userapp_no['USER_UNIQUE_ID'] !='':
			# print("hii")
			applicantno = userapp_no['USER_UNIQUE_ID']
			
		else:
			cursor.execute("""SELECT `USER_UNIQUE_ID` FROM 
				`institution_user_credential` WHERE `INSTITUTION_USER_ID` 
				in(SELECT `INSTITUTION_USER_ID` FROM `institution_user_credential_master` 
				WHERE `INSTITUTION_ID` = 337 and INSTITUTION_USER_ROLE='S1') 
				order by `INSTITUTION_USER_ID` DESC limit 2""")
			uniqueid = cursor.fetchall()
			# print(uniqueid)
			if uniqueid:
				USER_UNIQUE_ID = uniqueid[1]['USER_UNIQUE_ID']
				studentidno = USER_UNIQUE_ID.split("-", 1)
				idno = studentidno[1]
				nextidno = int(idno)+1
				applicantno = str(current_year)+ "-"+str(nextidno)

			else:
				firstid = 1
				applicantno = str(current_year)+ "-"+str(firstid)
				# print(applicantno)

			updateappno_query = ("""UPDATE `institution_user_credential` SET `USER_UNIQUE_ID`=%s 
	        	WHERE `INSTITUTION_USER_ID`=%s""")
			appno_data = (applicantno,user_id)

			cursor.execute(updateappno_query,appno_data)

			update_query = ("""UPDATE `institution_user_credential` 
				SET `INSTITUTION_USER_NAME`=%s,`INSTITUTION_USER_PASSWORD`=%s
				WHERE `INSTITUTION_USER_ID`=%s""")
			data = (applicantno,applicantno,user_id)

			cursor.execute(update_query,data)
			connection.commit()

			updateappno = ("""UPDATE `institution_user_personal_details` SET `USER_UNIQUE_ID`=%s WHERE
	         `INSTITUTION_USER_ID`=%s and `institution_id`=%s""")
			app_data = (applicantno,user_id,institution_id)

			cursor.execute(updateappno,app_data)
			connection.commit()
		return ({"attributes": {"status_desc": "Applicant Number",
								"status": "success"
								},
				"responseList": applicantno}), status.HTTP_200_OK
		
#---------------------------------------------------------------------------#

#---------------------------------------------------------------------------#
@name_space.route("/StudentDocumentsByStudentIdDocumentLabel/<int:student_id>/<string:document_label>")
class StudentDocumentsByStudentIdDocumentLabel(Resource):
	def get(self,student_id,document_label):

		connection = mysql_connection()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT `student_document_id`,`institution_user_id`,`document_label`,
			`document_filepath`,`document_filetype`,`last_update_ts` FROM `student_document` 
			WHERE `institution_user_id`=%s and locate(%s,`document_label`)""",(student_id,document_label))
		documnetDtls = cursor.fetchall()

		for i in range(len(documnetDtls)):
			documnetDtls[i]['last_update_ts'] = documnetDtls[i]['last_update_ts'].isoformat()

		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Document Details",
								"status": "success"
								},
				"responseList": documnetDtls}), status.HTTP_200_OK
#---------------------------------------------------------------------------#

#---------------------------------------------------------------------------#
@name_space.route("/ListOfStudentByFrachaiseCode/<string:franchisee_code>")
class ListOfStudentByFrachaiseCode(Resource):
	def get(self,franchisee_code):

		connection = mysql_connection()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT institution_dtls.`Institution_ID`, institution_dtls.
	        	`INSTITUTION_NAME`,`INSTITUTION_USER_ROLE`,institution_user_credential.`INSTITUTION_USER_ID`,
	        	concat(`FIRST_NAME`,' ',`LAST_NAME`) 
	        	as name,`INSTITUTION_USER_NAME`, `INSTITUTION_USER_PASSWORD`,
	        	`PRIMARY_CONTACT_NUMBER`,institution_user_credential.`IMAGE_URL`, 
	        	institution_user_credential_master.`INSTITUTION_NAME` as school_name,`CLASS`,`Board`,
	        	`institution_user_credential`.`LAST_UPDATE_TIMESTAMP`
        	FROM `institution_user_credential` inner join 
        	`institution_user_credential_master` on institution_user_credential.
        	`INSTITUTION_USER_ID`=institution_user_credential_master.`INSTITUTION_USER_ID` 
            INNER JOIN `institution_dtls` on institution_user_credential_master.`INSTITUTION_ID`
	        	 =institution_dtls.`INSTITUTION_ID` INNER join `student_dtls` on 
	        	 institution_user_credential.`INSTITUTION_USER_ID`=student_dtls.
	        	 `INSTITUTION_USER_ID_STUDENT`
        	where  institution_user_credential_master.`INSTITUTION_ID`=337
        	 and institution_user_credential_master.`INSTITUTION_NAME`= %s""",(franchisee_code))
		studentDtls = cursor.fetchall()

		for i in range(len(studentDtls)):
			studentDtls[i]['LAST_UPDATE_TIMESTAMP'] = studentDtls[i]['LAST_UPDATE_TIMESTAMP'].isoformat()

		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Student Details",
								"status": "success"
								},
				"responseList": studentDtls}), status.HTTP_200_OK
#---------------------------------------------------------------------------#

#-----------------------------------------------------------------------------------#
@name_space.route("/studentDtlsByInsIdDate/<int:INSTITUTION_ID>/<string:Start_date>/<string:End_date>/<string:franchisee_code>")
class studentDtlsByInsIdDate(Resource):
    def get(self,INSTITUTION_ID,Start_date,End_date,franchisee_code):
        connection = mysql_connection()
        cursor = connection.cursor()

        cursor.execute("""SELECT institution_dtls.`Institution_ID`, institution_dtls.
	        	`INSTITUTION_NAME`,`INSTITUTION_USER_ROLE`,institution_user_credential.`INSTITUTION_USER_ID`,
	        	concat(`FIRST_NAME`,' ',`LAST_NAME`) 
	        	as name,`INSTITUTION_USER_NAME`, `INSTITUTION_USER_PASSWORD`,
	        	`PRIMARY_CONTACT_NUMBER`,`USER_UNIQUE_ID`,institution_user_credential.`IMAGE_URL`, 
	        	institution_user_credential_master.`INSTITUTION_NAME` as school_name,`CLASS`,`Board`,
	        	`institution_user_credential`.`LAST_UPDATE_TIMESTAMP`
        	FROM `institution_user_credential` inner join 
        	`institution_user_credential_master` on institution_user_credential.
        	`INSTITUTION_USER_ID`=institution_user_credential_master.`INSTITUTION_USER_ID` 
            INNER JOIN `institution_dtls` on institution_user_credential_master.`INSTITUTION_ID`
	        	 =institution_dtls.`INSTITUTION_ID` INNER join `student_dtls` on 
	        	 institution_user_credential.`INSTITUTION_USER_ID`=student_dtls.
	        	 `INSTITUTION_USER_ID_STUDENT`
        	where date(institution_user_credential.`LAST_UPDATE_TIMESTAMP`) 
        	between %s and %s and institution_user_credential_master.`INSTITUTION_ID`=%s
        	 and `INSTITUTION_USER_ROLE`= 'S1' and 
        	 institution_user_credential_master.`INSTITUTION_NAME`= %s""",(Start_date,End_date,INSTITUTION_ID,franchisee_code))


        studtlsbydate = cursor.fetchall()
        for i in range(len(studtlsbydate)):
        	studtlsbydate[i]['LAST_UPDATE_TIMESTAMP'] = studtlsbydate[i]['LAST_UPDATE_TIMESTAMP'].isoformat()
    
        return ({"attributes": {"status_desc": "user Details",
                                "status": "success"
                                },
                 "responseList": studtlsbydate
                }), status.HTTP_200_OK
#------------------------------------------------------------------------------------#

@name_space.route("/SubmitAdmissionFee")
class SubmitAdmissionFee(Resource):
	@api.expect(admissionfee)
	def post(self):
		conn = mysql_connection()
		cur = conn.cursor()
		details = request.get_json()
		
		institution_id = details['institution_id']
		user_id = details['user_id']
		payment_mood = details['payment_mood']
		actual_amount = details['actual_amount']
		payment_amount = details['payment_amount']
		is_pending = details['is_pending']
		
		admission_query = ("""INSERT INTO `student_admission_fee`(`institution_id`, 
			`user_id`, `payment_mood`, `actual_amount`, `payment_amount`, `is_pending`) 
			VALUES(%s,%s,%s,%s,%s,%s)""")
		insert_data = (institution_id,user_id,payment_mood,actual_amount,
			payment_amount,is_pending)
		admissiondata = cur.execute(admission_query,insert_data)
		# print(smsbackdata)

		conn.commit()
		cur.close()
		if admissiondata:
			return ({"attributes": {"status_desc": "Admission fee Submitted",
	                                "status": "success"
	                                },
                 "responseList": details
                }), status.HTTP_200_OK
		

#------------------------------------------------------------------------------------#

@name_space.route("/SubmitExamFee")
class SubmitExamFee(Resource):
	@api.expect(examfee)
	def post(self):
		conn = mysql_connection()
		cur = conn.cursor()
		details = request.get_json()
		
		institution_id = details['institution_id']
		user_id = details['user_id']
		payment_mood = details['payment_mood']
		actual_amount = details['actual_amount']
		payment_amount = details['payment_amount']
		is_pending = details['is_pending']
		
		admission_query = ("""INSERT INTO `student_exam_fee`(`institution_id`, 
			`user_id`, `payment_mood`, `actual_amount`, `payment_amount`, `is_pending`) 
			VALUES(%s,%s,%s,%s,%s,%s)""")
		insert_data = (institution_id,user_id,payment_mood,actual_amount,
			payment_amount,is_pending)
		admissiondata = cur.execute(admission_query,insert_data)
		# print(smsbackdata)

		conn.commit()
		cur.close()
		if admissiondata:
			return ({"attributes": {"status_desc": "Exam fee Submitted",
	                                "status": "success"
	                                },
                 "responseList": details
                }), status.HTTP_200_OK
		
#-------------------------------------------------------------------------#
@name_space.route("/updateAdmissionFeeByFeeID/<int:fee_id>")
class updateAdmissionFeeByFeeID(Resource):
    @api.expect(update_admissionfee)
    def put(self,fee_id):
        details = request.get_json()
        connection = mysql_connection()
        cursor = connection.cursor()
        
        Payment_mood = details.get('payment_mood')
        Actual_amount = details.get('actual_amount')
        Payment_amount = details.get('payment_amount')
        Is_pending = details.get('is_pending')

        cursor.execute("""SELECT `payment_mood`,`actual_amount`, `payment_amount`, `is_pending`
        	FROM `student_admission_fee` WHERE `admission_fee_id`=%s""",(fee_id))
        fee_dtls = cursor.fetchone()
        # print(fee_dtls)
        if fee_dtls:
            if not Payment_mood:
                Payment_mood = fee_dtls.get('payment_mood')
             
            if not Actual_amount:
                Actual_amount = fee_dtls.get('actual_amount')
                
            if not Payment_amount:
                Payment_amount = fee_dtls.get('payment_amount')
                
            if not Is_pending:
                Is_pending = fee_dtls.get('is_pending')

        update_student_fee = ("""UPDATE `student_admission_fee` SET `payment_mood`=%s,`actual_amount`=%s,
        	`payment_amount`=%s,`is_pending`=%s WHERE `admission_fee_id`= %s""")
        student_document_data = (Payment_mood,Actual_amount,Payment_amount,Is_pending,fee_id)

        updatedata = cursor.execute(update_student_fee,student_document_data)

        # cursor.commit()
        return ({"attributes": {"status_desc": "Student Admission Fee Update Details.",
                            "status": "success"
                            },
                "responseList":details}), status.HTTP_200_OK


#-------------------------------------------------------------------------#
@name_space.route("/updateExamFeeByFeeID/<int:fee_id>")
class updateExamFeeByFeeID(Resource):
    @api.expect(update_examfee)
    def put(self,fee_id):
        details = request.get_json()
        connection = mysql_connection()
        cursor = connection.cursor()
        
        Payment_mood = details.get('payment_mood')
        Actual_amount = details.get('actual_amount')
        Payment_amount = details.get('payment_amount')
        Is_pending = details.get('is_pending')

        cursor.execute("""SELECT `payment_mood`,`actual_amount`, `payment_amount`, `is_pending`
        	FROM `student_exam_fee` WHERE `exam_fee_id`=%s""",(fee_id))
        fee_dtls = cursor.fetchone()
        # print(fee_dtls)
        if fee_dtls:
            if not Payment_mood:
                Payment_mood = fee_dtls.get('payment_mood')
             
            if not Actual_amount:
                Actual_amount = fee_dtls.get('actual_amount')
                
            if not Payment_amount:
                Payment_amount = fee_dtls.get('payment_amount')
                
            if not Is_pending:
                Is_pending = fee_dtls.get('is_pending')

        update_student_fee = ("""UPDATE `student_exam_fee` SET `payment_mood`=%s,`actual_amount`=%s,
        	`payment_amount`=%s,`is_pending`=%s WHERE `exam_fee_id`= %s""")
        student_document_data = (Payment_mood,Actual_amount,Payment_amount,Is_pending,fee_id)

        updatedata = cursor.execute(update_student_fee,student_document_data)


        # cursor.commit()
        return ({"attributes": {"status_desc": "Student Exam Fee Update Details.",
                            "status": "success"
                            },
                "responseList":details}), status.HTTP_200_OK

#---------------------------------------------------------------------------#
@name_space.route("/StudentAdmissionfeeDtlsByInstitutionID/<int:institution_id>")
class StudentAdmissionfeeDtlsByInstitutionID(Resource):
	def get(self,institution_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		current_year = date.today().year

		cursor.execute("""SELECT institution_dtls.`Institution_ID`, institution_dtls.
    		`INSTITUTION_NAME`,`INSTITUTION_USER_ROLE`,
    		institution_user_credential.`INSTITUTION_USER_ID`,
    		concat(`FIRST_NAME`,' ',`LAST_NAME`) 
    		as name,`PRIMARY_CONTACT_NUMBER`,`USER_UNIQUE_ID`,
    		institution_user_credential_master.`INSTITUTION_NAME` as franchaise_code,
    		`admission_fee_id`,`actual_amount`, `payment_amount`, `is_pending`,
    		`institution_user_credential`.`LAST_UPDATE_TIMESTAMP` FROM 
    		`institution_user_credential` inner join `institution_user_credential_master`
    		 on institution_user_credential. `INSTITUTION_USER_ID`=
    		 institution_user_credential_master.`INSTITUTION_USER_ID` INNER JOIN 
    		 `institution_dtls` on institution_user_credential_master.`INSTITUTION_ID` =
    		institution_dtls.`INSTITUTION_ID` INNER JOIN `student_admission_fee` 
    		on institution_user_credential_master.`INSTITUTION_USER_ID` =
    		student_admission_fee.`user_id` where institution_dtls.
    		`INSTITUTION_ID`=%s and `INSTITUTION_USER_ROLE`='S1' order by 
    		institution_user_credential.`INSTITUTION_USER_ID` asc""",(institution_id))
		studtls = cursor.fetchall()
		# print(studtls)
		if studtls:
			for i in range(len(studtls)):
				studtls[i]['LAST_UPDATE_TIMESTAMP'] = studtls[i]['LAST_UPDATE_TIMESTAMP'].isoformat()
				studtls[i]['is_pending'] = studtls[i]['actual_amount'] - studtls[i]['payment_amount']
		
		return ({"attributes": {"status_desc": "Student Admission Fee Details",
								"status": "success"
								},
				"responseList": studtls}), status.HTTP_200_OK
#---------------------------------------------------------------------------#

#---------------------------------------------------------------------------#
@name_space.route("/StudentExamfeeDtlsByInstitutionID/<int:institution_id>")
class StudentExamfeeDtlsByInstitutionID(Resource):
	def get(self,institution_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		current_year = date.today().year

		cursor.execute("""SELECT institution_dtls.`Institution_ID`, institution_dtls.
    		`INSTITUTION_NAME`,`INSTITUTION_USER_ROLE`,
    		institution_user_credential.`INSTITUTION_USER_ID`,
    		concat(`FIRST_NAME`,' ',`LAST_NAME`) 
    		as name,`PRIMARY_CONTACT_NUMBER`,`USER_UNIQUE_ID`,
    		institution_user_credential_master.`INSTITUTION_NAME` as franchaise_code,
    		`exam_fee_id`,`actual_amount`, `payment_amount`, `is_pending`,
    		`institution_user_credential`.`LAST_UPDATE_TIMESTAMP` FROM 
    		`institution_user_credential` inner join `institution_user_credential_master`
    		 on institution_user_credential. `INSTITUTION_USER_ID`=
    		 institution_user_credential_master.`INSTITUTION_USER_ID` INNER JOIN 
    		 `institution_dtls` on institution_user_credential_master.`INSTITUTION_ID` =
    		institution_dtls.`INSTITUTION_ID` INNER JOIN `student_exam_fee` 
    		on institution_user_credential_master.`INSTITUTION_USER_ID` =
    		student_exam_fee.`user_id` where institution_dtls.
    		`INSTITUTION_ID`=%s and `INSTITUTION_USER_ROLE`='S1' order by 
    		institution_user_credential.`INSTITUTION_USER_ID` asc""",(institution_id))
		studtls = cursor.fetchall()
		# print(studtls)
		if studtls:
			for i in range(len(studtls)):
				studtls[i]['LAST_UPDATE_TIMESTAMP'] = studtls[i]['LAST_UPDATE_TIMESTAMP'].isoformat()
				studtls[i]['is_pending'] = studtls[i]['actual_amount'] - studtls[i]['payment_amount']
		
		return ({"attributes": {"status_desc": "Student Exam Fee Details",
								"status": "success"
								},
				"responseList": studtls}), status.HTTP_200_OK

#---------------------------------------------------------------------------#
@name_space.route("/StudentAdmissionfeeDtlsByInstitutionIDFrachaiseCode/<string:franchisee_code>/<int:institution_id>")
class StudentAdmissionfeeDtlsByInstitutionIDFrachaiseCode(Resource):
	def get(self,institution_id,franchisee_code):
		connection = mysql_connection()
		cursor = connection.cursor()
		current_year = date.today().year

		cursor.execute("""SELECT institution_dtls.`Institution_ID`, institution_dtls.
    		`INSTITUTION_NAME`,`INSTITUTION_USER_ROLE`,
    		institution_user_credential.`INSTITUTION_USER_ID`,
    		concat(`FIRST_NAME`,' ',`LAST_NAME`) 
    		as name,`PRIMARY_CONTACT_NUMBER`,`USER_UNIQUE_ID`,
    		institution_user_credential_master.`INSTITUTION_NAME` as franchaise_code,
    		`admission_fee_id`,`actual_amount`, `payment_amount`, `is_pending`,
    		`institution_user_credential`.`LAST_UPDATE_TIMESTAMP` FROM 
    		`institution_user_credential` inner join `institution_user_credential_master`
    		 on institution_user_credential. `INSTITUTION_USER_ID`=
    		 institution_user_credential_master.`INSTITUTION_USER_ID` INNER JOIN 
    		 `institution_dtls` on institution_user_credential_master.`INSTITUTION_ID` =
    		institution_dtls.`INSTITUTION_ID` INNER JOIN `student_admission_fee` 
    		on institution_user_credential_master.`INSTITUTION_USER_ID` =
    		student_admission_fee.`user_id` where institution_dtls.
    		`INSTITUTION_ID`=%s and `INSTITUTION_USER_ROLE`='S1' 
    		and institution_user_credential_master.`INSTITUTION_NAME`=%s order by 
    		institution_user_credential.`INSTITUTION_USER_ID` asc""",(institution_id,franchisee_code))
		studtls = cursor.fetchall()
		# print(studtls)
		if studtls:
			for i in range(len(studtls)):
				studtls[i]['LAST_UPDATE_TIMESTAMP'] = studtls[i]['LAST_UPDATE_TIMESTAMP'].isoformat()
				studtls[i]['is_pending'] = studtls[i]['actual_amount'] - studtls[i]['payment_amount']
		
		return ({"attributes": {"status_desc": "Student Admission Fee Details",
								"status": "success"
								},
				"responseList": studtls}), status.HTTP_200_OK
#---------------------------------------------------------------------------#

#---------------------------------------------------------------------------#
@name_space.route("/StudentExamfeeDtlsByInstitutionIDFrachaiseCode/<string:franchisee_code>/<int:institution_id>")
class StudentExamfeeDtlsByInstitutionIDFrachaiseCode(Resource):
	def get(self,institution_id,franchisee_code):
		connection = mysql_connection()
		cursor = connection.cursor()
		current_year = date.today().year

		cursor.execute("""SELECT institution_dtls.`Institution_ID`, institution_dtls.
    		`INSTITUTION_NAME`,`INSTITUTION_USER_ROLE`,
    		institution_user_credential.`INSTITUTION_USER_ID`,
    		concat(`FIRST_NAME`,' ',`LAST_NAME`) 
    		as name,`PRIMARY_CONTACT_NUMBER`,`USER_UNIQUE_ID`,
    		institution_user_credential_master.`INSTITUTION_NAME` as franchaise_code,
    		`exam_fee_id`,`actual_amount`, `payment_amount`, `is_pending`,
    		`institution_user_credential`.`LAST_UPDATE_TIMESTAMP` FROM 
    		`institution_user_credential` inner join `institution_user_credential_master`
    		 on institution_user_credential. `INSTITUTION_USER_ID`=
    		 institution_user_credential_master.`INSTITUTION_USER_ID` INNER JOIN 
    		 `institution_dtls` on institution_user_credential_master.`INSTITUTION_ID` =
    		institution_dtls.`INSTITUTION_ID` INNER JOIN `student_exam_fee` 
    		on institution_user_credential_master.`INSTITUTION_USER_ID` =
    		student_exam_fee.`user_id` where institution_dtls.
    		`INSTITUTION_ID`=%s and `INSTITUTION_USER_ROLE`='S1' 
    		and institution_user_credential_master.`INSTITUTION_NAME`=%s  order by 
    		institution_user_credential.`INSTITUTION_USER_ID` asc""",(institution_id,franchisee_code))
		studtls = cursor.fetchall()
		# print(studtls)
		if studtls:
			for i in range(len(studtls)):
				studtls[i]['LAST_UPDATE_TIMESTAMP'] = studtls[i]['LAST_UPDATE_TIMESTAMP'].isoformat()
				studtls[i]['is_pending'] = studtls[i]['actual_amount'] - studtls[i]['payment_amount']
		
		return ({"attributes": {"status_desc": "Student Exam Fee Details",
								"status": "success"
								},
				"responseList": studtls}), status.HTTP_200_OK
#---------------------------------------------------------------------------#

#--------------------------------------------------------------------------#
@name_space.route("/UploadUserResult")
class UploadUserResult(Resource):
	@api.expect(userresult)
	def post(self):
		details = request.get_json()		

		connection = mysql_connection()
		cursor = connection.cursor()

		institution_id = details.get('institution_id')
		studentList = details.get('institution_user_id',[])
		content_filepath = details.get('content_filepath')
		content_filetype =details.get('content_filetype')
		remarks = details.get('remarks')

		insert_query = ("""INSERT INTO `user_result`(`institution_id`, 
			`institution_user_id`, `content_filepath`, `content_filetype`, 
			`remarks`) VALUES (%s,%s,%s,%s,%s)""")
		for sid in studentList:
			data= (institution_id,sid,content_filepath,content_filetype,remarks)
			cursor.execute(insert_query,data)

			# if assign_course_fees == "y":
			url = 'http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com/flaskapp/app_notify/AppCommunicationAPI/appMessage'
			headers = {'Content-type':'application/json', 'Accept':'application/json'}
        
			data ={
                        "appParams": {},
                        "userId": sid,
                        "sourceapp": "SRESLT00S",
                        "toMail": "",
                        "role": "S1",
                        "toNumber": 0,
                        "mailParams": {"link":content_filepath}
                    }
			response = requests.post(url, data=json.dumps(data), headers=headers).json()
			# print(response)


		cursor.close()
		cursor.close()		

		return ({"atributes": {
	    			"status_desc": "RESULT Uploaded",
	    			"status": "success"
	    			},
	    			"responseList":"Data Inserted Successfully"}), status.HTTP_200_OK

#------------------------------------------------------------------------#	

#--------------------------------------------------------------------------#
@name_space.route("/UploadResultPath")
class UploadResultPath(Resource):
	@api.expect(uploadresult)
	def post(self):
		details = request.get_json()		

		connection = mysql_connection()
		cursor = connection.cursor()

		institution_id = details.get('institution_id')
		institution_user_id = details.get('institution_user_id')
		title = details.get('title')
		content_filepath = details.get('content_filepath')
		

		insert_query = ("""INSERT INTO `upload_result`(`institution_id`, 
			`institution_user_id`,`title`,`content_filepath`) VALUES (%s,%s,%s,%s)""")
		data= (institution_id,institution_user_id,title,content_filepath)
		cursor.execute(insert_query,data)

			
		cursor.close()
		cursor.close()		

		return ({"atributes": {
	    			"status_desc": "RESULT Uploaded",
	    			"status": "success"
	    			},
	    			"responseList":details}), status.HTTP_200_OK

#------------------------------------------------------------------------#

#---------------------------------------------------------------------------#
@name_space.route("/getUploadResultPath/<int:institution_id>")
class UploadResultPath(Resource):
	def get(self,institution_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		current_year = date.today().year

		cursor.execute("""SELECT `upload_id`, `institution_id`, 
		 `institution_user_id`, `title`, `content_filepath`,`last_update_ts` 
		 FROM `upload_result` WHERE `institution_id`=%s""",(institution_id))
		pathdtls = cursor.fetchall()
		# print(pathdtls)
		if pathdtls:
			for i in range(len(pathdtls)):
				pathdtls[i]['last_update_ts'] = pathdtls[i]['last_update_ts'].isoformat()
				
		return ({"attributes": {"status_desc": "Result Path Details",
								"status": "success"
								},
				"responseList": pathdtls}), status.HTTP_200_OK
#---------------------------------------------------------------------------#

#---------------------------------------------------------------------------#
@name_space.route("/getUserResult/<int:user_id>")
class getUserResult(Resource):
	def get(self,user_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		current_year = date.today().year

		cursor.execute("""SELECT `result_id`,`institution_id`,
			`institution_user_id`,`content_filepath`,`content_filetype`,
			`remarks`,`last_update_ts` FROM `user_result` WHERE 
			`institution_user_id`=%s""",(user_id))
		pathdtls = cursor.fetchall()
		
		if pathdtls:
			for i in range(len(pathdtls)):
				pathdtls[i]['last_update_ts'] = pathdtls[i]['last_update_ts'].isoformat()
				
		return ({"attributes": {"status_desc": "Result Path Details",
								"status": "success"
								},
				"responseList": pathdtls}), status.HTTP_200_OK
#---------------------------------------------------------------------------#
#-------------------------------------------------------------------------#
@name_space.route("/updateUploadResultPathByUploadID/<int:upload_id>")
class updateUploadResultPathByUploadID(Resource):
    @api.expect(update_path)
    def put(self,upload_id):
        details = request.get_json()
        connection = mysql_connection()
        cursor = connection.cursor()
        
        Title = details.get('title')
        Content_filepath = details.get('content_filepath')

        cursor.execute("""SELECT `upload_id`, `institution_id`, 
		 `institution_user_id`, `title`, `content_filepath`,`last_update_ts` 
		 FROM `upload_result` WHERE `upload_id`=%s""",(upload_id))
        pathdtls = cursor.fetchone()
        # print(pathdtls)
        if pathdtls:
            
            if not Title:
                Title = pathdtls.get('title')
                
            if not Content_filepath:
                Content_filepath = pathdtls.get('content_filepath')
                
        update_path = ("""UPDATE `upload_result` SET `title`=%s,
        	`content_filepath`=%s WHERE `upload_id`= %s""")
        path_data = (Title,Content_filepath,upload_id)

        updatedata = cursor.execute(update_path,path_data)

        # cursor.commit()
        return ({"attributes": {"status_desc": "Result Path Update Details.",
                            "status": "success"
                            },
                "responseList":details}), status.HTTP_200_OK

#---------------------------------------------------------------------------#

#------------------------------------------------------------------------------------------#

@name_space.route("/DeleteUploadResultPath/<int:upload_id>")
class DeleteUploadResultPath(Resource):
	def delete(self,upload_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		pathdelete_query = ("""DELETE FROM `upload_result` WHERE 
			`upload_id`=%s""")
		delData = (upload_id)
		
		cursor.execute(pathdelete_query,delData)
		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Delete Result Path Details",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK
#------------------------------------------------------------------------------------------#

@name_space.route("/userUsageDtlsByuserid/<int:Userid>")
class userUsageDtlsByuserid(Resource):
    def get(self,Userid):
        connection = mysql_connection()
        cursor = connection.cursor()

        conn = user_library()
        cur = conn.cursor()
        
        cursor.execute("""SELECT institution_dtls.`Institution_ID`, institution_dtls.
        	`INSTITUTION_NAME`,`INSTITUTION_USER_ROLE`,concat(`FIRST_NAME`,' ',`LAST_NAME`) 
        	as name,`INSTITUTION_USER_NAME`, `INSTITUTION_USER_PASSWORD`,
        	`PRIMARY_CONTACT_NUMBER`,`USER_UNIQUE_ID`,institution_user_credential.`IMAGE_URL`, 
        	institution_user_credential_master.`INSTITUTION_NAME` as school_name,`CLASS`,`Board`,
        	`institution_user_credential`.`LAST_UPDATE_TIMESTAMP` FROM 
        	`institution_user_credential` inner join `institution_user_credential_master` 
        	on institution_user_credential.`INSTITUTION_USER_ID`=
        	institution_user_credential_master.`INSTITUTION_USER_ID` 
        	INNER JOIN `institution_dtls` on institution_user_credential_master.`INSTITUTION_ID`
        	 =institution_dtls.`INSTITUTION_ID` INNER join `student_dtls` on 
        	 institution_user_credential.`INSTITUTION_USER_ID`=student_dtls.
        	 `INSTITUTION_USER_ID_STUDENT` where institution_user_credential.
        	 `INSTITUTION_USER_ID`=%s""", (Userid))


        regdtlsbyUserid = cursor.fetchone()
        regdtlsbyUserid['LAST_UPDATE_TIMESTAMP'] = regdtlsbyUserid['LAST_UPDATE_TIMESTAMP'].isoformat()
        regdtlsbyUserid['teacher_id'] = 36524

        cursor.execute("""SELECT `student_document_id`,`document_filepath`, 
			`document_filename`,`document_filetype` FROM `student_document` 
			WHERE `document_label`='AdmitCard' AND `institution_user_id`=%s""",
			(Userid))
        AdmitCarddtls =cursor.fetchone()
        if AdmitCarddtls == None:
        	regdtlsbyUserid['AdmitCard'] = 'Not issued'
        else:
        	regdtlsbyUserid['AdmitCard'] = 'Issued'

        cursor.execute("""SELECT `student_document_id`,`document_filepath`,
    		`document_filename`,`document_filetype` FROM `student_document` 
    		WHERE `document_label`='IdentityCard' AND `institution_user_id`=%s""",(Userid))
        IdentityCarddtls =cursor.fetchone()
        if IdentityCarddtls == None:
        	regdtlsbyUserid['IdentityCard'] = 'Not issued'
        else:
        	regdtlsbyUserid['IdentityCard'] = 'Issued'

        cursor.execute("""SELECT `student_document_id`,`document_filepath`,
    		`document_filename`,`document_filetype` FROM `student_document` 
    		WHERE `document_label`='StudyMaterial' AND `institution_user_id`=%s""",(Userid))
        StudyMaterialdtls =cursor.fetchone()
        if StudyMaterialdtls == None:
        	regdtlsbyUserid['StudyMaterial'] = 'Not issued'
        else:
        	regdtlsbyUserid['StudyMaterial'] = 'Issued'

        cur.execute("""SELECT `coursefee_id` FROM `student_coursefee_mapping` 
    		WHERE `student_id`=%s""",(Userid))
        coursefeedtls =cur.fetchone()
        if coursefeedtls == None:
        	regdtlsbyUserid['TMAProject'] = 'Not purchased'
        else:
        	regdtlsbyUserid['TMAProject'] = 'Purchased'

        cur.execute("""SELECT `onlinetestfee_id` FROM `student_onlinetestfee_mapping` 
		    WHERE `student_id`=%s""",(Userid))
        onlinetestfeedtls =cur.fetchone()
        if onlinetestfeedtls == None:
        	regdtlsbyUserid['OnlineTest'] = 'Not purchased'
        else:
        	regdtlsbyUserid['OnlineTest'] = 'Purchased'

        cursor.execute("""SELECT `exam_fee_id`,`payment_amount`,`is_pending` 
        	FROM `student_exam_fee` WHERE `user_id`=%s""",(Userid))
        examfeedtls =cursor.fetchall()
        if examfeedtls == None:
        	regdtlsbyUserid['exam_fee_id'] = examfeedtls[i]['exam_fee_id']
        	regdtlsbyUserid['exam_fee'] = 0
        else:
        	for i in range(len(examfeedtls)):
	        	regdtlsbyUserid['exam_fee'] = examfeedtls
	        	# regdtlsbyUserid['exam_fee'] = examfeedtls[i]['payment_amount']

        cursor.execute("""SELECT `admission_fee_id`,`payment_amount`,`is_pending`
        	as 'pending_admission_fee',
        	`actual_amount`,`payment_amount` FROM `student_admission_fee` 
			WHERE `user_id`=%s""",(Userid))
        admissionfeedtls =cursor.fetchone()
        if admissionfeedtls == None:
        	regdtlsbyUserid['admission_fee_id'] = admissionfeedtls['admission_fee_id']
        	regdtlsbyUserid['admission_fee'] = 0
        	regdtlsbyUserid['pending_admission_fee'] =admissionfeedtls['actual_amount'] - admissionfeedtls['payment_amount']
		
        else:
        	regdtlsbyUserid['admission_fee_id'] = admissionfeedtls['admission_fee_id']
        	regdtlsbyUserid['admission_fee'] = admissionfeedtls['payment_amount']
        	regdtlsbyUserid['pending_admission_fee'] =admissionfeedtls['actual_amount'] - admissionfeedtls['payment_amount']
		
        connection.commit()
        cursor.close()
        conn.commit()
        cur.close()

        return ({"attributes": {"status_desc": "user Details",
                                "status": "success"
                                },
                 "responseList": regdtlsbyUserid
                }), status.HTTP_200_OK



@name_space.route("/SubmitPayUMoneyPaymentDetails")
class SubmitPayUMoneyPaymentDetails(Resource):
	@api.expect(payumoney_payment)
	def post(self):
		conn = mysql_connection()
		cur = conn.cursor()

		con = user_library()
		cursor = con.cursor()

		details = request.get_json()
		
		student_id = details['student_id']
		teacher_id = details['teacher_id']
		Institution_ID = details['Institution_ID']
		product_desc_id = details['product_desc_id']
		payment_status = details['payment_status']
		payment_Id = details['payment_Id']
		mode = details['mode']
		amount = details['amount']
		payuMoneyId = details['payuMoneyId']
		product_desc = details['product_desc']
		postUrl = details['postUrl']
		addedon = details['addedon']
		
		
		payment_query = ("""INSERT INTO `payumoney_payment_details`(`student_id`, 
			`teacher_id`, `Institution_ID`, `product_desc_id`, `payment_status`, `payment_Id`, `mode`,
			`amount`, `payuMoneyId`, `productinfo`, `product_desc`, `postUrl`,
			`addedon`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
		payment_data = (student_id,teacher_id,Institution_ID,product_desc_id,payment_status,payment_Id,
		  mode,amount,payuMoneyId,product_desc,product_desc,postUrl,addedon)
		paymentdata = cur.execute(payment_query,payment_data)
		# print(paymentdata)
		if product_desc != "test":
			insert_query = ("""INSERT INTO `student_course_master`(`student_id`,`course_id`,`Institution_ID`,
				`teacher_id`,`coursefee_id`) VALUES(%s,%s,%s,%s,%s)""")
			insert_data = (student_id,product_desc_id,teacher_id,Institution_ID,0)
			insertdata = cursor.execute(insert_query,insert_data)
			
			curdate = datetime.now().strftime('%Y-%m-%d')

			courseFeeInsertQuery = ("""INSERT INTO `student_coursefee_mapping`(`purchase_type`,`student_id`, 
				`course_id`,`payment_mode`, `payment_type`, `no_of_installment`, `total_amount`, 
				`actual_amount`,`purchased_on`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

			courseFeeData = ('course',student_id,product_desc_id,'payumoney','full','0',amount,amount,curdate)
			cursor.execute(courseFeeInsertQuery,courseFeeData)

			courseFeeId = cursor.lastrowid

			studentPaymentDetailsInsert = ("""INSERT INTO `student_coursefee_payment_details`(`student_id`,
			   `payment_amount`,`payment_duedate`,`is_pending`,`paid_on`,`coursefee_id`,`transaction_id`) 
			   VALUES(%s,%s,%s,%s,%s,%s,%s)""")
			studentPaymentData = (student_id,amount,'','n',curdate,courseFeeId,payuMoneyId)
			cursor.execute(studentPaymentDetailsInsert,studentPaymentData)

			course_fees_update_query = ("""UPDATE `student_course_master` SET `coursefee_id` = %s
				WHERE `course_id` = %s and `student_id` = %s and `teacher_id` = %s and `Institution_ID` = %s""")
			update_data = (courseFeeId,product_desc_id,student_id,teacher_id,Institution_ID)
			cursor.execute(course_fees_update_query,update_data)

		else:
			insert_query = ("""INSERT INTO `student_onlinetest_master`(`student_id`,`Online_Test_ID`,`Institution_ID`,
				`teacher_id`,`onlinetestfee_id`) VALUES(%s,%s,%s,%s,%s)""")
			insert_data = (student_id,product_desc_id,teacher_id,Institution_ID,0)
			insertdata = cursor.execute(insert_query,insert_data)
			
			curdate = datetime.now().strftime('%Y-%m-%d')

			onlinetestFeeInsertQuery = ("""INSERT INTO `student_onlinetestfee_mapping`(`student_id`, 
				`Online_Test_ID`,`payment_mode`, `payment_type`, `no_of_installment`, `total_amount`, 
				`actual_amount`,`purchased_on`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""")

			onlinetestFeeData = (student_id,product_desc_id,'payumoney','full','0',amount,amount,curdate)
			cursor.execute(onlinetestFeeInsertQuery,onlinetestFeeData)

			testFeeId = cursor.lastrowid

			studentPaymentDetailsInsert = ("""INSERT INTO `student_onlinetestfee_payment_details`(`student_id`,
			   `payment_amount`,`payment_duedate`,`is_pending`,`paid_on`,`onlinetestfee_id`,`transaction_id`) 
			   VALUES(%s,%s,%s,%s,%s,%s,%s)""")
			studentPaymentData = (student_id,amount,'','n',curdate,testFeeId,payuMoneyId)
			cursor.execute(studentPaymentDetailsInsert,studentPaymentData)

			onlinetest_fees_update_query = ("""UPDATE `student_onlinetest_master` SET `onlinetestfee_id` = %s
				WHERE `Online_Test_ID` = %s and `student_id` = %s and `teacher_id` = %s and `Institution_ID` = %s""")
			update_data = (testFeeId,product_desc_id,student_id,teacher_id,Institution_ID)
			cursor.execute(onlinetest_fees_update_query,update_data)

		conn.commit()
		cur.close()
		con.commit()
		cursor.close()
		if paymentdata:
			return ({"attributes": {"status_desc": "Payment Details",
	                                "status": "success"
	                                },
                 "responseList": details
                }), status.HTTP_200_OK
		


@name_space.route("/SubmitFees")
class SubmitFees(Resource):
	@api.expect(payumoney_fee)
	def post(self):
		conn = mysql_connection()
		cur = conn.cursor()

		details = request.get_json()
		
		student_id = details['student_id']
		teacher_id = details['teacher_id']
		Institution_ID = details['Institution_ID']
		product_desc_id = details['product_desc_id']
		payment_status = details['payment_status']
		payment_Id = details['payment_Id']
		mode = details['mode']
		amount = details['amount']
		payuMoneyId = details['payuMoneyId']
		product_desc = details['product_desc']
		actual_amount = details['actual_amount']
		postUrl = details['postUrl']
		addedon = details['addedon']
		
		
		payment_query = ("""INSERT INTO `payumoney_payment_details`(`student_id`, 
			`teacher_id`, `Institution_ID`, `product_desc_id`, `payment_status`, `payment_Id`, `mode`,
			`amount`, `payuMoneyId`, `productinfo`, `product_desc`, `postUrl`,
			`addedon`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
		payment_data = (student_id,teacher_id,Institution_ID,product_desc_id,payment_status,payment_Id,
		  mode,amount,payuMoneyId,product_desc,product_desc,postUrl,addedon)
		paymentdata = cur.execute(payment_query,payment_data)

		if product_desc == "admission":
			admission_fees_url = BASE_URL + 'myelsa_academy/MyelsaAcademy/updateAdmissionFeeByFeeID/{}'.format(product_desc_id)
			if amount != actual_amount:
				is_pending ="Yes"
			else:
				is_pending ="No"
			# print(is_pending)
			post_data = {
				  "payment_mood": "payumoney",
				  "actual_amount": actual_amount,
				  "payment_amount": amount,
				  "is_pending": is_pending
				}

			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			post_response = requests.put(admission_fees_url, data=json.dumps(post_data), headers=headers)
			# print(post_response)

		else:
			exam_fees_url = BASE_URL + 'myelsa_academy/MyelsaAcademy/updateExamFeeByFeeID//{}'.format(product_desc_id)
			is_pending ="No"
			post_data = {
				  "payment_mood": "payumoney",
				  "actual_amount": actual_amount,
				  "payment_amount": amount,
				  "is_pending": is_pending
				}

			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			post_response = requests.put(exam_fees_url, data=json.dumps(post_data), headers=headers)

		conn.commit()
		cur.close()
		
		if paymentdata:
			return ({"attributes": {"status_desc": "Payment Details",
	                                "status": "success"
	                                },
                 "responseList": details
                }), status.HTTP_200_OK
		


@name_space.route("/AddStudyMaterial")
class AddStudyMaterial(Resource):
    @api.expect(studentdocument)
    def post(self):
        details = request.get_json()
        connection = mysql_connection()
        cursor = connection.cursor()
        # currentDate = date.today().strftime("%d%b%y")
        
        group_id = details['group_id']
        document_label = details['document_label']
        document_filepath = details['document_filepath']
        document_filetype = details['document_filetype']
        last_upadte_id = details['last_upadte_id']

        cursor.execute("""SELECT gsm.`Group_ID`,gsm.`Student_Id` FROM 
    		`group_student_mapping` gsm WHERE gsm.`Group_ID` = %s""",
    		(group_id))
        student_mapping_data = cursor.fetchall()
        for data in student_mapping_data:
        	student_id = data['Student_Id']
        	group_ID = data['Group_ID']
	        
	        student_document_query = ("""INSERT INTO `student_document`(`institution_user_id`,
	         `document_label`, `document_filepath`, `document_filetype`,
	          `last_upadte_id`) VALUES (%s,%s,%s,%s,%s)""")
	        student_document_data = (student_id,document_label,document_filepath,
	            document_filetype,last_upadte_id)

	        documentdata = cursor.execute(student_document_query,student_document_data)

		        
        connection.commit()
        cursor.close()
        if documentdata:
            return ({"attributes": {"status_desc": "Added Student Document",
                                    "status": "success"
                                    }
                     }), status.HTTP_200_OK



#----------------------Assign-Online-Test---------------------#
@name_space.route("/AssignAllStudentOnlineTest/")
class AssignAllStudentOnlineTest(Resource):
	@api.expect(online_test_student_model)
	def post(self):	

		details = request.get_json()
		connection = mysql_connection()
		cursor = connection.cursor()

		conn = user_library()
		cur = conn.cursor()

		online_test_id = details['online_test_id']
		Institution_ID = details['Institution_ID']
		start_time = details['start_time']
		end_time = details['end_time']
		nstatus = "n"
		No_Of_attempts = 0
		teacher_id = details['teacher_id']

		cursor.execute("""SELECT `INSTITUTION_USER_ID` FROM 
			`institution_user_credential_master` WHERE `INSTITUTION_USER_ROLE`=
			'S1' and `INSTITUTION_ID`=%s""",(Institution_ID))
		studentList = cursor.fetchall()
		
		for i in range(len(studentList)):
			sid = studentList[i]['INSTITUTION_USER_ID']
			insert_query = ("""INSERT INTO `online_test_student_mapping`(`online_test_id`,`Institution_ID`,`Institution_user_ID`,`teacher_id`,`status`,`No_Of_attempts`,`start_time`,`end_time`) VALUES(%s,%s,%s,%s,
			   %s,%s,%s,%s)""")
		
			data= (online_test_id,Institution_ID,sid,teacher_id,nstatus,No_Of_attempts,start_time,end_time)
			
			cur.execute(insert_query,data)
		
		cursor.close()
		cur.close()		

		return ({"atributes": {
	    			"status_desc": "Assign Online Test",
	    			"status": "success"
	    			},
	    			"responseList":"Saved Data Successfully"}), status.HTTP_200_OK


#----------------------Assign-Online-Test---------------------#
