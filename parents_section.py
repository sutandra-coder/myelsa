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
app1 = Flask(__name__)
cors = CORS(app)
mysql = MySQL()
mysql1 = MySQL()
parents_service = Blueprint('parents_service_api', __name__)
api = Api(parents_service, version='1.0', title='myElsa User Tracking',
    description='myElsa User Tracking')
name_space = api.namespace('ParentsSection', description=':Parents Section')

app.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app.config['MYSQL_DATABASE_DB'] = 'creamson_logindb'
app.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'
mysql.init_app(app)


app1.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app1.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app1.config['MYSQL_DATABASE_DB'] = 'creamson_lab_lang1'
app1.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'
mysql1.init_app(app1)

app.config['CORS_HEADERS'] = 'Content-Type'

@name_space.route("/getChildListByParentId/<int:parent_userid>")
class getChildListByParentId(Resource):
    def get(self,parent_userid):
    	connection = mysql.connect()
    	cursor = connection.cursor()

    	conn = mysql1.connect()
    	cur = conn.cursor()
    	child_list = []
    	cursor.execute("""SELECT `INSTITUTION_USER_ID_STUDENT` FROM `guardian_dtls` 
    		WHERE `INSTITUTION_USER_ID_GUARDIAN` = %s""",(parent_userid))


    	child_id = cursor.fetchall()

    	for i in range(len(child_id)):

    		cursor.execute("""SELECT CONCAT(`FIRST_NAME`," ",`LAST_NAME`) , `image_url`
    			FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(child_id[i][0]))

    		child_name = cursor.fetchone()

    		if child_name:
    			name = child_name[0]
    			image_url = child_name[1]

    		cur.execute("""SELECT `Class`,`Board` FROM `student` 
    			WHERE `Student_UserID` = %s""",(child_id[i][0]))

    		child_class_and_board = cur.fetchone()
    		if child_class_and_board:
    			child_class = child_class_and_board[0]
    			child_board = child_class_and_board[1]

    		child_list.append({"child_userid":child_id[i][0],
    							"child_name":name,
    							"image_url":image_url,
    							"child_class":child_class,
    							"child_board":child_board})
    	return ({"attributes": {
	    				"status_desc": "Student Voting Details.",
	    				"status": "success"	    				
	    				},
	    				"responseList":child_list}), status.HTTP_200_OK


@name_space.route("/getAttendanceReportByChildId/<int:child_userid>/<string:month>/<string:date>")
class getAttendanceReportByChildId(Resource):
    def get(self,child_userid,month,date):
    	connection = mysql.connect()
    	cursor = connection.cursor()
    	
    	cursor.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`), `image_url` as student_name 
    		FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(child_userid))

    	student_name = cursor.fetchone()
    	if student_name:
    		name = student_name[0]
    		image_url = student_name[1]
    	if date != '0' and month == '0':
	    	cursor.execute("""SELECT a.`MEETING_ID`,a.`Status`,m.`TEACHER_ID`,m.`NOTIFICATION_ID`,
	    		m.`SET_BY_USER_ID`,m.`START_DATE`,m.`END_DATE`,m.`LOCATION`,m.`SUBJECT`,m.`DESCRIPTION`,
	    		m.`MEETING_STATUS`,m.`MEETING_TYPE`,concat(i.`FIRST_NAME`," ",i.`LAST_NAME`) teacher_name 
	    		FROM `attendance` a, `meeting_dtls` m, `institution_user_credential` i 
	    		WHERE a.`INSTITUTION_USER_ID` = %s and date(a.`LAST_UPDATE_TIMESTAMP`) = %s
	    		and a.`MEETING_ID` = m.`MEETING_ID` 
	    		and m.`TEACHER_ID` = i.`INSTITUTION_USER_ID`""",(child_userid,date))

	    	attendance_dtls = cursor.fetchall()
    	elif date == '0' and month != '0':
    		cursor.execute("""SELECT a.`MEETING_ID`,a.`Status`,m.`TEACHER_ID`,m.`NOTIFICATION_ID`,
	    		m.`SET_BY_USER_ID`,m.`START_DATE`,m.`END_DATE`,m.`LOCATION`,m.`SUBJECT`,m.`DESCRIPTION`,
	    		m.`MEETING_STATUS`,m.`MEETING_TYPE`,concat(i.`FIRST_NAME`," ",i.`LAST_NAME`) teacher_name 
	    		FROM `attendance` a, `meeting_dtls` m, `institution_user_credential` i 
	    		WHERE a.`INSTITUTION_USER_ID` = %s and month(a.`LAST_UPDATE_TIMESTAMP`) = %s
	    		and a.`MEETING_ID` = m.`MEETING_ID` 
	    		and m.`TEACHER_ID` = i.`INSTITUTION_USER_ID`""",(child_userid,month))

    		attendance_dtls = cursor.fetchall()
    	else:
	    	cursor.execute("""SELECT a.`MEETING_ID`,a.`Status`,m.`TEACHER_ID`,m.`NOTIFICATION_ID`,
	    		m.`SET_BY_USER_ID`,m.`START_DATE`,m.`END_DATE`,m.`LOCATION`,m.`SUBJECT`,m.`DESCRIPTION`,
	    		m.`MEETING_STATUS`,m.`MEETING_TYPE`,concat(i.`FIRST_NAME`," ",i.`LAST_NAME`) teacher_name 
	    		FROM `attendance` a, `meeting_dtls` m, `institution_user_credential` i 
	    		WHERE a.`INSTITUTION_USER_ID` = %s and a.`MEETING_ID` = m.`MEETING_ID` 
	    		and m.`TEACHER_ID` = i.`INSTITUTION_USER_ID`""",(child_userid))

	    	attendance_dtls = cursor.fetchall()

    	if attendance_dtls:
    		desc = cursor.description
    		col_names = [col[0] for col in desc]
    		details = [dict(izip(col_names,row)) for row in attendance_dtls]

	    	for i in range(len(details)):
	    		# print(details[i])
	    		details[i]['START_DATE'] = details[i]['START_DATE'].isoformat()
	    		details[i]['END_DATE'] = details[i]['END_DATE'].isoformat()
    	
	    	
    		attendance_details = {"studentName":name,
    							"image_url":image_url,
    							"attendanceDtls":details}
    		
    	else:
    		attendance_details = {"studentName":name,
    							"image_url":image_url,
    							"attendanceDtls":[]}
	    	
    	return ({"attributes": {
	    				"status_desc": "Child Attendance Details.",
	    				"status": "success"	    				
	    				},
	    				"responseList":attendance_details}), status.HTTP_200_OK

if __name__ == '__main__':
	app.run(host='0.0.0.0')