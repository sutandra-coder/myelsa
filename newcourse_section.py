from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from werkzeug.utils import cached_property
from database_connections import connect_elsalibrary,connect_logindb
import requests
import calendar
import json
from threading import Thread
import time
from database_connections import connect_logindb

app = Flask(__name__)
cors = CORS(app)

newcourse_section = Blueprint('newcourse_section_api', __name__)
api = Api(newcourse_section,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('MyelsaNewCourse',description='Myelsa New Course')

#---------------------------------------------------------#
update_subject = api.model('update_subject',{
	"subject_name":fields.String(),
	"subject_id":fields.Integer()
	})

update_section = api.model('update_section',{
	"section_id":fields.Integer(),
	"module_id":fields.Integer(),
	"course_id":fields.Integer(),
	"section_name":fields.String(),
	"section_desc":fields.String(),
	"content_path":fields.String()
	})

update_module = api.model('update_module',{
	"module_id":fields.Integer(),
	"course_id":fields.Integer(),
	"module_name":fields.String(),
	"module_desc":fields.String(),
	"content_path":fields.String()
	})

update_coursecontent = api.model('update_coursecontent',{
	"coursecontent_id":fields.Integer(),
	"section_id":fields.Integer(),
	"module_id":fields.Integer(),
	"course_id":fields.Integer(),
	"content_name":fields.String(),
	"content_path":fields.String(),
	"content_type":fields.String(),
	"content_length":fields.String()
	})

course_track = api.model('course_track',{
	"user_id":fields.Integer(),
	"course_id":fields.Integer(),
	"institution_id":fields.Integer()
	})


#--------------------------------------------------------#
@name_space.route("/ContinueStudyingByStudentIdInstitutionId/<int:student_id>/<int:institution_id>")
class ContinueStudyingByStudentIdInstitutionId(Resource):
	def get(self,student_id,institution_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		cursor.execute("""SELECT `course_content_id`,`last_update_ts` FROM `user_course_content_tracking` 
			WHERE `user_id`=%s and `institution_id`=%s ORDER by `user_tracking_id` 
			DESC limit 5""",(student_id,institution_id))

		continueContentdata = cursor.fetchall()
		newContinueData = []
		if continueContentdata == ():
			continueContentdata = []
		else:
			for conid in continueContentdata:
				data = {}
				data['course_content_id'] = conid['course_content_id']
				data['last_update_ts'] = conid['last_update_ts'].isoformat()
				
				cursor.execute("""SELECT `content_id`,`content_name`,`content_path`,
					`content_type`,`content_length`FROM `course_content` where 
					`content_id`=%s and `institution_id`=%s""",(conid['course_content_id'],institution_id))

				contentDtls = cursor.fetchone()
				if contentDtls:
					data['content_name'] = contentDtls['content_name']
					data['content_path'] = contentDtls['content_path']
					data['content_type'] = contentDtls['content_type']
					data['content_length'] = contentDtls['content_length']
					newContinueData.append(data)

		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Continue Studying Content Details",
	    				"status": "success"
	    				},
	    				"responseList":newContinueData }), status.HTTP_200_OK


#--------------------------------------------------------#
@name_space.route("/UpdateSubject")
class UpdateSubject(Resource):
	@api.expect(update_subject)
	def put(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()

		update_query = ("""UPDATE `subject` SET `subject_name`=%s WHERE `subject_id`=%s""")
		
		updatedata = cursor.execute(update_query,(details['subject_name'],
			details['subject_id']))

		if updatedata:
			msg = "Updated"
		else:
			msg = "Not Updated"

		connection.commit()
		cursor.close()
		
		return ({"attributes": {
	    				"status_desc": "Update Subject Details",
	    				"status": "success"
	    				},
	    				"responseList":msg}), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/UpdateSectionDetails")
class UpdateSectionDetails(Resource):
	@api.expect(update_section)
	def put(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()

		section_id = details.get('section_id')
		Module_id = details.get('module_id')
		Course_id = details.get('course_id')
		Section_name = details.get('section_name')
		Section_desc = details.get('section_desc')
		Content_path = details.get('content_path')

		cursor.execute("""SELECT `module_id`,`course_id`,`section_name`,
			`section_desc`,`content_path` FROM `section` WHERE `section_id`=%s""",(section_id))
		sectionDtls = cursor.fetchone()

		if not Module_id:
			Module_id = sectionDtls.get("module_id")
		if not Course_id:
			Course_id = sectionDtls.get("course_id")
		if not Section_name:
			Section_name = sectionDtls.get("section_name")
		if not Section_desc:
			Section_desc = sectionDtls.get("section_desc")
		if not Content_path:
			Content_path = sectionDtls.get("content_path")

		update_query = ("""UPDATE `section` SET `module_id`=%s,`course_id`=%s,
			`section_name`=%s,`section_desc`=%s,`content_path`=%s WHERE `section_id`=%s""")
		
		updatedata = cursor.execute(update_query,(Module_id,Course_id,Section_name,
			Section_desc,Content_path,section_id))

		if updatedata:
			msg = "Updated"
		else:
			msg = "Not Updated"

		connection.commit()
		cursor.close()
		
		return ({"attributes": {
	    				"status_desc": "Update Section Details",
	    				"status": "success",
	    				"msg": msg
	    				},
	    				"responseList":details}), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/UpdateModuleDetails")
class UpdateModuleDetails(Resource):
	@api.expect(update_module)
	def put(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()

		module_id = details.get('module_id')
		Course_id = details.get('course_id')
		Module_name = details.get('module_name')
		Module_desc = details.get('module_desc')
		Content_path = details.get('content_path')

		cursor.execute("""SELECT `course_id`,`module_name`,`module_desc`,`content_path`
			FROM `module` WHERE `module_id`=%s""",(module_id))
		moduleDtls = cursor.fetchone()

		if not Course_id:
			Course_id = moduleDtls.get("course_id")

		if not Module_name:
			Module_name = moduleDtls.get("module_name")

		if not Module_desc:
			Module_desc = moduleDtls.get("module_desc")

		if not Content_path:
			Content_path = moduleDtls.get("content_path")

		update_query = ("""UPDATE `module` SET `course_id`=%s,
			`module_name`=%s,`module_desc`=%s,`content_path`=%s 
			WHERE `module_id`=%s""")
		
		updatedata = cursor.execute(update_query,(Course_id,Module_name,
			Module_desc,Content_path,module_id))

		if updatedata:
			msg = "Updated"
		else:
			msg = "Not Updated"

		connection.commit()
		cursor.close()
		
		return ({"attributes": {
	    				"status_desc": "Update Module Details",
	    				"status": "success",
	    				"msg": msg
	    				},
	    				"responseList":details}), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/UpdateCourseContentDetails")
class UpdateCourseContentDetails(Resource):
	@api.expect(update_coursecontent)
	def put(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()

		coursecontent_id = details.get('coursecontent_id')
		Module_id = details.get('module_id')
		Section_id = details.get('section_id')
		Course_id = details.get('course_id')
		Content_name = details.get('content_name')
		Content_path = details.get('content_path')
		Content_type = details.get('content_type')
		Content_length = details.get('content_length')
		
		cursor.execute("""SELECT `section_id`,`module_id`,`course_id`,`content_name`,
			`content_path`,`content_type`,`content_length` FROM `course_content` 
			WHERE `content_id`=%s""",(coursecontent_id))
		coursecontentDtls = cursor.fetchone()

		if not Module_id:
			Module_id = coursecontentDtls.get("module_id")

		if not Section_id:
			Section_id = coursecontentDtls.get("section_id")

		if not Course_id:
			Course_id = coursecontentDtls.get("course_id")

		if not Content_name:
			Content_name = coursecontentDtls.get("content_name")

		if not Content_path:
			Content_path = coursecontentDtls.get("content_path")

		if not Content_type:
			Content_type = coursecontentDtls.get("content_type")

		if not Content_length:
			Content_length = coursecontentDtls.get("content_length")

		update_query = ("""UPDATE `course_content` SET `section_id`=%s,`module_id`=%s,
			`course_id`=%s,`content_name`=%s,`content_path`=%s,`content_type`=%s,
			`content_length`=%s where `content_id`=%s""")
		
		updatedata = cursor.execute(update_query,(Section_id,Module_id,
			Course_id,Content_name,Content_path,Content_type,Content_length,coursecontent_id))

		if updatedata:
			msg = "Updated"
		else:
			msg = "Not Updated"

		connection.commit()
		cursor.close()
		
		return ({"attributes": {
	    				"status_desc": "Update Course Content Details",
	    				"status": "success",
	    				"msg": msg
	    				},
	    				"responseList":details}), status.HTTP_200_OK
#--------------------------------------------------------#
@name_space.route("/RemoveSubject/<int:subject_id>")
class RemoveSubject(Resource):
	def delete(self, subject_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		
		delete_query = ("""DELETE FROM `subject` WHERE `subject_id` = %s """)
		delData = (subject_id)
		
		cursor.execute(delete_query,delData)
		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Remove Subject",
								"status": "success"},
				"responseList": 'Removed Successfully'}), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/RemoveSection/<int:section_id>")
class RemoveSection(Resource):
	def delete(self, section_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		
		delete_query = ("""DELETE FROM `section` WHERE `section_id` = %s """)
		delData = (section_id)
		
		cursor.execute(delete_query,delData)

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Remove Section",
								"status": "success"},
				"responseList": 'Removed Successfully'}), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/RemoveModule/<int:module_id>")
class RemoveModule(Resource):
	def delete(self, module_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		
		delete_query = ("""DELETE FROM `module` WHERE `module_id` = %s """)
		delData = (module_id)
		
		cursor.execute(delete_query,delData)

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Remove Module",
								"status": "success"},
				"responseList": 'Removed Successfully'}), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/RemoveCourseContent/<int:coursecontent_id>")
class RemoveCourseContent(Resource):
	def delete(self, coursecontent_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		
		delete_query = ("""DELETE FROM `course_content` WHERE `content_id` = %s """)
		delData = (coursecontent_id)
		
		cursor.execute(delete_query,delData)

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Remove Course Content",
								"status": "success"},
				"responseList": 'Removed Successfully'}), status.HTTP_200_OK

#--------------------------------------------------------#
#--------------------------------------------------------#
@name_space.route("/getModuleSectionAndContents/<int:course_id>/<int:student_id>")
class GetModuleSectionAndContents(Resource):
	def get(self, course_id, student_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT `module_id`, `module_name` FROM `module` WHERE `course_id` = %s ORDER BY `module_id`""",(course_id))
		moduledata = cursor.fetchall()

		if moduledata == ():
			moduledata = []
		else:
			for module in moduledata:

				cursor.execute("""SELECT COUNT(`content_id`) as 'total' FROM `course_content` WHERE `module_id` = %s""",(module['module_id']))

				temp1= cursor.fetchone()
				if temp1:
					module['total_content_in_module'] = temp1['total']
				else:
					module['total_content_in_module'] = 0

				cursor.execute("""SELECT COUNT(DISTINCT(`course_content_id`)) as 'total' FROM `user_course_content_tracking`
			 	WHERE `user_id` = %s AND `module_id` = %s""",(student_id,module['module_id']))

				temp2= cursor.fetchone()
				if temp2:
					module['completed_content_in_module'] = temp2['total']
				else:
					module['completed_content_in_module'] = 0

				cursor.execute("""SELECT `section_id`, `section_name` FROM `section` WHERE `module_id` = %s""",(module['module_id']))
				sectiondata = cursor.fetchall()

				if sectiondata == ():
					module['section_list'] = []
				else:
					for section in sectiondata:
						cursor.execute("""SELECT `content_id`,`content_name`,`content_length`,
							`content_path`,`content_type` FROM `course_content` WHERE `section_id`=%s""",(section['section_id']))

						contentdata = cursor.fetchall()
						if contentdata == ():
							section['total_content_in_section'] = 0
							section['content_list'] = []
						else:
							section['total_content_in_section'] = len(contentdata)

							for content in contentdata:
								cursor.execute("""SELECT `user_tracking_id` FROM `user_course_content_tracking` WHERE 
									`course_content_id`=%s and user_id=%s""",
									(content['content_id'],student_id))
								
								completedData = cursor.fetchone()

								if completedData:
									content['completed'] = "y"
								else:
									content['completed'] = "n"


							section['content_list'] = contentdata

					module['section_list'] = sectiondata

		cursor.close()
		
		return ({"attributes": {"status_desc": "Course Details",
								"status": "success"},
				"responseList": moduledata}), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/UserCourseTracking")
class UserCourseTracking(Resource):
	@api.expect(course_track)
	def post(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()
		
		user_id = details.get('user_id')
		course_id = details.get('course_id')
		institution_id = details.get('institution_id')
		
		course_query = ("""INSERT INTO `user_course_tracking`(`user_id`,
			`course_id`,`institution_id`,`last_update_id`) VALUES(%s,%s,
			%s,%s)""")
		course_data = (user_id,course_id,institution_id,user_id)
		coursedata = cursor.execute(course_query,course_data)

		if coursedata:
			course_tracking_id = cursor.lastrowid
			details['user_tracking_id'] = course_tracking_id
			msg = "Added"
			
		else:
			msg = "Not Added"

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Course Tracking Details",
                                "status": "success",
                                "msg": msg
	                                },
	             "responseList": details}), status.HTTP_200_OK

#-----------------------------------------------------#
@name_space.route("/GetBoardsByInstitutionId/<int:institution_id>")
class GetBoardsByInstitutionId(Resource):
	def get(self,institution_id):
		connection = connect_logindb()
		cursor = connection.cursor()

		cursor.execute("""SELECT `board_id`,`board_name`,`last_update_id`,`last_update_ts` 
			FROM `institution_board_dtls` WHERE`institution_id`=%s""",(institution_id))
		boards = cursor.fetchall()

		if boards == ():
			boards = []
		else:
			for x in boards:
				x['last_update_ts'] = x['last_update_ts'].isoformat()

		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Board Details.",
	    				"status": "success"
	    				},
				"responseList":boards}), status.HTTP_200_OK

#-----------------------------------------------------#
@name_space.route("/GetClassByBoardIdInstitutionIdV2/<int:board_id>/<int:institution_id>")
class GetClassByBoardIdInstitutionIdV2(Resource):
	def get(self,board_id,institution_id):
		connection = connect_logindb()
		cursor = connection.cursor()

		cursor.execute("""SELECT * FROM `institution_class` 
			WHERE `board_id`=%s and `institution_id`=%s""",
			(board_id,institution_id))
		classList = cursor.fetchall()

		if classList == ():
			classList = []
		else:
			for x in classList:
				x['last_update_ts'] = x['last_update_ts'].isoformat()

				cursor.execute("""SELECT `board_name` FROM `institution_board_dtls` WHERE 
					`board_id`=%s""",(board_id))
				boardname = cursor.fetchone()
				if boardname:
					x['board_name'] = boardname['board_name']
				else:
					x['board_name'] = ""
		
		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Class Details.",
	    				"status": "success"
	    				},
				"responseList":classList}), status.HTTP_200_OK


#-----------------------------------------------------#

#--------------------------------------------------------#
@name_space.route("/hasSubcribedCourse/<int:student_id>/<int:course_id>")
class HasSubcribedCourse(Resource):
	def get(self,student_id,course_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		cursor.execute("""SELECT `mapping_id` FROM `student_course_master` WHERE `student_id` = %s AND `course_id` = %s""",(student_id,course_id))

		if cursor.fetchone():
			data = "subscribed"
		else:
			data = "not-subscribed"
		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Course Subcribtion status",
	    				"status": "success"
	    				},
	    				"responseList":data }), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/getSubjectNameBySubjectId/<int:subject_id>")
class GetSubjectNameBySubjectId(Resource):
	def get(self,subject_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		cursor.execute("""SELECT `subject_name` FROM `subject` WHERE `subject_id` = %s """,(subject_id))

		data = cursor.fetchone().get('subject_name')
		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Subject Name",
	    				"status": "success"
	    				},
	    				"responseList":data }), status.HTTP_200_OK

#-----------------------------------------------------#
@name_space.route("/GetCoursesWithBoardClassByInstitutionId/<int:institution_id>")
class GetCoursesWithBoardClassByInstitutionId(Resource):
	def get(self,institution_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		cursor.execute("""SELECT `course_id`,`subject_id`,`course_name`,`board`,`class`,`last_update_ts` FROM `course` 
			WHERE `institution_id` =%s and `course_status`='public'""",(institution_id))
		courseList = cursor.fetchall()

		if courseList == ():
			courseList = []
		else:
			for cid in courseList:
				cid['last_update_ts'] = cid['last_update_ts'].isoformat()

				cursor.execute("""SELECT `subject_name` FROM `subject` WHERE `subject_id`=%s""",(cid['subject_id']))
				subname = cursor.fetchone()
				if subname:
					cid['subject_name'] = subname['subject_name']
				else:
					cid['subject_name'] = ""
		
		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Courses Details.",
	    				"status": "success"
	    				},
				"responseList":courseList}), status.HTTP_200_OK

#----------------------------------------------------------------------#
@name_space.route("/GetRecommendedNonSubsribecoursesByStudentIdCategoryIdInstitutionId/<int:student_id>/<int:category_id>/<int:institution_id>")
class GetRecommendedNonSubsribecoursesByStudentIdCategoryIdInstitutionId(Resource):
	def get(self,student_id,category_id,institution_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		conn = connect_logindb()
		cur = conn.cursor()
		board = ''
		clss = ''
		if category_id == 1:
			cur.execute("""SELECT `CLASS`,`Board` FROM `student_dtls` 
			WHERE `INSTITUTION_USER_ID_STUDENT`=%s and INSTITUTION_ID=%s limit 1""",(student_id,institution_id))

			studentdata = cur.fetchone()
			if studentdata:
				board = studentdata['Board']
				clss = studentdata['CLASS']

			cursor.execute("""SELECT c.`course_id`,`subject_id`,
					`course_name`,`hours`,`course_image`,fee_id,is_paid_course,
					total_fee,installment_available, installment_type,
					no_of_installments,c.`board`,c.`class` FROM `course` c INNER join 
					`course_fee_mapping` cfm on c.`course_id`=cfm.`course_id` 
					WHERE c.`course_id` not in(SELECT `course_id` FROM 
					`student_course_master` WHERE `student_id`=%s) and 
					`institution_id`=%s and `board`=%s and `class`=%s and course_status ='public'
					order by total_fee DESC""",(student_id,institution_id,board,clss))

		else:
			cursor.execute("""SELECT c.`course_id`,`subject_id`,
				`course_name`,`hours`,`course_image`,fee_id,is_paid_course,
				total_fee,installment_available, installment_type,
				no_of_installments,c.`board`,c.`class` FROM `course` c INNER join 
				`course_fee_mapping` cfm on c.`course_id`=cfm.`course_id` 
				WHERE c.`course_id` not in(SELECT `course_id` FROM 
				`student_course_master` WHERE `student_id`=%s) and 
				`institution_id`=%s and `category_id`=%s and course_status ='public'
				order by total_fee DESC""",(student_id,institution_id,category_id))

		nonsubscribecourse = cursor.fetchall()
				
		if nonsubscribecourse == ():
			recnonsubscribecourseData = []

		else:
			for cid in range(len(nonsubscribecourse)):
				cursor.execute("""SELECT count(`content_id`)as 'total' FROM 
					`course_content` where `course_id`=%s""",(nonsubscribecourse[cid]['course_id']))

				coursecontentdata = cursor.fetchone()

				if coursecontentdata:
					content_count = coursecontentdata['total']
					nonsubscribecourse[cid]['content_count'] = content_count
				else:
					nonsubscribecourse[cid]['content_count'] = 0

				cursor.execute("""SELECT count(`module_id`)as 'total' FROM 
					`module` where `course_id`=%s""",(nonsubscribecourse[cid]['course_id']))

				moduledata = cursor.fetchone()
				if moduledata:
					module_count = moduledata['total']
					nonsubscribecourse[cid]['module_count'] = module_count
				else:
					nonsubscribecourse[cid]['module_count'] = 0
				
				cursor.execute("""SELECT count(`section_id`)as 'total' FROM 
					`section` where `course_id`=%s""",(nonsubscribecourse[cid]['course_id']))

				secdata = cursor.fetchone()
				if secdata:
					section_count = secdata['total']
					nonsubscribecourse[cid]['section_count'] = section_count
				else:
					nonsubscribecourse[cid]['section_count'] = 0 
				nonsubscribecourse[cid]['rating'] = "4.4"

				recnonsubscribecourseData = nonsubscribecourse

		cursor.close()
		cur.close()

		return ({"attributes": {
	    				"status_desc": "Recommended NonSubscribe Course Details.",
	    				"status": "success"
	    				},
				"responseList":recnonsubscribecourseData}), status.HTTP_200_OK

#-----------------------------------------------------------------#
@name_space.route("/GetSubjectByCategoryIdStudentIdInstitutionId/<int:category_id>/<int:institution_id>/<int:student_id>")
class GetSubjectByCategoryIdStudentIdInstitutionId(Resource):
	def get(self,category_id,institution_id,student_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		conn = connect_logindb()
		cur = conn.cursor()

		subList = []
		board = ''
		clss = ''
		if category_id == 1:
			cur.execute("""SELECT `CLASS`,`Board` FROM `student_dtls` 
			WHERE `INSTITUTION_USER_ID_STUDENT`=%s and INSTITUTION_ID=%s limit 1""",(student_id,institution_id))

			studentdata = cur.fetchone()
			if studentdata:
				board = studentdata['Board']
				clss = studentdata['CLASS']

				cursor.execute("""SELECT * FROM `subject` WHERE `institution_id`=%s""",
					(institution_id))

				subjectdata = cursor.fetchall()
				if subjectdata == ():
					subList = []
				else:
					for x in subjectdata:
						cursor.execute("""SELECT `course_id` FROM `course` WHERE `subject_id`=%s and 
							`institution_id`=%s and `board`=%s and `class`=%s and course_status ='public'""",
							(x['subject_id'],institution_id,board,clss))
						courseDtls = cursor.fetchall()
						if courseDtls == ():
							subjectData = []
						else:
							if len(courseDtls) != 0:

								x['subject_id'] = x['subject_id']
								x['institution_id'] = x['institution_id']
								x['subject_name'] = x['subject_name']
								x['content_path'] = x['content_path']
								x['subject_desc'] = x['subject_desc']
								x['totalcourse'] = len(courseDtls) 
								x['last_update_id'] = x['last_update_id']
								x['last_update_ts'] = x['last_update_ts'].isoformat()
								
								subList.append(x)
							else:
								subList = []
		else:
			
			cursor.execute("""SELECT * FROM `subject` WHERE `institution_id`=%s 
				and category_id=%s""",(institution_id,category_id))

			subjectdata = cursor.fetchall()
			if subjectdata == ():
				subList = []

			else:
				for x in subjectdata:
					cursor.execute("""SELECT `course_id` FROM `course` WHERE `subject_id`=%s and 
						`institution_id`=%s and `category_id`=%s and course_status ='public'""",
						(x['subject_id'],institution_id,category_id))
					courseDtls = cursor.fetchall()
					if courseDtls == ():
						subjectData = []
					else:
						if len(courseDtls) != 0:

							x['subject_id'] = x['subject_id']
							x['institution_id'] = x['institution_id']
							x['subject_name'] = x['subject_name']
							x['content_path'] = x['content_path']
							x['subject_desc'] = x['subject_desc']
							x['totalcourse'] = len(courseDtls) 
							x['last_update_id'] = x['last_update_id']
							x['last_update_ts'] = x['last_update_ts'].isoformat()
							
							subList.append(x)
						else:
							subList = []

		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Subject Details.",
	    				"status": "success"
	    				},
	    				"responseList":subList}), status.HTTP_200_OK

@name_space.route("/CourseListByUserIdAndInstitutionId/<int:user_id>/<int:institution_id>")
class CourseListByUserIdAndInstitutionId(Resource):
	def get(self,user_id,institution_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		details=[]
		detail=[]
		goals=()
		recommendedcourselist=[]
		not_recommendedcourselist = []

		cursor.execute("""SELECT `goal_id` FROM `user_goal_tracking` WHERE `user_id`=%s AND `institution_id`=%s""",(user_id,institution_id))
		goal_id = cursor.fetchall()
		
		for i in goal_id:
			details.append(i['goal_id'])
		goals = tuple(details)

		if len(goals)==1:

			cursor.execute("""SELECT `course`.`course_id`,`course`.`subject_id`,`course`.`course_name`,`course`.`hours`,`course`.`course_image`,`course`.`course_video`,`course`.`course_desc`,`course_fee_mapping`.`fee_id`,`course_fee_mapping`.`is_paid_course`,`course_fee_mapping`.`total_fee`,`course_fee_mapping`.`installment_available`,`course_fee_mapping`.`installment_type`,`course_fee_mapping`.`no_of_installments`,`subject`.`subject_id` FROM `course` INNER JOIN `course_fee_mapping` ON `course`.`course_id` = `course_fee_mapping`.`course_id` INNER JOIN `subject` ON `course`.`subject_id` = `subject`.`subject_id` WHERE `course`.`subject_id` IN (SELECT `goal_id` FROM `user_goal_tracking` WHERE `user_id` = (%s)) AND `course`.`institution_id`= %s""",(user_id,institution_id))
			recommendedcourselist = cursor.fetchall()

			if recommendedcourselist == ():
				recommendedcourselist = []

			else:
				for cid in range(len(recommendedcourselist)):

					cursor.execute("""SELECT count(`content_id`)as 'total' FROM 
						`course_content` where `course_id`=%s""",(recommendedcourselist[cid]['course_id']))

					coursecontentdata = cursor.fetchone()

					if coursecontentdata:
						content_count = coursecontentdata['total']
						recommendedcourselist[cid]['content_count'] = content_count
					else:
						recommendedcourselist[cid]['content_count'] = 0

					cursor.execute("""SELECT count(`module_id`)as 'total' FROM 
						`module` where `course_id`=%s""",(recommendedcourselist[cid]['course_id']))

					moduledata = cursor.fetchone()
					if moduledata:
						module_count = moduledata['total']
						recommendedcourselist[cid]['module_count'] = module_count
					else:
						recommendedcourselist[cid]['module_count'] = 0

					cursor.execute("""SELECT count(`section_id`)as 'total' FROM 
						`section` where `course_id`=%s""",(recommendedcourselist[cid]['course_id']))

					secdata = cursor.fetchone()
					if secdata:
						section_count = secdata['total']
						recommendedcourselist[cid]['section_count'] = section_count
					else:
						recommendedcourselist[cid]['section_count'] = 0

					recommendedcourselist[cid]['rating'] = "4.4"

					recommendedcourselist = recommendedcourselist
			

			cursor.execute("""SELECT `course`.`course_id`,`course`.`subject_id`,`course`.`course_name`,`course`.`hours`,`course`.`course_image`,`course`.`course_video`,`course`.`course_desc`,`course_fee_mapping`.`fee_id`,`course_fee_mapping`.`is_paid_course`,`course_fee_mapping`.`total_fee`,`course_fee_mapping`.`installment_available`,`course_fee_mapping`.`installment_type`,`course_fee_mapping`.`no_of_installments`,`subject`.`subject_name` FROM `course` INNER JOIN `course_fee_mapping` ON `course`.`course_id` = `course_fee_mapping`.`course_id` INNER JOIN `subject` ON `course`.`subject_id` = `subject`.`subject_id` WHERE `course`.`subject_id` NOT IN (%s) AND `course`.`institution_id`= %s""",(goals,institution_id))
			not_recommendedcourselist = cursor.fetchall()

			if not_recommendedcourselist == ():
				not_recommendedcourselist = []

			else:
				for cid in range(len(not_recommendedcourselist)):

					cursor.execute("""SELECT count(`content_id`)as 'total' FROM 
						`course_content` where `course_id`=%s""",(not_recommendedcourselist[cid]['course_id']))

					coursecontentdata = cursor.fetchone()

					if coursecontentdata:
						content_count = coursecontentdata['total']
						not_recommendedcourselist[cid]['content_count'] = content_count
					else:
						not_recommendedcourselist[cid]['content_count'] = 0

					cursor.execute("""SELECT count(`module_id`)as 'total' FROM 
						`module` where `course_id`=%s""",(not_recommendedcourselist[cid]['course_id']))

					moduledata = cursor.fetchone()
					if moduledata:
						module_count = moduledata['total']
						not_recommendedcourselist[cid]['module_count'] = module_count
					else:
						not_recommendedcourselist[cid]['module_count'] = 0

					cursor.execute("""SELECT count(`section_id`)as 'total' FROM 
						`section` where `course_id`=%s""",(not_recommendedcourselist[cid]['course_id']))

					secdata = cursor.fetchone()
					if secdata:
						section_count = secdata['total']
						not_recommendedcourselist[cid]['section_count'] = section_count
					else:
						not_recommendedcourselist[cid]['section_count'] = 0

					not_recommendedcourselist[cid]['rating'] = "4.4"

					not_recommendedcourselist = not_recommendedcourselist
			

			cursor.close()
			if len(recommendedcourselist)==0:
				return ({"attributes": {"status_desc": "Course List",
	                            "status": "success"
	                           },
	           
	             "responseList": not_recommendedcourselist}), status.HTTP_200_OK
			if len(recommendedcourselist)!=0:
				for i in not_recommendedcourselist:
					recommendedcourselist.append(i)
				return ({"attributes": {"status_desc": "Course List",
	                            "status": "success"
	                           },
	            
	             "responseList": recommendedcourselist}), status.HTTP_200_OK

		elif len(goals)>1:
			cursor.execute("""SELECT `course`.`course_id`,`course`.`subject_id`,`course`.`course_name`,`course`.`hours`,`course`.`course_image`,`course`.`course_video`,`course`.`course_desc`,`course_fee_mapping`.`fee_id`,`course_fee_mapping`.`is_paid_course`,`course_fee_mapping`.`total_fee`,`course_fee_mapping`.`installment_available`,`course_fee_mapping`.`installment_type`,`course_fee_mapping`.`no_of_installments`,`subject`.`subject_name` FROM `course` INNER JOIN `course_fee_mapping` ON `course`.`course_id` = `course_fee_mapping`.`course_id` INNER JOIN `subject` ON `course`.`subject_id` = `subject`.`subject_id` WHERE `course`.`subject_id` IN (SELECT `goal_id` FROM `user_goal_tracking` WHERE `user_id`=(%s)) AND `course`.`institution_id`=%s """,(user_id,institution_id))
			recommendedcourselist = cursor.fetchall()

			if recommendedcourselist == ():
				recommendedcourselist = []

			else:
				for cid in range(len(recommendedcourselist)):

					cursor.execute("""SELECT count(`content_id`)as 'total' FROM 
						`course_content` where `course_id`=%s""",(recommendedcourselist[cid]['course_id']))

					coursecontentdata = cursor.fetchone()

					if coursecontentdata:
						content_count = coursecontentdata['total']
						recommendedcourselist[cid]['content_count'] = content_count
					else:
						recommendedcourselist[cid]['content_count'] = 0

					cursor.execute("""SELECT count(`module_id`)as 'total' FROM 
						`module` where `course_id`=%s""",(recommendedcourselist[cid]['course_id']))

					moduledata = cursor.fetchone()
					if moduledata:
						module_count = moduledata['total']
						recommendedcourselist[cid]['module_count'] = module_count
					else:
						recommendedcourselist[cid]['module_count'] = 0

					cursor.execute("""SELECT count(`section_id`)as 'total' FROM 
						`section` where `course_id`=%s""",(recommendedcourselist[cid]['course_id']))

					secdata = cursor.fetchone()
					if secdata:
						section_count = secdata['total']
						recommendedcourselist[cid]['section_count'] = section_count
					else:
						recommendedcourselist[cid]['section_count'] = 0

					recommendedcourselist[cid]['rating'] = "4.4"

					recommendedcourselist = recommendedcourselist

			

			cursor.execute("""SELECT `course`.`course_id`,`course`.`subject_id`,`course`.`course_name`,`course`.`hours`,`course`.`course_image`,`course`.`course_video`,`course`.`course_desc`,`course_fee_mapping`.`fee_id`,`course_fee_mapping`.`is_paid_course`,`course_fee_mapping`.`total_fee`,`course_fee_mapping`.`installment_available`,`course_fee_mapping`.`installment_type`,`course_fee_mapping`.`no_of_installments`,`subject`.`subject_name` FROM `course` INNER JOIN `course_fee_mapping` ON `course`.`course_id` = `course_fee_mapping`.`course_id` INNER JOIN `subject` ON `course`.`subject_id` = `subject`.`subject_id` WHERE `course`.`subject_id` NOT IN {} AND `course`.`institution_id`= %s""".format(goals),(institution_id))
			not_recommendedcourselist = cursor.fetchall()

			if not_recommendedcourselist == ():
				not_recommendedcourselist = []

			else:
				for cid in range(len(not_recommendedcourselist)):

					cursor.execute("""SELECT count(`content_id`)as 'total' FROM 
						`course_content` where `course_id`=%s""",(not_recommendedcourselist[cid]['course_id']))

					coursecontentdata = cursor.fetchone()

					if coursecontentdata:
						content_count = coursecontentdata['total']
						not_recommendedcourselist[cid]['content_count'] = content_count
					else:
						not_recommendedcourselist[cid]['content_count'] = 0

					cursor.execute("""SELECT count(`module_id`)as 'total' FROM 
						`module` where `course_id`=%s""",(not_recommendedcourselist[cid]['course_id']))

					moduledata = cursor.fetchone()
					if moduledata:
						module_count = moduledata['total']
						not_recommendedcourselist[cid]['module_count'] = module_count
					else:
						not_recommendedcourselist[cid]['module_count'] = 0

					cursor.execute("""SELECT count(`section_id`)as 'total' FROM 
						`section` where `course_id`=%s""",(not_recommendedcourselist[cid]['course_id']))

					secdata = cursor.fetchone()
					if secdata:
						section_count = secdata['total']
						not_recommendedcourselist[cid]['section_count'] = section_count
					else:
						not_recommendedcourselist[cid]['section_count'] = 0

					not_recommendedcourselist[cid]['rating'] = "4.4"

					not_recommendedcourselist = not_recommendedcourselist

			

			for i in not_recommendedcourselist:
				recommendedcourselist.append(i)

			cursor.close()

			return ({"attributes": {"status_desc": "Course List",
	                            "status": "success"
	                           },

	            
	             "responseList": recommendedcourselist}), status.HTTP_200_OK

		elif len(goals)==0:
			recommendedcourselist = []
			

			cursor.execute("""SELECT `course`.`course_id`,`course`.`subject_id`,`course`.`course_name`,`course`.`hours`,`course`.`course_image`,`course`.`course_video`,`course`.`course_desc`,`course_fee_mapping`.`fee_id`,`course_fee_mapping`.`is_paid_course`,`course_fee_mapping`.`total_fee`,`course_fee_mapping`.`installment_available`,`course_fee_mapping`.`installment_type`,`course_fee_mapping`.`no_of_installments`,`subject`.`subject_name` FROM `course` INNER JOIN `course_fee_mapping` ON `course`.`course_id` = `course_fee_mapping`.`course_id` INNER JOIN `subject` ON `course`.`subject_id` = `subject`.`subject_id` WHERE `course`.`institution_id`= %s""",(institution_id))
			not_recommendedcourselist = cursor.fetchall()

			if not_recommendedcourselist == ():
				not_recommendedcourselist = []

			else:
				for cid in range(len(not_recommendedcourselist)):

					cursor.execute("""SELECT count(`content_id`)as 'total' FROM 
						`course_content` where `course_id`=%s""",(not_recommendedcourselist[cid]['course_id']))

					coursecontentdata = cursor.fetchone()

					if coursecontentdata:
						content_count = coursecontentdata['total']
						not_recommendedcourselist[cid]['content_count'] = content_count
					else:
						not_recommendedcourselist[cid]['content_count'] = 0

					cursor.execute("""SELECT count(`module_id`)as 'total' FROM 
						`module` where `course_id`=%s""",(not_recommendedcourselist[cid]['course_id']))

					moduledata = cursor.fetchone()
					if moduledata:
						module_count = moduledata['total']
						not_recommendedcourselist[cid]['module_count'] = module_count
					else:
						not_recommendedcourselist[cid]['module_count'] = 0

					cursor.execute("""SELECT count(`section_id`)as 'total' FROM 
						`section` where `course_id`=%s""",(not_recommendedcourselist[cid]['course_id']))

					secdata = cursor.fetchone()
					if secdata:
						section_count = secdata['total']
						not_recommendedcourselist[cid]['section_count'] = section_count
					else:
						not_recommendedcourselist[cid]['section_count'] = 0

					not_recommendedcourselist[cid]['rating'] = "4.4"

					not_recommendedcourselist = not_recommendedcourselist

			cursor.close()

			

			return ({"attributes": {"status_desc": "Course List",
	                            "status": "success"},
	                         
	             "responseList": not_recommendedcourselist}), status.HTTP_200_OK