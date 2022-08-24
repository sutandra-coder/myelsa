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
student_favorite = Blueprint('favorite_api', __name__)
api = Api(student_favorite, version='1.0', title='MyElsa API',
    description='MyElsa API')
name_space = api.namespace('StudentFavorite', description='Student Favorite')

app.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app.config['MYSQL_DATABASE_DB'] = 'creamson_lab_lang1'
app.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'
mysql.init_app(app)

app.config['CORS_HEADERS'] = 'Content-Type'

favorite_post = api.model('favoritePost', {
	"user_id":fields.Integer(required=True),
	"status":fields.String(required=True),
	"content_detail_id":fields.Integer(required=True)})

@name_space.route("/favoriteContent")
class favoriteContent(Resource):
	@name_space.expect(favorite_post)
	def post(self):
		details = request.get_json()
		connection = mysql.connect()
		cursor = connection.cursor()
		user_id = details['user_id']
		content_status = details['status']
		content_detail_id = details['content_detail_id']
		try:
			student_favorite_insert_query = ("""INSERT INTO `student_favourite`(`User_Id`, `Status`, 
				`content_detail_id`) VALUES(%s,%s,%s)""")
			student_favorite_data = (user_id,content_status,content_detail_id)
			cursor.execute(student_favorite_insert_query,student_favorite_data)
		except:
			pass
		connection.commit()
		details['favorite_id'] = cursor.lastrowid
		cursor.close()
		return ({"attributes": {
		    				"status_desc": "Favotite Content Details.",
		    				"status": "success"
		    				},
		    				"responseList":{"FavoriteDtls":details}}), status.HTTP_200_OK

if __name__ == '__main__':
	app.run(host='0.0.0.0',debug=True)