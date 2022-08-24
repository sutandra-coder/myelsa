from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests

app = Flask(__name__)
cors = CORS(app)
mysql = MySQL()
mock_test = Blueprint('mock_test_api', __name__)
api = Api(mock_test, version='1.0', title='MyElsa API',
    description='MyElsa API')
name_space = api.namespace('MockTest', description=':Mock Test')

app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'cbdHoRPQPRfTdC0uSPLt'
app.config['MYSQL_DATABASE_DB'] = 'creamson_logindb'
app.config['MYSQL_DATABASE_HOST'] = 'myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com'
mysql.init_app(app)

app.config['CORS_HEADERS'] = 'Content-Type'

mocktest_model = api.model('Mock Test', {
	"user_id":fields.Integer(required=True),
	"content_id":fields.Integer(required=True),
	"model_type":fields.String(required=True),
	"percentage":fields.Float(required=True)
	})


@name_space.route("/updateMockTestMarks")
class updateMockTestMarks(Resource):
	@api.expect(mocktest_model)
	def put(self):
		details = request.get_json()
		connection = mysql.connect()
		cursor = connection.cursor()
		user_id = details['user_id']
		content_id = details['content_id']
		model_type = details['model_type']
		percentage = details['percentage']

		cursor.execute("""SELECT `Id`,`total_marks`,`Last_Id` FROM `user_assessment_tracking` 
			WHERE `user_id` = %s AND `content_master_id` = %s 
			AND `type` = %s """,(user_id,content_id,model_type))

		marks = 0
		count = 0

		marks_dtls = cursor.fetchall()[0]
		print(marks_dtls[1],marks_dtls[2])
		if marks_dtls:
			idx = marks_dtls[0]
			marks = marks_dtls[1]
			count = marks_dtls[2]

		total_marks = marks + percentage
		total_count = count + 1

		total_percent = round((total_marks/total_count),2)

		percent_update_query = ("""UPDATE `user_assessment_tracking` SET `total_marks`= %s,
			`percentage`= %s,`Last_Id`=%s WHERE `Id` = %s""")
		percent_data = (total_marks,total_percent,total_count,idx)
		cursor.execute(percent_update_query,percent_data)
		cursor.close()
		details['total_marks'] = total_marks
		details['total_tests'] = total_count
		details['total_percentage'] = total_percent

		return ({"attributes": {
	    				"status_desc": "Student Assessment Percentage.",
	    				"status": "success"
	    				},
	    				"responseList":{"PercentageDtls":details}}), status.HTTP_200_OK



@name_space.route("/postMockTestMarks")
class postMockTestMarks(Resource):
	@api.expect(mocktest_model)
	def post(self):
		details = request.get_json()
		connection = mysql.connect()
		cursor = connection.cursor()
		user_id = details['user_id']
		content_id = details['content_id']
		model_type = details['model_type']
		percentage = details['percentage']

		cursor.execute("""SELECT `Id`,`total_marks`,`Last_Id` FROM `user_assessment_tracking` 
			WHERE `user_id` = %s AND `content_master_id` = %s 
			AND `type` = %s """,(user_id,content_id,model_type))

		marks = 0
		count = 0

		marks_dtls = cursor.fetchall()
		print(marks_dtls)
		if len(marks_dtls) == 0:
			total_marks = marks + percentage
			total_count = count + 1

			total_percent = round((total_marks/total_count),2)

			percent_insert_query = ("""INSERT INTO `user_assessment_tracking`(`user_id`, `content_master_id`, 
				`type`, `total_marks`, `percentage`, `Last_Id`) VALUES(%s,%s,%s,%s,%s,%s)""")
			percent_data = (user_id,content_id,model_type,total_marks,total_percent,total_count)
			cursor.execute(percent_insert_query,percent_data)
			cursor.close()
			details['total_marks'] = total_marks
			details['total_tests'] = total_count
			details['total_percentage'] = total_percent

			return ({"attributes": {
		    				"status_desc": "Student Assessment Percentage.",
		    				"status": "success"
		    				},
		    				"responseList":{"PercentageDtls":details}}), status.HTTP_200_OK
		else:
			marks_put_url = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/student_marks/MockTest/updateMockTestMarks'
			marks_put_data = details
			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			marks_put_res = requests.put(marks_put_url, data=json.dumps(marks_put_data),headers=headers)
			res = marks_put_res.json()
			return res
			print(res)

if __name__ == '__main__':
	app.run(host='0.0.0.0')