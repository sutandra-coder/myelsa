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


'''def mysql_connection():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='creamson_logindb',
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

def mysql_b2b_connection():
    connection = pymysql.connect(host='creamsonservices.com',
                                user='creamson_langlab',
                                password='Langlab@123',
                                db='creamson_lab_lang1',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
    return connection


fee_management = Blueprint('fee_management_api', __name__)
api = Api(fee_management,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('feeManagement',description='Fee Management')
name_spaceV2 = api.namespace('feeManagementV2',description='Fee ManagementV2')

personalDtls = api.model('personalDtlsDto', {
	"fathers_occupation":fields.String(),
	"father_aadhaarNo":fields.String(),
	"mothers_name":fields.String(),
	"mothers_oocupation":fields.String(),
	"mothers_aadharNo":fields.String(),
	"social_status":fields.String(),
	"social_category":fields.String(),
	"physical_status":fields.String(),
	"religion":fields.String(),
	"school_last_studied":fields.String(),
	"optional_subject":fields.String(),
	})


addUser = api.model('addUserDto', {
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
    "personal_details":fields.Nested(personalDtls)
    })

transactionDtls = api.model('transactionDtls', {
	"activity_id":fields.Integer(),
	"amount":fields.String(),
	"month_id":fields.Integer(),

	})

fee_transaction = api.model('fee_transaction', {
	"institution_id":fields.Integer(),
	"user_id":fields.Integer(),
	"transactionDtls":fields.List(fields.Nested(transactionDtls)),
	"total_amount":fields.String(),
	})

payment_request = api.model('payment_request', {
	"institution_id":fields.Integer(),
	"user_id":fields.Integer(),
	"activity_id":fields.Integer(),
	"month_id":fields.Integer(),
	"no_of_month":fields.Integer(),
	"amount":fields.String()
	})

payment_requestDtls=api.model('payment_requestDtls', {
	"payment_request":fields.List(fields.Nested(payment_request))
	})

apstransactionDtls = api.model('apstransactionDtls', {
	"activity_id":fields.Integer(),
	"amount":fields.String(),
	"month_id":fields.Integer(),
	"no_of_month":fields.String()
	})

apsfee_transaction = api.model('apsfee_transaction', {
	"institution_id":fields.Integer(),
	"user_id":fields.Integer(),
	"total_amount":fields.String(),
	"apstransactionDtls":fields.List(fields.Nested(apstransactionDtls)),
	
	})

feetransaction = api.model('feetransaction', {
	"institution_id":fields.Integer(),
	"institution_user_id":fields.Integer(),
	"class":fields.String(),
	"stream":fields.String(),
	"fee_type":fields.String(),
	"month_id":fields.Integer(),
	"amount":fields.Float(),
	"totalamount":fields.Float()
	})

feeTransactionDtls = api.model('feeTransactionDtls', {
	"feetransaction":fields.List(fields.Nested(feetransaction))
	})

student_hostel = api.model('student_hostel', {
	"student_id":fields.Integer(),
	"institution_id":fields.Integer(),
	"hostel_room_no":fields.String()
	})

userresult = api.model('userresult', {
	"institution_id":fields.Integer(),
	"institution_user_id":fields.Integer(),
	"content_filepath":fields.String(),
	"content_filetype":fields.String(),
	"remarks":fields.String()
	})

update_result = api.model('update_result', {
	"content_filepath":fields.String(),
	"content_filetype":fields.String(),
	"remarks":fields.String()
	})

#---------------------------------------------------------------#
create_payment_link_model = api.model('create_payment_link_model', {
	"amount":fields.Integer(),
	"purpose":fields.String(),
	"buyer_name":fields.String(),
	"email":fields.String(),
	"phone":fields.String(),
	"feetransaction_id":fields.Integer(),
	"user_id":fields.Integer(),
	"institution_id":fields.Integer(),
	"transaction_id":fields.Integer()
	})

ask_for_fees_model = api.model('ask_for_fees_model', {
	"amount":fields.Integer(),
	"purpose":fields.String(),
	"teacher_id":fields.Integer(),
	"institution_id":fields.Integer(),
	"feetransaction_id":fields.Integer(),
	"student_id":fields.Integer()
	})


MOJO_TEST_URL = 'https://test.instamojo.com/'

MOJO_BASE_URL = 'https://api.instamojo.com/'

BASE_URL = "http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/"

# BASE_URL = "http://127.0.0.1:5000/"
#----------------------------------------------------------------------#
@name_space.route("/getInstitutionActivity/<int:institution_id>")
class getInstitutionActivity(Resource):
	def get(self,institution_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		cursor.execute("""SELECT DISTINCT ai.`Activity_Id`, `Activity_Description` 
			FROM `activity_institution` ai INNER JOIN `activity_institution_mapping` aim 
			ON ai.`Activity_Id` = aim.`Activity_Id` AND `Institution_Id` = %s""",(institution_id))


		activityList = cursor.fetchall()

		return ({"attributes": {"status_desc": "Institution Activity Details",
                                "status": "success"
                                },
                 "responseList": activityList}), status.HTTP_200_OK

@name_space.route("/getInstitutionClass/<int:institution_id>")
class getInstitutionClass(Resource):
	def get(self,institution_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		cursor.execute("""SELECT distinct `class` FROM `activity_institution_mapping` 
			WHERE `Institution_Id` = %s""",(institution_id))

		classList = cursor.fetchall()

		return ({"attributes": {"status_desc": "Institution Class Details",
								"status": "success"
								},
				"responseList": classList}), status.HTTP_200_OK


@name_space.route("/getInstitutionFeeByActivityAndClass/<int:institution_id>/<int:activity_id>/<string:u_class>")
class getInstitutionFeeByActivityAndClass(Resource):
	def get(self,institution_id,activity_id,u_class):

		connection = mysql_connection()
		cursor = connection.cursor()

		cursor.execute("""SELECT `cost` FROM `activity_institution_mapping` 
			WHERE `Institution_Id` = %s AND `Activity_ID` = %s 
			AND `class` = %s""",(institution_id,activity_id,u_class.upper()))


		costList = cursor.fetchone()

		return ({"attributes": {"status_desc": "Institution Fee Details",
								"status": "success"
								},
				"responseList": costList}), status.HTTP_200_OK


@name_space.route("/getMonth")
class getMonth(Resource):
	def get(self):

		connection = mysql_connection()
		cursor = connection.cursor()
		current_year = date.today().year+1
		cursor.execute("""SELECT `Month_Id`,`Month` FROM `month_details` 
			WHERE `Year` = %s""",(current_year))


		monthList = cursor.fetchall()

		return ({"attributes": {"status_desc": "Month Details",
								"status": "success"
								},
				"responseList": monthList}), status.HTTP_200_OK


@name_space.route("/studentRegistration")
class studentRegistration(Resource):
	@api.expect(addUser)
	def post(self):

		details = request.get_json()
		r = {}
		connection = mysql_connection()
		cursor = connection.cursor()
		
		personal_details = details['personal_details']
		
		add_user = details
		add_user.pop('personal_details',None)
		
		city = details.get('city')
		dateOfBirth = details.get('dateOfBirth',None)
		if not dateOfBirth:
			dateOfBirth = None
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
		userEndDate = details.get('userEndDate')
		userEnrollDate = details.get('userEnrollDate')
		userTaxId = details.get('userTaxId')
		userUniqueId = details.get('userUniqueId')
		board = details.get('board')
		studentname = details.get('studentname')
		u_class = details.get('class')
		institutionName = details.get('institutionName')
		institutionId = details.get('institutionId')
		licenseKey = details.get('licenseKey')
		fathers_Name = details.get('fathers_Name')
		fathers_occupation = personal_details.get('fathers_occupation')
		father_aadhaarNo = personal_details.get('father_aadhaarNo')
		mothers_name = personal_details.get('mothers_name')
		mothers_oocupation = personal_details.get('mothers_oocupation')
		mothers_aadharNo = personal_details.get('mothers_aadharNo')
		social_status = personal_details.get('social_status')
		social_category = personal_details.get('social_category')
		physical_status = personal_details.get('physical_status')
		religion = personal_details.get('religion')
		school_last_studied = personal_details.get('school_last_studied')
		optional_subject = personal_details.get('optional_subject')

		cursor.execute("""SELECT `institution_user_id` FROM `institution_user_personal_details` 
			WHERE `INSTITUTION_USER_NAME` =%s""",(institutionUserName))

		user_id = cursor.fetchone()


		if not user_id: 

			details_insert_query = ("""INSERT INTO `institution_user_personal_details`(`CITY`, 
				`DATE_OF_BIRTH`, `EMAIL_ID`, `FIRST_NAME`, `GENDER`, 
				`INSTITUTION_USER_NAME`, `INSTITUTION_USER_PASSWORD`, `LAST_NAME`, 
				`MIDDLE_NAME`, `PINCODE`, `PRIMARY_CONTACT_NUMBER`, `SECONDARY_CONTACT_NUMBER`, 
				`STATE`, `STREET_ADDRESS`, `USER_TAX_ID`, `USER_UNIQUE_ID`,`father_name`,
				`fathers_occupation`, `father_aadhaarNo`, `mothers_name`, `mothers_oocupation`, 
				`mothers_aadharNo`, `social_status`, `social_category`, `physical_status`, `religion`, 
				`school_last_studied`, `optional_subject`) 
				VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

			
			insert_data = (city,dateOfBirth,emailId,firstName,gender,institutionUserName,institutionUserPassword,
				lastName,middleName,pincode,primaryContactNumber,secondaryContactNumber,state,streetAddress,
				userTaxId,userUniqueId,fathers_Name,fathers_occupation,father_aadhaarNo,mothers_name,mothers_oocupation,
				mothers_aadharNo,social_status,social_category,physical_status,religion,school_last_studied,optional_subject)

			cursor.execute(details_insert_query,insert_data)
			post_url = 'http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com/flaskapp/myelsa_registration/myELSARegistration/registration'
			payload = json.dumps(add_user)
			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			post_response = requests.post(post_url, data=payload, headers=headers)
			r = post_response.json()
			res_user_id = r['responseList']['user_id']
			idx = cursor.lastrowid


			update_peronalDtls = ("""UPDATE `institution_user_personal_details` 
				SET `institution_user_id` = %s where `ID` = %s""")
			update_data = (res_user_id,idx)

			cursor.execute(update_peronalDtls,update_data)
			connection.commit()
			cursor.close()
			return r
		else:

			res_user_id = user_id['institution_user_id']
			connection.commit()
			cursor.close()
			return ({"attributes": {"status_desc": "Registration Details",
								"status": "success"
								},
				"responseList": {"STATUS": "User Added",
								"user_id": res_user_id,
								"Response": {
									"status": "Success",
									"UserId": res_user_id
								}}}), status.HTTP_200_OK


@name_space.route("/feeTransaction")
class feeTransaction(Resource):
	@api.expect(fee_transaction)
	def post(self):
		details = request.get_json()
		connection = mysql_connection()
		cursor = connection.cursor()
		currentDate = date.today().strftime("%d%b%y")
		feeDtls = details['transactionDtls']

		transaction_insert_query = ("""INSERT INTO `activity_institution_transaction`(`institution_id`, 
			`institution_user_id`, `amount`) VALUES (%s,%s,%s)""")
		transact_data = (details['institution_id'],details['user_id'],
			details['total_amount'])

		cursor.execute(transaction_insert_query,transact_data)
		tran_id = cursor.lastrowid
		details['tran_id'] = tran_id
		for t, dtls in enumerate(feeDtls):

			dtls_inser_query = ("""INSERT INTO `activity_institution_transaction_details`(`transaction_id`, 
				`institution_id`, `activity_id`, `institution_user_id`, 
				`month_id`, `amount`) VALUES (%s,%s,%s,%s,%s,%s)""")

			dtls_data = (tran_id,details['institution_id'],feeDtls[t]['activity_id'],
				details['user_id'],feeDtls[t]['month_id'],feeDtls[t]['amount'])

			cursor.execute(dtls_inser_query,dtls_data)

			feeDtls[t]['tranDtl_id'] = cursor.lastrowid
		if details['user_id'] > 0:
			url = 'http://creamsonservices.com:8080/CommunicationModule2/sendMailMessage'
			data = {
					  'mailDetails': [
					    {
					      'appParams': {},
					      'mailParams': {"total_amount":details['total_amount'],
					      				"current_date":currentDate},
					      'role': 's1',
					      'toMail': '',
					      'toNumber': '',
					      'userId': details['user_id']
					    }
					  ],
					  'sourceApp': 'FEETRAN0S'
					}
			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			response = requests.post(url, data=json.dumps(data), headers=headers)
		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Fee Transaction Details",
								"status": "success"
								},
				"responseList": details}), status.HTTP_200_OK


@name_space.route("/transactionListForStudents/<int:institution_user_id>/<int:institution_id>")
class transactionListForStudents(Resource):
	def get(self,institution_user_id,institution_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		cursor.execute("""SELECT `id`,`transaction_id`,`institution_id`,`institution_user_id`,
			`Activity_Description`,`amount`,`month_id`,date(`last_update_ts`) paid_on 
			FROM `activity_institution_transaction_details` INNER JOIN `activity_institution` 
			ON `activity_institution_transaction_details`.`activity_id`= `activity_institution`.`Activity_Id` 
			where  `institution_user_id`= %s and `institution_id`= %s 
			order by activity_institution.`activity_id` ASC""",(institution_user_id,institution_id))
		payment_dtls = cursor.fetchall()

		for i in range(len(payment_dtls)):
			if payment_dtls[i]['month_id'] > 0 :
				cursor.execute("""SELECT `Month`,`Year` FROM `month_details` 
					WHERE `Month_Id` = %s""",(payment_dtls[i]['month_id']))
				month_dtls = cursor.fetchone()
				payment_dtls[i]['month_dtls'] = month_dtls
			else:
				payment_dtls[i]['month_dtls'] = {}
			payment_dtls[i]['paid_on'] = payment_dtls[i]['paid_on'].isoformat()
		
		return ({"attributes": {"status_desc": "Payment Details Of Individual Student.",
								"status": "success"
								},
				"responseList": payment_dtls}), status.HTTP_200_OK

#-------------------------------Fees Report Analysis----------------------------------------------------------------------#

@name_space.route("/feesReportAnalysisByInsttutionUserId/<int:institution_user_id>/<string:Start_date>/<string:End_date>")
class feesReportAnalysisByInsttutionUserId(Resource):
    def get(self,institution_user_id,Start_date,End_date):
        connection = mysql_connection()
        cursor = connection.cursor()
        
        
        cursor.execute("""SELECT `id`, `transaction_id`, `institution_id`, `institution_user_id`, `Activity_Description`, `amount`, 
            `month_id`, DATE(`last_update_ts`) paid_on FROM `activity_institution_transaction_details` INNER JOIN `activity_institution` 
            ON `activity_institution_transaction_details`.`activity_id` = `activity_institution`.`Activity_Id` WHERE `institution_user_id`
            =%s AND date(`last_update_ts`) between %s and %s""",(institution_user_id,Start_date,End_date))
        stu_fees_dtls = cursor.fetchall()

        for i in range(len(stu_fees_dtls)):
              
            if stu_fees_dtls[i]['month_id'] > 0 :

                # print(payment_dtls[i]['month_id'])
                cursor.execute("""SELECT `Month`,`Year` FROM `month_details` 
                WHERE `Month_Id` = %s""",(stu_fees_dtls[i]['month_id']))

                month_dtls = cursor.fetchone()
                # print(month_dtls)
                # if payment_dtls[i]['month_id']> 0 :
                stu_fees_dtls[i]['month_dtls'] = month_dtls
            else:
                stu_fees_dtls[i]['month_dtls'] = {}

            stu_fees_dtls[i]['paid_on'] = stu_fees_dtls[i]['paid_on'].isoformat()

        return ({"attributes": {"status_desc": "PFees Details Of Individual Student.",
                                "status": "success"
                                },
                "responseList": stu_fees_dtls}), status.HTTP_200_OK

@name_space.route("/feesReportAnalysisByBatchwise/<int:group_id>/<string:Start_date>/<string:End_date>")
class feesReportAnalysisByBatchwise(Resource):
    def get(self,group_id,Start_date,End_date):
        connection = mysql_connection()
        cursor = connection.cursor()
        
        cursor.execute("""SELECT GROUP_CONCAT(`Student_Id`) as Student_Id  FROM `group_student_mapping` 
            WHERE `Group_ID` = %s""",(group_id))

        batchwise_student_id = cursor.fetchall() 
        for i in range(len(batchwise_student_id)):
         student_id= batchwise_student_id[i]['Student_Id'].split(",")
         print(student_id)
         

         cursor.execute("""SELECT `id`, `transaction_id`, `institution_id`, activity_institution_transaction_details.`institution_user_id`,
            concat(`FIRST_NAME`," ",`LAST_NAME`) as student_name, `Activity_Description`, `amount`, `month_id`, DATE(`last_update_ts`) 
            paid_on FROM `activity_institution_transaction_details` INNER JOIN `activity_institution` ON 
            `activity_institution_transaction_details`.`activity_id` = `activity_institution`.`Activity_Id` INNER JOIN 
            `institution_user_credential` ON activity_institution_transaction_details.`institution_user_id`= institution_user_credential.
            `institution_user_id` WHERE activity_institution_transaction_details.`institution_user_id` in 
            %s AND date(`last_update_ts`) between %s and %s""",(student_id,Start_date,End_date))
         stu_fees_dtls = cursor.fetchall()

         for i in range(len(stu_fees_dtls)):
              
            if stu_fees_dtls[i]['month_id'] > 0 :

                # print(payment_dtls[i]['month_id'])
                cursor.execute("""SELECT `Month`,`Year` FROM `month_details` 
                WHERE `Month_Id` = %s""",(stu_fees_dtls[i]['month_id']))

                month_dtls = cursor.fetchone()
                # print(month_dtls)
                # if payment_dtls[i]['month_id']> 0 :
                stu_fees_dtls[i]['month_dtls'] = month_dtls
            else:
                stu_fees_dtls[i]['month_dtls'] = {}

            stu_fees_dtls[i]['paid_on'] = stu_fees_dtls[i]['paid_on'].isoformat() 

         
        return ({"attributes": {"status_desc": "Batch Wise Fees Details.",
                                "status": "success"
                                },
                "responseList": stu_fees_dtls}), status.HTTP_200_OK

#-------------------------------Fees Report Analysis----------------------------------------------------------------------#

@name_space.route("ClasstestReportAnalysis/InstitutionUserId/<int:student_id>/<string:date>")
class ClasstestReportAnalysis(Resource):
    def get(self,date,student_id):

        b2b_connection = mysql_b2b_connection()
        b2b_cursor = b2b_connection.cursor()

        connection = mysql_connection()
        cursor = connection.cursor()
        details=[]

        b2b_cursor.execute("""SELECT class_test.`test_id`,`test_type`,`title`,`teacher_id`,`student_id`,`marks`,classtest_result.
            `remarks` FROM `class_test` INNER join `classtest_result` on class_test.`test_id`= 
            classtest_result.`test_id` WHERE date(class_test.`last_update_ts`)= %s and 
            classtest_result.`student_id`=%s""",(date,student_id))
        individual_cls_test = b2b_cursor.fetchall()
        # print(individual_cls_test)

        if individual_cls_test :
            for i in range(len(individual_cls_test)):
                tea_id = individual_cls_test[i]['teacher_id']
                print(tea_id)
                
                details.append(tea_id)
                
            details = tuple(details)
            print(details)  
            cursor.execute("""SELECT `INSTITUTION_USER_ID` as teacher_id,concat(`FIRST_NAME`,' ', `LAST_NAME`) as teacher_name FROM 
                    `institution_user_credential` WHERE `INSTITUTION_USER_ID`=%s""",(details))
                
            teacher_dtls = cursor.fetchone()
            individual_cls_test[i]['teacher_dtls']=teacher_dtls
            print(teacher_dtls)
        else:
             []
        return ({"attributes":{"status_desc":"Individual Class Report Analysis",
                               "status":"success"
                               },
                 "responseList":  individual_cls_test }), status.HTTP_200_OK


@name_space.route("/ClasstestReportAnalysisBatchwise/<int:group_id>/<string:date>")
class ClasstestReportAnalysis(Resource):
    def get(self,group_id,date):

        connection = mysql_connection()
        cursor = connection.cursor()

        b2b_connection = mysql_b2b_connection()
        b2b_cursor = b2b_connection.cursor()
        # details=[]

        cursor.execute("""SELECT DISTINCT(`Student_Id`) as Student_Id,concat(`FIRST_NAME`,' ',`LAST_NAME`)as 
            name,`PRIMARY_CONTACT_NUMBER`,`CLASS`,`Board` FROM `group_student_mapping` left join 
            `institution_user_credential` on group_student_mapping.`Student_Id` = institution_user_credential.
            `INSTITUTION_USER_ID` inner join student_dtls on institution_user_credential.`INSTITUTION_USER_ID` =
            student_dtls.`INSTITUTION_USER_ID_STUDENT` WHERE `Group_ID` = %s""",(group_id))

        batchwise_student = cursor.fetchall() 
        # print(batchwise_student)
        for i in range(len(batchwise_student)):
            student_id= batchwise_student[i]['Student_Id']
            # print(student_id)

            b2b_cursor.execute("""SELECT class_test.`test_id`,`test_type`,`title`,`teacher_id`,`student_id`,`marks`,classtest_result.
                `remarks` FROM `class_test` Inner join `classtest_result` on class_test.`test_id`= 
                classtest_result.`test_id` WHERE date(class_test.`last_update_ts`)= %s and 
                classtest_result.`student_id` = %s""",(date,batchwise_student[i]['Student_Id']))
            individual_cls_test = b2b_cursor.fetchall()
            # print(individual_cls_test)

            if individual_cls_test :
                # print("hi")
                batchwise_student[i]['Classtest_dtls']=individual_cls_test 
                # print(batchwise_student[i]['Classtest_dtls'])
            else:
                batchwise_student[i]['Classtest_dtls']={}
                # print(batchwise_student[i]['Classtest_dtls'])
        return ({"attributes":{"status_desc":"Individual Class Report Analysis",
                               "status":"success"
                               },
                 "responseList":  batchwise_student }), status.HTTP_200_OK  
#-----------------------------------class-test------------------------------------------------# 

@name_space.route("/getMonthCurrentYear")
class getMonthCurrentYear(Resource):
	def get(self):

		connection = mysql_connection()
		cursor = connection.cursor()
		current_year = date.today().year

		cursor.execute("""SELECT `Month_Id`,`Month` FROM `month_details` 
			WHERE `Year` = %s""",(current_year))


		monthList = cursor.fetchall()

		return ({"attributes": {"status_desc": "Month Details",
								"status": "success"
								},
				"responseList": monthList}), status.HTTP_200_OK





@name_space.route("/getInstitutionFeeByClass/<int:institution_id>/<string:u_class>")
class getInstitutionFeeByClass(Resource):
	def get(self,institution_id,u_class):

		connection = mysql_connection()
		cursor = connection.cursor()
		current_year = date.today().year

		cursor.execute("""SELECT activity_institution.`Activity_Id`,
			`Activity_Description`,`Payment_Interval`,`Activity_value`,`Institution_Id`,`class` FROM 
			`activity_institution` inner join `activity_institution_mapping` on 
			activity_institution.`Activity_Id` = activity_institution_mapping.`Activity_ID` 
			where `class`=%s and `Institution_Id`=%s""",(u_class,institution_id))


		feesList = cursor.fetchall()

		return ({"attributes": {"status_desc": "Month Details",
								"status": "success"
								},
				"responseList": feesList}), status.HTTP_200_OK





@name_space.route("/PaymentRequest")
class PaymentRequest(Resource):
	@api.expect(payment_requestDtls)
	def post(self):
		details = request.get_json()
		connection = mysql_connection()
		cursor = connection.cursor()
		currentDate = date.today().strftime("%d%b%y")
		# feeDtls = details['transactionDtls']

		paymentrequest = details['payment_request']
		payment = paymentrequest


		for pay in payment:
			institution_id = pay.get('institution_id')
			user_id = pay.get('user_id')
			activity_id = pay.get('activity_id')
			month_id = pay.get('month_id')
			no_of_month = pay.get('no_of_month')
			amount = pay.get('amount')

			cursor.execute("""SELECT `Activity_value` FROM `activity_institution` WHERE 
				`Activity_Id`=%s""",(activity_id))
			feesList = cursor.fetchone()

			paidamount = feesList['Activity_value']

			if activity_id == 7 or activity_id == 8 or activity_id == 11 or activity_id == 12:
				
				payment_request_query = ("""INSERT INTO `activity_institution_payment_request`(`student_id`,
					`institution_id`, `activity_id`,`starting_month_id`, `no_of_month`,`amount`) 
					VALUES (%s,%s,%s,%s,%s,%s)""")
				request_data = (user_id,institution_id,activity_id,'0','0',paidamount)
				cursor.execute(payment_request_query,request_data)
			else:
				
				payment_request_query = ("""INSERT INTO `activity_institution_payment_request`(`student_id`,
					`institution_id`, `activity_id`,`starting_month_id`, `no_of_month`,`amount`) 
					VALUES (%s,%s,%s,%s,%s,%s)""")
				request_data = (user_id,institution_id,activity_id,month_id,no_of_month,paidamount)
				cursor.execute(payment_request_query,request_data)
			

		cursor.close()
		
		return ({"attributes": {"status_desc": "Payment Request Details",
								"status": "success"
								}
					}), status.HTTP_200_OK




@name_space.route("/ApsfeeTransaction")
class ApsfeeTransaction(Resource):
	@api.expect(apsfee_transaction)
	def post(self):
		details = request.get_json()
		connection = mysql_connection()
		cursor = connection.cursor()
		currentDate = date.today().strftime("%d%b%y")
		feeDtls = details['apstransactionDtls']

		transaction_insert_query = ("""INSERT INTO `activity_institution_transaction`(`institution_id`, 
			`institution_user_id`, `amount`) VALUES (%s,%s,%s)""")
		transact_data = (details['institution_id'],details['user_id'],details['total_amount'])

		cursor.execute(transaction_insert_query,transact_data)
		tran_id = cursor.lastrowid
		details['tran_id'] = tran_id

		for t, dtls in enumerate(feeDtls):

			cursor.execute("""SELECT `Activity_value` FROM `activity_institution` WHERE 
				`Activity_Id`=%s""",(feeDtls[t]['activity_id']))
			feesList = cursor.fetchone()

			paidamount = feesList['Activity_value']
			if feeDtls[t]['activity_id'] == 7 or feeDtls[t]['activity_id'] == 8 or feeDtls[t]['activity_id'] == 11 or feeDtls[t]['activity_id'] == 12:
				
				dtls_inser_query = ("""INSERT INTO `activity_institution_transaction_details`(`transaction_id`, 
					`institution_id`, `activity_id`, `institution_user_id`, 
					`month_id`, `amount`) VALUES (%s,%s,%s,%s,%s,%s)""")

				dtls_data = (tran_id,details['institution_id'],feeDtls[t]['activity_id'],
					details['user_id'],0,paidamount)

				cursor.execute(dtls_inser_query,dtls_data)
			else:
				no_of_month = feeDtls[t]['no_of_month']
				
				month_id = feeDtls[t]['month_id']

				dtls_inser_query = ("""INSERT INTO `activity_institution_transaction_details`(`transaction_id`, 
					`institution_id`, `activity_id`, `institution_user_id`, 
					`month_id`, `amount`) VALUES (%s,%s,%s,%s,%s,%s)""")

				dtls_data = (tran_id,details['institution_id'],feeDtls[t]['activity_id'],
				 details['user_id'],month_id,paidamount)

				cursor.execute(dtls_inser_query,dtls_data)
				no_month = int(no_of_month)-1
				
				for i in range(0,no_month):
					
					month_id = month_id +1
					
					dtls_inser_query = ("""INSERT INTO `activity_institution_transaction_details`(`transaction_id`, 
					`institution_id`, `activity_id`, `institution_user_id`, 
					`month_id`, `amount`) VALUES (%s,%s,%s,%s,%s,%s)""")

					dtls_data = (tran_id,details['institution_id'],feeDtls[t]['activity_id'],
					 details['user_id'],month_id,paidamount)

					cursor.execute(dtls_inser_query,dtls_data)
					
			feeDtls[t]['tranDtl_id'] = cursor.lastrowid
		
		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Fee Transaction Details",
								"status": "success"
								},
				"responseList": details}), status.HTTP_200_OK



@name_space.route("/getFeesDetailsByTransactionId/<int:transaction_id>")
class getFeesDetailsByTransactionId(Resource):
	def get(self,transaction_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		current_year = date.today().year

		cursor.execute("""SELECT activity_institution_transaction_details.`activity_id`,
			`Activity_Description`,`Month`,`amount`,(SELECT sum(`amount`)as 'total' FROM `activity_institution_transaction_details`
		  WHERE `transaction_id` =%s)as 'subtotal' FROM 
			`activity_institution_transaction_details` inner join `activity_institution` 
			on activity_institution_transaction_details.`activity_id`=
			activity_institution.`Activity_Id` left join `month_details` on 
			activity_institution_transaction_details.`month_id`=month_details.`Month_Id` 
			WHERE `transaction_id` = %s""",(transaction_id,transaction_id))

		feesList = cursor.fetchall()
		
		return ({"attributes": {"status_desc": "Fees Details",
								"status": "success"
								},
				"responseList": feesList}), status.HTTP_200_OK




@name_space.route("/ApsfeesSummary")
class ApsfeesSummary(Resource):
	@api.expect(payment_requestDtls)
	def post(self):
		details = request.get_json()
		connection = mysql_connection()
		cursor = connection.cursor()
		currentDate = date.today().strftime("%d%b%y")

		paymentrequest = details['payment_request']
		payment = paymentrequest

		detail = []

		for pay in payment:
			institution_id = pay.get('institution_id')
			user_id = pay.get('user_id')
			activity_id = pay.get('activity_id')
			month_id = pay.get('month_id')
			no_of_month = pay.get('no_of_month')
			amount = pay.get('amount')

			if activity_id ==7 or activity_id ==8 or activity_id==11 or activity_id==12:
				amount = amount*1;
				# print(amount)
			else:
				amount = amount*no_of_month;
				# print(amount)
			detail.append(amount)
		detail = tuple(detail)
		# print(details)
		Sum = sum(detail)
		print(Sum)

		details['Sum']	= Sum
		cursor.close()
		
		return ({"attributes": {"status_desc": "Payment Request Details",
								"status": "success"
								},
				"responseList": details}), status.HTTP_200_OK



@name_space.route("/StudentHostelMapping")
class PaymentRequest(Resource):
	@api.expect(student_hostel)
	def post(self):
		details = request.get_json()
		connection = mysql_connection()
		cursor = connection.cursor()
		
		student_id = details['student_id']
		institution_id = details['institution_id']
		hostel_room_no = details['hostel_room_no']

		student_hostel_query = ("""INSERT INTO `student_hostel_mapping`(`student_id`,
			`institution_id`, `hostel_room_no`) VALUES (%s,%s,%s)""")
		student_hostel_data = (student_id,institution_id,hostel_room_no)
		cursor.execute(student_hostel_query,student_hostel_data)	
				
		cursor.close()
		
		return ({"attributes": {"status_desc": "Student Hostel Details Added",
								"status": "success"
								},
				"responseList": details}), status.HTTP_200_OK




@name_space.route("/UploadUserResult")
class UploadUserResult(Resource):
	@api.expect(userresult)
	def post(self):
		details = request.get_json()
		connection = mysql_connection()
		cursor = connection.cursor()
		
		institution_id = details['institution_id']
		institution_user_id = details['institution_user_id']
		content_filepath = details['content_filepath']
		content_filetype = details['content_filetype']
		remarks = details['remarks']

		student_result_query = ("""INSERT INTO `user_result`(`institution_id`, 
			`institution_user_id`, `content_filepath`, `content_filetype`, 
			`remarks`) VALUES (%s,%s,%s,%s,%s)""")
		student_result_data = (institution_id,institution_user_id,content_filepath,
			content_filetype,remarks)
		cursor.execute(student_result_query,student_result_data)	
				
		cursor.close()
		
		return ({"attributes": {"status_desc": "Student Result Details Added",
								"status": "success"
								},
				"responseList": details}), status.HTTP_200_OK




@name_space.route("/getStudentResultDetailsByUserId/<int:user_id>")
class getStudentResultDetailsByUserId(Resource):
    def get(self,user_id):
        connection = mysql_connection()
        cursor = connection.cursor()

        cursor.execute("""SELECT `result_id`,`institution_id`,
          `institution_user_id`,`content_filepath`,`content_filetype`,`remarks` 
          FROM `user_result` WHERE institution_user_id= %s""",
        (user_id))
        get_resultdtls = cursor.fetchone()

        if get_resultdtls:
	        cursor.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`)as name 
	        	FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` =%s""",
	        	(user_id))
	        user_name = cursor.fetchone()
	        if user_name:
	        	username = user_name['name']
	        	get_resultdtls['name'] = username
	        
	        else:
	            get_resultdtls['name'] =""
        else:
        	get_resultdtls = []   
        
            
            
        return ({"attributes": {"status_desc": "Student Result Details",
                                "status": "success"
                                    },
                "responseList":get_resultdtls}), status.HTTP_200_OK




@name_space.route("/updateStudentResultdetailsByResultID/<int:result_id>")
class updateStudentResultdetailsByResultID(Resource):
    @api.expect(update_result)
    def put(self,result_id):
        details = request.get_json()
        connection = mysql_connection()
        cursor = connection.cursor()
        
        Content_filepath = details.get('content_filepath')
        Content_filetype = details.get('content_filetype')
        Remarks = details.get('remarks')

        cursor.execute("""SELECT `result_id`,`content_filepath`,
        	`content_filetype`,`remarks` FROM `user_result` WHERE 
        	`result_id`=%s""",(result_id))
        student_resltdtls = cursor.fetchone()

        if student_resltdtls:
            if not Content_filepath:
                Content_filepath = student_resltdtls.get('content_filepath')
                
            if not Content_filetype:
                Content_filetype = student_resltdtls.get('content_filetype')
                
            if not Remarks:
                Remarks = student_resltdtls.get('remarks')

        update_student_result = ("""UPDATE `user_result` SET 
        	`content_filepath`=%s,`content_filetype`=%s,`remarks`=%s 
        	WHERE `result_id`= %s""")
        student_result_data = (Content_filepath,Content_filetype,Remarks,
            result_id)
        
        updatedata = cursor.execute(update_student_result,student_result_data)
        
        connection.commit()
        
        return ({"attributes": {"status_desc": "Student Result Update Details.",
                            "status": "success"
                            },
                            "responseList":details}), status.HTTP_200_OK



@name_spaceV2.route("/FeeTransactionV2")
class FeeTransactionV2(Resource):
	@api.expect(feeTransactionDtls)
	def post(self):
		details = request.get_json()
		connection = mysql_connection()
		cursor = connection.cursor()
		
		feeDtls = details.get('feetransaction')
		totalamount = feeDtls[0].get('totalamount')
		institutionId = feeDtls[0].get('institution_id')
		user_id = feeDtls[0].get('institution_user_id')
		
		fees = feeDtls

		fee_query = ("""INSERT INTO `institution_fee_transaction`(`institution_id`,
		 `institution_user_id`,`amount`) VALUES (%s,%s,%s)""")
		transactdata = (institutionId,user_id,totalamount)

		cursor.execute(fee_query,transactdata)
		transaction_id = cursor.lastrowid
		details['feetransaction_id'] = transaction_id

		for fee in fees:
			institution_id = fee.get('institution_id')
			institution_user_id = fee.get('institution_user_id')
			clss = fee.get('class')
			stream = fee.get('stream')
			fee_type = fee.get('fee_type')
			month_id = fee.get('month_id')
			amount = fee.get('amount')
			
			if stream == None:
				stream = ''
			feeDtls_query = ("""INSERT INTO `institution_fee_transaction_dtls`(`transaction_id`,
				`institution_id`,`institution_user_id`,`class`,`stream`,
				`fee_type`,`month_id`,`amount`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""")
			transactDtlsdata = (transaction_id,institution_id,institution_user_id,
				clss,stream,fee_type,month_id,amount)

			cursor.execute(feeDtls_query,transactDtlsdata)
			
		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Fee Transaction Details",
								"status": "success"
								},
				"responseList": details}), status.HTTP_200_OK


@name_spaceV2.route("/getFeeTransactionHistotyByStudentId/<int:student_id>")
class getFeeTransactionHistotyByStudentId(Resource):
	def get(self,student_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		
		cursor.execute("""SELECT `transaction_id`,`status` FROM 
			`institution_fee_transaction` where `institution_user_id`=%s""",
			(student_id))
		transaction = cursor.fetchall()

		for i in range(len(transaction)):
			if transaction[i]['status'] == 'Complete':
				cursor.execute("""SELECT Id,iftd.`institution_id`,
					ind.`INSTITUTION_NAME`,`institution_user_id`,`class`,`stream`,
					`fee_type`,iftd.`month_id`,`Month`,`amount`,`last_update_ts` FROM 
					`institution_fee_transaction_dtls` iftd left join `institution_dtls` ind 
					on iftd.`institution_id`= ind.`INSTITUTION_ID` left join 
					`month_details` md on iftd.`month_id`= md.`Month_Id` where 
					`institution_user_id`=%s and iftd.`transaction_id`=%s""",
					(student_id,transaction[i]['transaction_id']))
				transactiondtls = cursor.fetchall()
				
				transaction[i]['transactinHistory'] = transactiondtls
				for i in range(len(transactiondtls)):
					transactiondtls[i]['last_update_ts'] = transactiondtls[i]['last_update_ts'].isoformat()
					if transactiondtls[i]['institution_id'] == 2226:
						transactiondtls[i]['INSTITUTION_NAME']  = '2226'
						
					else:
						transactiondtls[i]['INSTITUTION_NAME']  = transactiondtls[i]['INSTITUTION_NAME']
					
					if transactiondtls[i]['month_id'] == 0:
						transactiondtls[i]['Month']  = ''
						
					else:
						transactiondtls[i]['Month']  = transactiondtls[i]['Month']
					
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Fee Transaction Details",
                                "status": "success"
                                },
                 "responseList": transaction}), status.HTTP_200_OK



@name_spaceV2.route("/createPaymentRequest")
class createPaymentRequest(Resource):
	@api.expect(create_payment_link_model)
	def post(self):
		
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		client_id = 'y1ByaJbMoPCxU3pNREwGjS9p2cqLhUvIPrNasDt2'
		client_secret = 'U6yCJ41RXA9MuIsLMu706qVWG7NvXpUsKEXLuZFcBeQAQ8v6xkhzMag8ZnAE7g0JfNx3jTm7kBxeiAKZaJytmCkYKswFQMdmaoRuw11i4KLq4A3oKUT8gTawhomw3l17'
		referrer_id = 'APS'

		payload = {"grant_type": "client_credentials",
					"client_id": client_id,
					"client_secret": client_secret}
		# print(payload)

		authResponse = requests.post(MOJO_BASE_URL+"oauth2/token/",
			data=payload).json()
		# print(authResponse)

		accesstoken = authResponse.get('access_token')

		headers = {"Authorization": "Bearer "+accesstoken}

		details['redirect_url'] = 'http://creamsonservices.com/apsinstamojo_test.php'
		details['allow_repeated_payments'] = False
		details['send_email'] = False
		details['send_sms'] = True
		feetransactionId= details.get('feetransaction_id',None)
		details.pop('feetransaction_id',None) 
		userId = details.get('user_id',None)
		details.pop('user_id',None)
		institutionId = details.get('institution_id',None)
		details.pop('institution_id',None)
		transactionId = details.get('transaction_id',None)
		details.pop('transaction_id',None)
		mojoResponse = requests.post(MOJO_BASE_URL+"v2/payment_requests/",
			data=details, headers=headers)

		statusCode = mojoResponse.status_code
		# print(statusCode)
		response = mojoResponse.json()
		# print(response)

		if statusCode == 201:

			mojoResInsertQuery = ("""INSERT INTO `instamojo_payment_request`(`instamojo_request_id`, 
				`phone`, `email`, `buyer_name`, `amount`, `purpose`, `status`, `send_sms`, 
				`send_email`, `sms_status`, `email_status`, `shorturl`, `longurl`, 
				`redirect_url`, `webhook`, `scheduled_at`, `expires_at`, `allow_repeated_payments`, 
				`mark_fulfilled`, `customer_id`, `created_at`, `modified_at`, `resource_uri`, 
				`remarks`, `user_id`,`institution_id`,`transaction_id`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
				%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

			created_at = datetime.strptime(response.get('created_at'),'%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
			modified_at = datetime.strptime(response.get('modified_at'),'%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')

			mojoData = (response.get('id'),details.get('phone'),response.get('email'),
				response.get('buyer_name'),response.get('amount'),response.get('purpose'),
				response.get('status'),response.get('send_sms'),response.get('send_email'),
				response.get('sms_status'),response.get('email_status'),response.get('shorturl'),
				response.get('longurl'),response.get('redirect_url'),response.get('webhook'),
				response.get('scheduled_at'),response.get('expires_at'),response.get('allow_repeated_payments'),
				response.get('mark_fulfilled'),response.get('customer_id'),
				created_at,modified_at,response.get('resource_uri'),feetransactionId,userId,institutionId,transactionId)
			cursor.execute(mojoResInsertQuery,mojoData)

			requestId = cursor.lastrowid
			response['paymentRequestId'] = requestId

			connection.commit()

			msg = 'Payment Link Created'
		else:
			response = {}
			msg = 'No matching credentials'
		cursor.close()

		return ({"attributes": {"status_desc": "Instamojo payment request Details",
								"status": "success",
								"msg":msg},
				"responseList": response}), status.HTTP_200_OK



@name_spaceV2.route("/askForFess")
class askForFess(Resource):
	@api.expect(ask_for_fees_model)
	def post(self):
		
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()


		URL = BASE_URL + "fee_management/feeManagementV2/createPaymentRequest"

		headers = {'Content-type':'application/json', 'Accept':'application/json'}

		amount = details.get('amount')
		purpose = details.get('purpose')
		teacher_id = details.get('teacher_id')
		institution_id = details.get('institution_id')
		feetransaction_id = details.get('feetransaction_id')
		student_id = details.get('student_id')
		
		initiatePaymentQuery = ("""INSERT INTO `instamojo_initiate_payment`(`user_id`, 
			`institution_id`,`initiated_for`) VALUES (%s,%s,%s)""")
		initiateData = (teacher_id,institution_id,'I')
		cursor.execute(initiatePaymentQuery,initiateData)
		transaction_id = cursor.lastrowid

		cursor.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name,
			`PRIMARY_CONTACT_NUMBER` as phone FROM 
			`institution_user_credential` WHERE 
			`INSTITUTION_USER_ID` = %s""",(student_id))

		student = cursor.fetchone()

		if student:
			student_name = student['name']
			student_phone = student['phone']

			payload = {"amount":amount,
						"purpose":purpose,
						"buyer_name":student_name,
						"phone":student_phone,
						"feetransaction_id":feetransaction_id,
						"user_id":teacher_id,
						"institution_id":institution_id,
						"transaction_id":transaction_id}
			
			mojoResponse = requests.post(URL,data=json.dumps(payload), headers=headers).json()

			# print(mojoResponse)
			if mojoResponse.get('attributes').get('msg') == 'Payment Link Created':

				paymentStudentMapQuery = ("""INSERT INTO `instamojo_payment_student_mapping`(
					`request_id`, `student_id`, `status`) VALUES (%s,%s,%s)""")
				responseList = mojoResponse.get('responseList')
				mapData = (responseList.get('paymentRequestId'),student_id,responseList.get('status'))

				cursor.execute(paymentStudentMapQuery,mapData)
			elif mojoResponse.get('attributes').get('msg') == 'No matching credentials':
				mojoResponse = "Enter valid EmailId Or Phone No"
				
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Instamojo Payment Initiation Details",
							"status": "success"},
			"responseList": mojoResponse}), status.HTTP_200_OK



@name_spaceV2.route("/updatePaymentDetails/<string:payment_id>/<string:payment_status>/<string:payment_request_id>")
class updatePaymentDetails(Resource):
	def put(self,payment_id,payment_status,payment_request_id):
		
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		update_status = 'Complete'
		if payment_status == 'Credit':

			updatePaymentQuery = ("""UPDATE `instamojo_payment_request` SET  
				`payment_status` = %s,`payment_id`= %s, `status` = %s WHERE `instamojo_request_id`= %s""")

			paymentData = (payment_status,payment_id,update_status,payment_request_id)

			cursor.execute(updatePaymentQuery,paymentData)

			cursor.execute("""SELECT `request_id`,`remarks` FROM `instamojo_payment_request` 
				WHERE `instamojo_request_id` = %s""",(payment_request_id))
			reqDtls = cursor.fetchone()

			reqId = reqDtls.get('request_id')	
			feetransaction_id = reqDtls.get('remarks')	

			cursor.execute("""SELECT `student_id` FROM `instamojo_payment_student_mapping`
			 	WHERE `request_id` = %s""",(reqId))
			preqDtls = cursor.fetchone()

			student_id = preqDtls.get('student_id')	
			
			updateStudentStatus = ("""UPDATE `instamojo_payment_student_mapping` SET 
				`status` = %s where `request_id` = %s""")
			cursor.execute(updateStudentStatus,(update_status,reqId))

			updatefeeStatus = ("""UPDATE `institution_fee_transaction` SET 
				`status` = %s where `institution_user_id` = %s and 
				`transaction_id`=%s""")
			cursor.execute(updatefeeStatus,('Complete',student_id,feetransaction_id))

			msg = 'Payment Details Updated'
		else:
			msg = 'Payment Details Not Updated'
			
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Instamojo Payment Details",
							"status": "success"},
			"responseList": msg}), status.HTTP_200_OK

