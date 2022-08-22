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

myelsa_new_course = Blueprint('myelsa_new_course_api', __name__)
api = Api(myelsa_new_course,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('MyelsaNewCourse',description='Myelsa New Course')

def last_update_ts():
	return (datetime.now() + timedelta(days=0, hours=5, minutes=30)).strftime('%Y-%m-%dT%H:%M:%S')

subject_post_model = api.model('SelectSubject', {
	"institution_id":fields.Integer(),
	"subject_name":fields.String(),
	"content_path":fields.String(),
	"subject_desc":fields.String(),
	"category_id":fields.Integer()
	})

topic_post_model = api.model('SelectTopic', {
	"subject_id":fields.Integer(),
	"institution_id":fields.Integer(),
	"topic_name":fields.String(),
	"content_path":fields.String(),
	"topic_desc":fields.String()
	})

subtopic_post_model = api.model('subtopic_post_model', {
	"subject_id":fields.Integer(),
	"topic_id":fields.Integer(),
	"institution_id":fields.Integer(),
	"subtopic_name":fields.String(),
	"content_path":fields.String(),
	"subtopic_desc":fields.String(),
	"last_update_id":fields.Integer()
	})

course_post_model = api.model('PostCourse',{
	"subject_id":fields.Integer(),
	"topic_id":fields.Integer(),
	"subtopic_id":fields.Integer(),
	"institution_id":fields.Integer(),
	"teacher_id":fields.Integer(),
	"course_name":fields.String(),
	"hours":fields.String(),
	"board":fields.String(),
	"class":fields.String(),
	"course_image":fields.String(),
	"course_video":fields.String(),
	"course_desc":fields.String(),
	"category_id":fields.Integer()
	})

module_model = api.model('PostModule',{
	"course_id":fields.Integer(),
	"institution_id":fields.Integer(),
	"teacher_id":fields.Integer(),
	"module_name":fields.String(),
	"module_desc":fields.String(),
	"content_path":fields.String(),
	"last_update_id":fields.Integer()
	})

section_model = api.model('PostSection',{
	"module_id":fields.Integer(),
	"course_id":fields.Integer(),
	"institution_id":fields.Integer(),
	"teacher_id":fields.Integer(),
	"section_name":fields.String(),
	"section_desc":fields.String(),
	"content_path":fields.String()
	})

update_course_model = api.model('update_course_model', {
	"course_id":fields.Integer(),
	"teacher_id":fields.Integer(),
	"course_name":fields.String(),
	"hours":fields.String(),
	"course_desc":fields.String(),
	"course_image":fields.String(),
	"course_video":fields.String()
	})

update_course_model_status = api.model('update_course_model_status',{
	"course_id":fields.Integer(),
	"course_status":fields.String()
	})

create_content_model = api.model('create_content_model', {
	"section_id":fields.Integer(),
	"module_id":fields.Integer(),
	"course_id":fields.Integer(),
	"teacher_id":fields.Integer(),
	"institution_id":fields.Integer(),
	"content_name":fields.String(),
	"content_path":fields.String(),
	"content_length":fields.String(),
	"content_type":fields.String()
	})

add_class_model = api.model('add_class_model',{
	"board_id":fields.Integer(),
	"institution_id":fields.Integer(),
	"class_name":fields.String()
	})

add_board_model = api.model('add_board_model',{
	"institution_id":fields.Integer(),
	"board_name":fields.String()
	})

update_course_board_model = api.model('update_course_board_model', {
	"course_id":fields.Integer(),
	"teacher_id":fields.Integer(),
	"board":fields.String(),
	"class":fields.String()
	})

#----------------------Post-Subject---------------------#
@name_space.route("/CreateSubject")
class CreateSubject(Resource):
	@api.expect(subject_post_model)
	def post(self):
	
		connection = connect_elsalibrary()
		cursor = connection.cursor()		
		details = request.get_json()

		institution_id = details['institution_id']
		subject_name = details['subject_name']
		content_path = details['content_path']
		subject_desc = details['subject_desc']
		category_id = details.get('category_id')

		if category_id == None:
			category_id = 0

		last_update_id = 0

		cursor.execute("""SELECT * FROM `subject` WHERE 
			`subject_name`=%s and `institution_id` = %s""",(subject_name,institution_id))
		existing_subject_cr = cursor.fetchone()

		if existing_subject_cr:
			existing_subject['last_update_ts'] = existing_subject['last_update_ts'].isoformat()

			return ({"attributes": {
	    				"status_desc": "Subject Details.",
	    				"status": "success",
	    				"msg":"Already Exist"
	    				},
	    				"responseList":existing_subject}), status.HTTP_200_OK

		else:
			insert_query = ("""INSERT INTO `subject`(`institution_id`,`category_id`,
				`subject_name`,`content_path`,`subject_desc`,
				`last_update_id`) VALUES(%s,%s,%s,%s,%s,%s)""")
			insertdata = cursor.execute(insert_query,((institution_id,category_id,
				subject_name,content_path,subject_desc,last_update_id)))

			if insertdata:
				msg = "Added"
				subject_id = cursor.lastrowid
				details['subject_id'] = subject_id

			else:
				msg = "Not Added"

		connection.commit()
		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Subject Details.",
	    				"status": "success"
	    				},
	    				"responseList":details }), status.HTTP_200_OK

#----------------------Post-Subject---------------------#
@name_space.route("/GetSubjectByInstitutionId/<int:institution_id>/<int:student_id>")
class GetSubjectByInstitutionId(Resource):
	def get(self, institution_id,student_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		conn = connect_logindb()
		cur = conn.cursor()

		subList = []
		cur.execute("""SELECT `CLASS`,`Board` FROM `student_dtls` 
			WHERE `INSTITUTION_USER_ID_STUDENT`=%s limit 1""",(student_id))

		studentdata = cur.fetchone()
		if studentdata:
			board = studentdata['Board']
			clss = studentdata['CLASS']
		else:
			board = ''
			clss = ''

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

		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Subject Details.",
	    				"status": "success"
	    				},
	    				"responseList":subList}), status.HTTP_200_OK


@name_space.route("/GetSubjectByInstitutionId/<int:institution_id>",
	doc={'params':{'category_id':'category_id'}})
class GetSubjectByInstitutionId(Resource):
	def get(self, institution_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		category_id = int(request.args.get('category_id',0))

		if category_id == 0:
			cursor.execute("""SELECT * FROM `subject` WHERE `institution_id`=%s""",
			(institution_id))
		else:
			cursor.execute("""SELECT * FROM `subject` WHERE `institution_id`=%s AND `category_id` = %s""",
			(institution_id,category_id))

		subjectdata = cursor.fetchall()
		if subjectdata == ():
			subjectdata = []

		else:
			for x in subjectdata:
				x['last_update_ts'] = x['last_update_ts'].isoformat()

		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Subject Details.",
	    				"status": "success"
	    				},
	    				"responseList":subjectdata}), status.HTTP_200_OK

#----------------------------------------------------------#
@name_space.route("/GetTopicsBySubjectId/<int:subject_id>")
class GetTopicsBySubjectId(Resource):
	def get(self, subject_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		cursor.execute("""SELECT `topic_id`,`topic_name`,sub.`subject_id`,`subject_name`,top.`content_path`,
			`topic_desc`,top.`last_update_id`,top.`last_update_ts` FROM `topic` top
			INNER JOIN `subject` sub ON top.`subject_id`=sub.`subject_id` 
			WHERE top.`subject_id`=%s""",(subject_id))

		topicdata = cursor.fetchall()
		if topicdata == ():
			topicdata = []

		else:
			for x in topicdata:
				x['last_update_ts'] = x['last_update_ts'].isoformat()

		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Topic Details.",
	    				"status": "success"
	    				},
	    				"responseList":topicdata}), status.HTTP_200_OK

#----------------------Post-Topic---------------------#
@name_space.route("/CreateTopic")
class CreateTopic(Resource):
	@api.expect(topic_post_model)	
	def post(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()		
		details = request.get_json()

		subject_id = details['subject_id']
		institution_id = details['institution_id']
		topic_name = details['topic_name']
		content_path = details['content_path']
		topic_desc = details['topic_desc']
		last_update_id = 0

		existing_topic_cr = cursor.execute("""SELECT `topic_id`,`topic_name`,sub.`subject_id`,`subject_name`,`topic_desc`,`top`.`last_update_ts` FROM `topic` top
			INNER JOIN `subject` sub ON top.`subject_id`=sub.`subject_id` 
			WHERE top.`subject_id`=%s and `topic_name` = %s""",(subject_id,topic_name))
		existing_topic = cursor.fetchone()

		if existing_topic_cr:

			details['last_update_ts'] =existing_topic.get('last_update_ts').isoformat()
			cursor.close()

			return ({"attributes": {
	    				"status_desc": "Topic Details.",
	    				"status": "success",
	    				"msg":"Already Exist"
	    				},
	    				"responseList":details}), status.HTTP_200_OK
		else:

			insert_query = ("""INSERT INTO `topic` (`subject_id`,`institution_id`,`topic_name`,`content_path`,
			`topic_desc`,`last_update_id`) VALUES(%s,%s,%s,%s,%s,%s)""")
			data = (subject_id,institution_id,topic_name,content_path,topic_desc,last_update_id)
			insertdata = cursor.execute(insert_query,data)
			if insertdata:
				msg = "Added"
				details['topic_id'] = cursor.lastrowid
			else:
				msg = "Not Added"

		connection.commit()
		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Topic Details.",
	    				"status": "success",
	    				"msg":msg
	    				},
	    				"responseList":details}), status.HTTP_200_OK

#----------------------------------------------------------#
@name_space.route("/CreateSubTopic")
class CreateSubTopic(Resource):
	@api.expect(subtopic_post_model)
	def post(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()		
		details = request.get_json()

		subject_id = details['subject_id']
		topic_id = details['topic_id']
		institution_id = details['institution_id']
		subtopic_name = details['subtopic_name']
		content_path = details['content_path']
		subtopic_desc = details['subtopic_desc']
		last_update_id = details['last_update_id']

		verify_name_query_execution = cursor.execute(("""SELECT * FROM `subtopic` WHERE `subtopic_name` = %s"""),(subtopic_name))
		print(verify_name_query_execution)
		if verify_name_query_execution:
			name_data = cursor.fetchone()

			details['last_update_ts'] = name_data.get('last_update_ts').isoformat()
			cursor.close()

			return ({"attributes": {
	    				"status_desc": "SubTopic Details.",
	    				"status": "success",
	    				"msg":"Already Exist"
	    				},
	    				"responseList":details}), status.HTTP_200_OK

		#---------------Insert Into subtopic database ----------------#
		insert_query = ("""INSERT INTO `subtopic` (`subject_id`,`topic_id`,`institution_id`,`subtopic_name`,
			`content_path`,`subtopic_desc`,`last_update_id`) VALUES(%s,%s,%s,%s,%s,%s,%s)""")
		data = (subject_id,topic_id,institution_id,subtopic_name,content_path,subtopic_desc,last_update_id)
		insertdata =cursor.execute(insert_query,data)

		if insertdata:
			msg = "Added"
			details['subtopic_id'] = cursor.lastrowid
		else:
			msg = "Not Added"

		connection.commit()
		cursor.close()

		return ({"attributes": {
	    				"status_desc": "SubTopic Details.",
	    				"status": "success",
	    				"msg":msg
	    				},
	    				"responseList":details}), status.HTTP_200_OK

#----------------------Post-SubTopic---------------------#
@name_space.route("/GetSubTopicByTopic/<int:topic_id>")
class GetSubTopicByTopic(Resource):
	def get(self, topic_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		cursor.execute("""SELECT `st`.`subtopic_id`, `st`.`topic_id`,`st`.`subject_id`,`st`.`subtopic_name`,`t`.`topic_name`,`s`.`subject_name`,
			`st`.`subtopic_desc`,`st`.`content_path`,`st`.`last_update_ts`
			 FROM `subtopic` st INNER JOIN `topic` t ON `st`.`topic_id` = `t`.`topic_id` INNER JOIN `subject` s
			 ON `st`.`subject_id` = `s`.`subject_id` WHERE `st`.`topic_id` = %s""",(topic_id))

		data = cursor.fetchall()

		if data == ():
			data = []

		else:
			for x in data:
				x['last_update_ts'] = x['last_update_ts'].isoformat()

		cursor.close()

		return ({"attributes": {
	    				"status_desc": "SubTopic Details.",
	    				"status": "success"
	    				},
	    				"responseList":data}), status.HTTP_200_OK

#----------------------Create Course----------------------#

@name_space.route("/CreateCourse")
class CreateCourse(Resource):
	@api.expect(course_post_model)
	def post(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()

		subject_id = details['subject_id']
		topic_id = details['topic_id']
		subtopic_id = details['subtopic_id']
		institution_id = details['institution_id']
		course_name = details['course_name']
		hours = details['hours']
		board = details['board']
		_class = details['class']
		course_image = details['course_image']
		course_video = details['course_video']
		course_desc = details['course_desc']
		teacher_id = details['teacher_id']
		category_id = details.get('category_id')

		if category_id == None:
			category_id = 0

		#--------------------Insert Course Into Database-----------------#
		insert_query = ("""INSERT INTO `course` (`subject_id`,`category_id`,`topic_id`,`subtopic_id`,`institution_id`,
			`teacher_id`,`board`,`class`,`course_name`,hours,`course_image`,`course_video`,`course_desc`)
			 VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
		data = (subject_id,category_id,topic_id,subtopic_id,institution_id,teacher_id,board,_class,course_name,
			hours,course_image,course_video,course_desc)
		insertdata = cursor.execute(insert_query,data)

		if insertdata:
			course_id = cursor.lastrowid

			fees_query = ("""INSERT INTO `course_fee_mapping`(`is_paid_course`,
			`total_fee`,`installment_available`,`installment_type`,
			`course_id`,`no_of_installments`) VALUES(%s,%s,%s,%s,%s,%s)""")

			msg = ""
			feedata = cursor.execute(fees_query,("n","0","n","",course_id,0))
			if feedata:
				msg = "Added"
			else:
				msg = "Not Added"

		else:
			msg = "Not Added"
			course_id = 0

		connection.commit()
		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Course Details.",
	    				"status": "success",
	    				"msg":msg
	    				},
	    				"responseList":course_id}), status.HTTP_200_OK

#----------------------Create Course----------------------#
@name_space.route("/SubjcetWiseCourseModuleSectionDtlsByInstitutionId/<int:institution_id>",
	doc={'params':{'category_id':'category_id'}})
class SubjcetWiseCourseModuleSectionDtlsByInstitutionId(Resource):
	def get(self,institution_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		cList = []

		category_id = int(request.args.get('category_id',0))

		if category_id == 0:
			cursor.execute("""SELECT `subject_id`,`category_id`,`subject_name`,
			`content_path`,`subject_desc`,`last_update_ts` FROM 
			`subject` WHERE `institution_id`=%s""",(institution_id))
		else:
			cursor.execute("""SELECT `subject_id`,`category_id`,`subject_name`,
			`content_path`,`subject_desc`,`last_update_ts` FROM 
			`subject` WHERE `institution_id`=%s AND `category_id` = %s""",(institution_id,category_id))

		subjectdata = cursor.fetchall()
		if subjectdata == ():
			subjectdata = []
			
		else:
			for sid in range(len(subjectdata)):
				subjectdata[sid]['last_update_ts'] = subjectdata[sid]['last_update_ts'].isoformat()

				cursor.execute("""SELECT count(`topic_id`)as total FROM `topic` 
					where `subject_id`=%s""",(subjectdata[sid]['subject_id']))

				totalTopic = cursor.fetchone()
				if totalTopic:
					subjectdata[sid]['totaltopic'] = totalTopic['total']
				else:
					subjectdata[sid]['totaltopic'] = 0

				cursor.execute("""SELECT `course_id` FROM `course` 
					where `subject_id`=%s and `institution_id`=%s""",
					(subjectdata[sid]['subject_id'],institution_id))

				totalCourse = cursor.fetchall()
				
				subjectdata[sid]['totalcourse'] = len(totalCourse)
				courseList = [course['course_id'] for cid, course in enumerate(totalCourse)]
	
				courselist = list(set(courseList))
				clist = tuple(courselist)
				if len(courselist) == 0:
					subjectdata[sid]['totalsection'] = 0
					subjectdata[sid]['totalmodule'] = 0
				elif len(courselist) <2:
					cursor.execute("""SELECT `section_id` FROM 
						`section` where `course_id` in (%s)""",format(clist[0]))

					sectiondata = cursor.fetchall()

					subjectdata[sid]['totalsection'] = len(sectiondata)

					cursor.execute("""SELECT `module_id` FROM 
						`module` where `course_id` in(%s)""",format(clist[0]))

					moduledata = cursor.fetchall()

					subjectdata[sid]['totalmodule'] = len(moduledata)
				else:
					seclist = []
					modlist = []
					for clid in courselist:
						cursor.execute("""SELECT count(`section_id`)as total FROM 
							`section` where `course_id`=%s""",format(clid))

						sectiondata = cursor.fetchone()
						
						cursor.execute("""SELECT count(`module_id`)as total FROM 
							`module` where `course_id`=%s""",format(clid))

						moduledata = cursor.fetchone()

						seclist.append(sectiondata['total'])
						modlist.append(moduledata['total'])
						
					subjectdata[sid]['totalsection'] = sum(seclist)

					subjectdata[sid]['totalmodule'] = sum(modlist)
				
		cursor.close()

		return ({"attributes": {
	    				"status_desc": "SubjcetWise Course Module Section Details.",
	    				"status": "success"
	    				},
	    				"responseList":subjectdata}), status.HTTP_200_OK

#--------------------------Get Course Paginated---------------------#

@name_space.route("/GetCourseBySubjectIdPaginated/<int:subject_id>",
	doc={'params':{'start':'course_id','limit':'limit','page':'pageno'}})
class GetCourseBySubjectIdPaginated(Resource):
	def get(self,subject_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		start = int(request.args.get('start',0))
		limit = int(request.args.get('limit',50))
		page = int(request.args.get('page',1))

		cursor.execute("""SELECT count(`course_id`) as 'count' FROM `course` WHERE `subject_id`=%s
			and course_status = 'public'""",(subject_id))
		total_count = cursor.fetchone().get('count')
		cur_count = int(page) * int(limit)

		if start==0:
			cursor.execute("""SELECT c.*,s.`subject_name`,t.`topic_name`,st.`subtopic_name` FROM `course` c INNER JOIN 
				`subject` s ON c.`subject_id` = s.`subject_id` INNER JOIN `topic` t ON c.`topic_id`=t.`topic_id` INNER JOIN 
				`subtopic` st ON c.`subtopic_id`=st.`subtopic_id` WHERE c.`subject_id`=%s and course_status = 'public' 
				order by c.`course_id` limit %s""",(subject_id,limit))
			course_dtls = cursor.fetchall()
		else:
			cursor.execute("""SELECT c.*,s.`subject_name`,t.`topic_name`,st.`subtopic_name` FROM `course` c INNER JOIN 
				`subject` s ON c.`subject_id` = s.`subject_id` INNER JOIN `topic` t ON c.`topic_id`=t.`topic_id` INNER JOIN 
				`subtopic` st ON c.`subtopic_id`=st.`subtopic_id` WHERE c.`subject_id`=%s and c.`course_id`>%s 
				and course_status = 'public' order by c.`course_id` limit %s""",(subject_id,start,limit))
			course_dtls = cursor.fetchall()

		for x in course_dtls:
			x['last_update_ts'] = x['last_update_ts'].isoformat()

		page_next = page + 1

		if cur_count < total_count:
			next_url = '?start={}&limit={}&page={}'.format(course_dtls[-1].get('subject_id'),limit,page_next)
		else:
			next_url = ''

		return ({"attributes": {"status_desc": "Courses By Subject Id Details.",
									"status": "success",
									"total":total_count,
									"next":next_url
									},
					"responseList": course_dtls}), status.HTTP_200_OK

#--------------------------Get Course Paginated---------------------#

#------------------------- Post Module-----------------------------#

@name_space.route("/CreateCourseModule")
class CreateCourseModule(Resource):
	@api.expect(module_model)
	def post(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		details = request.get_json()
		course_id=details['course_id']
		institution_id = details['institution_id']
		teacher_id = details['teacher_id']
		module_name=details['module_name']
		module_desc=details['module_desc']
		content_path=details['content_path']
		last_update_id=details['last_update_id']


		#verify module name
		cursor.execute("""SELECT `module_id`,`last_update_ts` FROM `module` WHERE `module_name` = %s and `course_id` = %s""",(module_name,course_id))
		verify_name_details=cursor.fetchone()

		if verify_name_details:
			details['module_id'] = verify_name_details.get('module_id')
			details['last_update_ts'] = verify_name_details.get('last_update_ts').isoformat()

			cursor.close()
			return ({"attributes": {
	    				"status_desc": "Course Module Details.",
	    				"status": "success",
	    				"msg":"Module Already Exist"
	    				},
	    				"responseList":details}), status.HTTP_200_OK

		insert_query = ("""INSERT INTO `module` (`course_id`,`institution_id`,`teacher_id`,`module_name`,`module_desc`,`content_path`,`last_update_id`) VALUES(%s,%s,%s,%s,%s,%s,%s)""")
		insertdata = cursor.execute(insert_query,(course_id,institution_id,teacher_id,module_name,module_desc,content_path,last_update_id))

		if insertdata:
			msg = "Added"
			details['module_id'] = cursor.lastrowid
			details['last_update_ts'] = last_update_ts()
		else:
			msg = "Not Added"

		connection.commit()
		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Course Module Details.",
	    				"status": "success",
	    				"msg":msg
	    				},
	    				"responseList":details}), status.HTTP_200_OK


#------------------------- Post Module-----------------------------#

#--------------------------Get Module Paginated---------------------#

@name_space.route("/GetModuleByCourseIdPaginated/<int:course_id>",
	doc={'params':{'start':'module_id','limit':'limit','page':'pageno'}})
class GetModuleByCourseIdPaginated(Resource):
	def get(self,course_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		start = int(request.args.get('start',0))
		limit = int(request.args.get('limit',50))
		page = int(request.args.get('page',1))

		cursor.execute("""SELECT count(`module_id`) as 'count' FROM `module` WHERE `course_id`=%s""",(course_id))
		total_count = cursor.fetchone().get('count')
		cur_count = int(page) * int(limit)

		if start==0:
			cursor.execute("""SELECT `module_id`,`course_id`,`institution_id`,`teacher_id`,`module_name`,
				`module_desc`,`content_path`,`last_update_id`,`last_update_ts` FROM `module` WHERE `course_id`=%s order by `module_id`
	        	limit %s""",(course_id,limit))
			module_dtls = cursor.fetchall()
		else:
			cursor.execute("""SELECT `module_id`,`course_id`,`institution_id`,`teacher_id`,`module_name`,
				`module_desc`,`content_path`,`last_update_id`,`last_update_ts` FROM `module` WHERE `course_id`=%s and `module_id`>%s order by `module_id`
	        	limit %s""",(course_id,start,limit))
			module_dtls = cursor.fetchall()

		for x in module_dtls:
			x['last_update_ts'] = x['last_update_ts'].isoformat()
			cursor.execute("""SELECT count(`section_id`) as 'count' FROM `section` WHERE `module_id` = %s""",(x['module_id']))
			x['section_count'] = cursor.fetchone().get('count')

		page_next = page + 1

		if cur_count < total_count:
			next_url = '?start={}&limit={}&page={}'.format(module_dtls[-1].get('module_id'),limit,page_next)
		else:
			next_url = ''

		return ({"attributes": {"status_desc": "Modules By Course Id Details.",
									"status": "success",
									"total":total_count,
									"next":next_url
									},
					"responseList": module_dtls}), status.HTTP_200_OK

#--------------------------Get Module Paginated---------------------#

#--------------------------Get Module Paginated---------------------#

@name_space.route("/GetModuleByCourseId/<int:course_id>")
class GetModuleByCourseId(Resource):
	def get(self,course_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		cursor.execute("""SELECT `module_id`,`course_id`,`institution_id`,`teacher_id`,`module_name`,
				`module_desc`,`content_path`,`last_update_id`,`last_update_ts` FROM `module` WHERE `course_id`=%s order by `module_id` """,(course_id))
		module_dtls = cursor.fetchall()

		for x in module_dtls:
			x['last_update_ts'] = x['last_update_ts'].isoformat()
			cursor.execute("""SELECT count(`section_id`) as 'count' FROM `section` WHERE `module_id` = %s""",(x['module_id']))
			x['section_count'] = cursor.fetchone().get('count')



		return ({"attributes": {"status_desc": "Modules By Course Id Details.",
									"status": "success"
									},
					"responseList": module_dtls}), status.HTTP_200_OK

#--------------------------Get Module Paginated---------------------#

#-----------------------------Post Section--------------------------#

@name_space.route("/CreateModuleSection")
class CreateModuleSection(Resource):
	@api.expect(section_model)
	def post(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		details = request.get_json()
		cursor.execute("""SELECT `section_id`,`last_update_ts` FROM `section` WHERE `section_name`=%s and `module_id` = %s""",(details['section_name'],details['module_id']))
		verify_name_details = cursor.fetchone()

		if verify_name_details:
			details['section_id'] = verify_name_details.get('section_id')
			details['last_update_ts'] = verify_name_details.get('last_update_ts').isoformat()
			cursor.close()

			return ({"attributes": {
	    				"status_desc": "Module Section Details.",
	    				"status": "success",
	    				"msg":"Already Exist"
	    				},
	    				"responseList":details}), status.HTTP_200_OK

		insert_query = ("""INSERT INTO `section` (`module_id`,`course_id`,`institution_id`,`teacher_id`,`section_name`,`section_desc`,
			`content_path`,`last_update_id`) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")
		insertdata = (details['module_id'],details['course_id'],details['institution_id'],details['teacher_id'],details['section_name'],
			details['section_desc'],details['content_path'],details['teacher_id'])
		data = cursor.execute(insert_query,insertdata)

		if data:
			details['section_id'] = cursor.lastrowid
			details['last_update_ts'] = last_update_ts()
			msg = "Added"
		else:
			msg = "Not Added"

		connection.commit()
		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Module Section Details.",
	    				"status": "success",
	    				"msg":msg
	    				},
	    				"responseList":details}), status.HTTP_200_OK

#-----------------------------Post Section--------------------------#

#------------------------Get Section Paginated----------------------#

@name_space.route("/GetSectionsByModuleIdPaginated/<int:module_id>",
	doc={'params':{'start':'section_id','limit':'limit','page':'pageno'}})
class GetSectionsByModuleIdPaginated(Resource):
	def get(self,module_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		start = int(request.args.get('start',0))
		limit = int(request.args.get('limit',50))
		page = int(request.args.get('page',1))

		cursor.execute("""SELECT count(`section_id`) as 'count' FROM `section` WHERE `module_id`=%s""",(module_id))
		total_count = cursor.fetchone().get('count')
		cur_count = int(page) * int(limit)

		if start==0:
			cursor.execute("""SELECT `section_id`,`module_id`,`course_id`,`section_name`,`section_desc`,`content_path`,`last_update_ts` FROM `section` WHERE `module_id`=%s order by `section_id`
	        	limit %s""",(module_id,limit))
			section_dtls = cursor.fetchall()
		else:
			cursor.execute("""SELECT `section_id`,`module_id`,`course_id`,`section_name`,`section_desc`,`content_path`,`last_update_ts` FROM `section` WHERE `module_id`=%s and `section_id`>%s order by `section_id`
	        	limit %s""",(module_id,start,limit))
			section_dtls = cursor.fetchall()

		for x in section_dtls:
			x['last_update_ts'] = x['last_update_ts'].isoformat()
			cursor.execute("""SELECT count(`content_id`) as 'count' FROM `course_content` WHERE `section_id` = %s""",(x['section_id']))
			x['content_count'] = cursor.fetchone().get('count')

		page_next = page + 1

		if cur_count < total_count:
			next_url = '?start={}&limit={}&page={}'.format(section_dtls[-1].get('module_id'),limit,page_next)
		else:
			next_url = ''

		return ({"attributes": {"status_desc": "Modules By Course Id Details.",
									"status": "success",
									"total":total_count,
									"next":next_url
									},
					"responseList": section_dtls}), status.HTTP_200_OK

#------------------------Get Section Paginated----------------------#

#------------------------Get Section----------------------#

@name_space.route("/GetSectionsByModuleId/<int:module_id>")
class GetSectionsByModuleId(Resource):
	def get(self,module_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		
		cursor.execute("""SELECT `section_id`,`module_id`,`course_id`,`section_name`,`section_desc`,`content_path`,`last_update_ts` FROM `section` WHERE `module_id`=%s order by `section_id`
	        	""",(module_id))
		section_dtls = cursor.fetchall()

		for x in section_dtls:
			x['last_update_ts'] = x['last_update_ts'].isoformat()
			cursor.execute("""SELECT count(`content_id`) as 'count' FROM `course_content` WHERE `section_id` = %s""",(x['section_id']))
			x['content_count'] = cursor.fetchone().get('count')

		return ({"attributes": {"status_desc": "Modules By Course Id Details.",
									"status": "success"
									},
					"responseList": section_dtls}), status.HTTP_200_OK

#------------------------Get Section----------------------#

#------------------------Get Last 10 Course ------------------------#

@name_space.route("/GetRecentCoursesByInstitutionId/<int:institution_id>",doc={'params':{'limit':'recent'}})
class GetRecentCoursesByInstitutionId(Resource):
	def get(self,institution_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		limit = int(request.args.get('limit',10))

		cursor.execute("""SELECT c.`course_id`,`course_name`,c.`hours`,
			`course_image`,`course_status`,board,class,is_paid_course,total_fee,
			installment_available,installment_type,no_of_installments FROM `course` c inner join
			`course_fee_mapping` cfm on c.`course_id`=cfm.`course_id`
			WHERE `institution_id` = %s ORDER BY `course_id` DESC LIMIT %s""",(institution_id,limit))

		data = cursor.fetchall()
		
		if data == ():
			data = []
		else:
			for x in data:
				cursor.execute("""SELECT count(`module_id`) as 'count' FROM `module` 
					WHERE `course_id` = %s""",(x['course_id']))
				x['module_count'] = cursor.fetchone().get('count')
				

		return ({"attributes": {"status_desc": "Recent Courses",
									"status": "success"
								},
					"responseList": data}), status.HTTP_200_OK

#------------------------Get Last 10 Course ------------------------#

#--------------------------Get Course Paginated---------------------#

#date-31-07-21
@name_space.route("/GetAllCourseBySubjectIdPaginated/<int:subject_id>",
	doc={'params':{'start':'course_id','limit':'limit','page':'pageno'}})
class GetAllCourseBySubjectIdPaginated(Resource):
	def get(self,subject_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		start = int(request.args.get('start',0))
		limit = int(request.args.get('limit',10))
		page = int(request.args.get('page',1))

		cursor.execute("""SELECT count(`course_id`) as 'count' FROM `course` WHERE `subject_id`=%s""",(subject_id))
		total_count = cursor.fetchone().get('count')
		cur_count = int(page) * int(limit)
		
		if start==0:
			cursor.execute("""SELECT c.`course_id`,c.`course_name`,c.`hours`,
				c.`course_status`,c.`course_image`,board,class,
				is_paid_course,total_fee,installment_available,
				installment_type,no_of_installments,c.`last_update_ts` 
				FROM `course` c inner join `course_fee_mapping` cfm on 
				c.`course_id`=cfm.`course_id` WHERE c.`subject_id`=%s 
				order by c.`course_id` limit %s""",(subject_id,limit))
			course_dtls = cursor.fetchall()
			for x in course_dtls:
				x['last_update_ts'] = x['last_update_ts'].isoformat()
				cursor.execute("""SELECT count(`module_id`) as 'count' FROM `module` WHERE `course_id` = %s""",(x['course_id']))
				x['module_count'] = cursor.fetchone().get('count')
		else:
			cursor.execute("""SELECT c.`course_id`,c.`course_name`,c.`hours`,
				c.`course_status`,c.`course_image`,board,class,
				is_paid_course,total_fee,installment_available,
				installment_type,no_of_installments,c.`last_update_ts` 
				FROM `course` c inner join `course_fee_mapping` cfm on 
				c.`course_id`=cfm.`course_id` WHERE c.`subject_id`=%s and c.`course_id`>%s 
	        	order by c.`course_id` limit %s""",(subject_id,start,limit))
			course_dtls = cursor.fetchall()

			for x in course_dtls:
				x['last_update_ts'] = x['last_update_ts'].isoformat()
				cursor.execute("""SELECT count(`module_id`) as 'count' FROM `module` WHERE `course_id` = %s""",(x['course_id']))
				x['module_count'] = cursor.fetchone().get('count')

		page_next = page + 1

		if cur_count < total_count:
			next_url = '?start={}&limit={}&page={}'.format(course_dtls[-1].get('course_id'),limit,page_next)
		else:
			next_url = ''

		return ({"attributes": {"status_desc": "Courses By Subject Id Details.",
									"status": "success",
									"total":total_count,
									"next":next_url
									},
					"responseList": course_dtls}), status.HTTP_200_OK

#--------------------------Get Course Paginated---------------------#

#--------------------------Get Course Paginated---------------------#

#date-31-07-21
@name_space.route("/GetAllCourseBySubjectId/<int:subject_id>")
class GetAllCourseBySubjectId(Resource):
	def get(self,subject_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT c.`course_id`,c.`course_name`,c.`hours`,
				c.`course_status`,c.`course_image`,board,class,
				is_paid_course,total_fee,installment_available,
				installment_type,no_of_installments,c.`last_update_ts` 
				FROM `course` c inner join `course_fee_mapping` cfm on 
				c.`course_id`=cfm.`course_id` WHERE c.`subject_id`=%s 
				order by c.`course_id`""",(subject_id))
		course_dtls = cursor.fetchall()
		for x in course_dtls:
			x['last_update_ts'] = x['last_update_ts'].isoformat()
			cursor.execute("""SELECT count(`module_id`) as 'count' FROM `module` WHERE `course_id` = %s""",(x['course_id']))
			x['module_count'] = cursor.fetchone().get('count')

		

		return ({"attributes": {"status_desc": "Courses By Subject Id Details.",
									"status": "success"
									},
					"responseList": course_dtls}), status.HTTP_200_OK

#--------------------------Get Course Paginated---------------------#

#--------------------------Get Course Paginated With Filter---------------------#

@name_space.route("/GetAllCourseBySubjectIdPaginatedWithFilter/<int:subject_id>",
	doc={'params':{'start':'course_id','limit':'limit','page':'pageno','board_name':'board_name','class_name':'class_name'}})
class GetAllCourseBySubjectIdPaginatedWithFilter(Resource):
	def get(self,subject_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		start = int(request.args.get('start',0))
		limit = int(request.args.get('limit',10))
		page = int(request.args.get('page',1))
		board_name = request.args.get('board_name','n')
		class_name = request.args.get('class_name','n')

		cursor.execute("""SELECT count(`course_id`) as 'count' FROM `course` WHERE `subject_id`=%s""",(subject_id))
		total_count = cursor.fetchone().get('count')
		cur_count = int(page) * int(limit)
		
		if start==0:
			if board_name != 'n':
				if class_name != 'n':
					qry = ("""SELECT c.`course_id`,c.`course_name`,c.`hours`, c.`course_status`,c.`course_image`,board,class,is_paid_course,
						total_fee,installment_available,installment_type,no_of_installments,c.`last_update_ts` FROM 
						`course` c inner join `course_fee_mapping` cfm on c.`course_id`=cfm.`course_id` WHERE c.`subject_id`=%s and c.`board` = %s and c.`class` = %s
						 order by c.`course_id` limit %s""")
					qdata = (subject_id,board_name,class_name,limit)
				else:
					qry = ("""SELECT c.`course_id`,c.`course_name`,c.`hours`, c.`course_status`,c.`course_image`,board,class,is_paid_course,
						total_fee,installment_available,installment_type,no_of_installments,c.`last_update_ts` FROM 
						`course` c inner join `course_fee_mapping` cfm on c.`course_id`=cfm.`course_id` WHERE c.`subject_id`=%s and c.`board` = %s
						 order by c.`course_id` limit %s""")
					qdata = (subject_id,board_name,limit)
			else:
				qry = ("""SELECT c.`course_id`,c.`course_name`,c.`hours`,
				c.`course_status`,c.`course_image`,board,class,
				is_paid_course,total_fee,installment_available,
				installment_type,no_of_installments,c.`last_update_ts` 
				FROM `course` c inner join `course_fee_mapping` cfm on 
				c.`course_id`=cfm.`course_id` WHERE c.`subject_id`=%s 
				order by c.`course_id` limit %s""")
				qdata = (subject_id,limit)

			cursor.execute(qry,qdata)
			course_dtls = cursor.fetchall()
			for x in course_dtls:
				x['last_update_ts'] = x['last_update_ts'].isoformat()
				cursor.execute("""SELECT count(`module_id`) as 'count' FROM `module` WHERE `course_id` = %s""",(x['course_id']))
				x['module_count'] = cursor.fetchone().get('count')
		else:
			if board_name != 'n':
				if class_name != 'n':
					qry = ("""SELECT c.`course_id`,c.`course_name`,c.`hours`, c.`course_status`,c.`course_image`,board,class,is_paid_course,
						total_fee,installment_available,installment_type,no_of_installments,c.`last_update_ts` FROM 
						`course` c inner join `course_fee_mapping` cfm on c.`course_id`=cfm.`course_id` WHERE c.`subject_id`=%s and c.`course_id`>%s and c.`board` = %s and c.`class` = %s 
						 order by c.`course_id` limit %s""")
					qdata = (subject_id,start,board_name,class_name,limit)
				else:
					qry = ("""SELECT c.`course_id`,c.`course_name`,c.`hours`, c.`course_status`,c.`course_image`,board,class,is_paid_course,
						total_fee,installment_available,installment_type,no_of_installments,c.`last_update_ts` FROM 
						`course` c inner join `course_fee_mapping` cfm on c.`course_id`=cfm.`course_id` WHERE c.`subject_id`=%s and c.`course_id`>%s and c.`board` = %s 
						 order by c.`course_id` limit %s""")
					qdata = (subject_id,start,board_name,limit)
			else:
				qry = ("""SELECT c.`course_id`,c.`course_name`,c.`hours`,
				c.`course_status`,c.`course_image`,board,class,
				is_paid_course,total_fee,installment_available,
				installment_type,no_of_installments,c.`last_update_ts` 
				FROM `course` c inner join `course_fee_mapping` cfm on 
				c.`course_id`=cfm.`course_id` WHERE c.`subject_id`=%s and c.`course_id`>%s 
				order by c.`course_id` limit %s""")
				qdata = (subject_id,limit)

			cursor.execute(qry,qdata)
			cursor.execute("""SELECT c.`course_id`,c.`course_name`,c.`hours`,
				c.`course_status`,c.`course_image`,board,class,
				is_paid_course,total_fee,installment_available,
				installment_type,no_of_installments,c.`last_update_ts` 
				FROM `course` c inner join `course_fee_mapping` cfm on 
				c.`course_id`=cfm.`course_id` WHERE c.`subject_id`=%s and c.`course_id`>%s 
	        	order by c.`course_id` limit %s""",(subject_id,start,limit))
			course_dtls = cursor.fetchall()

			for x in course_dtls:
				x['last_update_ts'] = x['last_update_ts'].isoformat()
				cursor.execute("""SELECT count(`module_id`) as 'count' FROM `module` WHERE `course_id` = %s""",(x['course_id']))
				x['module_count'] = cursor.fetchone().get('count')

		page_next = page + 1

		if cur_count < total_count:
			next_url = '?start={}&limit={}&page={}'.format(course_dtls[-1].get('course_id'),limit,page_next)
		else:
			next_url = ''

		return ({"attributes": {"status_desc": "Courses By Subject Id Details.",
									"status": "success",
									"total":total_count,
									"next":next_url
									},
					"responseList": course_dtls}), status.HTTP_200_OK

#--------------------------Get Course Paginated With Filter---------------------#

#--------------------------Get Subject Details----------------------#
#date-02-08-21
@name_space.route("/GetSubjectDtlsBySubjectId/<int:subject_id>")
class GetSubjectDtlsBySubjectId(Resource):
	def get(self, subject_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		cursor.execute("""SELECT * FROM `subject` WHERE `subject_id` = %s""",(subject_id))

		data = cursor.fetchone()

		if data:
			data['last_update_ts'] = data['last_update_ts'].isoformat()
		

		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Subject Details",
	    				"status": "success"
	    				},
	    				"responseList":data}), status.HTTP_200_OK


#--------------------------Get Subject Details----------------------#

#date 03-08-21
#--------------------------Get Course Details-----------------------#

@name_space.route("/GetCourseDtlsByCourseId/<int:course_id>",
	doc={'params':{'student_id':'student_id'}})
class GetCourseDtlsByCourseId(Resource):
	def get(self,course_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		conn = connect_lab_lang1()
		cur = conn.cursor()
		student_id = int(request.args.get('student_id',0))

		cursor.execute("""SELECT c.`course_id`,c.`subject_id`,c.`topic_id`,c.`subtopic_id`,c.`course_name`,c.`hours`,
			c.`category_id`,s.`subject_name`,t.`topic_name`,st.`subtopic_name`,c.`course_image`,c.`course_video`,c.`course_desc`,
			c.`course_status`,c.`board`,c.`class`,cfm.`is_paid_course`,cfm.`total_fee`,cfm.`installment_available`,
			cfm.`installment_type`,cfm.`no_of_installments`,c.`last_update_ts` FROM `course` c INNER JOIN `subject` s ON c.`subject_id` = s.`subject_id`
			 INNER JOIN `topic` t ON c.`topic_id` = t.`topic_id` INNER JOIN `subtopic` st ON c.`subtopic_id` = st.`subtopic_id` INNER JOIN
			`course_fee_mapping` cfm ON c.`course_id` = cfm.`course_id` WHERE c.`course_id` = %s""",(course_id))

		data = cursor.fetchone()

		if data:
			data['last_update_ts'] = data['last_update_ts'].isoformat()

			cur.execute("""SELECT `Board_ID` FROM `board` WHERE 
				`Board_Desc`=%s""",(data['board']))
			boardid = cur.fetchone()
			if boardid:
				data['board_id'] = boardid['Board_ID']
			else:
				data['board_id'] = 0
				
			cursor.execute("""SELECT count(`module_id`) as 'count' FROM `module` WHERE `course_id` = %s""",(data['course_id']))
			data['module_count'] = cursor.fetchone().get('count')

			cursor.execute("""SELECT count(`content_id`) as 'count' FROM `course_content` WHERE `course_id` = %s""",(data['course_id']))
			data['content_count'] = cursor.fetchone().get('count')

			cursor.execute("""SELECT count(`section_id`) as 'count' FROM `section` WHERE `course_id` = %s""",(data['course_id']))
			data['section_count'] = cursor.fetchone().get('count')

			if student_id != 0:
				cursor.execute("""SELECT `favourite_course_id` FROM `student_favourite_courses` WHERE `course_id` = %s AND `student_id` = %s""",(course_id,student_id))
				if cursor.fetchone():
					data['favourite'] = "y"
				else:
					data['favourite'] = "n"

			#static data
			data['rating'] = "4.4"
		

		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Course Details",
	    				"status": "success"
	    				},
	    				"responseList":data}), status.HTTP_200_OK

#--------------------------Get Course Details-----------------------#

#date - 03-08-21
#---------------------------Update Course---------------------------#
@name_space.route("/UpdateCourse")
class UpdateCourse(Resource):
	@api.expect(update_course_model)
	def put(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		details = request.get_json()

		update_query = ("""UPDATE `course` SET `course_name` = %s,`hours`=%s,`course_desc` = %s,`course_image` = %s,
			`course_video` = %s,`last_update_id` = %s WHERE `course_id` = %s""")
		data = (details['course_name'],details['hours'],details['course_desc'],details['course_image'],details['course_video'],
			details['teacher_id'],details['course_id'])

		cursor.execute(update_query,data)

		connection.commit()
		cursor.close()
		
		return ({"attributes": {
	    				"status_desc": "Update Course Details",
	    				"status": "success"
	    				},
	    				"responseList":"Updated successfully"}), status.HTTP_200_OK

#---------------------------Update Course---------------------------#

#date-03-08-21
#---------------------------Update Course Status--------------------#

@name_space.route("/UpdateCourseStatus")
class UpdateCourseStatus(Resource):
	@api.expect(update_course_model_status)
	def put(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		details = request.get_json()

		cursor.execute("""UPDATE `course` SET `course_status` = %s WHERE `course_id` = %s""",(details['course_status'],details['course_id']))

		connection.commit()
		cursor.close()
		
		return ({"attributes": {
	    				"status_desc": "Course Status Details",
	    				"status": "success"
	    				},
	    				"responseList":"Status Updated successfully"}), status.HTTP_200_OK

#---------------------------Update Course Status--------------------#

#date-04-08-21
#---------------------------Create Course Content-------------------#

@name_space.route("/CreateCourseContent")
class CreateCourseContent(Resource):
	@api.expect(create_content_model)
	def post(self):

		connection = connect_elsalibrary()
		cursor = connection.cursor()		
		details = request.get_json()

		section_id = details['section_id']
		module_id = details['module_id']
		course_id = details['course_id']
		teacher_id = details['teacher_id']
		institution_id = details['institution_id']
		content_name = details['content_name']
		content_path = details['content_path']
		content_type = details['content_type']
		content_length = details['content_length']
		last_update_id = teacher_id

		insertdata = cursor.execute("""INSERT INTO `course_content` (`section_id`,`module_id`,`course_id`,
			`teacher_id`,`institution_id`,`content_name`,`content_path`,`content_type`,`content_length`,`last_update_id`) 
			VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(section_id,module_id,course_id,teacher_id,
				institution_id,content_name,content_path,content_type,content_length,last_update_id))

		if insertdata:
			msg = "Content Added"
			content_id = cursor.lastrowid
		else:
			msg = "Content Not Added"
			content_id = 0

		return ({"attributes": {
	    				"status_desc": "Content Details.",
	    				"status": "success",
	    				"msg":msg
	    				},
	    				"responseList":content_id}), status.HTTP_200_OK

#---------------------------Create Course Content-------------------#

#date-04-08-21
#-----------------------Get Contents By Section Id------------------#
@name_space.route("/GetContentsBySectionId/<int:section_id>")
class GetContentsBySectionId(Resource):
	def get(self,section_id):
		
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		cursor.execute("""SELECT `content_id`,`section_id`,`module_id`,`course_id`,`content_name`,`content_path`,`content_type`,
			`content_length`,`last_update_ts` FROM `course_content` WHERE `section_id` = %s""",(section_id))

		data = cursor.fetchall()

		for x in data:
			x['last_update_ts'] = x['last_update_ts'].isoformat()

		return ({"attributes": {
	    				"status_desc": "Content Details.",
	    				"status": "success"
	    				},
	    				"responseList":data}), status.HTTP_200_OK

#-----------------------Get Contents By Section Id------------------#

#date-04-08-21
#-----------------------Module Details By Module Id-----------------#

@name_space.route("/GetModuleDetailsByModuleId/<int:module_id>")
class GetModuleDetailsByModuleId(Resource):
	def get(self,module_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		cursor.execute("""SELECT `module_id`,`module_name`,`module_desc`,`content_path`,`last_update_ts` FROM `module` WHERE `module_id` = %s""",(module_id))
		data = cursor.fetchone()

		if data:
			data['last_update_ts'] = data['last_update_ts'].isoformat()

		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Module Details.",
	    				"status": "success"
	    				},
	    				"responseList":data}), status.HTTP_200_OK


#-----------------------Module Details By Module Id-----------------#

#-------------------Add Class----------------------#

@name_space.route("/AddClassInBoard")
class AddClassInBoard(Resource):
	@api.expect(add_class_model)
	def post(self):
		connection = connect_logindb()
		cursor = connection.cursor()
		details = request.get_json()

		classdata = cursor.execute("""INSERT INTO `institution_class`(`board_id`,
			`institution_id`,`class_name`) VALUES(%s,%s,%s)""",
			(details['board_id'],details['institution_id'],details['class_name']))

		if classdata:
			msg = "Added"
		else:
			msg = "Not Added"

		connection.commit()
		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Class Details.",
	    				"status": "success",
	    				"msg": msg
	    				},
	    		"responseList":details}), status.HTTP_200_OK
#-------------------Add Class----------------------#

#-------------------Add Board----------------------#
@name_space.route("/AddBoard")
class AddBoardInInstitution(Resource):
	@api.expect(add_board_model)
	def post(self):
		connection = connect_logindb()
		cursor = connection.cursor()
		details = request.get_json()

		classdata = cursor.execute("""INSERT INTO `institution_board_dtls`(institution_id,
			`board_name`) 
			VALUES(%s,%s)""",(details['institution_id'],details['board_name']))

		if classdata:
			msg = "Added"
		else:
			msg = "Not Added"

		connection.commit()
		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Board Details.",
	    				"status": "success",
	    				"msg": msg
	    				},
	    		"responseList":details }), status.HTTP_200_OK
		
#-------------------Add Board----------------------#

#-------------------Get Boards----------------------#
@name_space.route("/GetBoards")
class GetBoards(Resource):
	def get(self):
		connection = connect_lab_lang1()
		cursor = connection.cursor()

		cursor.execute("""SELECT `Board_ID`as board_id,`Board_Desc`
			as board_name,Last_update_Ts FROM `board`""")
		boards = cursor.fetchall()

		if boards == ():
			boards = []
		else:
			for x in boards:
				x['Last_update_Ts'] = x['Last_update_Ts'].isoformat()

		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Board Details.",
	    				"status": "success"
	    				},
				"responseList":boards}), status.HTTP_200_OK
#-------------------Get Boards----------------------#

#-------------------Get Classes----------------------#
@name_space.route("/GetClassByBoardIdInstitutionId/<int:board_id>/<int:institution_id>")
class GetClassByBoardIdInstitutionId(Resource):
	def get(self,board_id,institution_id):
		connection = connect_logindb()
		cursor = connection.cursor()

		conn = connect_lab_lang1()
		cur = conn.cursor()

		cursor.execute("""SELECT * FROM `institution_class` 
			WHERE `board_id`=%s and `institution_id`=%s""",
			(board_id,institution_id))
		classList = cursor.fetchall()

		if classList == ():
			classList = []
		else:
			for x in classList:
				x['last_update_ts'] = x['last_update_ts'].isoformat()

				cur.execute("""SELECT `Board_Desc` FROM `board` WHERE 
					`Board_ID`=%s""",board_id)
				boardname = cur.fetchone()

				x['board_name'] = boardname['Board_Desc']
		
		cur.close()
		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Class Details.",
	    				"status": "success"
	    				},
				"responseList":classList}), status.HTTP_200_OK

#-------------------Get Classes----------------------#

#---------------getRecommendedCourseBySubjectIdStudentIdSortedByFee---------------#

@name_space.route("/getRecommendedCourseBySubjectIdStudentIdSortedByFee/<int:subject_id>/<string:board>/<string:_class>/<int:student_id>",
	doc={'params':{'category_id':'category_id'}})
class getRecommendedCourseBySubjectIdSortedByFee(Resource):
	def get(self,subject_id,board,_class,student_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		category_id = int(request.args.get('category_id',0))

		if category_id == 0 or category_id == 1:
			course_query = ("""SELECT c.`course_id`,c.`category_id`,c.`course_image`,c.`course_name`,c.`hours`,c.`board`,c.`class`,cfm.`fee_id`,
			cfm.`is_paid_course`,cfm.`total_fee`,cfm.`installment_available`,cfm.`installment_type`
			,cfm.`no_of_installments` FROM `course` c INNER JOIN `course_fee_mapping` cfm ON c.`course_id` = cfm.`course_id` 
			WHERE c.`subject_id` = %s AND c.`board` = %s AND c.`class` = %s and c.`course_status` = 'public' AND c.`course_id` 
			NOT IN (SELECT scm.`course_id` FROM `student_course_master` scm WHERE scm.`student_id` = %s)
			 ORDER BY cfm.`total_fee` ASC""")

			cursor.execute(course_query,(subject_id,board,_class,student_id))
		else:
			course_query = ("""SELECT c.`course_id`,c.`category_id`,c.`course_image`,c.`course_name`,c.`hours`,c.`board`,c.`class`,cfm.`fee_id`,
			cfm.`is_paid_course`,cfm.`total_fee`,cfm.`installment_available`,cfm.`installment_type`
			,cfm.`no_of_installments` FROM `course` c INNER JOIN `course_fee_mapping` cfm ON c.`course_id` = cfm.`course_id` 
			WHERE c.`subject_id` = %s AND c.`category_id` = %s AND c.`course_status` = 'public' AND c.`course_id` 
			NOT IN (SELECT scm.`course_id` FROM `student_course_master` scm WHERE scm.`student_id` = %s)
			 ORDER BY cfm.`total_fee` ASC""")

			cursor.execute(course_query,(subject_id,category_id,student_id))
		
		data = cursor.fetchall()

		for x in data:
			cursor.execute("""SELECT count(`module_id`) as 'count' FROM `module` WHERE `course_id` = %s""",(x['course_id']))
			x['module_count'] = cursor.fetchone().get('count')

			cursor.execute("""SELECT count(`content_id`) as 'count' FROM `course_content` WHERE `course_id` = %s""",(x['course_id']))
			x['content_count'] = cursor.fetchone().get('count')

			cursor.execute("""SELECT count(`section_id`) as 'count' FROM `section` WHERE `course_id` = %s""",(x['course_id']))
			x['section_count'] = cursor.fetchone().get('count')

			#static data
			x['rating'] = "4.4"

		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Course Details.",
	    				"status": "success"
	    				},
	    				"responseList":data}), status.HTTP_200_OK

#---------------getRecommendedCourseBySubjectIdStudentIdSortedByFee---------------#

#----------------------Remove-Course-From-Favourite---------------------#

@name_space.route("/removeCourseFromFavourite/<int:course_id>")
class removeCourseFromFavourite(Resource):
	def delete(self, course_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		
		course_delete_query = ("""DELETE FROM `student_favourite_courses` WHERE `favourite_course_id` = %s """)
		delData = (course_id)
		
		cursor.execute(course_delete_query,delData)
		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Remove Favourite Course",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Remove-Course-From-Favourite---------------------#

#---------------------------Update Course Board Class Status--------------------#

@name_space.route("/UpdateCourseBoardClass")
class UpdateCourseStatus(Resource):
	@api.expect(update_course_board_model)
	def put(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		details = request.get_json()

		cursor.execute("""UPDATE `course` SET `board` = %s, `class` = %s, `last_update_id` = %s WHERE `course_id` = %s""",
			(details['board'],details['class'],details['teacher_id'],details['course_id']))

		connection.commit()
		cursor.close()
		
		return ({"attributes": {
	    				"status_desc": "Course Status Details",
	    				"status": "success"
	    				},
	    				"responseList":"Status Updated successfully"}), status.HTTP_200_OK

#---------------------------Update Course Board Class Status--------------------#
