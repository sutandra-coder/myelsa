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

def mysql_connection_lab_lang():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='creamson_lab_lang1',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

def mysql_connection():
	connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
	                             user='admin',
	                             password='cbdHoRPQPRfTdC0uSPLt',
	                             db='creamson_logindb',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection


	
teacher_portal = Blueprint('teacher_portal_api', __name__)
api = Api(teacher_portal,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('teacher_portal',description='Teacher Portal')
name_space1 = api.namespace('assignmentController',description='Assignment Controller')
class_test = api.namespace('classTestController',description='ClassTest Controller')

attendance_model = api.model('attendance_model', {
	"student_id":fields.Integer(),
	"status":fields.Integer(required=True),
	"group_id":fields.Integer(),
	})

submit_attendance = api.model('Submit Attendance', {
	"attendance_details":fields.List(fields.Nested(attendance_model)),
	"is_group":fields.Integer(),
	"teacher_id":fields.Integer(required=True),
	"meeting_id":fields.Integer()
	})

assignment_model = api.model('assignment_model', {
	"student_id":fields.Integer(),
	"group_id":fields.Integer(),
	})

validate_assignment = api.model('validate_assignment', {
	"student_id":fields.List(fields.Integer()),
	"group_id":fields.List(fields.Integer()),
	"assignment_id":fields.Integer(required=True),
	})

createclasstest = api.model('create class test', {
	"teacher_id":fields.Integer(),
	"test_type":fields.String(),
	"title":fields.String(),
	"remarks":fields.String(),
	"content_filepath":fields.String(),
	"content_filetype":fields.String(),
	"submission_date":fields.String(),
	"exam_startTime":fields.String(),
	"exam_endTime":fields.String()
	})


assign_classtest = api.model('Assign ClassTest', {
	"student_id":fields.List(fields.Integer()),
	"group_id":fields.List(fields.Integer()),
	"is_group":fields.Integer(required=True),
	"teacher_id":fields.Integer(required=True),
	"test_id":fields.Integer(required=True)
	})

classtest_result = api.model('ClassTest Result', {
	"student_id":fields.Integer(required=True),
	"teacher_id":fields.Integer(required=True),
	"test_id":fields.Integer(required=True),
	"marks":fields.Integer(required=True),
	"parameter_id":fields.Integer(),
	"remarks":fields.String(),
	"answersheet_filepath":fields.String(),
	"filetype":fields.String()
	})

updateassignment = api.model('update assignment', {
	"content_path":fields.String(),
	"content_filetype":fields.String(),
	"assignmentTitle":fields.String(),
	})

@name_space.route("/submitAttendance/<string:start_timestamp>/<string:end_timestamp>")
class submitAttendance(Resource):
	@api.expect(submit_attendance)
	def post(self,start_timestamp,end_timestamp):
		details = request.get_json()
		connection = mysql_connection()
		cursor = connection.cursor()
		is_group = details['is_group']
		attendance_details = details['attendance_details']
		res = 'Something went wrong!'
		student_id = []
		url = 'http://creamsonservices.com:8080/CommunicationModule2/sendMailMessage'
		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		cursor.execute("""SELECT CONCAT(`FIRST_NAME`, " ", `LAST_NAME`) AS name,`INSTITUTION_ID` 
			FROM `institution_user_credential` ic,`institution_user_credential_master` icm 
			WHERE ic.`INSTITUTION_USER_ID` = icm.`INSTITUTION_USER_ID` 
			and ic.`INSTITUTION_USER_ID` = %s""",(details['teacher_id']))
		teacher = cursor.fetchone()

		if teacher:
			teacher_name = teacher['name']
			instiID = teacher['INSTITUTION_ID']

		if is_group:
			for i, j in enumerate(attendance_details):
				group_id = attendance_details[i]['group_id']
				cursor.execute("""SELECT `Student_Id` FROM `group_student_mapping` 
					WHERE `Group_ID` = %s""",(group_id))

				std_id = cursor.fetchall()
				if std_id:
					for idx,std in enumerate(std_id):
						sid = std['Student_Id']

						attendance_insert_query = ("""INSERT INTO `attendance`(`MEETING_ID`, 
							`INSTITUTION_USER_ID`, `STATUS`, `batch_start_time`, `batch_end_time`, 
							`LAST_UPDATE_ID`) VALUES (%s,%s,%s,%s,%s,%s)""")
						attendance_data = (details['meeting_id'],sid,j['status'],
							start_timestamp,end_timestamp,details['teacher_id'])

						cursor.execute(attendance_insert_query,attendance_data)

						attendance_details[i]['attendance_id'] = cursor.lastrowid
						res = 'Attendance Successfully submitted'


						cursor.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name, 
							`image_url` as student_image FROM `institution_user_credential` 
							WHERE `INSTITUTION_USER_ID` = %s""",(sid))
						student_name = cursor.fetchone()

						if student_name:
							data = {
									  'mailDetails': [
									    {
									      'appParams': {"imageUrl":""},
									      'mailParams': {"student":student_name['name'],
									      					"batchdate":start_timestamp,
									      					"teacher":teacher_name},
									      'role': 'S1',
									      'toMail': '',
									      'toNumber': '',
									      'userId': sid
									    }
									  ],
									  'sourceApp': 'ATDNC0S'
									}
							
							response = requests.post(url, data=json.dumps(data), headers=headers)

							cursor.execute("""SELECT `Fathers_Name`, `INSTITUTION_USER_ID_GUARDIAN` FROM `student_dtls` sd 
								INNER JOIN `guardian_dtls` gd ON 
								sd.`INSTITUTION_USER_ID_STUDENT` = gd.`INSTITUTION_USER_ID_STUDENT`
								AND sd.`INSTITUTION_ID` = gd.`INSTITUTION_ID` 
								WHERE sd.`INSTITUTION_USER_ID_STUDENT` = %s 
								and sd.`INSTITUTION_ID` = %s""",(sid,instiID))
							parent = cursor.fetchone()

							if parent:
								parent_name = parent['Fathers_Name']
								parentID = parent['INSTITUTION_USER_ID_GUARDIAN']

								pdata = {
										  'mailDetails': [
										    {
										      'appParams': {"imageUrl":""},
										      'mailParams': {"parent":parent_name,
										      					"student":student_name['name'],
										      					"startdate":createdate,
										      					"teacher":teacher_name},
										      'role': 'G1',
										      'toMail': '',
										      'toNumber': '',
										      'userId': parentID
										    }
										  ],
										  'sourceApp': 'ATDNC0G'
										}
								
								presponse = requests.post(url, data=json.dumps(pdata), headers=headers)

		else:
			for idx, std in enumerate(attendance_details):
				sid = std['student_id']
				attendance_insert_query = ("""INSERT INTO `attendance`(`MEETING_ID`, 
							`INSTITUTION_USER_ID`, `STATUS`, `batch_start_time`, `batch_end_time`, 
							`LAST_UPDATE_ID`) VALUES (%s,%s,%s,%s,%s,%s)""")
				attendance_data = (details['meeting_id'],sid,std['status'],
							start_timestamp,end_timestamp,details['teacher_id'])

				cursor.execute(attendance_insert_query,attendance_data)

				attendance_details[idx]['attendance_id'] = cursor.lastrowid
				res = 'Attendance Successfully submitted'

				cursor.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name, 
					`image_url` as student_image FROM `institution_user_credential` 
					WHERE `INSTITUTION_USER_ID` = %s""",(sid))
				student_name = cursor.fetchone()

				if student_name:
					data = {
							  'mailDetails': [
							    {
							      'appParams': {"imageUrl":""},
							      'mailParams': {"student":student_name['name'],
							      					"batchdate":start_timestamp,
							      					"teacher":teacher_name},
							      'role': 'S1',
							      'toMail': '',
							      'toNumber': '',
							      'userId': sid
							    }
							  ],
							  'sourceApp': 'ATDNC0S'
							}
					
					response = requests.post(url, data=json.dumps(data), headers=headers)

					cursor.execute("""SELECT `Fathers_Name`, `INSTITUTION_USER_ID_GUARDIAN` FROM `student_dtls` sd 
						INNER JOIN `guardian_dtls` gd ON 
						sd.`INSTITUTION_USER_ID_STUDENT` = gd.`INSTITUTION_USER_ID_STUDENT`
						AND sd.`INSTITUTION_ID` = gd.`INSTITUTION_ID` 
						WHERE sd.`INSTITUTION_USER_ID_STUDENT` = %s 
						and sd.`INSTITUTION_ID` = %s""",(sid,instiID))
					parent = cursor.fetchone()

					if parent:
						parent_name = parent['Fathers_Name']
						parentID = parent['INSTITUTION_USER_ID_GUARDIAN']

						pdata = {
								  'mailDetails': [
								    {
								      'appParams': {"imageUrl":""},
								      'mailParams': {"parent":parent_name,
								      					"student":student_name['name'],
								      					"batchdate":start_timestamp,
								      					"teacher":teacher_name},
								      'role': 'G1',
								      'toMail': '',
								      'toNumber': '',
								      'userId': parentID
								    }
								  ],
								  'sourceApp': 'ATDNC0G'
								}
						
						presponse = requests.post(url, data=json.dumps(pdata), headers=headers)
		connection.commit()
		cursor.close()
		
		details['message'] = res
		return ({"attributes": {"status_desc": "Attendance Details",
                                "status": "success"
                                },
                 "responseList": details}), status.HTTP_200_OK



@name_space1.route("/validateAssignment")
class validateAssignment(Resource):
	@api.expect(validate_assignment)
	def post(self):
		details = request.get_json()

		connection = mysql_connection()
		cursor = connection.cursor()

		conn = mysql_connection_lab_lang()
		cur = conn.cursor()

		student_id = details['student_id']
		group_id = details['group_id']
		assignment_id = details['assignment_id']
		assigned_to = []

		assigned = {}
		if group_id:
			for gid in group_id:
				cursor.execute("""SELECT `Student_Id` FROM `group_student_mapping`
					WHERE `Group_ID` = %s""",(gid))

				std_id = cursor.fetchall()

				if std_id:
					for idx,std in enumerate(std_id):
						student_id.append(std['Student_Id'])
		student_id = list(set(student_id))
		for stid in student_id:
			# print(stid)
			cur.execute("""SELECT `Student_UserID` FROM `assignment_mapping` 
				WHERE `Student_UserID` = %s and `Assignment_ID` = %s""",(stid,assignment_id))

			sid = cur.fetchone()
			# print(sid)
			if sid:
				print(sid)
				assigned_to.append(sid)

		for idx,asgned in enumerate(assigned_to):
			cursor.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name, 
				`image_url` as student_image FROM `institution_user_credential` 
				WHERE `INSTITUTION_USER_ID` = %s""",(assigned_to[idx]['Student_UserID']))
			student_name = cursor.fetchone()
			if student_name:
				assigned_to[idx]['student_name'] = student_name['name']
				assigned_to[idx]['student_image'] = student_name['student_image']
		cursor.close()
		cur.close()
		return ({"attributes": {"status_desc": "Validate Assignment Details",
                                "status": "success"
                                },
                 "responseList": assigned_to}), status.HTTP_200_OK



@name_space.route("/getAttendanceBatch/<int:teacher_id>/<string:batch_date>")
class getAttendanceBatch(Resource):
	def get(self,teacher_id,batch_date):

		connection = mysql_connection()
		cursor = connection.cursor()

		cursor.execute("""SELECT  `batch_start_time`, `batch_end_time`
			FROM `attendance` WHERE date(`LAST_UPDATE_TIMESTAMP`) = %s 
			and `LAST_UPDATE_ID` = %s 
			GROUP by `batch_start_time`,`batch_end_time`""",(batch_date,teacher_id))


		res = cursor.fetchall()
		for i, j in enumerate(res):
			res[i]['batch_start_time'] = res[i]['batch_start_time'].isoformat()
			res[i]['batch_end_time'] = res[i]['batch_end_time'].isoformat()
			res[i]['batch_name'] = 'Batch-'+str(i+1)
		cursor.close()
		return ({"attributes": {"status_desc": "Attendance Batch Details",
                                "status": "success"
                                },
                 "responseList": res}), status.HTTP_200_OK



@name_space.route("/getAttendanceBatchDetails/<string:teacher_id>/<string:batch_start_time>/<string:batch_end_time>")
class getAttendanceBatchDetails(Resource):
	def get(self,teacher_id,batch_start_time,batch_end_time):

		connection = mysql_connection()
		cursor = connection.cursor()


		cursor.execute("""SELECT `INSTITUTION_USER_ID` as userid,`STATUS` as status FROM `attendance` 
			WHERE `LAST_UPDATE_ID` = %s and `batch_start_time` = %s 
			and `batch_end_time` = %s""",(teacher_id,batch_start_time,batch_end_time))


		batch_details = cursor.fetchall()
		if not batch_details:
			batch_details = []
		else:
			for idx,batch in enumerate(batch_details):
				cursor.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name, 
					`image_url` as student_image,`PRIMARY_CONTACT_NUMBER` as phone_no
					FROM `institution_user_credential` 
					WHERE `INSTITUTION_USER_ID` = %s""",(batch_details[idx]['userid']))
				student_name = cursor.fetchone()
				cursor.execute("""SELECT `CLASS` as class FROM `student_dtls` 
					WHERE `INSTITUTION_USER_ID_STUDENT` = %s""",(batch_details[idx]['userid']))

				clss = cursor.fetchone()

				cursor.execute("""SELECT `Board` as board FROM `student_dtls` 
					WHERE `INSTITUTION_USER_ID_STUDENT` = %s""",(batch_details[idx]['userid']))

				board = cursor.fetchone()
				if student_name:
					batch_details[idx]['student_name'] = student_name['name']
					batch_details[idx]['image_url'] = student_name['student_image']
					batch_details[idx]['phone_no'] = student_name['phone_no']
					batch_details[idx]['class'] = clss['class']
					batch_details[idx]['board'] = board['board']
		cursor.close()		
		return ({"attributes": {"status_desc": "Attendance Batch Details",
                                "status": "success"
                                },
                 "responseList": batch_details}), status.HTTP_200_OK

@name_space1.route("/getAssignmentDetailsByTeacherdId/<int:teacher_id>")
class getAssignmentDetailsByTeacherdId(Resource):
	def get(self,teacher_id):
		connection = mysql_connection_lab_lang()
		cursor = connection.cursor()

		cursor.execute("""SELECT assmt.`Assignment_ID`, assmt.`Assignment_Type`,assmt.`Content_Master_ID`, 
			assmt.`Content_path`, assmt.`Title`,assmt.`Remarks`, assmt.`Content_File_Type`, 
			count(aasmtmap.`Status`) as status, assmt.`Last_Update_TS` 
			FROM  `assignment` assmt LEFT JOIN `assignment_mapping` aasmtmap 
			ON assmt.`Assignment_ID` = aasmtmap.`Assignment_ID`
			WHERE assmt.`Teacher_ID`= %s 
			group by assmt.`Assignment_ID` order by assmt.`Last_Update_TS` desc""",(teacher_id))


		assignDtls = cursor.fetchall()

		for a, assd in enumerate(assignDtls):
			assignDtls[a]['Last_Update_TS'] = assignDtls[a]['Last_Update_TS'].isoformat()

		cursor.close()
		return ({"attributes": {"status_desc": "Content fetched",
                                "status": "success",
                                "Teacher_ID":teacher_id
                                },
                 "responseList": assignDtls}), status.HTTP_200_OK


@class_test.route("/createClassTest")
class createClassTest(Resource):
	@api.expect(createclasstest)
	def post(self):

		details = request.get_json()
		connection = mysql_connection_lab_lang()
		cursor = connection.cursor()

		conn = mysql_connection()
		cur = conn.cursor()

		create_test_insert_query = ("""INSERT INTO `class_test`(`teacher_id`, `test_type`, `title`, 
			`remarks`, `content_path`, `content_file_type`,`submisson_date`, 
			`exam_starttime`, `exam_endtime`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

		test_data = (details['teacher_id'],details['test_type'],details['title'],
			details['remarks'],details['content_filepath'],details['content_filetype'],
			details['submission_date'],details['exam_startTime'],details['exam_endTime'])

		cursor.execute(create_test_insert_query,test_data)
		
		test_id = cursor.lastrowid
		
		details['test_id'] = test_id

		createdate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		cur.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name
			FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(details['teacher_id']))
		teacher = cur.fetchone()

		if teacher:
			teacher_name = teacher['name']
		url = 'http://creamsonservices.com:8080/CommunicationModule2/sendMailMessage'
		data = {
				  'mailDetails': [
				    {
				      'appParams': {"imageUrl":""},
				      'mailParams': {"teacher":teacher_name,
				      					"startdate":createdate,
				      					"classtestName":details['title']},
				      'role': 'T1',
				      'toMail': '',
				      'toNumber': '',
				      'userId': details['teacher_id']
				    }
				  ],
				  'sourceApp': 'CLST00T'
				}
		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		response = requests.post(url, data=json.dumps(data), headers=headers)
		connection.commit()
		cursor.close()
		cur.close()
		return ({"attributes": {"status_desc": "Create Test Details",
                                "status": "success"
                                },
                 "responseList": details}), status.HTTP_200_OK

@class_test.route("/listOfClassTestForTeacher/<int:teacher_id>")
class listOfClassTestForTeacher(Resource):
	def get(self,teacher_id):
		connection = mysql_connection_lab_lang()
		cursor = connection.cursor()

		cursor.execute("""SELECT `test_id`,`teacher_id`,`test_type`,`title`,`remarks`,
			`content_path` as 'question_filepath',`content_file_type` as 'question_filetype',`submisson_date`,`exam_starttime`, 
			`exam_endtime`,date(`last_update_ts`) as 'assigned_on' FROM `class_test` WHERE `teacher_id` = %s""",(teacher_id))

		testList = cursor.fetchall()
		for t,test in enumerate(testList):
			test_id = test['test_id']
			test['submisson_date'] = test['submisson_date'].isoformat()
			test['exam_starttime'] = test['exam_starttime'].isoformat()
			test['exam_endtime'] = test['exam_endtime'].isoformat()
			test['assigned_on'] = test['assigned_on'].isoformat()
			test['filename'] = test['question_filepath'].split('/')[-1].split('.')[0]

			cursor.execute("""SELECT `student_id` FROM `classtest_student_mapping` 
				WHERE `test_id` = %s limit 1""",(test_id))

			student_id = cursor.fetchone()
			if student_id:
				idx = student_id['student_id']
				# print(student_id)

				cursor.execute("""SELECT `Class`,`Board` FROM `student` 
					WHERE `Student_UserID` = %s""",(idx))

				stdDtls = cursor.fetchone()
				print(stdDtls)
				test['classs'] = stdDtls['Class']
				test['board'] = stdDtls['Board']

		cursor.close()
		return ({"attributes": {"status_desc": "Create Test Details",
                                "status": "success"
                                },
                 "responseList": testList}), status.HTTP_200_OK



@class_test.route("/assignClassTest")
class assignClassTest(Resource):
	@api.expect(assign_classtest)
	def post(self):
		details = request.get_json() 

		connection = mysql_connection()
		cursor = connection.cursor()

		conn = mysql_connection_lab_lang()
		cur = conn.cursor()

		student_id = details['student_id']
		group_id = details['group_id']
		teacher_id = details['teacher_id']
		is_group = details['is_group']
		test_id = details['test_id']
		assigned_to = []
		not_assigned = []

		cur.execute("""SELECT `title` FROM `class_test` WHERE `test_id` = %s""",(test_id))
		title = cur.fetchone()
		testTitle = title.get('title','')
		
		url = 'http://creamsonservices.com:8080/CommunicationModule2/sendMailMessage'
		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		createdate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		cursor.execute("""SELECT CONCAT(`FIRST_NAME`, " ", `LAST_NAME`) AS name,`INSTITUTION_ID` 
			FROM `institution_user_credential` ic,`institution_user_credential_master` icm 
			WHERE ic.`INSTITUTION_USER_ID` = icm.`INSTITUTION_USER_ID` 
			and ic.`INSTITUTION_USER_ID` = %s""",(teacher_id))
		teacher = cursor.fetchone()

		if teacher:
			teacher_name = teacher['name']
			instiID = teacher['INSTITUTION_ID']
		

		if is_group:
			for gid in group_id:
				cursor.execute("""SELECT `Student_Id` FROM `group_student_mapping`
					WHERE `Group_ID` = %s""",(gid))

				std_id = cursor.fetchall()

				if std_id:
					for idx,std in enumerate(std_id):
						student_id.append(std['Student_Id'])
		student_id = list(set(student_id))
		
		student_list = []
		
		for i, stid in enumerate(student_id):

			cur.execute("""SELECT `student_id` FROM `classtest_student_mapping` 
				WHERE `student_id` = %s and `test_id` = %s""",(student_id[i],test_id))

			sid = cur.fetchone()
			
			if sid:
				continue
			else:
				student_list.append(student_id[i])
				
		if student_list:
			for idx,student in enumerate(student_list):

				test_mapping_query = ("""INSERT INTO `classtest_student_mapping`(`test_id`, `student_id`, 
					`status`) VALUES (%s,%s,%s)""")

				map_data = (test_id,student,'i')

				cur.execute(test_mapping_query,map_data)

				cursor.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name, 
					`image_url` as student_image FROM `institution_user_credential` 
					WHERE `INSTITUTION_USER_ID` = %s""",(student_list[idx]))
				student_name = cursor.fetchone()

				if student_name:
					assigned_to.append({'student_name':student_name['name'],
												'student_image':student_name['student_image'],
												'mapping_id':cur.lastrowid,
												'status':'i'})
					data = {
							  'mailDetails': [
							    {
							      'appParams': {"imageUrl":""},
							      'mailParams': {"student":student_name['name'],
							      					"classtestName":testTitle,
							      					"startdate":createdate,
							      					"teacher":teacher_name},
							      'role': 'S1',
							      'toMail': '',
							      'toNumber': '',
							      'userId': student_list[idx]
							    }
							  ],
							  'sourceApp': 'CLST00S'
							}
					
					response = requests.post(url, data=json.dumps(data), headers=headers)

					cursor.execute("""SELECT `Fathers_Name`, `INSTITUTION_USER_ID_GUARDIAN` FROM `student_dtls` sd 
						INNER JOIN `guardian_dtls` gd ON 
						sd.`INSTITUTION_USER_ID_STUDENT` = gd.`INSTITUTION_USER_ID_STUDENT`
						AND sd.`INSTITUTION_ID` = gd.`INSTITUTION_ID` 
						WHERE sd.`INSTITUTION_USER_ID_STUDENT` = %s 
						and sd.`INSTITUTION_ID` = %s""",(student_list[idx],instiID))
					parent = cursor.fetchone()

					if parent:
						parent_name = parent['Fathers_Name']
						parentID = parent['INSTITUTION_USER_ID_GUARDIAN']

						pdata = {
								  'mailDetails': [
								    {
								      'appParams': {"imageUrl":""},
								      'mailParams': {"parent":parent_name,
								      					"student":student_name['name'],
								      					"classtestName":testTitle,
								      					"startdate":createdate,
								      					"teacher":teacher_name},
								      'role': 'G1',
								      'toMail': '',
								      'toNumber': '',
								      'userId': parentID
								    }
								  ],
								  'sourceApp': 'CLST00G'
								}
						
						presponse = requests.post(url, data=json.dumps(pdata), headers=headers)
			assigned_status = 'Successfully Assigned to all'


		else:
			assigned_status = 'Already Assigned to selected students'


		cursor.close()
		cur.close()
		return ({"attributes": {"status_desc": "Create Test Details",
                                "status": "success",
                                "assigned_status":assigned_status
                                },
                 "responseList": assigned_to}), status.HTTP_200_OK


@class_test.route("/listOfAssignedStudents/<int:test_id>")
class listOfAssignedStudents(Resource):
	def get(self,test_id):
		connection = mysql_connection_lab_lang()
		cursor = connection.cursor()


		conn = mysql_connection()
		cur = conn.cursor()

		cursor.execute("""SELECT `student_id`,`status` FROM`classtest_student_mapping` 
			where `test_id` =%s""",(test_id))

		studentList = cursor.fetchall()

		if studentList:
			for i,std in enumerate(studentList):

				cursor.execute("""SELECT `student_id`,csr.`marks`,csr.`remarks`,csr.`parameter_id`,
					csr.`answersheet_filepath`,csr.`filetype` FROM `classtest_result` csr 
					Where csr.`student_id`= %s 
					and csr.`test_id` = %s""",(studentList[i]['student_id'],test_id))

				student_list = cursor.fetchall()

				if student_list:
					for s, stdnt in enumerate(student_list):
						studentList[i]['marks'] = student_list[s]['marks']
						studentList[i]['remarks'] = student_list[s]['remarks']
						studentList[i]['parameter_id'] = student_list[s]['parameter_id']
						studentList[i]['answersheet_filepath'] = student_list[s]['answersheet_filepath']
						studentList[i]['filetype'] = student_list[s]['filetype']
				else:
					studentList[i]['marks'] = ''
					studentList[i]['remarks'] = ''
					studentList[i]['parameter_id'] = ''
					studentList[i]['answersheet_filepath'] = ''
					studentList[i]['filetype'] = ''

				cur.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name, 
					`image_url` as student_image FROM `institution_user_credential` 
					WHERE `INSTITUTION_USER_ID` = %s""",(studentList[i]['student_id']))
				student_name = cur.fetchone()

				if student_name:
					studentList[i]['student_name'] = student_name['name']
					studentList[i]['student_image'] = student_name['student_image']
				else:
					studentList[i]['student_name'] = ''
					studentList[i]['student_image'] = ''
					
											
		cursor.close()
		cur.close()
		return ({"attributes": {"status_desc": "List of students assigned a ClassTest",
								"status": "success",
								},
				"responseList": studentList}), status.HTTP_200_OK



@class_test.route("/updateTestCompletionStatus/<int:student_id>/<int:test_id>")
class updateTestCompletionStatus(Resource):
	def put(self,student_id,test_id):
		connection = mysql_connection_lab_lang()
		cursor = connection.cursor()


		update_query = ("""UPDATE `classtest_student_mapping` SET `status` = %s
			where `test_id` = %s and `student_id` = %s""")

		update_data = ('c',test_id,student_id)

		cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()
		message = 'Status Update Successfully'
		return ({"attributes": {"status_desc": "Test Completion Status",
								"status": "success",
								},
				"responseList": message}), status.HTTP_200_OK

@class_test.route("/submitAnswerSheetOfClassTest")
class submitAnswerSheetOfClassTest(Resource):
	@api.expect(classtest_result)
	def post(self):
		details = request.get_json() 

		connection = mysql_connection_lab_lang()
		cursor = connection.cursor()


		submit_inser_query = ("""INSERT INTO `classtest_result`(`student_id`, `test_id`, `marks`, 
			`remarks`, `parameter_id`, `answersheet_filepath`, 
			`filetype`,`last_update_id`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""")

		submit_data = (details['student_id'],details['test_id'],details['marks'],details['remarks'],
			details['parameter_id'],details['answersheet_filepath'],details['filetype'],details['teacher_id'])


		cursor.execute(submit_inser_query,submit_data)
		details['submit_id'] = cursor.lastrowid
		connection.commit()
		cursor.close()
		message = 'Submission Successfully'
		return ({"attributes": {"status_desc": "Class Test Submission Details",
								"status": "success",
								"message":message
								},
				"responseList": details}), status.HTTP_200_OK


@class_test.route("/listOfTestsForStudents/<int:student_id>")
class listOfTestsForStudents(Resource):
	def get(self,student_id):
		connection = mysql_connection_lab_lang()
		cursor = connection.cursor()

		conn = mysql_connection()
		cur = conn.cursor()

		cursor.execute("""SELECT
							csm.`student_id`,
							csm.`status`,
							ct.`teacher_id`,
							ct.`test_type`,
							ct.`title`,
							ct.`remarks`,
							ct.`content_path` as 'question_filepath',
							ct.`content_file_type` as 'question_filetype',
							ct.`submisson_date`,
							ct.`exam_starttime`,
							ct.`exam_endtime`,
							DATE(ct.`last_update_ts`) AS 'assigned_on',
							csr.`marks`,
							csr.`remarks` as 'feedback',
							csr.`parameter_id`,
							csr.`answersheet_filepath`,
							csr.`filetype` as 'answer_filetype',
							st.`Class` 'classs',
							st.`Board` 'board'
							FROM
							`class_test` ct
							INNER JOIN classtest_student_mapping csm ON
							ct.`test_id` = csm.`test_id` AND csm.`student_id` = %s
							INNER JOIN student st ON csm.`student_id` = st.`Student_UserID`
							LEFT JOIN classtest_result csr on csm.`student_id` = csr.`student_id`
							AND csm.`test_id` = csr.`test_id` order by assigned_on desc""",(student_id))

		testList = cursor.fetchall()

		for t,test in enumerate(testList):
			test['submisson_date'] = test['submisson_date'].isoformat()
			test['exam_starttime'] = test['exam_starttime'].isoformat()
			test['exam_endtime'] = test['exam_endtime'].isoformat()
			test['assigned_on'] = test['assigned_on'].isoformat()

			cur.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name, 
				`image_url` as teacher_image FROM `institution_user_credential` 
				WHERE `INSTITUTION_USER_ID` = %s""",(test['teacher_id']))
			teacher_name = cur.fetchone()

			if teacher_name:
				testList[t]['teacher_name'] = teacher_name['name']
				testList[t]['teacher_image'] = teacher_name['teacher_image']


		cursor.close()
		cur.close()
		return ({"attributes": {"status_desc": "Class Test List",
								"status": "success",
								},
				"responseList": testList}), status.HTTP_200_OK

@name_space1.route("/updateAssignmentByAssignmentId/<int:assignment_id>")
class updateAssignmentByAssignmentId(Resource):
	@api.expect(updateassignment)
	def put(self,assignment_id):
		details = request.get_json()

		connection = mysql_connection_lab_lang()
		cursor = connection.cursor()

		conn = mysql_connection()
		cur = conn.cursor()
		cursor.execute("""SELECT `Teacher_ID`,`Title` FROM `assignment` 
			WHERE `Assignment_ID` = %s""",(assignment_id))
		assgnDtls = cursor.fetchone()
		teacher_id = assgnDtls.get('Teacher_ID')
		
		if details.get('assignmentTitle'):
			assignTitle = details.get('assignmentTitle')
		else:
			assignTitle = assgnDtls.get('Title')
		studentList = []
		cursor.execute("""SELECT `Student_UserID` FROM `assignment_mapping` 
			WHERE `Assignment_ID` = %s""",(assignment_id))
		stdntDtls = cursor.fetchall()
		
		try:
			if not details.get('content_path'):

				updateAssignmentQuery = ("""UPDATE `assignment` SET `Title` = %s
					WHERE `Assignment_ID` = %s""")

				updateData = (assignTitle,assignment_id)
			else:
				updateAssignmentQuery = ("""UPDATE `assignment` SET `Content_path` = %s,
					`Content_File_Type` = %s, `Assignment_Type` = %s, `Title` = %s
					 WHERE `Assignment_ID` = %s""")

				updateData = (details.get('content_path'),details.get('content_filetype'),
					details.get('content_filetype'),assignTitle,assignment_id)

			cursor.execute(updateAssignmentQuery,updateData)
			connection.commit()
			msg = 'Assignment Successfully Updated'

		except:
			msg = 'Assignment Not Updated'

		cursor.close()
		return ({"attributes": {"status_desc": "Assignment Updated Details",
								"status": "success",
								},
				"responseList": msg}), status.HTTP_200_OK