from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests

app = Flask(__name__)
cors = CORS(app)
mysql = MySQL()
time_discount = Blueprint('time_discount_api', __name__)
api = Api(time_discount, version='1.0', title='MyElsa API',
    description='MyElsa API')
name_space = api.namespace('YRBProductDiscount', description='YRB Product Discount')
name_space1 = api.namespace('ProductDiscount', description='Product Discount')
app.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app.config['MYSQL_DATABASE_DB'] = 'creamson_logindb'
app.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'
mysql.init_app(app)

app.config['CORS_HEADERS'] = 'Content-Type'

postTime_post = api.model('postTime', {
	"user_id":fields.Integer(required=True),
	"product_code":fields.String(required=True)})

@name_space.route("/postTime")
class postTime(Resource):
	@name_space.expect(postTime_post)
	def post(self):
		details = request.get_json()
		connection = mysql.connect()
		cursor = connection.cursor()
		user_id = details['user_id']
		product_code = details['product_code']
		current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		try:
			user_time_insert_query = ("""INSERT INTO `user_time_mapping`(`user_id`, `product_code`, `system_time`) 
				VALUES(%s,%s,%s)""")
			user_time_data = (user_id,product_code,current_time)
			cursor.execute(user_time_insert_query,user_time_data)
		except:
			pass
		cursor.close()

		return ({"attributes": {
		    				"status_desc": "User Time Details.",
		    				"status": "success"
		    				},
		    				"responseList":{"UserTimeDtls":details}}), status.HTTP_200_OK


@name_space.route("/getTimeAndDiscount/<int:user_id>/<string:product_code>")
class getTimeAndDiscount(Resource):
	def get(self,user_id,product_code):
		connection = mysql.connect()
		cursor = connection.cursor()
		current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		fmt = '%Y-%m-%d %H:%M:%S'
		current_time = datetime.strptime(current_time, fmt)
		details = {"is_eligible":'',
					"discount":'',
					"timeleft":'',
					"price":''}

		message = 'Invalid Code'
		time = None
		discount = None
		cursor.execute("""SELECT `time`, `discount` FROM `product_time_mapping` 
				WHERE `product_code` = %s""",(product_code.lower()))
		product_dtls = cursor.fetchall()
		if len(product_dtls) != 0:
			product_dtls = product_dtls[0]
			time = product_dtls[0]*60
			discount = product_dtls[1]

		cursor.execute("""SELECT `Product_Price` FROM `product`
		 WHERE `Product_CODE` = %s""",(product_code))
		product_price = cursor.fetchall()
		if len(product_price) != 0:
			product_price = product_price[0]
			price = product_price[0]
			print(price)
		
		if time == None and discount == None:
			details = {"is_eligible":'',
					"discount":'',
					"timeleft":'',
					"price":''}

			message = 'Invalid Code'
		else:
			details = {"is_eligible":'y',
						"discount":discount,
						"timeleft":time,
						"price":price}

			message = 'Valid Code'


		
		try:
			cursor.execute("""SELECT `system_time` FROM `user_time_mapping` 
				WHERE `user_id` = %s and `product_code` = %s 
				ORDER BY system_time ASC LIMIT 1""",(user_id,product_code))
			last_time = cursor.fetchone()[0]
			time_diff = current_time - last_time
			total_mins = round((time_diff.total_seconds() / 60),2)
			total_secs = total_mins*60
			if total_secs <= time:
				timeleft = round((time - total_secs),0)
				details = {"is_eligible":'y',
							"discount":discount,
							"timeleft":timeleft,
							"price":price}

				message = 'Valid Code'
			else:
				details = {"is_eligible":'n',
							"discount":'',
							"timeleft":0,
							"price":price}

				message = 'Valid Code'
		except:
			pass
		cursor.close()
		return ({"attributes": {
		    				"status_desc": "Product Discount Details.",
		    				"status": "success",
		    				"message":message
		    				},
		    				"responseList":{"ProductDiscountDtls":details}}), status.HTTP_200_OK


@name_space.route("/getTodaysContest/<string:start_date>/<string:contest_desc>")
class getTodaysContest(Resource):
	def get(self,start_date,contest_desc):
		connection = mysql.connect()
		cursor = connection.cursor()

		cursor.execute("""SELECT `Contest_ID` FROM `contest_table` WHERE `Start_Date` = %s
		 AND `Contest_Description` LIKE %s""",(start_date,contest_desc))

		contest_id = cursor.fetchone()
		if contest_id:
			contest_id = contest_id[0]
		else:
			contest_id = ''

		cursor.close()
		return ({"attributes": {
	    				"status_desc": "ContestID Details.",
	    				"status": "success"
	    				},
	    				"responseList":{"ContestID":contest_id}}), status.HTTP_200_OK


@name_space1.route("/getSpecialUserDiscount/<int:user_id>/<string:product_code>")
class getSpecialUserDiscount(Resource):
	def get(self,user_id,product_code):
		connection = mysql.connect()
		cursor = connection.cursor()

		details = {"is_eligible":'',
					"discount":'',
					"price":''}

		
		discount = 0
		price = 0
		cursor.execute("""SELECT `discount` FROM `product_time_mapping` 
				WHERE `product_code` = %s and user_id = %s""",(product_code.lower(),user_id))

		product_dtls = cursor.fetchone()
		
		cursor.execute("""SELECT `Product_Price` FROM `product`
		 WHERE `Product_CODE` = %s""",(product_code))
		product_price = cursor.fetchone()

		if product_price:
			price = product_price[0]

		if product_dtls:
			discount = product_dtls[0]

		if discount > 0:
			try:
				cursor.execute("""SELECT `system_time` FROM `user_time_mapping` 
					WHERE `user_id` = %s and `product_code` = %s 
					ORDER BY system_time ASC LIMIT 1""",(user_id,product_code))
				last_time = cursor.fetchone()

				if last_time:
					details = {"is_eligible":'n',
								"discount":0,
								"price":price}

					message = 'Valid Code'
				else:
					details = {"is_eligible":'y',
							"discount":discount,
							"price":price}

					message = 'Valid Code'
			except:
				pass
		else:
			details = {"is_eligible":'n',
						"discount":discount,
						"price":price}

			message = 'Valid Code'
		message = 'Invalid Code'
		cursor.close()

		return ({"attributes": {
		    				"status_desc": "Product Discount Details.",
		    				"status": "success",
		    				"message":message
		    				},
		    				"responseList":details}), status.HTTP_200_OK



if __name__ == '__main__':
	app.run(host='0.0.0.0',debug=True)