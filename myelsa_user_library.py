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

myelsa_user_library = Blueprint('myelsa_user_library_api', __name__)
api = Api(myelsa_user_library,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('MyelsaUserLibrary',description='Myelsa User Library')

base_url = "http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/"

#----------------------------------------------------#
add_content = api.model('add_content',{
	"content_name":fields.String(),
	"content_filepath":fields.String(),
	"content_filetype":fields.String(),
	"subject_id":fields.Integer(),
	"topic_id":fields.Integer(),
	"teacher_id":fields.Integer(),
	"institution_id":fields.Integer()
	})

content_track = api.model('add_content',{
	"user_id":fields.Integer(),
	"content_id":fields.Integer(),
	"institution_id":fields.Integer()
	})

section_track = api.model('section_track',{
	"user_id":fields.Integer(),
	"section_id":fields.Integer(),
	"institution_id":fields.Integer()
	})

module_track = api.model('module_track',{
	"user_id":fields.Integer(),
	"module_id":fields.Integer(),
	"institution_id":fields.Integer()
	})

paid_course = api.model('paid_course', {
	"total_fee":fields.Float(),
	"installment_available":fields.String(),
	"installment_type":fields.String(),
	"course_id":fields.Integer(),
	"no_of_installments":fields.Integer(),
	"is_paid_course":fields.String()
	})

course_paymentdtls = api.model('course_paymentdtls', {
	"student_id":fields.Integer(),
	"course_id":fields.Integer(),
	"payment_mode":fields.String(),
	"payment_type":fields.String(),
	"no_of_installment":fields.Integer(),
	"institution_id":fields.Integer(),
	"teacher_id":fields.Integer(),
	"actual_amount":fields.String()
	})

razorpay_model = api.model('razorpay_model', {
	"amount":fields.String(),
	"purpose":fields.String(),
	"user_id":fields.Integer(),
	"course_id":fields.Integer(),
	"coursefee_id":fields.Integer(),
	"teacher_id":fields.Integer(),
	"institution_id":fields.Integer(),
	"payment_status":fields.String(),
	"payment_id":fields.String(),
	"remarks":fields.String()
	})

coursecontent_track = api.model('coursecontent_track',{
	"user_id":fields.Integer(),
	"course_id":fields.Integer(),
	"course_content_id":fields.Integer(),
	"institution_id":fields.Integer()
	})

add_favcourse = api.model('add_favcourse', {
	"student_id":fields.Integer(),
	"course_id":fields.Integer(),
	"institution_id":fields.Integer()
	})
#----------------------------------------------------#
@name_space.route("/AddContent")
class AddContent(Resource):
	@api.expect(add_content)
	def post(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()
		
		content_name = details.get('content_name')
		content_filepath = details.get('content_filepath')
		content_filetype = details.get('content_filetype')
		teacher_id = details.get('teacher_id')
		topic_id = details.get('topic_id')
		subject_id = details.get('subject_id')
		institution_id = details.get('institution_id')
		
		content_query = ("""INSERT INTO `content_library`(`content_name`,
			`content_filepath`,`content_filetype`,`topic_id`,
			`subject_id`,`teacher_id`,`institution_id`)
			VALUES(%s,%s,%s,%s,%s,%s,%s)""")
		content_data = (content_name,content_filepath,content_filetype,
			topic_id,subject_id,teacher_id,institution_id)
		contentdata = cursor.execute(content_query,content_data)

		if contentdata:
			content_id = cursor.lastrowid
			details['content_id'] = content_id
			msg = "Added"
			
		else:
			msg = "Not Added"

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Content Details",
                                "status": "success",
                                "msg": msg
	                                },
	             "responseList": details}), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/getContentDtlsBySubjectId/<int:subject_id>",
	doc={'params':{'start':'topicId','limit':'limit','page':'pageno'}})
class getContentDtlsBySubjectId(Resource):
    def get(self,subject_id):
        connection = connect_elsalibrary()
        cursor = connection.cursor()

        loginconnection = connect_logindb()
        logincursor = loginconnection.cursor()
        
        start=int(request.args.get('start', 0))
        limit=int(request.args.get('limit', 10))
        page=int(request.args.get('page', 1))

        previous_url = ''
        next_url = ''

        cursor.execute("""SELECT count(`topic_id`)as 'tpccount' FROM `topic`
        	where `subject_id`=%s""",(subject_id))
        tpccountDtls = cursor.fetchone()

        total_tpccount = tpccountDtls.get('tpccount')
        cur_count = int(page) * int(limit)
        
        if start == 0:
        	previous_url = ''

        	cursor.execute("""SELECT `topic_id`,`topic_name` FROM `topic` 
	        	where `subject_id`=%s order by topic_id Asc limit %s""",
	        	(subject_id,limit))
	        topicList = cursor.fetchall()
	        for tid in range(len(topicList)):

		        cursor.execute("""SELECT `content_id`,`content_name`,
		        	`content_filepath`,`content_filetype`,cl.`topic_id`,
		        	cl.`subject_id`,`teacher_id`,cl.`institution_id`,
		        	cl.`last_update_ts` FROM `content_library` cl 
		        	INNER JOIN `topic` top on cl.`topic_id`= top.`topic_id` 
		        	INNER JOIN `subject` sub on cl.`subject_id`=sub.`subject_id` 
		        	where cl.`topic_id`=%s order by content_id Asc""",
		        	(topicList[tid]['topic_id']))
		        content_dtls = cursor.fetchall()

		        for j in range(len(content_dtls)):
		        	if content_dtls[j]['last_update_ts'] == '0000-00-00':
		        		content_dtls[j]['last_update_ts'] = '0000-00-00'
		        		
		        		topicList[tid]['content_dtls'] = content_dtls
		        	else:
			        	content_dtls[j]['last_update_ts'] = content_dtls[j]['last_update_ts'].isoformat()
			        	
			        	topicList[tid]['content_dtls'] = content_dtls

				        logincursor.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`)as 
				        	teachername FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID`
				        	=%s""",(content_dtls[j]['teacher_id']))
			        	teacherdtls = logincursor.fetchone()
			        	if teacherdtls:
				        	content_dtls[j]['teachername'] = teacherdtls['teachername']

				        else:
				        	content_dtls[j]['teachername']= ''
        else:
        	cursor.execute("""SELECT `topic_id`,`topic_name` FROM `topic` 
	        	where `subject_id`=%s and `topic_id`>%s order by 
	        	topic_id Asc limit %s""",(subject_id,start,limit))
	        topicList = cursor.fetchall()

	        for tid in range(len(topicList)):

	        	cursor.execute("""SELECT `content_id`,`content_name`,
		        	`content_filepath`,`content_filetype`,cl.`topic_id`,
		        	cl.`subject_id`,`teacher_id`,cl.`institution_id`,
		        	cl.`last_update_ts` FROM `content_library` cl 
		        	INNER JOIN `topic` top on cl.`topic_id`= top.`topic_id` 
		        	INNER JOIN `subject` sub on cl.`subject_id`=sub.`subject_id` 
		        	where cl.`topic_id`=%s order by content_id Asc""",
		        	(topicList[tid]['topic_id']))
		        content_dtls = cursor.fetchall()
		        
		        for j in range(len(content_dtls)):
		        	if content_dtls[j]['last_update_ts'] == '0000-00-00':
		        		content_dtls[j]['last_update_ts'] = '0000-00-00'
		        		
		        		topicList[tid]['content_dtls'] = content_dtls
		        	else:
			        	content_dtls[j]['last_update_ts'] = content_dtls[j]['last_update_ts'].isoformat()
			        	
			        	topicList[tid]['content_dtls'] = content_dtls

				        logincursor.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`)as 
				        	teachername FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID`
				        	=%s""",(content_dtls[j]['teacher_id']))
			        	teacherdtls = logincursor.fetchone()
			        	if teacherdtls:
				        	content_dtls[j]['teachername'] = teacherdtls['teachername']

				        else:
				        	content_dtls[j]['teachername']= ''

        page_next = page + 1
        if cur_count < total_tpccount:
        	next_url = '?start={}&limit={}&page={}'.format(topicList[-1].get('topic_id'),limit,page_next)
        else:
        	next_url = ''
		
        connection.commit()
        cursor.close()
        loginconnection.commit()
        logincursor.close()

        return ({"attributes": {"status_desc": "Content Details.",
									"status": "success",
									"totalTopic":total_tpccount,
									"previous":previous_url,
									"next":next_url
									},
					"responseList": topicList}), status.HTTP_200_OK	

#--------------------------------------------------------#
@name_space.route("/UserContentTracking")
class UserContentTracking(Resource):
	@api.expect(content_track)
	def post(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()
		
		user_id = details.get('user_id')
		content_id = details.get('content_id')
		institution_id = details.get('institution_id')
		
		content_query = ("""INSERT INTO `user_content_tracking`(`user_id`,
			`content_id`,`institution_id`,`last_update_id`) VALUES(%s,%s,
			%s,%s)""")
		content_data = (user_id,content_id,institution_id,user_id)
		contentdata = cursor.execute(content_query,content_data)

		if contentdata:
			content_tracking_id = cursor.lastrowid
			details['user_tracking_id'] = content_tracking_id
			msg = "Added"
			
		else:
			msg = "Not Added"

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Content Tracking Details",
                                "status": "success",
                                "msg": msg
	                                },
	             "responseList": details}), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/UserSectionTracking")
class UserSectionTracking(Resource):
	@api.expect(section_track)
	def post(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()
		
		user_id = details.get('user_id')
		section_id = details.get('section_id')
		institution_id = details.get('institution_id')
		
		content_query = ("""INSERT INTO `user_section_tracking`(`user_id`,
			`section_id`,`institution_id`,`last_update_id`) VALUES(%s,%s,
			%s,%s)""")
		content_data = (user_id,section_id,institution_id,user_id)
		contentdata = cursor.execute(content_query,content_data)

		if contentdata:
			section_tracking_id = cursor.lastrowid
			details['section_tracking_id'] = section_tracking_id
			msg = "Added"
			
		else:
			msg = "Not Added"

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Section Tracking Details",
                                "status": "success",
                                "msg": msg
	                                },
	             "responseList": details}), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/UserModuleTracking")
class UserModuleTracking(Resource):
	@api.expect(module_track)
	def post(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()
		
		user_id = details.get('user_id')
		module_id = details.get('module_id')
		institution_id = details.get('institution_id')
		
		content_query = ("""INSERT INTO `user_module_tracking`(`user_id`,
			`module_id`,`institution_id`,`last_update_id`) VALUES(%s,%s,
			%s,%s)""")
		content_data = (user_id,module_id,institution_id,user_id)
		contentdata = cursor.execute(content_query,content_data)

		if contentdata:
			module_tracking_id = cursor.lastrowid
			details['module_tracking_id'] = module_tracking_id
			msg = "Added"
			
		else:
			msg = "Not Added"

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Module Tracking Details",
                                "status": "success",
                                "msg": msg
	                                },
	             "responseList": details}), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/ProgressReportByUserIdInstitutionId/<int:user_id>/<int:institution_id>")
class ProgressReportByUserIdInstitutionId(Resource):
	def get(self, user_id,institution_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		cursor.execute("""SELECT count(`module_id`)as total FROM `module` 
			where `institution_id`=%s""",(institution_id))

		totalModule = cursor.fetchone()
		if totalModule:
			totalmodule = totalModule['total']
		else:
			totalmodule = 0

		cursor.execute("""SELECT COUNT(DISTINCT(`module_id`))as total FROM 
			`user_module_tracking` WHERE `user_id`=%s and 
			`institution_id`=%s""",(user_id,institution_id))

		completedModule = cursor.fetchone()
		if completedModule:
			completedmodule = completedModule['total']
		else:
			completedmodule = 0

		cursor.execute("""SELECT count(`section_id`)as total FROM `section` 
			where `institution_id`=%s""",(institution_id))

		totalSection = cursor.fetchone()
		if totalSection:
			totalsection = totalSection['total']
		else:
			totalsection = 0

		cursor.execute("""SELECT COUNT(DISTINCT(`section_id`))as total FROM 
			`user_section_tracking` WHERE `user_id`=%s and 
			`institution_id`=%s""",(user_id,institution_id))

		completedSection = cursor.fetchone()
		if completedSection:
			completedsection = completedSection['total']
		else:
			completedsection = 0

		cursor.execute("""SELECT count(`content_id`)as total FROM `content_library` 
			where `institution_id`=%s""",(institution_id))

		totalContent = cursor.fetchone()
		if totalContent:
			totalcontent = totalContent['total']
		else:
			totalcontent = 0

		cursor.execute("""SELECT COUNT(DISTINCT(`content_id`))as total FROM 
			`user_content_tracking` WHERE `user_id`=%s and 
			`institution_id`=%s""",(user_id,institution_id))

		completedContent = cursor.fetchone()
		if completedContent:
			completedcontent = completedContent['total']
		else:
			completedcontent = 0
		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Progress Report",
	    				"status": "success"
	    				},
	    				"responseList":{
	    								"totalmodule": totalmodule,
	    								"completedmodule": completedmodule,
	    								"totalsection": totalsection,
	    								"completedsection": completedsection,
	    								"totalcontent": totalcontent,
	    								"completedcontent": completedcontent,
	    								}
	    				}), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/UpdateCourseFee")
class UpdateCourseFee(Resource):
	@api.expect(paid_course)
	def put(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()
		
		Total_fee = details.get('total_fee')
		Installment_available = details.get('installment_available')
		course_id = details.get('course_id')
		Is_paid_course = details.get('is_paid_course')
		No_of_installments = details.get('no_of_installments')
		Installment_type = details.get('installment_type')
		
		cursor.execute("""SELECT `is_paid_course`,`total_fee`,
			`installment_available`,`installment_type`,
			no_of_installments FROM `course_fee_mapping` 
			WHERE `course_id`=%s""",(course_id))
		coursedtls = cursor.fetchone()

		if coursedtls:
			if not Is_paid_course:
				Is_paid_course = coursedtls.get('is_paid_course')
				
			if not Total_fee:
				Total_fee = coursedtls.get('total_fee')
				
			if not Installment_available:
				Installment_available = coursedtls.get('installment_available')
				
			if not Installment_type:
				Installment_type = coursedtls.get('installment_type')
				
			if not No_of_installments:
				No_of_installments = coursedtls.get('no_of_installments')
				
		if Is_paid_course == 'n':
			Total_fee = 0      

		updated_query = ("""UPDATE `course_fee_mapping` SET `is_paid_course`=%s,
			`total_fee`=%s,`installment_available`=%s,`installment_type`=%s,
			`no_of_installments`=%s where `course_id`=%s""")

		updated_data = cursor.execute(updated_query,(Is_paid_course,
			Total_fee,Installment_available,Installment_type,
			No_of_installments,course_id))

		if updated_data:
			msg = "Updated"
			
		else:
			msg = "Not Updated"

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Paid Course Details",
                                "status": "success",
                                "msg": msg
	                                },
	             "responseList": details}), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/GetModuleListByCourseIdStudentId/<int:course_id>/<int:student_id>")
class GetModuleListByCourseIdStudentId(Resource):
	def get(self,course_id,student_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = []

		cursor.execute("""SELECT `module_id`,`module_name` FROM 
			`module` WHERE `course_id`=%s""",(course_id))

		moduledata = cursor.fetchall()
		if moduledata == ():
			moduledata = []

		else:
			for x in moduledata:
				cursor.execute("""SELECT COUNT(`assignment_id`) as 'total' FROM 
					`course_assignment_mapping` WHERE `module_id`=%s""",(x['module_id']))

				assignmentdata = cursor.fetchone()
				if assignmentdata:
					x['totalassignment'] = assignmentdata.get('total')
				else:
					x['totalassignment'] = 0

				cursor.execute("""SELECT COUNT(`liveclass_id`) as 'total' FROM `course_liveclass_mapping` 
					WHERE `module_id`=%s""",(x['module_id']))
				
				livesectiondata = cursor.fetchone()
				if livesectiondata:
					x['totalliveclass'] = livesectiondata.get('total')
				else:
					x['totalliveclass'] = 0

				cursor.execute("""SELECT COUNT(`exam_id`) as 'total' FROM `exam_master` WHERE `module_id` = %s""",(x['module_id']))
				examdata = cursor.fetchone()

				if examdata:
					x['totalexam'] = examdata['total']
				else:
					x['totalexam'] = 0

				cursor.execute("""SELECT count(section_id)as total 
					FROM `section` WHERE `module_id`=%s""",
					(x['module_id']))

				countsection = cursor.fetchone()
				if countsection:
					x['totalsection'] = countsection['total']
				else:
					x['totalsection'] = 0

				cursor.execute("""SELECT count(`section_id`)as total FROM `section` 
					where `section_id` not in(SELECT `section_id` 
					FROM `course_content` where `course_id`=%s) and 
					`course_id`=%s and `module_id`=%s""",
					(course_id,course_id,x['module_id']))

				checksections = cursor.fetchone()
				detail = []
				if checksections:
					cursor.execute("""SELECT `section_id` FROM `course_content` where 
						`course_id`=%s and `module_id`=%s""",(course_id,x['module_id']))

					contentsections = cursor.fetchall()
					if contentsections == ():
						x['completedsection'] = 0
					else:
						for sid in contentsections:
							
							cursor.execute("""SELECT count(`content_id`)as total FROM `course_content` 
								where `content_id` not in(SELECT `course_content_id` FROM 
								`user_course_content_tracking` where `user_id`=%s and 
								`course_id`=%s) and `course_id`=%s and `section_id`=%s""",
								(student_id,course_id,course_id,sid['section_id']))

							notexistcontent = cursor.fetchone()
							if notexistcontent['total'] != 0:
								cursor.execute("""SELECT section_id FROM `course_content` 
									WHERE `module_id`=%s""",(x['module_id']))

								sectionData = cursor.fetchall()
								detail = []
								if sectionData:
									for secid in sectionData:
										detail.append(secid['section_id'])
									detail = tuple(detail)
									
									cursor.execute("""SELECT count(distinct(`section_id`))as total FROM 
										`user_section_tracking` where `user_id`=%s and 
										`section_id` in %s""",(student_id,detail))

									completedsecdata = cursor.fetchone()
									if completedsecdata:
										x['completedsection'] = completedsecdata['total'] + checksections['total'] - notexistcontent['total']
									else:
										x['completedsection'] = 0
								else:
									x['completedsection'] = 0
							else:
								cursor.execute("""SELECT section_id FROM `course_content` 
									WHERE `module_id`=%s""",(x['module_id']))

								sectionData = cursor.fetchall()
								detail = []
								if sectionData:
									for secid in sectionData:
										detail.append(secid['section_id'])
									detail = tuple(detail)
									
									cursor.execute("""SELECT count(distinct(`section_id`))as total FROM 
										`user_section_tracking` where `user_id`=%s and 
										`section_id` in %s""",(student_id,detail))

									completedsecdata = cursor.fetchone()
									if completedsecdata:
										x['completedsection'] = completedsecdata['total'] + checksections['total']
									else:
										x['completedsection'] = 0

				else:
					cursor.execute("""SELECT `section_id` FROM `course_content` where 
						`course_id`=%s and `module_id`=%s""",(course_id,x['module_id']))

					contentsections = cursor.fetchall()
					if contentsections == ():
						x['completedsection'] = 0
					else:
						for sid in contentsections:

							cursor.execute("""SELECT count(`content_id`)as total FROM `course_content` 
								where `content_id` not in(SELECT `course_content_id` FROM 
								`user_course_content_tracking` where `user_id`=%s and 
								`course_id`=%s) and `course_id`=%s and `section_id`=%s""",
								(student_id,course_id,course_id,sid['section_id']))

							notexistcontent = cursor.fetchone()
							if notexistcontent['total'] != 0:
								cursor.execute("""SELECT section_id FROM `course_content` 
									WHERE `module_id`=%s""",(x['module_id']))

								sectionData = cursor.fetchall()
								detail = []
								if sectionData:
									for secid in sectionData:
										detail.append(secid['section_id'])
									detail = tuple(detail)
									
									cursor.execute("""SELECT count(distinct(`section_id`))as total FROM 
										`user_section_tracking` where `user_id`=%s and 
										`section_id` in %s""",(student_id,detail))

									completedsecdata = cursor.fetchone()
									if completedsecdata:
										x['completedsection'] = completedsecdata['total'] - notexistcontent['total']
									else:
										x['completedsection'] = 0
							else:
								cursor.execute("""SELECT section_id FROM `course_content` 
									WHERE `module_id`=%s""",(x['module_id']))

								sectionData = cursor.fetchall()
								detail = []
								if sectionData:
									for secid in sectionData:
										detail.append(secid['section_id'])
									detail = tuple(detail)
									
									cursor.execute("""SELECT count(distinct(`section_id`))as total FROM 
										`user_section_tracking` where `user_id`=%s and 
										`section_id` in %s""",(student_id,detail))

									completedsecdata = cursor.fetchone()
									if completedsecdata:
										x['completedsection'] = completedsecdata['total'] + checksections['total']
									else:
										x['completedsection'] = 0
										

				details.append(x['module_id'])
			details = tuple(details)
			
			cursor.execute("""SELECT `history_tracking_id`,`module_id` 
				FROM `user_module_tracking_history` where `user_id`=%s and 
				`module_id` in %s order by `history_tracking_id` DESC limit 1""",
				(student_id,details))

			moduletrackdata = cursor.fetchone()
			
			if moduletrackdata:
				cursor.execute("""SELECT `module_name` FROM `module` WHERE 
					`module_id`=%s""",(moduletrackdata['module_id']))

				lastaccessmoduledata = cursor.fetchone()
				if lastaccessmoduledata:
					lastaccessModule = lastaccessmoduledata['module_name']
				
			else:
				lastaccessModule = ''

		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Module Details.",
	    				"status": "success",
	    				"lastaccessMoodule":lastaccessModule
	    				},
	    				"responseList":moduledata}), status.HTTP_200_OK

#-------------------------------------------------------------#
@name_space.route("/GetModuleWiseSectionContentByModuleIdStudentId/<int:module_id>/<int:student_id>")
class GetModuleWiseSectionContentByModuleIdStudentId(Resource):
	def get(self,module_id,student_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		conn = connect_lab_lang1()
		cur = conn.cursor()

		details = []
		lastaccessSection = ''

		cursor.execute("""SELECT `section_id`,`section_name` FROM 
			`section` where `module_id`=%s""",(module_id))

		Sectiondata = cursor.fetchall()
		if Sectiondata == ():
			Sectiondata = []

		else:
			for x in Sectiondata:

				cursor.execute("""SELECT `assignment_id`,`last_update_ts` FROM 
					`course_assignment_mapping` WHERE `section_id`=%s""",(x['section_id']))

				assignmentdata = cursor.fetchall()
				if assignmentdata == ():
					x['totalassignment'] = 0
				else:
					x['totalassignment'] = len(assignmentdata)

				cursor.execute("""SELECT `liveclass_id` FROM `course_liveclass_mapping` 
					WHERE `section_id`=%s""",(x['section_id']))
				
				livesectiondata = cursor.fetchall()
				if livesectiondata == ():
					x['totalliveclass'] = 0
				else:
					x['totalliveclass'] = len(livesectiondata)

				cursor.execute("""SELECT COUNT(`exam_id`) as 'total' FROM `exam_master` WHERE `section_id` = %s""",(x['section_id']))

				examdata = cursor.fetchone()
				if examdata:
					x['totalexam'] = examdata['total']
				else:
					x['totalexam'] = 0

				cursor.execute("""SELECT count(`content_id`) as count FROM 
					`course_content` WHERE `section_id`=%s""",
					(x['section_id']))

				countContent = cursor.fetchone()

				if countContent:
					x['total_content'] = countContent['count']
				else:
					x['total_content'] = 0

				cursor.execute("""SELECT `content_id`,`content_name`,
					`course_id`,`teacher_id`,`content_length`,
					`content_path`,`content_type` FROM 
					`course_content` WHERE `section_id`=%s""",
					(x['section_id']))

				contentdata = cursor.fetchall()
				detail = []
				if contentdata == ():
					x['contentList'] = []
				else:
					for conid in range(len(contentdata)):
						cursor.execute("""SELECT `user_tracking_id` FROM 
							`user_course_content_tracking` WHERE 
							`course_content_id`=%s and user_id=%s""",
							(contentdata[conid]['content_id'],student_id))

						completedData = cursor.fetchone()
						if completedData:
							contentdata[conid]['completed'] = "y"
						else:
							contentdata[conid]['completed'] = "n"

						
						detail.append(contentdata[conid]['content_id'])
					detail = tuple(detail)
					cursor.execute("""SELECT count(DISTINCT(`course_content_id`))as 'count' FROM 
						`user_course_content_tracking` WHERE 
						`course_content_id`in %s and user_id=%s""",(detail,student_id))

					countCompleted = cursor.fetchone()
					
					if countCompleted != None:
						x['completed_content'] = countCompleted['count']	
					else:
						x['completed_content'] = 0
					
					x['contentList'] = contentdata

				details.append(x['section_id'])
			details = tuple(details)
			
			if details != ():
				cursor.execute("""SELECT `history_tracking_id`,`section_id` 
					FROM `user_section_tracking_history` where `user_id`=%s and 
					`section_id` in %s order by `history_tracking_id` DESC limit 1""",
					(student_id,details))

				sectiontrackdata = cursor.fetchone()
				
				if sectiontrackdata:
					cursor.execute("""SELECT `section_id`,`section_name` FROM 
						`section` where `section_id`=%s""",(sectiontrackdata['section_id']))

					lastaccesssectiondata = cursor.fetchone()
					if lastaccesssectiondata:
						lastaccessSection = lastaccesssectiondata['section_name']
					
					else:
						lastaccessSection = ''
				else:
					lastaccessSection = ''

			else:
				lastaccessSection = ''

		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Section Content Details.",
	    				"status": "success",
				 		"lastaccessSection":lastaccessSection
	    				},
	    				"responseList":Sectiondata}), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/AddStudentCoursePaymentDetails")	
class AddStudentCoursePaymentDetails(Resource):
	@api.expect(course_paymentdtls)
	def post(self):

		connection = connect_elsalibrary()
		curlab = connection.cursor()
		details = request.get_json()

		student_id = details.get('student_id')
		course_id = details.get('course_id')
		payment_mode = details.get('payment_mode')
		payment_type = details.get('payment_type')
		no_of_installment = details.get('no_of_installment')
		institution_id = details.get('institution_id')
		teacher_id = details.get('teacher_id')
		actual_amount = details.get('actual_amount')
		curdate = datetime.now().strftime('%Y-%m-%d')

		courseFeeInsertQuery = ("""INSERT INTO `student_coursefee_mapping`(`purchase_type`,
			`student_id`, `course_id`,`payment_mode`, `payment_type`, 
			`no_of_installment`, `actual_amount`, `total_amount`,
			`purchased_on`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

		courseFeeData = ('course',student_id,course_id,payment_mode,
			payment_type,no_of_installment,actual_amount,actual_amount,
			curdate)
		
		curlab.execute(courseFeeInsertQuery,courseFeeData)

		courseFeeId = curlab.lastrowid
		details['coursefee_id'] = courseFeeId

		studentPaymentDetailsInsert = ("""INSERT INTO 
			`student_coursefee_payment_details`(`student_id`,
			`payment_amount`,`payment_duedate`,`is_pending`,
			`coursefee_id`) VALUES(%s,%s,%s,%s,%s)""")

		if no_of_installment > 1:

			installment_amount = float(actual_amount)/no_of_installment

			payment_due_date = curdate
			
			paymentDtlsData = (student_id,installment_amount,payment_due_date,'y',courseFeeId)

			coursefeeDtls = curlab.execute(studentPaymentDetailsInsert,paymentDtlsData)
			
			if coursefeeDtls:
				msg = "Added"
			else:
				msg = "Not Added"
		else:

			paymentDtlsData = (student_id,actual_amount,curdate,'n',courseFeeId)

			coursefeeDtls = curlab.execute(studentPaymentDetailsInsert,paymentDtlsData)

			if coursefeeDtls:
				msg = "Added"
			else:
				msg = "Not Added"

		connection.commit()
		curlab.close()

		return ({"attributes": {
								"status_desc": "Student Course Payment Details",
								"status": "success",
								"msg": msg
								},
			"responseList": details}), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/SubscribeCourse")
class SubscribeCourse(Resource):
	@api.expect(razorpay_model)
	def post(self):
		
		connection = connect_logindb()
		cursor = connection.cursor()

		conn = connect_elsalibrary()
		cur = conn.cursor()

		details = request.get_json()

		amount = details.get('amount')
		purpose = details.get('purpose')
		user_id = details.get('user_id')
		course_id = details.get('course_id')
		coursefee_id = details.get('coursefee_id')
		teacher_id = details.get('teacher_id') 
		institution_id = details.get('institution_id')  
		payment_status = details.get('payment_status') 
		payment_id = details.get('payment_id') 
		remarks = details.get('remarks')
		
		paymentQuery = ("""INSERT INTO `razorpay_payment_dtls`(`user_id`,
			purpose, amount,`payment_status`,payment_id,remarks) VALUES (%s,
			%s,%s,%s,%s,%s)""")
		
		paymentData = cursor.execute(paymentQuery,(user_id,
			purpose, amount,payment_status,payment_id,remarks))

		if paymentData:
			request_id = cursor.lastrowid
			details['request_id'] = request_id

			updateCourseFeePayment = ("""UPDATE `student_coursefee_payment_details` SET 
				`razor_payment_id`=%s where `coursefee_id`=%s and 
				`student_id` = %s""")
			cur.execute(updateCourseFeePayment,(payment_id,coursefee_id,user_id))

			subscribeQuery = ("""INSERT INTO `student_course_master`(`student_id`,
				`course_id`,`teacher_id`,`coursefee_id`,
				`Institution_ID`) VALUES (%s,%s,%s,%s,%s)""")

			subscribed = cur.execute(subscribeQuery,(user_id,course_id,teacher_id,
				coursefee_id,institution_id))

			if subscribed:
				msg = 'Subscribed'
			else:
				msg = 'Non Subscribed'
		else:
			msg = 'Payment Details Not Added'
		
		conn.commit()
		cur.close()	
		connection.commit()
		cursor.close()

		return ({"attributes": {
								"status_desc": "Razor Pay Payment Details",
								"status": "success",
								"msg": msg
								},
			"responseList": details}), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/GetAllNonSubsribecoursesBySubjectIdStudentId/<int:subject_id>/<int:student_id>")
class GetAllNonSubsribecoursesBySubjectIdStudentId(Resource):
	def get(self,subject_id,student_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		conn = connect_logindb()
		cur = conn.cursor()

		cursor.execute("""SELECT c.`course_id`,`subject_id`,
			`course_name`,`hours`,`course_image`,fee_id,is_paid_course,
			total_fee,installment_available, installment_type,
			no_of_installments,c.`board`,c.`class` FROM `course` c INNER join 
			`course_fee_mapping` cfm on c.`course_id`=cfm.`course_id` 
			WHERE c.`course_id` not in(SELECT `course_id` FROM 
			`student_course_master` WHERE `student_id`=%s) and 
			`subject_id`=%s and course_status ='public' order by total_fee DESC""",(student_id,subject_id))
		nonsubscribecourse = cursor.fetchall()
		
		if nonsubscribecourse == ():
			nonsubscribecourseData = []

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

				nonsubscribecourseData = nonsubscribecourse

		cursor.close()
		cur.close()

		return ({"attributes": {
	    				"status_desc": " All Non Subscribe Course Details.",
	    				"status": "success"
	    				},
				"responseList":nonsubscribecourseData}), status.HTTP_200_OK

#------------------------------------------------------#
@name_space.route("/GetRecommendedNonSubsribecoursesByStudentIdInstitutionId/<int:student_id>/<int:institution_id>")
class GetRecommendedNonSubsribecoursesByStudentIdInstitutionId(Resource):
	def get(self,student_id,institution_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		conn = connect_logindb()
		cur = conn.cursor()

		cur.execute("""SELECT `CLASS`,`Board` FROM `student_dtls` 
			WHERE `INSTITUTION_USER_ID_STUDENT`=%s limit 1""",(student_id))

		studentdata = cur.fetchone()
		if studentdata:
			board = studentdata['Board']
			clss = studentdata['CLASS']
		else:
			board = ''
			clss = ''

		cursor.execute("""SELECT c.`course_id`,`subject_id`,
			`course_name`,`hours`,`course_image`,fee_id,is_paid_course,
			total_fee,installment_available, installment_type,
			no_of_installments,c.`board`,c.`class` FROM `course` c INNER join 
			`course_fee_mapping` cfm on c.`course_id`=cfm.`course_id` 
			WHERE c.`course_id` not in(SELECT `course_id` FROM 
			`student_course_master` WHERE `student_id`=%s) and 
			`institution_id`=%s and `board`=%s and `class`=%s and course_status ='public'
			order by total_fee DESC""",(student_id,institution_id,board,clss))
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

#---------------------------------------------------------#
@name_space.route("/GetAllNonSubsribecoursesByPaginatedStudentIdInstitutionId/<int:student_id>/<int:institution_id>",
	doc={'params':{'start':'course_id','limit':'limit','page':'pageno'}})
class GetAllNonSubsribecoursesByPaginatedStudentIdInstitutionId(Resource):
	def get(self,student_id,institution_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		
		start = int(request.args.get('start',0))
		limit = int(request.args.get('limit',10))
		page = int(request.args.get('page',1))

		cursor.execute("""SELECT count(c.`course_id`) as 'count' FROM `course` c INNER join 
			`course_fee_mapping` cfm on c.`course_id`=cfm.`course_id` 
			WHERE c.`course_id` not in(SELECT `course_id` FROM 
			`student_course_master` WHERE `student_id`=%s) and 
			`institution_id`=%s and course_status = 'public' order by total_fee DESC""",(student_id,institution_id))
		total_count = cursor.fetchone().get('count')

		cur_count = int(page) * int(limit)

		if start==0:

			cursor.execute("""SELECT c.`course_id`,`subject_id`,
				`course_name`,`hours`,`course_image`,fee_id,is_paid_course,
				total_fee,installment_available, installment_type,
				no_of_installments,c.`board`,c.`class` FROM `course` c INNER join 
				`course_fee_mapping` cfm on c.`course_id`=cfm.`course_id` 
				WHERE c.`course_id` not in(SELECT `course_id` FROM 
				`student_course_master` WHERE `student_id`=%s) and 
				`institution_id`=%s and course_status = 'public' order by total_fee 
				DESC limit %s""",(student_id,institution_id,limit))
			nonsubscribecourse = cursor.fetchall()
			
			if nonsubscribecourse == ():
				nonsubscribecourseData = []

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

					nonsubscribecourseData = nonsubscribecourse
		else:
			cursor.execute("""SELECT c.`course_id`,`subject_id`,
				`course_name`,`hours`,`course_image`,fee_id,is_paid_course,
				total_fee,installment_available, installment_type,
				no_of_installments FROM `course` c INNER join 
				`course_fee_mapping` cfm on c.`course_id`=cfm.`course_id` 
				WHERE c.`course_id` not in(SELECT `course_id` FROM 
				`student_course_master` WHERE `student_id`=%s) and 
				`institution_id`=%s and c.`course_id`>%s and course_status = 'public'
				order by total_fee DESC limit %s""",(student_id,institution_id,start,limit))
			nonsubscribecourse = cursor.fetchall()
			
			if nonsubscribecourse == ():
				nonsubscribecourseData = []

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

					nonsubscribecourse[cid]['rating'] = "4.4"

					nonsubscribecourseData = nonsubscribecourse
		
		page_next = page + 1

		if cur_count < total_count:
			next_url = '?start={}&limit={}&page={}'.format(nonsubscribecourseData[-1].get('course_id'),limit,page_next)
		else:
			next_url = ''
		cursor.close()
		
		return ({"attributes": {
	    				"status_desc": "All Non Subscribe Course Details.",
	    				"status": "success",
						"total":total_count,
						"next":next_url
	    				},
				"responseList":nonsubscribecourseData}), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/UserCourseContentTracking")
class UserCourseContentTracking(Resource):
	@api.expect(coursecontent_track)
	def post(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()
		
		user_id = details.get('user_id')
		course_id = details.get('course_id')
		course_content_id = details.get('course_content_id')
		institution_id = details.get('institution_id')
		
		cursor.execute(("""SELECT `module_id`,`section_id` FROM `course_content` WHERE `content_id` = %s"""),
			(course_content_id))
		tempdata = cursor.fetchone()
		module_id = tempdata.get('module_id')
		section_id = tempdata.get('section_id')
		
		content_query = ("""INSERT INTO `user_course_content_tracking`(`user_id`,
			`course_content_id`,`course_id`,`module_id`,`section_id`,`institution_id`,`last_update_id`) VALUES(%s,%s,%s,%s,
			%s,%s,%s)""")
		content_data = (user_id,course_content_id,course_id,module_id,section_id,institution_id,user_id)
		contentdata = cursor.execute(content_query,content_data)

		if contentdata:
			content_tracking_id = cursor.lastrowid
			details['user_tracking_id'] = content_tracking_id
			msg = "Added"
			
			cursor.execute("""SELECT distinct(`section_id`)as section_id FROM
				`course_content` where `content_id`=%s""",(course_content_id))
			hissectiondata = cursor.fetchone()
			if hissectiondata:
				sechis_query = ("""INSERT INTO `user_section_tracking_history`(`user_id`,
					section_id,`institution_id`,`last_update_id`) VALUES(%s,%s,%s,%s)""")
				sechis_data = (user_id,hissectiondata['section_id'],institution_id,user_id)
				sechisdata = cursor.execute(sechis_query,sechis_data)
	
			cursor.execute("""SELECT distinct(`section_id`)as section_id FROM
				`course_content` where `course_id`=%s""",(course_id))
			sectiondata = cursor.fetchall()
			if sectiondata != ():
				for secid in sectiondata:
					
					cursor.execute("""SELECT `content_id` FROM `course_content` 
						where `content_id` not in(SELECT `course_content_id`
						FROM `user_course_content_tracking` WHERE `user_id`=%s) 
						and `section_id`=%s""",(user_id,secid['section_id']))
					contentdata = cursor.fetchall()
					
					if contentdata == ():
						headers = {'Content-type':'application/json', 'Accept':'application/json'}
							
						url = base_url +"myelsa_user_library/MyelsaUserLibrary/UserSectionTracking"

						sectdata = {
										"user_id": user_id,
									    "section_id": secid['section_id'],
									    "institution_id": institution_id
									}

						sectionRes = requests.post(url, data=json.dumps(sectdata), headers=headers).json()
						sres = json.dumps(sectionRes['responseList'])
						sresp = json.loads(sres)
						
			cursor.execute("""SELECT distinct(`module_id`)as module_id FROM
				`course_content` where `content_id`=%s""",(course_content_id))
			hismoduledata = cursor.fetchone()
			if hismoduledata:
				modhis_query = ("""INSERT INTO `user_module_tracking_history`(`user_id`,
					module_id,`institution_id`,`last_update_id`) VALUES(%s,%s,%s,%s)""")
				modhis_data = (user_id,hismoduledata['module_id'],institution_id,user_id)
				modhisdata = cursor.execute(modhis_query,modhis_data)

			cursor.execute("""SELECT distinct(`module_id`)as module_id FROM 
				`course_content` where `course_id`=%s""",(course_id))
			moduledata = cursor.fetchall()
			if moduledata != ():
				for mid in moduledata:
					
					cursor.execute("""SELECT `content_id` FROM `course_content` 
						where `content_id` not in(SELECT `course_content_id`
						FROM `user_course_content_tracking` WHERE `user_id`=%s) 
						and `module_id`=%s""",(user_id,mid['module_id']))
					contentdata = cursor.fetchall()
					
					if contentdata == ():
						headers = {'Content-type':'application/json', 'Accept':'application/json'}
							
						url = base_url +"myelsa_user_library/MyelsaUserLibrary/UserModuleTracking"

						moddata = {
										"user_id": user_id,
									    "module_id": mid['module_id'],
									    "institution_id": institution_id
									}

						moduleRes = requests.post(url, data=json.dumps(moddata), headers=headers).json()
						mres = json.dumps(moduleRes['responseList'])
						
						mresp = json.loads(mres)
						
		else:
			msg = "Not Added"

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Course Content Tracking Details",
                                "status": "success",
                                "msg": msg
	                                },
	             "responseList": details}), status.HTTP_200_OK

#------------------------------------------------------------#
@name_space.route("/GetAllSubsribeCoursesByStudentIdInstitutionId/<int:student_id>/<int:institution_id>")
class GetAllSubsribeCoursesByStudentIdInstitutionId(Resource):
	def get(self,student_id,institution_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT `course_id`,`course_name`,`hours`,
			`course_image` FROM `course` WHERE `course_id` in(SELECT 
			`course_id` FROM `student_course_master` WHERE `student_id`=%s) and 
			`institution_id`=%s and course_status ='public'""",(student_id,institution_id))
		subscribecourse = cursor.fetchall()

		for course in subscribecourse:
			course_id = course['course_id']

			cursor.execute("""SELECT `module_id` FROM `module` where `course_id`=%s""",(course_id))

			moduledata = cursor.fetchall()
			course['module_count'] = len(moduledata)

			course['completedmodule'] = 0

			for module in moduledata:
				cursor.execute("""SELECT `section_id` FROM `section` WHERE `module_id` = %s AND `section_id` in
				(select `section_id` from `user_section_tracking` where `user_id` = %s)""",(module['module_id'],student_id))

				secdata = cursor.fetchone()

				if secdata:
					course['completedmodule'] = course['completedmodule'] + 1
				else:
					#if did't get in tracking table the test if there is a content with this module id or not.
					#if it is not availble in course_content table too then mark it complete

					cursor.execute("""SELECT `content_id` FROM `course_content` WHERE `module_id` = %s""",(module['module_id']))
					
					condata = cursor.fetchone()

					if condata:
						pass
					else:
						course['completedmodule'] = course['completedmodule'] + 1

		cursor.close()
		
		return ({"attributes": {
	    				"status_desc": "All Subscribe Course Details.",
	    				"status": "success"
	    				},
				"responseList":subscribecourse}), status.HTTP_200_OK

#------------------------------------------------------------#
@name_space.route("/GetAllSubsribeCoursesByStudentIdInstitutionIdV2/<int:student_id>/<int:institution_id>")
class GetAllSubsribeCoursesByStudentIdInstitutionIdV2(Resource):
	def get(self,student_id,institution_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT `course_id`,`course_name`,`hours`,
			`course_image` FROM `course` WHERE `course_id` in(SELECT 
			`course_id` FROM `student_course_master` WHERE `student_id`=%s) and 
			`institution_id`=%s""",(student_id,institution_id))
		subscribecourse = cursor.fetchall()

		for course in subscribecourse:
			course_id = course['course_id']

			cursor.execute("""SELECT COUNT(`content_id`) as 'total' FROM `course_content` WHERE `course_id` = %s""",(course_id))

			temp1= cursor.fetchone()
			if temp1:
				course['total_content'] = temp1['total']
			else:
				course['total_content'] = 0


			cursor.execute("""SELECT COUNT(DISTINCT(`course_content_id`)) as 'total' FROM `user_course_content_tracking`
			 WHERE `user_id` = %s AND `course_id` = %s""",(student_id,course_id))

			temp2= cursor.fetchone()
			if temp2:
				course['completed_content'] = temp2['total']
			else:
				course['completed_content'] = 0

		cursor.close()
		
		return ({"attributes": {
	    				"status_desc": "All Subscribe Course Details.",
	    				"status": "success"
	    				},
				"responseList":subscribecourse}), status.HTTP_200_OK

#------------------------------------------------------------#		

#------------------------------------------------------------#
@name_space.route("/StudentFavouriteCourse")
class StudentFavouriteCourse(Resource):
	@api.expect(add_favcourse)
	def post(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()
		
		course_id = details.get('course_id')
		student_id = details.get('student_id')
		institution_id = details.get('institution_id')
		
		fav_query = ("""INSERT INTO `student_favourite_courses`(`course_id`,
			`student_id`,`institution_id`) VALUES(%s,%s,%s)""")
		fav_data = (course_id,student_id,institution_id)
		favdata = cursor.execute(fav_query,fav_data)

		if favdata:
			favourite_course_id = cursor.lastrowid
			details['favourite_course_id'] = favourite_course_id
			msg = "Added"
			
		else:
			msg = "Not Added"

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Favourite Course Details",
                                "status": "success",
                                "msg": msg
	                                },
	             "responseList": details}), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/GetAllFavouriteCoursesByStudentIdInstitutionId/<int:student_id>/<int:institution_id>")
class GetAllFavouriteCoursesByStudentIdInstitutionId(Resource):
	def get(self,student_id,institution_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		conn = connect_logindb()
		cur = conn.cursor()

		cursor.execute("""SELECT c.`course_id`,`subject_id`,
			`course_name`,`hours`,`course_image`,favourite_course_id,sfc.`last_update_ts`
			FROM `course` c INNER join `student_favourite_courses` sfc 
			on c.`course_id`=sfc.`course_id` WHERE sfc.`student_id`=%s and 
			sfc.`institution_id`=%s and course_status = 'public'""",(student_id,institution_id))
		favcourseData = cursor.fetchall()
		
		if favcourseData == ():
			favcourseData = []

		else:
			for cid in range(len(favcourseData)):

				favcourseData[cid]['last_update_ts'] = favcourseData[cid]['last_update_ts'].isoformat()

		cursor.close()
		cur.close()

		return ({"attributes": {
	    				"status_desc": " Student Favourite Course Details.",
	    				"status": "success"
	    				},
				"responseList":favcourseData}), status.HTTP_200_OK

#--------------------------------------------------------#

@name_space.route("/GetModuleListByCourseIdStudentIdV2/<int:course_id>/<int:student_id>")
class GetModuleListByCourseIdStudentIdV2(Resource):
	def get(self,course_id,student_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = []

		cursor.execute("""SELECT `module_id`,`module_name` FROM 
			`module` WHERE `course_id`=%s""",(course_id))

		moduledata = cursor.fetchall()
		if moduledata == ():
			moduledata = []

		else:
			for x in moduledata:
				cursor.execute("""SELECT COUNT(`assignment_id`) as 'total' FROM 
					`course_assignment_mapping` WHERE `module_id`=%s""",(x['module_id']))

				assignmentdata = cursor.fetchone()
				if assignmentdata:
					x['totalassignment'] = assignmentdata.get('total')
				else:
					x['totalassignment'] = 0

				cursor.execute("""SELECT COUNT(`liveclass_id`) as 'total' FROM `course_liveclass_mapping` 
					WHERE `module_id`=%s""",(x['module_id']))
				
				livesectiondata = cursor.fetchone()
				if livesectiondata:
					x['totalliveclass'] = livesectiondata.get('total')
				else:
					x['totalliveclass'] = 0

				cursor.execute("""SELECT COUNT(`exam_id`) as 'total' FROM `exam_master` WHERE `module_id` = %s""",(x['module_id']))
				examdata = cursor.fetchone()

				if examdata:
					x['totalexam'] = examdata['total']
				else:
					x['totalexam'] = 0
				
				cursor.execute("""SELECT COUNT(`content_id`) as 'total' FROM `course_content` WHERE `module_id` = %s""",(x['module_id']))

				temp1= cursor.fetchone()
				if temp1:
					x['total_content'] = temp1['total']
				else:
					x['total_content'] = 0


				cursor.execute("""SELECT COUNT(DISTINCT(`course_content_id`)) as 'total' FROM `user_course_content_tracking`
			 	WHERE `user_id` = %s AND `module_id` = %s""",(student_id,x['module_id']))

				temp2= cursor.fetchone()
				if temp2:
					x['completed_content'] = temp2['total']
				else:
					x['completed_content'] = 0

		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Module Details.",
	    				"status": "success",
	    				"lastaccessMoodule":""
	    				},
	    				"responseList":moduledata}), status.HTTP_200_OK

#--------------------------------GET API FOR CATEGORY TABLE-------------------------------------------#
@name_space.route("/getCategoryListByInstitutionId/<int:institution_id>")    
class GetCategoryListByInstitutionId(Resource):
    def get(self,institution_id):
        connection = connect_elsalibrary()
        cursor = connection.cursor()
        cursor.execute("""SELECT `category_id`,`category_name`,`category_image`,`teacher_id` FROM category WHERE  `institution_id` = %s""",(institution_id))
        
        category_list = cursor.fetchall()
        
        cursor.close()
        
        return ({"attributes": {
                    "status_desc": "Category List",
                    "status": "success"
                },
            "responseList":category_list}), status.HTTP_200_OK