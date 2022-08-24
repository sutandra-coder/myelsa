from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from werkzeug.utils import cached_property
from database_connections import connect_elsalibrary,connect_logindb,connect_lab_lang1,connect_userLibrary
import requests
from pytz import timezone
from time import strftime
import pytz
import calendar
import json

app = Flask(__name__)
cors = CORS(app)

dashboard_section = Blueprint('dashboard_section_api', __name__)
api = Api(dashboard_section,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('MyelsaDashboard',description='Myelsa Dashboard')

#---------------------------------------------------------#


#--------------------------------------------------------#
@name_space.route("/DashboardSectionByDateFilterInstitutionId/<string:datefilterkey>/<int:institution_id>")
class DashboardSectionByDateFilterInstitutionId(Resource):
	def get(self,datefilterkey,institution_id):
		connection = connect_userLibrary()
		cursor = connection.cursor()
		labconn = connect_lab_lang1()
		labcur = labconn.cursor()
		logconn = connect_logindb()
		logcur = logconn.cursor()
		elsaconn = connect_elsalibrary()
		elsacur = elsaconn.cursor()

		details = []
		detail = []

		tdate = date.today()
		date_format='%Y-%m-%d %H:%M:%S'
		today = datetime.now(tz=pytz.utc)
		today = today.astimezone(timezone('Asia/Kolkata'))
		now = datetime.strftime(today,'%Y-%m-%d %H:%M:%S')
		todays = datetime.strptime(now,'%Y-%m-%d %H:%M:%S')
		

		cursor.execute("""SELECT count(`liveclass_id`)as total FROM `liveclass_mapping` 
			WHERE `institution_id`=%s""",(institution_id))

		totalliveclassData = cursor.fetchone()
		if totalliveclassData:
			totalliveclass = totalliveclassData['total']
		else:
			totalliveclass = 0

		cursor.execute("""SELECT count(`liveclass_id`)as total FROM `liveclass_mapping` 
			WHERE date(`start_date`)=%s and `end_date`>=%s and  
			`institution_id`=%s""",(tdate,today,institution_id))

		todaysliveclassData = cursor.fetchone()
		if todaysliveclassData:
			todaysliveclass = todaysliveclassData['total']
		else:
			todaysliveclass = 0

		cursor.execute("""SELECT count(`liveclass_id`)as total FROM `liveclass_mapping` 
			WHERE date(`start_date`)=%s and `end_date`>=%s and `institution_id`=%s""",(tdate,today,institution_id))

		upcomingliveclassData = cursor.fetchone()
		if upcomingliveclassData:
			upcomingliveclass = upcomingliveclassData['total']
		else:
			upcomingliveclass = 0

		cursor.execute("""SELECT count(`liveclass_id`)as total FROM `liveclass_mapping` 
			WHERE `start_date`<%s and `end_date`<%s and  
			`institution_id`=%s""",(today,today,institution_id))

		completediveclassData = cursor.fetchone()
		if completediveclassData:
			completedliveclass = completediveclassData['total']
		else:
			completedliveclass = 0

		if datefilterkey == 'today':

			logcur.execute("""SELECT `INSTITUTION_USER_ID` FROM 
				`institution_user_credential_master` WHERE `INSTITUTION_ID`=%s and 
				`INSTITUTION_USER_ROLE`='TA'""",(institution_id))
			teacherList = logcur.fetchall()
			
			logcur.execute("""SELECT `INSTITUTION_USER_ID` FROM 
				`institution_user_credential_master` WHERE `INSTITUTION_ID`=%s and 
				`INSTITUTION_USER_ROLE`='S1'""",(institution_id))
			studentList = logcur.fetchall()

			if teacherList != () or studentList != ():
				for i in teacherList:
					details.append(i['INSTITUTION_USER_ID'])
				teachers = tuple(details)
				
				for i in studentList:
					detail.append(i['INSTITUTION_USER_ID'])
				students = tuple(detail)

				labcur.execute("""SELECT `Assignment_ID` FROM `assignment` WHERE 
					`Teacher_ID` in (%s) and date(`Last_Update_TS`)= DATE(NOW())""",(format(teachers)))
				createdAssignmentData = labcur.fetchall()

				labcur.execute("""SELECT count(`Student_UserID`) FROM `assignment_mapping` WHERE 
					`Student_UserID` in (%s) and `Status`='c' and date(`Last_Update_TS`)= DATE(NOW())""",(format(students)))
				submittedAssignmentData = labcur.fetchall()

				elsacur.execute("""SELECT `exam_id` FROM `exam_master` WHERE `teacher_id` in (%s) 
					and date(`last_update_ts`)= DATE(NOW())""",(format(teachers)))
				createdExamData = elsacur.fetchall()

				elsacur.execute("""SELECT `mapping_id` FROM `student_exam_mapping` WHERE `student_id` in (%s) 
					and date(`last_update_ts`)= DATE(NOW())""",(format(students)))
				attemptedExamData = elsacur.fetchall()

			elsacur.execute("""SELECT `course_id` FROM `course` WHERE `institution_id`=%s and 
				date(`last_update_ts`)= DATE(NOW())""",(institution_id))
			createdCourseData = elsacur.fetchall()

			elsacur.execute("""SELECT `user_id` FROM `user_course_tracking` WHERE 
				`institution_id`=%s and date(`last_update_ts`)= DATE(NOW())""",(institution_id))
			seenCourseData = elsacur.fetchall()

			elsacur.execute("""SELECT `mapping_id`  FROM `student_course_master` WHERE 
				`Institution_ID`=%s and date(`last_update_ts`)= DATE(NOW())""",(institution_id))
			courseSubscribedStudent = elsacur.fetchall()		

		elif datefilterkey == 'yesterday':
			
			logcur.execute("""SELECT `INSTITUTION_USER_ID` FROM 
				`institution_user_credential_master` WHERE `INSTITUTION_ID`=%s and 
				`INSTITUTION_USER_ROLE`='TA'""",(institution_id))
			teacherList = logcur.fetchall()
			
			logcur.execute("""SELECT `INSTITUTION_USER_ID` FROM 
				`institution_user_credential_master` WHERE `INSTITUTION_ID`=%s and 
				`INSTITUTION_USER_ROLE`='S1'""",(institution_id))
			studentList = logcur.fetchall()

			if teacherList != () or studentList != ():
				for i in teacherList:
					details.append(i['INSTITUTION_USER_ID'])
				teachers = tuple(details)
				
				for i in studentList:
					detail.append(i['INSTITUTION_USER_ID'])
				students = tuple(detail)

				labcur.execute("""SELECT `Assignment_ID` FROM `assignment` WHERE 
					`Teacher_ID` in(%s) and date(`Last_Update_TS`)= DATE(NOW()) + INTERVAL -1 DAY""",(format(teachers)))
				createdAssignmentData = labcur.fetchall()
				
				labcur.execute("""SELECT `Student_UserID` FROM `assignment_mapping` WHERE 
					`Student_UserID` in (%s) and `Status`='c' and date(`Last_Update_TS`)= DATE(NOW()) + INTERVAL -1 DAY""",(format(students)))
				submittedAssignmentData = labcur.fetchall()

				elsacur.execute("""SELECT `exam_id` FROM `exam_master` WHERE `teacher_id` in (%s) 
					and date(`last_update_ts`)= DATE(NOW()) + INTERVAL -1 DAY""",(format(teachers)))
				createdExamData = elsacur.fetchall()

				elsacur.execute("""SELECT `mapping_id` FROM `student_exam_mapping` WHERE `student_id` in (%s) 
					and date(`last_update_ts`)= DATE(NOW()) + INTERVAL -1 DAY""",(format(students)))
				attemptedExamData = elsacur.fetchall()

			elsacur.execute("""SELECT `course_id` FROM `course` WHERE `institution_id`=%s 
				and date(`last_update_ts`)= DATE(NOW()) + INTERVAL -1 DAY""",(institution_id))
			createdCourseData = elsacur.fetchall()

			elsacur.execute("""SELECT `user_id` FROM `user_course_tracking` WHERE 
				`institution_id`=%s and date(`last_update_ts`)= DATE(NOW()) + INTERVAL -1 DAY""",(institution_id))
			seenCourseData = elsacur.fetchall()

			elsacur.execute("""SELECT `mapping_id`  FROM `student_course_master` WHERE 
				`Institution_ID`=%s and date(`last_update_ts`)= DATE(NOW()) + INTERVAL -1 DAY""",(institution_id))
			courseSubscribedStudent = elsacur.fetchall()

		elif datefilterkey == 'last 7 days':
			logcur.execute("""SELECT `INSTITUTION_USER_ID` FROM 
				`institution_user_credential_master` WHERE `INSTITUTION_ID`=%s and 
				`INSTITUTION_USER_ROLE`='TA'""",(institution_id))
			teacherList = logcur.fetchall()
			
			logcur.execute("""SELECT `INSTITUTION_USER_ID` FROM 
				`institution_user_credential_master` WHERE `INSTITUTION_ID`=%s and 
				`INSTITUTION_USER_ROLE`='S1'""",(institution_id))
			studentList = logcur.fetchall()

			if teacherList != () or studentList != ():
				for i in teacherList:
					details.append(i['INSTITUTION_USER_ID'])
				teachers = tuple(details)
				
				for i in studentList:
					detail.append(i['INSTITUTION_USER_ID'])
				students = tuple(detail)

				labcur.execute("""SELECT `Assignment_ID` FROM `assignment` WHERE 
					`Teacher_ID` in (%s) and date(`Last_Update_TS`)>= DATE(NOW()) + INTERVAL -7 DAY AND 
            		date(`Last_Update_TS`) < DATE(NOW()) + INTERVAL 0 DAY""",format(teachers))
				createdAssignmentData = labcur.fetchall()
				
				labcur.execute("""SELECT `Student_UserID` FROM `assignment_mapping` WHERE 
					`Student_UserID` in (%s) and `Status`='c' and date(`Last_Update_TS`)>= DATE(NOW()) + INTERVAL -7 DAY AND 
            		date(`Last_Update_TS`) < DATE(NOW()) + INTERVAL 0 DAY""",format(students))
				submittedAssignmentData = labcur.fetchall()

				elsacur.execute("""SELECT `exam_id` FROM `exam_master` WHERE `teacher_id` in (%s)
					and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",format(teachers))
				createdExamData = elsacur.fetchall()

				elsacur.execute("""SELECT `mapping_id` FROM `student_exam_mapping` WHERE `student_id` in (%s) 
					and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",format(students))
				attemptedExamData = elsacur.fetchall()

			elsacur.execute("""SELECT `course_id` FROM `course` WHERE `institution_id`=%s 
				and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(institution_id))
			createdCourseData = elsacur.fetchall()

			elsacur.execute("""SELECT `user_id` FROM `user_course_tracking` WHERE 
				`institution_id`=%s and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(institution_id))
			seenCourseData = elsacur.fetchall()

			elsacur.execute("""SELECT `mapping_id`  FROM `student_course_master` WHERE 
				`Institution_ID`=%s and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(institution_id))
			courseSubscribedStudent = elsacur.fetchall()

		elif datefilterkey == 'last month':
			logcur.execute("""SELECT `INSTITUTION_USER_ID` FROM 
				`institution_user_credential_master` WHERE `INSTITUTION_ID`=%s and 
				`INSTITUTION_USER_ROLE`='TA'""",(institution_id))
			teacherList = logcur.fetchall()
			
			logcur.execute("""SELECT `INSTITUTION_USER_ID` FROM 
				`institution_user_credential_master` WHERE `INSTITUTION_ID`=%s and 
				`INSTITUTION_USER_ROLE`='S1'""",(institution_id))
			studentList = logcur.fetchall()

			if teacherList != () or studentList != ():
				for i in teacherList:
					details.append(i['INSTITUTION_USER_ID'])
				teachers = tuple(details)
				
				for i in studentList:
					detail.append(i['INSTITUTION_USER_ID'])
				students = tuple(detail)

				labcur.execute("""SELECT `Assignment_ID` FROM `assignment` WHERE 
					`Teacher_ID` in (%s) and date(`Last_Update_TS`)>= DATE(NOW()) + INTERVAL -30 DAY AND 
            		date(`Last_Update_TS`) < DATE(NOW()) + INTERVAL 0 DAY""",format(teachers))
				createdAssignmentData = labcur.fetchall()
				
				labcur.execute("""SELECT `Student_UserID` FROM `assignment_mapping` WHERE 
					`Student_UserID` in (%s) and `Status`='c' and date(`Last_Update_TS`)>= DATE(NOW()) + INTERVAL -30 DAY AND 
            		date(`Last_Update_TS`) < DATE(NOW()) + INTERVAL 0 DAY""",format(students))
				submittedAssignmentData = labcur.fetchall()

				elsacur.execute("""SELECT `exam_id` FROM `exam_master` WHERE `teacher_id` in (%s) 
					and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -30 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",format(teachers))
				createdExamData = elsacur.fetchall()

				elsacur.execute("""SELECT `mapping_id` FROM `student_exam_mapping` WHERE `student_id` in (%s) 
					and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -30 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",format(students))
				attemptedExamData = elsacur.fetchall()

			elsacur.execute("""SELECT `course_id` FROM `course` WHERE `institution_id`=%s 
				and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -30 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(institution_id))
			createdCourseData = elsacur.fetchall()

			elsacur.execute("""SELECT `user_id` FROM `user_course_tracking` WHERE 
				`institution_id`=%s and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -30 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(institution_id))
			seenCourseData = elsacur.fetchall()

			elsacur.execute("""SELECT `mapping_id`  FROM `student_course_master` WHERE 
				`Institution_ID`=%s and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -30 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(institution_id))
			courseSubscribedStudent = elsacur.fetchall()

		if datefilterkey == 'lifetime':

			logcur.execute("""SELECT `INSTITUTION_USER_ID` FROM 
				`institution_user_credential_master` WHERE `INSTITUTION_ID`=%s and 
				`INSTITUTION_USER_ROLE`='TA'""",(institution_id))
			teacherList = logcur.fetchall()
			
			logcur.execute("""SELECT `INSTITUTION_USER_ID` FROM 
				`institution_user_credential_master` WHERE `INSTITUTION_ID`=%s and 
				`INSTITUTION_USER_ROLE`='S1'""",(institution_id))
			studentList = logcur.fetchall()

			if teacherList != () or studentList != ():
				for i in teacherList:
					details.append(i['INSTITUTION_USER_ID'])
				teachers = tuple(details)
				
				for i in studentList:
					detail.append(i['INSTITUTION_USER_ID'])
				students = tuple(detail)

				labcur.execute("""SELECT `Assignment_ID` FROM `assignment` WHERE 
					`Teacher_ID` in (%s)""",format(teachers))
				createdAssignmentData = labcur.fetchall()
				
				labcur.execute("""SELECT `Student_UserID` FROM `assignment_mapping` WHERE 
					`Student_UserID` in (%s) and `Status`='c'""",format(students))
				submittedAssignmentData = labcur.fetchall()

				elsacur.execute("""SELECT `exam_id` FROM `exam_master` WHERE `teacher_id` in (%s)""",format(teachers))
				createdExamData = elsacur.fetchall()

				elsacur.execute("""SELECT `mapping_id` FROM `student_exam_mapping` WHERE `student_id` in (%s)""",format(students))
				attemptedExamData = elsacur.fetchall()

			elsacur.execute("""SELECT `course_id` FROM `course` WHERE `institution_id`=%s""",(institution_id))
			createdCourseData = elsacur.fetchall()

			elsacur.execute("""SELECT `user_id` FROM `user_course_tracking` WHERE 
				`institution_id`=%s""",(institution_id))
			seenCourseData = elsacur.fetchall()

			elsacur.execute("""SELECT `mapping_id`  FROM `student_course_master` WHERE 
				`Institution_ID`=%s""",(institution_id))
			courseSubscribedStudent = elsacur.fetchall()
		
		cursor.close()
		logcur.close()
		labcur.close()
		elsacur.close()

		return ({"attributes": {
	    				"status_desc": "Dashboard Details",
	    				"status": "success"
	    				},
	    				"responseList":{
								"totalLiveClass": totalliveclass,
								"todaysLiveClass": todaysliveclass,
								"upcomingLiveClass": upcomingliveclass,
								"completedLiveClass": completedliveclass,
								"createdAssignment":len(createdAssignmentData),
								"submittedAssignment":len(submittedAssignmentData),
								"createdCourse":len(createdCourseData),
								"seenCourse":len(seenCourseData),
								"courseSubscribedStudent":len(courseSubscribedStudent),
								"coursesellAmount":0,
								"createdExam":len(createdExamData),
								"attemptedExam":len(attemptedExamData),
								"seenExam":0,
								"examsellAmount":0
								} 
								}), status.HTTP_200_OK
#--------------------------------------------------------#


#------------------------------------------------------RITAM CREATED API------------------------------------------------------------------------#

@name_space.route("/DashboardSectionByDateFilterInstitutionIdV3/<string:datefilterkey>/<int:institution_user_id>")
class DashboardSectionByDateFilterInstitutionIdV3(Resource):
	def get(self,datefilterkey,institution_user_id):
		connection = connect_userLibrary()
		cursor = connection.cursor()
		labconn = connect_lab_lang1()
		labcur = labconn.cursor()
		logconn = connect_logindb()
		logcur = logconn.cursor()
		elsaconn = connect_elsalibrary()
		elsacur = elsaconn.cursor()

		details = []
		detail = []
		teachers=()
		students=()

		tdate = date.today()
		date_format='%Y-%m-%d %H:%M:%S'
		today = datetime.now(tz=pytz.utc)
		today = today.astimezone(timezone('Asia/Kolkata'))
		now = datetime.strftime(today,'%Y-%m-%d %H:%M:%S')
		todays = datetime.strptime(now,'%Y-%m-%d %H:%M:%S')
		totalliveclass=0
		todaysliveclass=0
		upcomingliveclass=0
		completedliveclass = 0
		createdAssignmentData = []
		submittedAssignmentData = []
		createdExamData = []
		attemptedExamData = []
		createdCourseData = []
		seenCourseData = []
		courseSubscribedStudent =[]
		
		

		logcur.execute("""SELECT `INSTITUTION_USER_ROLE` as role FROM `institution_user_credential_master` WHERE `INSTITUTION_USER_ID`=%s""",(institution_user_id))
		user_role_info=logcur.fetchall()

		for i in user_role_info:
			user_role = i
			role = user_role['role']
		
		if role =='A1':
			logcur.execute("""SELECT `INSTITUTION_ID` as id FROM `institution_user_credential_master` WHERE `INSTITUTION_USER_ID`=%s""",(institution_user_id))
			institution_id=logcur.fetchall()

			for i in institution_id:
				inst_id = i
				institute_id = inst_id['id']

			cursor.execute("""SELECT count(`liveclass_id`)as total FROM `liveclass_mapping` 
			WHERE `institution_id`=%s""",(institute_id))
			totalliveclassData = cursor.fetchone()
			if totalliveclassData:
				totalliveclass = totalliveclassData['total']
			else:
				totalliveclass = 0

			cursor.execute("""SELECT count(`liveclass_id`)as total FROM `liveclass_mapping` 
			WHERE date(`start_date`)=%s and `end_date`>=%s and  
			`institution_id`=%s""",(tdate,today,institute_id))

			todaysliveclassData = cursor.fetchone()
			if todaysliveclassData:
				todaysliveclass = todaysliveclassData['total']
			else:
				todaysliveclass = 0

			cursor.execute("""SELECT count(`liveclass_id`)as total FROM `liveclass_mapping` 
			WHERE date(`start_date`)=%s and `end_date`>=%s and `institution_id`=%s""",(tdate,today,institute_id))

			upcomingliveclassData = cursor.fetchone()
			if upcomingliveclassData:
				upcomingliveclass = upcomingliveclassData['total']
			else:
				upcomingliveclass = 0

			cursor.execute("""SELECT count(`liveclass_id`)as total FROM `liveclass_mapping` 
			WHERE `start_date`<%s and `end_date`<%s and  
			`institution_id`=%s""",(today,today,institute_id))

			completediveclassData = cursor.fetchone()

			if completediveclassData:
				completedliveclass = completediveclassData['total']

			else:
				completedliveclass = 0

			if datefilterkey == 'today':

				logcur.execute("""SELECT `INSTITUTION_USER_ID` FROM 
				`institution_user_credential_master` WHERE `INSTITUTION_ID`=%s and 
				`INSTITUTION_USER_ROLE`='TA'""",(institute_id))

				teacherList = logcur.fetchall()

				logcur.execute("""SELECT `INSTITUTION_USER_ID` FROM 
				`institution_user_credential_master` WHERE `INSTITUTION_ID`=%s and 
				`INSTITUTION_USER_ROLE`='S1'""",(institute_id))

				studentList = logcur.fetchall()

				if teacherList != () or studentList != ():
					for i in teacherList:
						details.append(i['INSTITUTION_USER_ID'])
					teachers = tuple(details)

					for j in studentList:
						detail.append(j['INSTITUTION_USER_ID'])
					students = tuple(detail)

					labcur.execute("""SELECT `Assignment_ID` FROM `assignment` WHERE 
					`Teacher_ID` in(%s) and date(`Last_Update_TS`)= DATE(NOW())""",format(teachers))

					createdAssignmentData = labcur.fetchall()

				

					labcur.execute("""SELECT count(`Student_UserID`) FROM `assignment_mapping` WHERE 
					`Student_UserID` in (%s) and `Status`='c' and date(`Last_Update_TS`)= DATE(NOW())""",(format(students)))

					submittedAssignmentData = labcur.fetchall()

					elsacur.execute("""SELECT `exam_id` FROM `exam_master` WHERE `teacher_id` in (%s) 
					and date(`last_update_ts`)= DATE(NOW())""",(format(teachers)))

					createdExamData = elsacur.fetchall()

					elsacur.execute("""SELECT `mapping_id` FROM `student_exam_mapping` WHERE `student_id` in (%s) 
					and date(`last_update_ts`)= DATE(NOW())""",(format(students)))

					attemptedExamData = elsacur.fetchall()

				elsacur.execute("""SELECT `course_id` FROM `course` WHERE `institution_id`=%s and 
				date(`last_update_ts`)= DATE(NOW())""",(institute_id))

				createdCourseData = elsacur.fetchall()

				elsacur.execute("""SELECT distinct `user_id` FROM `user_course_tracking` WHERE 
				`institution_id`=%s and date(`last_update_ts`)= DATE(NOW())""",(institute_id))

				seenCourseData = elsacur.fetchall()

				elsacur.execute("""SELECT `mapping_id`  FROM `student_course_master` WHERE 
				`Institution_ID`=%s and date(`last_update_ts`)= DATE(NOW())""",(institute_id))

				courseSubscribedStudent = elsacur.fetchall()

			elif datefilterkey == 'yesterday':
				logcur.execute("""SELECT `INSTITUTION_USER_ID` FROM 
				`institution_user_credential_master` WHERE `INSTITUTION_ID`=%s and 
				`INSTITUTION_USER_ROLE`='TA'""",(institute_id))

				teacherList = logcur.fetchall()

				logcur.execute("""SELECT `INSTITUTION_USER_ID` FROM 
				`institution_user_credential_master` WHERE `INSTITUTION_ID`=%s and 
				`INSTITUTION_USER_ROLE`='S1'""",(institute_id))

				studentList = logcur.fetchall()

				if teacherList != () or studentList != ():
					for i in teacherList:
						details.append(i['INSTITUTION_USER_ID'])
					teachers = tuple(details)

					for i in studentList:
						detail.append(i['INSTITUTION_USER_ID'])
					students = tuple(details)

					labcur.execute("""SELECT `Assignment_ID` FROM `assignment` WHERE 
					`Teacher_ID` in(%s) and date(`Last_Update_TS`)= DATE(NOW()) + INTERVAL -1 DAY""",(format(teachers)))

					createdAssignmentData = labcur.fetchall()

					labcur.execute("""SELECT `Student_UserID` FROM `assignment_mapping` WHERE 
					`Student_UserID` in (%s) and `Status`='c' and date(`Last_Update_TS`)= DATE(NOW()) + INTERVAL -1 DAY""",(format(students)))

					submittedAssignmentData = labcur.fetchall()

					elsacur.execute("""SELECT `exam_id` FROM `exam_master` WHERE `teacher_id` in (%s) 
					and date(`last_update_ts`)= DATE(NOW()) + INTERVAL -1 DAY""",(format(teachers)))

					createdExamData = elsacur.fetchall()

					elsacur.execute("""SELECT `mapping_id` FROM `student_exam_mapping` WHERE `student_id` in (%s) 
					and date(`last_update_ts`)= DATE(NOW()) + INTERVAL -1 DAY""",(format(students)))

					attemptedExamData = elsacur.fetchall()

				elsacur.execute("""SELECT `course_id` FROM `course` WHERE `institution_id`=%s 
				and date(`last_update_ts`)= DATE(NOW()) + INTERVAL -1 DAY""",(institute_id))

				createdCourseData = elsacur.fetchall()

				elsacur.execute("""SELECT distinct `user_id` FROM `user_course_tracking` WHERE 
				`institution_id`=%s and date(`last_update_ts`)= DATE(NOW()) + INTERVAL -1 DAY""",(institute_id))

				seenCourseData = elsacur.fetchall()

				elsacur.execute("""SELECT `mapping_id`  FROM `student_course_master` WHERE 
				`Institution_ID`=%s and date(`last_update_ts`)= DATE(NOW()) + INTERVAL -1 DAY""",(institute_id))

				courseSubscribedStudent = elsacur.fetchall()

				elsacur.execute("""SELECT `student_id`  FROM `student_course_master` WHERE `Institution_ID`=%s""",(institute_id))
				courseSubscribedStudent = elsacur.fetchall()		
				subsribeddetails = []
				if courseSubscribedStudent != ():
					for k in courseSubscribedStudent:
						subsribeddetails.append(k['student_id'])
						subsribedStudents = subsribeddetails

						logcur.execute("""SELECT SUM(amount)as total FROM `razorpay_payment_dtls` where `user_id` in(%s)""",format(subsribedStudents))

						razorData = logcur.fetchone()
						
						if razorData:
							coursesellAmount = razorData['total']
						else:
							coursesellAmount = 0

			elif datefilterkey == 'last 7 days':
				logcur.execute("""SELECT `INSTITUTION_USER_ID` FROM 
				`institution_user_credential_master` WHERE `INSTITUTION_ID`=%s and 
				`INSTITUTION_USER_ROLE`='TA'""",(institute_id))

				teacherList = logcur.fetchall()

				logcur.execute("""SELECT `INSTITUTION_USER_ID` FROM 
				`institution_user_credential_master` WHERE `INSTITUTION_ID`=%s and 
				`INSTITUTION_USER_ROLE`='S1'""",(institute_id))

				studentList = logcur.fetchall()

				if teacherList != () or studentList != ():
					for i in teacherList:
						details.append(i['INSTITUTION_USER_ID'])
					teachers = tuple(details)

					for i in studentList:
						detail.append(i['INSTITUTION_USER_ID'])
					students = tuple(detail)

				labcur.execute("""SELECT `Assignment_ID` FROM `assignment` WHERE 
					`Teacher_ID` in (%s) and date(`Last_Update_TS`)>= DATE(NOW()) + INTERVAL -7 DAY AND 
            		date(`Last_Update_TS`) < DATE(NOW()) + INTERVAL 0 DAY""",format(teachers))
				createdAssignmentData = labcur.fetchall()
				
				labcur.execute("""SELECT `Student_UserID` FROM `assignment_mapping` WHERE 
					`Student_UserID` in (%s) and `Status`='c' and date(`Last_Update_TS`)>= DATE(NOW()) + INTERVAL -7 DAY AND 
            		date(`Last_Update_TS`) < DATE(NOW()) + INTERVAL 0 DAY""",format(students))
				submittedAssignmentData = labcur.fetchall()

				elsacur.execute("""SELECT `exam_id` FROM `exam_master` WHERE `teacher_id` in (%s)
					and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",format(teachers))
				createdExamData = elsacur.fetchall()

				elsacur.execute("""SELECT `mapping_id` FROM `student_exam_mapping` WHERE `student_id` in (%s) 
					and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",format(students))
				attemptedExamData = elsacur.fetchall()

				elsacur.execute("""SELECT `course_id` FROM `course` WHERE `institution_id`=%s 
				and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(institute_id))

				createdCourseData = elsacur.fetchall()

				elsacur.execute("""SELECT distinct `user_id` FROM `user_course_tracking` WHERE 
				`institution_id`=%s and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(institute_id))

				seenCourseData = elsacur.fetchall()

				elsacur.execute("""SELECT `mapping_id`  FROM `student_course_master` WHERE 
				`Institution_ID`=%s and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(institute_id))

				courseSubscribedStudent = elsacur.fetchall()

			elif datefilterkey == 'last month':
				logcur.execute("""SELECT `INSTITUTION_USER_ID` FROM 
				`institution_user_credential_master` WHERE `INSTITUTION_ID`=%s and 
				`INSTITUTION_USER_ROLE`='TA'""",(institute_id))

				teacherList = logcur.fetchall()

				logcur.execute("""SELECT `INSTITUTION_USER_ID` FROM 
				`institution_user_credential_master` WHERE `INSTITUTION_ID`=%s and 
				`INSTITUTION_USER_ROLE`='S1'""",(institute_id))

				studentList = logcur.fetchall()

				if teacherList != () or studentList != ():
					for i in teacherList:
						details.append(i['INSTITUTION_USER_ID'])
					teachers = tuple(details)

					for i in studentList:
						detail.append(i['INSTITUTION_USER_ID'])
					students = tuple(detail)

				labcur.execute("""SELECT `Assignment_ID` FROM `assignment` WHERE 
					`Teacher_ID` in (%s) and date(`Last_Update_TS`)>= DATE(NOW()) + INTERVAL -30 DAY AND 
            		date(`Last_Update_TS`) < DATE(NOW()) + INTERVAL 0 DAY""",format(teachers))
				createdAssignmentData = labcur.fetchall()
				
				labcur.execute("""SELECT `Student_UserID` FROM `assignment_mapping` WHERE 
					`Student_UserID` in (%s) and `Status`='c' and date(`Last_Update_TS`)>= DATE(NOW()) + INTERVAL -30 DAY AND 
            		date(`Last_Update_TS`) < DATE(NOW()) + INTERVAL 0 DAY""",format(students))
				submittedAssignmentData = labcur.fetchall()

				elsacur.execute("""SELECT `exam_id` FROM `exam_master` WHERE `teacher_id` in (%s) 
					and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -30 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",format(teachers))
				createdExamData = elsacur.fetchall()

				elsacur.execute("""SELECT `mapping_id` FROM `student_exam_mapping` WHERE `student_id` in (%s) 
					and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -30 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",format(students))
				attemptedExamData = elsacur.fetchall()

				elsacur.execute("""SELECT `course_id` FROM `course` WHERE `institution_id`=%s 
				and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -30 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(institute_id))

				createdCourseData = elsacur.fetchall()

				elsacur.execute("""SELECT distinct `user_id` FROM `user_course_tracking` WHERE 
				`institution_id`=%s and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -30 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(institute_id))

				seenCourseData = elsacur.fetchall()

				elsacur.execute("""SELECT `mapping_id`  FROM `student_course_master` WHERE 
				`Institution_ID`=%s and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -30 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(institute_id))

				courseSubscribedStudent = elsacur.fetchall()


			elif datefilterkey == 'lifetime':
				logcur.execute("""SELECT `INSTITUTION_USER_ID` FROM 
				`institution_user_credential_master` WHERE `INSTITUTION_ID`=%s and 
				`INSTITUTION_USER_ROLE`='TA'""",(institute_id))

				teacherList = logcur.fetchall()

				logcur.execute("""SELECT `INSTITUTION_USER_ID` FROM 
				`institution_user_credential_master` WHERE `INSTITUTION_ID`=%s and 
				`INSTITUTION_USER_ROLE`='S1'""",(institute_id))

				studentList = logcur.fetchall()

				if teacherList != () or studentList != ():
					for i in teacherList:
						details.append(i['INSTITUTION_USER_ID'])
					teachers = tuple(details)

					for i in studentList:
						detail.append(i['INSTITUTION_USER_ID'])
					students = tuple(detail)

				labcur.execute("""SELECT `Assignment_ID` FROM `assignment` WHERE 
					`Teacher_ID` in (%s)""",format(teachers))
				createdAssignmentData = labcur.fetchall()
				
				labcur.execute("""SELECT `Student_UserID` FROM `assignment_mapping` WHERE 
					`Student_UserID` in (%s) and `Status`='c'""",format(students))
				submittedAssignmentData = labcur.fetchall()

				elsacur.execute("""SELECT `exam_id` FROM `exam_master` WHERE `teacher_id` in (%s)""",format(teachers))
				createdExamData = elsacur.fetchall()

				elsacur.execute("""SELECT `mapping_id` FROM `student_exam_mapping` WHERE `student_id` in (%s)""",format(students))
				attemptedExamData = elsacur.fetchall()

				elsacur.execute("""SELECT `course_id` FROM `course` WHERE `institution_id`=%s""",(institute_id))

				createdCourseData = elsacur.fetchall()

				elsacur.execute("""SELECT distinct `user_id` FROM `user_course_tracking` WHERE 
				`institution_id`=%s""",(institute_id))

				seenCourseData = elsacur.fetchall()

				elsacur.execute("""SELECT `mapping_id`  FROM `student_course_master` WHERE 
				`Institution_ID`=%s""",(institute_id))

				courseSubscribedStudent = elsacur.fetchall()

		elif role =='TA':
			logcur.execute("""SELECT `INSTITUTION_ID` as id FROM `institution_user_credential_master` WHERE `INSTITUTION_USER_ID`=%s""",(institution_user_id))
			institution_id=logcur.fetchall()

			for i in institution_id:
				inst_id = i
				institute_id = inst_id['id']
			cursor.execute("""SELECT count(`liveclass_id`)as total FROM `liveclass_mapping` 
			WHERE `teacher_id`=%s""",(institution_user_id))
			totalliveclassData = cursor.fetchone()

			if totalliveclassData:
				totalliveclass = totalliveclassData['total']
			else:
				totalliveclass = 0

			cursor.execute("""SELECT count(`liveclass_id`)as total FROM `liveclass_mapping` 
			WHERE date(`start_date`)=%s and `end_date`>=%s and  
			`teacher_id`=%s""",(tdate,today,institution_user_id))

			todaysliveclassData = cursor.fetchone()
			if todaysliveclassData:
				todaysliveclass = todaysliveclassData['total']
			else:
				todaysliveclass = 0

			cursor.execute("""SELECT count(`liveclass_id`)as total FROM `liveclass_mapping` 
			WHERE date(`start_date`)=%s and `end_date`>=%s and `teacher_id`=%s""",(tdate,today,institution_user_id))

			upcomingliveclassData = cursor.fetchone()
			if upcomingliveclassData:
				upcomingliveclass = upcomingliveclassData['total']
			else:
				upcomingliveclass = 0

			cursor.execute("""SELECT count(`liveclass_id`)as total FROM `liveclass_mapping` 
			WHERE `start_date`<%s and `end_date`<%s and  
			`teacher_id`=%s""",(today,today,institution_user_id))

			completediveclassData = cursor.fetchone()

			if completediveclassData:
				completedliveclass = completediveclassData['total']

			else:
				completedliveclass = 0

			if datefilterkey == 'today':

				logcur.execute("""SELECT `INSTITUTION_USER_ID` FROM 
				`institution_user_credential_master` WHERE `INSTITUTION_ID`=%s and 
				`INSTITUTION_USER_ROLE`='S1'""",(institute_id))

				studentList = logcur.fetchall()

				if studentList != ():
					for j in studentList:
						detail.append(j['INSTITUTION_USER_ID'])
					students = tuple(detail)

				labcur.execute("""SELECT `Assignment_ID` FROM `assignment` WHERE 
				`Teacher_ID` in(%s) and date(`Last_Update_TS`)= DATE(NOW())""",(institution_user_id))

				createdAssignmentData = labcur.fetchall()

				
				labcur.execute("""SELECT count(`Student_UserID`) FROM `assignment_mapping` WHERE 
				`Student_UserID` in (%s) and `Status`='c' and date(`Last_Update_TS`)= DATE(NOW())""",(format(students)))

				submittedAssignmentData = labcur.fetchall()

				elsacur.execute("""SELECT `exam_id` FROM `exam_master` WHERE `teacher_id` in (%s) 
				and date(`last_update_ts`)= DATE(NOW())""",(institution_user_id))

				createdExamData = elsacur.fetchall()

				elsacur.execute("""SELECT `mapping_id` FROM `student_exam_mapping` WHERE `student_id` in (%s) 
				and date(`last_update_ts`)= DATE(NOW())""",(format(students)))

				attemptedExamData = elsacur.fetchall()

				elsacur.execute("""SELECT `course_id` FROM `course` WHERE `teacher_id`=%s and 
				date(`last_update_ts`)= DATE(NOW())""",(institution_user_id))

				createdCourseData = elsacur.fetchall()

				elsacur.execute("""SELECT distinct `user_id` FROM `user_course_tracking` WHERE 
				`institution_id`=%s and date(`last_update_ts`)= DATE(NOW())""",(institute_id))

				seenCourseData = elsacur.fetchall()

				elsacur.execute("""SELECT `mapping_id`  FROM `student_course_master` WHERE 
				`teacher_ID`=%s and date(`last_update_ts`)= DATE(NOW())""",(institution_user_id))

				courseSubscribedStudent = elsacur.fetchall()


			elif datefilterkey == 'yesterday':
				
				logcur.execute("""SELECT `INSTITUTION_USER_ID` FROM 
				`institution_user_credential_master` WHERE `INSTITUTION_ID`=%s and 
				`INSTITUTION_USER_ROLE`='S1'""",(institute_id))

				studentList = logcur.fetchall()

				if  studentList != ():
					
					for i in studentList:
						detail.append(i['INSTITUTION_USER_ID'])
					students = tuple(details)

				labcur.execute("""SELECT `Assignment_ID` FROM `assignment` WHERE 
				`Teacher_ID` in(%s) and date(`Last_Update_TS`)= DATE(NOW()) + INTERVAL -1 DAY""",(institution_user_id))

				createdAssignmentData = labcur.fetchall()

				labcur.execute("""SELECT `Student_UserID` FROM `assignment_mapping` WHERE 
				`Student_UserID` in (%s) and `Status`='c' and date(`Last_Update_TS`)= DATE(NOW()) + INTERVAL -1 DAY""",(format(students)))

				submittedAssignmentData = labcur.fetchall()

				elsacur.execute("""SELECT `exam_id` FROM `exam_master` WHERE `teacher_id` in (%s) 
				and date(`last_update_ts`)= DATE(NOW()) + INTERVAL -1 DAY""",(institution_user_id))

				createdExamData = elsacur.fetchall()

				elsacur.execute("""SELECT `mapping_id` FROM `student_exam_mapping` WHERE `student_id` in (%s) 
				and date(`last_update_ts`)= DATE(NOW()) + INTERVAL -1 DAY""",(format(students)))

				attemptedExamData = elsacur.fetchall()

				elsacur.execute("""SELECT `course_id` FROM `course` WHERE `teacher_id`=%s 
				and date(`last_update_ts`)= DATE(NOW()) + INTERVAL -1 DAY""",(institution_user_id))

				createdCourseData = elsacur.fetchall()

				elsacur.execute("""SELECT distinct `user_id` FROM `user_course_tracking` WHERE 
				`institution_id`=%s and date(`last_update_ts`)= DATE(NOW()) + INTERVAL -1 DAY""",(institute_id))

				seenCourseData = elsacur.fetchall()

				elsacur.execute("""SELECT `mapping_id`  FROM `student_course_master` WHERE 
				`teacher_id`=%s and date(`last_update_ts`)= DATE(NOW()) + INTERVAL -1 DAY""",(institution_user_id))

				courseSubscribedStudent = elsacur.fetchall()

				elsacur.execute("""SELECT `student_id`  FROM `student_course_master` WHERE `teacher_id`=%s""",(institution_user_id))
				courseSubscribedStudent = elsacur.fetchall()		
				subsribeddetails = []
				if courseSubscribedStudent != ():
					for k in courseSubscribedStudent:
						subsribeddetails.append(k['student_id'])
						subsribedStudents = subsribeddetails

						logcur.execute("""SELECT SUM(amount)as total FROM `razorpay_payment_dtls` where `user_id` in(%s)""",format(subsribedStudents))

						razorData = logcur.fetchone()

						if razorData:
							coursesellAmount = razorData['total']
						else:
							coursesellAmount = 0

			elif datefilterkey == 'last 7 days':
				
				logcur.execute("""SELECT `INSTITUTION_USER_ID` FROM 
				`institution_user_credential_master` WHERE `INSTITUTION_ID`=%s and 
				`INSTITUTION_USER_ROLE`='S1'""",(institute_id))

				studentList = logcur.fetchall()

				if studentList != ():
					
					for i in studentList:
						detail.append(i['INSTITUTION_USER_ID'])
					students = tuple(detail)

				labcur.execute("""SELECT `Assignment_ID` FROM `assignment` WHERE 
					`Teacher_ID` in (%s) and date(`Last_Update_TS`)>= DATE(NOW()) + INTERVAL -7 DAY AND 
            		date(`Last_Update_TS`) < DATE(NOW()) + INTERVAL 0 DAY""",(institution_user_id))
				createdAssignmentData = labcur.fetchall()
				
				labcur.execute("""SELECT `Student_UserID` FROM `assignment_mapping` WHERE 
					`Student_UserID` in (%s) and `Status`='c' and date(`Last_Update_TS`)>= DATE(NOW()) + INTERVAL -7 DAY AND 
            		date(`Last_Update_TS`) < DATE(NOW()) + INTERVAL 0 DAY""",format(students))
				submittedAssignmentData = labcur.fetchall()

				elsacur.execute("""SELECT `exam_id` FROM `exam_master` WHERE `teacher_id` in (%s)
					and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(institution_user_id))
				createdExamData = elsacur.fetchall()

				elsacur.execute("""SELECT `mapping_id` FROM `student_exam_mapping` WHERE `student_id` in (%s) 
					and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",format(students))
				attemptedExamData = elsacur.fetchall()

				elsacur.execute("""SELECT `course_id` FROM `course` WHERE `teacher_id`=%s 
				and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(institution_user_id))

				createdCourseData = elsacur.fetchall()

				elsacur.execute("""SELECT distinct `user_id` FROM `user_course_tracking` WHERE 
				`institution_id`=%s and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(institute_id))

				seenCourseData = elsacur.fetchall()

				elsacur.execute("""SELECT `mapping_id`  FROM `student_course_master` WHERE 
				`teacher_id`=%s and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(institution_user_id))

				courseSubscribedStudent = elsacur.fetchall()

			elif datefilterkey == 'last month':
				

				logcur.execute("""SELECT `INSTITUTION_USER_ID` FROM 
				`institution_user_credential_master` WHERE `INSTITUTION_ID`=%s and 
				`INSTITUTION_USER_ROLE`='S1'""",(institute_id))

				studentList = logcur.fetchall()

				if studentList != ():
					
					for i in studentList:
						detail.append(i['INSTITUTION_USER_ID'])
					students = tuple(detail)

				labcur.execute("""SELECT `Assignment_ID` FROM `assignment` WHERE 
					`Teacher_ID` in (%s) and date(`Last_Update_TS`)>= DATE(NOW()) + INTERVAL -30 DAY AND 
            		date(`Last_Update_TS`) < DATE(NOW()) + INTERVAL 0 DAY""",(institution_user_id))
				createdAssignmentData = labcur.fetchall()
				
				labcur.execute("""SELECT `Student_UserID` FROM `assignment_mapping` WHERE 
					`Student_UserID` in (%s) and `Status`='c' and date(`Last_Update_TS`)>= DATE(NOW()) + INTERVAL -30 DAY AND 
            		date(`Last_Update_TS`) < DATE(NOW()) + INTERVAL 0 DAY""",format(students))
				submittedAssignmentData = labcur.fetchall()

				elsacur.execute("""SELECT `exam_id` FROM `exam_master` WHERE `teacher_id` in (%s) 
					and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -30 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(institution_user_id))
				createdExamData = elsacur.fetchall()

				elsacur.execute("""SELECT `mapping_id` FROM `student_exam_mapping` WHERE `student_id` in (%s) 
					and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -30 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",format(students))
				attemptedExamData = elsacur.fetchall()

				elsacur.execute("""SELECT `course_id` FROM `course` WHERE `teacher_id`=%s 
				and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -30 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(institution_user_id))

				createdCourseData = elsacur.fetchall()

				elsacur.execute("""SELECT distinct `user_id` FROM `user_course_tracking` WHERE 
				`institution_id`=%s and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -30 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(institute_id))

				seenCourseData = elsacur.fetchall()

				elsacur.execute("""SELECT `mapping_id`  FROM `student_course_master` WHERE 
				`teacher_id`=%s and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -30 DAY AND 
            		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(institution_user_id))

				courseSubscribedStudent = elsacur.fetchall()


			elif datefilterkey == 'lifetime':
				

				logcur.execute("""SELECT `INSTITUTION_USER_ID` FROM 
				`institution_user_credential_master` WHERE `INSTITUTION_ID`=%s and 
				`INSTITUTION_USER_ROLE`='S1'""",(institute_id))

				studentList = logcur.fetchall()

				if studentList != ():
					

					for i in studentList:
						detail.append(i['INSTITUTION_USER_ID'])
					students = tuple(detail)

				labcur.execute("""SELECT `Assignment_ID` FROM `assignment` WHERE 
					`Teacher_ID` in (%s)""",(institution_user_id))
				createdAssignmentData = labcur.fetchall()
				
				labcur.execute("""SELECT `Student_UserID` FROM `assignment_mapping` WHERE 
					`Student_UserID` in (%s) and `Status`='c'""",format(students))
				submittedAssignmentData = labcur.fetchall()

				elsacur.execute("""SELECT `exam_id` FROM `exam_master` WHERE `teacher_id` in (%s)""",(institution_user_id))
				createdExamData = elsacur.fetchall()

				elsacur.execute("""SELECT `mapping_id` FROM `student_exam_mapping` WHERE `student_id` in (%s)""",format(students))
				attemptedExamData = elsacur.fetchall()

				elsacur.execute("""SELECT `course_id` FROM `course` WHERE `teacher_id`=%s""",(institution_user_id))

				createdCourseData = elsacur.fetchall()

				elsacur.execute("""SELECT distinct `user_id` FROM `user_course_tracking` WHERE 
				`institution_id`=%s""",(institute_id))

				seenCourseData = elsacur.fetchall()

				elsacur.execute("""SELECT `mapping_id`  FROM `student_course_master` WHERE 
				`teacher_id`=%s""",(institution_user_id))

				courseSubscribedStudent = elsacur.fetchall()



					

            	



		labcur.close()
		logcur.close()
		cursor.close()
		elsacur.close()

		return ({"attributes": {
	    				"status_desc": "Dashboard Details",
	    				"status": "success"
	    				},
	    				"responseList":{
								"totalLiveClass": totalliveclass,
								"todaysLiveClass": todaysliveclass,
								"upcomingLiveClass": upcomingliveclass,
								"completedLiveClass": completedliveclass,
								"createdAssignment":len(createdAssignmentData),
								"submittedAssignment":len(submittedAssignmentData),
								"createdCourse":len(createdCourseData),
								"seenCourse":len(seenCourseData),
								"courseSubscribedStudent":len(courseSubscribedStudent),
								"coursesellAmount":0,
								"createdExam":len(createdExamData),
								"attemptedExam":len(attemptedExamData),
								"seenExam":0,
								"examsellAmount":0,
								
								
								} 
								}), status.HTTP_200_OK

#ritam - 30-11-21
@name_space.route("/GetGoalsByUserId/<int:user_id>")
class GetGoalsByUserId(Resource):
	def get(self,user_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		cursor.execute("""SELECT ugt.`goal_id`,ugt.`institution_id`,s.`subject_name` FROM `user_goal_tracking` ugt INNER JOIN `subject` s ON ugt.`goal_id` = s.`subject_id` WHERE `user_id` = %s""",(user_id))
		goals = cursor.fetchall()

		cursor.close()
		return ({"attributes": {
    				"status_desc": "Goal Details",
    				"status": "success"
    				},
			"responseList":goals }), status.HTTP_200_OK

@name_space.route("/GetAllNonSetGoalsByUserIdInsId/<int:user_id>/<int:institution_id>")
class GetAllNonSetGoalsByUserIdInsId(Resource):
	def get(self,user_id,institution_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details=[]
		
		cursor.execute("""SELECT `goal_id` FROM `user_goal_tracking` WHERE `user_id`=%s AND `institution_id`=%s""",(user_id,institution_id))
		goal_id = cursor.fetchall()
		if goal_id != ():
			for i in goal_id:
				details.append(i['goal_id'])
			goals = tuple(details)
			cursor.execute("""SELECT `subject_id`,`subject_name`,`content_path`,`subject_desc` FROM `subject` WHERE `subject_id` NOT IN (%s) AND `institution_id` = (%s)""",(goals,institution_id))
		else:
			cursor.execute("""SELECT `subject_id`,`subject_name`,`content_path`,`subject_desc` FROM `subject` WHERE `institution_id` = (%s)""",(institution_id))
		subjects = cursor.fetchall()

		return ({"attributes": {
    				"status_desc": "Subject Details",
    				"status": "success"
    				},
			"responseList":subjects }), status.HTTP_200_OK