from __future__ import division
from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests,math

app = Flask(__name__)
app1 = Flask(__name__)
cors = CORS(app)
mysql = MySQL()
mysql1 = MySQL()
report_analysis = Blueprint('report_analysis_api', __name__)
api = Api(report_analysis, version='1.0', title='myElsa Report Analysis',
    description='myElsa Report Analysis')

batch_wise = api.namespace('ReportAnalysisForBatch', description=':Report Analysis')
student_wise = api.namespace('ReportAnalysisForIndividuals', description=':Report Analysis')

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

@batch_wise.route("/getAttendancePercentageForBatch/<int:group_id>/<string:month>/<string:year>")
class getAttendancePercentageForBatch(Resource):
	def get(self,group_id,month,year):
		connection = mysql.connect()
		cursor = connection.cursor()
		user_details = []
		if month != '0' and year == '0':
			cursor.execute("""SELECT `INSTITUTION_USER_ID`,`STATUS`,
				(count(`STATUS`)/(30)*100) percentage FROM `attendance` WHERE `INSTITUTION_USER_ID` 
				in(SELECT `Student_Id` FROM `group_student_mapping` WHERE `Group_ID` = %s) 
				and `STATUS` = 1 and month(`LAST_UPDATE_TIMESTAMP`) = %s 
				group by `INSTITUTION_USER_ID`""",(group_id,month))

			attendance_dtls = cursor.fetchall()
		elif month == '0' and year != '0':
			cursor.execute("""SELECT `INSTITUTION_USER_ID`,`STATUS`,
				(count(`STATUS`)/(365)*100) percentage FROM `attendance` WHERE `INSTITUTION_USER_ID` 
				in(SELECT `Student_Id` FROM `group_student_mapping` WHERE `Group_ID` = %s) 
				and `STATUS` = 1 and year(`LAST_UPDATE_TIMESTAMP`) = %s 
				group by `INSTITUTION_USER_ID`""",(group_id,year))

			attendance_dtls = cursor.fetchall()
		elif month != '0' and year != '0':
			cursor.execute("""SELECT `INSTITUTION_USER_ID`,`STATUS`,
				(count(`STATUS`)/(30)*100) percentage FROM `attendance` WHERE `INSTITUTION_USER_ID` 
				in(SELECT `Student_Id` FROM `group_student_mapping` WHERE `Group_ID` = %s) 
				and `STATUS` = 1 and month(`LAST_UPDATE_TIMESTAMP`) = %s 
				and year(`LAST_UPDATE_TIMESTAMP`) = %s 
				group by `INSTITUTION_USER_ID`""",(group_id,month,year))

			attendance_dtls = cursor.fetchall()
		else:
			cursor.execute("""SELECT `INSTITUTION_USER_ID`,`STATUS`,
				(count(`STATUS`)/(365)*100) percentage FROM `attendance` WHERE `INSTITUTION_USER_ID` 
				in(SELECT `Student_Id` FROM `group_student_mapping` WHERE `Group_ID` = %s) 
				and `STATUS` = 1 and year(`LAST_UPDATE_TIMESTAMP`) = %s 
				group by `INSTITUTION_USER_ID`""",(group_id,year))

			attendance_dtls = cursor.fetchall()
			# print(attendance_dtls)
		if attendance_dtls:
			desc = cursor.description
			col_names = [col[0] for col in desc]
			details = [dict(izip(col_names,row)) for row in attendance_dtls]

			for d in range(len(details)):
				# print(details[d]['INSTITUTION_USER_ID'])
				details[d]['percentage'] = int(details[d]['percentage'])
				print(details[d]['percentage'])
				cursor.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`), 
					`image_url` as student_name FROM `institution_user_credential` 
					WHERE `INSTITUTION_USER_ID` = %s""",(details[d]['INSTITUTION_USER_ID']))

				student_name = cursor.fetchone()
				if student_name:
					name = student_name[0]
					image_url = student_name[1]
					details[d]['student_name'] = name
					details[d]['student_image'] = image_url

				attendance = {"user_id":details[d]['INSTITUTION_USER_ID'],
						"name":name,
						"image_url":image_url,
						"percentage":details[d]['percentage']}

				user_details.append(attendance)
		return ({"attributes": {
						"status_desc": "Child Attendance Details.",
						"status": "success"
						},
	    				"responseList":user_details}), status.HTTP_200_OK


@batch_wise.route("/getAssignmentPercentageForBatch/<int:group_id>/<string:month>/<string:year>")
class getAssignmentPercentageForBatch(Resource):
	def get(self,group_id,month,year):
		connection = mysql.connect()
		cursor = connection.cursor()

		conn = mysql1.connect()
		cur = conn.cursor()
		user_ids = []
		user_details = []
		cursor.execute("""SELECT `Student_Id` FROM `group_student_mapping` 
			WHERE `Group_ID` = %s""",(group_id))

		student_id = cursor.fetchall()
		if student_id:
			for i in range(len(student_id)):
				user_ids.append(student_id[i][0])

		print(user_ids)
		for i, ids in enumerate(user_ids):
			cursor.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as student_name , `image_url` 
	    		FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(ids))

			user_dtls = cursor.fetchone()

			if user_dtls:
				name = user_dtls[0]
				image = user_dtls[1]
			if month != '0' and year == '0':
				cur.execute("""SELECT sum(`Result`)/COUNT(`Result`) 
					FROM `assigment_result` WHERE `Student_ID` = %s 
					and month(`Last_Update_TS`) = %s""",(ids,month))

				percentage = cur.fetchone()
			elif month == '0' and year != '0':
				cur.execute("""SELECT sum(`Result`)/COUNT(`Result`) 
					FROM `assigment_result` WHERE `Student_ID` = %s 
					and year(`Last_Update_TS`) = %s""",(ids,year))

				percentage = cur.fetchone()
			elif month != '0' and year != '0':
				cur.execute("""SELECT sum(`Result`)/COUNT(`Result`) 
					FROM `assigment_result` WHERE `Student_ID` = %s
					and month(`Last_Update_TS`) = %s 
					and year(`Last_Update_TS`) = %s""",(ids,month,year))

				percentage = cur.fetchone()
			else:
				cur.execute("""SELECT sum(`Result`)/COUNT(`Result`) 
					FROM `assigment_result` WHERE `Student_ID` = %s""",(ids))

				percentage = cur.fetchone()
			if percentage:
				percentage = percentage[0] or 0
				percentage = float(round(percentage,0))
			print(name,image,ids,i,percentage)

			details = {"user_id":ids,
						"name":name,
						"image_url":image,
						"percentage":percentage}

			user_details.append(details)

		return ({"attributes": {
						"status_desc": "Batch Assignments Details.",
						"status": "success"
						},
	    				"responseList":user_details}), status.HTTP_200_OK

@batch_wise.route("/getAssessmentPercentageForBatch/<int:group_id>/<string:month>/<string:year>")
class getAssignmentPercentageForBatch(Resource):
	def get(self,group_id,month,year):
		connection = mysql.connect()
		cursor = connection.cursor()

		conn = mysql1.connect()
		cur = conn.cursor()

		user_ids = []
		user_details = []
		cursor.execute("""SELECT `Student_Id` FROM `group_student_mapping` 
			WHERE `Group_ID` = %s""",(group_id))

		student_id = cursor.fetchall()
		if student_id:
			for i in range(len(student_id)):
				user_ids.append(student_id[i][0])

		print(user_ids)
		for i, ids in enumerate(user_ids):
			cursor.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as student_name , `image_url` 
	    		FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(ids))

			user_dtls = cursor.fetchone()

			if user_dtls:
				name = user_dtls[0]
				image = user_dtls[1]
			if month != '0' and year == '0':
				cur.execute("""SELECT avg(`Marks`)  FROM `assessment_tracking` 
					WHERE `Student_Id` = %s and month(`Last_Update_TS`) = %s""",(ids,month))

				percentage = cur.fetchone()
			elif month == '0' and year != '0':
				cur.execute("""SELECT avg(`Marks`)  FROM `assessment_tracking` 
					WHERE `Student_Id` = %s and year(`Last_Update_TS`) = %s""",(ids,year))

				percentage = cur.fetchone()
			elif month != '0' and year != '0':
				cur.execute("""SELECT avg(`Marks`)  FROM `assessment_tracking` 
					WHERE `Student_Id` = %s	and month(`Last_Update_TS`) = %s 
					and year(`Last_Update_TS`) = %s""",(ids,month,year))

				percentage = cur.fetchone()
			else:
				cur.execute("""SELECT avg(`Marks`)  FROM `assessment_tracking` 
					WHERE `Student_Id` = %s""",(ids))

				percentage = cur.fetchone()
			if percentage:
				percentage = percentage[0] or 0
				percentage = float(round(percentage,0))
			print(name,image,ids,i,percentage)

			details = {"user_id":ids,
						"name":name,
						"image_url":image,
						"percentage":percentage}

			user_details.append(details)

		return ({"attributes": {
						"status_desc": "Batch Assessment Details.",
						"status": "success"
						},
	    				"responseList":user_details}), status.HTTP_200_OK
		

@student_wise.route("/getAttendanceReportByChildId/<int:child_userid>/<string:month>/<string:date>/<string:year>")
class getAttendanceReportByChildId(Resource):
    def get(self,child_userid,month,date,year):
    	connection = mysql.connect()
    	cursor = connection.cursor()
    	attendance_percentage = 0
    	cursor.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as student_name, `image_url`  
    		FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(child_userid))

    	student_name = cursor.fetchone()
    	if student_name:
    		name = student_name[0]
    		image_url = student_name[1]
    	if date != '0' and month == '0' and year == '0':
	    	cursor.execute("""SELECT a.`MEETING_ID`,a.`Status`,m.`TEACHER_ID`,m.`NOTIFICATION_ID`,
	    		m.`SET_BY_USER_ID`,m.`START_DATE`,m.`END_DATE`,m.`LOCATION`,m.`SUBJECT`,m.`DESCRIPTION`,
	    		m.`MEETING_STATUS`,m.`MEETING_TYPE`,concat(i.`FIRST_NAME`," ",i.`LAST_NAME`) teacher_name 
	    		FROM `attendance` a, `meeting_dtls` m, `institution_user_credential` i 
	    		WHERE a.`INSTITUTION_USER_ID` = %s and date(a.`LAST_UPDATE_TIMESTAMP`) = %s
	    		and a.`MEETING_ID` = m.`MEETING_ID` 
	    		and m.`TEACHER_ID` = i.`INSTITUTION_USER_ID`""",(child_userid,date))

	    	attendance_dtls = cursor.fetchall()
    	elif date == '0' and month != '0' and year == '0':
    		cursor.execute("""SELECT a.`MEETING_ID`,a.`Status`,m.`TEACHER_ID`,m.`NOTIFICATION_ID`,
	    		m.`SET_BY_USER_ID`,m.`START_DATE`,m.`END_DATE`,m.`LOCATION`,m.`SUBJECT`,m.`DESCRIPTION`,
	    		m.`MEETING_STATUS`,m.`MEETING_TYPE`,concat(i.`FIRST_NAME`," ",i.`LAST_NAME`) teacher_name 
	    		FROM `attendance` a, `meeting_dtls` m, `institution_user_credential` i 
	    		WHERE a.`INSTITUTION_USER_ID` = %s and month(a.`LAST_UPDATE_TIMESTAMP`) = %s
	    		and year(a.`LAST_UPDATE_TIMESTAMP`) = year(a.`LAST_UPDATE_TIMESTAMP`) 
	    		and a.`MEETING_ID` = m.`MEETING_ID` 
	    		and m.`TEACHER_ID` = i.`INSTITUTION_USER_ID`""",(child_userid,month))

    		attendance_dtls = cursor.fetchall()
    	elif date == '0' and month != '0' and year != '0':
    		cursor.execute("""SELECT a.`MEETING_ID`,a.`Status`,m.`TEACHER_ID`,m.`NOTIFICATION_ID`,
	    		m.`SET_BY_USER_ID`,m.`START_DATE`,m.`END_DATE`,m.`LOCATION`,m.`SUBJECT`,m.`DESCRIPTION`,
	    		m.`MEETING_STATUS`,m.`MEETING_TYPE`,concat(i.`FIRST_NAME`," ",i.`LAST_NAME`) teacher_name 
	    		FROM `attendance` a, `meeting_dtls` m, `institution_user_credential` i 
	    		WHERE a.`INSTITUTION_USER_ID` = %s and month(a.`LAST_UPDATE_TIMESTAMP`) = %s
	    		and year(a.`LAST_UPDATE_TIMESTAMP`) = %s and a.`MEETING_ID` = m.`MEETING_ID` 
	    		and m.`TEACHER_ID` = i.`INSTITUTION_USER_ID`""",(child_userid,month,year))

    		attendance_dtls = cursor.fetchall()
    	elif date == '0' and month == '0' and year != '0':
    		cursor.execute("""SELECT a.`MEETING_ID`,a.`Status`,m.`TEACHER_ID`,m.`NOTIFICATION_ID`,
	    		m.`SET_BY_USER_ID`,m.`START_DATE`,m.`END_DATE`,m.`LOCATION`,m.`SUBJECT`,m.`DESCRIPTION`,
	    		m.`MEETING_STATUS`,m.`MEETING_TYPE`,concat(i.`FIRST_NAME`," ",i.`LAST_NAME`) teacher_name 
	    		FROM `attendance` a, `meeting_dtls` m, `institution_user_credential` i 
	    		WHERE a.`INSTITUTION_USER_ID` = %s and year(a.`LAST_UPDATE_TIMESTAMP`) = %s
	    		and a.`MEETING_ID` = m.`MEETING_ID` 
	    		and m.`TEACHER_ID` = i.`INSTITUTION_USER_ID`""",(child_userid,year))

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
    		
    		if 	date == '0' and month != '0' and year == '0':
	    		attendance_percentage = math.ceil((len(details)/30)*100)
	    	elif date == '0' and month != '0' and year != '0':
	    		attendance_percentage = math.ceil((len(details)/30)*100)
	    	elif date == '0' and month == '0' and year != '0':
	    		attendance_percentage = math.ceil((len(details)/365)*100)
	    	else:
	    		attendance_percentage = 0
    		attendance_details = {"studentName":name,
    							"image_url":image_url,
    							"percentage":attendance_percentage}
    							#"attendanceDtls":details}
    		
    	else:
    		attendance_details = {"studentName":name,
    							"image_url":image_url,
    							"percentage":attendance_percentage}
    							#"attendanceDtls":[]}
	    	
    	return ({"attributes": {
	    				"status_desc": "Child Attendance Details.",
	    				"status": "success",    				
	    				},
	    				"responseList":attendance_details}), status.HTTP_200_OK

@student_wise.route("/getAssignmentPercentageByChildId/<int:userid>/<string:month>/<string:date>/<string:year>")
class getAssignmentPercentageByChildId(Resource):
    def get(self,userid,month,date,year):
    	connection = mysql.connect()
    	cursor = connection.cursor()
    	conn = mysql1.connect()
    	cur = conn.cursor()
    	user_details = []
    	details = {}
    	assignment_details ={}
    	cursor.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as student_name, `image_url` 
			FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(userid))

    	user_dtls = cursor.fetchone()
    	if user_dtls:
    		name = user_dtls[0]
    		image = user_dtls[1]

    	if month != '0' and year == '0' and date == '0':
    		cur.execute("""SELECT `Assignment_ID`,sum(`Result`)/COUNT(`Result`) 
    			FROM `assigment_result` WHERE `Student_ID` = %s 
    			and month(`Last_Update_TS`) = %s group by `Assignment_ID`""",(userid,month))
    		assignment = cur.fetchall()
    	elif month == '0' and year != '0' and date == '0':
    		cur.execute("""SELECT `Assignment_ID`,sum(`Result`)/COUNT(`Result`)
    			FROM `assigment_result` WHERE `Student_ID` = %s 
    			and year(`Last_Update_TS`) = %s group by `Assignment_ID`""",(userid,year))
    		assignment = cur.fetchall()
    	elif month == '0' and year == '0' and date != '0':
    		cur.execute("""SELECT `Assignment_ID`,sum(`Result`)/COUNT(`Result`)
    			FROM `assigment_result` WHERE `Student_ID` = %s
    			and date(`Last_Update_TS`) = %s group by `Assignment_ID`""",(userid,date))
    		assignment = cur.fetchall()
    	elif month != '0' and year != '0' and date == '0':
    		cur.execute("""SELECT `Assignment_ID`,sum(`Result`)/COUNT(`Result`) 
    			FROM `assigment_result` WHERE `Student_ID` = %s
    			and month(`Last_Update_TS`) = %s
    			and year(`Last_Update_TS`) = %s group by `Assignment_ID`""",(userid,month,year))
    		assignment = cur.fetchall()
    	else:
    		cur.execute("""SELECT `Assignment_ID`,sum(`Result`)/COUNT(`Result`)
    			FROM `assigment_result` WHERE `Student_ID` = %s group by `Assignment_ID`""",(userid))
    		assignment = cur.fetchall()

    	if assignment:
    		for i, p in enumerate(assignment):
    			assignment_id = assignment[i][0]

    			cur.execute("""SELECT `Teacher_ID`,`Assignment_Type`,`Content_Master_ID`,
    				`Remarks`,`Title` FROM `assignment` WHERE `Assignment_ID` = %s""",(assignment_id))
    			assignment_dtls = cur.fetchone()

    			if assignment_dtls:
    				teacher_id = assignment_dtls[0]
    				cursor.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as teacher_name, 
    					`image_url` FROM `institution_user_credential` 
    					WHERE `INSTITUTION_USER_ID` = %s""",(teacher_id))
    				tchr_dtls = cursor.fetchone()

    				if tchr_dtls:
	    				teacher_name = tchr_dtls[0]
	    				teacher_image = tchr_dtls[1]
    				assignment_type = assignment_dtls[1]
    				content_master_id = assignment_dtls[2]
    				try:
	    				cur.execute("""SELECT `Content_Master_Name`  FROM `content_master` 
	    					WHERE `Content_Master_ID` = %s""",(content_master_id))
	    			except:
	    				pass
	    			content_dtls = cur.fetchone()
	    			if content_dtls:
	    				content_name = content_dtls[0]
	    			else:
	    				content_name = ''
    				remarks = assignment_dtls[3]
    				title = assignment_dtls[4]
		    		percent = assignment[i][1] or 0
		    		percent = float(round(percent,0))

			    	details = {"percentage":percent,
				    			"assignment_id":assignment_id,
				    			"title":title,
				    			"teacher_id":teacher_id,
				    			"teacher_name":teacher_name,
				    			"teacher_image":teacher_image,
				    			"assignment_type":assignment_type,
				    			"content_master_id":content_master_id,
				    			"content_name":content_name,
				    			"remarks":remarks
				    			}

			    	user_details.append(details)
		
    	cursor.close()
    	cur.close()

    	if details:
    		assignment_details = {"studentName":name,
    								"image_url":image,
    								"assignmentDtls":user_details}
    	else:
    		assignment_details = {"studentName":name,
    								"image_url":image,
    								"assignmentDtls":user_details}

    	return ({"attributes": {
						"status_desc": "Individual Assignments Details.",
						"status": "success"
						},
						"responseList":assignment_details}), status.HTTP_200_OK

if __name__ == '__main__':
	app.run(host='0.0.0.0')

