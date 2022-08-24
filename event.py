from pyfcm import FCMNotification
from flask import Flask, request, jsonify, json
from flask_api import status
import datetime
from datetime import datetime,timedelta,date
import time
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from werkzeug.utils import cached_property
import requests
from database_connections import connect_logindb,connect_lab_lang1
from pytz import timezone
import pytz
import string
import random

app = Flask(__name__)
cors = CORS(app)

#----------------------database-connection---------------------#
def mysql_connection():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='event',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

#----------------------database-connection---------------------#

event = Blueprint('event_api', __name__)
api = Api(event,  title='Myelsa API',description='Myelsa API')
name_space = api.namespace('event',description='Event')
name_space_food = api.namespace('EventFood',description='Event Food')
name_space_dashboard = api.namespace('Dashboard',description='Dashboard')
name_space_function = api.namespace('EventFunction',description='Event Function')
name_space_content = api.namespace('EventContent',description='Event Content')

name_space_event_photo = api.namespace('EventPhoto',description='Event Photo')

addGuest = api.model('addGuest', {
	"first_name":  fields.String(),
	"last_name":  fields.String(),
	"client_id":fields.Integer(required=True),
	"phoneno":fields.String(required=True),
	"arrival_time":fields.String(),
	"departure_time":fields.String(),
	"how_to_arrive":fields.String(),
	"pickup_location":fields.String(),
	"pickup_time":fields.String(),
	"drop_time":fields.String(),
	"departure_location":fields.String(),
	"guest_status":fields.Integer(),
	"INSTITUTION_ID":fields.Integer(required=True)
})

addGuestWithFamily = api.model('addGuestWithFamily', {
	"first_name":  fields.String(),
	"last_name":  fields.String(),
	"client_id":fields.Integer(required=True),
	"phoneno":fields.String(required=True),
	"arrival_time":fields.String(),
	"departure_time":fields.String(),
	"how_to_arrive":fields.String(),
	"pickup_location":fields.String(),
	"pickup_time":fields.String(),
	"drop_time":fields.String(),
	"departure_location":fields.String(),
	"guest_status":fields.Integer(),
	"family_first_name":fields.List(fields.String),
	"family_last_name":fields.List(fields.String),
	"family_phoneno":fields.List(fields.String),
	"INSTITUTION_ID":fields.Integer(required=True)
})

addFamily = api.model('addFamily', {
	"first_name":  fields.String(),
	"last_name":  fields.String(),
	"client_id":fields.Integer(required=True),
	"phoneno":fields.String(required=True),
	"arrival_time":fields.String(),
	"departure_time":fields.String(),
	"how_to_arrive":fields.String(),
	"pickup_location":fields.String(),
	"pickup_time":fields.String(),
	"drop_time":fields.String(),
	"departure_location":fields.String(),
	"guest_status":fields.Integer(),
	"guest_id":fields.Integer(required=True),
	"INSTITUTION_ID":fields.Integer(required=True)
})

guest_putmodel = api.model('updateGuest', {
	"arrival_time":fields.String(),
	"departure_time":fields.String(),
	"how_to_arrive":fields.String(),
	"pickup_location":fields.String(),
	"pickup_time":fields.String(),
	"drop_time":fields.String(),
	"departure_location":fields.String(),
	"guest_status":fields.Integer()
})

addClient = api.model('addClient', {
	"first_name":  fields.String(),
	"last_name":  fields.String(),
	"phoneno":fields.String(required=True),
	"event_manager_id":fields.Integer(required=True),
	"INSTITUTION_ID":fields.Integer(required=True)
})

createOccasion = api.model('addOcassion', {
	"name": fields.String(),
	"date": fields.String(),
	"time": fields.String(),
	"end_time": fields.String(),
	"mens_dress_code": fields.String(),
	"womens_dress_code": fields.String(),
	"kid_dress_code": fields.String(),
	"place": fields.String(),
	"event_id":fields.Integer,
	"occasion_type":fields.Integer,
	"theme_id":fields.Integer,
	"event_manager_id":fields.Integer(required=True)
})

ocassion_putmodel = api.model('ocassion_putmodel', {
	"name": fields.String(),
	"date": fields.String(),
	"time": fields.String(),
	"end_time": fields.String(),
	"place": fields.String(),
	"mens_dress_code":fields.String(),
	"womens_dress_code":fields.String(),
	"kid_dress_code":fields.String(),
	"theme_id":fields.Integer
})

createFood = api.model('addFood', {
	"name": fields.String(),
	"date": fields.String(),
	"time": fields.String(),
	"end_time": fields.String(),
	"place": fields.String(),
	"function_id":fields.Integer,
	"event_manager_id":fields.Integer(required=True)
})

food_putmodel = api.model('updateFood', {
	"name": fields.String(),
	"date": fields.String(),
	"time": fields.String(),
	"end_time": fields.String(),
	"place": fields.String()
})

createFoodItem = api.model('createFoodItem', {
	"item_name":fields.String(),
	"item_type":fields.Integer(),
	"cuisine":fields.String(),
	"cuisine_id":fields.Integer(),
	"food_id":fields.Integer(required=True),
	"event_manager_id":fields.Integer(required=True)
})

createMultipleFoodItem = api.model('createMultipleFoodItem', {
	"item_name":fields.List(fields.String),
	"item_type":fields.Integer(),
	"cuisine":fields.String(),
	"cuisine_id":fields.Integer(),
	"food_id":fields.Integer(required=True),
	"event_manager_id":fields.Integer(required=True)
})

food_item_putmodel = api.model('food_item_putmodel', {
	"item_name":fields.String(),
	"item_type":fields.Integer(),
	"cuisine":fields.String(),
	"cuisine_id":fields.Integer()
})

devicetoken_postmodel = api.model('deviceToken',{
	"user_id":fields.Integer(required=True),	
	"device_type":fields.Integer(required=True),
	"device_token":fields.String(required=True)
})

appmsg_model = api.model('appmsg_model', {	
	"device_id":fields.String(),
	"title":fields.String(),
	"text":fields.String()
})

function_postmodel = api.model('function_postmodel', {
	"function_name":fields.String(),
	"function_date":fields.String(),
	"function_time":fields.String(),
	"end_time":fields.String(),
	"place":fields.String(),
	"mens_dress_code":fields.String(),	
	"womens_dress_code":fields.String(),
	"kid_dress_code":fields.String(),
	"event_id":fields.Integer(required=True),
	"theme_id":fields.Integer,
	"function_type":fields.Integer,
	"occasion_id":fields.Integer(required=True),
	"client_id":fields.Integer(required=True)
})

function_putmodel =  api.model('function_putmodel', {
	"function_name":fields.String(),
	"function_date":fields.String(),
	"function_time":fields.String(),
	"end_time":fields.String(),
	"place":fields.String(),
	"mens_dress_code":fields.String(),	
	"womens_dress_code":fields.String(),
	"kid_dress_code":fields.String(),
	"theme_id":fields.Integer
})

event_postmodel = api.model('event_postmodel', {
	"event_name":fields.String(),
	"event_date":fields.String(),
	"event_time":fields.String(),
	"event_end_date":fields.String(),
	"event_end_time":fields.String(),	
	"location":fields.String(),
	"city":fields.String(),
	"client_id":fields.Integer(required=True)
})

event_putmodel = api.model('event_putmodel', {
	"event_name":fields.String(),
	"event_date":fields.String(),
	"event_time":fields.String(),
	"event_end_date":fields.String(),
	"event_end_time":fields.String(),	
	"location":fields.String(),
	"city":fields.String()
})

assign_guest_postmodel = api.model('assign_guest_postmodel', {
	"guest_id":fields.List(fields.Integer),
	"function_id":fields.Integer(required=True),
	"client_id":fields.Integer(required=True)
})

zoom_postmodel = api.model('zoom_postmodel', {
	"user_id":fields.Integer(required=True)
})

event_photo_postmodel = api.model('EventPhoto', {
	"image":fields.String(required=True),
	"text":fields.String,
	"event_id":fields.Integer(required=True),	
	"event_manager_id":fields.Integer(required=True),
	"user_id":fields.Integer(required=True),
})

like_photo_postmodel = api.model('LikePhoto', {
	"event_photo_id":fields.Integer(required=True),
	"user_id":fields.Integer(required=True),
	"is_like":fields.Integer(required=True)
})

notification_model = api.model('notification_model', {	
	"user_id":fields.Integer(required=True),
	"text":fields.String(),	
	"image":fields.String(),
	"title": fields.String(required=True)
})

comments_on_event_photo_post_model = api.model('comments_on_event_photo_post_model',{
	"user_id":fields.Integer(required=True),
	"event_photo_id":fields.Integer(required=True),
	"comments":fields.String()
})


tag_photo_postmodel = api.model('TagPhoto', {
	"event_photo_id":fields.Integer(required=True),
	"tagged_user_id":fields.List(fields.Integer),
	"photo_user_id":fields.Integer(required=True),
	"is_tagged":fields.Integer(required=True)
})

cuisine_putmodel = api.model('cuisine_putmodel', {
	"cuisine_name":fields.String()
})

createcuisine = api.model('createcuisine', {
	"cuisine_name":fields.String(required=True),
})

content_postmodel = api.model('content_postmodel', {
	"content_link":fields.String(required=True),
	"content_name":fields.String(required=True),
	"user_id":fields.Integer(required=True),
	"role":fields.Integer(required=True)
})

assign_content_postmodel = api.model('assign_content_postmodel', {
	"content_id":fields.Integer(required=True),
	"user_id":fields.List(fields.Integer)	
})

createFilteringFoodItem = api.model('createFilteringFoodItem', {
	"item_name":fields.String(),	
	"cuisine_id":fields.Integer(),
	"item_type":fields.Integer(required=True)
})

filtering_item_putmodel = api.model('filtering_item_putmodel', {
	"item_name":fields.String(),	
	"cuisine_id":fields.Integer(),
	"item_type":fields.Integer()
})


BASE_URL = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/event/'


#----------------------Add-Guest---------------------#

@name_space.route("/addGuest")
class addGuest(Resource):
	@api.expect(addGuest)
	def post(self):

		connection = connect_logindb()
		cursor = connection.cursor()
		details = request.get_json()

		first_name = details['first_name']
		last_name = details['last_name']
		client_id = details['client_id']
		phoneno = details['phoneno']
		arrival_time = details['arrival_time']
		departure_time = details['departure_time']
		how_to_arrive = details['how_to_arrive']
		pickup_location = details['pickup_location']
		pickup_time = details['pickup_time']
		guest_status = details['guest_status']
		INSTITUTION_ID = details['INSTITUTION_ID']

		if details and "departure_location" in details:
			departure_location = details['departure_location']
		else:
			departure_location = ""

		if details and "drop_time" in details:
			drop_time = details['drop_time']
		else:
			drop_time = ""

		today = date.today()

		insert_user_credential_query = ("""INSERT INTO `institution_user_credential`(`first_name`,`INSTITUTION_USER_NAME`,`INSTITUTION_USER_PASSWORD`,`last_name`,`PRIMARY_CONTACT_NUMBER`) 
							VALUES(%s,%s,%s,%s,%s)""")

		insert_user_credential_data = (first_name,phoneno,phoneno,last_name,phoneno)
		cursor.execute(insert_user_credential_query,insert_user_credential_data)

		INSTITUTION_USER_ID = cursor.lastrowid

		insert_user_credential_master_query = ("""INSERT INTO `institution_user_credential_master`(`INSTITUTION_ID`,`INSTITUTION_USER_ID`,`INSTITUTION_USER_ROLE`,`USER_ENROLL_DATE`,`USER_END_DATE`) 
							VALUES(%s,%s,%s,%s,%s)""")
		INSTITUTION_USER_ROLE = "G1"
		insert_user_credential_master_data = (INSTITUTION_ID,INSTITUTION_USER_ID,INSTITUTION_USER_ROLE,today,today)
		cursor.execute(insert_user_credential_master_query,insert_user_credential_master_data)

		insert_guardian_dtls_query = ("""INSERT INTO `guardian_dtls`(`INSTITUTION_ID`,`INSTITUTION_USER_ID_GUARDIAN`,`INSTITUTION_USER_ID_STUDENT`,`RELATIONSHIP`) 
							VALUES(%s,%s,%s,%s)""")		
		RELATIONSHIP = 'Parent'
		insert_guardian_dtls_data = (INSTITUTION_ID,INSTITUTION_USER_ID,client_id,RELATIONSHIP)

		cursor.execute(insert_guardian_dtls_query,insert_guardian_dtls_data)

		insert_guest_details_query = ("""INSERT INTO `guest_details`(`guest_id`,`arrival_time`,`departure_time`,`how_to_arrive`,`pickup_location`,`pickup_time`,`drop_time`,`departure_location`,`status`,`INSTITUTION_ID`,`client_id`) 
							VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
		guest_details_data = (INSTITUTION_USER_ID,arrival_time,departure_time,how_to_arrive,pickup_location,pickup_time,drop_time,departure_location,guest_status,INSTITUTION_ID,client_id)

		cursor.execute(insert_guest_details_query,guest_details_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Add Guest",
	                                "status": "success"
	                            },
								"responseList":details}), status.HTTP_200_OK


#----------------------Add-Guest---------------------#

#----------------------Add-Guest-With-Family--------------------#

@name_space.route("/addGuestWithFamily")
class addGuestWithFamily(Resource):
	@api.expect(addGuestWithFamily)
	def post(self):

		connection = connect_logindb()
		cursor = connection.cursor()
		details = request.get_json()

		first_name = details['first_name']
		last_name = details['last_name']
		client_id = details['client_id']
		phoneno = details['phoneno']
		arrival_time = details['arrival_time']
		departure_time = details['departure_time']
		how_to_arrive = details['how_to_arrive']
		pickup_location = details['pickup_location']
		pickup_time = details['pickup_time']
		guest_status = details['guest_status']
		INSTITUTION_ID = details['INSTITUTION_ID']

		if details and "departure_location" in details:
			departure_location = details['departure_location']
		else:
			departure_location = ""

		if details and "drop_time" in details:
			drop_time = details['drop_time']
		else:
			drop_time = ""

		family_first_names = details.get('family_first_name',[])
		family_last_names = details.get('family_last_name',[])
		family_phonenos = details.get('family_phoneno',[])

		today = date.today()

		insert_user_credential_query = ("""INSERT INTO `institution_user_credential`(`first_name`,`INSTITUTION_USER_NAME`,`INSTITUTION_USER_PASSWORD`,`last_name`,`PRIMARY_CONTACT_NUMBER`) 
							VALUES(%s,%s,%s,%s,%s)""")

		insert_user_credential_data = (first_name,phoneno,phoneno,last_name,phoneno)
		cursor.execute(insert_user_credential_query,insert_user_credential_data)

		INSTITUTION_USER_ID = cursor.lastrowid

		insert_user_credential_master_query = ("""INSERT INTO `institution_user_credential_master`(`INSTITUTION_ID`,`INSTITUTION_USER_ID`,`INSTITUTION_USER_ROLE`,`USER_ENROLL_DATE`,`USER_END_DATE`) 
							VALUES(%s,%s,%s,%s,%s)""")
		INSTITUTION_USER_ROLE = "G1"
		insert_user_credential_master_data = (INSTITUTION_ID,INSTITUTION_USER_ID,INSTITUTION_USER_ROLE,today,today)
		cursor.execute(insert_user_credential_master_query,insert_user_credential_master_data)

		insert_guardian_dtls_query = ("""INSERT INTO `guardian_dtls`(`INSTITUTION_ID`,`INSTITUTION_USER_ID_GUARDIAN`,`INSTITUTION_USER_ID_STUDENT`,`RELATIONSHIP`) 
							VALUES(%s,%s,%s,%s)""")		
		RELATIONSHIP = 'Parent'
		insert_guardian_dtls_data = (INSTITUTION_ID,INSTITUTION_USER_ID,client_id,RELATIONSHIP)

		cursor.execute(insert_guardian_dtls_query,insert_guardian_dtls_data)

		insert_guest_details_query = ("""INSERT INTO `guest_details`(`guest_id`,`arrival_time`,`departure_time`,`how_to_arrive`,`pickup_location`,`pickup_time`,`drop_time`,`departure_location`,`status`,`INSTITUTION_ID`,`client_id`) 
							VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
		guest_details_data = (INSTITUTION_USER_ID,arrival_time,departure_time,how_to_arrive,pickup_location,pickup_time,drop_time,departure_location,guest_status,INSTITUTION_ID,client_id)

		cursor.execute(insert_guest_details_query,guest_details_data)

		for key,family_first_name in enumerate(family_first_names):
			insert_user_credential_query = ("""INSERT INTO `institution_user_credential`(`first_name`,`INSTITUTION_USER_NAME`,`INSTITUTION_USER_PASSWORD`,`last_name`,`PRIMARY_CONTACT_NUMBER`) 
							VALUES(%s,%s,%s,%s,%s)""")

			insert_user_credential_data = (family_first_name,family_phonenos[key],family_phonenos[key],family_last_names[key],family_phonenos[key])
			cursor.execute(insert_user_credential_query,insert_user_credential_data)

			family_id = cursor.lastrowid

			insert_user_credential_master_query = ("""INSERT INTO `institution_user_credential_master`(`INSTITUTION_ID`,`INSTITUTION_USER_ID`,`INSTITUTION_USER_ROLE`,`USER_ENROLL_DATE`,`USER_END_DATE`) 
								VALUES(%s,%s,%s,%s,%s)""")
			INSTITUTION_USER_ROLE = "G1"
			insert_user_credential_master_data = (INSTITUTION_ID,family_id,INSTITUTION_USER_ROLE,today,today)
			cursor.execute(insert_user_credential_master_query,insert_user_credential_master_data)

			insert_guardian_dtls_query = ("""INSERT INTO `guardian_dtls`(`INSTITUTION_ID`,`INSTITUTION_USER_ID_GUARDIAN`,`INSTITUTION_USER_ID_STUDENT`,`RELATIONSHIP`) 
								VALUES(%s,%s,%s,%s)""")		
			RELATIONSHIP = 'Parent'
			insert_guardian_dtls_data = (INSTITUTION_ID,family_id,client_id,RELATIONSHIP)

			cursor.execute(insert_guardian_dtls_query,insert_guardian_dtls_data)

			is_family = 1

			insert_guest_details_query = ("""INSERT INTO `guest_details`(`guest_id`,`arrival_time`,`departure_time`,`how_to_arrive`,`pickup_location`,`pickup_time`,`drop_time`,`departure_location`,`is_family`,`status`,`INSTITUTION_ID`,`client_id`) 
								VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
			guest_details_data = (family_id,arrival_time,departure_time,how_to_arrive,pickup_location,pickup_time,drop_time,departure_location,is_family,guest_status,INSTITUTION_ID,client_id)

			cursor.execute(insert_guest_details_query,guest_details_data)

			insert_family_guest_query = ("""INSERT INTO `guest_family_mapping`(`family_id`,`guest_id`) 
								VALUES(%s,%s)""")
			family_details_data = (family_id,INSTITUTION_USER_ID)

			cursor.execute(insert_family_guest_query,family_details_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Add Guest With Family",
	                                "status": "success"
	                            },
								"responseList":details}), status.HTTP_200_OK


#----------------------Add-Guest-With-Family--------------------#

#----------------------Add-Family-Under-Guest-------------------#

@name_space.route("/addFamily")
class addFamily(Resource):
	@api.expect(addFamily)
	def post(self):

		connection = connect_logindb()
		cursor = connection.cursor()
		details = request.get_json()

		first_name = details['first_name']
		last_name = details['last_name']
		client_id = details['client_id']
		phoneno = details['phoneno']
		arrival_time = details['arrival_time']
		departure_time = details['departure_time']
		how_to_arrive = details['how_to_arrive']
		pickup_location = details['pickup_location']
		pickup_time = details['pickup_time']
		guest_status = details['guest_status']
		INSTITUTION_ID = details['INSTITUTION_ID']
		guest_id = details['guest_id']

		if details and "departure_location" in details:
			departure_location = details['departure_location']
		else:
			departure_location = ""

		if details and "drop_time" in details:
			drop_time = details['drop_time']
		else:
			drop_time = ""

		today = date.today()

		insert_user_credential_query = ("""INSERT INTO `institution_user_credential`(`first_name`,`INSTITUTION_USER_NAME`,`INSTITUTION_USER_PASSWORD`,`last_name`,`PRIMARY_CONTACT_NUMBER`) 
							VALUES(%s,%s,%s,%s,%s)""")

		insert_user_credential_data = (first_name,phoneno,phoneno,last_name,phoneno)
		cursor.execute(insert_user_credential_query,insert_user_credential_data)

		family_id = cursor.lastrowid

		insert_user_credential_master_query = ("""INSERT INTO `institution_user_credential_master`(`INSTITUTION_ID`,`INSTITUTION_USER_ID`,`INSTITUTION_USER_ROLE`,`USER_ENROLL_DATE`,`USER_END_DATE`) 
								VALUES(%s,%s,%s,%s,%s)""")
		INSTITUTION_USER_ROLE = "G1"
		insert_user_credential_master_data = (INSTITUTION_ID,family_id,INSTITUTION_USER_ROLE,today,today)
		cursor.execute(insert_user_credential_master_query,insert_user_credential_master_data)

		insert_guardian_dtls_query = ("""INSERT INTO `guardian_dtls`(`INSTITUTION_ID`,`INSTITUTION_USER_ID_GUARDIAN`,`INSTITUTION_USER_ID_STUDENT`,`RELATIONSHIP`) 
								VALUES(%s,%s,%s,%s)""")		
		RELATIONSHIP = 'Parent'
		insert_guardian_dtls_data = (INSTITUTION_ID,family_id,client_id,RELATIONSHIP)

		cursor.execute(insert_guardian_dtls_query,insert_guardian_dtls_data)

		is_family = 1

		insert_guest_details_query = ("""INSERT INTO `guest_details`(`guest_id`,`arrival_time`,`departure_time`,`how_to_arrive`,`pickup_location`,`pickup_time`,`drop_time`,`departure_location`,`is_family`,`status`,`INSTITUTION_ID`,`client_id`) 
								VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
		guest_details_data = (family_id,arrival_time,departure_time,how_to_arrive,pickup_location,pickup_time,drop_time,departure_location,is_family,guest_status,INSTITUTION_ID,client_id)

		cursor.execute(insert_guest_details_query,guest_details_data)

		insert_family_guest_query = ("""INSERT INTO `guest_family_mapping`(`family_id`,`guest_id`) 
								VALUES(%s,%s)""")
		family_details_data = (family_id,guest_id)

		cursor.execute(insert_family_guest_query,family_details_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Add Family",
	                                "status": "success"
	                            },
								"responseList":details}), status.HTTP_200_OK


#----------------------Add-Family-Under-Guest-------------------#

#----------------------Update-Guest---------------------#

@name_space.route("/updateGuest/<int:guest_id>")
class updateGuest(Resource):
	@api.expect(guest_putmodel)
	def put(self, guest_id):

		connection = connect_logindb()
		cursor = connection.cursor()
		details = request.get_json()

		if details and "arrival_time" in details:
			arrival_time = details['arrival_time']
			update_query = ("""UPDATE `guest_details` SET `arrival_time` = %s
				WHERE `guest_id` = %s """)
			update_data = (arrival_time,guest_id)
			cursor.execute(update_query,update_data)

		if details and "departure_time" in details:
			departure_time = details['departure_time']
			update_query = ("""UPDATE `guest_details` SET `departure_time` = %s
				WHERE `guest_id` = %s """)
			update_data = (departure_time,guest_id)
			cursor.execute(update_query,update_data)

		if details and "how_to_arrive" in details:
			how_to_arrive = details['how_to_arrive']
			update_query = ("""UPDATE `guest_details` SET `how_to_arrive` = %s
				WHERE `guest_id` = %s """)
			update_data = (how_to_arrive,guest_id)
			cursor.execute(update_query,update_data)

		if details and "pickup_location" in details:
			pickup_location = details['pickup_location']
			update_query = ("""UPDATE `guest_details` SET `pickup_location` = %s
				WHERE `guest_id` = %s """)
			update_data = (pickup_location,guest_id)
			cursor.execute(update_query,update_data)

		if details and "pickup_time" in details:
			pickup_time = details['pickup_time']
			update_query = ("""UPDATE `guest_details` SET `pickup_time` = %s
				WHERE `guest_id` = %s """)
			update_data = (pickup_time,guest_id)
			cursor.execute(update_query,update_data)

		if details and "drop_time" in details:
			drop_time = details['drop_time']
			update_query = ("""UPDATE `guest_details` SET `drop_time` = %s
				WHERE `guest_id` = %s """)
			update_data = (drop_time,guest_id)
			cursor.execute(update_query,update_data)

		if details and "guest_status" in details:
			guest_status = details['guest_status']
			update_query = ("""UPDATE `guest_details` SET `status` = %s
				WHERE `guest_id` = %s """)
			update_data = (guest_status,guest_id)
			cursor.execute(update_query,update_data)

		if details and "departure_location" in details:
			departure_location = details['departure_location']
			update_query = ("""UPDATE `guest_details` SET `departure_location` = %s
				WHERE `guest_id` = %s """)
			update_data = (departure_location,guest_id)
			cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Occasion",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK


#----------------------Update-Guest---------------------#

#----------------------Delete-Guest---------------------#

@name_space.route("/deleteGuest/<int:guest_id>")
class deleteGuest(Resource):
	def delete(self, guest_id):

		connection = connect_logindb()
		cursor = connection.cursor()

		delete_guardian_query = ("""DELETE FROM `guardian_dtls` WHERE `INSTITUTION_USER_ID_GUARDIAN` = %s """)
		delGuardianData = (guest_id)
		
		cursor.execute(delete_guardian_query,delGuardianData)

		delete_guest_query = ("""DELETE FROM `guest_details` WHERE `guest_id` = %s """)
		delGuestData = (guest_id)
		
		cursor.execute(delete_guest_query,delGuestData)

		delete_user_credential_master_query = ("""DELETE FROM `institution_user_credential_master` WHERE `INSTITUTION_USER_ID` = %s """)
		deleteUserCredentialMasterData = (guest_id)
		cursor.execute(delete_user_credential_master_query,deleteUserCredentialMasterData)

		delete_user_credential_query = ("""DELETE FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s """)
		deleteUserCredentialData = (guest_id)
		cursor.execute(delete_user_credential_query,deleteUserCredentialData)

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Delete Guest",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Guest---------------------#

#----------------------Guest-List-By-Client-Id---------------------#

@name_space.route("/getGuestListByClientId/<int:INSTITUTION_ID>/<int:client_id>")	
class getGuestListByClientId(Resource):
	def get(self,INSTITUTION_ID,client_id):

		connection = connect_logindb()
		cursor = connection.cursor()

		get_guest_list_query = ("""SELECT iuc.`INSTITUTION_USER_ID`,iuc.`INSTITUTION_USER_NAME`,iuc.`INSTITUTION_USER_PASSWORD`,iuc.`FIRST_NAME`,iuc.`LAST_NAME`,iuc.`PRIMARY_CONTACT_NUMBER`
					FROM `guardian_dtls` gd
					INNER JOIN `institution_user_credential` iuc ON iuc.`INSTITUTION_USER_ID` = gd.`INSTITUTION_USER_ID_GUARDIAN`
					INNER JOIN `guest_details` ggd ON ggd.`guest_id` = gd.`INSTITUTION_USER_ID_GUARDIAN`
					WHERE gd.`INSTITUTION_ID` = %s and `INSTITUTION_USER_ID_STUDENT` = %s""")
		get_guest_list_data = (INSTITUTION_ID,client_id)
		guest_list_count = cursor.execute(get_guest_list_query,get_guest_list_data)

		if guest_list_count > 0:
			guest_list_data =  cursor.fetchall()

			for key,data in enumerate(guest_list_data):
				get_guest_details_query = ("""SELECT * FROM `guest_details` 
						WHERE `guest_id` = %s""")
				get_guest_details_data = (data['INSTITUTION_USER_ID'])
				count_guest_details = cursor.execute(get_guest_details_query,get_guest_details_data)
				if count_guest_details > 0:
					guest_details_data = cursor.fetchone()
					guest_list_data[key]['arrival_time'] = guest_details_data['arrival_time']
					guest_list_data[key]['departure_time'] = guest_details_data['departure_time']
					guest_list_data[key]['how_to_arrive'] = guest_details_data['how_to_arrive']
					guest_list_data[key]['pickup_location'] = guest_details_data['pickup_location']
					guest_list_data[key]['pickup_time'] = guest_details_data['pickup_time']
					guest_list_data[key]['drop_time'] = guest_details_data['drop_time']
					guest_list_data[key]['departure_location'] = guest_details_data['departure_location']
					guest_list_data[key]['status'] = guest_details_data['status']
				else:
					guest_list_data[key]['arrival_time'] =""
					guest_list_data[key]['departure_time'] = ""
					guest_list_data[key]['how_to_arrive'] = ""
					guest_list_data[key]['pickup_location'] = ""
					guest_list_data[key]['pickup_time'] = ""
					guest_list_data[key]['drop_time'] = ""
					guest_list_data[key]['departure_location'] = ""
					guest_list_data[key]['status'] = 0

				get_family_count_query=("""SELECT count(*) as `family_count` FROM `guest_family_mapping` 
						WHERE `guest_id` = %s""")
				get_family_count_data = (data['INSTITUTION_USER_ID'])
				count_family =  cursor.execute(get_family_count_query,get_family_count_data)

				if count_family > 0:
					family_count = cursor.fetchone()
					guest_list_data[key]['family_count'] = family_count['family_count']
				else:
					guest_list_data[key]['family_count'] = 0
		else:
			guest_list_data = []

		return ({"attributes": {
		    		"status_desc": "guest_list",
		    		"status": "success"
		    	},
		    	"responseList":guest_list_data}), status.HTTP_200_OK

#----------------------Guest-List-By-Client-Id---------------------#

#----------------------Guest-List-By-Client-Id---------------------#

@name_space.route("/getGuestListByClientIdWithFilteration/<int:INSTITUTION_ID>/<int:client_id>/<int:arrival_or_departure_type>/<string:time>")	
class getGuestListByClientIdWithFilteration(Resource):
	def get(self,INSTITUTION_ID,client_id,arrival_or_departure_type,time):

		connection = connect_logindb()
		cursor = connection.cursor()

		if arrival_or_departure_type == 1:
			get_guest_list_query = ("""SELECT iuc.`INSTITUTION_USER_ID`,iuc.`INSTITUTION_USER_NAME`,iuc.`INSTITUTION_USER_PASSWORD`,iuc.`FIRST_NAME`,iuc.`LAST_NAME`,iuc.`PRIMARY_CONTACT_NUMBER`,
					ggd.`arrival_time`,ggd.`departure_time`,ggd.`how_to_arrive`,ggd.`pickup_location`,ggd.`pickup_time`,ggd.`drop_time`,ggd.`departure_location`,ggd.`status`
					FROM `guardian_dtls` gd
					INNER JOIN `institution_user_credential` iuc ON iuc.`INSTITUTION_USER_ID` = gd.`INSTITUTION_USER_ID_GUARDIAN`
					INNER JOIN `guest_details` ggd ON ggd.`guest_id` = gd.`INSTITUTION_USER_ID_GUARDIAN`
					WHERE gd.`INSTITUTION_ID` = %s and gd.`INSTITUTION_USER_ID_STUDENT` = %s and ggd.`arrival_time` LIKE %s""")
		else:
			get_guest_list_query = ("""SELECT iuc.`INSTITUTION_USER_ID`,iuc.`INSTITUTION_USER_NAME`,iuc.`INSTITUTION_USER_PASSWORD`,iuc.`FIRST_NAME`,iuc.`LAST_NAME`,iuc.`PRIMARY_CONTACT_NUMBER`,
					ggd.`arrival_time`,ggd.`departure_time`,ggd.`how_to_arrive`,ggd.`pickup_location`,ggd.`pickup_time`,ggd.`drop_time`,ggd.`departure_location`,ggd.`status`
					FROM `guardian_dtls` gd
					INNER JOIN `institution_user_credential` iuc ON iuc.`INSTITUTION_USER_ID` = gd.`INSTITUTION_USER_ID_GUARDIAN`
					INNER JOIN `guest_details` ggd ON ggd.`guest_id` = gd.`INSTITUTION_USER_ID_GUARDIAN`
					WHERE gd.`INSTITUTION_ID` = %s and gd.`INSTITUTION_USER_ID_STUDENT` = %s and ggd.`departure_time` LIKE %s""")
		get_guest_list_data = (INSTITUTION_ID,client_id,"%"+time+"%")
		guest_list_count = cursor.execute(get_guest_list_query,get_guest_list_data)

		if guest_list_count > 0:
			guest_list_data =  cursor.fetchall()

			for key,data in enumerate(guest_list_data):	
				get_family_count_query=("""SELECT count(*) as `family_count` FROM `guest_family_mapping` 
						WHERE `guest_id` = %s""")
				get_family_count_data = (data['INSTITUTION_USER_ID'])
				count_family =  cursor.execute(get_family_count_query,get_family_count_data)

				if count_family > 0:
					family_count = cursor.fetchone()
					guest_list_data[key]['family_count'] = family_count['family_count']
				else:
					guest_list_data[key]['family_count'] = 0		
		else:
			guest_list_data = []

		return ({"attributes": {
		    		"status_desc": "guest_list",
		    		"status": "success"
		    	},
		    	"responseList":guest_list_data}), status.HTTP_200_OK

#----------------------Guest-List-By-Client-Id---------------------#

#----------------------Guest-Details---------------------#

@name_space.route("/getGuestDetails/<int:guest_id>")	
class getGuestDetails(Resource):
	def get(self,guest_id):

		connection = connect_logindb()
		cursor = connection.cursor()


		get_guest_query = ("""SELECT iuc.`INSTITUTION_USER_ID`,iuc.`INSTITUTION_USER_NAME`,iuc.`INSTITUTION_USER_PASSWORD`,iuc.`FIRST_NAME`,iuc.`LAST_NAME`,iuc.`PRIMARY_CONTACT_NUMBER`,
					ggd.`arrival_time`,ggd.`departure_time`,ggd.`how_to_arrive`,ggd.`pickup_location`,ggd.`pickup_time`,ggd.`drop_time`,ggd.`departure_location`,ggd.`status`
					FROM `institution_user_credential` iuc 					
					INNER JOIN `guest_details` ggd ON ggd.`guest_id` = iuc.`INSTITUTION_USER_ID`
					WHERE iuc.`INSTITUTION_USER_ID` = %s""")
		get_guest_data = (guest_id)
		cursor.execute(get_guest_query,get_guest_data)

		guest_data = cursor.fetchone()	

		return ({"attributes": {
		    		"status_desc": "guest_data",
		    		"status": "success"
		    	},
		    	"responseList":guest_data}), status.HTTP_200_OK


#----------------------Guest-Details---------------------#

#----------------------Guest-Details---------------------#

@name_space.route("/getFamilyListByGuestId/<int:guest_id>")	
class getFamilyListByGuestId(Resource):
	def get(self,guest_id):

		connection = connect_logindb()
		cursor = connection.cursor()

		get_guest_query = ("""SELECT iuc.`INSTITUTION_USER_ID`,iuc.`INSTITUTION_USER_NAME`,iuc.`INSTITUTION_USER_PASSWORD`,iuc.`FIRST_NAME`,iuc.`LAST_NAME`,iuc.`PRIMARY_CONTACT_NUMBER`,
					ggd.`arrival_time`,ggd.`departure_time`,ggd.`how_to_arrive`,ggd.`pickup_location`,ggd.`pickup_time`,ggd.`drop_time`,ggd.`departure_location`,ggd.`status`
					FROM `guest_family_mapping` gfm 					
					INNER JOIN `institution_user_credential` iuc ON iuc.`INSTITUTION_USER_ID` = gfm.`family_id`
					INNER JOIN `guest_details` ggd ON ggd.`guest_id` = iuc.`INSTITUTION_USER_ID`
					WHERE gfm.`guest_id` = %s""")
		get_guest_data = (guest_id)
		cursor.execute(get_guest_query,get_guest_data)

		guest_family_data = cursor.fetchall()	

		return ({"attributes": {
		    		"status_desc": "guest_family_data",
		    		"status": "success"
		    	},
		    	"responseList":guest_family_data}), status.HTTP_200_OK


#----------------------Guest-Details---------------------#

#----------------------Delete-Family---------------------#

@name_space.route("/deleteFamily/<int:family_id>")
class deleteFamily(Resource):
	def delete(self, family_id):

		connection = connect_logindb()
		cursor = connection.cursor()

		delete_guardian_query = ("""DELETE FROM `guardian_dtls` WHERE `INSTITUTION_USER_ID_GUARDIAN` = %s """)
		delGuardianData = (family_id)
		
		cursor.execute(delete_guardian_query,delGuardianData)

		delete_guest_query = ("""DELETE FROM `guest_details` WHERE `guest_id` = %s """)
		delGuestData = (family_id)
		
		cursor.execute(delete_guest_query,delGuestData)

		delete_family_query = ("""DELETE FROM `guest_family_mapping` WHERE `family_id` = %s """)
		delFamilyData = (family_id)
		
		cursor.execute(delete_family_query,delFamilyData)

		delete_user_credential_master_query = ("""DELETE FROM `institution_user_credential_master` WHERE `INSTITUTION_USER_ID` = %s """)
		deleteUserCredentialMasterData = (family_id)
		cursor.execute(delete_user_credential_master_query,deleteUserCredentialMasterData)

		delete_user_credential_query = ("""DELETE FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s """)
		deleteUserCredentialData = (family_id)
		cursor.execute(delete_user_credential_query,deleteUserCredentialData)

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Delete Family",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Family---------------------#

#----------------------Add-Client---------------------#

@name_space.route("/addClient")
class addClient(Resource):
	@api.expect(addClient)
	def post(self):
		connection = connect_logindb()
		cursor = connection.cursor()
		details = request.get_json()

		first_name = details['first_name']
		last_name = details['last_name']
		phoneno = details['phoneno']
		event_manager_id = details['event_manager_id']
		INSTITUTION_ID = details['INSTITUTION_ID']
		today = date.today()

		insert_user_credential_query = ("""INSERT INTO `institution_user_credential`(`first_name`,`INSTITUTION_USER_NAME`,`INSTITUTION_USER_PASSWORD`,`last_name`,`PRIMARY_CONTACT_NUMBER`) 
							VALUES(%s,%s,%s,%s,%s)""")

		insert_user_credential_data = (first_name,phoneno,phoneno,last_name,phoneno)
		cursor.execute(insert_user_credential_query,insert_user_credential_data)

		INSTITUTION_USER_ID = cursor.lastrowid

		insert_user_credential_master_query = ("""INSERT INTO `institution_user_credential_master`(`INSTITUTION_ID`,`INSTITUTION_USER_ID`,`INSTITUTION_USER_ROLE`,`USER_ENROLL_DATE`,`USER_END_DATE`) 
							VALUES(%s,%s,%s,%s,%s)""")
		INSTITUTION_USER_ROLE = "S1"
		insert_user_credential_master_data = (INSTITUTION_ID,INSTITUTION_USER_ID,INSTITUTION_USER_ROLE,today,today)
		cursor.execute(insert_user_credential_master_query,insert_user_credential_master_data)

		insert_student_dtls_query = ("""INSERT INTO `student_dtls`(`INSTITUTION_ID`,`INSTITUTION_USER_ID_STUDENT`,`INSTITUTION_USER_ID_TEACHER`,`STUDENT_NAME`) 
							VALUES(%s,%s,%s,%s)""")		
		STUDENT_NAME = first_name+" "+last_name
		insert_guardian_dtls_data = (INSTITUTION_ID,INSTITUTION_USER_ID,event_manager_id,STUDENT_NAME)
		cursor.execute(insert_student_dtls_query,insert_guardian_dtls_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Add Client",
	                                "status": "success"
	                            },
								"responseList":details}), status.HTTP_200_OK

#----------------------Add-Client---------------------#

#----------------------Create-Occasion---------------------#

@name_space.route("/createOccasion")
class createOccasion(Resource):
	@api.expect(createOccasion)
	def post(self):
		connection = connect_logindb()
		cursor = connection.cursor()
		details = request.get_json()

		name = details['name']
		date = details['date']
		time = details['time']
		mens_dress_code = details['mens_dress_code']
		womens_dress_code = details['womens_dress_code']
		kid_dress_code = details['kid_dress_code']
		place = details['place']
		event_manager_id = details['event_manager_id'] #client_id
		INSTITUTION_ID = 367

		if details and "end_time" in details:
			end_time = details['end_time']
		else:
			end_time = ""

		if details and "theme_id" in details:
			theme_id = details['theme_id']
		else:
			theme_id = 0

		if details and "occasion_type" in details:
			occasion_type = details['occasion_type']

			if occasion_type == 1 or  occasion_type == 3:
				get_event_manager_details_query = ("""SELECT *
									  FROM `student_dtls` where `INSTITUTION_USER_ID_STUDENT` = %s and `INSTITUTION_ID` = %s""")
				get_event_manager_details_data = (event_manager_id,INSTITUTION_ID)
				event_anager_count = cursor.execute(get_event_manager_details_query,get_event_manager_details_data)

				if event_anager_count > 0:
					event_anager_data = cursor.fetchone()
					client_event_manager_id = event_anager_data['INSTITUTION_USER_ID_TEACHER']

					get_zoom_details_query = ("""SELECT * FROM `zoom_user_details` where `user_id` =  %s""")
					get_zoom_details_data = (client_event_manager_id)
					zoom_count = cursor.execute(get_zoom_details_query,get_zoom_details_data)

					if zoom_count > 0:
						zoom_data = cursor.fetchone()

						mailId = zoom_data.get('user_mailid')
						apiKey = zoom_data.get('zoom_api_key')

						headers = {'Content-Type':'application/json','authorization': 'Bearer ' + apiKey}
						createUrl = 'https://api.zoom.us/v2/users/{userId}/meetings'.format(userId=mailId)
						print(createUrl)
						zoom_payload = {"topic": name,
											"type": 2,
											"start_time": time,
											"duration": 40,
											"timezone": "Asia/Calcutta",
											"password": "",
											"agenda": name,
											"settings": {
												"host_video": "true",
												"participant_video": "false",
												"join_before_host": "true",
												"mute_upon_entry": "true",
												"watermark": "true",
												"use_pmi": "false",
												"approval_type": "2",
												"registration_type": "1",
												"audio": "both",
												"auto_recording": "local"
												}
										}

						print(zoom_payload)

						postRequest = requests.post(createUrl, data=json.dumps(zoom_payload), headers=headers)
						postStatus = postRequest.status_code
						print(postStatus)

						if postStatus == 201:	

							postRes = postRequest.json()
							zoom_meeting_id = postRes.get('id')
							zoom_uuid = postRes.get('uuid')
							zoom_join_url = postRes.get('join_url')
							print(zoom_join_url)
						else:
							zoom_join_url = ""
			else:
				zoom_join_url = ""
		else:
			occasion_type = 2
			zoom_join_url = ""


		if details and "event_id" in details:
			event_id = details['event_id']
		else:
			event_id = 0

		insert_ocassion_query = ("""INSERT INTO `occasion`(`occasion_name`,`occasion_date`,`occasion_time`,`end_time`,`mens_dress_code`,`womens_dress_code`,`kid_dress_code`,`place`,`event_id`,`theme_id`,`occasion_type`,`zoom_join_url`,`event_manager_id`) 
							VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

		insert_ocassion_data = (name,date,time,end_time,mens_dress_code,womens_dress_code,kid_dress_code,place,event_id,theme_id,occasion_type,zoom_join_url,event_manager_id)
		cursor.execute(insert_ocassion_query,insert_ocassion_data)

		details['occasion_id'] = cursor.lastrowid

		return ({"attributes": {"status_desc": "Create Occasion",
	                                "status": "success"
	                            },
								"responseList":details}), status.HTTP_200_OK


#----------------------Create-Occasion---------------------#

#----------------------Get-Ocassion-List---------------------#

@name_space.route("/getOccasionList/<int:user_id>/<int:INSTITUTION_ID>")	
class getOccasionList(Resource):
	def get(self,user_id,INSTITUTION_ID):

		connection = connect_logindb()
		cursor = connection.cursor()

		get_user_role_query = ("""SELECT * FROM institution_user_credential_master where `INSTITUTION_USER_ID` = %s""")
		get_user_role_data = (user_id)
		user_role_count = cursor.execute(get_user_role_query,get_user_role_data)
		if user_role_count > 0:
			user_role_data =  cursor.fetchone()				

			if user_role_data['INSTITUTION_USER_ROLE'] == 'S1':
				get_evnet_manager_query = ("""SELECT * FROM `student_dtls` where `INSTITUTION_USER_ID_STUDENT` = %s""")
				get_event_manager_data = (user_id)
				event_manager_count = cursor.execute(get_evnet_manager_query,get_event_manager_data)

				if event_manager_count > 0:
					event_manager_data =  cursor.fetchone()
					print(event_manager_data)

					get_query = ("""SELECT * FROM `occasion` where `event_manager_id` = %s and `status` = 1 ORDER BY occasion_date ASC, occasion_time
									""")
					get_data = (event_manager_data['INSTITUTION_USER_ID_STUDENT'])
					cursor.execute(get_query,get_data)
					occasion_data = cursor.fetchall()

					for key,data in enumerate(occasion_data):
						occasion_data[key]['occasion_date'] = str(data['occasion_date'])
						occasion_data[key]['last_update_ts'] = str(data['last_update_ts'])

			elif user_role_data['INSTITUTION_USER_ROLE'] == 'G1':
				get_client_query = ("""SELECT * FROM `guardian_dtls` where `INSTITUTION_USER_ID_GUARDIAN` = %s""")
				get_client_data = (user_id)
				count_client_data = cursor.execute(get_client_query,get_client_data)
				if count_client_data > 0:
					client_data = cursor.fetchone()
					get_evnet_manager_query = ("""SELECT * FROM `student_dtls` where `INSTITUTION_USER_ID_STUDENT` = %s""")
					get_event_manager_data = (client_data['INSTITUTION_USER_ID_STUDENT'])
					event_manager_count = cursor.execute(get_evnet_manager_query,get_event_manager_data)

					if event_manager_count > 0:
						event_manager_data =  cursor.fetchone()
						print(event_manager_data)

						get_query = ("""SELECT * FROM `occasion` where `event_manager_id` = %s and `status` = 1 ORDER BY occasion_date ASC, occasion_time
											""")
						get_data = (event_manager_data['INSTITUTION_USER_ID_STUDENT'])
						cursor.execute(get_query,get_data)
						occasion_data = cursor.fetchall()

						for key,data in enumerate(occasion_data):
							occasion_data[key]['occasion_date'] = str(data['occasion_date'])
							occasion_data[key]['last_update_ts'] = str(data['last_update_ts'])
				else:
					occasion_data = []

			else:
				get_client_query = ("""SELECT `INSTITUTION_USER_ID_STUDENT`
					FROM `student_dtls` WHERE `INSTITUTION_USER_ID_TEACHER` = %s and INSTITUTION_ID =%s""")
				get_client_data = (user_id,INSTITUTION_ID)
				count_client_query = cursor.execute(get_client_query,get_client_data)

				if count_client_query > 0:
					client_data = cursor.fetchone()
					get_query = ("""SELECT * FROM `occasion` where `event_manager_id` = %s and `status` = 1
												""")
					get_data = (client_data['INSTITUTION_USER_ID_STUDENT'])
					cursor.execute(get_query,get_data)
					occasion_data = cursor.fetchall()

					for key,data in enumerate(occasion_data):
						occasion_data[key]['occasion_date'] = str(data['occasion_date'])
						occasion_data[key]['last_update_ts'] = str(data['last_update_ts'])	
				else:
					occasion_data = []				
					
		else:
			occasion_data = []

		return ({"attributes": {
		    		"status_desc": "occasion_list",
		    		"status": "success"
		    	},
		    	"responseList":occasion_data}), status.HTTP_200_OK

#----------------------Get-Ocassion-List---------------------#

#----------------------Update-Occasion---------------------#

@name_space.route("/updateOcassion/<int:ocassion_id>")
class updateOcassion(Resource):
	@api.expect(ocassion_putmodel)
	def put(self, ocassion_id):

		connection = connect_logindb()
		cursor = connection.cursor()
		details = request.get_json()

		if details and "name" in details:
			name = details['name']
			update_query = ("""UPDATE `occasion` SET `occasion_name` = %s
				WHERE `ocassion_id` = %s """)
			update_data = (name,ocassion_id)
			cursor.execute(update_query,update_data)

		if details and "date" in details:
			date = details['date']
			update_query = ("""UPDATE `occasion` SET `occasion_date` = %s
				WHERE `ocassion_id` = %s """)
			update_data = (date,ocassion_id)
			cursor.execute(update_query,update_data)

		if details and "time" in details:
			time = details['time']
			update_query = ("""UPDATE `occasion` SET `occasion_time` = %s
				WHERE `ocassion_id` = %s """)
			update_data = (time,ocassion_id)
			cursor.execute(update_query,update_data)

		if details and "end_time" in details:
			end_time = details['end_time']
			update_query = ("""UPDATE `occasion` SET `end_time` = %s
				WHERE `ocassion_id` = %s """)
			update_data = (end_time,ocassion_id)
			cursor.execute(update_query,update_data)

		if details and "place" in details:
			place = details['place']
			update_query = ("""UPDATE `occasion` SET `place` = %s
				WHERE `ocassion_id` = %s """)
			update_data = (place,ocassion_id)
			cursor.execute(update_query,update_data)

		if details and "mens_dress_code" in details:
			mens_dress_code = details['mens_dress_code']
			update_query = ("""UPDATE `occasion` SET `mens_dress_code` = %s
				WHERE `ocassion_id` = %s """)
			update_data = (mens_dress_code,ocassion_id)
			cursor.execute(update_query,update_data)

		if details and "womens_dress_code" in details:
			womens_dress_code = details['womens_dress_code']
			update_query = ("""UPDATE `occasion` SET `womens_dress_code` = %s
				WHERE `ocassion_id` = %s """)
			update_data = (womens_dress_code,ocassion_id)
			cursor.execute(update_query,update_data)

		if details and "kid_dress_code" in details:
			kid_dress_code = details['kid_dress_code']
			update_query = ("""UPDATE `occasion` SET `kid_dress_code` = %s
				WHERE `ocassion_id` = %s """)
			update_data = (kid_dress_code,ocassion_id)
			cursor.execute(update_query,update_data)

		if details and "kid_dress_code" in details:
			kid_dress_code = details['kid_dress_code']
			update_query = ("""UPDATE `occasion` SET `kid_dress_code` = %s
				WHERE `ocassion_id` = %s """)
			update_data = (kid_dress_code,ocassion_id)
			cursor.execute(update_query,update_data)

		if details and "theme_id" in details:
			theme_id = details['theme_id']
			update_query = ("""UPDATE `occasion` SET `theme_id` = %s
				WHERE `ocassion_id` = %s """)
			update_data = (theme_id,ocassion_id)
			cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Occasion",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-Occasion---------------------#

#----------------------Delete-Occasion---------------------#

@name_space.route("/deleteOcassion/<int:ocassion_id>")
class deleteOcassion(Resource):
	def delete(self, ocassion_id):

		connection = connect_logindb()
		cursor = connection.cursor()

		occasion_status = 0

		update_query = ("""UPDATE `occasion` SET `status` = %s
				WHERE `ocassion_id` = %s """)
		update_data = (occasion_status,ocassion_id)
		cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Delete Occasion",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Occasion---------------------#

#----------------------Create-Event---------------------#

@name_space.route("/createEvent")
class createEvent(Resource):
	@api.expect(event_postmodel)
	def post(self):

		connection = connect_logindb()
		cursor = connection.cursor()

		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		details = request.get_json()

		event_name = details['event_name']
		event_date = details['event_date']
		event_time = details['event_time']
		event_end_date = details['event_end_date']
		event_end_time = details['event_end_time']
		location = details['location']
		if details and "city" in details:
			city = details['city']
		else:
			city = ""
		client_id = details['client_id']

		INSTITUTION_ID = 367	


		event_code = random_string(2,2)

		get_event_manager_query = ("""SELECT * FROM `student_dtls` where `INSTITUTION_USER_ID_STUDENT` = %s and INSTITUTION_ID = %s""")
		get_event_manager_data = (client_id,INSTITUTION_ID)
		event_manager_data_count = cursor.execute(get_event_manager_query,get_event_manager_data)

		if event_manager_data_count > 0:
			event_manager_data = cursor.fetchone()
			event_manager_id = event_manager_data['INSTITUTION_USER_ID_TEACHER']
		else:
			event_manager_id = 0

		insert_query = ("""INSERT INTO `event`(`event_name`,`date`,`time`,`end_date`,`end_time`,`location`,`city`,`event_code`,`client_id`,`event_manager_id`,`INSTITUTION_ID`) 
						VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
		data = (event_name,event_date,event_time,event_end_date,event_end_time,location,city,event_code,client_id,event_manager_id,INSTITUTION_ID)
		cursor_event.execute(insert_query,data)

		event_id = cursor_event.lastrowid

		details['event_code'] = event_code
		details['event_id'] = event_id

		connection_event.commit()
		cursor_event.close()

		return ({"attributes": {
					    "status_desc": "event_details",
					    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK

#----------------------Create-Event---------------------#

#----------------------Update-Event---------------------#

@name_space.route("/updateEvent/<int:event_id>")
class updateEvent(Resource):
	@api.expect(event_putmodel)
	def put(self, event_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		if details and "event_name" in details:
			event_name = details['event_name']
			update_query = ("""UPDATE `event` SET `event_name` = %s
				WHERE `event_id` = %s """)
			update_data = (event_name,event_id)
			cursor.execute(update_query,update_data)

		if details and "event_date" in details:
			event_date = details['event_date']
			update_query = ("""UPDATE `event` SET `date` = %s
				WHERE `event_id` = %s """)
			update_data = (event_date,event_id)
			cursor.execute(update_query,update_data)

		if details and "event_time" in details:
			event_time = details['event_time']
			update_query = ("""UPDATE `event` SET `time` = %s
				WHERE `event_id` = %s """)
			update_data = (event_time,event_id)
			cursor.execute(update_query,update_data)

		if details and "event_end_date" in details:
			event_end_date = details['event_end_date']
			update_query = ("""UPDATE `event` SET `end_date` = %s
				WHERE `event_id` = %s """)
			update_data = (event_end_date,event_id)
			cursor.execute(update_query,update_data)

		if details and "event_end_time" in details:
			event_end_time = details['event_end_time']
			update_query = ("""UPDATE `event` SET `end_time` = %s
				WHERE `event_id` = %s """)
			update_data = (event_end_time,event_id)
			cursor.execute(update_query,update_data)

		if details and "location" in details:
			location = details['location']
			update_query = ("""UPDATE `event` SET `location` = %s
				WHERE `event_id` = %s """)
			update_data = (location,event_id)
			cursor.execute(update_query,update_data)

		if details and "city" in details:
			city = details['city']
			update_query = ("""UPDATE `event` SET `city` = %s
				WHERE `event_id` = %s """)
			update_data = (city,event_id)
			cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {
					    "status_desc": "event_details",
					    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK

#----------------------Update-Event---------------------#	

#----------------------Theme-List---------------------#

@name_space.route("/getThemeList/<int:theme_type>")	
class getThemeList(Resource):
	def get(self,theme_type):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT * FROM `theme` where `theme_type` = %s""")
		get_data = (theme_type)
		cursor.execute(get_query,get_data)
		theme_data = cursor.fetchall()

		for key,data in enumerate(theme_data):
			theme_data[key]['last_update_ts'] = str(data['last_update_ts'])

		return ({"attributes": {
					    "status_desc": "event_details",
					    "status": "success"
				},
				"responseList":theme_data}), status.HTTP_200_OK

#----------------------Theme-List---------------------#

#----------------------Notification-List---------------------#

@name_space.route("/getNotificationList/<int:user_id>")	
class getNotificationList(Resource):
	def get(self,user_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT * FROM `app_notification` where `user_id` = %s""")
		get_data = (user_id)
		cursor.execute(get_query,get_data)
		notification_data = cursor.fetchall()

		for key,data in enumerate(notification_data):
			notification_data[key]['last_update_ts'] = str(data['last_update_ts'])

		return ({"attributes": {
					    "status_desc": "event_details",
					    "status": "success"
				},
				"responseList":notification_data}), status.HTTP_200_OK

#----------------------Notification-List---------------------#


#----------------------Create-Food---------------------#

@name_space_food.route("/createFood")
class createFood(Resource):
	@api.expect(createFood)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		name = details['name']
		date = details['date']
		time = details['time']
		if details and "end_time" in details:
			end_time = details['end_time']
		else:
			end_time = ""

		if details and "function_id" in details:
			function_id = details['function_id']
			get_function_query = ("""SELECT * FROM `function` where `function_id` = %s""")
			get_function_data = (function_id)
			function_count = cursor.execute(get_function_query,get_function_data)

			if function_count > 0:
				function_data = cursor.fetchone()
				occasion_id = function_data['occasion_id']
				event_id = function_data['event_id']
		else:
			function_id = 0
			occasion_id = 0
			event_id = 0

		place = details['place']
		event_manager_id = details['event_manager_id']

		insert_food_query = ("""INSERT INTO `food`(`food_name`,`date`,`time`,`end_time`,`place`,`occasion_id`,`event_id`,`function_id`,`event_manager_id`) 
							VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

		insert_ocassion_data = (name,date,time,end_time,place,occasion_id,event_id,function_id,event_manager_id)
		cursor.execute(insert_food_query,insert_ocassion_data)

		details['food_id'] = cursor.lastrowid

		return ({"attributes": {"status_desc": "Create Occasion",
	                                "status": "success"
	                            },
								"responseList":details}), status.HTTP_200_OK

#----------------------Create-Food---------------------#

#----------------------Create--Filtering-Food-Item---------------------#

@name_space_food.route("/createFilteringFoodItem")
class createFilteringFoodItem(Resource):
	@api.expect(createFilteringFoodItem)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		item_name = details['item_name']
		item_type = details['item_type']
		cuisine_id = details['cuisine_id']

		insert_food_query = ("""INSERT INTO `filtering_items`(`item_name`,`item_type`,`cuisine_id`) 
							VALUES(%s,%s,%s)""")

		insert_food_data = (item_name,item_type,cuisine_id)
		cursor.execute(insert_food_query,insert_food_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Create Food Items",
	                                "status": "success"
	                            },
								"responseList":details}), status.HTTP_200_OK

#----------------------Create--Filtering-Food-Item---------------------#


#----------------------Update-Filtering-Item---------------------#

@name_space_food.route("/updateFilterinItem/<int:filtering_item_id>")
class updateFilterinItem(Resource):
	@api.expect(filtering_item_putmodel)
	def put(self, filtering_item_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		if details and "item_name" in details:
			item_name = details['item_name']
			update_query = ("""UPDATE `filtering_items` SET `item_name` = %s
				WHERE `filtering_item_id` = %s """)
			update_data = (item_name,filtering_item_id)
			cursor.execute(update_query,update_data)

		if details and "item_type" in details:
			item_type = details['item_type']
			update_query = ("""UPDATE `filtering_items` SET `item_type` = %s
				WHERE `filtering_item_id` = %s """)
			update_data = (item_type,filtering_item_id)
			cursor.execute(update_query,update_data)

		if details and "cuisine_id" in details:
			cuisine_id = details['cuisine_id']
			update_query = ("""UPDATE `filtering_items` SET `cuisine_id` = %s
				WHERE `filtering_item_id` = %s """)
			update_data = (cuisine_id,filtering_item_id)
			cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Create Food Items",
	                                "status": "success"
	                            },
								"responseList":details}), status.HTTP_200_OK

#----------------------Update-Filtering-Item---------------------#

#----------------------Delete-Filter-Items---------------------#

@name_space_food.route("/deleteFilterItems/<int:filtering_item_id>")
class deleteFilterItems(Resource):
	def delete(self, filtering_item_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		delete_query = ("""DELETE FROM `filtering_items` WHERE `filtering_item_id` = %s """)
		delData = (filtering_item_id)
		
		cursor.execute(delete_query,delData)		

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Delete Filter Items",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Filter-Items---------------------#

#----------------------Update-Food---------------------#

@name_space_food.route("/updateFood/<int:food_id>")
class updateFood(Resource):
	@api.expect(food_putmodel)
	def put(self, food_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		if details and "name" in details:
			name = details['name']
			update_query = ("""UPDATE `food` SET `food_name` = %s
				WHERE `food_id` = %s """)
			update_data = (name,food_id)
			cursor.execute(update_query,update_data)

		if details and "date" in details:
			date = details['date']
			update_query = ("""UPDATE `food` SET `date` = %s
				WHERE `food_id` = %s """)
			update_data = (date,food_id)
			cursor.execute(update_query,update_data)

		if details and "time" in details:
			time = details['time']
			update_query = ("""UPDATE `food` SET `time` = %s
				WHERE `food_id` = %s """)
			update_data = (time,food_id)
			cursor.execute(update_query,update_data)

		if details and "end_time" in details:
			end_time = details['end_time']
			update_query = ("""UPDATE `food` SET `end_time` = %s
				WHERE `food_id` = %s """)
			update_data = (end_time,food_id)
			cursor.execute(update_query,update_data)

		if details and "place" in details:
			place = details['place']
			update_query = ("""UPDATE `food` SET `place` = %s
				WHERE `food_id` = %s """)
			update_data = (place,food_id)
			cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Food",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-Food---------------------#


#----------------------Delete-Food---------------------#

@name_space_food.route("/deleteFood/<int:food_id>")
class deleteFood(Resource):
	def delete(self, food_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		delete_query = ("""DELETE FROM `food` WHERE `food_id` = %s """)
		delData = (food_id)
		
		cursor.execute(delete_query,delData)

		delete_food_items_query = ("""DELETE FROM `food_items` WHERE `food_id` = %s """)
		delFoodItemData = (food_id)
		
		cursor.execute(delete_food_items_query,delFoodItemData)

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Delete Food",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Food---------------------#

#----------------------Get-Food-List---------------------#

@name_space_food.route("/getFoodList/<int:user_id>")	
class getFoodList(Resource):
	def get(self,user_id):

		connection = connect_logindb()
		cursor = connection.cursor()

		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		get_user_role_query = ("""SELECT * FROM institution_user_credential_master where `INSTITUTION_USER_ID` = %s""")
		get_user_role_data = (user_id)
		user_role_count = cursor.execute(get_user_role_query,get_user_role_data)
		if user_role_count > 0:
			user_role_data =  cursor.fetchone()
			if user_role_data['INSTITUTION_USER_ROLE'] == 'G1': 
				get_client_query = ("""SELECT * FROM `guardian_dtls` where `INSTITUTION_USER_ID_GUARDIAN` = %s""")
				get_client_data = (user_id)
				count_client_data = cursor.execute(get_client_query,get_client_data)

				if count_client_data > 0:
					client_data = cursor.fetchone()
					get_food_query = ("""SELECT * FROM `food` where `event_manager_id` = %s""")
					get_food_data = (client_data['INSTITUTION_USER_ID_STUDENT'])
					count_food = cursor_event.execute(get_food_query,get_food_data)

					if count_food > 0:
						food_data = cursor_event.fetchall()
						for key,data in enumerate(food_data):
							food_data[key]['last_update_ts'] = str(data['last_update_ts'])
					else:
						food_data = []
				else:
					food_data = []

			elif user_role_data['INSTITUTION_USER_ROLE'] == 'S1': 
				get_food_query = ("""SELECT * FROM `food` where `event_manager_id` = %s""")
				get_food_data = (user_id)
				count_food = cursor_event.execute(get_food_query,get_food_data)

				if count_food > 0:
					food_data = cursor_event.fetchall()
					for key,data in enumerate(food_data):
							food_data[key]['last_update_ts'] = str(data['last_update_ts'])
				else:
					food_data = []
		else:
			food_data = []

		return ({"attributes": {
		    		"status_desc": "food_list",
		    		"status": "success"
		    	},
		    	"responseList":food_data}), status.HTTP_200_OK


#----------------------Get-Food-List---------------------#

#----------------------Get-Food-List---------------------#

@name_space_food.route("/getFoodListByFunctionId/<int:user_id>/<int:function_id>")	
class getFoodListByFunctionId(Resource):
	def get(self,user_id,function_id):

		connection = connect_logindb()
		cursor = connection.cursor()

		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		get_user_role_query = ("""SELECT * FROM institution_user_credential_master where `INSTITUTION_USER_ID` = %s""")
		get_user_role_data = (user_id)
		user_role_count = cursor.execute(get_user_role_query,get_user_role_data)
		if user_role_count > 0:
			user_role_data =  cursor.fetchone()
			if user_role_data['INSTITUTION_USER_ROLE'] == 'G1': 
				get_client_query = ("""SELECT * FROM `guardian_dtls` where `INSTITUTION_USER_ID_GUARDIAN` = %s""")
				get_client_data = (user_id)
				count_client_data = cursor.execute(get_client_query,get_client_data)

				if count_client_data > 0:
					client_data = cursor.fetchone()
					get_food_query = ("""SELECT * FROM `food` where `event_manager_id` = %s and `function_id` = %s""")
					get_food_data = (client_data['INSTITUTION_USER_ID_STUDENT'],function_id)
					count_food = cursor_event.execute(get_food_query,get_food_data)

					if count_food > 0:
						food_data = cursor_event.fetchall()
						for key,data in enumerate(food_data):
							food_data[key]['last_update_ts'] = str(data['last_update_ts'])
					else:
						food_data = []
				else:
					food_data = []

			elif user_role_data['INSTITUTION_USER_ROLE'] == 'S1': 
				get_food_query = ("""SELECT * FROM `food` where `event_manager_id` = %s and `function_id` = %s""")
				get_food_data = (user_id,function_id)
				count_food = cursor_event.execute(get_food_query,get_food_data)

				if count_food > 0:
					food_data = cursor_event.fetchall()
					for key,data in enumerate(food_data):
							food_data[key]['last_update_ts'] = str(data['last_update_ts'])
				else:
					food_data = []
		else:
			food_data = []

		return ({"attributes": {
		    		"status_desc": "food_list",
		    		"status": "success"
		    	},
		    	"responseList":food_data}), status.HTTP_200_OK


#----------------------Get-Food-List---------------------#

#----------------------Get-Food-Item-List---------------------#

@name_space_food.route("/getFoodItemList/<int:food_id>")	
class getFoodItemList(Resource):
	def get(self,food_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		food_data = {}

		get_veg_food_items_query = ("""SELECT * FROM `food_items` where `food_id` = %s and `item_type` = 1""")
		get_veg_food_items_data = (food_id)
		count_veg_food_items = cursor.execute(get_veg_food_items_query,get_veg_food_items_data)
		if count_veg_food_items > 0:
			veg_food_data = cursor.fetchall()
			for vkey,vdata in enumerate(veg_food_data):
				veg_food_data[vkey]['last_update_ts'] = str(vdata['last_update_ts'])				
			food_data['veg'] = veg_food_data
		else:
			food_data['veg'] = []

		get_non_veg_food_items_query = ("""SELECT * FROM `food_items` where `food_id` = %s and `item_type` = 2""")
		get_non_veg_food_items_data = (food_id)
		count_non_veg_food_items = cursor.execute(get_non_veg_food_items_query,get_non_veg_food_items_data)
		if count_non_veg_food_items > 0:
			non_veg_food_data = cursor.fetchall()
			for nvkey,nvdata in enumerate(non_veg_food_data):
				non_veg_food_data[nvkey]['last_update_ts'] = str(nvdata['last_update_ts'])				
			food_data['non_veg'] = non_veg_food_data
		else:
			food_data['non_veg'] = []


		return ({"attributes": {
		    		"status_desc": "food_item_list",
		    		"status": "success"
		    	},
		    	"responseList":food_data}), status.HTTP_200_OK

#----------------------Get-Food-Item-List---------------------#


#----------------------Get-Food-Item-List---------------------#

@name_space_food.route("/getFoodItemListNew/<int:food_id>")	
class getFoodItemListNew(Resource):
	def get(self,food_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		food_data = {}

		get_side_food_items_query = ("""SELECT * FROM `food_items` where `food_id` = %s and `item_type` = 6 ORDER BY cuisine asc""")
		get_side_food_items_data = (food_id)
		count_side_food_items = cursor.execute(get_side_food_items_query,get_side_food_items_data)
		if count_side_food_items > 0:
			side_food_data = cursor.fetchall()
			for sskey,ssdata in enumerate(side_food_data):
				side_food_data[sskey]['last_update_ts'] = str(ssdata['last_update_ts'])				
			food_data['snacks_sides'] = side_food_data
		else:
			food_data['snacks_sides'] = []

		get_live_food_items_query = ("""SELECT * FROM `food_items` where `food_id` = %s and `item_type` = 5 ORDER BY cuisine asc""")
		get_live_food_items_data = (food_id)
		count_live_food_items = cursor.execute(get_live_food_items_query,get_live_food_items_data)
		if count_live_food_items > 0:
			live_food_data = cursor.fetchall()
			for lkey,ldata in enumerate(live_food_data):
				live_food_data[lkey]['last_update_ts'] = str(ldata['last_update_ts'])				
			food_data['live'] = live_food_data
		else:
			food_data['live'] = []

		get_veg_food_items_query = ("""SELECT * FROM `food_items` where `food_id` = %s and `item_type` = 1 ORDER BY cuisine asc""")
		get_veg_food_items_data = (food_id)
		count_veg_food_items = cursor.execute(get_veg_food_items_query,get_veg_food_items_data)
		if count_veg_food_items > 0:
			veg_food_data = cursor.fetchall()
			for vkey,vdata in enumerate(veg_food_data):
				veg_food_data[vkey]['last_update_ts'] = str(vdata['last_update_ts'])				
			food_data['Soup'] = veg_food_data
		else:
			food_data['Soup'] = []

		get_non_veg_food_items_query = ("""SELECT * FROM `food_items` where `food_id` = %s and `item_type` = 2 ORDER BY cuisine asc""")
		get_non_veg_food_items_data = (food_id)
		count_non_veg_food_items = cursor.execute(get_non_veg_food_items_query,get_non_veg_food_items_data)
		if count_non_veg_food_items > 0:
			non_veg_food_data = cursor.fetchall()
			for nvkey,nvdata in enumerate(non_veg_food_data):
				non_veg_food_data[nvkey]['last_update_ts'] = str(nvdata['last_update_ts'])				
			food_data['Starters'] = non_veg_food_data
		else:
			food_data['Starters'] = []

		get_main_course_food_items_query = ("""SELECT * FROM `food_items` where `food_id` = %s and `item_type` = 3 ORDER BY cuisine asc""")
		get_main_course_food_items_data = (food_id)
		count_main_course_food_items = cursor.execute(get_main_course_food_items_query,get_main_course_food_items_data)
		if count_main_course_food_items > 0:
			main_course_food_data = cursor.fetchall()
			for mckey,mcdata in enumerate(main_course_food_data):
				main_course_food_data[mckey]['last_update_ts'] = str(mcdata['last_update_ts'])				
			food_data['Main_course'] = main_course_food_data
		else:
			food_data['Main_course'] = []

		get_deserts_food_items_query = ("""SELECT * FROM `food_items` where `food_id` = %s and `item_type` = 4 ORDER BY cuisine asc""")
		get_deserts_food_items_data = (food_id)
		count_deserts_food_items = cursor.execute(get_deserts_food_items_query,get_deserts_food_items_data)
		if count_deserts_food_items > 0:
			deserts_food_data = cursor.fetchall()
			for dkey,ddata in enumerate(deserts_food_data):
				deserts_food_data[dkey]['last_update_ts'] = str(ddata['last_update_ts'])				
			food_data['Deserts'] = deserts_food_data
		else:
			food_data['Deserts'] = []


		return ({"attributes": {
		    		"status_desc": "food_item_list",
		    		"status": "success"
		    	},
		    	"responseList":food_data}), status.HTTP_200_OK

#----------------------Get-Food-Item-List---------------------#

#----------------------Get-Food-Item-List-By-Meal-Type-And-Cuisine--------------------#

@name_space_food.route("/getFoodItemListByMealTypeAndCuisine/<int:item_type>/<int:cuisine_id>")	
class getFoodItemListByMealTypeAndCuisine(Resource):
	def get(self,item_type,cuisine_id):

		connection = mysql_connection()
		cursor = connection.cursor()		

		get_food_items_query = ("""SELECT * FROM `filtering_items` where `item_type` = %s and `cuisine_id` = %s""")
		get_food_items_data = (item_type,cuisine_id)
		count_food_items = cursor.execute(get_food_items_query,get_food_items_data)
		if count_food_items > 0:
			food_data = cursor.fetchall()
			for key,data in enumerate(food_data):
				food_data[key]['last_update_ts'] = str(data['last_update_ts'])
				get_cuisine_query = ("""SELECT * FROM `cuisine` where `cuisine_id` = %s""")
				get_cuisine_data = (data['cuisine_id'])
				cuisine_count =  cursor.execute(get_cuisine_query,get_cuisine_data)

				if cuisine_count > 0:
					cuisine_data = cursor.fetchone()
					food_data[key]['cuisine'] = cuisine_data['cuisine_name']
				else:
					food_data[key]['cuisine'] = ""
		else:
			food_data = []

		return ({"attributes": {
		    		"status_desc": "food_item_list",
		    		"status": "success"
		    	},
		    	"responseList":food_data}), status.HTTP_200_OK

#----------------------Get-Food-Item-List-By-Meal-Type-And-Cuisine--------------------#

#----------------------Create-Food---------------------#

@name_space_food.route("/createFoodItem")
class createFoodItem(Resource):
	@api.expect(createFoodItem)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		item_name = details['item_name']
		item_type = details['item_type']
		food_id = details['food_id']

		if details and "cuisine" in details:
			cuisine = details['cuisine']
		else:
			cuisine = ""

		if details and "cuisine_id" in details:
			cuisine_id = details['cuisine_id']
		else:
			cuisine_id = 0

		event_manager_id = details['event_manager_id']
		
		insert_food_query = ("""INSERT INTO `food_items`(`item_name`,`item_type`,`cuisine`,`cuisine_id`,`food_id`,`event_manager_id`) 
							VALUES(%s,%s,%s,%s,%s,%s)""")

		insert_food_data = (item_name,item_type,cuisine,cuisine_id,food_id,event_manager_id)
		cursor.execute(insert_food_query,insert_food_data)

		details['food_items_id'] = cursor.lastrowid

		return ({"attributes": {"status_desc": "Create Food Item",
	                                "status": "success"
	                            },
								"responseList":details}), status.HTTP_200_OK

#----------------------Create-Food---------------------#

#----------------------Create-Food---------------------#

@name_space_food.route("/createMultipleFoodItem")
class createMultipleFoodItem(Resource):
	@api.expect(createMultipleFoodItem)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		item_names = details.get('item_name',[])
		
		item_type = details['item_type']
		food_id = details['food_id']

		if details and "cuisine" in details:
			cuisine = details['cuisine']
		else:
			cuisine = ""

		if details and "cuisine_id" in details:
			cuisine_id = details['cuisine_id']
		else:
			cuisine_id = 0

		event_manager_id = details['event_manager_id']

		for key,item_name in enumerate(item_names):	
		
			insert_food_query = ("""INSERT INTO `food_items`(`item_name`,`item_type`,`cuisine`,`cuisine_id`,`food_id`,`event_manager_id`) 
								VALUES(%s,%s,%s,%s,%s,%s)""")

			insert_food_data = (item_name,item_type,cuisine,cuisine_id,food_id,event_manager_id)
			cursor.execute(insert_food_query,insert_food_data)
		

		return ({"attributes": {"status_desc": "Create Food Item",
	                                "status": "success"
	                            },
								"responseList":details}), status.HTTP_200_OK

#----------------------Create-Food---------------------#

#----------------------Update-Food---------------------#

@name_space_food.route("/updateFoodItem/<int:food_items_id>")
class updateFoodItem(Resource):
	@api.expect(food_item_putmodel)
	def put(self, food_items_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		if details and "item_name" in details:
			item_name = details['item_name']
			update_query = ("""UPDATE `food_items` SET `item_name` = %s
				WHERE `food_items_id` = %s """)
			update_data = (item_name,food_items_id)
			cursor.execute(update_query,update_data)

		if details and "item_type" in details:
			item_type = details['item_type']
			update_query = ("""UPDATE `food_items` SET `item_type` = %s
				WHERE `food_items_id` = %s """)
			update_data = (item_type,food_items_id)
			cursor.execute(update_query,update_data)		

		if details and "cuisine" in details:
			cuisine = details['cuisine']
			update_query = ("""UPDATE `food_items` SET `cuisine` = %s
				WHERE `food_items_id` = %s """)
			update_data = (cuisine,food_items_id)
			cursor.execute(update_query,update_data)

		if details and "cuisine_id" in details:
			cuisine_id = details['cuisine_id']
			update_query = ("""UPDATE `food_items` SET `cuisine_id` = %s
				WHERE `food_items_id` = %s """)
			update_data = (cuisine_id,food_items_id)
			cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Food Items",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-Food---------------------#

#----------------------Delete-Food-Item---------------------#

@name_space_food.route("/deleteFoodItems/<int:food_items_id>")
class deleteFoodItems(Resource):
	def delete(self, food_items_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		delete_query = ("""DELETE FROM `food_items` WHERE `food_items_id` = %s """)
		delData = (food_items_id)
		
		cursor.execute(delete_query,delData)

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Delete Food",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Food-Item---------------------#

#----------------------Create-Cuisine---------------------#

@name_space_food.route("/createcuisine")
class createcuisine(Resource):
	@api.expect(createcuisine)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		cuisine_name = details['cuisine_name']			
		
		insert_query = ("""INSERT INTO `cuisine`(`cuisine_name`) 
							VALUES(%s)""")

		insert_data = (cuisine_name)
		cursor.execute(insert_query,insert_data)

		details['food_items_id'] = cursor.lastrowid

		return ({"attributes": {"status_desc": "Create cuisine",
	                                "status": "success"
	                            },
								"responseList":details}), status.HTTP_200_OK

#----------------------Create-Cuisine---------------------#

#----------------------Update-Cuisine---------------------#

@name_space_food.route("/updateCuisine/<int:cuisine_id>")
class updateFoodItem(Resource):
	@api.expect(cuisine_putmodel)
	def put(self, cuisine_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		if details and "cuisine_name" in details:
			cuisine_name = details['cuisine_name']
			update_query = ("""UPDATE `cuisine` SET `cuisine_name` = %s
				WHERE `cuisine_id` = %s """)
			update_data = (cuisine_name,cuisine_id)
			cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Update cuisine",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Get-Cuisinelist---------------------#

@name_space_food.route("/cuisineList")	
class cuisineList(Resource):
	def get(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT * FROM `cuisine`""")
		cuisine_count  = cursor.execute(get_query)
		if cuisine_count > 0:
			cuisine_data = 	cursor.fetchall()
			for key,data in enumerate(cuisine_data):
				cuisine_data[key]['last_update_ts'] = str(data['last_update_ts'])
		else:
			cuisine_data = []

		return ({"attributes": {
				    		"status_desc": "device_token_details",
				    		"status": "success"
				    	},
				    	"responseList":cuisine_data}), status.HTTP_200_OK

#----------------------Get-Cuisinelist---------------------#

#----------------------Save-Device-Token---------------------#
@name_space.route("/saveDeviceToken")	
class saveDeviceToken(Resource):
	@api.expect(devicetoken_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()		

		device_token_query = ("""SELECT `device_type`,`device_token`
				FROM `devices` WHERE `user_id` = %s and device_type = %s""")
		deviceData = (details['user_id'],details['device_type'])
		count_device_token = cursor.execute(device_token_query,deviceData)

		if count_device_token >0 :
			update_query = ("""UPDATE `devices` SET `device_token` = %s
							WHERE `user_id` = %s and `device_type` = %s""")
			update_data = (details['device_token'],details['user_id'],details['device_type'])
			cursor.execute(update_query,update_data)
		else:
			insert_query = ("""INSERT INTO `devices`(`device_type`,`device_token`,`user_id`) 
							VALUES(%s,%s,%s)""")

			insert_data = (details['device_type'],details['device_token'],details['user_id'])
			cursor.execute(insert_query,insert_data)

		return ({"attributes": {
				    		"status_desc": "device_token_details",
				    		"status": "success"
				    	},
				    	"responseList":details}), status.HTTP_200_OK

#----------------------Save-Device-Token---------------------#

#----------------------Get-Event-Manager-Dashboard---------------------#

@name_space_dashboard.route("/getEventManagerDashboard/<int:event_manager_id>")	
class getEventManagerDashboard(Resource):
	def get(self,event_manager_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		connection_login = connect_logindb()
		cursor_login = connection_login.cursor()

		today = date.today()
		#filter_date = today.strftime("%d-%m-%Y")
		filter_date = today.strftime("%Y-%m-%d")
		
		complete_event_count = 5
		INSTITUTION_ID = 367

		get_client_count_query = ("""SELECT count(*) as client_count
				FROM `student_dtls` where `INSTITUTION_ID` = %s and `INSTITUTION_USER_ID_TEACHER` = %s """)
		get_client_count_data = (INSTITUTION_ID,event_manager_id)
		count_client_count = cursor_login.execute(get_client_count_query,get_client_count_data)
		if count_client_count > 0:
			client_data =  cursor_login.fetchone()
			client_count = client_data['client_count']
		else:
			client_count = 0

		get_group_count_query = ("""SELECT count(*) as group_count
				FROM `group_master` where `INSTITUTION_ID` = %s """)
		get_group_count_data = (INSTITUTION_ID)
		count_group_count = cursor_login.execute(get_group_count_query,get_group_count_data)

		if count_group_count > 0:
			group_data = cursor_login.fetchone()
			group_count = group_data['group_count']
		else:
			group_count = 0

		get_upcoming_event_count_query = ("""SELECT count(*) as upcoming_event_count
				FROM `event` where `event_manager_id` = %s and `date` > %s""")
		get_upcoming_event_count_data = (event_manager_id,filter_date)
		count_upcoming_event_count = cursor.execute(get_upcoming_event_count_query,get_upcoming_event_count_data)

		if count_upcoming_event_count > 0:
			upcoming_event_data = cursor.fetchone()
			upcoming_event_count = upcoming_event_data['upcoming_event_count']
		else:
			upcoming_event_count = 0

		get_ongoing_event_count_query = ("""SELECT count(*) as ongoing_event_count
				FROM `event` where `event_manager_id` = %s and `date` <= %s and `end_date` >= %s""")
		get_ongoing_event_count_data = (event_manager_id,filter_date,filter_date)
		count_ongoing_event_count = cursor.execute(get_ongoing_event_count_query,get_ongoing_event_count_data)

		if count_ongoing_event_count > 0:
			ongoing_event_data = cursor.fetchone()
			ongoing_event_count = ongoing_event_data['ongoing_event_count']
		else:
			ongoing_event_count = 0


		get_completed_event_count_query = ("""SELECT count(*) as completed_event_count
				FROM `event` where `event_manager_id` = %s and `end_date` < %s""")
		get_completed_event_count_data = (event_manager_id,filter_date)
		count_completed_event_count = cursor.execute(get_completed_event_count_query,get_completed_event_count_data)

		if count_completed_event_count > 0:
			completed_event_data = cursor.fetchone()
			completed_event_count = completed_event_data['completed_event_count']
		else:
			completed_event_count = 0

		upcomming_event_list_query = ("""SELECT *
				FROM `event`  where `event_manager_id` = %s and `date` >= %s ORDER BY date ASC""")	
		upcomming_event_list_data = (event_manager_id,filter_date)	
		upcomming_event_count = cursor.execute(upcomming_event_list_query,upcomming_event_list_data)

		if upcomming_event_count > 0:
			upcomming_event_data = cursor.fetchall()
			for key,data in enumerate(upcomming_event_data):
				upcomming_event_data[key]['date'] = str(data['date'])
				upcomming_event_data[key]['end_date'] = str(data['end_date'])
				upcomming_event_data[key]['last_update_ts'] = str(data['last_update_ts'])
		else:
			upcomming_event_data = []

		return ({"attributes": {
				    		"status_desc": "event_manager_dashboard",
				    		"status": "success"
				    	},
				    	"responseList":{"client_count":client_count,"group_count":group_count,"upcoming_event_count":upcoming_event_count,"ongoing_event_count":ongoing_event_count,"completed_event_count":completed_event_count,"upcomming_event_data":upcomming_event_data}}), status.HTTP_200_OK


#----------------------Get-Event-Manager-Dashboard---------------------#

#----------------------Get-Client-Dashboard---------------------#

@name_space_dashboard.route("/getClientDashboard/<int:client_id>")	
class getClientDashboard(Resource):
	def get(self,client_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		connection_login = connect_logindb()
		cursor_login = connection_login.cursor()			
		
		completed_occasion_count = 3

		today = date.today()
		filter_date = today.strftime("%Y-%m-%d")	

		get_guest_count_query = ("""SELECT count(*) as guest_count
				FROM `guest_details` where client_id = %s""")
		get_guest_count_data = (client_id)
		count_guest_count = cursor_login.execute(get_guest_count_query,get_guest_count_data)

		if count_guest_count > 0:
			guest_data = cursor_login.fetchone()
			guest_count = guest_data['guest_count']
		else:
			guest_count = 0

		get_upcoming_event_count_query = ("""SELECT count(*) as upcoming_event_count
				FROM `event` where `client_id` = %s and `date` > %s""")
		get_upcoming_event_count_data = (client_id,filter_date)
		count_upcoming_event_count = cursor.execute(get_upcoming_event_count_query,get_upcoming_event_count_data)

		if count_upcoming_event_count > 0:
			upcoming_event_data = cursor.fetchone()
			upcoming_event_count = upcoming_event_data['upcoming_event_count']
		else:
			upcoming_event_count = 0

		get_completed_event_count_query = ("""SELECT count(*) as completed_event_count
				FROM `event` where `client_id` = %s and `end_date` < %s""")
		get_completed_event_count_data = (client_id,filter_date)
		count_completed_event_count = cursor.execute(get_completed_event_count_query,get_completed_event_count_data)

		if count_completed_event_count > 0:
			completed_event_data = cursor.fetchone()
			completed_event_count = completed_event_data['completed_event_count']
		else:
			completed_event_count = 0

		get_completed_occasion_count_query = ("""SELECT count(*) as completed_occasion_count
				FROM `occasion` where `event_manager_id` = %s and `occasion_date` < %s and `status` = 1 """)
		get_completed_occasion_count_data = (client_id,filter_date)
		count_completed_occasion_count = cursor_login.execute(get_completed_occasion_count_query,get_completed_occasion_count_data)

		if count_completed_occasion_count > 0:
			completed_occasion_data = cursor_login.fetchone()
			completed_occasion_count = completed_occasion_data['completed_occasion_count']
		else:
			completed_occasion_count = 0

		get_ongoing_occasion_count_query = ("""SELECT count(*) as ongoing_occasion_count
				FROM `occasion` where `event_manager_id` = %s and `occasion_date` = %s and `status` = 1""")
		get_ongoing_occasion_count_data = (client_id,filter_date)
		count_ongoing_occasion_count = cursor_login.execute(get_ongoing_occasion_count_query,get_ongoing_occasion_count_data)

		if count_ongoing_occasion_count > 0:
			ongoing_occasion_data = cursor_login.fetchone()
			ongoing_occasion_count = ongoing_occasion_data['ongoing_occasion_count']
		else:
			ongoing_occasion_count = 0

		get_upcomming_occasion_list_query = ("""SELECT *
				FROM `occasion` where `event_manager_id` = %s and `occasion_date` >=  %s and `status` = 1 ORDER BY occasion_date ASC""")	
		get_upcomming_occasion_list_data = (client_id,filter_date)					
		upcomming_occasion_count = cursor_login.execute(get_upcomming_occasion_list_query,get_upcomming_occasion_list_data)

		if upcomming_occasion_count > 0:
			upcomming_occasion_data = cursor_login.fetchall()
			for key,data in enumerate(upcomming_occasion_data):
				upcomming_occasion_data[key]['occasion_date'] = str(data['occasion_date'])
				upcomming_occasion_data[key]['last_update_ts'] = str(data['last_update_ts'])
		else:
			upcomming_occasion_data = []

		get_upcomming_function_list_query = ("""SELECT *
				FROM `function` where `evant_manger_id` = %s and `function_date` >=  %s and `status` = 1 ORDER BY function_date ASC""")	
		get_upcomming_function_list_data = (client_id,filter_date)					
		upcomming_function_count = cursor.execute(get_upcomming_function_list_query,get_upcomming_function_list_data)

		if upcomming_function_count > 0:
			upcomming_function_data = cursor.fetchall()
			for key,data in enumerate(upcomming_function_data):
				upcomming_function_data[key]['function_date'] = str(data['function_date'])
				upcomming_function_data[key]['last_update_ts'] = str(data['last_update_ts'])
		else:
			upcomming_function_data = []

		return ({"attributes": {
				    		"status_desc": "client_dashboard",
				    		"status": "success"
				    	},
				    	"responseList":{"guest_count":guest_count,"upcoming_event_count":upcoming_event_count,"ongoing_occasion_count":ongoing_occasion_count,"completed_event_count":completed_event_count,"completed_occasion_count":completed_occasion_count,"upcomming_occasion_list":upcomming_occasion_data,"upcomming_function_data":upcomming_function_data}}), status.HTTP_200_OK


#----------------------Get-Client-Dashboard---------------------#

#----------------------Get-Guest-Dashboard---------------------#

@name_space_dashboard.route("/getGuestDashboard/<int:guest_id>")	
class getGuestDashboard(Resource):
	def get(self,guest_id):

		connection = connect_logindb()
		cursor = connection.cursor()

		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		today = date.today()
		#filter_date = today.strftime("%d-%m-%Y")
		filter_date = today.strftime("%Y-%m-%d")	

		get_client_query = ("""SELECT *
				FROM `guest_details` where guest_id = %s""")
		get_client_data = (guest_id)
		client_count = cursor.execute(get_client_query,get_client_data)

		if client_count > 0:
			client_data = cursor.fetchone()
			client_id = client_data['client_id']	
		else:
			client_id = 0

		if client_id > 0:
			get_event_query = ("""SELECT *
				FROM `event` where `client_id` = %s and `end_date`  >= %s""")
			get_event_data = (client_id,filter_date)
			event_count = cursor_event.execute(get_event_query,get_event_data)

			if event_count > 0:
				event_data = cursor_event.fetchone()
				event_id = event_data['event_id']
				event_name = event_data['event_name']
				event_date = str(event_data['date'])
				time = event_data['time']
				end_date = str(event_data['end_date'])
				end_time = event_data['end_time']
				location =  event_data['location']
				city = event_data['city']
				event_code = event_data['event_code']
			else:
				event_name = ""
				event_id = 0
				event_date = ''
				time = ''
				end_date = ''
				end_time = ''
				location = ''
				city = ''
				event_code = ''

			get_guset_list_query = ("""SELECT count(*) as guest_count
				FROM `guest_details` where client_id = %s""")
			get_guest_list_data = (client_id)
			guest_list_count = cursor.execute(get_guset_list_query,get_guest_list_data)
			if guest_list_count > 0:
				guest_data = cursor.fetchone()
				total_guest_attend = guest_data['guest_count']
			else:
				total_guest_attend = 0

			get_completed_occasion_count_query = ("""SELECT count(*) as completed_occasion_count
				FROM `occasion` where `event_manager_id` = %s and `occasion_date` < %s and `status` = 1""")
			get_completed_occasion_count_data = (client_id,filter_date)
			count_completed_occasion_count = cursor.execute(get_completed_occasion_count_query,get_completed_occasion_count_data)

			if count_completed_occasion_count > 0:
				completed_occasion_data = cursor.fetchone()
				completed_occasion_count = completed_occasion_data['completed_occasion_count']
			else:
				completed_occasion_count = 0


			get_ongoing_occasion_count_query = ("""SELECT count(*) as ongoing_occasion_count
				FROM `occasion` where `event_manager_id` = %s and `occasion_date` = %s and `status` = 1""")
			get_ongoing_occasion_count_data = (client_id,filter_date)
			count_ongoing_occasion_count = cursor.execute(get_ongoing_occasion_count_query,get_ongoing_occasion_count_data)

			if count_ongoing_occasion_count > 0:
				ongoing_occasion_data = cursor.fetchone()
				ongoing_occasion_count = ongoing_occasion_data['ongoing_occasion_count']
			else:
				ongoing_occasion_count = 0

			get_completed_function_count_query = ("""SELECT count(*) as completed_function_count
				FROM `function` where `evant_manger_id` = %s and `function_date` < %s and `status` = 1""")
			get_completed_function_count_data = (client_id,filter_date)
			count_completed_function_count = cursor_event.execute(get_completed_function_count_query,get_completed_function_count_data)

			if count_completed_function_count > 0:
				completed_function_data = cursor_event.fetchone()
				completed_function_count = completed_function_data['completed_function_count']
			else:
				completed_function_count = 0

			get_ongoing_function_count_query = ("""SELECT count(*) as ongoing_function_count
				FROM `function` where `evant_manger_id` = %s and `function_date` = %s and `status` = 1""")
			get_ongoing_function_count_data = (client_id,filter_date)
			count_ongoing_function_count = cursor_event.execute(get_ongoing_function_count_query,get_ongoing_function_count_data)

			if count_ongoing_function_count > 0:
				ongoing_function_data = cursor_event.fetchone()
				ongoing_function_count = ongoing_function_data['ongoing_function_count']
			else:
				ongoing_function_count = 0

			get_upcomming_occasion_list_query = ("""SELECT count(*) as upcomming_occasion_count
				FROM `occasion` where `event_manager_id` = %s and `occasion_date` > %s and `status` = 1""")
			get_upcomming_occasion_list_data = (client_id,filter_date)				
			count_upcomming_occasion_count = cursor.execute(get_upcomming_occasion_list_query,get_upcomming_occasion_list_data)

			if count_upcomming_occasion_count > 0:
				upcomming_occasion_data = cursor.fetchone()
				upcomming_occasion_count = upcomming_occasion_data['upcomming_occasion_count']					
			else:
				upcomming_occasion_count = 0

			get_upcomming_function_query = ("""SELECT count(*) as upcomming_function_count
					FROM `function`  where `evant_manger_id` = %s and `function_date` >= %s and `status` = 1""")
			upcomming_function_data = (client_id,filter_date)	

			count_upcomming_function_count = cursor_event.execute(get_upcomming_function_query,upcomming_function_data)

			if count_upcomming_function_count > 0:
				upcomming_function = cursor_event.fetchone()
				upcomming_function_count = upcomming_function['upcomming_function_count']
			else:
				upcomming_function_count = 0

			occasion_data = []

			get_assign_function_list = ("""SELECT f.`occasion_id`
				FROM `function_guest_mapping` fgm
				INNER JOIN `function` f ON f.`function_id` = fgm.`function_id`
				where `guest_id` = %s GROUP BY f.`occasion_id`""")
			get_assign_function_data = (guest_id)
			assign_function_count = cursor_event.execute(get_assign_function_list,get_assign_function_data)

			if assign_function_count > 0:
				assign_function = cursor_event.fetchall()
				for akey,adata in enumerate(assign_function):
					get_occasion_list_query = ("""SELECT *
						FROM `occasion` where `occasion_date` >= %s and `status` = 1  and `ocassion_id` = %s ORDER BY occasion_date ASC,occasion_time""")
					get_occasion_list_data = (filter_date,adata['occasion_id'])				
					occasion_count = cursor.execute(get_occasion_list_query,get_occasion_list_data)

					if occasion_count > 0:
						assign_occasion_data = cursor.fetchall()
						for key,data in enumerate(assign_occasion_data):					
							assign_occasion_data[key]['occasion_date'] = str(data['occasion_date'])
							assign_occasion_data[key]['last_update_ts'] = str(data['last_update_ts'])

							get_function_query = ("""SELECT count(*) as function_count FROM `function` where `evant_manger_id` = %s and `occasion_id` = %s and `status` = 1""")
							get_function_data = (client_id,data['ocassion_id'])
							get_function_count = cursor_event.execute(get_function_query,get_function_data)

							if get_function_count > 0:
								function_data = cursor_event.fetchone()
								assign_occasion_data[key]['function_count'] = function_data['function_count']
							else:
								assign_occasion_data[key]['function_count'] = 0
							occasion_data.append(assign_occasion_data[key])
					else:
						occasion_data = []
			else:
				occasion_data = []			

			'''for nokey,noadata in enumerate(occasion_data):
				if occasion_data[0]['ocassion_id'] == noadata['ocassion_id']:
					print(noadata['ocassion_id'])
				else:
					new_occasion_data.append(occasion_data[nokey])'''

			'''get_upcomming_function_list_query = ("""SELECT *
					FROM `function`  where `evant_manger_id` = %s and `function_date` >= %s and `status` = 1  ORDER BY function_date ASC""")	
			get_upcomming_function_data = (client_id,filter_date)				
			upcomming_function_count = cursor_event.execute(get_upcomming_function_list_query,get_upcomming_function_data)

			if upcomming_function_count > 0:
				print(cursor_event._last_executed)
				upcomming_function_data = cursor_event.fetchall()
				print
				for ukey,udata in enumerate(upcomming_function_data):
					upcomming_function_data[ukey]['function_date'] = str(udata['function_date'])
					upcomming_function_data[ukey]['last_update_ts'] = str(udata['last_update_ts'])
			else:
				upcomming_function_data = []'''

			get_upcomming_function_list_query = ("""SELECT f.*
					FROM `function_guest_mapping` fgm 
					INNER JOIN `function` f ON f.`function_id` = fgm.`function_id`
					where fgm.`guest_id` = %s and f.`function_date` >= %s and f.`status` = 1  ORDER BY f.`function_date` ASC,f.`function_time`""")	
			get_upcomming_function_data = (guest_id,filter_date)				
			upcomming_function_count = cursor_event.execute(get_upcomming_function_list_query,get_upcomming_function_data)

			if upcomming_function_count > 0:
				print(cursor_event._last_executed)
				upcomming_function_data = cursor_event.fetchall()
				print
				for ukey,udata in enumerate(upcomming_function_data):
					upcomming_function_data[ukey]['function_date'] = str(udata['function_date'])
					upcomming_function_data[ukey]['last_update_ts'] = str(udata['last_update_ts'])
			else:
				upcomming_function_data = []
		else:
			event_name = ""
			total_guest_attend = 0
			client_id= client_id

		
			completed_occasion_count = 0	
			completed_function_count = 0
			ongoing_occasion_count = 0
			ongoing_function_count = 0
			upcomming_occasion_count = 0
			upcomming_function_count = 0
			occasion_data = []	
			upcomming_function_data = []
			client_id = 0
			event_id = 0
			event_date = ''
			time = ''
			end_date = ''
			end_time = ''
			location = ''
			city = ''
			event_code = ''


		print(upcomming_function_data)

		return ({"attributes": {
				    		"status_desc": "Guest_dashboard",
				    		"status": "success"
				    	},
				    	"responseList":{"event_name":event_name,"event_id":event_id,"event_date":event_date,"time":time,"end_date":end_date,"end_time":end_time,"location":location,"city":city,"event_code":event_code,"client_id":client_id,"total_guest_attend":total_guest_attend,"completed_occasion_count":completed_occasion_count,"ongoing_occasion_count":ongoing_occasion_count,"completed_function_count":completed_function_count,"ongoing_function_count":ongoing_function_count,"upcomming_occasion_count":upcomming_occasion_count,"upcomming_function_count":upcomming_function_count,"upcomming_occasion_list":occasion_data,"upcomming_function_list":upcomming_function_data}}), status.HTTP_200_OK

#----------------------Get-Guest-Dashboard---------------------#

def checkIfDuplicates_1(listOfElems):
    ''' Check if given list contains any duplicates '''
    if len(listOfElems) == len(set(listOfElems)):
        return False
    else:
        return True

def get_unique(some_array, seen=None):
    if seen is None:
        seen = set()
    for i in some_array:
        if isinstance(i, list):
            seen.union(get_unique(i, seen))
        else:
            seen.add(i)
    return seen

#----------------------Get-City-List---------------------#
@name_space.route("/getCityList")	
class getCityList(Resource):
	def get(self):

		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		get_city_query = ("""SELECT * FROM `city_master` """)
		cursor_event.execute(get_city_query)

		city_data =  cursor_event.fetchall()

		for key,data in enumerate(city_data):
			city_data[key]['last_update_ts'] = str(data['last_update_ts'])

		return ({"attributes": {
				    		"status_desc": "city_list",
				    		"status": "success"
				    	},
				    	"responseList":city_data}), status.HTTP_200_OK



#----------------------Get-City-List---------------------#

#----------------------Get-Airport-List---------------------#
@name_space.route("/getAirportList")	
class getAirportList(Resource):
	def get(self):

		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		get_airport_query = ("""SELECT * FROM `airport_master` """)
		cursor_event.execute(get_airport_query)

		airport_data =  cursor_event.fetchall()

		for key,data in enumerate(airport_data):
			airport_data[key]['last_update_ts'] = str(data['last_update_ts'])

		return ({"attributes": {
				    		"status_desc": "airport_list",
				    		"status": "success"
				    	},
				    	"responseList":airport_data}), status.HTTP_200_OK


#----------------------Get-Airport-List---------------------#

#----------------------Get-Railway-List---------------------#
@name_space.route("/getRailwayList")	
class getRailwayList(Resource):
	def get(self):

		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		get_railway_query = ("""SELECT * FROM `railway_master` """)
		cursor_event.execute(get_railway_query)

		railway_data =  cursor_event.fetchall()

		for key,data in enumerate(railway_data):
			railway_data[key]['last_update_ts'] = str(data['last_update_ts'])

		return ({"attributes": {
				    		"status_desc": "railway_list",
				    		"status": "success"
				    	},
				    	"responseList":railway_data}), status.HTTP_200_OK


#----------------------Get-Railway-List---------------------#

#----------------------Get-Event-List---------------------#
@name_space.route("/getEventList/<int:flag>/<int:user_id>")	
class getEventList(Resource):
	def get(self,flag,user_id):

		connection = connect_logindb()
		cursor = connection.cursor()

		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		today = date.today()
		filter_date = today.strftime("%Y-%m-%d")	

		print(filter_date)

		get_user_role_query = ("""SELECT * FROM institution_user_credential_master where `INSTITUTION_USER_ID` = %s""")
		get_user_role_data = (user_id)
		user_role_count = cursor.execute(get_user_role_query,get_user_role_data)

		if user_role_count > 0:
			user_role_data =  cursor.fetchone()
			if user_role_data['INSTITUTION_USER_ROLE'] == 'G1':
				print('hiihg')
				get_client_query = ("""SELECT * FROM `guardian_dtls` where `INSTITUTION_USER_ID_GUARDIAN` = %s""")
				get_client_data = (user_id)
				count_client_data = cursor.execute(get_client_query,get_client_data)

				if count_client_data > 0:
					client_data = cursor.fetchone()
					if flag == 0:
						get_event_query = ("""SELECT * FROM `event` where `client_id` = %s ORDER BY `date` ASC, `time`""")
						get_event_data = (client_data['INSTITUTION_USER_ID_STUDENT'])
					if flag == 1:
						get_event_query = ("""SELECT * FROM `event` where `client_id` = %s and `date` > %s ORDER BY `date` ASC, `time` """)
						get_event_data = (client_data['INSTITUTION_USER_ID_STUDENT'],filter_date)
					if flag == 2:
						get_event_query = ("""SELECT * FROM `event` where `client_id` = %s and `end_date` < %s ORDER BY `date` ASC, `time` """)
						get_event_data = (client_data['INSTITUTION_USER_ID_STUDENT'],filter_date)
					if flag == 3:
						get_event_query = ("""SELECT * FROM `event` where `client_id` = %s and `date` <= %s and `end_date` >= %s ORDER BY `date` ASC, `time`""")
						get_event_data = (client_data['INSTITUTION_USER_ID_STUDENT'],filter_date,filter_date)
					if flag == 4:
						get_event_query = ("""SELECT * FROM `event` where `client_id` = %s and `end_date` >= %s ORDER BY `date` ASC, `time`""")
						get_event_data = (client_data['INSTITUTION_USER_ID_STUDENT'],filter_date)
					count_event = cursor_event.execute(get_event_query,get_event_data)

					if count_event > 0:
						event_data = cursor_event.fetchall()
						for key,data in enumerate(event_data):
							if str(data['date']) > filter_date:
								event_data[key]['event_status'] = 1
							if str(data['end_date']) < filter_date:
								event_data[key]['event_status'] = 2
							if str(data['date']) < filter_date and str(data['end_date']) >= filter_date:
								event_data[key]['event_status'] = 3
							if str(data['end_date']) >= filter_date:
								event_data[key]['event_status'] = 4
										
							event_data[key]['last_update_ts'] = str(data['last_update_ts'])
							event_data[key]['date'] = str(data['date'])
							event_data[key]['end_date'] = str(data['end_date'])
							get_occasion_query = ("""SELECT count(*) as occasion_count FROM `occasion` where `event_manager_id` = %s and `event_id` = %s and `status` = 1""")
							get_occasion_data = (client_data['INSTITUTION_USER_ID_STUDENT'],data['event_id'])
							get_occasion_count = cursor.execute(get_occasion_query,get_occasion_data)

							if get_occasion_count > 0:
								occasion_data = cursor.fetchone()
								event_data[key]['occasion_count'] = occasion_data['occasion_count']
							else:
								event_data[key]['occasion_count'] = 0
					else:
						event_data = []
				else:
					event_data = []
			elif user_role_data['INSTITUTION_USER_ROLE'] == 'S1': 
				print('hiih')
				if flag == 0:
					get_event_query = ("""SELECT * FROM `event` where `client_id` = %s ORDER BY `date` ASC, `time`""")
					get_event_data = (client_data['INSTITUTION_USER_ID_STUDENT'])
				if flag == 1:
					get_event_query = ("""SELECT * FROM `event` where `client_id` = %s and `date` > %s ORDER BY `date` ASC, `time` """)
					get_event_data = (client_data['INSTITUTION_USER_ID_STUDENT'],filter_date)
				if flag == 2:
					get_event_query = ("""SELECT * FROM `event` where `client_id` = %s and `end_date` < %s ORDER BY `date` ASC, `time` """)
					get_event_data = (client_data['INSTITUTION_USER_ID_STUDENT'],filter_date)
				if flag == 3:
					get_event_query = ("""SELECT * FROM `event` where `client_id` = %s and `date` <= %s and `end_date` >= %s ORDER BY `date` ASC, `time`""")
					get_event_data = (client_data['INSTITUTION_USER_ID_STUDENT'],filter_date,filter_date)
				if flag == 4:
					get_event_query = ("""SELECT * FROM `event` where `client_id` = %s and `end_date` >= %s ORDER BY `date` ASC, `time`""")
					get_event_data = (client_data['INSTITUTION_USER_ID_STUDENT'],filter_date)
				count_event = cursor_event.execute(get_event_query,get_event_data)

				if count_event > 0:
					event_data = cursor_event.fetchall()
					for key,data in enumerate(event_data):
						if str(data['date']) > filter_date:
							event_data[key]['event_status'] = 1
						if str(data['end_date']) < filter_date:
							event_data[key]['event_status'] = 2
						if str(data['date']) < filter_date and str(data['end_date']) >= filter_date:
							event_data[key]['event_status'] = 3
						if str(data['end_date']) >= filter_date:
							event_data[key]['event_status'] = 4

						event_data[key]['last_update_ts'] = str(data['last_update_ts'])	
						event_data[key]['end_date'] = str(data['end_date'])	
						event_data[key]['date'] = str(data['date'])					
						get_occasion_query = ("""SELECT count(*) as occasion_count FROM `occasion` where `event_manager_id` = %s and `event_id` = %s and `status` = 1""")
						get_occasion_data = (user_id,data['event_id'])
						get_occasion_count = cursor.execute(get_occasion_query,get_occasion_data)

						if get_occasion_count > 0:
							occasion_data = cursor.fetchone()
							event_data[key]['occasion_count'] = occasion_data['occasion_count']
						else:
							event_data[key]['occasion_count'] = 0
				else:
					event_data = []	
			else:
				print('hii')
				if flag == 0:
					get_event_query = ("""SELECT * FROM `event` where `event_manager_id` = %s ORDER BY `date` ASC, `time`""")
					get_event_data = (user_id)
				if flag == 1:
					get_event_query = ("""SELECT * FROM `event` where `event_manager_id` = %s and `date` > %s ORDER BY `date` ASC, `time`""")
					get_event_data = (user_id,filter_date)
				if flag == 2:
					get_event_query = ("""SELECT * FROM `event` where `event_manager_id` = %s and `end_date` < %s ORDER BY `date` ASC, `time`""")
					get_event_data = (user_id,filter_date)					
				if flag == 3:
					get_event_query = ("""SELECT * FROM `event` where `event_manager_id` = %s and `date` <= %s and `end_date` >= %s ORDER BY `date` ASC, `time`""")
					get_event_data = (user_id,filter_date,filter_date)
				if flag == 4:
					get_event_query = ("""SELECT * FROM `event` where `event_manager_id` = %s and `end_date` >= %s ORDER BY `date` ASC, `time` """)
					get_event_data = (user_id,filter_date)
				count_event = cursor_event.execute(get_event_query,get_event_data)

				print(cursor_event._last_executed)


				if count_event > 0:
					event_data = cursor_event.fetchall()
					for key,data in enumerate(event_data):
						if str(data['date']) > filter_date:
							event_data[key]['event_status'] = 1
						if str(data['end_date']) < filter_date:
							event_data[key]['event_status'] = 2
						if str(data['date']) < filter_date and str(data['end_date']) >= filter_date:
							event_data[key]['event_status'] = 3
						if str(data['end_date']) >= filter_date:
							event_data[key]['event_status'] = 4

						event_data[key]['last_update_ts'] = str(data['last_update_ts'])	
						event_data[key]['date'] = str(data['date'])	
						event_data[key]['end_date'] = str(data['end_date'])	

						final_occasion_count = 0

						get_client_query = ("""SELECT * FROM `student_dtls` where `INSTITUTION_USER_ID_TEACHER` = %s""")
						get_client_data = (user_id)
						client_count = cursor.execute(get_client_query,get_client_data)

						if client_count > 0:
							cleint_data =  cursor.fetchall()

							for ckey,cdata in enumerate(cleint_data):

								get_occasion_query = ("""SELECT count(*) as occasion_count FROM `occasion` where `event_manager_id` = %s and `event_id` = %s and `status` = 1""")
								get_occasion_data = (cdata['INSTITUTION_USER_ID_STUDENT'],data['event_id'])
								get_occasion_count = cursor.execute(get_occasion_query,get_occasion_data)

								if get_occasion_count > 0:
									print(cursor._last_executed)
									occasion_data = cursor.fetchone()
									occasion_count = occasion_data['occasion_count']
									final_occasion_count = final_occasion_count + occasion_count
								else:
									occasion_count = 0

						event_data[key]['occasion_count'] = final_occasion_count
				else:
					event_data = []	
		else:
			event_manager_id		

		return ({"attributes": {
				    		"status_desc": "event_list",
				    		"status": "success"
				    	},
				    	"responseList":event_data}), status.HTTP_200_OK

#----------------------Get-Event-List---------------------#

#----------------------Get-Occasion-List-With-Filteration---------------------#
@name_space.route("/getOccasionListwithFilter/<int:flag>/<int:user_id>/<int:event_id>")	
class getOccasionListwithFilter(Resource):
	def get(self,flag,user_id,event_id):
		
		connection = connect_logindb()
		cursor = connection.cursor()

		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		today = date.today()
		#filter_date = today.strftime("%d-%m-%Y")	
		filter_date = today.strftime("%Y-%m-%d")

		get_user_role_query = ("""SELECT * FROM institution_user_credential_master where `INSTITUTION_USER_ID` = %s""")
		get_user_role_data = (user_id)
		user_role_count = cursor.execute(get_user_role_query,get_user_role_data)

		if user_role_count > 0:
			user_role_data =  cursor.fetchone()
			if user_role_data['INSTITUTION_USER_ROLE'] == 'G1':
				get_client_query = ("""SELECT * FROM `guardian_dtls` where `INSTITUTION_USER_ID_GUARDIAN` = %s""")
				get_client_data = (user_id)
				count_client_data = cursor.execute(get_client_query,get_client_data)

				if count_client_data > 0:
					client_data = cursor.fetchone()
					occasion_data = []

					get_assign_function_list = ("""SELECT f.`occasion_id`
							FROM `function_guest_mapping` fgm
							INNER JOIN `function` f ON f.`function_id` = fgm.`function_id`
							where `guest_id` = %s GROUP BY f.`occasion_id`""")
					get_assign_function_data = (user_id)
					assign_function_count = cursor_event.execute(get_assign_function_list,get_assign_function_data)
					if assign_function_count > 0:
						assign_function = cursor_event.fetchall()
						for akey,adata in enumerate(assign_function):
							if flag == 0:
								get_occasion_query = ("""SELECT * FROM `occasion` where `event_manager_id` = %s and `ocassion_id` = %s and `status` = 1 ORDER BY occasion_date ASC, occasion_time""")
								get_occasion_data = (client_data['INSTITUTION_USER_ID_STUDENT'],adata['occasion_id'])
							if flag == 1:
								get_occasion_query = ("""SELECT * FROM `occasion` where `event_manager_id` = %s and `occasion_date` > %s and `ocassion_id` = %s and `status` = 1 ORDER BY occasion_date ASC, occasion_time""")
								get_occasion_data = (client_data['INSTITUTION_USER_ID_STUDENT'],filter_date,adata['occasion_id'])
							if flag == 2:
								get_occasion_query = ("""SELECT * FROM `occasion` where `event_manager_id` = %s and `occasion_date` < %s and `ocassion_id` = %s and `status` = 1 ORDER BY occasion_date ASC, occasion_time""")
								get_occasion_data = (client_data['INSTITUTION_USER_ID_STUDENT'],filter_date,adata['occasion_id'])
							if flag == 3:
								get_occasion_query = ("""SELECT * FROM `occasion` where `event_manager_id` = %s and `occasion_date` = %s and `ocassion_id` = %s and `status` = 1 ORDER BY occasion_date ASC, occasion_time""")
								get_occasion_data = (client_data['INSTITUTION_USER_ID_STUDENT'],filter_date,adata['occasion_id'])
							if flag == 4:
								get_occasion_query = ("""SELECT * FROM `occasion` where `event_manager_id` = %s and `occasion_date` >= %s and `ocassion_id` = %s and `status` = 1 ORDER BY occasion_date ASC, occasion_time""")
								get_occasion_data = (client_data['INSTITUTION_USER_ID_STUDENT'],filter_date,adata['occasion_id'])
							count_occasion = cursor.execute(get_occasion_query,get_occasion_data)

							if count_occasion > 0:
								assign_occasion_data = cursor.fetchall()
								for key,data in enumerate(assign_occasion_data):
									if str(data['occasion_date']) > filter_date:
										assign_occasion_data[key]['occasion_status'] = 1
									if str(data['occasion_date']) > filter_date:
										assign_occasion_data[key]['occasion_status'] = 2
									if str(data['occasion_date']) > filter_date:
										assign_occasion_data[key]['occasion_status'] = 3
									if str(data['occasion_date']) > filter_date:
										assign_occasion_data[key]['occasion_status'] = 4

									if data['theme_id'] > 0:
										get_theme_query = ("""SELECT * FROM `theme` where `theme_id` = %s""")
										get_theme_data = (data['theme_id'])
										theme_count = cursor_event.execute(get_theme_query,get_theme_data)

										if theme_count > 0:
											theme_data = cursor_event.fetchone()
											assign_occasion_data[key]['theme_url'] = theme_data['theme_url']
											assign_occasion_data[key]['theme_name'] = theme_data['theme_name']
										else:
											assign_occasion_data[key]['theme_url'] = ""
											assign_occasion_data[key]['theme_name'] = ""
									else:
										assign_occasion_data[key]['theme_url'] = ""
										assign_occasion_data[key]['theme_name'] = ""

									assign_occasion_data[key]['occasion_date'] = str(data['occasion_date'])
									assign_occasion_data[key]['last_update_ts'] = str(data['last_update_ts'])
									get_function_query = ("""SELECT count(*) as function_count FROM `function` where `evant_manger_id` = %s and `occasion_id` = %s and `status` = 1""")
									get_function_data = (client_data['INSTITUTION_USER_ID_STUDENT'],data['ocassion_id'])
									get_function_count = cursor_event.execute(get_function_query,get_function_data)

									if get_function_count > 0:
										function_data = cursor_event.fetchone()
										assign_occasion_data[key]['function_count'] = function_data['function_count']
									else:
										assign_occasion_data[key]['function_count'] = 0

									occasion_data.append(assign_occasion_data[key])	
							else:
								occasion_data = []
					else:
						occasion_data = []					
				else:
					occasion_data = []
			elif user_role_data['INSTITUTION_USER_ROLE'] == 'S1': 
				if flag == 0:
					get_occasion_query = ("""SELECT * FROM `occasion` where `event_manager_id` = %s and `event_id` = %s and `status` = 1 ORDER BY occasion_date ASC, occasion_time""")
					get_occasion_data = (user_id,event_id)
				if flag == 1:
					get_occasion_query = ("""SELECT * FROM `occasion` where `event_manager_id` = %s and `occasion_date` > %s and `event_id` = %s and `status` = 1 ORDER BY occasion_date ASC, occasion_time""")
					get_occasion_data = (user_id,filter_date,event_id)
				if flag == 2:
					get_occasion_query = ("""SELECT * FROM `occasion` where `event_manager_id` = %s and `occasion_date` < %s and `event_id` = %s and `status` = 1 ORDER BY occasion_date ASC, occasion_time""")
					get_occasion_data = (user_id,filter_date,event_id)
				if flag == 3:
					get_occasion_query = ("""SELECT * FROM `occasion` where `event_manager_id` = %s and `occasion_date` = %s and `event_id` = %s and `status` = 1 ORDER BY occasion_date ASC, occasion_time""")
					get_occasion_data = (user_id,filter_date,event_id)
				if flag == 4:
					get_occasion_query = ("""SELECT * FROM `occasion` where `event_manager_id` = %s and `occasion_date` >= %s and `event_id` = %s and `status` = 1 ORDER BY occasion_date ASC, occasion_time""")
					get_occasion_data = (user_id,filter_date,event_id)
				count_occasion = cursor.execute(get_occasion_query,get_occasion_data)
				print(cursor._last_executed)

				if count_occasion > 0:
					occasion_data = cursor.fetchall()
					for key,data in enumerate(occasion_data):
						if str(data['occasion_date']) > filter_date:
							occasion_data[key]['occasion_status'] = 1
						if str(data['occasion_date']) < filter_date:
							occasion_data[key]['occasion_status'] = 2
						if str(data['occasion_date']) == filter_date:
							occasion_data[key]['occasion_status'] = 3
						if str(data['occasion_date']) >= filter_date:
							occasion_data[key]['occasion_status'] = 4

						if data['theme_id'] > 0:
							get_theme_query = ("""SELECT * FROM `theme` where `theme_id` = %s""")
							get_theme_data = (data['theme_id'])
							theme_count = cursor_event.execute(get_theme_query,get_theme_data)

							if theme_count > 0:
								theme_data = cursor_event.fetchone()
								occasion_data[key]['theme_url'] = theme_data['theme_url']
								occasion_data[key]['theme_name'] = theme_data['theme_name']
							else:
								occasion_data[key]['theme_url'] = ""
								occasion_data[key]['theme_name'] = ""
						else:
							occasion_data[key]['theme_url'] = ""
							occasion_data[key]['theme_name'] = ""

						occasion_data[key]['occasion_date'] = str(data['occasion_date'])	
						occasion_data[key]['last_update_ts'] = str(data['last_update_ts'])
						get_function_query = ("""SELECT count(*) as function_count FROM `function` where `evant_manger_id` = %s and `occasion_id` = %s and `status` = 1""")
						get_function_data = (user_id,data['ocassion_id'])
						get_function_count = cursor_event.execute(get_function_query,get_function_data)

						if get_function_count > 0:
							function_data = cursor_event.fetchone()
							occasion_data[key]['function_count'] = function_data['function_count']
						else:
							occasion_data[key]['function_count'] = 0
				else:
					occasion_data = []				
		else:
			occasion_data = []		

		return ({"attributes": {
				    		"status_desc": "occasion_list",
				    		"status": "success"
				    	},
				    	"responseList":occasion_data}), status.HTTP_200_OK

#----------------------Get-Occasion-List-With-Filteration---------------------#

#----------------------Create-Function---------------------#
@name_space_function.route("/createFunction")	
class createFunction(Resource):
	@api.expect(function_postmodel)
	def post(self):
		connection = connect_logindb()
		cursor = connection.cursor()

		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		details = request.get_json()

		function_name = details['function_name']
		function_date = details['function_date']
		function_time = details['function_time']
		place = details['place']
		mens_dress_code = details['mens_dress_code']
		womens_dress_code = details['womens_dress_code']
		kid_dress_code = details['kid_dress_code']
		event_id = details['event_id']
		occasion_id = details['occasion_id']
		client_id = details['client_id']



		if details and "theme_id" in details:
			theme_id = details['theme_id']
		else:
			theme_id = 0

		if details and "end_time" in details:
			end_time = details['end_time']
		else:
			end_time = ""

		if details and "function_type" in details:
			function_type = details['function_type']
		else:
			function_type = 2

		INSTITUTION_ID = 367

		if function_type == 1 or  function_type == 3:
			get_event_manager_details_query = ("""SELECT *
									  FROM `student_dtls` where `INSTITUTION_USER_ID_STUDENT` = %s and `INSTITUTION_ID` = %s""")
			get_event_manager_details_data = (client_id,INSTITUTION_ID)
			event_anager_count = cursor.execute(get_event_manager_details_query,get_event_manager_details_data)

			if event_anager_count > 0:
				event_anager_data = cursor.fetchone()
				client_event_manager_id = event_anager_data['INSTITUTION_USER_ID_TEACHER']

				get_zoom_details_query = ("""SELECT * FROM `zoom_user_details` where `user_id` =  %s""")
				get_zoom_details_data = (client_event_manager_id)
				zoom_count = cursor.execute(get_zoom_details_query,get_zoom_details_data)

				if zoom_count > 0:
					zoom_data = cursor.fetchone()

					mailId = zoom_data.get('user_mailid')
					apiKey = zoom_data.get('zoom_api_key')

					headers = {'Content-Type':'application/json','authorization': 'Bearer ' + apiKey}
					createUrl = 'https://api.zoom.us/v2/users/{userId}/meetings'.format(userId=mailId)
					print(createUrl)
					zoom_payload = {"topic": function_name,
											"type": 2,
											"start_time": function_time,
											"duration": 40,
											"timezone": "Asia/Calcutta",
											"password": "",
											"agenda": function_name,
											"settings": {
												"host_video": "true",
												"participant_video": "false",
												"join_before_host": "true",
												"mute_upon_entry": "true",
												"watermark": "true",
												"use_pmi": "false",
												"approval_type": "2",
												"registration_type": "1",
												"audio": "both",
												"auto_recording": "local"
												}
										}

					print(zoom_payload)

					postRequest = requests.post(createUrl, data=json.dumps(zoom_payload), headers=headers)
					postStatus = postRequest.status_code
					print(postStatus)

					if postStatus == 201:	

						postRes = postRequest.json()
						zoom_meeting_id = postRes.get('id')
						zoom_uuid = postRes.get('uuid')
						zoom_join_url = postRes.get('join_url')
						print(zoom_join_url)
					else:
						zoom_join_url = ""
				else:
					zoom_join_url = ""
			else:
				zoom_join_url = ""
		else:
			function_type = 0
			zoom_join_url = ""


		insert_function_query = ("""INSERT INTO `function`(`function_name`,`function_date`,`function_time`,`end_time`,`place`,`mens_dress_code`,`womens_dress_code`,`kid_dress_code`,`event_id`,`theme_id`,`function_type`,`zoom_join_url`,`occasion_id`,`evant_manger_id`) 
							VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

		insert_function_data = (function_name,function_date,function_time,end_time,place,mens_dress_code,womens_dress_code,kid_dress_code,event_id,theme_id,function_type,zoom_join_url,occasion_id,client_id)
		cursor_event.execute(insert_function_query,insert_function_data)

		details['function_id'] = cursor_event.lastrowid

		return ({"attributes": {"status_desc": "Create Function",
	                                "status": "success"
	                            },
								"responseList":details}), status.HTTP_200_OK

#----------------------Create-Function---------------------#

#----------------------Get-Function-List---------------------#
@name_space_function.route("/getFunctionList/<int:occasion_id>/<int:user_id>/<int:flag>")	
class getFunctionList(Resource):
	def get(self,occasion_id,user_id,flag):
		connection = connect_logindb()
		cursor = connection.cursor()

		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		today = date.today()
		#filter_date = today.strftime("%d-%m-%Y")
		filter_date = today.strftime("%Y-%m-%d")

		get_user_role_query = ("""SELECT * FROM institution_user_credential_master where `INSTITUTION_USER_ID` = %s""")
		get_user_role_data = (user_id)
		user_role_count = cursor.execute(get_user_role_query,get_user_role_data)

		if user_role_count > 0:
			user_role_data =  cursor.fetchone()
			if user_role_data['INSTITUTION_USER_ROLE'] == 'G1':
				get_client_query = ("""SELECT * FROM `guardian_dtls` where `INSTITUTION_USER_ID_GUARDIAN` = %s""")
				get_client_data = (user_id)
				count_client_data = cursor.execute(get_client_query,get_client_data)

				if count_client_data > 0:
					client_data = cursor.fetchone()
					if flag == 0:
						function_list_query = ("""SELECT f.*
								FROM `function_guest_mapping` fgm
								INNER JOIN `function` f ON f.`function_id` = fgm.`function_id`
								where f.`occasion_id` = %s and fgm.`guest_id` = %s and f.`status` = 1 ORDER BY function_date ASC, function_time """)
						function_list_data = (occasion_id,user_id)	
					if flag == 1:
						function_list_query = ("""SELECT f.*
								FROM `function_guest_mapping` fgm
								INNER JOIN `function` f ON f.`function_id` = fgm.`function_id`
								where f.`occasion_id` = %s and fgm.`guest_id` = %s and `function_date` > %s and `status` = 1 ORDER BY function_date ASC, function_time""")
						function_list_data = (occasion_id,user_id,filter_date)	

					if flag == 2:
						function_list_query = ("""SELECT f.*
								FROM `function_guest_mapping` fgm
								INNER JOIN `function` f ON f.`function_id` = fgm.`function_id`
								where f.`occasion_id` = %s and fgm.`guest_id` = %s and `function_date` < %s and `status` = 1 ORDER BY function_date ASC, function_time""")
						function_list_data = (occasion_id,client_data['INSTITUTION_USER_ID_STUDENT'],filter_date)
					if flag == 3:
						function_list_query = ("""SELECT f.*
								FROM `function_guest_mapping` fgm
								INNER JOIN `function` f ON f.`function_id` = fgm.`function_id`
								where f.`occasion_id` = %s and fgm.`guest_id` = %s and `function_date` = %s and `status` = 1 ORDER BY function_date ASC, function_time""")
						function_list_data = (occasion_id,user_id,filter_date)
					if flag == 4:
						function_list_query = ("""SELECT f.*
								FROM `function_guest_mapping` fgm
								INNER JOIN `function` f ON f.`function_id` = fgm.`function_id`
								where f.`occasion_id` = %s and fgm.`guest_id` = %s and `function_date` >= %s and `status` = 1 ORDER BY function_date ASC, function_time""")
						function_list_data = (occasion_id,client_data['INSTITUTION_USER_ID_STUDENT'],filter_date)
						
					function_count = cursor_event.execute(function_list_query,function_list_data)

					if function_count > 0:
						function_data = cursor_event.fetchall()
						for key,data in enumerate(function_data):

							if data['theme_id'] > 0:
								get_theme_query = ("""SELECT * FROM `theme` where `theme_id` = %s""")
								get_theme_data = (data['theme_id'])
								theme_count = cursor_event.execute(get_theme_query,get_theme_data)

								if theme_count > 0:
									theme_data = cursor_event.fetchone()
									function_data[key]['theme_url'] = theme_data['theme_url']
									function_data[key]['theme_name'] = theme_data['theme_name']
								else:
									function_data[key]['theme_url'] = ""
									function_data[key]['theme_name'] = ""
							else:
								function_data[key]['theme_url'] = ""
								function_data[key]['theme_name'] = ""

							function_data[key]['function_date'] = str(data['function_date'])	
							function_data[key]['last_update_ts'] = str(data['last_update_ts'])
							get_assign_guest_query = ("""SELECT count(*) as assigned_guest_count
								FROM `function_guest_mapping` where `function_id` = %s""")
							get_assign_guest_data = (data['function_id'])
							get_assign_guestcount = cursor_event.execute(get_assign_guest_query,get_assign_guest_data)

							if get_assign_guestcount > 0:
								assign_guest = cursor_event.fetchone()
								function_data[key]['assigned_guest_count'] = assign_guest['assigned_guest_count']
							else:
								function_data[key]['assigned_guest_count'] = 0

					else:
						function_data = []
				else:
					function_data = []

			elif user_role_data['INSTITUTION_USER_ROLE'] == 'S1': 
				if flag == 0:
					function_list_query = ("""SELECT *
								FROM `function` where `occasion_id` = %s and `evant_manger_id` = %s and `status` = 1 ORDER BY function_date ASC, function_time""")
					function_list_data = (occasion_id,user_id)	
				if flag == 1:
					function_list_query = ("""SELECT *
								FROM `function` where `occasion_id` = %s and `evant_manger_id` = %s and `function_date` > %s and `status` = 1 ORDER BY function_date ASC, function_time""")
					function_list_data = (occasion_id,user_id,filter_date)	

				if flag == 2:
					function_list_query = ("""SELECT *
								FROM `function` where `occasion_id` = %s and `evant_manger_id` = %s and `function_date` < %s and `status` = 1 ORDER BY function_date ASC, function_time""")
					function_list_data = (occasion_id,user_id,filter_date)
				if flag == 3:
					function_list_query = ("""SELECT *
								FROM `function` where `occasion_id` = %s and `evant_manger_id` = %s and `function_date` = %s and `status` = 1 ORDER BY function_date ASC, function_time""")
					function_list_data = (occasion_id,user_id,filter_date)
				if flag == 4:
					function_list_query = ("""SELECT *
								FROM `function` where `occasion_id` = %s and `evant_manger_id` = %s and `function_date` >= %s and `status` = 1 ORDER BY function_date ASC, function_time""")
					function_list_data = (occasion_id,user_id,filter_date)
						
				function_count = cursor_event.execute(function_list_query,function_list_data)

				if function_count > 0:
					function_data = cursor_event.fetchall()
					for key,data in enumerate(function_data):
						if data['theme_id'] > 0:
							get_theme_query = ("""SELECT * FROM `theme` where `theme_id` = %s""")
							get_theme_data = (data['theme_id'])
							theme_count = cursor_event.execute(get_theme_query,get_theme_data)

							if theme_count > 0:
								theme_data = cursor_event.fetchone()
								function_data[key]['theme_url'] = theme_data['theme_url']
								function_data[key]['theme_name'] = theme_data['theme_name']
							else:
								function_data[key]['theme_url'] = ""
								function_data[key]['theme_name'] = ""
						else:
							function_data[key]['theme_url'] = ""
							function_data[key]['theme_name'] = ""


						function_data[key]['function_date'] = str(data['function_date'])

						function_data[key]['last_update_ts'] = str(data['last_update_ts'])
						get_assign_guest_query = ("""SELECT count(*) as assigned_guest_count
								FROM `function_guest_mapping` where `function_id` = %s""")
						get_assign_guest_data = (data['function_id'])
						get_assign_guestcount = cursor_event.execute(get_assign_guest_query,get_assign_guest_data)

						if get_assign_guestcount > 0:
							assign_guest = cursor_event.fetchone()
							function_data[key]['assigned_guest_count'] = assign_guest['assigned_guest_count']
						else:
							function_data[key]['assigned_guest_count'] = 0
				else:
					function_data = []				

		else:
			function_data = []
		

		return ({"attributes": {
				    		"status_desc": "function_list",
				    		"status": "success"
				    	},
				    	"responseList":function_data}), status.HTTP_200_OK


#----------------------Get-Function-List---------------------#

#----------------------Get-Guest-List-By-Function-Id---------------------#
@name_space_function.route("/getGuestListByFunctionId/<int:function_id>")	
class getGuestListByFunctionId(Resource):
	def get(self,function_id):
		connection = connect_logindb()
		cursor = connection.cursor()

		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		get_assign_guest_query = ("""SELECT `guest_id`
								FROM `function_guest_mapping` where `function_id` = %s""")
		get_assign_guest_data = (function_id)
		get_assign_guestcount = cursor_event.execute(get_assign_guest_query,get_assign_guest_data)

		if get_assign_guestcount > 0:
			assign_guest = cursor_event.fetchall()

			for key,data in enumerate(assign_guest):
				get_guest_query = ("""SELECT iuc.`INSTITUTION_USER_ID`,iuc.`INSTITUTION_USER_NAME`,iuc.`INSTITUTION_USER_PASSWORD`,iuc.`FIRST_NAME`,iuc.`LAST_NAME`,iuc.`PRIMARY_CONTACT_NUMBER`,
						gd.`arrival_time`,gd.`departure_time`,gd.`how_to_arrive`,gd.`pickup_location`,gd.`pickup_time`,gd.`departure_location`,gd.`status`
						FROM `institution_user_credential` iuc
						INNER JOIN `guest_details` gd on gd.`guest_id` = iuc.`INSTITUTION_USER_ID`
						WHERE `INSTITUTION_USER_ID` = %s""")
				get_guest_data = (data['guest_id'])
				guest_count = cursor.execute(get_guest_query,get_guest_data)
				if guest_count > 0:
					print(cursor._last_executed)
					guest_data = cursor.fetchone()
					assign_guest[key]['INSTITUTION_USER_ID'] = guest_data['INSTITUTION_USER_ID']
					assign_guest[key]['INSTITUTION_USER_NAME'] = guest_data['INSTITUTION_USER_NAME']
					assign_guest[key]['INSTITUTION_USER_PASSWORD'] = guest_data['INSTITUTION_USER_PASSWORD']
					assign_guest[key]['FIRST_NAME'] = guest_data['FIRST_NAME']
					assign_guest[key]['LAST_NAME'] = guest_data['LAST_NAME']
					assign_guest[key]['PRIMARY_CONTACT_NUMBER'] = guest_data['PRIMARY_CONTACT_NUMBER']
					assign_guest[key]['arrival_time'] = guest_data['arrival_time']
					assign_guest[key]['departure_time'] = guest_data['departure_time']
					assign_guest[key]['how_to_arrive'] = guest_data['how_to_arrive']
					assign_guest[key]['pickup_location'] = guest_data['pickup_location']
					assign_guest[key]['pickup_time'] = guest_data['pickup_time']
					assign_guest[key]['departure_location'] = guest_data['departure_location']
					assign_guest[key]['status'] = guest_data['status']
				else:
					assign_guest[key]['INSTITUTION_USER_ID'] = 0
					assign_guest[key]['INSTITUTION_USER_NAME'] = ""
					assign_guest[key]['INSTITUTION_USER_PASSWORD'] = ""
					assign_guest[key]['FIRST_NAME'] = ""
					assign_guest[key]['LAST_NAME'] = ""
					assign_guest[key]['PRIMARY_CONTACT_NUMBER'] = ""
					assign_guest[key]['arrival_time'] = ""
					assign_guest[key]['departure_time'] = ""
					assign_guest[key]['how_to_arrive'] = ""
					assign_guest[key]['pickup_location'] = ""
					assign_guest[key]['pickup_time'] = ""
					assign_guest[key]['departure_location'] = ""
					assign_guest[key]['status'] = ""
		else:
			assign_guest = []

		return ({"attributes": {
				    		"status_desc": "assign_guest_list",
				    		"status": "success"
				    	},
				    	"responseList":assign_guest}), status.HTTP_200_OK

#----------------------Get-Guest-List-By-Function-Id---------------------#

#----------------------Update-Function---------------------#

@name_space_function.route("/updatefunction/<int:function_id>")
class updatefunction(Resource):
	@api.expect(function_putmodel)
	def put(self, function_id):

		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		details = request.get_json()

		if details and "function_name" in details:
			function_name = details['function_name']
			update_query = ("""UPDATE `function` SET `function_name` = %s
				WHERE `function_id` = %s """)
			update_data = (function_name,function_id)
			cursor_event.execute(update_query,update_data)

		if details and "function_date" in details:
			function_date = details['function_date']
			update_query = ("""UPDATE `function` SET `function_date` = %s
				WHERE `function_id` = %s """)
			update_data = (function_date,function_id)
			cursor_event.execute(update_query,update_data)

		if details and "function_time" in details:
			function_time = details['function_time']
			update_query = ("""UPDATE `function` SET `function_time` = %s
				WHERE `function_id` = %s """)
			update_data = (function_time,function_id)
			cursor_event.execute(update_query,update_data)

		if details and "end_time" in details:
			end_time = details['end_time']
			update_query = ("""UPDATE `function` SET `end_time` = %s
				WHERE `function_id` = %s """)
			update_data = (end_time,function_id)
			cursor_event.execute(update_query,update_data)

		if details and "place" in details:
			place = details['place']
			update_query = ("""UPDATE `function` SET `place` = %s
				WHERE `function_id` = %s """)
			update_data = (place,function_id)
			cursor_event.execute(update_query,update_data)	

		if details and "mens_dress_code" in details:
			mens_dress_code = details['mens_dress_code']
			update_query = ("""UPDATE `function` SET `mens_dress_code` = %s
				WHERE `function_id` = %s """)
			update_data = (mens_dress_code,function_id)
			cursor_event.execute(update_query,update_data)	

		if details and "womens_dress_code" in details:
			womens_dress_code = details['womens_dress_code']
			update_query = ("""UPDATE `function` SET `womens_dress_code` = %s
				WHERE `function_id` = %s """)
			update_data = (womens_dress_code,function_id)
			cursor_event.execute(update_query,update_data)

		if details and "kid_dress_code" in details:
			kid_dress_code = details['kid_dress_code']
			update_query = ("""UPDATE `function` SET `kid_dress_code` = %s
				WHERE `function_id` = %s """)
			update_data = (kid_dress_code,function_id)
			cursor_event.execute(update_query,update_data)

		if details and "theme_id" in details:
			theme_id = details['theme_id']
			update_query = ("""UPDATE `function` SET `theme_id` = %s
				WHERE `function_id` = %s """)
			update_data = (theme_id,function_id)
			cursor_event.execute(update_query,update_data)

		connection_event.commit()
		cursor_event.close()

		return ({"attributes": {"status_desc": "Update Function",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-Function---------------------#

#----------------------Assign-Guest-For-Function---------------------#
@name_space_function.route("/assignGuestForFunction")	
class assignGuestForFunction(Resource):
	@api.expect(assign_guest_postmodel)
	def post(self):
		connection = connect_logindb()
		cursor = connection.cursor()

		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		details = request.get_json()

		guest_ids = details.get('guest_id',[])	
		function_id = details['function_id']
		client_id =  details['client_id']

		get_client_details_query = ("""SELECT * FROM `institution_user_credential` where `INSTITUTION_USER_ID` = %s""")
		get_client_details_data = (client_id)
		client_details_count =  cursor.execute(get_client_details_query,get_client_details_data)

		if client_details_count > 0:
			client_details = cursor.fetchone()
			cleint_name = client_details['FIRST_NAME']
		else:
			cleint_name = ""

		get_function_details_query = ("""SELECT * FROM `function` where `function_id` = %s""")
		get_function_details_data = (function_id)
		function_details_count = cursor_event.execute(get_function_details_query,get_function_details_data)

		if function_details_count > 0:
			function_details = cursor_event.fetchone()
			function_name = function_details['function_name']
		else:
			function_name = ""

		get_evnet_manager_query = ("""SELECT * FROM `student_dtls` where `INSTITUTION_USER_ID_STUDENT` = %s""")
		get_event_manager_data = (client_id)
		event_manager_count = cursor.execute(get_evnet_manager_query,get_event_manager_data)

		if event_manager_count > 0:
			event_manager_data = cursor.fetchone()
			event_manager_id =event_manager_data['INSTITUTION_USER_ID_TEACHER']
		else:
			event_manager_id = 0	

		for key,guest_id in enumerate(guest_ids):
			get_assign_query = ("""SELECT * FROM `function_guest_mapping` where `guest_id` = %s and `function_id` =  %s""")
			get_assign_data = (guest_id,function_id)
			assign_count = cursor_event.execute(get_assign_query,get_assign_data)
			if assign_count < 1 :
				insert_query = ("""INSERT INTO `function_guest_mapping`(`function_id`,`guest_id`,`client_id`,`event_manager_id`,`last_update_id`) 
									VALUES(%s,%s,%s,%s,%s)""")
				data = (function_id,guest_id,client_id,event_manager_id,event_manager_id)
				cursor_event.execute(insert_query,data)

			get_device_token_query = ("""SELECT * FROM `devices` where `user_id` = %s""")
			get_device_token_data = (guest_id)
			device_token_count = cursor_event.execute(get_device_token_query,get_device_token_data)
			if device_token_count > 0:
				device_token_data = cursor_event.fetchone()

				data_message = {
							"title" : "Invitation",
							"message": cleint_name+" has invited to attend the "+function_name
						}
				api_key = "AAAA66tddZI:APA91bG89PrDCMns8-RSyLHUBiyu8VO1Kj9lchokDygCPg6NeRB59yD0sKXIe2xviw1XGraugdm9T8obOcGwf8tD_fiBVhHzAR_H186SNN88nEtOPxkFt7GQoyXVD91mt_3pVEeVwOb1"
				device_id = device_token_data['device_token']
				push_service = FCMNotification(api_key=api_key)
				msgResponse = push_service.notify_single_device(registration_id=device_id,data_message = data_message)
				sent = 'N'
				if msgResponse.get('success') == 1:
					sent = 'Y'
					body = cleint_name+" has invited to attend the "+function_name
					title = "Invitation"
					insert_app_notification_query = ("""INSERT INTO `app_notification`(`title`,`body`,`user_id`) 
						VALUES(%s,%s,%s)""")
					insert_app_notification_data = (title,body,guest_id)
					cursor_event.execute(insert_app_notification_query,insert_app_notification_data)


		connection.commit()
		cursor.close()

		return ({"attributes": {
					    "status_desc": "assign_guest",
					    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK

#----------------------Assign-Guest-For-Function---------------------#

#----------------------Delete-Occasion---------------------#

@name_space_function.route("/deleteFunction/<int:function_id>")
class deleteFunction(Resource):
	def delete(self, function_id):

		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		function_status = 0

		update_query = ("""UPDATE `function` SET `status` = %s
				WHERE `function_id` = %s """)
		update_data = (function_status,function_id)
		cursor_event.execute(update_query,update_data)

		connection_event.commit()
		cursor_event.close()
		
		return ({"attributes": {"status_desc": "Delete Function",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Occasion---------------------#

#----------------------create-Zoom-Url---------------------#
@name_space_function.route("/createZoomUrl")	
class createZoomUrl(Resource):
	@api.expect(zoom_postmodel)
	def post(self):
		connection = connect_logindb()
		cursor = connection.cursor()
		details = request.get_json()

		user_id = details['user_id']

		get_zoom_details_query = ("""SELECT * FROM `zoom_user_details` where `user_id` =  %s""")
		get_zoom_details_data = (user_id)
		zoom_count = cursor.execute(get_zoom_details_query,get_zoom_details_data)

		if zoom_count > 0:
			zoom_data = cursor.fetchone()

			mailId = zoom_data.get('user_mailid')
			apiKey = zoom_data.get('zoom_api_key')

			headers = {'Content-Type':'application/json','authorization': 'Bearer ' + apiKey}
			createUrl = 'https://api.zoom.us/v2/users/{userId}/meetings'.format(userId=mailId)
			print(createUrl)
			zoom_payload = {"topic": 'test',
								"type": 2,
								"start_time": '06:00 PM',
								"duration": 40,
								"timezone": "Asia/Calcutta",
								"password": "",
								"agenda": 'test',
								"settings": {
									"host_video": "true",
									"participant_video": "false",
									"join_before_host": "true",
									"mute_upon_entry": "true",
									"watermark": "true",
									"use_pmi": "false",
									"approval_type": "2",
									"registration_type": "1",
									"audio": "both",
									"auto_recording": "local"
									}
							}

			print(zoom_payload)

			postRequest = requests.post(createUrl, data=json.dumps(zoom_payload), headers=headers)
			postStatus = postRequest.status_code
			print(postStatus)

			if postStatus == 201:	

				postRes = postRequest.json()
				zoom_meeting_id = postRes.get('id')
				zoom_uuid = postRes.get('uuid')
				zoom_join_url = postRes.get('join_url')
				print(zoom_join_url)


#----------------------create-Zoom-Url---------------------#

#----------------------Add-Event-Photo--------------------#

@name_space_event_photo.route("/AddEventPhoto")
class AddEventPhoto(Resource):
	@api.expect(event_photo_postmodel)
	def post(self):

		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		connection = connect_logindb()
		cursor = connection.cursor()

		details = request.get_json()

		image = details['image']
		text = details['text']
		event_id = details['event_id']
		event_manager_id = details['event_manager_id']
		user_id = details['user_id']	

		get_user_role_query = ("""SELECT * FROM institution_user_credential_master where `INSTITUTION_USER_ID` = %s""")
		get_user_role_data = (user_id)
		user_role_count = cursor.execute(get_user_role_query,get_user_role_data)

		if user_role_count > 0:
			user_role_data =  cursor.fetchone()	
			if user_role_data['INSTITUTION_USER_ROLE'] == 'G1':
				get_client_query = ("""SELECT * FROM `guardian_dtls` where `INSTITUTION_USER_ID_GUARDIAN` = %s""")
				get_client_data = (user_id)
				count_client_data = cursor.execute(get_client_query,get_client_data)

				if count_client_data > 0:
					client_data = cursor.fetchone()
					insert_query = ("""INSERT INTO `event_photos`(`image`,`text`,`event_id`,`guest_id`,`client_id`,`event_manager_id`) 
									VALUES(%s,%s,%s,%s,%s,%s)""")
					data = (image,text,event_id,user_id,client_data['INSTITUTION_USER_ID_STUDENT'],event_manager_id)
					cursor_event.execute(insert_query,data)

					event_photo_id = cursor_event.lastrowid
					
					details['event_photo_id'] = event_photo_id
				
			elif user_role_data['INSTITUTION_USER_ROLE'] == 'S1':
				insert_query = ("""INSERT INTO `event_photos`(`image`,`text`,`event_id`,`client_id`,`event_manager_id`) 
									VALUES(%s,%s,%s,%s,%s)""")
				data = (image,text,event_id,user_id,event_manager_id)
				cursor_event.execute(insert_query,data)

				event_photo_id = cursor_event.lastrowid
					
				details['event_photo_id'] = event_photo_id

		connection_event.commit()
		cursor_event.close()

		return ({"attributes": {
					    "status_desc": "event_details",
					    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK

#----------------------Add-Event-Photo--------------------#

#----------------------Like-Event-Photo--------------------#

@name_space_event_photo.route("/LikeEventPhoto")
class LikeEventPhoto(Resource):
	@api.expect(like_photo_postmodel)
	def post(self):
		connection = connect_logindb()
		cursor = connection.cursor()

		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		event_photo_id = details['event_photo_id']
		user_id = details['user_id']
		is_like = details['is_like']

		if is_like == 1:
			insert_query = ("""INSERT INTO `event_photo_like`(`event_photo_id`,`user_id`) 
						VALUES(%s,%s)""")
			data = (event_photo_id,user_id)
			cursor_event.execute(insert_query,data)

			get_image_query = ("""SELECT *
									  FROM `event_photos` ep where ep.`event_photo_id` = %s""")
			get_image_data = (event_photo_id)
			image_count = cursor_event.execute(get_image_query,get_image_data)
			image_data = cursor_event.fetchone()

			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			sendAppPushNotificationUrl = BASE_URL + "/event/sendNotifications"

			payloadpushData = {										
										"text":"Some One Liked Photo",
										"title":"Liked Your Photo",
										"image":image_data['image'],
										"user_id":image_data['client_id']
							}
			print(payloadpushData)

			send_push_notification = requests.post(sendAppPushNotificationUrl,data=json.dumps(payloadpushData), headers=headers).json()

		else:
			delete_query = ("""DELETE FROM `event_photo_like` WHERE `event_photo_id` = %s and `user_id` = %s""")
			delData = (event_photo_id,user_id)
			
			cursor_event.execute(delete_query,delData)

			connection.commit()
			cursor.close()

		return ({"attributes": {
					    "status_desc": "like_event_photo",
					    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK

#----------------------Like-Event-Photo--------------------#

#----------------------Send-Notification---------------------#

@name_space.route("/sendNotifications")
class sendNotifications(Resource):
	@api.expect(notification_model)
	def post(self):

		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()
		details = request.get_json()

		user_id = details['user_id']

		get_device_query = ("""SELECT *
									FROM `devices` WHERE `user_id` = %s""")
		get_device_data = (user_id)
		count_device_token = cursor_event.execute(get_device_query,get_device_data)
		if count_device_token > 0:
			device_data = cursor_event.fetchone()
			print(cursor_event._last_executed)
			print(device_data['device_token'])

			data_message = {
								"title" : details['title'],
								"message": details['text'],
								"image-url":details['image']
							}
			print(data_message)
			api_key = 'AAAA66tddZI:APA91bG89PrDCMns8-RSyLHUBiyu8VO1Kj9lchokDygCPg6NeRB59yD0sKXIe2xviw1XGraugdm9T8obOcGwf8tD_fiBVhHzAR_H186SNN88nEtOPxkFt7GQoyXVD91mt_3pVEeVwOb1'
			device_id = device_data['device_token']
			push_service = FCMNotification(api_key=api_key)
			msgResponse = push_service.notify_single_device(registration_id=device_id,data_message = data_message)
			sent = 'N'
			if msgResponse.get('success') == 1:
				sent = 'Y'
		else:
			sent = 'N'
		
		
		connection_event.commit()
		cursor_event.close()

		return ({"attributes": {
				    		"status_desc": "Push Notification",
				    		"status": "success"
				    	},
				    	"responseList":msgResponse}), status.HTTP_200_OK

#----------------------Send-Notification---------------------#

#----------------------Comments-On-Event-Photo--------------------#

@name_space_event_photo.route("/CommentsOnEventPhoto")
class CommentsOnEventPhoto(Resource):
	@api.expect(comments_on_event_photo_post_model)
	def post(self):
		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		details = request.get_json()

		user_id = details['user_id']
		event_photo_id = details['event_photo_id']
		comments = details['comments']

		insert_query = ("""INSERT INTO `event_photo_comments`(`event_photo_id`,`user_id`,`comments`) 
						VALUES(%s,%s,%s)""")
		data = (event_photo_id,user_id,comments)
		cursor_event.execute(insert_query,data)

		event_photo_comments_id = cursor_event.lastrowid

		get_image_query = ("""SELECT *
									  FROM `event_photos` ep where ep.`event_photo_id` = %s""")
		get_image_data = (event_photo_id)
		image_count = cursor_event.execute(get_image_query,get_image_data)
		image_data = cursor_event.fetchone()

		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		sendAppPushNotificationUrl = BASE_URL + "/event/sendNotifications"

		payloadpushData = {										
										"text":"Some One Commented On Your Photo",
										"title":comments,
										"image":image_data['image'],
										"user_id":image_data['client_id']
							}
		print(payloadpushData)

		send_push_notification = requests.post(sendAppPushNotificationUrl,data=json.dumps(payloadpushData), headers=headers).json()

		connection_event.commit()
		cursor_event.close()

		return ({"attributes": {
					    "status_desc": "event_comment_details",
					    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK

#----------------------Comments-On-Event-Photo--------------------#

#----------------------Get-Event-Photo-List---------------------#

@name_space_event_photo.route("/EventPhotoList/<int:user_id>/<int:role>/<int:event_id>")	
class EventPhotoList(Resource):
	def get(self,user_id,role,event_id):
		connection = connect_logindb()
		cursor = connection.cursor()

		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		if role == 1: #client
			get_query = ("""SELECT ep.*, e.`event_name`
									FROM `event_photos` ep
									INNER JOIN `event` e ON e.`event_id` = ep.`event_id`								
									where ep.`client_id` = %s and ep.`event_id` = %s order by event_photo_id desc""")
			get_data = (user_id,event_id)
			cursor_event.execute(get_query,get_data)
			event_photo_data = cursor_event.fetchall()
		if role == 2: #guest
			get_query = ("""SELECT ep.*, e.`event_name`
									FROM `event_photos` ep
									INNER JOIN `event` e ON e.`event_id` = ep.`event_id`								
									where ep.`guest_id` = %s and ep.`event_id` = %s order by event_photo_id desc""")
			get_data = (user_id,event_id)
			cursor_event.execute(get_query,get_data)
			event_photo_data = cursor_event.fetchall()

		'''elif role == 2:
			get_client_query = ("""SELECT * FROM `guardian_dtls` where `INSTITUTION_USER_ID_GUARDIAN` = %s""")
			get_client_data = (user_id)
			count_client_data = cursor.execute(get_client_query,get_client_data)

			if count_client_data > 0:
				client_data = cursor.fetchone()

				get_query = ("""SELECT ep.*, e.`event_name`
										FROM `event_photos` ep
										INNER JOIN `event` e ON e.`event_id` = ep.`event_id`								
										where ep.`client_id` = %s and ep.`event_id` = %s order by event_photo_id desc""")
				get_data = (client_data['INSTITUTION_USER_ID_STUDENT'],event_id)
				cursor_event.execute(get_query,get_data)
				event_photo_data = cursor_event.fetchall()
			else:
				event_photo_data = []'''

		if event_photo_data:
			for key,data in enumerate(event_photo_data):
				event_photo_data[key]['last_update_ts'] = str(data['last_update_ts'])

				if data['guest_id'] == 0:
					get_user_information_query = ("""SELECT `IMAGE_URL` as 'profile_image' , `FIRST_NAME` as 'name' FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""")
					get_user_information_data = (data['client_id'])
					user_information_count = cursor.execute(get_user_information_query,get_user_information_data)

					if user_information_count > 0:
						user_information = cursor.fetchone()
						event_photo_data[key]['user_id'] = data['client_id']
						event_photo_data[key]['name'] = user_information['name']
						if user_information['profile_image'] is None:
							event_photo_data[key]['profile_image'] = ""
						else:
							event_photo_data[key]['profile_image'] = user_information['profile_image']
					else:
						event_photo_data[key]['name'] = ""
						event_photo_data[key]['profile_image'] = ""
				else:
					get_user_information_query = ("""SELECT `IMAGE_URL` as 'profile_image' , `FIRST_NAME` as 'name' FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""")
					get_user_information_data = (data['guest_id'])
					user_information_count = cursor.execute(get_user_information_query,get_user_information_data)

					if user_information_count > 0:
						user_information = cursor.fetchone()
						event_photo_data[key]['user_id'] = data['guest_id']
						event_photo_data[key]['name'] = user_information['name']
						if user_information['profile_image'] is None:
							event_photo_data[key]['profile_image'] = ""
						else:
							event_photo_data[key]['profile_image'] = user_information['profile_image']
					else:
						event_photo_data[key]['name'] = ""
						event_photo_data[key]['profile_image'] = ""

				get_event_photo_like_count_query = ("""SELECT count(*) event_photo_like_count
							FROM `event_photo_like` epl							
							where epl.`event_photo_id` = %s""")
				get_event_photo_like_count_data = (data['event_photo_id'])
				count_like = cursor_event.execute(get_event_photo_like_count_query,get_event_photo_like_count_data)

				if count_like > 0:

					event_photo_like_data =  cursor_event.fetchone()
					event_photo_data[key]['total_like_count'] = event_photo_like_data['event_photo_like_count']
				else:
					event_photo_data[key]['total_like_count'] = 0

				get_event_photo_comment_count_query = ("""SELECT count(*) event_photo_comment_count
							FROM `event_photo_comments` epc							
							where epc.`event_photo_id` = %s""")
				get_event_photo_comment_count_data = (data['event_photo_id'])
				count_comment = cursor_event.execute(get_event_photo_comment_count_query,get_event_photo_comment_count_data)

				if count_comment > 0:

					event_photo_comment_data =  cursor_event.fetchone()
					event_photo_data[key]['total_comment_count'] = event_photo_comment_data['event_photo_comment_count']
				else:
					event_photo_data[key]['total_comment_count'] = 0

				get_event_photo_tag_query = ("""SELECT `tagged_user_id` as `user_id`
							FROM `tagged_event_photo`														
							where `event_photo_id` = %s""")		
				get_event_photo_tag_data = (data['event_photo_id'])	
				event_photo_tag_count = cursor_event.execute(get_event_photo_tag_query,get_event_photo_tag_data)
				event_photo_tag = cursor_event.fetchall()

				for tkey,tdata in enumerate(event_photo_tag):
					get_tag_user_information_query = ("""SELECT `FIRST_NAME` as 'name' FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""")
					get_tag_user_information_data = (tdata['user_id'])
					tag_user_information_count = cursor.execute(get_tag_user_information_query,get_tag_user_information_data)

					if tag_user_information_count > 0:
						tag_user_information = cursor.fetchone()
						event_photo_tag[tkey]['name'] = tag_user_information['name']
					else:
						event_photo_tag[tkey]['name'] = ""


				event_photo_data[key]['photo_tag_list'] = event_photo_tag

		get_event_tag_photo_list_query = ("""SELECT ep.*,e.`event_name`,tep.`tagged_user_id`
									FROM `tagged_event_photo` tep
									INNER JOIN `event_photos` ep ON ep.`event_photo_id` = tep.`event_photo_id`
									INNER JOIN `event` e ON e.`event_id` = ep.`event_id`									
									where ep.`event_id` = %s  and tep.`tagged_user_id` = %s order by tagged_event_photo_id desc""")

		get_event_tag_photo_list_data = (event_id,user_id)
		cursor_event.execute(get_event_tag_photo_list_query,get_event_tag_photo_list_data)
		event_photo_tag_list_data = cursor_event.fetchall()

		for etkey,etdata in enumerate(event_photo_tag_list_data):
			event_photo_tag_list_data[etkey]['last_update_ts'] = str(etdata['last_update_ts'])
			get_user_information_query = ("""SELECT `IMAGE_URL` as 'profile_image' , `FIRST_NAME` as 'name' FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""")
			get_user_information_data = (etdata['tagged_user_id'])
			user_information_count = cursor.execute(get_user_information_query,get_user_information_data)

			if user_information_count > 0:
				user_information = cursor.fetchone()
				event_photo_tag_list_data[etkey]['name'] = user_information['name']
				if user_information['profile_image'] is None:
					event_photo_tag_list_data[etkey]['profile_image'] = ""
				else:
					event_photo_tag_list_data[etkey]['profile_image'] = user_information['profile_image']
			else:
				event_photo_tag_list_data[etkey]['name'] = ""
				event_photo_tag_list_data[etkey]['profile_image'] = ""

			get_event_photo_like_count_query = ("""SELECT count(*) event_photo_like_count
							FROM `event_photo_like` epl							
							where epl.`event_photo_id` = %s""")
			get_event_photo_like_count_data = (etdata['event_photo_id'])
			count_like = cursor_event.execute(get_event_photo_like_count_query,get_event_photo_like_count_data)

			if count_like > 0:

				event_photo_like_data =  cursor_event.fetchone()
				event_photo_tag_list_data[etkey]['total_like_count'] = event_photo_like_data['event_photo_like_count']
			else:
				event_photo_tag_list_data[etkey]['total_like_count'] = 0

			get_event_photo_comment_count_query = ("""SELECT count(*) event_photo_comment_count
							FROM `event_photo_comments` epc							
							where epc.`event_photo_id` = %s""")
			get_event_photo_comment_count_data = (etdata['event_photo_id'])
			count_comment = cursor_event.execute(get_event_photo_comment_count_query,get_event_photo_comment_count_data)

			if count_comment > 0:

				event_photo_comment_data =  cursor_event.fetchone()
				event_photo_tag_list_data[etkey]['total_comment_count'] = event_photo_comment_data['event_photo_comment_count']
			else:
				event_photo_tag_list_data[etkey]['total_comment_count'] = 0

			get_event_photo_tag_query = ("""SELECT `photo_user_id` as `user_id`
							FROM `tagged_event_photo`														
							where `event_photo_id` = %s""")		
			get_event_photo_tag_data = (etdata['event_photo_id'])	
			event_photo_tag_count = cursor_event.execute(get_event_photo_tag_query,get_event_photo_tag_data)
			event_photo_tag = cursor_event.fetchall()

			for tkey,tdata in enumerate(event_photo_tag):
				get_tag_user_information_query = ("""SELECT `FIRST_NAME` as 'name' FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""")
				get_tag_user_information_data = (tdata['user_id'])
				tag_user_information_count = cursor.execute(get_tag_user_information_query,get_tag_user_information_data)

				if tag_user_information_count > 0:
					tag_user_information = cursor.fetchone()
					event_photo_tag[tkey]['name'] = tag_user_information['name']
				else:
					event_photo_tag[tkey]['name'] = ""

			event_photo_tag_list_data[etkey]['photo_tag_list'] = event_photo_tag

		if len(event_photo_data) == 0:
			event_photo_data = event_photo_tag_list_data
		elif len(event_photo_tag_list_data) == 0:
			event_photo_data = event_photo_data
		else:
			event_photo_data = event_photo_data + event_photo_tag_list_data

		get_event_tag_query = ("""SELECT `tagged_user_id` as `user_id`
							FROM `tagged_event_photo`														
							where `event_id` = %s  and `photo_user_id` = %s GROUP BY `tagged_user_id`""")		
		get_event_tag_data = (event_id,user_id)	
		event_tag_count = cursor_event.execute(get_event_tag_query,get_event_tag_data)
		event_tag_user_list = cursor_event.fetchall()

		for etkey,etdata in enumerate(event_tag_user_list):
			get_tag_user_information_query = ("""SELECT `FIRST_NAME` as 'name' FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""")
			get_tag_user_information_data = (etdata['user_id'])
			tag_user_information_count = cursor.execute(get_tag_user_information_query,get_tag_user_information_data)

			if tag_user_information_count > 0:
				tag_user_information = cursor.fetchone()
				event_tag_user_list[etkey]['name'] = tag_user_information['name']
			else:
				event_tag_user_list[etkey]['name'] = ""

		get_event_tag_another_query = ("""SELECT `photo_user_id` as `user_id`
							FROM `tagged_event_photo`														
							where `event_id` = %s  and `tagged_user_id` = %s GROUP BY `photo_user_id`""")		
		get_event_tag_another_data = (event_id,user_id)	
		event_tag_count = cursor_event.execute(get_event_tag_another_query,get_event_tag_another_data)
		event_tag_another_user_list = cursor_event.fetchall()

		for etakey,etadata in enumerate(event_tag_another_user_list):
			get_tag_user_information_query = ("""SELECT `FIRST_NAME` as 'name' FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""")
			get_tag_user_information_data = (etadata['user_id'])
			tag_user_information_count = cursor.execute(get_tag_user_information_query,get_tag_user_information_data)

			if tag_user_information_count > 0:
				tag_user_information = cursor.fetchone()
				event_tag_another_user_list[etakey]['name'] = tag_user_information['name']
			else:
				event_tag_another_user_list[etakey]['name'] = ""

		if len(event_tag_user_list) == 0:
			event_tag_user_list = event_tag_another_user_list
		elif len(event_tag_another_user_list) == 0:
			event_tag_user_list = event_tag_user_list
		else:
			event_tag_user_list = event_tag_user_list + event_tag_another_user_list
		

		return ({"attributes": {
					    "status_desc": "event_photo_details",
					    "status": "success",
					    "tagged_user_list":event_tag_user_list
				},
				"responseList":event_photo_data}), status.HTTP_200_OK

#----------------------Get-Event-Photo-List---------------------#

#----------------------Tag-Event-Photo--------------------#

@name_space_event_photo.route("/TagEventPhoto")
class TagEventPhoto(Resource):
	@api.expect(tag_photo_postmodel)
	def post(self):
		connection = connect_logindb()
		cursor = connection.cursor()

		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		details = request.get_json()

		event_photo_id = details['event_photo_id']
		tagged_user_ids = details.get('tagged_user_id',[])		
		is_tagged = details['is_tagged']
		photo_user_id = details['photo_user_id']

		get_query = ("""SELECT *
				FROM `event_photos` ep				
				WHERE  ep.`event_photo_id` = %s""")
		get_data = (event_photo_id)
		count_event_photo = cursor_event.execute(get_query,get_data)
		

		if count_event_photo > 0:
			evnet_photo_data = cursor_event.fetchone()
			event_id = evnet_photo_data['event_id']
		else:
			event_id = 0

		for key,tagged_user_id in enumerate(tagged_user_ids):
			if is_tagged == 1:
				get_tag_image_query = ("""SELECT *
									  FROM `tagged_event_photo` tep where tep.`event_photo_id` = %s and tep.`tagged_user_id` = %s""")
				get_tag_image_data = (event_photo_id,tagged_user_id)
				tag_image_count = cursor_event.execute(get_tag_image_query,get_tag_image_data)

				if tag_image_count < 1:				
					insert_query = ("""INSERT INTO `tagged_event_photo`(`event_photo_id`,`event_id`,`photo_user_id`,`tagged_user_id`) 
								VALUES(%s,%s,%s,%s)""")
					data = (event_photo_id,event_id,photo_user_id,tagged_user_id)
					cursor_event.execute(insert_query,data)

					get_image_query = ("""SELECT *
										  FROM `event_photos` ep where ep.`event_photo_id` = %s""")
					get_image_data = (event_photo_id)
					image_count = cursor_event.execute(get_image_query,get_image_data)
					image_data = cursor_event.fetchone()

					headers = {'Content-type':'application/json', 'Accept':'application/json'}
					sendAppPushNotificationUrl = BASE_URL + "social_photo/SocialPhoto/sendNotifications"

					payloadpushData = {										
											"text":"Tagged Successfully",
											"title":"Tagged Your Photo",
											"image":image_data['image'],
											"user_id":photo_user_id
									  }
					print(payloadpushData)

					send_push_notification = requests.post(sendAppPushNotificationUrl,data=json.dumps(payloadpushData), headers=headers).json()


			else:
				delete_query = ("""DELETE FROM `tagged_event_photo` WHERE `event_photo_id` = %s and `tagged_user_id` = %s""")
				delData = (event_photo_id,tagged_user_id)
				
				cursor_event.execute(delete_query,delData)

			connection_event.commit()
			cursor_event.close()

		return ({"attributes": {
					    "status_desc": "tag_event_photo",
					    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK

#----------------------Tag-Event-Photo--------------------#

#----------------------Event-Photo-List-With-Tagged-User-and-user-Id--------------------#

@name_space_event_photo.route("/EventPhotoListwithTaggeduseridandUserId/<int:user_id>/<int:event_id>/<int:tagged_by_user_id>")	
class EventPhotoListwithTaggeduseridandUserId(Resource):
	def get(self,user_id,event_id,tagged_by_user_id):
		connection = connect_logindb()
		cursor = connection.cursor()

		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		get_query = ("""SELECT ep.*
							FROM `tagged_event_photo` tep
							INNER JOIN  `event_photos` ep ON ep.`event_photo_id` = tep.`event_photo_id` 
							INNER JOIN `event` e ON e.`event_id` = tep.`event_id`							
							where tep.`photo_user_id` = %s and tep.`event_id` = %s and tep.`tagged_user_id` = %s order by event_photo_id desc""")
		get_data = (user_id,event_id,tagged_by_user_id)
		count_event_photo = cursor_event.execute(get_query,get_data)

		if count_event_photo > 0:
			event_photo_data = cursor_event.fetchall()
			for key,data in enumerate(event_photo_data):
				event_photo_data[key]['last_update_ts'] = str(data['last_update_ts'])

				get_user_information_query = ("""SELECT `IMAGE_URL` as 'profile_image' , `FIRST_NAME` as 'name' FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""")
				get_user_information_data = (data['client_id'])
				user_information_count = cursor.execute(get_user_information_query,get_user_information_data)

				if user_information_count > 0:
					user_information = cursor.fetchone()
					event_photo_data[key]['name'] = user_information['name']
					if user_information['profile_image'] is None:
						event_photo_data[key]['profile_image'] = ""
					else:
						event_photo_data[key]['profile_image'] = user_information['profile_image']
				else:
					event_photo_data[key]['name'] = ""
					event_photo_data[key]['profile_image'] = ""

				get_event_photo_like_count_query = ("""SELECT count(*) event_photo_like_count
							FROM `event_photo_like` epl							
							where epl.`event_photo_id` = %s""")
				get_event_photo_like_count_data = (data['event_photo_id'])
				count_like = cursor_event.execute(get_event_photo_like_count_query,get_event_photo_like_count_data)

				if count_like > 0:

					event_photo_like_data =  cursor_event.fetchone()
					event_photo_data[key]['total_like_count'] = event_photo_like_data['event_photo_like_count']
				else:
					event_photo_data[key]['total_like_count'] = 0

				get_event_photo_comment_count_query = ("""SELECT count(*) event_photo_comment_count
								FROM `event_photo_comments` epc							
								where epc.`event_photo_id` = %s""")
				get_event_photo_comment_count_data = (data['event_photo_id'])
				count_comment = cursor_event.execute(get_event_photo_comment_count_query,get_event_photo_comment_count_data)

				if count_comment > 0:

					event_photo_comment_data =  cursor_event.fetchone()
					event_photo_data[key]['total_comment_count'] = event_photo_comment_data['event_photo_comment_count']
				else:
					event_photo_data[key]['total_comment_count'] = 0

				get_event_photo_tag_query = ("""SELECT `tagged_user_id` as `user_id`
							FROM `tagged_event_photo`														
							where `event_photo_id` = %s""")		
				get_event_photo_tag_data = (data['event_photo_id'])	
				event_photo_tag_count = cursor_event.execute(get_event_photo_tag_query,get_event_photo_tag_data)
				event_photo_tag = cursor_event.fetchall()

				for tkey,tdata in enumerate(event_photo_tag):
					get_tag_user_information_query = ("""SELECT `FIRST_NAME` as 'name' FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""")
					get_tag_user_information_data = (tdata['user_id'])
					tag_user_information_count = cursor.execute(get_tag_user_information_query,get_tag_user_information_data)

					if tag_user_information_count > 0:
						tag_user_information = cursor.fetchone()
						event_photo_tag[tkey]['name'] = tag_user_information['name']
					else:
						event_photo_tag[tkey]['name'] = ""

				event_photo_data[key]['photo_tag_list'] = event_photo_tag
			

			get_event_tag_query = ("""SELECT `tagged_user_id` as `user_id`
							FROM `tagged_event_photo`														
							where `event_id` = %s  and `photo_user_id` = %s GROUP BY `tagged_user_id`""")		
			get_event_tag_data = (event_id,user_id)	
			event_tag_count = cursor_event.execute(get_event_tag_query,get_event_tag_data)
			event_tag_user_list = cursor_event.fetchall()

			for etkey,etdata in enumerate(event_tag_user_list):
				get_tag_user_information_query = ("""SELECT `FIRST_NAME` as 'name' FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""")
				get_tag_user_information_data = (etdata['user_id'])
				tag_user_information_count = cursor.execute(get_tag_user_information_query,get_tag_user_information_data)

				if tag_user_information_count > 0:
					tag_user_information = cursor.fetchone()
					event_tag_user_list[etkey]['name'] = tag_user_information['name']
				else:
					event_tag_user_list[etkey]['name'] = ""
		
			return ({"attributes": {
						    "status_desc": "event_details",
						    "status": "success",
						    "tagged_user_list":event_tag_user_list
					},
					"responseList":event_photo_data}), status.HTTP_200_OK
		else:
			get_query = ("""SELECT ep.*
							FROM `tagged_event_photo` tep
							INNER JOIN  `event_photos` ep ON ep.`event_photo_id` = tep.`event_photo_id` 
							INNER JOIN `event` e ON e.`event_id` = tep.`event_id`							
							where tep.`photo_user_id` = %s and tep.`event_id` = %s and tep.`tagged_user_id` = %s order by event_photo_id desc""")
			get_data = (tagged_by_user_id,event_id,user_id)
			count_event_photo = cursor_event.execute(get_query,get_data)

			if count_event_photo > 0:
				event_photo_data = cursor_event.fetchall()
				for key,data in enumerate(event_photo_data):
					event_photo_data[key]['last_update_ts'] = str(data['last_update_ts'])

					get_user_information_query = ("""SELECT `IMAGE_URL` as 'profile_image' , `FIRST_NAME` as 'name' FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""")
					get_user_information_data = (data['client_id'])
					user_information_count = cursor.execute(get_user_information_query,get_user_information_data)

					if user_information_count > 0:
						user_information = cursor.fetchone()
						event_photo_data[key]['name'] = user_information['name']
						if user_information['profile_image'] is None:
							event_photo_data[key]['profile_image'] = ""
						else:
							event_photo_data[key]['profile_image'] = user_information['profile_image']
					else:
						event_photo_data[key]['name'] = ""
						event_photo_data[key]['profile_image'] = ""

					get_event_photo_like_count_query = ("""SELECT count(*) event_photo_like_count
							FROM `event_photo_like` epl							
							where epl.`event_photo_id` = %s""")
					get_event_photo_like_count_data = (data['event_photo_id'])
					count_like = cursor_event.execute(get_event_photo_like_count_query,get_event_photo_like_count_data)

					if count_like > 0:

						event_photo_like_data =  cursor_event.fetchone()
						event_photo_data[key]['total_like_count'] = event_photo_like_data['event_photo_like_count']
					else:
						event_photo_data[key]['total_like_count'] = 0

					get_event_photo_comment_count_query = ("""SELECT count(*) event_photo_comment_count
									FROM `event_photo_comments` epc							
									where epc.`event_photo_id` = %s""")
					get_event_photo_comment_count_data = (data['event_photo_id'])
					count_comment = cursor_event.execute(get_event_photo_comment_count_query,get_event_photo_comment_count_data)

					if count_comment > 0:

						event_photo_comment_data =  cursor_event.fetchone()
						event_photo_data[key]['total_comment_count'] = event_photo_comment_data['event_photo_comment_count']
					else:
						event_photo_data[key]['total_comment_count'] = 0

					get_event_photo_tag_query = ("""SELECT `photo_user_id` as `user_id`
							FROM `tagged_event_photo`														
							where `event_photo_id` = %s""")		
					get_event_photo_tag_data = (data['event_photo_id'])	
					event_photo_tag_count = cursor_event.execute(get_event_photo_tag_query,get_event_photo_tag_data)
					event_photo_tag = cursor_event.fetchall()

					for tkey,tdata in enumerate(event_photo_tag):
						get_tag_user_information_query = ("""SELECT `FIRST_NAME` as 'name' FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""")
						get_tag_user_information_data = (tdata['user_id'])
						tag_user_information_count = cursor.execute(get_tag_user_information_query,get_tag_user_information_data)

						if tag_user_information_count > 0:
							tag_user_information = cursor.fetchone()
							event_photo_tag[tkey]['name'] = tag_user_information['name']
						else:
							event_photo_tag[tkey]['name'] = ""

					event_photo_data[key]['photo_tag_list'] = event_photo_tag

				get_event_tag_another_query = ("""SELECT `photo_user_id` as `user_id`
							FROM `tagged_event_photo`														
							where `event_id` = %s  and `tagged_user_id` = %s GROUP BY `photo_user_id`""")		
				get_event_tag_another_data = (event_id,user_id)	
				event_tag_count = cursor_event.execute(get_event_tag_another_query,get_event_tag_another_data)
				event_tag_another_user_list = cursor_event.fetchall()

				for etakey,etadata in enumerate(event_tag_another_user_list):
					get_tag_user_information_query = ("""SELECT `FIRST_NAME` as 'name' FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""")
					get_tag_user_information_data = (etadata['user_id'])
					tag_user_information_count = cursor.execute(get_tag_user_information_query,get_tag_user_information_data)

					if tag_user_information_count > 0:
						tag_user_information = cursor.fetchone()
						event_tag_another_user_list[etakey]['name'] = tag_user_information['name']
					else:
						event_tag_another_user_list[etakey]['name'] = ""
		
				return ({"attributes": {
							    "status_desc": "event_details",
							    "status": "success",
							    "tagged_user_list":event_tag_another_user_list
						},
						"responseList":event_photo_data}), status.HTTP_200_OK

#----------------------Event-Photo-List-With-Tagged-User-and-user-Id--------------------#

#----------------------Comment-List-By-Event-Photo-Id---------------------#

@name_space_event_photo.route("/commentListByEventPhotoId/<int:event_photo_id>")	
class commentListByEventPhotoId(Resource):
	def get(self,event_photo_id):
		connection = connect_logindb()
		cursor = connection.cursor()

		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		get_query = ("""SELECT *
							FROM `event_photo_comments`							
							where `event_photo_id` = %s order by event_photo_id desc""")
		get_data = (event_photo_id)
		cursor_event.execute(get_query,get_data)

		comment_data = cursor_event.fetchall()

		for key,data in enumerate(comment_data):
			comment_data[key]['last_update_ts'] = str(data['last_update_ts'])	

			get_user_information_query = ("""SELECT `IMAGE_URL` as 'profile_image' , `FIRST_NAME` as 'name' FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""")
			get_user_information_data = (data['user_id'])
			user_information_count = cursor.execute(get_user_information_query,get_user_information_data)

			if user_information_count > 0:
				user_information = cursor.fetchone()
				comment_data[key]['name'] = user_information['name']
				if user_information['profile_image'] is None:
					comment_data[key]['profile_image'] = ""
				else:
					comment_data[key]['profile_image'] = user_information['profile_image']
			else:
				comment_data[key]['name'] = ""
				comment_data[key]['profile_image'] = ""

		return ({"attributes": {
					    "status_desc": "event_comment_details",
					    "status": "success"
				},
				"responseList":comment_data}), status.HTTP_200_OK
		

#----------------------Comment-List-By-Event-Photo-Id---------------------#

#----------------------Delete-Event-Image---------------------#

@name_space_event_photo.route("/deleteEventImage/<int:event_photo_id>")
class deleteEventImage(Resource):
	def delete(self, event_photo_id):
		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		delete_query = ("""DELETE FROM `event_photos` WHERE `event_photo_id` = %s """)
		delData = (event_photo_id)		
		cursor_event.execute(delete_query,delData)

		delete_like_query = ("""DELETE FROM `event_photo_like` WHERE `event_photo_id` = %s """)
		delLikeData = (event_photo_id)		
		cursor_event.execute(delete_like_query,delLikeData)

		delete_tag_query = ("""DELETE FROM `tagged_event_photo` WHERE `event_photo_id` = %s """)
		delTagData = (event_photo_id)		
		cursor_event.execute(delete_tag_query,delTagData)

		delete_comment_query = ("""DELETE FROM `event_photo_comments` WHERE `event_photo_id` = %s """)
		delCommentData = (event_photo_id)		
		cursor_event.execute(delete_comment_query,delCommentData)

		connection_event.commit()
		cursor_event.close()
		
		return ({"attributes": {"status_desc": "Delete Image",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Event-Image---------------------#

#----------------------Get-User-List-By-Event-Id--------------------#

@name_space_event_photo.route("/UserListByEventId/<int:event_id>/<int:user_id>")	
class UserListByEventId(Resource):
	def get(self,event_id,user_id):
		connection = connect_logindb()
		cursor = connection.cursor()

		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		get_user_list_query = ("""SELECT *
							FROM `event_photos` 													
							where `event_id` = %s""")
		get_user_list_data = (event_id)
		user_list_count = cursor_event.execute(get_user_list_query,get_user_list_data)

		new_user_list = []

		user_list = cursor_event.fetchall()

		for key,data in enumerate(user_list):
			if data['guest_id'] == 0:
				get_user_information_query = ("""SELECT `IMAGE_URL` as 'profile_image' , `FIRST_NAME` as 'name' FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""")
				get_user_information_data = (data['client_id'])
				user_information_count = cursor.execute(get_user_information_query,get_user_information_data)

				if user_information_count > 0:
					user_information = cursor.fetchone()
					user_list[key]['user_id'] = data['client_id']
					user_list[key]['name'] = user_information['name']
					if user_information['profile_image'] is None:
						user_list[key]['profile_image'] = ""
					else:
						user_list[key]['profile_image'] = user_information['profile_image']
				else:
					user_list[key]['name'] = ""
					user_list[key]['profile_image'] = ""
			else:
				get_user_information_query = ("""SELECT `IMAGE_URL` as 'profile_image' , `FIRST_NAME` as 'name' FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""")
				get_user_information_data = (data['guest_id'])
				user_information_count = cursor.execute(get_user_information_query,get_user_information_data)

				if user_information_count > 0:
					user_information = cursor.fetchone()
					user_list[key]['user_id'] = data['guest_id']
					user_list[key]['name'] = user_information['name']
					if user_information['profile_image'] is None:
						user_list[key]['profile_image'] = ""
					else:
						user_list[key]['profile_image'] = user_information['profile_image']
				else:
					user_list[key]['name'] = ""
					user_list[key]['profile_image'] = ""

			if data['guest_id'] == 0:
				if data['client_id'] != user_id:
					new_user_list.append({"user_id":data['client_id'],"name":data['name']})
			else:
				if data['guest_id'] != user_id:
					new_user_list.append({"user_id":data['guest_id'],"name":data['name']})

		return ({"attributes": {
					    "status_desc": "user_list",
					    "status": "success"
				},
				"responseList":new_user_list}), status.HTTP_200_OK


#----------------------Get-User-List-By-Event-Id--------------------#

#----------------------Add-Content--------------------#

@name_space_content.route("/AddContent")
class AddContent(Resource):
	@api.expect(content_postmodel)
	def post(self):
		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		details = request.get_json()

		content_link = details['content_link']
		content_name = details['content_name']
		user_id = details['user_id']
		role = details['role']

		insert_query = ("""INSERT INTO `content`(`content_link`,`content_name`,`user_id`,`role`) 
								VALUES(%s,%s,%s,%s)""")
		data = (content_link,content_name,user_id,role)
		cursor_event.execute(insert_query,data)


		return ({"attributes": {
					    "status_desc": "content_details",
					    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK



#----------------------Add-Content--------------------#

#----------------------Add-Content--------------------#

@name_space_content.route("/AssignContent")
class AssignContent(Resource):
	@api.expect(assign_content_postmodel)
	def post(self):
		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		details = request.get_json()

		content_id = details['content_id']
		user_ids = details.get('user_id',[])	

		for key,user_id in enumerate(user_ids):			
			get_query = ("""SELECT *
				FROM `content` WHERE `content_id` = %s""")
			getData = (content_id)
			content_count = cursor_event.execute(get_query,getData)

			if content_count > 0:
				content_data = cursor_event.fetchone()
				insert_query = ("""INSERT INTO `assign_content`(`content_id`,`content_user_id`,`assign_user_id`) 
										VALUES(%s,%s,%s)""")
				data = (content_id,content_data['user_id'],user_id)
				cursor_event.execute(insert_query,data)
			else:
				print('error')


		return ({"attributes": {
					    "status_desc": "content_details",
					    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK



#----------------------Add-Content--------------------#

#----------------------Get-Content-List--------------------#

@name_space_content.route("/getContentList/<int:user_id>")	
class getContentList(Resource):
	def get(self,user_id):
		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		connection = connect_logindb()
		cursor = connection.cursor()

		get_user_content_query = ("""SELECT * FROM content where `user_id` = %s""")
		user_content_data = (user_id)
		count_user_content = cursor_event.execute(get_user_content_query,user_content_data)
		user_content = cursor_event.fetchall()

		get_assign_content_query = ("""SELECT c.* FROM `assign_content` ac									  
									   INNER JOIN `content` c ON c.`content_id` = ac.`content_id`
									   where ac.`assign_user_id` = %s""")
		get_assign_content_data = (user_id)
		count_assign_content =  cursor_event.execute(get_assign_content_query,get_assign_content_data)
		assigned_user_content = cursor_event.fetchall()

		if len(user_content) == 0:
			user_content = assigned_user_content
		elif len(assigned_user_content) == 0:
			user_content = user_content
		else:
			user_content = user_content + assigned_user_content

		for key,data in enumerate(user_content):
			user_content[key]['last_update_ts'] = str(data['last_update_ts'])

			get_user_information_query = ("""SELECT `IMAGE_URL` as 'profile_image' , `FIRST_NAME` as 'name' FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""")
			get_user_information_data = (data['user_id'])
			user_information_count = cursor.execute(get_user_information_query,get_user_information_data)

			if user_information_count > 0:
				user_information = cursor.fetchone()				
				user_content[key]['name'] = user_information['name']
				if user_information['profile_image'] is None:
					user_content[key]['profile_image'] = ""
				else:
					user_content[key]['profile_image'] = user_information['profile_image']
			else:
				user_content[key]['name'] = ""
				user_content[key]['profile_image'] = ""



		return ({"attributes": {
					    "status_desc": "content_list",
					    "status": "success"
				},
				"responseList":user_content}), status.HTTP_200_OK

#----------------------Get-Content-List--------------------#

#----------------------Get-Assign-User-List--------------------#

@name_space_content.route("/getAssignUsertList/<int:content_id>")	
class getAssignUsertList(Resource):
	def get(self,content_id):
		connection_event = mysql_connection()
		cursor_event = connection_event.cursor()

		connection = connect_logindb()
		cursor = connection.cursor()

		get_assign_user_query = ("""SELECT * FROM `assign_content`									  
									   where `content_id` = %s""")
		get_assign_user_data = (content_id)
		count_assign_user =  cursor_event.execute(get_assign_user_query,get_assign_user_data)
		assign_user = cursor_event.fetchall()

		for key,data in enumerate(assign_user):
			assign_user[key]['last_update_ts'] = str(data['last_update_ts'])

			get_user_query = ("""SELECT iuc.`INSTITUTION_USER_ID`,iuc.`INSTITUTION_USER_NAME`,iuc.`INSTITUTION_USER_PASSWORD`,iuc.`FIRST_NAME`,iuc.`LAST_NAME`,iuc.`PRIMARY_CONTACT_NUMBER`
						FROM `institution_user_credential` iuc
						WHERE `INSTITUTION_USER_ID` = %s""")
			get_user_data = (data['assign_user_id'])
			user_count = cursor.execute(get_user_query,get_user_data)

			if user_count > 0:
				user_data = cursor.fetchone()
				print(user_data)
				assign_user[key]['INSTITUTION_USER_ID'] = user_data['INSTITUTION_USER_ID']
				assign_user[key]['INSTITUTION_USER_NAME'] = user_data['INSTITUTION_USER_NAME']
				assign_user[key]['INSTITUTION_USEINSTITUTION_USER_PASSWORDR_NAME'] = user_data['INSTITUTION_USER_PASSWORD']
				assign_user[key]['FIRST_NAME'] = user_data['FIRST_NAME']
				assign_user[key]['LAST_NAME'] = user_data['LAST_NAME']
				assign_user[key]['PRIMARY_CONTACT_NUMBER'] = user_data['PRIMARY_CONTACT_NUMBER']
			else:
				assign_user[key]['INSTITUTION_USER_ID'] = 0
				assign_user[key]['INSTITUTION_USER_NAME'] = ""
				assign_user[key]['INSTITUTION_USEINSTITUTION_USER_PASSWORDR_NAME'] = ""
				assign_user[key]['FIRST_NAME'] = ""
				assign_user[key]['LAST_NAME'] = ""
				assign_user[key]['PRIMARY_CONTACT_NUMBER'] = ""

		return ({"attributes": {
					    "status_desc": "user_list",
					    "status": "success"
				},
				"responseList":assign_user}), status.HTTP_200_OK

#----------------------Get-Assign-User-List--------------------#

#----------------------Send-Push-Notification---------------------#

@name_space.route("/sendAppPushNotifications")
class sendAppPushNotifications(Resource):
	@api.expect(appmsg_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		data_message = {
							"title" : details['title'],
							"message": details['text']
						}
		api_key = "AAAA66tddZI:APA91bG89PrDCMns8-RSyLHUBiyu8VO1Kj9lchokDygCPg6NeRB59yD0sKXIe2xviw1XGraugdm9T8obOcGwf8tD_fiBVhHzAR_H186SNN88nEtOPxkFt7GQoyXVD91mt_3pVEeVwOb1"
		device_id = details.get('device_id')
		push_service = FCMNotification(api_key=api_key)
		msgResponse = push_service.notify_single_device(registration_id=device_id,data_message = data_message)
		sent = 'N'
		if msgResponse.get('success') == 1:
			sent = 'Y'
		
		
		connection.commit()
		cursor.close()

		return ({"attributes": {
				    		"status_desc": "Push Notification",
				    		"status": "success"
				    	},
				    	"responseList":msgResponse}), status.HTTP_200_OK
#----------------------Send-Push-Notification---------------------#

def random_string(letter_count, digit_count):  
    str1 = ''.join((random.choice(string.ascii_letters) for x in range(letter_count)))  
    str1 += ''.join((random.choice(string.digits) for x in range(digit_count)))  
  
    sam_list = list(str1) # it converts the string to list.  
    random.shuffle(sam_list) # It uses a random.shuffle() function to shuffle the string.  
    final_string = ''.join(sam_list)  
    return final_string