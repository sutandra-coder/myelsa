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
product_rating = Blueprint('product_rating_api', __name__)
api = Api(product_rating, version='1.0', title='MyElsa API',
    description='MyElsa API')
name_space = api.namespace('ProductRating', description='Product Rating')

'''app.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app.config['MYSQL_DATABASE_DB'] = 'creamson_logindb'
app.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'
'''

app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'cbdHoRPQPRfTdC0uSPLt'
app.config['MYSQL_DATABASE_DB'] = 'creamson_logindb'
app.config['MYSQL_DATABASE_HOST'] = 'myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com'

mysql.init_app(app)

app.config['CORS_HEADERS'] = 'Content-Type'

rating_post = api.model('rating_post', {
	"user_id":fields.Integer(required=True),
	"status":fields.String(),
	"rating":fields.Integer(),
	"product_code":fields.String(required=True)})

@name_space.route("/rateProductPost")
class rateProductPost(Resource):
	@name_space.expect(rating_post)
	def post(self):
		details = request.get_json()
		connection = mysql.connect()
		cursor = connection.cursor()
		user_id = details['user_id']
		fav_status = details['status']
		product_code = details['product_code']
		rating = details['rating']

		cursor.execute("""SELECT `id` FROM `product_rating` WHERE 
			`user_id` = %s and `product_code` = %s""",(user_id,product_code))

		idx = cursor.fetchone()
		# print(idx)
		if idx:
			idx = idx[0]
		else:
			idx = None

		if idx == None:
			product_rating_insert_query = ("""INSERT INTO `product_rating`(`user_id`, `product_code`, 
				`rating`, `status`) VALUES(%s,%s,%s,%s)""")
			product_rating_data = (user_id,product_code,rating,fav_status)
			cursor.execute(product_rating_insert_query,product_rating_data)
			connection.commit()
			details['rating_id'] = cursor.lastrowid


			cursor.execute("""SELECT avg(`rating`),COUNT(`product_code`) FROM product_rating 
					WHERE product_code = %s GROUP BY product_code""",(product_code))

			rating_data = cursor.fetchall()
			if rating_data:
				avg_rating = rating_data[0][0]
				noofrating = rating_data[0][1]
				avg_rating = 4.5
				noofrating = 12 + noofrating
				if noofrating < 20:
					avg_rating = 4.5
				if noofrating > 20:
					avg_rating = round((rating_data[0][0]),2)

			details['noofrating'] = noofrating
			details['avg_rating'] = avg_rating

			return ({"attributes": {
		    				"status_desc": "Product Rating Details.",
		    				"status": "success"
		    				},
		    				"responseList":{"RatingDtls":details}}), status.HTTP_200_OK

		else:
			# update_url = 'http://127.0.0.1:5000/product_rating/ProductRating/rateProductUpdate'
			update_url = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/product_rating/ProductRating/rateProductUpdate'
			update_data = details
			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			rating_put_res = requests.put(update_url, data=json.dumps(update_data),headers=headers)
			res = rating_put_res.json()
			print(res)
			return res
			
		
		connection.commit()
		cursor.close()

		

@name_space.route("/rateProductUpdate")
class rateProductUpdate(Resource):
	@name_space.expect(rating_post)
	def put(self):
		details = request.get_json()
		connection = mysql.connect()
		cursor = connection.cursor()
		user_id = details['user_id']
		fav_status = details['status']
		product_code = details['product_code']
		rating = details['rating']
		print(user_id,product_code)
		cursor.execute("""SELECT `id`,`rating`,`status` FROM `product_rating` WHERE 
			`user_id` = %s and `product_code` = %s""",(user_id,product_code))

		idx = cursor.fetchall()
		# print(idx)
		if idx:
			rating_id = idx[0][0]
			cursor.execute("""SELECT avg(`rating`),COUNT(`product_code`) FROM product_rating 
					WHERE product_code = %s GROUP BY product_code""",(product_code))

			rating_data = cursor.fetchall()
			if rating_data:
				avg_rating = rating_data[0][0]
				noofrating = rating_data[0][1]
				avg_rating = 4.5
				noofrating = 12 + noofrating
				if noofrating < 20:
					avg_rating = 4.5
				if noofrating > 20:
					avg_rating = round((rating_data[0][0]),2)

			details['noofrating'] = noofrating
			details['avg_rating'] = avg_rating
		if rating and not fav_status:
			update_rating_query = ("""UPDATE `product_rating` SET `rating`= %s 
				WHERE id = %s""")
			update_rating_data = (rating,rating_id)
			cursor.execute(update_rating_query,update_rating_data)
		elif fav_status and not rating:
			update_rating_query = ("""UPDATE `product_rating` SET `status`= %s 
				WHERE id = %s""")
			update_rating_data = (fav_status,rating_id)
			cursor.execute(update_rating_query,update_rating_data)

		elif fav_status and rating:
			update_rating_query = ("""UPDATE `product_rating` SET `rating`= %s,`status`= %s 
				WHERE id = %s""")
			update_rating_data = (rating,fav_status,rating_id)
			cursor.execute(update_rating_query,update_rating_data)
		else:
			user_rating = idx[0][1]
			user_fav_status = idx[0][2]
			update_rating_query = ("""UPDATE `product_rating` SET `rating`= %s ,`status`= %s 
				WHERE id = %s""")
			update_rating_data = (user_rating,user_fav_status,rating_id)
			cursor.execute(update_rating_query,update_rating_data)

		connection.commit()
		details['rating_id'] = rating_id
		cursor.close()
		return ({"attributes": {
		    				"status_desc": "Product Rating Details.",
		    				"status": "success"
		    				},
		    				"responseList":{"RatingDtls":details}}), status.HTTP_200_OK


@name_space.route("/getProductRatingAndLike/<int:user_id>/<string:product_code>")
class rateProductUpdate(Resource):
	def get(self,user_id,product_code):
		connection = mysql.connect()
		cursor = connection.cursor()
		details = {"avg_rating":4.5,
					"noofrating":12,
					"likes_count":0,
					"dislike_count":0,
					"user_rating":"",
					"user_vote":""}
		try:

			cursor.execute("""SELECT id FROM product_rating 
				WHERE product_code = %s""",(product_code))

			idx = cursor.fetchone()
			if idx:
				idx = idx[0]

			if idx:	
				cursor.execute("""SELECT avg(`rating`),COUNT(`product_code`) FROM product_rating 
					WHERE product_code = %s GROUP BY product_code""",(product_code))

				rating_data = cursor.fetchall()
				if rating_data:
					avg_rating = rating_data[0][0]
					noofrating = rating_data[0][1]
					avg_rating = 4.5
					noofrating = 12 + noofrating
					if noofrating < 20:
						avg_rating = 4.5
					if noofrating > 20:
						avg_rating = round((rating_data[0][0]),2)
				else:
					avg_rating = 0
					noofrating = 0
				

				cursor.execute("""SELECT COUNT(status) FROM product_rating WHERE 
					product_code = %s and status = 'l' GROUP BY product_code""",(product_code))

				like_data = cursor.fetchone()
				if like_data:
					likes_count = like_data[0]
				else:
					likes_count = 0

				cursor.execute("""SELECT COUNT(status) FROM product_rating WHERE 
					product_code = %s and status = 'd' GROUP BY product_code""",(product_code))

				dislike_data = cursor.fetchone()
				if dislike_data:
					dislike_count = dislike_data[0]
				else:
					dislike_count = 0

				cursor.execute("""SELECT `rating`,`status` FROM product_rating WHERE 
					product_code = %s and `user_id` = %s""",(product_code,user_id))

				user_data = cursor.fetchall()
				if user_data:
					user_rating = user_data[0][0]
					user_vote = user_data[0][1]
				else:
					user_rating = 0
					user_vote = ""
				# print(user_data)
				details = {"avg_rating":avg_rating,
					"noofrating":noofrating,
					"likes_count":likes_count,
					"dislike_count":dislike_count,
					"user_rating":user_rating,
					"user_vote":user_vote}
			
		except:
			pass
		

		return ({"attributes": {
		    				"status_desc": "Product Rating Details.",
		    				"status": "success"
		    				},
		    				"responseList":details}), status.HTTP_200_OK
		




if __name__ == '__main__':
	app.run(host='0.0.0.0',debug=True)