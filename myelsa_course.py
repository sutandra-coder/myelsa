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
	                             db='creamson_user_library',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection'''

def mysql_connection():
	connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
	                             user='admin',
	                             password='cbdHoRPQPRfTdC0uSPLt',
	                             db='creamson_user_library',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

#----------------------database-connection---------------------#

#----------------------database-connection-loginDb---------------------#
'''def mysql_connection_logindb():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='creamson_logindb',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection
'''
def mysql_connection_logindb():
	connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
	                             user='admin',
	                             password='cbdHoRPQPRfTdC0uSPLt',
	                             db='creamson_logindb',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection
#----------------------database-connection-loginDb---------------------#

BASE_URL = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/'

myelsa_course = Blueprint('myelsa_course_api', __name__)
api = Api(myelsa_course,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('MyelsaCourse',description='Myelsa Course')

course_postmodel = api.model('SelectCourse', {
	"institution_id":fields.Integer(required=True),
	"course_title":fields.String(required=True),
	"course_description":fields.String(required=True),
	"course_image":fields.String(required=True),
	"course_filetype":fields.String(required=True),
	"teacher_id":fields.Integer(required=True),
	"subject_id":fields.Integer(required=True),
	"topic_id":fields.Integer(required=True)
	})

course_putmodel = api.model('UpdateCourse', {
	"course_title":fields.String,
	"course_description":fields.String,
	"course_image":fields.String,
	"course_filetype":fields.String,
	"teacher_id":fields.Integer,
	"subject_id":fields.Integer,
	"topic_id":fields.Integer
	})

course_fees_postmodel = api.model('CourseFees', {
	"total_fee":fields.Float(),
	"installment_available":fields.String(required=True),
	"installment_type":fields.String(),
	"course_id":fields.Integer(required=True),
	"no_of_installments":fields.Integer(),
	"is_paid_course":fields.String()
	})


course_fees_putmodel = api.model('UpdateCourseFees', {
	"total_fee":fields.Float(),
	"installment_available":fields.String(),
	"installment_type":fields.String(),
	"course_id":fields.Integer(),
	"no_of_installments":fields.Integer(),
	"is_paid_course":fields.String()
	})


student_course_model = api.model('StudentCourse', {
	"student_id":fields.List(fields.Integer()),
	"group_id":fields.List(fields.Integer()),
	"course_id":fields.Integer(required=True),
	"payment_mode":fields.String(required=True),
	"payment_type":fields.String(required=True),
	"no_of_installment":fields.Integer(required=True),
	"discount_given":fields.String(required=True),
	"discount":fields.Float(required=True),
	"is_group":fields.String(required=True),
	"Institution_ID":fields.Integer(required=True),
	"teacher_id":fields.Integer(required=True),
	"purchase_on":fields.String(required=True),
	"assign_course_fees":fields.String(required=True)
	})

course_content_model = api.model('course_content_model', {
	"teacher_id":fields.Integer(required=True),
	"content_name":fields.String(required=True),
	"content_filepath":fields.String(required=True),
	"content_filetype":fields.String(required=True),
	"course_id":fields.Integer(required=True),
	"topic_id":fields.Integer()
	})

course_update_content_model = api.model('upload_model', {
	"teacher_id":fields.Integer,
	"content_name":fields.String,
	"content_filepath":fields.String,
	"content_filetype":fields.String,
	"topic_id":fields.Integer
	})

folder_course_postmodel = api.model('SelectFolderCourse', {
	"institution_id":fields.Integer(required=True),
	"course_title":fields.String(required=True),
	"course_description":fields.String(required=True),
	"course_image":fields.String(required=True),
	"course_filetype":fields.String(required=True),
	"teacher_id":fields.Integer(required=True),
	"subject_id":fields.Integer(required=True),
	"topic_id":fields.Integer(required=True),
	"folder_id":fields.Integer(required=True),
	"folder_name":fields.String()
	})
create_payment_dtls_model = api.model('create_payment_dtls_model', {
	"student_id":fields.Integer(),
	"course_id":fields.Integer(),
	"payment_mode":fields.String(),
	"payment_type":fields.String(),
	"no_of_installment":fields.Integer(),
	"discount_given":fields.String(),
	"discount":fields.Float(),
	"institution_id":fields.Integer(),
	"teacher_id":fields.Integer(),
	"total_amount":fields.String(),
	})


create_payment_course_combo = api.model('create_payment_course_combo_model', {
	"student_id":fields.Integer(),
	"combo_id":fields.Integer(),
	"course_id":fields.List(fields.Integer()),
	"payment_mode":fields.String(),
	"payment_type":fields.String(),
	"no_of_installment":fields.Integer(),
	"discount_given":fields.String(),
	"discount":fields.Float(),
	"institution_id":fields.Integer(),
	"teacher_id":fields.Integer(),
	"total_amount":fields.String(),
	})




#----------------------Post-Course---------------------#
@name_space.route("/CreateCourse")
class CreateCourse(Resource):
	@api.expect(course_postmodel)
	def post(self):
	
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		institution_id = details['institution_id']
		course_title = details['course_title']
		course_description = details['course_description']
		course_image = details['course_image']
		course_filetype = details['course_filetype']
		teacher_id = details['teacher_id']
		subject_id = details['subject_id']
		topic_id = details['topic_id']

		insert_query = ("""INSERT INTO `instituition_course_master`(`institution_id`,`course_title`,`course_description`,`course_image`,
		`course_filetype`,`teacher_id`,`subject_id`,`topic_id`) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")
		data = (institution_id,course_title,course_description,course_image,course_filetype,teacher_id,subject_id,topic_id)
		cursor.execute(insert_query,data)

		course_id = cursor.lastrowid
		details['course_id'] = course_id

		connection.commit()
		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Course Details.",
	    				"status": "success"
	    				},
	    				"responseList":{"CourseDtls":details}}), status.HTTP_200_OK

#----------------------Post-Course---------------------#

#----------------------Delete-Course---------------------#

@name_space.route("/courseDelete/<int:course_id>")
class courseDelete(Resource):
	def delete(self, course_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		course_delete_query = ("""DELETE FROM `instituition_course_master` WHERE `course_id` = %s """)
		delData = (course_id)
		
		cursor.execute(course_delete_query,delData)
		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Delete Course",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Course---------------------#

#----------------------Get-Course-List---------------------#

@name_space.route("/getCourseList/<int:teacher_id>")	
class getCourseList(Resource):
	def get(self,teacher_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		course_get_query = ("""SELECT `course_id`,`institution_id`,`course_title`,`course_description`,`course_image`,
			`course_filetype`,`teacher_id`,`subject_id`,`topic_id`
			FROM `instituition_course_master` WHERE `teacher_id` = %s """)

		getData = (teacher_id)
		cursor.execute(course_get_query,getData)

		couse_data = cursor.fetchall()

		for key,data in enumerate(couse_data):
			get_topic_query = ("""SELECT `topic_id`,`topic_name`
			FROM `topic` WHERE `topic_id` = %s """)

			topicData = (data['topic_id'])

			row_count_topic = cursor.execute(get_topic_query,topicData)

			if row_count_topic>0:
				topic_data = cursor.fetchone()

				couse_data[key]['topic_name'] = topic_data['topic_name']
				
			else:
				couse_data[key]['topic_name'] = ""

			get_subject_query = ("""SELECT `subject_id`,`subject_name`
			FROM `subject` WHERE `subject_id` = %s """)

			subjectData = (data['subject_id'])

			row_subject_topic = cursor.execute(get_subject_query,subjectData)

			if row_subject_topic>0:
				subject_data = cursor.fetchone()

				couse_data[key]['subject_name'] = subject_data['subject_name']
				
			else:
				couse_data[key]['subject_name'] = ""
				
		return ({"attributes": {
		    		"status_desc": "Course_details",
		    		"status": "success"
		    	},
		    	"responseList":couse_data}), status.HTTP_200_OK
		
#----------------------Get-Course-List---------------------#

#----------------------Get-Course-List-with-institute---------------------#

@name_space.route("/getCourseListIns/<int:teacher_id>/<int:institution_id>")	
class getCourseListIns(Resource):
	def get(self,teacher_id,institution_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		if teacher_id == 0:
			course_get_query = ("""SELECT `course_id`,`institution_id`,`course_title`,`course_description`,`course_image`,
			`course_filetype`,`teacher_id`,`subject_id`,`topic_id`
			FROM `instituition_course_master` WHERE `institution_id` = %s """)

			getData = (institution_id)

			row_count_course = cursor.execute(course_get_query,getData)

			couse_data = cursor.fetchall()
		else:	
			course_get_query = ("""SELECT `course_id`,`institution_id`,`course_title`,`course_description`,`course_image`,
				`course_filetype`,`teacher_id`,`subject_id`,`topic_id`
				FROM `instituition_course_master` WHERE `teacher_id` = %s and `institution_id` = %s""")

			getData = (teacher_id,institution_id)

			row_count_course = cursor.execute(course_get_query,getData)

			if row_count_course>0:
				couse_data = cursor.fetchall()

			else:
				course_get_query = ("""SELECT `course_id`,`institution_id`,`course_title`,`course_description`,`course_image`,
				`course_filetype`,`teacher_id`,`subject_id`,`topic_id`
				FROM `instituition_course_master` WHERE `institution_id` = %s""")

				getData = (institution_id)

				cursor.execute(course_get_query,getData)

				couse_data = cursor.fetchall()

		for key,data in enumerate(couse_data):
			get_topic_query = ("""SELECT `topic_id`,`topic_name`
			FROM `topic` WHERE `topic_id` = %s """)

			topicData = (data['topic_id'])

			row_count_topic = cursor.execute(get_topic_query,topicData)

			if row_count_topic>0:
				topic_data = cursor.fetchone()

				couse_data[key]['topic_name'] = topic_data['topic_name']
				
			else:
				couse_data[key]['topic_name'] = ""

			get_subject_query = ("""SELECT `subject_id`,`subject_name`
			FROM `subject` WHERE `subject_id` = %s """)

			subjectData = (data['subject_id'])

			row_subject_topic = cursor.execute(get_subject_query,subjectData)

			if row_subject_topic>0:
				subject_data = cursor.fetchone()

				couse_data[key]['subject_name'] = subject_data['subject_name']
				
			else:
				couse_data[key]['subject_name'] = ""
			
			no_of_student_assign_query = ("""SELECT count(Distinct(student_id)) as no_of_student_assign FROM `student_course_master` where course_id = %s """)	
			student_assign_data = (data['course_id'])
			row_student_assign = cursor.execute(no_of_student_assign_query,student_assign_data)

			if row_student_assign>0:
				student_data = cursor.fetchone()

				couse_data[key]['no_of_student_assign'] = student_data['no_of_student_assign']
				
			else:
				couse_data[key]['no_of_student_assign'] = ""

			couse_data[key]['no_of_student_seen'] = 1
				
		return ({"attributes": {
		    		"status_desc": "Course_details",
		    		"status": "success"
		    	},
		    	"responseList":couse_data}), status.HTTP_200_OK
		
#----------------------Get-Course-List-with-institute---------------------#

#----------------------Put-Course---------------------#

@name_space.route("/updateCourse/<int:course_id>")
class updateCourse(Resource):
	@api.expect(course_putmodel)
	def put(self, course_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		if details and "course_title" in details:
			course_title = details['course_title']
			course_update_query = ("""UPDATE `instituition_course_master` SET `course_title` = %s
				WHERE `course_id` = %s """)
			update_data = (course_title,course_id)
			cursor.execute(course_update_query,update_data)

		if details and "course_description" in details:	
			course_description = details['course_description']
			course_update_query = ("""UPDATE `instituition_course_master` SET `course_description` = %s
				WHERE `course_id` = %s """)
			update_data = (course_description,course_id)
			cursor.execute(course_update_query,update_data)

		if details and "course_image" in details:		
			course_image = details['course_image']
			course_update_query = ("""UPDATE `instituition_course_master` SET `course_image` = %s
				WHERE `course_id` = %s """)
			update_data = (course_image,course_id)
			cursor.execute(course_update_query,update_data)

		if details and "course_filetype" in details:	
			course_filetype = details['course_filetype']
			course_update_query = ("""UPDATE `instituition_course_master` SET `course_filetype` = %s
				WHERE `course_id` = %s """)
			update_data = (course_filetype,course_id)
			cursor.execute(course_update_query,update_data)

		if details and "subject_id" in details:	
			subject_id = details['subject_id']
			course_update_query = ("""UPDATE `instituition_course_master` SET `subject_id` = %s
				WHERE `course_id` = %s """)
			update_data = (subject_id,course_id)
			cursor.execute(course_update_query,update_data)

		if details and "topic_id" in details:	
			topic_id = details['topic_id']
			course_update_query = ("""UPDATE `instituition_course_master` SET `topic_id` = %s
				WHERE `course_id` = %s """)
			update_data = (topic_id,course_id)
			cursor.execute(course_update_query,update_data)

		
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Course",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Put-Course---------------------#

#----------------------Post-Course-Fees---------------------#

@name_space.route("/CreateCourseFees")
class CreateCourseFees(Resource):
	@api.expect(course_fees_postmodel)
	def post(self):
	
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		total_fee = details.get('total_fee',0)
		installment_available = details.get('installment_available')
		course_id = details.get('course_id')
		is_paid_course = details.get('is_paid_course')
		no_of_installments = details.get('no_of_installments',0)
		installment_type = details.get('installment_type')

		insert_query = ("""INSERT INTO `course_fee_mapping`(`is_paid_course`,`total_fee`,`installment_available`,
			`installment_type`,`course_id`,`no_of_installments`) VALUES(%s,%s,%s,%s,%s,%s)""")

		
		feesData = (is_paid_course,total_fee,installment_available,installment_type,course_id,no_of_installments)
		
		cursor.execute(insert_query,feesData)

		coursefeeId = cursor.lastrowid

		details['coursefeeId'] = coursefeeId

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Course Fees Details.",
							"status": "success"},
	    		"responseList":details}), status.HTTP_200_OK
#----------------------Post-Student-Course---------------------#

#----------------------Put-Course-Fees---------------------#

@name_space.route("/updateCourseFees/<int:fee_id>")
class updateCourseFees(Resource):
	@api.expect(course_fees_putmodel)
	def put(self, fee_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		if details and "total_fee" in details:
			total_fee = details['total_fee']
			course_fees_update_query = ("""UPDATE `course_fee_mapping` SET `total_fee` = %s
				WHERE `fee_id` = %s """)
			update_data = (total_fee,fee_id)
			cursor.execute(course_fees_update_query,update_data)

		if details and "installment_available" in details:	
			installment_available = details['installment_available']
			course_fees_update_query = ("""UPDATE `course_fee_mapping` SET `installment_available` = %s
				WHERE `fee_id` = %s """)
			update_data = (installment_available,fee_id)
			cursor.execute(course_fees_update_query,update_data)

		if details and "installment_type" in details:		
			if details['installment_type'] == '':
				installment_type = None
			else:	
				installment_type = details['installment_type']
				
			course_fees_update_query = ("""UPDATE `course_fee_mapping` SET `installment_type` = %s
				WHERE `fee_id` = %s """)
			update_data = (installment_type,fee_id)
			cursor.execute(course_fees_update_query,update_data)

		if details and "course_id" in details:	
			course_id = details['course_id']
			course_update_query = ("""UPDATE `course_fee_mapping` SET `course_id` = %s
				WHERE `fee_id` = %s """)
			update_data = (course_id,fee_id)
			cursor.execute(course_update_query,update_data)

		if details.get('no_of_installments'):
			course_fees_update_query = ("""UPDATE `course_fee_mapping` SET `no_of_installments` = %s
				WHERE `fee_id` = %s """)
			update_data = (details.get('no_of_installments'),fee_id)
			cursor.execute(course_fees_update_query,update_data)

		if details.get('is_paid_course'):
			course_fees_update_query = ("""UPDATE `course_fee_mapping` SET `is_paid_course` = %s
				WHERE `fee_id` = %s """)
			update_data = (details.get('is_paid_course'),fee_id)
			cursor.execute(course_fees_update_query,update_data)
		
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Course Fees",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Put-Course-Fees---------------------#

#----------------------Get-Course-Fees-List---------------------#

@name_space.route("/getCourseFeesList/<int:course_id>")	
class getCourseFeesList(Resource):
	def get(self,course_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		course_get_query = ("""SELECT `fee_id`,`total_fee`,`installment_available`,`installment_type`,
			`course_id`,`is_paid_course`,`no_of_installments`
			FROM `course_fee_mapping` WHERE `course_id` = %s""")

		getData = (course_id)
		cursor.execute(course_get_query,getData)

		couse_fees_data = cursor.fetchone()
		if not couse_fees_data:
			couse_fees_data = {}

		return ({"attributes": {
		    		"status_desc": "Course_Fees_details",
		    		"status": "success"
		    	},
		    	"responseList":couse_fees_data}), status.HTTP_200_OK

#----------------------Get-Course-Fees-List---------------------#

#----------------------Delete-Course-Fees---------------------#

@name_space.route("/courseFeesDelete/<int:fee_id>")
class courseFeesDelete(Resource):
	def delete(self, fee_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		course_fees_delete_query = ("""DELETE FROM `course_fee_mapping` WHERE `fee_id` = %s """)
		delData = (fee_id)
		
		cursor.execute(course_fees_delete_query,delData)
		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Delete Course Fees",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Course-Fees---------------------#

#----------------------Assign-Course-Fees---------------------#

@name_space.route("/AssignCourseFees")
class AssignCourseFees(Resource):
	@api.expect(student_course_model)
	def post(self):
	
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		student_id = details['student_id']
		course_id = details['course_id']
		payment_mode = details['payment_mode']
		payment_type = details['payment_type']
		purchased_on = details['purchase_on']
		discount_given = details['discount_given']
		discount = details['discount']
		teacher_id = details['teacher_id']
		Institution_ID = details['Institution_ID']		

		get_course_fee_mapping_query = ("""SELECT `total_fee`,`installment_available`,`installment_type`
			FROM `course_fee_mapping` WHERE `course_id` = %s """)

		getData = (course_id)
		rows_count = cursor.execute(get_course_fee_mapping_query,getData)

		couse_fees_data = cursor.fetchone()

		if rows_count>0:
			if couse_fees_data['installment_available'] == "y":
				no_of_installment = details['no_of_installment']
			else:	
				no_of_installment = 0

			if discount_given == "y":
				discount_percentage = discount
				discount = (couse_fees_data['total_fee']/100)*discount_percentage
				actual_amount = couse_fees_data['total_fee'] - discount
			else:
				discount_percentage = 0	
				discount = None
				actual_amount = couse_fees_data['total_fee']

			insert_student_course_fees = ("""INSERT INTO `student_coursefee_mapping`(`student_id`,`course_id`,`payment_mode`,
								`payment_type`,`no_of_installment`,`total_amount`,`discount_given`,`discount_percentage`,`discount`,`actual_amount`,`purchased_on`) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
			student_course_data = (student_id,course_id,payment_mode,payment_type,no_of_installment,couse_fees_data['total_fee'],discount_given,discount_percentage,discount,actual_amount,purchased_on)
			cursor.execute(insert_student_course_fees,student_course_data)

			course_fees_id = cursor.lastrowid

			
			course_fees_update_query = ("""UPDATE `student_course_master` SET `coursefee_id` = %s
				WHERE `course_id` = %s and `student_id` = %s and `teacher_id` = %s and `Institution_ID` = %s""")
			update_data = (course_fees_id,course_id,student_id,teacher_id,Institution_ID)
			cursor.execute(course_fees_update_query,update_data)	

			
			
			if couse_fees_data['installment_available'] == "y":	
				is_pending = 'y'

				if discount_given == "y":
						
					payment_amount = actual_amount/details['no_of_installment']
				else:	
					payment_amount = couse_fees_data['total_fee']/details['no_of_installment']	


				

				insert_student_course_fees_payment = ("""INSERT INTO `student_coursefee_payment_details`(`student_id`,`payment_amount`,`payment_duedate`,`is_pending`,
								`coursefee_id`) VALUES(%s,%s,%s,%s,%s)""")
				

				payment_due_date = purchased_on

				for x in range(details['no_of_installment']):

					if couse_fees_data['installment_type'] == "monthly":

						payment_due_date=later_date(payment_due_date)

					else:
						payment_due_date = one_year_later_date(purchased_on,x)

					student_course_fees_payment_data = (student_id,payment_amount,payment_due_date,is_pending,course_fees_id)
					cursor.execute(insert_student_course_fees_payment,student_course_fees_payment_data)
			else:
				is_pending = 'y'

				if discount_given == "y":
						
					payment_amount = actual_amount
				else:	
					payment_amount = couse_fees_data['total_fee']

				if couse_fees_data['installment_type'] == "monthly":	
					payment_due_date = later_date(purchased_on)
					
				else:
					payment_due_date = one_year_later_date(purchased_on,1)	

				insert_student_course_fees_payment = ("""INSERT INTO `student_coursefee_payment_details`(`student_id`,`payment_amount`,`is_pending`,`payment_duedate`,
								`coursefee_id`) VALUES(%s,%s,%s,%s,%s)""")
				student_course_fees_payment_data = (student_id,payment_amount,is_pending,payment_due_date,course_fees_id)

				cursor.execute(insert_student_course_fees_payment,student_course_fees_payment_data)		

		connection.commit()
		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Course Details.",
	    				"status": "success"
	    				},
	    				"responseList":{"CourseDtls":couse_fees_data}}), status.HTTP_200_OK

#----------------------Assign-Course-Fees---------------------#
def assignedCourseNotification(course_id,student_list):
	connection = mysql_connection()
	cursor = connection.cursor()

	conn = mysql_connection_logindb()
	curlog = conn.cursor()
	current_date = datetime.now()
	cursor.execute("""SELECT `course_title`,`teacher_id` FROM `instituition_course_master` 
		WHERE `course_id` = %s""",(course_id))

	courseDtls = cursor.fetchone()
	teacherId = courseDtls.get('teacher_id')
	courseDesc = courseDtls.get('course_title')

	curlog.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name 
					FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(teacherId))
	tidDtls = curlog.fetchone()

	notify_url = BASE_URL + 'app_notify/AppCommunicationAPI/appMessage'
	headers = {'Content-type':'application/json', 'Accept':'application/json'}
	for sid in student_list:
		curlog.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name 
				FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(sid))
		sidDtls = curlog.fetchone()
		data = {'appParams': {},
				'mailParams': {"student":sidDtls.get('name'),
								"coursename":courseDesc,
								"teacher":tidDtls.get('name')},
				'role': 's1',
				'toMail': '',
				'toNumber': '',
				'userId': sid,
				'sourceapp': 'CRS00S1'
				}
		
		response = requests.post(notify_url, data=json.dumps(data), headers=headers)

	
	cursor.close()
	curlog.close()


class Compute(Thread):
	def __init__(self, request, funcname):
		Thread.__init__(self)
		self.request = request
		self.funcname = funcname

	def run(self):
		time.sleep(5)
		if self.funcname == 'StudentAssignCourse':
			course_id = self.request[0]
			studentList = self.request[1]
			assignedCourseNotification(course_id,studentList)
		else:
			pass 

#----------------------Assign-Student-Course---------------------#
@name_space.route("/StudentAssignCourse")
class StudentAssignCourse(Resource):
	@api.expect(student_course_model)
	def post(self):
		details = request.get_json()		

		connection = mysql_connection()
		cursor = connection.cursor()

		studentList = details.get('student_id',[])
		course_id = details['course_id']
		Institution_ID = details['Institution_ID']
		teacher_id = details['teacher_id']
		payment_mode = details['payment_mode']
		payment_type = details['payment_type']
		no_of_installment = details['no_of_installment']
		discount_given = details['discount_given']
		discount = details['discount']
		purchase_on = details['purchase_on']
		assign_course_fees = details['assign_course_fees']

		insert_query = ("""INSERT INTO `student_course_master`(`student_id`,`course_id`,`Institution_ID`,`teacher_id`) VALUES(%s,%s,%s,%s)""")
			
		for sid in studentList:
			data= (sid,course_id,Institution_ID,teacher_id)
			cursor.execute(insert_query,data)

			if assign_course_fees == "y":
				assign_course_fees_url = BASE_URL + 'myelsa_course/MyelsaCourse/AssignCourseFees'

				post_data = {
					  "student_id": sid,
					  "course_id": course_id,
					  "payment_mode": payment_mode,
					  "payment_type": payment_type,
					  "no_of_installment": no_of_installment,
					  "discount_given": discount_given,
					  "discount": discount,
					  "Institution_ID": Institution_ID,
					  "teacher_id": teacher_id,
					  "purchase_on":purchase_on,
					  "assign_course_fees":assign_course_fees,
					  "teacher_id": teacher_id
					}

				headers = {'Content-type':'application/json', 'Accept':'application/json'}
				post_response = requests.post(assign_course_fees_url, data=json.dumps(post_data), headers=headers)

		sendrReq = (course_id,studentList)
		thread_a = Compute(sendrReq,'StudentAssignCourse')
		thread_a.start()

		cursor.close()
		cursor.close()		

		return ({"atributes": {
	    			"status_desc": "Student Assign Course",
	    			"status": "success"
	    			},
	    			"responseList":"Saved Data Successfully"}), status.HTTP_200_OK

#----------------------Assign-Student-Course---------------------#	


#----------------------Assign-Group-Course---------------------#	
@name_space.route("/GroupAssignCourse")
class GroupAssignCourse(Resource):
	@api.expect(student_course_model)
	def post(self):
		details = request.get_json()

		connection = mysql_connection()
		gconnection = mysql_connection_logindb()

		cursor = connection.cursor()
		cur = gconnection.cursor()

		groupList = details.get('group_id',[])
		course_id = details['course_id']
		Institution_ID = details['Institution_ID']
		teacher_id = details['teacher_id']
		payment_mode = details['payment_mode']
		payment_type = details['payment_type']
		no_of_installment = details['no_of_installment']
		discount_given = details['discount_given']
		discount = details['discount']
		purchase_on = details['purchase_on']
		assign_course_fees = details['assign_course_fees']

		for gid in groupList:
				group_student_get_query = ("""SELECT gsm.`Group_ID`,gsm.`Student_Id`
				FROM `group_student_mapping` gsm
				WHERE gsm.`Group_ID` = %s """)

				getData = (gid)		
			
				cur.execute(group_student_get_query,getData)	

				student_mapping_data = cur.fetchall()

				for data in student_mapping_data:
					student_id = data['Student_Id']
					group_ID = data['Group_ID']

					insert_query = ("""INSERT INTO `student_course_master`(`student_id`,`course_id`,`Institution_ID`,`teacher_id`) VALUES(%s,%s,%s,%s)""")
					data = (student_id,course_id,Institution_ID,teacher_id)
					cursor.execute(insert_query,data)

					if assign_course_fees == "y":

						assign_course_fees_url = BASE_URL + 'myelsa_course/MyelsaCourse/AssignCourseFees'

						post_data = {
							  "student_id": student_id,
							  "course_id": course_id,
							  "payment_mode": payment_mode,
							  "payment_type": payment_type,
							  "no_of_installment": no_of_installment,
							  "discount_given": discount_given,
							  "discount": discount,
							  "Institution_ID": Institution_ID,
							  "teacher_id": teacher_id,
							  "purchase_on":purchase_on,
							  "assign_course_fees":assign_course_fees,
							  "teacher_id":teacher_id
							}

						headers = {'Content-type':'application/json', 'Accept':'application/json'}
						post_response = requests.post(assign_course_fees_url, data=json.dumps(post_data), headers=headers)

					
				insert_query_batch_mapping = ("""INSERT INTO `course_batch_mapping`(`course_id`,`Institution_ID`,
					`institution_user_id`,`Group_ID`) VALUES(%s,%s,%s,%s)""")
				batch_data = (course_id,Institution_ID,teacher_id,group_ID)
				cursor.execute(insert_query_batch_mapping,batch_data)

				

		return ({"atributes": {
	    			"status_desc": "Group Assign Course",
	    			"status": "success"
	    			},
	    			"responseList":"Saved Data Successfully"}), status.HTTP_200_OK		
#----------------------Assign-Group-Course---------------------#

#----------------------Assign-Course---------------------#
@name_space.route("/AssignCourse")
class AssignCourse(Resource):
	@api.expect(student_course_model)
	def post(self):
		details = request.get_json()
		studentList = details.get('student_id',[])
		groupList = details.get('group_id',[])
		course_id = details['course_id']
		is_group = details.get('is_group')
		Institution_ID = details['Institution_ID']
		teacher_id = details['teacher_id']
		payment_mode = details['payment_mode']
		payment_type = details['payment_type']
		no_of_installment = details['no_of_installment']
		discount_given = details['discount_given']
		discount = details['discount']
		purchase_on = details['purchase_on']
		assign_course_fees = details['assign_course_fees']

		if is_group == "n":
			student_assign_request_url = BASE_URL + 'myelsa_course/MyelsaCourse/StudentAssignCourse'

			post_data = {
					  "student_id": studentList,
					  "group_id": groupList,
					  "course_id": course_id,
					  "Institution_ID": Institution_ID,
					  "teacher_id": teacher_id,
					  "payment_mode": payment_mode,
					  "payment_type": payment_type,
					  "no_of_installment": no_of_installment,
					  "discount_given": discount_given,
					  "discount": discount,
					  "purchase_on":purchase_on,
					  "assign_course_fees":assign_course_fees
				}

			
			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			post_response = requests.post(student_assign_request_url, data=json.dumps(post_data), headers=headers)


		else:
			group_assign_request_url = BASE_URL + 'myelsa_course/MyelsaCourse/GroupAssignCourse'

			post_data = {
					  "student_id": studentList,
					  "group_id": groupList,
					  "course_id": course_id,
					  "Institution_ID": Institution_ID,
					  "teacher_id": teacher_id,
					  "payment_mode": payment_mode,
					  "payment_type": payment_type,
					  "no_of_installment": no_of_installment,
					  "discount_given": discount_given,
					  "discount": discount,
					  "purchase_on":purchase_on,
					  "assign_course_fees":assign_course_fees
				}

			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			post_response = requests.post(group_assign_request_url, data=json.dumps(post_data), headers=headers)
		
		

		return ({"atributes": {
	    			"status_desc": "Assign Course",
	    			"status": "success"
	    			},
	    			"responseList":"Saved Data Successfully"}), status.HTTP_200_OK	 	 
#----------------------Assign-Course---------------------#

#----------------------Create-Course-Content---------------------#

@name_space.route("/CreateCourseContent")
class CreateCourseContent(Resource):
	@api.expect(course_content_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		details = request.get_json()

		content_filepath = details.get('content_filepath')
		topic_id = details.get('topic_id',0)
		content_name = details.get('content_name')
		content_filetype = details.get('content_filetype')
		teacher_id = details.get('teacher_id')

		course_id = details.get('course_id')

		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		cretae_content_url = BASE_URL + 'user_library/userLibraryController/uploadContentToMyLibrary'

		post_data = {
					  "teacher_id": teacher_id,
					  "content_name": content_name,
					  "content_filepath": content_filepath,
					  "content_filetype": content_filetype,
					  "topic_id": topic_id
					}

		contentDetails = requests.post(cretae_content_url, data=json.dumps(post_data), headers=headers)

		
		my_json_string = contentDetails.json()

		s1 = json.dumps(my_json_string['responseList'])
		
		s2 = json.loads(s1)

		if s2['content_id'] :
			content_status = None
		
			insert_course_content_mapping = ("""INSERT INTO `course_content_mapping`(`course_id`,`content_id`,`status`) VALUES(%s,%s,%s)""")
			mapping_data = (course_id,s2['content_id'],content_status)
			cursor.execute(insert_course_content_mapping,mapping_data)

		details['content_id'] = s2['content_id']	

		connection.commit()
		cursor.close()

		return ({"atributes": {
	    			"status_desc": "Course Content",
	    			"status": "success"
	    			},
	    			"responseList":details}), status.HTTP_200_OK	
		

#----------------------Create-Course-Content---------------------#

#----------------------Course-Content-List---------------------#
@name_space.route("/getCourseContentList/<int:institution_id>/<int:course_id>")	
class getCourseList(Resource):
	def get(self,institution_id,course_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		course_content_get_query = ("""SELECT `course_id`,`content_id`
			FROM `course_content_mapping` WHERE `course_id` = %s """)

		getData = (course_id)
		cursor.execute(course_content_get_query,getData)

		couse_content_data = cursor.fetchall()

		for key,data in enumerate(couse_content_data):

			get_content_query = ("""SELECT `content_name`,`content_filepath`,`content_filename`,`content_filetype`,
				`topic_id`,`teacher_id`
				FROM `content_library` WHERE content_id = %s """)

			contentData = (data['content_id'])

			row_count_content = cursor.execute(get_content_query,contentData)

			if row_count_content>0:
				content_data = cursor.fetchone()

				couse_content_data[key]['content_name'] = content_data['content_name']
				couse_content_data[key]['content_filepath'] = content_data['content_filepath']
				couse_content_data[key]['content_filename'] = content_data['content_filename']
				couse_content_data[key]['content_filetype'] = content_data['content_filetype']
				couse_content_data[key]['topic_id'] = content_data['topic_id']

				if content_data['topic_id'] is None:
					couse_content_data[key]['topic_name'] = ""
				else:
					get_topic_query = ("""SELECT `topic_id`,`topic_name`
					FROM `topic` WHERE `topic_id` = %s """)

					topicData = (content_data['topic_id'])

					row_count_topic = cursor.execute(get_topic_query,topicData)

					if row_count_topic>0:
						topic_data = cursor.fetchone()

						couse_content_data[key]['topic_name'] = topic_data['topic_name']
						
					else:
						couse_content_data[key]['topic_name'] = ""
			else:
				couse_content_data[key]['content_name'] = ""
				couse_content_data[key]['content_filepath'] = ""
				couse_content_data[key]['content_filename'] = ""
				couse_content_data[key]['content_filetype'] = ""
				couse_content_data[key]['topic_name'] = ""
			
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Course_content_details",
		    		"status": "success"
		    	},
		    	"responseList":couse_content_data}), status.HTTP_200_OK

#----------------------Course-Content-List---------------------#

#----------------------Delete-Course-Content---------------------#

@name_space.route("/deleteCourseContent/<int:course_id>/<int:content_id>")
class deleteCourseContent(Resource):
	def delete(self, course_id,content_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		course_content_delete_query = ("""DELETE FROM `course_content_mapping` WHERE `course_id` = %s and `content_id` = %s""")
		delData = (course_id,content_id)
		
		cursor.execute(course_content_delete_query,delData)

		update_query = ("""UPDATE `content_library` SET `topic_id` = 0 ,`subtopic_id` = 0
				WHERE `content_id` = %s """)
		update_data = (content_id)
		cursor.execute(update_query,update_data)
		
		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Delete Course Content",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Course-Content---------------------#

#----------------------Delete-Content---------------------#

@name_space.route("/deleteContent/<int:content_id>")
class deleteContent(Resource):
	def delete(self, content_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_content_mapping_query = ("""SELECT `course_id`,`content_id`
			FROM `course_content_mapping` WHERE `content_id` = %s """)

		contentMappingData = (content_id)
		row_count_content_mapping = cursor.execute(get_content_mapping_query,contentMappingData)

		if row_count_content_mapping>0:
			connection.commit()
			cursor.close()

			return ({"attributes": {"status_desc": "Delete Course Content",
						"status": "error"},
				"responseList": 'Deleted is not Successful'}), status.HTTP_200_OK			
				
		else:
			content_delete_query = ("""DELETE FROM `content_library` WHERE `content_id` = %s """)
			delData = (content_id)		
			cursor.execute(content_delete_query,delData)

			connection.commit()
			cursor.close()

			return ({"attributes": {"status_desc": "Delete Content",
						"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK		
		

#----------------------Delete-Course-Content---------------------#

#----------------------Update-Course-Content---------------------#


@name_space.route("/updateCourseContent/<int:content_id>/<int:course_id>/<int:institution_id>")
class updateCourseContent(Resource):
	@api.expect(course_update_content_model)
	def put(self,content_id,course_id,institution_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		details = request.get_json()

		
		topic_id = details.get('topic_id',0)

		if details and "content_filepath" in details:
			filepath = details.get('content_filepath')
			if filepath:
				split_filepath = filepath.split('/')
				content_filepath = "/".join(split_filepath[:-1]) + '/'
				content_filename = filepath.split('/')[-1]
			else:
				content_filepath = None
				content_filename = None

			content_update_query = ("""UPDATE `content_library` SET `content_filepath` = %s,`content_filename`=%s
				WHERE `content_id` = %s """)
			update_data = (content_filepath,content_filename,content_id)
			cursor.execute(content_update_query,update_data)

		if details and "content_name" in details:
			content_name = details.get('content_name')			

			content_update_query = ("""UPDATE `content_library` SET `content_name` = %s
				WHERE `content_id` = %s """)
			update_data = (content_name,content_id)
			cursor.execute(content_update_query,update_data)	

		if details and "content_filetype" in details:
			content_filetype = details.get('content_filetype')			

			content_update_query = ("""UPDATE `content_library` SET `content_filetype` = %s
				WHERE `content_id` = %s """)
			update_data = (content_filetype,content_id)
			cursor.execute(content_update_query,update_data)

		if details and "teacher_id" in details:
			teacher_id = details.get('teacher_id')			

			content_update_query = ("""UPDATE `content_library` SET `teacher_id` = %s
				WHERE `content_id` = %s """)
			update_data = (teacher_id,content_id)
			cursor.execute(content_update_query,update_data)

		if details and "tpic_id" in details:
			teacher_id = details.get('teacher_id')			

			content_update_query = ("""UPDATE `content_library` SET `tpic_id` = %s
				WHERE `content_id` = %s """)
			update_data = (teacher_id,content_id)
			cursor.execute(content_update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Content Upload Details",
								"status": "success"
									},
				"responseList":details}), status.HTTP_200_OK

#----------------------Update-Course-Content---------------------#

def later_date(current_date):
  my_string = str(current_date)
  my_date = datetime.strptime(my_string,"%Y-%m-%d").date()
  first_weekday, days_in_month = calendar.monthrange(my_date.year, my_date.month)
  new_date = my_date + timedelta(days=days_in_month)
  return new_date

def one_year_later_date(current_date,x):
  my_string = str(current_date)
  startDate = datetime.strptime(my_string,"%Y-%m-%d").date()
  endDate = date(startDate.year + 1, startDate.month, startDate.day)
  endDate = startDate.replace(startDate.year + x)
  return endDate

    #----------------------Course-Student-list---------------------#
@name_space.route("/getInstitutionCourseAssignList/<string:key>/<int:Institution_ID>/<int:teacher_id>/<int:course_id>")	
class getOnlineTestAssignList(Resource):
	def get(self, key,Institution_ID,teacher_id,course_id):
		sconnection = mysql_connection()
		gconnection = mysql_connection_logindb()

		cursor = sconnection.cursor()
		cur = gconnection.cursor()

		if key == "s":
			course_assign_get_query = ("""SELECT `Institution_ID`,`student_id`,`course_id`,`teacher_id`,
				`coursefee_id`
			FROM `student_course_master` WHERE `Institution_ID` = %s and `teacher_id` = %s and `course_id` = %s""")

			getData = (Institution_ID,teacher_id,course_id)

			cursor.execute(course_assign_get_query,getData)

			course_assign_data = cursor.fetchall()

			for key,data in enumerate(course_assign_data):
				get_student_query = ("""SELECT `STUDENT_NAME`,`Image_URL`
				FROM `student_dtls` WHERE `INSTITUTION_USER_ID_STUDENT` = %s and INSTITUTION_ID =%s""")

				studentData = (data['student_id'],Institution_ID)

				row_count_student = cur.execute(get_student_query,studentData)

				if row_count_student>0:
					student_data = cur.fetchone()

					course_assign_data[key]['student_name'] = student_data['STUDENT_NAME']
					course_assign_data[key]['image_url'] = student_data['Image_URL']
				else:
					course_assign_data[key]['student_name'] = ""
					course_assign_data[key]['image_url'] = ""

				get_student_fees_query = ("""SELECT `payment_mode`,`payment_type`,`no_of_installment`,`total_amount`,
					`discount_given`,`discount_percentage`,`discount`,`actual_amount`,`purchased_on`,`remarks`
				FROM `student_coursefee_mapping` WHERE `course_id` = %s and student_id =%s""")

				studentFessData = (course_id,data['student_id'])

				row_count_student_fees = cursor.execute(get_student_fees_query,studentFessData)

				if row_count_student_fees>0:
					student_fees_data = cursor.fetchone()

					course_assign_data[key]['payment_mode'] = student_fees_data['payment_mode']
					course_assign_data[key]['payment_type'] = student_fees_data['payment_type']
					course_assign_data[key]['no_of_installment'] = student_fees_data['no_of_installment']
					course_assign_data[key]['total_amount'] = student_fees_data['total_amount']
					course_assign_data[key]['discount_given'] = student_fees_data['discount_given']
					course_assign_data[key]['discount_percentage'] = student_fees_data['discount_percentage']
					course_assign_data[key]['actual_amount'] = student_fees_data['actual_amount']
					course_assign_data[key]['purchased_on'] = str(student_fees_data['purchased_on'])
					course_assign_data[key]['remarks'] = student_fees_data['remarks']
				else:
					course_assign_data[key]['payment_mode'] = ""
					course_assign_data[key]['payment_type'] = ""
					course_assign_data[key]['no_of_installment'] = ""
					course_assign_data[key]['total_amount'] = ""
					course_assign_data[key]['discount_given'] = ""
					course_assign_data[key]['discount_percentage'] = ""
					course_assign_data[key]['actual_amount'] = ""
					course_assign_data[key]['purchased_on'] = ""
					course_assign_data[key]['remarks'] = ""
			

		if key == "g":

			course_assign_get_query = ("""SELECT `course_id`,`Institution_ID`,`institution_user_id`,`Group_ID`
			FROM `course_batch_mapping` WHERE `Institution_ID` = %s and `institution_user_id` = %s and `course_id` = %s""")


			getData = (Institution_ID,teacher_id,course_id)

			cursor.execute(course_assign_get_query,getData)

			course_assign_data = cursor.fetchall()

			for key,data in enumerate(course_assign_data):				

				get_student_query = ("""SELECT `Group_Description`
				FROM `group_master` WHERE `Group_ID` = %s and Institution_ID =%s""")

				studentData = (data['Group_ID'],Institution_ID)

				row_count_student = cur.execute(get_student_query,studentData)

				if row_count_student>0:
					student_data = cur.fetchone()

					course_assign_data[key]['Group_Description'] = student_data['Group_Description']					
				else:
					course_assign_data[key]['Group_Description'] = ""

				group_student_get_query = ("""SELECT gsm.`Group_ID`,gsm.`Student_Id`
				FROM `group_student_mapping` gsm
				WHERE gsm.`Group_ID` = %s """)

				getData = (data['Group_ID'])		
			
				cur.execute(group_student_get_query,getData)	

				student_mapping_data = cur.fetchall()

				course_assign_data[key]['student_info'] = student_mapping_data

				for skey,smdata in enumerate(student_mapping_data):
					get_student_query = ("""SELECT `STUDENT_NAME`,`Image_URL`
						FROM `student_dtls` WHERE `INSTITUTION_USER_ID_STUDENT` = %s and INSTITUTION_ID =%s""")

					studentData = (smdata['Student_Id'],Institution_ID)

					row_count_student = cur.execute(get_student_query,studentData)

					if row_count_student>0:
						student_data = cur.fetchone()

						course_assign_data[key]['student_info'][skey]['student_name'] = student_data['STUDENT_NAME']
						course_assign_data[key]['student_info'][skey]['image_url'] = student_data['Image_URL']
					else:
						course_assign_data[key]['student_info'][skey]['student_name'] = ""
						course_assign_data[key]['student_info'][skey]['image_url'] = ""


					get_student_fees_query = ("""SELECT `payment_mode`,`payment_type`,`no_of_installment`,`total_amount`,
					`discount_given`,`discount_percentage`,`discount`,`actual_amount`,`purchased_on`,`remarks`
						FROM `student_coursefee_mapping` WHERE `course_id` = %s and student_id =%s""")

					studentFessData = (course_id,smdata['Student_Id'])

					row_count_student_fees = cursor.execute(get_student_fees_query,studentFessData)

					if row_count_student_fees>0:
						student_fees_data = cursor.fetchone()

						course_assign_data[key]['student_info'][skey]['payment_mode'] = student_fees_data['payment_mode']
						course_assign_data[key]['student_info'][skey]['payment_type'] = student_fees_data['payment_type']
						course_assign_data[key]['student_info'][skey]['no_of_installment'] = student_fees_data['no_of_installment']
						course_assign_data[key]['student_info'][skey]['total_amount'] = student_fees_data['total_amount']
						course_assign_data[key]['student_info'][skey]['discount_given'] = student_fees_data['discount_given']
						course_assign_data[key]['student_info'][skey]['discount_percentage'] = student_fees_data['discount_percentage']
						course_assign_data[key]['student_info'][skey]['actual_amount'] = student_fees_data['actual_amount']
						course_assign_data[key]['student_info'][skey]['purchased_on'] = str(student_fees_data['purchased_on'])
						course_assign_data[key]['student_info'][skey]['remarks'] = student_fees_data['remarks']
					else:
						course_assign_data[key]['student_info'][skey]['payment_mode'] = ""
						course_assign_data[key]['student_info'][skey]['payment_type'] = ""
						course_assign_data[key]['student_info'][skey]['no_of_installment'] = ""
						course_assign_data[key]['student_info'][skey]['total_amount'] = ""
						course_assign_data[key]['student_info'][skey]['discount_given'] = ""
						course_assign_data[key]['student_info'][skey]['discount_percentage'] = ""
						course_assign_data[key]['student_info'][skey]['actual_amount'] = ""
						course_assign_data[key]['student_info'][skey]['purchased_on'] = ""
						course_assign_data[key]['student_info'][skey]['remarks'] = ""


		return ({"attributes": {
		    	"status_desc": "Assign List",
		    	"status": "success"
		    	},
		    	"responseList":course_assign_data}), status.HTTP_200_OK

#----------------------Course-Student-list---------------------#

#----------------------Student-Parent-List--------------------#

@name_space.route("/getStudentParentList/<int:student_id>/<int:institution_id>")	
class getStudentParentList(Resource):
	def get(self,student_id,institution_id):
		gconnection = mysql_connection_logindb()
		cur = gconnection.cursor()

		get_query = ("""SELECT `INSTITUTION_ID`,`INSTITUTION_USER_ID_GUARDIAN`,`INSTITUTION_USER_ID_STUDENT`
			FROM `guardian_dtls` WHERE  `INSTITUTION_USER_ID_STUDENT` = %s """)
		
		getData = (student_id)
		cur.execute(get_query,getData)
		student_parent_data = cur.fetchall()

		for key,data in enumerate(student_parent_data):

			get_parent_query = ("""SELECT `CITY`,`DATE_OF_BIRTH`,`EMAIL_ID`,`FIRST_NAME`,`GENDER`,`IMAGE_URL`,
						`INSTITUTION_USER_NAME`,`INSTITUTION_USER_PASSWORD`,`RESET`,`LAST_NAME`,`MIDDLE_NAME`,
						`PINCODE`,`PRIMARY_CONTACT_NUMBER`,`SECONDARY_CONTACT_NUMBER`,`STATE`,`STREET_ADDRESS`,
						`USER_TAX_ID`,`USER_UNIQUE_ID`,`address`	
						FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s """)

			parentData = (data['INSTITUTION_USER_ID_GUARDIAN'])

			row_count_parent = cur.execute(get_parent_query,parentData)

			if row_count_parent>0:
				parent_data = cur.fetchone()

				#student_parent_data[key]['CITY'] = parent_data['CITY']
				#student_parent_data[key]['DATE_OF_BIRTH'] = str(parent_data['DATE_OF_BIRTH'])
				#student_parent_data[key]['EMAIL_ID'] = parent_data['EMAIL_ID']
				student_parent_data[key]['FIRST_NAME'] = parent_data['FIRST_NAME']
				#student_parent_data[key]['GENDER'] = parent_data['GENDER']
				#student_parent_data[key]['IMAGE_URL'] = parent_data['IMAGE_URL']
				#student_parent_data[key]['INSTITUTION_USER_NAME'] = parent_data['INSTITUTION_USER_NAME']
				#student_parent_data[key]['INSTITUTION_USER_PASSWORD'] = parent_data['INSTITUTION_USER_PASSWORD']
				#student_parent_data[key]['RESET'] = parent_data['RESET']
				student_parent_data[key]['LAST_NAME'] = parent_data['LAST_NAME']
				student_parent_data[key]['MIDDLE_NAME'] = parent_data['MIDDLE_NAME']
				#student_parent_data[key]['PINCODE'] = parent_data['PINCODE']
				student_parent_data[key]['PRIMARY_CONTACT_NUMBER'] = parent_data['PRIMARY_CONTACT_NUMBER']
				#student_parent_data[key]['SECONDARY_CONTACT_NUMBER'] = parent_data['SECONDARY_CONTACT_NUMBER']
				#student_parent_data[key]['STATE'] = parent_data['STATE']
				#student_parent_data[key]['STREET_ADDRESS'] = parent_data['STREET_ADDRESS']
				#student_parent_data[key]['USER_TAX_ID'] = parent_data['USER_TAX_ID']
				#student_parent_data[key]['USER_UNIQUE_ID'] = parent_data['USER_UNIQUE_ID']
				#student_parent_data[key]['address'] = parent_data['address']
			else:
				#student_parent_data[key]['CITY'] = ""
				#student_parent_data[key]['DATE_OF_BIRTH'] = ""
				#student_parent_data[key]['EMAIL_ID'] = ""
				student_parent_data[key]['FIRST_NAME'] = ""
				#student_parent_data[key]['GENDER'] = ""
				#student_parent_data[key]['IMAGE_URL'] = ""
				#student_parent_data[key]['INSTITUTION_USER_NAME'] = ""
				#student_parent_data[key]['INSTITUTION_USER_PASSWORD'] = ""
				#student_parent_data[key]['RESET'] = ""
				student_parent_data[key]['LAST_NAME'] = ""
				student_parent_data[key]['MIDDLE_NAME'] = ""
				#student_parent_data[key]['PINCODE'] = ""
				student_parent_data[key]['PRIMARY_CONTACT_NUMBER']  = ""
				#student_parent_data[key]['SECONDARY_CONTACT_NUMBER'] = ""
				#student_parent_data[key]['STATE'] = ""
				#student_parent_data[key]['STREET_ADDRESS'] = ""
				#student_parent_data[key]['USER_TAX_ID'] = ""
				#student_parent_data[key]['USER_UNIQUE_ID']= ""
				#student_parent_data[key]['address'] = ""

		return ({"attributes": {
		    	"status_desc": "Student Parent List",
		    	"status": "success"
		    	},
		    	"responseList":student_parent_data}), status.HTTP_200_OK

#----------------------Student-Parent_List--------------------#

#----------------------Parent-Student-List--------------------#

@name_space.route("/getParentStudentList/<int:parent_id>/<int:institution_id>")	
class getParentStudentList(Resource):
	def get(self,parent_id,institution_id):
		gconnection = mysql_connection_logindb()
		cur = gconnection.cursor()

		get_query = ("""SELECT `INSTITUTION_ID`,`INSTITUTION_USER_ID_GUARDIAN`,`INSTITUTION_USER_ID_STUDENT`
			FROM `guardian_dtls` WHERE  `INSTITUTION_USER_ID_GUARDIAN` = %s """)
		
		getData = (parent_id)
		cur.execute(get_query,getData)
		parent_student_data = cur.fetchall()

		for key,data in enumerate(parent_student_data):

			get_student_query = ("""SELECT `STUDENT_NAME`,`Image_URL`
						FROM `student_dtls` WHERE `INSTITUTION_USER_ID_STUDENT` = %s """)

			studentData = (data['INSTITUTION_USER_ID_STUDENT'])

			row_count_student = cur.execute(get_student_query,studentData)

			if row_count_student>0:
				student_data = cur.fetchone()

				parent_student_data[key]['student_name'] = student_data['STUDENT_NAME']
				parent_student_data[key]['image_url'] = student_data['Image_URL']
			else:
				parent_student_data[key]['student_name'] = ""
				parent_student_data[key]['image_url'] = ""
			
		return ({"attributes": {
		    	"status_desc": "Parent Student List",
		    	"status": "success"
		    	},
		    	"responseList":parent_student_data}), status.HTTP_200_OK

#----------------------Parent-Student-List--------------------#


#----------------------Parent-Student-List--------------------#

@name_space.route("/getFolderCourseList/<int:folder_id>/<int:Institution_ID>")	
class getFolderCourseList(Resource):
	def get(self,folder_id,Institution_ID):
		sconnection = mysql_connection()

		cursor = sconnection.cursor()

		get_query = ("""SELECT `course_id`,`Institution_ID`,`folder_id`
			FROM `course_folder_mapping` WHERE  `folder_id` = %s and Institution_ID = %s""")
		
		getData = (folder_id,Institution_ID)
		cursor.execute(get_query,getData)
		folder_course_data = cursor.fetchall()

		for key,data in enumerate(folder_course_data):

			course_get_query = ("""SELECT `course_id`,`institution_id`,`course_title`,`course_description`,`course_image`,
				`course_filetype`,`teacher_id`,`subject_id`,`topic_id`
				FROM `instituition_course_master` WHERE `course_id` = %s """)

			getData = (data['course_id'])

			row_count_course = cursor.execute(course_get_query,getData)

			if row_count_course>0:
				couse_data = cursor.fetchone()

				folder_course_data[key]['course_title'] = couse_data['course_title']
				folder_course_data[key]['course_description'] = couse_data['course_description']
				folder_course_data[key]['course_image'] = couse_data['course_image']
				folder_course_data[key]['course_filetype'] = couse_data['course_filetype']
				folder_course_data[key]['teacher_id'] = couse_data['teacher_id']
				folder_course_data[key]['subject_id'] = couse_data['subject_id']
				folder_course_data[key]['topic_id'] = couse_data['topic_id']


				get_topic_query = ("""SELECT `topic_id`,`topic_name`
				FROM `topic` WHERE `topic_id` = %s """)

				topicData = (couse_data['topic_id'])

				row_count_topic = cursor.execute(get_topic_query,topicData)

				if row_count_topic>0:
					topic_data = cursor.fetchone()

					folder_course_data[key]['topic_name'] = topic_data['topic_name']
					
				else:
					folder_course_data[key]['topic_name'] = ""

				get_subject_query = ("""SELECT `subject_id`,`subject_name`
				FROM `subject` WHERE `subject_id` = %s """)

				subjectData = (couse_data['subject_id'])

				row_subject_topic = cursor.execute(get_subject_query,subjectData)

				if row_subject_topic>0:
					subject_data = cursor.fetchone()

					folder_course_data[key]['subject_name'] = subject_data['subject_name']
				else:
					folder_course_data[key]['subject_name'] = ""

				no_of_student_assign_query = ("""SELECT count(Distinct(student_id)) as no_of_student_assign FROM `student_course_master` where course_id = %s """)	
				student_assign_data = (data['course_id'])
				row_student_assign = cursor.execute(no_of_student_assign_query,student_assign_data)

				if row_student_assign>0:
					student_data = cursor.fetchone()

					folder_course_data[key]['no_of_student_assign'] = student_data['no_of_student_assign']
				
				else:
					folder_course_data[key]['no_of_student_assign'] = ""

				folder_course_data[key]['no_of_student_seen'] = 1

			else:
				folder_course_data[key]['course_title'] = ""
				folder_course_data[key]['course_description'] = ""
				folder_course_data[key]['course_image'] = ""
				folder_course_data[key]['course_filetype'] = ""
				folder_course_data[key]['teacher_id'] = ""
				folder_course_data[key]['subject_id'] = ""
				folder_course_data[key]['topic_id'] = ""
				folder_course_data[key]['topic_name'] = ""
				folder_course_data[key]['subject_name'] = ""
				folder_course_data[key]['no_of_student_assign'] = ""
				folder_course_data[key]['no_of_student_seen'] = ""
			
			
		return ({"attributes": {
		    	"status_desc": "Folder Course List",
		    	"status": "success"
		    	},
		    	"responseList":folder_course_data}), status.HTTP_200_OK

#----------------------Parent-Student-List--------------------#

#----------------------Delete-Folder-Course---------------------#

@name_space.route("/deleteFolderCourse/<int:course_id>/<int:folder_id>")
class deleteFolderCourse(Resource):
	def delete(self, course_id,folder_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		folder_course_delete_query = ("""DELETE FROM `course_folder_mapping` WHERE `course_id` = %s and `folder_id` = %s""")
		delData = (course_id,folder_id)
		
		cursor.execute(folder_course_delete_query,delData)

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Delete Folder Course",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Folder-Course---------------------#

#----------------------Create-Folder-Course---------------------#

@name_space.route("/CreateFolderCourse")
class CreateFolderCourse(Resource):
	@api.expect(folder_course_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		details = request.get_json()

		institution_id = details['institution_id']
		course_title = details['course_title']
		course_description = details['course_description']
		course_image = details['course_image']
		course_filetype = details['course_filetype']
		teacher_id = details['teacher_id']
		subject_id = details['subject_id']
		topic_id = details['topic_id']
		folder_id = details['folder_id']
		folder_name = details['folder_name']


		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		cretae_content_url = BASE_URL + 'myelsa_course/MyelsaCourse/CreateCourse'

		post_data = {
					  "institution_id": institution_id,
					  "course_title": course_title,
					  "course_description": course_description,
					  "course_image": course_image,
					  "course_filetype": course_filetype,
					  "teacher_id": teacher_id,
					  "subject_id": subject_id,
					  "topic_id": topic_id,
					}

		courseDetails = requests.post(cretae_content_url, data=json.dumps(post_data), headers=headers)

		
		my_json_string = courseDetails.json()

		s1 = json.dumps(my_json_string['responseList']['CourseDtls'])
		
		s2 = json.loads(s1)

		if s2['course_id'] :
		
			insert_folder_course_mapping = ("""INSERT INTO `course_folder_mapping`(`teacher_id`,`course_id`,`Institution_ID`,`folder_id`,`folder_name`) VALUES(%s,%s,%s,%s,%s)""")
			mapping_data = (teacher_id,s2['course_id'],institution_id,folder_id,folder_name)
			cursor.execute(insert_folder_course_mapping,mapping_data)

		details['course_id'] = s2['course_id']	

		connection.commit()
		cursor.close()

		return ({"atributes": {
	    			"status_desc": "Folder Course",
	    			"status": "success"
	    			},
	    			"responseList":details}), status.HTTP_200_OK	
		

#----------------------Create-Folder-Course---------------------#

@name_space.route("/getCourseListByStudentId/<int:student_id>/<int:institution_id>")	
class getCourseListByStudentId(Resource):
	def get(self,student_id,institution_id):

		connection = mysql_connection()
		curlab = connection.cursor()
		
		curlab.execute("""SELECT distinct scm.`course_id`,`course_title`,`course_description`,`course_image`,
			`course_filetype`,icm.`teacher_id`,icm.`subject_id`,`subject_name`,icm.`topic_id`,
			`topic_name` FROM `student_course_master` scm INNER JOIN `instituition_course_master` icm 
			ON scm.`course_id` = icm.`course_id` INNER JOIN `subject` 
			on icm.`subject_id` = `subject`.`subject_id` INNER JOIN `topic` 
			on icm.`topic_id` = `topic`.`topic_id` WHERE `student_id` = %s""",(student_id))


		assignedCoursesDtls = curlab.fetchall()


		curlab.execute("""SELECT icm.`course_id`, `course_title`, `course_description`, `course_image`, `course_filetype`, `is_paid_course`,`total_fee`,`installment_available`,`installment_type`,`no_of_installments`,`teacher_id`, icm.`subject_id`,`subject_name`,icm.`topic_id`,
			`topic_name` FROM `instituition_course_master` icm
			INNER JOIN `subject` 
			on icm.`subject_id` = `subject`.`subject_id` INNER JOIN `topic` 
			on icm.`topic_id` = `topic`.`topic_id`
			INNER JOIN `course_fee_mapping` cfm ON icm.`course_id` = cfm.`course_id`
			WHERE icm.`institution_id` = %s and icm.`course_id` not 
			in (SELECT `course_id` FROM `student_course_master` 
			WHERE `student_id` = %s)""",(institution_id,student_id))

		institutionCourseDtls = curlab.fetchall()


		courseDtls = {"assignedCourses":assignedCoursesDtls,
						"CoursesAvailable":institutionCourseDtls}

		totalCourses = len(assignedCoursesDtls) + len(institutionCourseDtls)
		totalAssigned = len(assignedCoursesDtls)

		return ({"attributes": {"status_desc": "Student Course Details",
								"status": "success",
								"total_courses_available":totalCourses,
								"total_courses_assigned":totalAssigned},
				"responseList": courseDtls}), status.HTTP_200_OK

@name_space.route("/getCourseFeesByStudentId/<int:student_id>/<int:course_id>")	
class getCourseFeesByStudentId(Resource):
	def get(self,student_id,course_id):

		connection = mysql_connection()
		curlab = connection.cursor()
		
		curlab.execute("""SELECT `coursefee_id`,`payment_mode`,`payment_type`,`no_of_installment`,`total_amount`,
			`discount_given`,`discount_percentage`,`discount`,`actual_amount`,`purchased_on`,
			`remarks` FROM `student_coursefee_mapping` WHERE `course_id` = %s 
			AND`student_id` = %s order by `coursefee_id` desc limit 1""",(course_id,student_id))


		coursesFeesDtls = curlab.fetchone()

		if coursesFeesDtls:
			courseFeeId = coursesFeesDtls.get('coursefee_id')
			coursesFeesDtls['purchased_on'] = coursesFeesDtls.get('purchased_on').isoformat()
			curlab.execute("""SELECT `payment_id`,`payment_amount`,`payment_duedate` FROM 
				`student_coursefee_payment_details` WHERE `student_id` = %s and `coursefee_id` = %s 
				and `is_pending` = 'y'""",(student_id,courseFeeId))


			pendingFeesDtls = curlab.fetchall()

			for pid, pend in enumerate(pendingFeesDtls):
				pend['payment_duedate'] = pend.get('payment_duedate').isoformat()
			pendingFeesDtls = sorted(pendingFeesDtls, key = lambda i: i['payment_duedate']) 
			coursesFeesDtls['pendingFeeDtls'] = pendingFeesDtls
		else:
			coursesFeesDtls = {}


		return ({"attributes": {"status_desc": "Student Course Details",
								"status": "success"},
				"responseList": coursesFeesDtls}), status.HTTP_200_OK


#----------------------Course-List-By-StudentId-FolderId---------------------#

@name_space.route("/getCourseListByStudentIdFolderId/<int:student_id>/<int:institution_id>/<int:folder_id>")	
class getCourseListByStudentIdFolderId(Resource):
	def get(self,student_id,institution_id,folder_id):

		sconnection = mysql_connection()
		cursor = sconnection.cursor()

		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		url = BASE_URL + 'myelsa_course/MyelsaCourse/getCourseListByStudentId/{}/{}'.format(student_id,institution_id)

		courseDetails = requests.get(url, headers=headers)

		my_json_string = courseDetails.json()

		s1 = json.dumps(my_json_string['responseList'])
		
		s2 = json.loads(s1)

		assignedCourses = s2['assignedCourses']
		CoursesAvailable = s2['CoursesAvailable']

		assignedCoursesDtls = []
		institutionCourseDtls = []

		for key,data in enumerate(assignedCourses): 

			get_query = ("""SELECT `course_id`,`Institution_ID`,`folder_id`
				FROM `course_folder_mapping` WHERE  `folder_id` = %s  and course_id = %s""")
			
			getData = (folder_id,data['course_id'])
			count_course = cursor.execute(get_query,getData)

			if count_course > 0:
				assignedCoursesDtls.append(assignedCourses[key])

		for akey,adata in enumerate(CoursesAvailable): 

			get_query = ("""SELECT `course_id`,`Institution_ID`,`folder_id`
				FROM `course_folder_mapping` WHERE  `folder_id` = %s  and course_id = %s""")
			
			getData = (folder_id,adata['course_id'])
			count_course = cursor.execute(get_query,getData)

			if count_course > 0:
				institutionCourseDtls.append(CoursesAvailable[akey])
				

		courseDtls = {"assignedCourses":assignedCoursesDtls,
						"CoursesAvailable":institutionCourseDtls}



		totalCourses = len(assignedCoursesDtls) + len(institutionCourseDtls)
		totalAssigned = len(assignedCoursesDtls)


		return ({"attributes": {"status_desc": "Student Course Details",
								"status": "success",
								"total_courses_available":totalCourses,
								"total_courses_assigned":totalAssigned},
				"responseList": courseDtls}), status.HTTP_200_OK	


#----------------------Course-List-By-StudentId-FolderId---------------------#


@name_space.route("/createPaymentLinkByPaymentId/<int:payment_id>")	
class createPaymentLinkByPaymentId(Resource):
	def put(self,payment_id):

		connection = mysql_connection()
		curlab = connection.cursor()

		conn = mysql_connection_logindb()
		curlog = conn.cursor()
		
		linkDtls = {}

		URL = BASE_URL + "instamojo_payments/paymentController/askForFessByTeacherV2"

		headers = {'Content-type':'application/json', 'Accept':'application/json'}

		curlab.execute("""SELECT scpd.`student_id`,`payment_amount`,`payment_duedate`,
			scpd.`coursefee_id`,icm.`teacher_id`,icm.`Institution_ID`,sm.`course_id` ,`course_title`
			FROM `student_coursefee_payment_details` scpd
			INNER JOIN `student_coursefee_mapping` sm on 
			scpd.`coursefee_id` = sm.`coursefee_id`
			INNER JOIN `instituition_course_master` icm on sm.`course_id` = icm.`course_id`
			WHERE `payment_id` = %s""",(payment_id))

		paymentDtls = curlab.fetchone()
		print(paymentDtls)
		if paymentDtls:

			payload = {"amount":int(paymentDtls.get('payment_amount')),
						"purpose":"Course-"+str(paymentDtls.get('course_title')),
						"teacher_id":paymentDtls.get('teacher_id'),
						"institution_id":paymentDtls.get('Institution_ID'),
						"student_id":[paymentDtls.get('student_id')],
						"group_id":[],
						"is_group":0}
			print(payload)
			mojoResponse = requests.post(URL,data=json.dumps(payload), headers=headers).json()
			transId = mojoResponse.get('responseList').get('transaction_id')
			curlog.execute("""SELECT `phone`,`buyer_name`,`amount`,`purpose`,`longurl`as 'payment_link',ipr.`instamojo_request_id`
				FROM `instamojo_payment_request` ipr 
				INNER JOIN `instamojo_payment_student_mapping` ipsm 
				on ipr.`request_id` = ipsm.`request_id` WHERE `transaction_id` = %s 
				and `student_id` = %s""",(transId,paymentDtls.get('student_id')))

			linkDtls = curlog.fetchone()
			if linkDtls:
				updateTran = ("""UPDATE `student_coursefee_payment_details` SET `transaction_id` = %s 
					WHERE `payment_id` = %s""")
				updateData = (linkDtls.get('instamojo_request_id'),payment_id)
				curlab.execute(updateTran,updateData)
		connection.commit()
		curlab.close()
		conn.commit()
		curlog.close()
		return ({"attributes": {"status_desc": "Student Payment Link Details",
								"status": "success"},
				"responseList": linkDtls}), status.HTTP_200_OK


@name_space.route("/createPaymentDetails")	
class createPaymentDetails(Resource):
	@api.expect(create_payment_dtls_model)
	def post(self):

		connection = mysql_connection()
		curlab = connection.cursor()

		conn = mysql_connection_logindb()
		curlog = conn.cursor()

		details = request.get_json()

		student_id = details.get('student_id')
		course_id = details.get('course_id')
		payment_mode = details.get('payment_mode')
		payment_type = details.get('payment_type')
		no_of_installment = details.get('no_of_installment')
		discount_given = details.get('discount_given')
		discount = details.get('discount')
		institution_id = details.get('institution_id')
		teacher_id = details.get('teacher_id')
		total_amount = details.get('total_amount')
		curdate = datetime.now().strftime('%Y-%m-%d')

		courseFeeInsertQuery = ("""INSERT INTO `student_coursefee_mapping`(`purchase_type`,`student_id`, `course_id`, 
			`payment_mode`, `payment_type`, `no_of_installment`, `total_amount`, `actual_amount`,
			`purchased_on`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

		courseFeeData = ('course',student_id,course_id,payment_mode,payment_type,no_of_installment,
			total_amount,total_amount,curdate)


		curlab.execute(courseFeeInsertQuery,courseFeeData)

		courseFeeId = curlab.lastrowid

		studentPaymentDetailsInsert = ("""INSERT INTO `student_coursefee_payment_details`(`student_id`,
			`payment_amount`,`payment_duedate`,`is_pending`,
			`coursefee_id`) VALUES(%s,%s,%s,%s,%s)""")

		if no_of_installment > 1:

			installment_amount = float(total_amount)/no_of_installment

			for x in range(no_of_installment):
					payment_due_date = curdate
					print(payment_due_date)
					paymentDtlsData = (student_id,installment_amount,payment_due_date,'y',courseFeeId)

					curlab.execute(studentPaymentDetailsInsert,paymentDtlsData)
					curdate = later_date(curdate)
		else:

			paymentDtlsData = (student_id,total_amount,curdate,'y',courseFeeId)

			curlab.execute(studentPaymentDetailsInsert,paymentDtlsData)

		connection.commit()
		curlab.close()

		getURL = BASE_URL + "myelsa_course/MyelsaCourse/getCourseFeesByStudentId/{}/{}".format(student_id,course_id)

		headers = {'Content-type':'application/json', 'Accept':'application/json'}

		getResponse = requests.get(getURL, headers=headers).json()

		return getResponse


@name_space.route("/getCourseComboFeesByStudentId/<int:student_id>/<int:combo_id>")	
class getCourseComboFeesByStudentId(Resource):
	def get(self,student_id,combo_id):

		connection = mysql_connection()
		curlab = connection.cursor()
		
		curlab.execute("""SELECT `coursefee_id`,`payment_mode`,`payment_type`,`no_of_installment`,`total_amount`,
			`discount_given`,`discount_percentage`,`discount`,`actual_amount`,`purchased_on`,
			`remarks` FROM `student_coursefee_mapping` WHERE `combo_id` = %s 
			AND`student_id` = %s  order by `coursefee_id` desc limit 1""",(combo_id,student_id))


		coursesFeesDtls = curlab.fetchone()

		if coursesFeesDtls:
			courseFeeId = coursesFeesDtls.get('coursefee_id')
			coursesFeesDtls['purchased_on'] = coursesFeesDtls.get('purchased_on').isoformat()
			curlab.execute("""SELECT `payment_id`,`payment_amount`,`payment_duedate` FROM 
				`student_coursefee_payment_details` WHERE `student_id` = %s and `coursefee_id` = %s 
				and `is_pending` = 'y'""",(student_id,courseFeeId))


			pendingFeesDtls = curlab.fetchall()

			for pid, pend in enumerate(pendingFeesDtls):
				pend['payment_duedate'] = pend.get('payment_duedate').isoformat()
			pendingFeesDtls = sorted(pendingFeesDtls, key = lambda i: i['payment_duedate']) 
			coursesFeesDtls['pendingFeeDtls'] = pendingFeesDtls
			
		else:
			coursesFeesDtls = {}


		return ({"attributes": {"status_desc": "Student Course Combo Details",
								"status": "success"},
				"responseList": coursesFeesDtls}), status.HTTP_200_OK



@name_space.route("/createPaymentDetailsForComboCourses")	
class createPaymentDetailsForComboCourses(Resource):
	@api.expect(create_payment_course_combo)
	def post(self):

		connection = mysql_connection()
		curlab = connection.cursor()

		conn = mysql_connection_logindb()
		curlog = conn.cursor()

		details = request.get_json()

		student_id = details.get('student_id')
		combo_id = details.get('combo_id')
		course_id = details.get('course_id')
		payment_mode = details.get('payment_mode')
		payment_type = details.get('payment_type')
		no_of_installment = details.get('no_of_installment')
		discount_given = details.get('discount_given')
		discount = details.get('discount')
		institution_id = details.get('institution_id')
		teacher_id = details.get('teacher_id')
		total_amount = details.get('total_amount')
		curdate = datetime.now().strftime('%Y-%m-%d')

		courseFeeInsertQuery = ("""INSERT INTO `student_coursefee_mapping`(`purchase_type`,`student_id`,
			`combo_id`, `payment_mode`, `payment_type`, `no_of_installment`, `total_amount`, `actual_amount`,
			`purchased_on`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

		courseFeeData = ('combo',student_id,combo_id,payment_mode,payment_type,no_of_installment,
			total_amount,total_amount,curdate)


		curlab.execute(courseFeeInsertQuery,courseFeeData)

		courseFeeId = curlab.lastrowid

		studentPaymentDetailsInsert = ("""INSERT INTO `student_coursefee_payment_details`(`student_id`,
			`payment_amount`,`payment_duedate`,`is_pending`,
			`coursefee_id`) VALUES(%s,%s,%s,%s,%s)""")

		if no_of_installment > 1:

			installment_amount = float(total_amount)/no_of_installment

			for x in range(no_of_installment):
					payment_due_date = curdate
					print(payment_due_date)
					paymentDtlsData = (student_id,installment_amount,payment_due_date,'y',courseFeeId)

					curlab.execute(studentPaymentDetailsInsert,paymentDtlsData)
					curdate = later_date(curdate)
		else:

			paymentDtlsData = (student_id,total_amount,curdate,'y',courseFeeId)

			curlab.execute(studentPaymentDetailsInsert,paymentDtlsData)
		comboMappingInsert = ("""INSERT INTO `student_combo_mapping`(`student_id`, `coursefee_id`, 
			`course_id`) VALUES (%s,%s,%s)""")
		for cid in course_id:
			comboData = (student_id,courseFeeId,cid)
			curlab.execute(comboMappingInsert,comboData)

		connection.commit()
		curlab.close()

		getURL = BASE_URL + "myelsa_course/MyelsaCourse/getCourseComboFeesByStudentId/{}/{}".format(student_id,combo_id)

		headers = {'Content-type':'application/json', 'Accept':'application/json'}

		getResponse = requests.get(getURL, headers=headers).json()

		return getResponse

@name_space.route("/createPaymentLinkByPaymentIdForComboCourse/<int:payment_id>")	
class createPaymentLinkByPaymentIdForComboCourse(Resource):
	def put(self,payment_id):

		connection = mysql_connection()
		curlab = connection.cursor()

		conn = mysql_connection_logindb()
		curlog = conn.cursor()
		
		linkDtls = {}

		URL = BASE_URL + "instamojo_payments/paymentController/askForFessByTeacherV2"

		headers = {'Content-type':'application/json', 'Accept':'application/json'}

		curlab.execute("""SELECT scpd.`student_id`,`payment_amount`,`payment_duedate`, 
			scpd.`coursefee_id`,icm.`teacher_id`,icm.`Institution_ID`,sm.`combo_id` ,`course_title` 
			FROM `student_coursefee_payment_details` scpd INNER JOIN `student_coursefee_mapping` sm 
			on scpd.`coursefee_id` = sm.`coursefee_id` inner JOIN `student_combo_mapping` scm 
			on sm.`coursefee_id` = scm.`coursefee_id` INNER JOIN `instituition_course_master` icm 
			on scm.`course_id` = icm.`course_id` WHERE `payment_id` = %s""",(payment_id))

		paymentDtls = curlab.fetchone()
		print(paymentDtls)
		if paymentDtls:

			payload = {"amount":int(paymentDtls.get('payment_amount')),
						"purpose":"ComboCourse-"+str(paymentDtls.get('combo_id'))+"-"+str(payment_id),
						"teacher_id":paymentDtls.get('teacher_id'),
						"institution_id":paymentDtls.get('Institution_ID'),
						"student_id":[paymentDtls.get('student_id')],
						"group_id":[],
						"is_group":0}
			print(payload)
			mojoResponse = requests.post(URL,data=json.dumps(payload), headers=headers).json()
			print(mojoResponse)
			transId = mojoResponse.get('responseList').get('transaction_id')
			curlog.execute("""SELECT `phone`,`buyer_name`,`amount`,`purpose`,`longurl`as 'payment_link',ipr.`instamojo_request_id`
				FROM `instamojo_payment_request` ipr 
				INNER JOIN `instamojo_payment_student_mapping` ipsm 
				on ipr.`request_id` = ipsm.`request_id` WHERE `transaction_id` = %s 
				and `student_id` = %s""",(transId,paymentDtls.get('student_id')))

			linkDtls = curlog.fetchone()
			if linkDtls:
				updateTran = ("""UPDATE `student_coursefee_payment_details` SET `transaction_id` = %s 
					WHERE `payment_id` = %s""")
				updateData = (linkDtls.get('instamojo_request_id'),payment_id)
				curlab.execute(updateTran,updateData)
		connection.commit()
		curlab.close()
		conn.commit()
		curlog.close()
		return ({"attributes": {"status_desc": "Student Payment Link Details",
								"status": "success"},
				"responseList": linkDtls}), status.HTTP_200_OK