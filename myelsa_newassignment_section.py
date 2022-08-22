from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from werkzeug.utils import cached_property
from database_connections import connect_elsalibrary,connect_logindb,connect_lab_lang1
import requests
import calendar
import json
from threading import Thread
import time

app = Flask(__name__)
cors = CORS(app)

myelsa_newassignment = Blueprint('myelsa_newassignment_api', __name__)
api = Api(myelsa_newassignment,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('MyelsaNewAssignment',description='Myelsa New Assignment')


mapp_assignment_section = api.model('mapp_assignment_section', {
	"assignment_id":fields.Integer(),
	"section_id":fields.Integer(),
	"module_id":fields.Integer(),
	"course_id":fields.Integer(),
	"teacher_id":fields.Integer(),
	"institution_id":fields.Integer()
	})

assignAssignment = api.model('assignAssignment', {
	"student_id":fields.Integer(),
	"assignment_id":fields.Integer()
	})

remove_mapassignment = api.model('remove_mapassignment', {
	"mapping_id":fields.Integer(),
	"section_id":fields.Integer(),
	"module_id":fields.Integer(),
	"course_id":fields.Integer()
	})

#--------------------------------------------------------#
@name_space.route("/MapAssignmentSection")
class MapAssignmentSection(Resource):
	@api.expect(mapp_assignment_section)
	def post(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()
		
		assignment_id = details.get('assignment_id')
		section_id = details.get('section_id')
		module_id = details.get('module_id')
		course_id = details.get('course_id')
		teacher_id = details.get('teacher_id')
		institution_id = details.get('institution_id')
    

		mapp_query = ("""INSERT INTO `course_assignment_mapping`(`assignment_id`,
			`section_id`,`module_id`,`course_id`,`teacher_id`,`institution_id`) 
			VALUES (%s,%s,%s,%s,%s,%s)""")

		mapp_data = cursor.execute(mapp_query,(assignment_id,section_id,
			module_id,course_id,teacher_id,institution_id))

		if mapp_data:
			msg = "Mapped"
			
		else:
			msg = "Not Mapped"

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Mapp Assignment Section",
                                "status": "success",
                                "msg": msg
                                },
	             "responseList": details}), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/AssignmentListBySectionId/<int:section_id>/<int:student_id>")
class AssignmentListBySectionId(Resource):
	def get(self,section_id,student_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		conn = connect_lab_lang1()
		cur = conn.cursor()

		cursor.execute("""SELECT `assignment_id`,`last_update_ts` FROM `course_assignment_mapping` WHERE `section_id`=%s""",(section_id))

		assignmentdata = cursor.fetchall()
		if assignmentdata == ():
			assignmentdata = []
		else:
			for aid in assignmentdata:
				aid['last_update_ts'] = aid['last_update_ts'].isoformat()

				assignment_id = aid['assignment_id']
				cur.execute("""SELECT `Title` FROM `assignment` where `Assignment_ID`=%s""",(assignment_id))

				assignmentDtls = cur.fetchone()
				if assignmentDtls:
					aid['assignmen_title'] = assignmentDtls['Title']
				else:
					aid['assignmen_title'] = ""

				cur.execute("""SELECT `Mapping_ID`,`Content_ID`,`File_Path`,`File_type` FROM `assignment_file_mapping` WHERE `Assignment_ID`=%s""",(assignment_id))

				tea_filesdtls = cur.fetchall()

				if tea_filesdtls:
					aid['Teacher_Files'] = tea_filesdtls
				else:
					aid['Teacher_Files'] =[]

				cur.execute("""SELECT `Student_Activity_Id`,`Content_Path`,`Content_Type` FROM `activity_assignment_mapping` WHERE `Student_Id`=%s and `Assignment_ID`=%s order by `Student_Activity_Id` Desc""",(student_id,assignment_id))

				stu_filesdtls = cur.fetchall()

				if stu_filesdtls:
					aid['Student_Files'] = stu_filesdtls
				else:
					aid['Student_Files'] =[]

				cur.execute("""SELECT `Remarks`, `Result` FROM `assigment_result` WHERE `Assignment_ID` = %s AND `Student_ID` = %s""",(assignment_id,student_id))

				resultdata = cur.fetchone()

				if resultdata:
					aid['result'] = resultdata['Result']
					aid['result_ramarks'] = resultdata['Remarks']
				else:
					aid['result'] = 0
					aid['result_ramarks'] = ""

				cur.execute("""SELECT `Status` FROM `assignment_mapping` WHERE `Assignment_ID` = %s AND `Student_UserID` = %s""",(assignment_id,student_id))

				statusdata = cur.fetchone()
				print(statusdata)
				if statusdata:
					aid['status'] = statusdata['Status']
				else:
					aid['status'] = ""
		cursor.close()

		return ({"attributes": {
    				"status_desc": "Section Wise Assignment Details",
    				"status": "success"
    				},
			"responseList":assignmentdata }), status.HTTP_200_OK

#--------------------------------------------------------#

@name_space.route("/GetAssignmentTitlesByTeacherId/<int:teacher_id>")
class GetAssignmentTitlesByTeacherId(Resource):
	def get(self, teacher_id):
		conn = connect_lab_lang1()
		cur = conn.cursor()

		cur.execute("""SELECT `Assignment_ID`,`Title`,`Last_Update_TS` FROM `assignment` WHERE `Teacher_ID` = %s""",(teacher_id))
		
		assignmentdata = cur.fetchall()

		for x in assignmentdata:
			x['Last_Update_TS'] = x['Last_Update_TS'].isoformat()

		cur.close()

		return ({"attributes": {
    				"status_desc": "Assignment Titles",
    				"status": "success"
    				},
			"responseList":assignmentdata }), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/AssignAssignment")
class AssignAssignment(Resource):
	@api.expect(assignAssignment)
	def post(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		conn = connect_lab_lang1()
		cur = conn.cursor()

		details = request.get_json()

		student_id = details['student_id']
		assignment_id = details['assignment_id']

		cur.execute("""SELECT `ID` FROM `assignment_mapping` where 
			`Assignment_ID`=%s and `Student_UserID`=%s""",(assignment_id,student_id))
	
		checkassignmentdata = cur.fetchone()
		
		if checkassignmentdata == None:
			assignmentQuery = ("""INSERT INTO `assignment_mapping`(`Assignment_ID`, 
				`Student_UserID`, `Status`, `DUE_DATE`) VALUES (%s,%s,%s,%s)""")
			assignStudentData = cur.execute(assignmentQuery,(assignment_id,student_id,'w',None))
			
			if assignStudentData:
				msg = "Assigned"
			else:
				msg = "Not Assigned"
		else:
			msg = "Already Assigned"

		conn.commit()
		cur.close()
		connection.commit()
		cursor.close()

		return ({"attributes": {
    				"status_desc": "Assign Assignment Details",
    				"status": "success",
    				"msg": msg
    				},
			"responseList":details }), status.HTTP_200_OK


#--------------------------------------------------------#
@name_space.route("/GetAllDueAssignmentByTeacherId/<int:teacher_id>")
class GetAllDueAssignmentByTeacherId(Resource):
	def get(self,teacher_id):
		connection = connect_logindb()
		cursor = connection.cursor()
		conn = connect_lab_lang1()
		cur = conn.cursor()
		

		cur.execute("""SELECT DISTINCT a.`Assignment_ID`,
			`Assignment_Type`,`Title` FROM `assignment` a 
			INNER JOIN `assignment_mapping` am on a.`Assignment_ID`=am.`Assignment_ID` 
			WHERE a.`Teacher_ID`=%s and am.`Status`='w'""",(teacher_id))
		
		assignmentdata = cur.fetchall()
		if assignmentdata != ():
			for aid in assignmentdata:
				cur.execute("""SELECT distinct`Student_UserID`,`Status`,`DUE_DATE` 
					FROM `assignment_mapping` WHERE `Assignment_ID`=%s order by Student_UserID asc""",(aid['Assignment_ID']))
				studentdata = cur.fetchall()

				for sid in studentdata:
					aid['studentList'] = studentdata
					if sid['DUE_DATE'] == '0000-00-00 00:00:00' or sid['DUE_DATE'] == None:
						sid['DUE_DATE'] = '0000-00-00 00:00:00'
					else:
						sid['DUE_DATE'] = sid['DUE_DATE'].isoformat()
			        
					cursor.execute("""SELECT `STUDENT_NAME`,`Board`,`CLASS` 
						FROM `student_dtls` WHERE `INSTITUTION_USER_ID_STUDENT`=%s""",(sid['Student_UserID']))
					studentdtls = cursor.fetchone()
					if studentdtls:
						sid['STUDENT_NAME'] = studentdtls['STUDENT_NAME']
						sid['Board'] = studentdtls['Board']
						sid['CLASS'] = studentdtls['CLASS']
					else:
						sid['STUDENT_NAME'] = ""
						sid['Board'] = ""
						sid['CLASS'] = ""
		
		cursor.close()
		cur.close()

		return ({"attributes": {
    				"status_desc": "Due Assignment Details",
    				"status": "success"
    				},
			"responseList":assignmentdata }), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/RemoveAssignmentMapping")
class RemoveAssignmentMapping(Resource):
	@api.expect(remove_mapassignment)
	def put(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()

		mapping_id = details.get('mapping_id')
		Module_id = details.get('module_id')
		Section_id = details.get('section_id')
		Course_id = details.get('course_id')


		cursor.execute("""SELECT `section_id`,`module_id`,`course_id` 
			FROM `course_assignment_mapping` where `mapping_id`=%s""",(mapping_id))
		mappingdtls = cursor.fetchone()

		if not Module_id and Module_id !=0:
			Module_id = mappingdtls.get("module_id")

		if not Section_id and Section_id !=0:
			Section_id = mappingdtls.get("section_id")

		if not Course_id and Course_id !=0:
			Course_id = mappingdtls.get("course_id")

		update_query = ("""UPDATE `course_assignment_mapping` SET `section_id`=%s,
			`module_id`=%s,`course_id`=%s WHERE `mapping_id`=%s""")
		
		updatedata = cursor.execute(update_query,(Section_id,Module_id,
			Course_id,mapping_id))

		if updatedata:
			msg = "Removed"
		else:
			msg = "Unremoved"

		cursor.execute("""SELECT `section_id`,`module_id`,`course_id` 
			FROM `course_assignment_mapping` where `mapping_id`=%s""",(mapping_id))
		mappingdtl = cursor.fetchone()
		
		if mappingdtl['section_id'] == 0 and mappingdtl['module_id'] ==0 and mappingdtl['course_id'] == 0:
			
			delete_query = ("""DELETE FROM `course_assignment_mapping` WHERE `mapping_id`=%s""")
			delData = (mapping_id)
			cursor.execute(delete_query,delData)

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Remove Assignment Mapping",
								"status": "success"},
				"responseList": msg}), status.HTTP_200_OK

#----------------------------------------------------------#
@name_space.route("/AssignmentListBySectionIdTeacherId/<int:section_id>/<int:teacher_id>")
class AssignmentListBySectionIdTeacherId(Resource):
	def get(self,section_id,teacher_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		conn = connect_lab_lang1()
		cur = conn.cursor()

		cursor.execute("""SELECT `assignment_id`,`last_update_ts` FROM 
			`course_assignment_mapping` WHERE `section_id`=%s and 
			teacher_id=%s""",(section_id,teacher_id))

		assignmentdata = cursor.fetchall()
		if assignmentdata == ():
			assignmentdata = []
		else:
			for aid in assignmentdata:
				aid['last_update_ts'] = aid['last_update_ts'].isoformat()

				assignment_id = aid['assignment_id']
				cur.execute("""SELECT `Title` FROM `assignment` where 
					`Assignment_ID`=%s""",(assignment_id))

				assignmentDtls = cur.fetchone()
				if assignmentDtls:
					aid['assignmen_title'] = assignmentDtls['Title']
				else:
					aid['assignmen_title'] = ""

				cur.execute("""SELECT `Mapping_ID`,`Content_ID`,`File_Path`,
					`File_type` FROM `assignment_file_mapping` WHERE `Assignment_ID`=%s""",(assignment_id))

				tea_filesdtls = cur.fetchall()

				if tea_filesdtls:
					aid['Teacher_Files'] = tea_filesdtls
				else:
					aid['Teacher_Files'] =[]

				cur.execute("""SELECT distinct`Student_UserID` FROM `assignment_mapping` WHERE 
					`Assignment_ID`=%s""",(assignment_id))

				studentdata = cur.fetchall()

				for sid,stud in enumerate(studentdata):

					cur.execute("""SELECT `Student_Activity_Id`,`Content_Path`,
						`Content_Type` FROM `activity_assignment_mapping` WHERE 
						`Student_Id`=%s and `Assignment_ID`=%s order by 
						`Student_Activity_Id` Desc""",(stud.get('Student_UserID'),assignment_id))

					stu_filesdtls = cur.fetchall()

					if stu_filesdtls:
						studentdata[sid]['Student_Files'] = stu_filesdtls
						aid['Student_Dtls'] = studentdata
					else:
						studentdata[sid]['Student_Files'] = []
						aid['Student_Dtls'] = studentdata

					cur.execute("""SELECT distinct Student_UserID,Remarks,`Result`,`Status` FROM `assignment_mapping` am 
						Left join `assigment_result` ar on am.`Student_UserID`=ar.`Student_ID` 
						WHERE am.`Student_UserID`=%s and am.`Assignment_ID`=%s""",
						(stud.get('Student_UserID'),assignment_id))

					resultdata = cur.fetchone()

					if resultdata['Result'] != None or resultdata['Remarks'] != None:
						studentdata[sid]['result'] = resultdata['Result']
						studentdata[sid]['result_ramarks'] = resultdata['Remarks']
						studentdata[sid]['status'] = resultdata['Status']
					else:
						studentdata[sid]['result'] = 0
						studentdata[sid]['result_ramarks'] = ""
						studentdata[sid]['status'] = "w"
	
		cur.close()
		cursor.close()

		return ({"attributes": {
    				"status_desc": "Assignment Details",
    				"status": "success"
    				},
			"responseList":assignmentdata }), status.HTTP_200_OK