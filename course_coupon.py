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
import random
import string
import time
from threading import Thread

app = Flask(__name__)
cors = CORS(app)


'''def mysql_connection():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='creamson_logindb',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

def nextmysql_connection():
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

def nextmysql_connection():
	connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
	                             user='admin',
	                             password='cbdHoRPQPRfTdC0uSPLt',
	                             db='creamson_user_library',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection


course_coupon_dtls = Blueprint('course_coupon_dtls_api', __name__)
api = Api(course_coupon_dtls,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('CourseCouponDetails',description='Course Coupon Details')

coursecoupon = api.model('coursecoupon', {
	"dashboard_id": fields.Integer(),
    "dashboard_desc": fields.String(),
    "item_id": fields.Integer(),
    "institution_id":fields.Integer(),
    "teacher_id": fields.Integer(),
    "student_id": fields.Integer(),
    "amount": fields.Integer(),
    "purpose": fields.String(),
    "remarks": fields.String(),
    "last_update_id": fields.Integer()
    })

update_coursecoupon = api.model('update_coursecoupon', {
    "dashboard_desc": fields.String(),
    "amount": fields.Integer(),
    "purpose": fields.String(),
    "remarks": fields.String()
})

validcoursecoupon = api.model('validcoursecoupon', {
    "dashboard_id": fields.Integer(),
    "item_id": fields.Integer(),
    "student_id": fields.Integer(),
    "coupon": fields.String(),
    "discount_given":fields.String(),
	"discount":fields.Float()
})

update_courseoffer = api.model('update_courseoffer', {
	"course_title": fields.String(),
    "course_description": fields.String(),
    "course_amount": fields.Float(),
    "discount_given": fields.String(),
    "discount_percentage":fields.Float(),
	"discount_value":fields.Float(),
	"actual_amount":fields.Float()
})

#-----------------------add-Course-Coupon------------------------------------#
@name_space.route("/addCourseCoupon")
class addCourseCoupon(Resource):
	@api.expect(coursecoupon)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		
		dashboard_id = details['dashboard_id']
		dashboard_desc = details['dashboard_desc']
		item_id = details['item_id']
		institution_id = details['institution_id']
		teacher_id = details['teacher_id']
		student_id = details['student_id']
		amount = details['amount']
		purpose = details['purpose']
		remarks = details['remarks']
		last_update_id = details['last_update_id']
		
		def get_random_alphaNumeric_string(stringLength=8):
		    lettersAndDigits = string.ascii_letters + string.digits
		    return ''.join((random.choice(lettersAndDigits) for i in range(stringLength)))
		
		coupon = get_random_alphaNumeric_string()
		# print(coupon)
		course_couponquery = ("""INSERT INTO `course_coupon_dtls`(`dashboard_id`, `dashboard_desc`,
			`item_id`, `institution_id`, `teacher_id`, `student_id`, `coupon`, `is_used`,
			 `amount`, `purpose`, `remarks`, `last_update_id`) VALUES 
				(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
		insert_data = (dashboard_id,dashboard_desc,item_id,institution_id,teacher_id,
			student_id,coupon,"n",amount,purpose,remarks,last_update_id)
		smsbackdata = cursor.execute(course_couponquery,insert_data)

		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Added Course Coupon",
	                                "status": "success"
	                                }
	                 }), status.HTTP_200_OK

#-----------------------add-Course-Coupon------------------------------------#

#--------------------get-Course-Coupon-by-teacher-id-------------------------#
@name_space.route("/CouseCouponDtlsByTeacherId/<int:teacher_id>")
class CouseCouponDtlsByTeacherId(Resource):
	def get(self,teacher_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		cursor.execute("""SELECT `course_coupon_id`,`dashboard_id`,`dashboard_desc`,
        	`item_id`,`institution_id`,`teacher_id`,`student_id`,`coupon`,`is_used`,
        	`amount`,`purpose`,`remarks`,`last_update_id`,`last_update_ts` 
        	FROM `course_coupon_dtls` WHERE `teacher_id`=%s""",(teacher_id))
		course_coupondtls = cursor.fetchall()

		for i in range(len(course_coupondtls)):
			course_coupondtls[i]['last_update_ts'] = course_coupondtls[i]['last_update_ts'].isoformat()

		cursor.close()
		return ({"attributes": {"status_desc": "Course Coupon Details",
                                "status": "success"
                                },
                 "responseList": course_coupondtls}), status.HTTP_200_OK
#--------------------get-Course-Coupon-by-teacher-id-------------------------#

#--------------------get-Course-Coupon-by-student-id-------------------------#
@name_space.route("/CouseCouponDtlsByStudentId/<int:student_id>")
class CouseCouponDtlsByStudentId(Resource):
	def get(self,student_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		cursor.execute("""SELECT `course_coupon_id`,`dashboard_id`,`dashboard_desc`,
        	`item_id`,`institution_id`,`teacher_id`,`student_id`,`coupon`,`is_used`,
        	`amount`,`purpose`,`remarks`,`last_update_id`,`last_update_ts` 
        	FROM `course_coupon_dtls` WHERE `student_id`=%s""",(student_id))
		course_coupondtls = cursor.fetchall()

		for i in range(len(course_coupondtls)):
			course_coupondtls[i]['last_update_ts'] = course_coupondtls[i]['last_update_ts'].isoformat()

		cursor.close()
		return ({"attributes": {"status_desc": "Course Coupon Details",
                                "status": "success"
                                },
                 "responseList": course_coupondtls}), status.HTTP_200_OK
#--------------------get-Course-Coupon-by-student-id-------------------------#

#-----------------------update-course-coupon-dtls----------------------------#
@name_space.route("/updateCourseCouponDtlsByCourseCouponId/<int:course_coupon_id>")
class updateCourseCouponDtlsByCourseCouponId(Resource):
    @api.expect(update_coursecoupon)
    def put(self,course_coupon_id):
        details = request.get_json()
        connection = mysql_connection()
        cursor = connection.cursor()
        
        Dashboard_desc = details.get('dashboard_desc')
        Amount = details.get('amount')
        Purpose = details.get('purpose')
        Remarks = details.get('remarks')

        cursor.execute("""SELECT `dashboard_desc`,`amount`,`purpose`,`remarks` FROM 
        	`course_coupon_dtls` WHERE `course_coupon_id`=%s""",(course_coupon_id))
        coupon_dtls = cursor.fetchone()

        if coupon_dtls:
            
            if not Dashboard_desc:
                Dashboard_desc = coupon_dtls.get('dashboard_desc')
                # print(Dashboard_desc)
            if not Amount:
                Amount = coupon_dtls.get('amount')
                # print(Amount)
            if not Purpose:
                Purpose = coupon_dtls.get('purpose')
                # print(Purpose)
            if not Remarks:
                Remarks = coupon_dtls.get('remarks')
                # print(Remarks)
            
        update_coupondtls = ("""UPDATE `course_coupon_dtls` SET 
            `dashboard_desc`=%s,`amount`=%s,`purpose`=%s,`remarks`=%s 
            where `course_coupon_id`= %s""")
        coupondtls_data = (Dashboard_desc,Amount,Purpose,Remarks,course_coupon_id)

        updatedata = cursor.execute(update_coupondtls,coupondtls_data)

        return ({"attributes": {"status_desc": "Course Coupon Update Details.",
                            "status": "success"
                            },
                            "responseList":details}), status.HTTP_200_OK

#-----------------------update-course-coupon-dtls------------------------------------#

#-----------------------------delete-student-assignment-------------------------------#
def deleteCoupon(course_coupon_id):
	connection = mysql_connection()
	cursor = connection.cursor()
        
	try:
		delCouseCouponDtls = ("""DELETE FROM `course_coupon_dtls` WHERE 
        	`course_coupon_id`=%s""")

		delData = (course_coupon_id)
		cursor.execute(delCouseCouponDtls,delData)
		connection.commit()
		cursor.close()
		
	except Exception as e:
		return e

	return 'updated'
	
@name_space.route("/deleteCouseCouponDtls/<int:course_coupon_id>")
class deleteCouseCouponDtls(Resource):
	def put(self,course_coupon_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		res = 'Course Coupon Details Removed.'
     
		cursor.execute("""SELECT * FROM `course_coupon_dtls` WHERE 
			`course_coupon_id` = %s""",(course_coupon_id))

		couponDtls = cursor.fetchall()
		if couponDtls:
			delRes = deleteCoupon(course_coupon_id)
				
			if delRes == 'updated':
				res = 'Course Coupon Details Removed.'

		cursor.close()

		return ({"attributes": {"status_desc": "Course Coupon Details.",
									"status": "success"
									},
					"responseList": res}), status.HTTP_200_OK

#-----------------------------delete-student-assignment-------------------------------#

#-----------------------update-course-coupon-dtls----------------------------#
def insert_studentcoursefees(dashboard_id,item_id,student_id,coupon,discount_given,discount,purchaseddate):
	connection = mysql_connection()
	cursor = connection.cursor()

	conn = nextmysql_connection()
	cur = conn.cursor()

	try:
		cursor.execute("""SELECT `course_coupon_id`,`dashboard_id`,`dashboard_desc`,
        	`item_id`,`institution_id`,`teacher_id`,`student_id`,`coupon`,
        	`amount`,`purpose`,`remarks` FROM 
        	`course_coupon_dtls` WHERE `dashboard_id`=%s and `item_id`=%s and 
        	`student_id`=%s and `coupon`=%s and `is_used`='y'""",
        	(dashboard_id,item_id,student_id,coupon))
		coupon_dtls = cursor.fetchone()
		
		if coupon_dtls:
			totalamount = coupon_dtls['amount']
			
			institutionid = coupon_dtls['institution_id']
			
			teacherid = coupon_dtls['teacher_id']
			
			if discount_given == 'y':
			    discount_percentage = (discount*100)/totalamount
			    actual_amount = totalamount - discount
			    
			else:
				discount_percentage = "0"
				actual_amount = totalamount

			insert_studentcoursefees = ("""INSERT INTO `student_coursefee_mapping`(`student_id`,`course_id`,`payment_mode`,
				`payment_type`,`no_of_installment`,`total_amount`,`discount_given`,
				`discount_percentage`,`discount`,`actual_amount`,`purchased_on`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
			student_course_data = (student_id,item_id,"coupon","full","1",totalamount,
				discount_given,discount_percentage,discount,actual_amount,purchaseddate)

			studentcoursefees = cur.execute(insert_studentcoursefees,student_course_data)
			course_fees_id = cur.lastrowid

			studentPaymentDetailsInsert = ("""INSERT INTO `student_coursefee_payment_details`(`student_id`,
				`payment_amount`,`payment_duedate`,`is_pending`,`paid_on`,`coursefee_id`,
				`transaction_id`) VALUES(%s,%s,%s,%s,%s,%s,%s)""")
			studentPayment_data = (student_id,actual_amount,"","n",purchaseddate,course_fees_id,coupon)
			studentPayment = cur.execute(studentPaymentDetailsInsert,studentPayment_data)
			
			studentCoursemaster = ("""INSERT INTO `student_course_master`(`student_id`,
				`course_id`, `teacher_id`, `coursefee_id`, `Institution_ID`)
				VALUES(%s,%s,%s,%s,%s)""")
			studentCourse_data = (student_id,item_id,teacherid,course_fees_id,institutionid)
			studentCourse = cur.execute(studentCoursemaster,studentCourse_data)
				
		
		connection.commit()
		conn.commit()
		cursor.close()
		cur.close()
	except Exception as e:
		return e

	return 'Inserted'

class Compute(Thread):
	def __init__(self, request, funcname):
		Thread.__init__(self)
		self.request = request
		self.funcname = funcname

	def run(self):
		time.sleep(5)
		if self.funcname == 'Couponvalidation':
			dashboard_id = self.request[0]
			item_id = self.request[1]
			student_id = self.request[2]
			coupon = self.request[3]
			discount_given = self.request[4]
			discount = self.request[5]
			purchaseddate = self.request[6]
			insert_studentcoursefees(dashboard_id,item_id,student_id,coupon,discount_given,discount,purchaseddate)
		else:
			pass 

@name_space.route("/Couponvalidation")
class Couponvalidation(Resource):
    @api.expect(validcoursecoupon)
    def put(self):
        details = request.get_json()
        connection = mysql_connection()
        cursor = connection.cursor()

        conn = nextmysql_connection()
        cur = conn.cursor()

        dashboard_id = details['dashboard_id']
        item_id = details['item_id']
        student_id = details['student_id']
        coupon = details['coupon']
        discount_given = details['discount_given']
        discount = details['discount']
        purchaseddate = datetime.now().strftime('%Y-%m-%d')

        cursor.execute("""SELECT `course_coupon_id`,`dashboard_id`,`dashboard_desc`,
        	`item_id`,`institution_id`,`teacher_id`,`student_id`,`coupon`,
        	`amount`,`purpose`,`remarks` FROM 
        	`course_coupon_dtls` WHERE `dashboard_id`=%s and `item_id`=%s and 
        	`student_id`=%s and `coupon`=%s and `is_used`='n'""",
        	(dashboard_id,item_id,student_id,coupon))
        coupon_dtls = cursor.fetchone()

        if coupon_dtls:
            totalamount = coupon_dtls['amount']
            institutionid = coupon_dtls['institution_id']
            teacherid = coupon_dtls['teacher_id']

            update_coupondtls = ("""UPDATE `course_coupon_dtls` SET `is_used`='y' 
            	WHERE `dashboard_id`=%s and `item_id`=%s and `student_id`=%s and 
            	`coupon`=%s""")
            coupondtls_data = (dashboard_id,item_id,student_id,coupon)

            updatedata = cursor.execute(update_coupondtls,coupondtls_data)
            
            coupon_dtls['is_used'] ='y'
            coupon_dtls['discount_given'] = discount_given
            coupon_dtls['discount'] = discount
            coupon_dtls['purchaseddate'] = purchaseddate 
            
            connection.commit()
            cursor.close()
            
            sendrReq = (dashboard_id,item_id,student_id,coupon,discount_given,discount,purchaseddate)
            thread_a = Compute(sendrReq,'Couponvalidation')
            thread_a.start()

            return ({"attributes": {"status_desc": "Course Coupon Details",
                            "status": "success",
                            "msg":"valid coupon"
                            },
                            "responseList":coupon_dtls}), status.HTTP_200_OK
        else:
        	return ({"attributes": {"status_desc": "Course Coupon Details",
                            "status": "success",
                            "msg":"invalid coupon"
                            },
                            "responseList":[]}), status.HTTP_200_OK

#-----------------------update-course-coupon-dtls------------------------------------#

#------------------------------------------------------------------------------------#
@name_space.route("/CourseOfferDtlsByInstitution_id/<int:institution_id>")
class CourseOfferDtlsByInstitution_id(Resource):
	def get(self,institution_id):
		connection = nextmysql_connection()
		cursor = connection.cursor()

		cursor.execute("""SELECT `courseoffer_id`,skywalk_courseoffer.`course_id`,
			`distributor_id`,`distributor_code`,`name`,`course_title`,`course_description`,
			`course_image`,`course_filetype`,`course_amount`,`discount_given`,
			`discount_percentage`,`discount_value`,`actual_amount`,
			skywalk_courseoffer.`last_update_ts` FROM `skywalk_courseoffer` 
			inner join `instituition_course_master` on skywalk_courseoffer.`course_id` = 
			instituition_course_master.`course_id` inner join `skywalk_distributor_channel` 
			on skywalk_courseoffer.`distributor_id` = 
			skywalk_distributor_channel.`skywalk_distributor_id` WHERE 
			instituition_course_master.`institution_id`=%s""",(institution_id))
		course_offer= cursor.fetchall()

		for i in range(len(course_offer)):
			course_offer[i]['last_update_ts'] = course_offer[i]['last_update_ts'].isoformat()

		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Course Offer Details",
                                "status": "success"
                                },
                 "responseList": course_offer}), status.HTTP_200_OK
#------------------------------------------------------------------------------------#

#------------------------------------------------------------------------------------#
@name_space.route("/OnlineTestOfferDtlsByInstitution_id/<int:institution_id>")
class CourseOfferDtlsByInstitution_id(Resource):
	def get(self,institution_id):
		connection = nextmysql_connection()
		cursor = connection.cursor()

		cursor.execute("""SELECT `onlinetest_offer_id`,skywalk_onlinetest_offer.`onlinetest_id`,
		  `Title`,`online_test_amount`,`discount_given`,`discount_percentage`,`discount_value`,
		  `actual_amount`,skywalk_onlinetest_offer.`last_update_ts` FROM 
		  `skywalk_onlinetest_offer` INNER JOIN `online_test` on 
		  skywalk_onlinetest_offer.`onlinetest_id` = online_test.`Online_Test_ID` 
		  WHERE online_test.`Institution_ID`=%s""",
		  (institution_id))
		onlinetest_offer= cursor.fetchall()

		for i in range(len(onlinetest_offer)):
			onlinetest_offer[i]['last_update_ts'] = onlinetest_offer[i]['last_update_ts'].isoformat()

		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Online-Test Offer Details",
                                "status": "success"
                                },
                 "responseList": onlinetest_offer}), status.HTTP_200_OK
#------------------------------------------------------------------------------------#

#------------------------------------------------------------------------------------#
@name_space.route("/updateCourseOfferDtlsByCourseId/<int:course_id>")
class updateCourseOfferDtlsByCourseId(Resource):
    @api.expect(update_courseoffer)
    def put(self,course_id):
        details = request.get_json()
        connection = nextmysql_connection()
        cursor = connection.cursor()
        
        Course_title = details.get('course_title')
        Course_description = details.get('course_description')
        Course_amount = details.get('course_amount')
        Discount_given = details.get('discount_given')
        Discount_percentage = details.get('discount_percentage')
        Discount_value = details.get('discount_value')
        Actual_amount = details.get('actual_amount')

        cursor.execute("""SELECT `course_title`,`course_description`, `course_amount`,
			`discount_given`,`discount_percentage`,`discount_value`,`actual_amount` FROM `skywalk_courseoffer` inner join 
			`instituition_course_master` on skywalk_courseoffer.`course_id` = 
			instituition_course_master.`course_id` WHERE 
			skywalk_courseoffer.`course_id`=%s""",(course_id))
        courseOffer_dtls = cursor.fetchone()

        if courseOffer_dtls:
            
            if not Course_title:
                Course_title = courseOffer_dtls.get('course_title')
                
            if not Course_description:
                Course_description = courseOffer_dtls.get('course_description')
                
            if not Course_amount:
                Course_amount = courseOffer_dtls.get('course_amount')
                
            if not Discount_given:
                Discount_given = courseOffer_dtls.get('discount_given')
                
            if not Discount_percentage:
                Discount_percentage = courseOffer_dtls.get('discount_percentage')
                
            if not Discount_value:
                Discount_value = courseOffer_dtls.get('discount_value')
                
            if not Actual_amount:
                Actual_amount = courseOffer_dtls.get('actual_amount')
                
        update_course_master = ("""UPDATE `instituition_course_master` SET `course_title`=%s,
        	`course_description`=%s WHERE `course_id`=%s""")
        course_master_data = (Course_title,Course_description,course_id)

        updatedata = cursor.execute(update_course_master,course_master_data)

        update_courseOfferdtls = ("""UPDATE `skywalk_courseoffer` SET `course_amount`=%s,`discount_given`=%s,
        	`discount_percentage`=%s,`discount_value`=%s,`actual_amount`=%s 
        	WHERE `course_id`=%s""")
        courseOffer_data = (Course_amount,Discount_given,Discount_percentage,
        	Discount_value,Actual_amount,course_id)

        updatedata = cursor.execute(update_courseOfferdtls,courseOffer_data)

        return ({"attributes": {"status_desc": "Course Offer Update Details.",
                            "status": "success"
                            },
                            "responseList":details}), status.HTTP_200_OK

#------------------------------------------------------------------------------------#

#------------------------------------------------------------------------------------#
@name_space.route("/CourseOfferDtlsByCourseId/<int:course_id>")
class CourseOfferDtlsByInstitution_id(Resource):
	def get(self,course_id):
		connection = nextmysql_connection()
		cursor = connection.cursor()

		cursor.execute("""SELECT `course_title`,`course_description`, `course_amount`,
			`discount_given`,`discount_percentage`,`discount_value`,`actual_amount`,
			skywalk_courseoffer.`last_update_ts` FROM `skywalk_courseoffer` inner join 
			`instituition_course_master` on skywalk_courseoffer.`course_id` = 
			instituition_course_master.`course_id` WHERE 
			skywalk_courseoffer.`course_id`=%s""",(course_id))
		course_offer= cursor.fetchone()

		course_offer['last_update_ts'] = course_offer['last_update_ts'].isoformat()

		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Course Offer Details",
                                "status": "success"
                                },
                 "responseList": course_offer}), status.HTTP_200_OK
#------------------------------------------------------------------------------------#

#------------------------------------------------------------------------------------#
@name_space.route("/SkywalkDistributorDtlsByInstitutionId/<int:institution_id>")
class SkywalkDistributorDtlsByInstitutionId(Resource):
	def get(self,institution_id):
		connection = nextmysql_connection()
		cursor = connection.cursor()

		cursor.execute("""SELECT `skywalk_distributor_id`,`distributor_code`,`name`,
			`location`,`last_update_ts` FROM `skywalk_distributor_channel` where 
			`institution_id`=%s""",(institution_id))
		SkywalkDistributorDtls= cursor.fetchall()

		for i in range(len(SkywalkDistributorDtls)):
			SkywalkDistributorDtls[i]['last_update_ts'] = SkywalkDistributorDtls[i]['last_update_ts'].isoformat()

		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Distributor Details",
                                "status": "success"
                                },
                 "responseList": SkywalkDistributorDtls}), status.HTTP_200_OK
#------------------------------------------------------------------------------------#