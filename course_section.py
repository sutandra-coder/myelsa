from flask import Flask, request, jsonify, json
from flask_api import status
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests
import json

app = Flask(__name__)
cors = CORS(app)


'''def connect_userlib():
	connection = pymysql.connect(host='creamsonservices.com',
									user='creamson_langlab',
									password='Langlab@123',
									db='creamson_user_library',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor)
	return connection

def connect_logindb():
	connection = pymysql.connect(host='creamsonservices.com',
								user='creamson_langlab',
								password='Langlab@123',
								db='creamson_logindb',
								charset='utf8mb4',
								cursorclass=pymysql.cursors.DictCursor)
	return connection'''

def connect_userlib():
	connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
									user='admin',
									password='cbdHoRPQPRfTdC0uSPLt',
									db='creamson_user_library',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor)
	return connection

def connect_logindb():
	connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
								user='admin',
								password='cbdHoRPQPRfTdC0uSPLt',
								db='creamson_logindb',
								charset='utf8mb4',
								cursorclass=pymysql.cursors.DictCursor)
	return connection


# BASE_URL = "http://127.0.0.1:5000/"
BASE_URL = "http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/"

course_section = Blueprint('course_section_api', __name__)
api = Api(course_section,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('MyelsaCourse',description='Myelsa Course')


create_folder_model = api.model('create_folder_model', {
	"institution_id":fields.Integer(),
	"teacher_id":fields.Integer(),
	"parent_folder_id":fields.Integer(),
	"folder_name":fields.String(),
	"root_folder_id":fields.Integer(),
	})

create_course_combo = api.model('create_course_combo_model', {
	"institution_id":fields.Integer(),
	"teacher_id":fields.Integer(),
	"combo_type":fields.Integer(),
	"combo_name":fields.String(),
	"combo_desc":fields.String(),
	"combo_image_url":fields.String(),
	"no_of_courses":fields.Integer(),
	"combo_amount":fields.String(),
	})


@name_space.route("/createFolder")
class createFolder(Resource):
	@api.expect(create_folder_model)
	def post(self):

		connection = connect_userlib()
		cursor = connection.cursor()
		
		details = request.get_json()

		teacherId = details.get('teacher_id')
		courseId = details.get('course_id')
		institutionId = details.get('institution_id')
		parentFolderId = details.get('parent_folder_id',0)
		folderName = details.get('folder_name')
		rootFolderId = details.get('root_folder_id',0)

		if parentFolderId == 0:
			depth = 0
		else:
			cursor.execute("""SELECT `depth` FROM `folder_depth_mapping` WHERE `folder_id` = %s""",(parentFolderId))
			depthDtls = cursor.fetchone()
			depth = depthDtls.get('depth') + 1



		folderInsertQuery = ("""INSERT INTO `folder_depth_mapping`(`root_folder_id`,`parent_folder_id`, `folder_name`, 
			`depth`, `teacher_id`, `institution_id`) VALUES (%s,%s,%s,%s,%s,%s)""")

		folderData = (rootFolderId,parentFolderId,folderName,depth,teacherId,institutionId)

		cursor.execute(folderInsertQuery,folderData)

		folderId = cursor.lastrowid

		details['folderId'] = folderId

		if rootFolderId == 0:

			updateRootFolder = ("""UPDATE `folder_depth_mapping` SET `root_folder_id` = %s 
				WHERE `folder_id` = %s""")

			rootData = (folderId,folderId)

			cursor.execute(updateRootFolder,rootData)

			details['root_folder_id'] = folderId

		return details


@name_space.route("/getFolderByTeacherId/<int:teacher_id>/<int:institution_id>")
class getFolderByTeacherId(Resource):
	def get(self,teacher_id,institution_id):

		connection = connect_userlib()
		cursor = connection.cursor()
		has_subFolder = 0
		has_course = 0
		cursor.execute("""SELECT `folder_id`,`root_folder_id`,`parent_folder_id`,`folder_name`,depth 
			FROM `folder_depth_mapping` WHERE `teacher_id` = %s and `institution_id` = %s 
			and `depth` = 0""",(teacher_id,institution_id))

		mainFolderDtls = cursor.fetchall()

		for fid, fold in enumerate(mainFolderDtls):
			subFolderURL = BASE_URL + "course_section/MyelsaCourse/getSubFolderDtlsByRootFolderId/{}/{}/{}".format(teacher_id,institution_id,fold.get('root_folder_id'))
			subFolderRes = requests.get(subFolderURL).json()
			fold['subFolderDtls'] = subFolderRes
			cursor.execute("""SELECT icm.`course_id`, `course_title`, `course_description`, `course_image`, 
				`course_filetype`, `is_paid_course`,`total_fee`,`installment_available`,`installment_type`,
				`no_of_installments`,`teacher_id`, icm.`subject_id`,`subject_name`,icm.`topic_id`,
				`topic_name` FROM `instituition_course_master` icm INNER JOIN `subject` 
				on icm.`subject_id` = `subject`.`subject_id` INNER JOIN `topic` 
				on icm.`topic_id` = `topic`.`topic_id` LEFT JOIN `course_fee_mapping` cfm 
				ON icm.`course_id` = cfm.`course_id` WHERE  icm.`course_id` 
				in (SELECT `course_id` FROM `course_folder_mapping` 
				WHERE `folder_id` = %s and `teacher_id` = %s 
				AND `Institution_ID` = %s)""",(fold.get('folder_id'),teacher_id,institution_id))
			courseDtls = cursor.fetchall()
			if courseDtls:
				fold['courseDtls'] = courseDtls
			else:
				fold['courseDtls'] = courseDtls = []

		return ({"attributes": {"status_desc": "Folder Details.",
								"status": "success"},
				"responseList":mainFolderDtls}), status.HTTP_200_OK

		# ("""SELECT GROUP_CONCAT(`folder_name` SEPARATOR '/'), GROUP_CONCAT(`folder_id` SEPARATOR '/') 
		# 	FROM `folder_depth_mapping` WHERE `teacher_id` = %s and `institution_id` = %s 
		# 	and `root_folder_id` = %s""")


@name_space.route("/getSubFolderDtlsByRootFolderId/<int:teacher_id>/<int:institution_id>/<int:root_folder_id>")
class getSubFolderDtlsByRootFolderId(Resource):
	def get(self,teacher_id,institution_id,root_folder_id):

		connection = connect_userlib()
		cursor = connection.cursor()

		# cursor.execute("""SELECT GROUP_CONCAT(`folder_name` SEPARATOR '/') as 'folder_structure', 
		# 	GROUP_CONCAT(`folder_id` SEPARATOR '/') as 'folder_id_structure', 
		# 	GROUP_CONCAT(`parent_folder_id` SEPARATOR '/') as 'parent_folder_id_structure',
		# 	GROUP_CONCAT(`depth` SEPARATOR '/') as 'depth_structure' 
		# 	FROM `folder_depth_mapping` WHERE `teacher_id` = %s and `institution_id` = %s 
		# 	and `root_folder_id` = %s and depth <> 0""",(teacher_id,institution_id,root_folder_id))

		# mainFolderDtls = cursor.fetchone()

		cursor.execute("""SELECT `folder_id`,`root_folder_id`,`parent_folder_id`,`folder_name`,`depth`,
			`teacher_id`,`institution_id` FROM `folder_depth_mapping` WHERE `institution_id` = %s 
			AND `root_folder_id` = %s AND depth <> 0 ORDER by `parent_folder_id`""",(institution_id,root_folder_id))
		mainFolderDtls = cursor.fetchall()
		if not mainFolderDtls:
			mainFolderDtls = []
		cursor.close()
		return mainFolderDtls

		# return ({"attributes": {"status_desc": "Folder Details.",
		# 						"status": "success"},
		# 		"responseList":mainFolderDtls}), status.HTTP_200_OK



@name_space.route("/getSubFolderDtlsByFolderId/<int:teacher_id>/<int:institution_id>/<int:folder_id>")
class getSubFolderDtlsByFolderId(Resource):
	def get(self,teacher_id,institution_id,folder_id):

		connection = connect_userlib()
		cursor = connection.cursor()
		isFolder = 0
		isCourse = 0
		isCourseOrFolder = 0
		cursor.execute("""SELECT `folder_id`,`root_folder_id`,`parent_folder_id`,`folder_name`,depth 
			FROM `folder_depth_mapping` WHERE `institution_id` = %s 
			and `parent_folder_id` = %s""",(institution_id,folder_id))

		mainFolderDtls = cursor.fetchall()
		if not mainFolderDtls:
			mainFolderDtls = []
			
			cursor.execute("""SELECT icm.`course_id`, `course_title`, `course_description`, `course_image`, 
				`course_filetype`, `is_paid_course`,`total_fee`,`installment_available`,`installment_type`,
				`no_of_installments`,`teacher_id`, icm.`subject_id`,`subject_name`,icm.`topic_id`,
				`topic_name` FROM `instituition_course_master` icm INNER JOIN `subject` 
				on icm.`subject_id` = `subject`.`subject_id` INNER JOIN `topic` 
				on icm.`topic_id` = `topic`.`topic_id` LEFT JOIN `course_fee_mapping` cfm 
				ON icm.`course_id` = cfm.`course_id` WHERE  icm.`course_id` 
				in (SELECT `course_id` FROM `course_folder_mapping` WHERE `folder_id` = %s)""",(folder_id))
			courseDtls = cursor.fetchall()
			if courseDtls:
				isCourse = 1
				mainFolderDtls = courseDtls
		else:
			isFolder = 1
			for mid, fdtls in enumerate(mainFolderDtls):
				cursor.execute("""SELECT `folder_id`,`root_folder_id`,`parent_folder_id`,`folder_name`,depth 
					FROM `folder_depth_mapping` WHERE `institution_id` = %s 
					and `parent_folder_id` = %s""",(institution_id,fdtls.get('folder_id')))
				subfolderDtls = cursor.fetchall()

				if subfolderDtls:
					isCourseOrFolder = 1
				else:
					cursor.execute("""SELECT icm.`course_id`, `course_title`, `course_description`, `course_image`, 
						`course_filetype`, `is_paid_course`,`total_fee`,`installment_available`,`installment_type`,
						`no_of_installments`,`teacher_id`, icm.`subject_id`,`subject_name`,icm.`topic_id`,
						`topic_name` FROM `instituition_course_master` icm INNER JOIN `subject` 
						on icm.`subject_id` = `subject`.`subject_id` INNER JOIN `topic` 
						on icm.`topic_id` = `topic`.`topic_id` left JOIN `course_fee_mapping` cfm 
						ON icm.`course_id` = cfm.`course_id` WHERE  icm.`course_id` 
						in (SELECT `course_id` FROM `course_folder_mapping` 
						WHERE `folder_id` = %s and `teacher_id` = %s 
						AND `Institution_ID` = %s)""",(fdtls.get('folder_id'),teacher_id,institution_id))
					subCourses = cursor.fetchall()
					
					if subCourses:
						isCourseOrFolder = 2
					else:
						isCourseOrFolder = 0
				
				fdtls['isCourseOrFolder'] = isCourseOrFolder
		cursor.close()
		return ({"attributes": {"status_desc": "SubFolder/Course Details.",
								"status": "success",
								"isFolder":isFolder,
								"isCourse":isCourse},
				"responseList":mainFolderDtls}), status.HTTP_200_OK


@name_space.route("/updateFolder/<int:folder_id>/<string:folder_name>")
class updateFolder(Resource):
	def put(self,folder_id,folder_name):

		connection = connect_userlib()
		cursor = connection.cursor()
		
		updateFolderQuery = ("""UPDATE `folder_depth_mapping` SET `folder_name` = %s 
			WHERE `folder_id` = %s""")

		cursor.execute(updateFolderQuery,(folder_name,folder_id))

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Folder Details.",
								"status": "success"},
				"responseList":'Folder Updated.'}), status.HTTP_200_OK


@name_space.route("/getFolderByInstitutionId/<int:user_id>/<int:institution_id>")
class getFolderByInstitutionId(Resource):
	def get(self,user_id,institution_id):

		connection = connect_userlib()
		cursor = connection.cursor()
		has_subFolder = 0
		has_course = 0
		teacher_id = user_id
		cursor.execute("""SELECT `folder_id`,`root_folder_id`,`parent_folder_id`,`folder_name`,depth 
			FROM `folder_depth_mapping` WHERE `institution_id` = %s 
			and `depth` = 0""",(institution_id))

		mainFolderDtls = cursor.fetchall()

		for fid, fold in enumerate(mainFolderDtls):
			subFolderURL = BASE_URL + "course_section/MyelsaCourse/getSubFolderDtlsByRootFolderId/{}/{}/{}".format(teacher_id,institution_id,fold.get('root_folder_id'))
			subFolderRes = requests.get(subFolderURL).json()
			fold['subFolderDtls'] = subFolderRes
			cursor.execute("""SELECT icm.`course_id`, `course_title`, `course_description`, `course_image`, 
				`course_filetype`, `is_paid_course`,`total_fee`,`installment_available`,`installment_type`,
				`no_of_installments`,`teacher_id`, icm.`subject_id`,`subject_name`,icm.`topic_id`,
				`topic_name` FROM `instituition_course_master` icm INNER JOIN `subject` 
				on icm.`subject_id` = `subject`.`subject_id` INNER JOIN `topic` 
				on icm.`topic_id` = `topic`.`topic_id` left JOIN `course_fee_mapping` cfm 
				ON icm.`course_id` = cfm.`course_id` WHERE  icm.`course_id` 
				in (SELECT `course_id` FROM `course_folder_mapping` 
				WHERE `folder_id` = %s 
				AND `Institution_ID` = %s)""",(fold.get('folder_id'),institution_id))
			courseDtls = cursor.fetchall()
			if courseDtls:
				fold['courseDtls'] = courseDtls
			else:
				fold['courseDtls'] = courseDtls = []
		cursor.close()
		return ({"attributes": {"status_desc": "Folder Details.",
								"status": "success"},
				"responseList":mainFolderDtls}), status.HTTP_200_OK



@name_space.route("/getCourseListByStudentId/<int:student_id>/<int:institution_id>/<int:folder_id>")	
class getCourseListByStudentId(Resource):
	def get(self,student_id,institution_id,folder_id):

		connection = connect_userlib()
		curlab = connection.cursor()
		
		curlab.execute("""SELECT distinct scm.`course_id`,`course_title`,`course_description`,`course_image`,
			`course_filetype`,icm.`teacher_id`,icm.`subject_id`,`subject_name`,icm.`topic_id`,
			`topic_name` FROM `student_course_master` scm 
			INNER JOIN `course_folder_mapping` cfm on scm.`course_id` = cfm.`course_id`
			INNER JOIN `instituition_course_master` icm 
			ON cfm.`course_id` = icm.`course_id` INNER JOIN `subject` 
			on icm.`subject_id` = `subject`.`subject_id` INNER JOIN `topic` 
			on icm.`topic_id` = `topic`.`topic_id` WHERE `student_id` = %s 
			and `folder_id` = %s""",(student_id,folder_id))


		assignedCoursesDtls = curlab.fetchall()


		curlab.execute("""SELECT cfm.`course_id`,`course_title`, `course_description`, `course_image`, 
			`course_filetype` `is_paid_course`,`total_fee`,`installment_available`,`installment_type`,
			`no_of_installments`,icm.`teacher_id`, icm.`subject_id`,`subject_name`,icm.`topic_id`, 
			`topic_name` FROM `course_folder_mapping` cfm INNER JOIN `instituition_course_master` icm 
			on cfm.`course_id` = icm.`course_id` INNER JOIN `subject` on icm.`subject_id` = 
			`subject`.`subject_id` INNER JOIN `topic` on icm.`topic_id` = `topic`.`topic_id` 
			INNER JOIN `course_fee_mapping` cf ON icm.`course_id` = cf.`course_id` 
			WHERE cfm.`folder_id` = %s and cfm.`course_id` NOT IN 
			(SELECT `course_id` FROM `student_course_master` 
			WHERE `student_id` = %s)""",(folder_id,student_id))

		institutionCourseDtls = curlab.fetchall()


		courseDtls = {"assignedCourses":assignedCoursesDtls,
						"CoursesAvailable":institutionCourseDtls}
		
		totalCourses = len(assignedCoursesDtls) + len(institutionCourseDtls)
		totalAssigned = len(assignedCoursesDtls)
		curlab.close()
		return ({"attributes": {"status_desc": "Student Course Details",
								"status": "success",
								"total_courses_available":totalCourses,
								"total_courses_assigned":totalAssigned},
				"responseList": courseDtls}), status.HTTP_200_OK



@name_space.route("/getSubFolderDtlsByFolderIdAndUserRole/<int:user_id>/<int:institution_id>/<int:folder_id>/<string:user_role>")
class getSubFolderDtlsByFolderIdAndUserRole(Resource):
	def get(self,user_id,institution_id,folder_id,user_role):

		connection = connect_userlib()
		cursor = connection.cursor()
		isFolder = 0
		isCourse = 0
		isCourseOrFolder = 0
		teacher_id = user_id
		cursor.execute("""SELECT `folder_id`,`root_folder_id`,`parent_folder_id`,`folder_name`,depth 
			FROM `folder_depth_mapping` WHERE `institution_id` = %s 
			and `parent_folder_id` = %s""",(institution_id,folder_id))

		mainFolderDtls = cursor.fetchall()
		if not mainFolderDtls:
			mainFolderDtls = []
			if user_role.lower() == 'ta':
				cursor.execute("""SELECT icm.`course_id`,`fee_id`, `course_title`, `course_description`, `course_image`, 
					`course_filetype`, `is_paid_course`,`total_fee`,`installment_available`,`installment_type`,
					`no_of_installments`,`teacher_id`, icm.`subject_id`,`subject_name`,icm.`topic_id`,
					`topic_name` FROM `instituition_course_master` icm INNER JOIN `subject` 
					on icm.`subject_id` = `subject`.`subject_id` INNER JOIN `topic` 
					on icm.`topic_id` = `topic`.`topic_id` left JOIN `course_fee_mapping` cfm 
					ON icm.`course_id` = cfm.`course_id` WHERE  icm.`course_id` 
					in (SELECT `course_id` FROM `course_folder_mapping` WHERE `folder_id` = %s)""",(folder_id))
				courseDtls = cursor.fetchall()
				if courseDtls:
					isCourse = 1
					for cid, course in enumerate(courseDtls):
						cursor.execute("""SELECT count(Distinct(student_id)) as no_of_student_assign 
							FROM `student_course_master` where course_id = %s""",(course.get('course_id')))
						no_of_student = cursor.fetchone()
						if no_of_student:
							course['no_of_student_assign'] = no_of_student.get('no_of_student_assign')
						else:
							course['no_of_student_assign'] = 0
						course['no_of_student_seen'] = 1
					mainFolderDtls = courseDtls
			elif user_role.lower() == 's1':
				cursor.execute("""SELECT distinct scm.`course_id`,`course_title`,`course_description`,`course_image`,
					`course_filetype`,icm.`teacher_id`,icm.`subject_id`,`subject_name`,icm.`topic_id`,
					`topic_name` FROM `student_course_master` scm 
					INNER JOIN `course_folder_mapping` cfm on scm.`course_id` = cfm.`course_id`
					INNER JOIN `instituition_course_master` icm 
					ON cfm.`course_id` = icm.`course_id` INNER JOIN `subject` 
					on icm.`subject_id` = `subject`.`subject_id` INNER JOIN `topic` 
					on icm.`topic_id` = `topic`.`topic_id` WHERE `student_id` = %s 
					and `folder_id` = %s""",(teacher_id,folder_id))


				assignedCoursesDtls = cursor.fetchall()

				cursor.execute("""SELECT cfm.`course_id`,`course_title`, `course_description`, `course_image`, 
					`course_filetype` `is_paid_course`,`total_fee`,`installment_available`,`installment_type`,
					`no_of_installments`,icm.`teacher_id`, icm.`subject_id`,`subject_name`,icm.`topic_id`, 
					`topic_name` FROM `course_folder_mapping` cfm INNER JOIN `instituition_course_master` icm 
					on cfm.`course_id` = icm.`course_id` INNER JOIN `subject` on icm.`subject_id` = 
					`subject`.`subject_id` INNER JOIN `topic` on icm.`topic_id` = `topic`.`topic_id` 
					INNER JOIN `course_fee_mapping` cf ON icm.`course_id` = cf.`course_id` 
					WHERE cfm.`folder_id` = %s and cfm.`course_id` NOT IN 
					(SELECT `course_id` FROM `student_course_master` 
					WHERE `student_id` = %s)""",(folder_id,teacher_id))

				institutionCourseDtls = cursor.fetchall()
				
				totalCourses = len(assignedCoursesDtls) + len(institutionCourseDtls)
				totalAssigned = len(assignedCoursesDtls)

				courseDtls = {"assignedCourses":assignedCoursesDtls,
								"CoursesAvailable":institutionCourseDtls,
								"totalCourses":totalCourses,
								"totalAssigned":totalAssigned}

				if courseDtls:
					isCourse = 1
					mainFolderDtls = courseDtls

		else:
			isFolder = 1
			
			for mid, fdtls in enumerate(mainFolderDtls):
				cursor.execute("""SELECT `folder_id`,`root_folder_id`,`parent_folder_id`,`folder_name`,depth 
					FROM `folder_depth_mapping` WHERE `institution_id` = %s 
					and `parent_folder_id` = %s""",(institution_id,fdtls.get('folder_id')))
				subfolderDtls = cursor.fetchall()

				if subfolderDtls:
					isCourseOrFolder = 1
				else:
					cursor.execute("""SELECT icm.`course_id`, `course_title`, `course_description`, `course_image`, 
						`course_filetype`, `is_paid_course`,`total_fee`,`installment_available`,`installment_type`,
						`no_of_installments`,`teacher_id`, icm.`subject_id`,`subject_name`,icm.`topic_id`,
						`topic_name` FROM `instituition_course_master` icm INNER JOIN `subject` 
						on icm.`subject_id` = `subject`.`subject_id` INNER JOIN `topic` 
						on icm.`topic_id` = `topic`.`topic_id` left JOIN `course_fee_mapping` cfm 
						ON icm.`course_id` = cfm.`course_id` WHERE  icm.`course_id` 
						in (SELECT `course_id` FROM `course_folder_mapping` 
						WHERE `folder_id` = %s 
						AND `Institution_ID` = %s)""",(fdtls.get('folder_id'),institution_id))
					subCourses = cursor.fetchall()
					
					if subCourses:
						isCourseOrFolder = 2
					else:
						isCourseOrFolder = 0
				
				fdtls['isCourseOrFolder'] = isCourseOrFolder

		cursor.close()
		return ({"attributes": {"status_desc": "SubFolder/Course Details.",
								"status": "success",
								"isFolder":isFolder,
								"isCourse":isCourse},
				"responseList":mainFolderDtls}), status.HTTP_200_OK


@name_space.route("/createCourseCombo")
class createCourseCombo(Resource):
	@api.expect(create_course_combo)
	def post(self):

		connection = connect_userlib()
		cursor = connection.cursor()

		details = request.get_json()

		institution_id = details.get('institution_id')
		teacher_id = details.get('teacher_id')
		combo_type = details.get('combo_type')
		combo_name = details.get('combo_name')
		combo_desc = details.get('combo_desc')
		combo_image_url = details.get('combo_image_url')
		no_of_courses = details.get('no_of_courses')
		combo_amount = details.get('combo_amount')

		comboInsertQuery = ("""INSERT INTO `course_combo`(`institution_id`, `teacher_id`, `combo_type`, 
			`combo_name`, `combo_desc`, `combo_image_url`, `no_of_courses`, 
			`combo_amount`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""")


		comboData = (institution_id,teacher_id,combo_type,combo_name,combo_desc,combo_image_url,
			no_of_courses,combo_amount)


		cursor.execute(comboInsertQuery,comboData)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Course Combo Details.",
								"status": "success"},
				"responseList":'Combo Created.'}), status.HTTP_200_OK



@name_space.route("/getCourseComboByInstitutionId/<int:institution_id>")
class getCourseComboByInstitutionId(Resource):
	def get(self,institution_id):

		connection = connect_userlib()
		cursor = connection.cursor()

		cursor.execute("""SELECT `combo_id`,`teacher_id`, `combo_type`,`combo_type_name`,
			`combo_type_desc`, `combo_name`, `combo_desc`, `combo_image_url`, `no_of_courses`, 
			`combo_amount` FROM `course_combo` cc INNER JOIN `combo_type` ct 
			on cc.`combo_type` = ct.`combo_type_id` WHERE `institution_id` = %s""",(institution_id))

		comboDtls = cursor.fetchall()

		cursor.close()
		return ({"attributes": {"status_desc": "Course Combo Details.",
								"status": "success"},
				"responseList":comboDtls}), status.HTTP_200_OK


@name_space.route("/getCourseComboTypes")
class getCourseComboTypes(Resource):
	def get(self):

		connection = connect_userlib()
		cursor = connection.cursor()


		cursor.execute("""SELECT `combo_type_id`, `combo_type_name`,`combo_type_desc` FROM `combo_type`""")

		comboDtls = cursor.fetchall()

		cursor.close()
		return ({"attributes": {"status_desc": "Combo Types.",
								"status": "success"},
				"responseList":comboDtls}), status.HTTP_200_OK


@name_space.route("/getCourseListByInstitutionId/<int:institution_id>/<string:is_paid>")	
class getCourseListByInstitutionId(Resource):
	def get(self,institution_id,is_paid):
		connection = connect_userlib()
		cursor = connection.cursor()

		cursor.execute("""SELECT icm.`course_id`, `course_title`, `course_description`, `course_image`, 
			`course_filetype`, `is_paid_course`,`total_fee`,`installment_available`,`installment_type`, 
			`no_of_installments`,`teacher_id`, icm.`subject_id`,`subject_name`,icm.`topic_id`, 
			`topic_name` FROM `instituition_course_master` icm INNER JOIN `subject` 
			on icm.`subject_id` = `subject`.`subject_id` INNER JOIN `topic` 
			on icm.`topic_id` = `topic`.`topic_id` left JOIN `course_fee_mapping` cfm 
			ON icm.`course_id` = cfm.`course_id` WHERE icm.`Institution_ID` = %s 
			and `is_paid_course` = %s""",(institution_id,is_paid))

		courseDtls = cursor.fetchall()

		cursor.close()
		return ({"attributes": {"status_desc": "Institution Course List",
								"status": "success"},
				"responseList":courseDtls}), status.HTTP_200_OK