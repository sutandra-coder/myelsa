from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from database_connections import connect_elsalibrary
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import requests
import calendar
import json
from threading import Thread
import time
import os   

app = Flask(__name__)
cors = CORS(app)

student_exam_section = Blueprint('student_exam_section_api', __name__)
api = Api(student_exam_section,  title='MyElsa API',description='StudyBreak API')
name_space = api.namespace('MyElsaNewStudentExamSection',description='MyElsa New Exam Section')

BASE_URL = "http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/"

student_exam_mapping =  api.model('student_exam_mapping', {
	"exam_id":fields.Integer(),
	"student_id":fields.Integer(),
	"exam_status":fields.String()
	})

stu_exam_section = api.model('stu_exam_section', {
	"exam_id":fields.Integer(),
	"section_id":fields.Integer(),
	"student_id":fields.Integer(),
	"section_status":fields.String(),
	"section_duration":fields.Float()
	})

stu_que_section = api.model('stu_que_section', {
	"exam_id":fields.Integer(),
	"section_id":fields.Integer(),
	"student_id":fields.Integer(),
	"question_id":fields.Integer(),
	"option_id":fields.Integer(),
	"answer":fields.String(),
	"question_status":fields.String(),
	"question_duration":fields.Float()
	})
#------------------------------------------------------#			
@name_space.route("/SectionWiseQuestionsBySectionIdExamId/<int:exam_id>/<int:section_id>",
	doc={'params':{'start':'questionId','limit':'limit','page':'pageno'}})	
class SectionWiseQuestionsBySectionId(Resource):
	def get(self,exam_id,section_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		
		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 1))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		cursor.execute("""SELECT count(`question_id`)as count FROM 
			`question` WHERE `section_id`=%s""",(section_id))

		countDtls = cursor.fetchone()
		total_count = countDtls.get('count')
		print(total_count)
		cur_count = int(page) * int(limit)
		print(cur_count)
		
		if start == 0:
			previous_url = ''

			cursor.execute("""SELECT section_id,name,section_type,duration 
				FROM `exam_section_master` WHERE `section_id`=%s""",(section_id))

			sectiondtls = cursor.fetchone()
			if sectiondtls == None:
				sectiondtls = []
				
			else:
				cursor.execute("""SELECT `question_id`,set_id FROM `question` 
					where `section_id`=%s and `exam_id`=%s""",
					(section_id,exam_id))

				setdtls = cursor.fetchall()
				
				if setdtls == ():
					sectiondtls['question'] = []

				else:
					for chksid in range(len(setdtls)):
						
						if setdtls != () and setdtls[chksid]['set_id'] == 0:
							
							cursor.execute("""SELECT q.`question_id`,quetion_type,set_id,marks,negative_marks, 
								difficulty_level,option_available,calculator_available,
								question_resource_id,resource_type,description,q.`solution`,
								sequence as 'que_sequence' FROM `question` q
								inner join question_resource_mapping qrm on q.`question_id`=qrm.`question_id`
								where q.`section_id`=%s and q.`exam_id`=%s order by q.`question_id` ASC limit %s""",
								(section_id,exam_id,limit))

							questiondtls = cursor.fetchall()
							
							if questiondtls == ():
								sectiondtls['question'] = []
								
							else:
								for i in range(len(questiondtls)):
									sectiondtls['question'] = questiondtls
									
									cursor.execute("""SELECT q.`question_id`,Option_ID,`Option`,Content_file_path,
										Content_FileName,File_Type FROM `question` q
										inner join options op on q.`question_id`=op.`Question_ID` where
										q.`Question_ID`=%s""",(questiondtls[i]['question_id']))
									optdtls = cursor.fetchall()
									if optdtls:
										questiondtls[i]['option'] = optdtls

									else:
										questiondtls[i]['option'] = []

						else:
							cursor.execute("""SELECT q.`question_id`,quetion_type,q.`set_id`,marks,negative_marks, 
								difficulty_level,option_available,calculator_available,
								set_resource_id,resource_type,description,q.`solution`,
								sequence as 'que_sequence' FROM `question` q
								inner join questionset_resource_mapping qrm on q.`set_id`=qrm.`set_id`
								where q.`section_id`=%s and q.`exam_id`=%s order by q.`question_id` ASC limit %s""",
								(section_id,exam_id,limit))

							questiondtls = cursor.fetchall()

							if questiondtls == ():
								sectiondtls['question'] = []
								
							else:
								for i in range(len(questiondtls)):
									sectiondtls['question'] = questiondtls

									cursor.execute("""SELECT q.`question_id`,Option_ID,`Option`,Content_file_path,
										Content_FileName,File_Type FROM `question` q
										inner join options op on q.`question_id`=op.`Question_ID` where
										q.`Question_ID`=%s""",(questiondtls[i]['question_id']))
									optdtls = cursor.fetchall()
									if optdtls != ():
										questiondtls[i]['option'] = optdtls

									else:
										questiondtls[i]['option'] = []

		else:
			cursor.execute("""SELECT section_id,name,section_type,duration 
				FROM `exam_section_master` WHERE `section_id`=%s""",(section_id))

			sectiondtls = cursor.fetchone()
			if sectiondtls == None:
				sectiondtls = []
				
			else:
				cursor.execute("""SELECT `question_id`,set_id FROM `question` 
					where `section_id`=%s and `exam_id`=%s""",
					(section_id,exam_id))

				setdtls = cursor.fetchall()
				
				if setdtls == ():
					sectiondtls['question'] = []

				else:
					for chksid in range(len(setdtls)):
						
						if setdtls != () and setdtls[chksid]['set_id'] == 0:
							
							cursor.execute("""SELECT q.`question_id`,quetion_type,set_id,marks,negative_marks, 
								difficulty_level,option_available,calculator_available,
								question_resource_id,resource_type,description,q.`solution`,
								sequence as 'que_sequence' FROM `question` q
								inner join question_resource_mapping qrm on q.`question_id`=qrm.`question_id`
								where q.`question_id`>%s and q.`section_id`=%s and q.`exam_id`=%s order by q.`question_id` ASC limit %s""",
								(start,section_id,exam_id,limit))

							questiondtls = cursor.fetchall()
							
							if questiondtls == ():
								sectiondtls['question'] = []
								
							else:
								for i in range(len(questiondtls)):
									sectiondtls['question'] = questiondtls
									
									cursor.execute("""SELECT q.`question_id`,Option_ID,`Option`,Content_file_path,
										Content_FileName,File_Type FROM `question` q
										inner join options op on q.`question_id`=op.`Question_ID` where
										q.`Question_ID`=%s""",(questiondtls[i]['question_id']))
									optdtls = cursor.fetchall()
									if optdtls:
										questiondtls[i]['option'] = optdtls

									else:
										questiondtls[i]['option'] = []

						else:
							cursor.execute("""SELECT q.`question_id`,quetion_type,q.`set_id`,marks,negative_marks,
								difficulty_level,option_available,calculator_available,
								set_resource_id,resource_type,description,q.`solution`,
								sequence as 'que_sequence' FROM `question` q
								inner join questionset_resource_mapping qrm on q.`set_id`=qrm.`set_id`
								where q.`question_id`>%s and q.`section_id`=%s and q.`exam_id`=%s order by q.`question_id` ASC limit %s""",
								(start,section_id,exam_id,limit))

							questiondtls = cursor.fetchall()

							if questiondtls == ():
								sectiondtls['question'] = []
								
							else:
								for i in range(len(questiondtls)):
									sectiondtls['question'] = questiondtls

									cursor.execute("""SELECT q.`question_id`,Option_ID,`Option`,Content_file_path,
										Content_FileName,File_Type FROM `question` q
										inner join options op on q.`question_id`=op.`Question_ID` where
										q.`Question_ID`=%s""",(questiondtls[i]['question_id']))
									optdtls = cursor.fetchall()
									if optdtls != ():
										questiondtls[i]['option'] = optdtls

									else:
										questiondtls[i]['option'] = []

		page_next = page + 1
		if cur_count < total_count:
			next_url = '?start={}&limit={}&page={}'.format(questiondtls[-1].get('question_id'),limit,page_next)
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Section Wise Questions Details",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url
								},
	             "responseList": sectiondtls}), status.HTTP_200_OK

#----------------------------------------------------------#
@name_space.route("/StudentExamMapping")
class StudentExamMapping(Resource):
	@api.expect(student_exam_mapping)
	def post(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()
		
		exam_id = details['exam_id']
		student_id = details['student_id']
		exam_status = details['exam_status']

		cursor.execute("""SELECT `mapping_id`,`exam_status` FROM 
			`student_exam_mapping` WHERE `exam_id`=%s and `student_id`=%s""",
			(exam_id,student_id))
		exammapdata = cursor.fetchone()

		if exammapdata != None:
			update_status = ("""UPDATE `student_exam_mapping` SET `exam_status`= %s 
				WHERE `exam_id`=%s and `student_id`=%s""")
			updatedata = cursor.execute(update_status,(exam_status,exam_id,student_id))
			if updatedata:
				msg = "Updated"
				exam_mapping_id = exammapdata['mapping_id']
				details['exam_mapping_id'] = exam_mapping_id

			else:
				msg = "Not Updated"
		else:
			map_query = ("""INSERT INTO `student_exam_mapping`(`exam_id`,
				`student_id`,`exam_status`) 
				VALUES(%s,%s,%s)""")
			
			mapdata = cursor.execute(map_query,(exam_id,student_id,
				exam_status))
			
			if mapdata:
				msg = "Added"
				exam_mapping_id = cursor.lastrowid
				details['exam_mapping_id'] = exam_mapping_id

			else:
				msg = "Not Added"
		total=0
		details2=[]

		question_query=("""SELECT `question_id`,`answer` FROM `student_question_mapping` WHERE `exam_id`=%s AND `student_id`=%s AND `question_status`="answered" """)
		question_data=(exam_id,student_id)
		question_count=cursor.execute(question_query,question_data)

		if question_count>0:
			questions=cursor.fetchall()
			for key,data in enumerate(questions):
				solution_query=("""SELECT `marks`,`solution` FROM `question` WHERE `question_id`=%s""")
				solution_data=(data["question_id"])
				solution_count=cursor.execute(solution_query,solution_data)
				if solution_count>0:
					solutions=cursor.fetchone()
					details2.append(solutions)


			for key,data in enumerate(details2):
				if data["solution"]==questions[key]["answer"]:
					total+=data["marks"]
				else:
					total+=0

		cursor.execute("""SELECT `published_id` FROM `publish_exam_results` WHERE `exam_id`=%s AND `student_id`=%s""",(exam_id,student_id))

		abc = cursor.fetchone()
		if abc:
			cursor.execute("""UPDATE `publish_exam_results` SET `total_marks`=%s WHERE `published_id` = %s""",(total,abc['published_id']))
		else:
			cursor.execute("""INSERT INTO `publish_exam_results`(`exam_id`,`student_id`,`total_marks`,`last_update_id`) VALUES(%s,%s,%s,%s)""",(exam_id,student_id,total,student_id))
			

		connection.commit()
		cursor.close()

		return ({"attributes": {
								"status_desc": "Student Exam Details",
                                "status": "success",
                                "msg": msg
	                            },
	             "responseList": details}), status.HTTP_200_OK

#----------------------------------------------------------#
@name_space.route("/StudentExamSectionMapping")
class StudentExamSectionMapping(Resource):
	@api.expect(stu_exam_section)
	def post(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()
		
		exam_id = details['exam_id']
		section_id = details['section_id']
		student_id = details['student_id']
		section_status = details['section_status']
		section_duration = details['section_duration']

		cursor.execute("""SELECT `section_mapping_id`,`section_status` FROM 
			`student_examsection_mapping` WHERE `exam_id`=%s and 
			`section_id`=%s and `student_id`=%s""",(exam_id,section_id,student_id))
		secmapdata = cursor.fetchone()

		if secmapdata != None:
			update_status = ("""UPDATE `student_examsection_mapping` SET `section_status`=%s,
				`section_duration`=%s WHERE `exam_id`=%s and 
				`section_id`=%s and `student_id`=%s""")
			updatedata = cursor.execute(update_status,(section_status,section_duration,exam_id,section_id,student_id))
			if updatedata:
				msg = "Updated"
				section_mapping_id = secmapdata['section_mapping_id']
				details['section_mapping_id'] = section_mapping_id

			else:
				msg = "Not Updated"
		else:
			map_query = ("""INSERT INTO `student_examsection_mapping`(`exam_id`,
				`section_id`,`student_id`,`section_status`,`section_duration`) 
				VALUES(%s,%s,%s,%s,%s)""")
			
			mapdata = cursor.execute(map_query,(exam_id,section_id,student_id,
				section_status,section_duration))
			
			if mapdata:
				msg = "Added"
				section_mapping_id = cursor.lastrowid
				details['section_mapping_id'] = section_mapping_id

			else:
				msg = "Not Added"

		connection.commit()
		cursor.close()

		return ({"attributes": {
								"status_desc": "Student Exam Section Details",
                                "status": "success",
                                "msg": msg
	                            },
	             "responseList": details}), status.HTTP_200_OK

#----------------------------------------------------------#
@name_space.route("/StudentQuestionMapping")
class StudentQuestionMapping(Resource):
	@api.expect(stu_que_section)
	def post(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()
		
		exam_id = details['exam_id']
		section_id = details['section_id']
		student_id = details['student_id']
		question_id = details['question_id']
		option_id = details['option_id']
		answer = details['answer']
		question_status = details['question_status']
		question_duration = details['question_duration']
		
		cursor.execute("""SELECT `mapping_id`,`question_status` FROM 
			`student_question_mapping` WHERE `exam_id`=%s 
			and `section_id`=%s and `question_id`=%s and 
			`student_id`=%s""",(exam_id,section_id,question_id,student_id))
		quemapdata = cursor.fetchone()

		if quemapdata != None:
			update_status = ("""UPDATE `student_question_mapping` SET `option_id`=%s,
				`answer`=%s,`question_status`=%s,`question_duration`=%s WHERE 
				`exam_id`=%s and `section_id`=%s and `question_id`=%s 
				and `student_id`=%s""")
			updatedata = cursor.execute(update_status,(option_id,answer,question_status,
				question_duration,exam_id,section_id,question_id,student_id))
			if updatedata:
				msg = "Updated"
				question_mapping_id = quemapdata['mapping_id']
				details['question_mapping_id'] = question_mapping_id

			else:
				msg = "Not Updated"
		else:
			map_query = ("""INSERT INTO `student_question_mapping`(`exam_id`,
				`section_id`,`student_id`,`question_id`,`option_id`,`answer`,`question_status`,
				`question_duration`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")
			
			mapdata = cursor.execute(map_query,(exam_id,section_id,student_id,
				question_id,option_id,answer,question_status,question_duration))
			
			if mapdata:
				msg = "Added"
				question_mapping_id = cursor.lastrowid
				details['question_mapping_id'] = question_mapping_id

			else:
				msg = "Not Added"

		connection.commit()
		cursor.close()

		return ({"attributes": {
								"status_desc": "Student Question Mapping Details",
                                "status": "success",
                                "msg": msg
	                            },
	             "responseList": details}), status.HTTP_200_OK

#----------------------------------------------------------#
@name_space.route("/SectionWiseStudentQuestionStatusByStudentIdSectionIdExamId/<int:exam_id>/<int:section_id>/<int:student_id>")	
class SectionWiseStudentQuestionStatusByStudentIdSectionIdExamId(Resource):
	def get(self,exam_id,section_id,student_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		queDtls = {}
		studentsectionDtls = []

		cursor.execute("""SELECT count(`question_id`)as count FROM 
			`question` WHERE `section_id`=%s and `exam_id`=%s""",
			(section_id,exam_id))

		countDtls = cursor.fetchone()
		total_count = countDtls.get('count')
		
		cursor.execute("""SELECT `question_id` FROM `question` WHERE 
			`exam_id`=%s and `section_id`=%s""",(exam_id,section_id))

		examdtls = cursor.fetchall()
		if examdtls != ():
			for qid in range(len(examdtls)):
				cursor.execute("""SELECT`question_id`,question_duration  FROM `student_question_mapping` sqm 
				 	WHERE `student_id`=%s and `exam_id`=%s and `section_id`=%s""",
					(student_id,exam_id,section_id))

				studentdtls = cursor.fetchone()
				if studentdtls == None:
					queDtls['section_id'] = section_id
					queDtls['section_status'] = "notvisited"
					queDtls['section_duration'] = ""
					queDtls['student_id'] = student_id
					queDtls['question_id'] = examdtls[qid]['question_id']
					queDtls['question_status'] = "notanswered"
					queDtls['question_duration'] = ""
					queDtls['exam_id'] = exam_id
					
					studentsectionDtls.append(queDtls.copy())
				else:
					
					cursor.execute("""SELECT distinct(sqm.`question_id`),`question_status`,
						question_duration,sqm.`exam_id`,sqm.`section_id`,sqm.`student_id`,
						`section_status`, `section_duration` FROM `student_question_mapping` sqm 
						Left join `student_examsection_mapping` ssm on 
						sqm.`section_id`=ssm.`section_id` WHERE 
						sqm.`student_id`=%s and sqm.`question_id`=%s 
						and sqm.`exam_id`=%s and sqm.`section_id`=%s""",
						(student_id,examdtls[qid]['question_id'],exam_id,section_id))

					sectiondtls = cursor.fetchone()

					if sectiondtls != None:
						sectiondtls['section_status'] = "visited"
						sectiondtls['section_duration'] = sectiondtls['section_duration']
						studentsectionDtls.append(sectiondtls)
						
					else:
						queDtls['section_id'] = section_id
						queDtls['section_status'] = "visited"
						queDtls['section_duration'] = ""
						queDtls['student_id'] = student_id
						queDtls['question_id'] = examdtls[qid]['question_id']
						queDtls['question_status'] = "notanswered"
						queDtls['question_duration'] = ""
						queDtls['exam_id'] = exam_id
						
						studentsectionDtls.append(queDtls.copy())	
					
		else:
			studentsectionDtls = []

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Section Wise Student Questions Details",
	                            "status": "success",
	                            "total":total_count
								},
	             "responseList": studentsectionDtls}), status.HTTP_200_OK

#----------------------------------------------------#
@name_space.route("/StudentExamSectionStatusByStudentIdExamId/<int:exam_id>/<int:student_id>")	
class StudentExamSectionStatusByStudentIdExamId(Resource):
	def get(self,exam_id,student_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		secList = []
		secDtls = {}

		cursor.execute("""SELECT count(`section_id`)as count FROM 
			`exam_section_master` WHERE `exam_id`=%s""",(exam_id))

		seccountDtls = cursor.fetchone()
		total_count = seccountDtls.get('count')
		
		cursor.execute("""SELECT count(`section_id`)as count FROM 
			`student_examsection_mapping` WHERE `exam_id`=%s and 
			`student_id`=%s and `section_status`='completed'""",
			(exam_id,student_id))

		secStatusDtls = cursor.fetchone()
		
		if secStatusDtls:
			Status_count = secStatusDtls.get('count')
		else:
			Status_count = 0
		
		cursor.execute("""SELECT `section_id`,`name` FROM 
			`exam_section_master` WHERE `exam_id`=%s""",(exam_id))
		sectionmasterDtls = cursor.fetchall()

		if sectionmasterDtls != ():
			for smid in range(len(sectionmasterDtls)):

				cursor.execute("""SELECT `section_status`,
					`section_duration`,`section_marks` FROM 
					`student_examsection_mapping` WHERE `student_id`=%s 
					and `section_id`=%s and `exam_id`=%s""",
					(student_id,sectionmasterDtls[smid]['section_id'],exam_id))

				sectionDtls = cursor.fetchone()
				print(sectionDtls)

				if sectionDtls:
					if sectionDtls['section_marks'] == None:
						sectionDtls['section_marks'] = ""
					else:
						sectionDtls['section_marks'] = sectionDtls['section_marks']
					
					if sectionDtls['section_duration'] == None:
						sectionDtls['section_duration'] = ""
					else:
						sectionDtls['section_duration'] = sectionDtls['section_duration']

					sectionDtls['section_id'] = sectionmasterDtls[smid]['section_id']
					sectionDtls['name'] = sectionmasterDtls[smid]['name']
					secList.append(sectionDtls)
				else:
					secDtls['section_status'] = "notcompleted"
					secDtls['section_marks'] = ""
					
					secDtls['section_duration'] = ""
					
					secDtls['section_id'] = sectionmasterDtls[smid]['section_id']
					secDtls['name'] = sectionmasterDtls[smid]['name']
					
					secList.append(secDtls.copy())
				
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Section Wise Student Questions Details",
	                            "status": "success",
	                            "totalSection":total_count,
             					"totalCompletedSection":Status_count
					             
	                            },
	             "responseList": secList }), status.HTTP_200_OK

#--------------------------------------------------------------#
@name_space.route("/ExamListByStudentId/<int:student_id>")	
class ExamListByStudentId(Resource):
	def get(self,student_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT count(`exam_id`)as count 
			FROM `exam_master` WHERE `exam_id` not in(SELECT `exam_id` 
			FROM `student_exam_mapping` WHERE `student_id`=%s)""",
			(student_id))

		countDtls = cursor.fetchone()
		total_count = countDtls.get('count')
		
		
		cursor.execute("""SELECT `exam_id`,`type`,`name`,`module_id`,
			`teacher_id`,`fullmarks`,`duration`,`topic_id`,`subject_id` 
			FROM `exam_master` WHERE `exam_id` not in(SELECT `exam_id` 
			FROM `student_exam_mapping` WHERE `student_id`=%s)""",
			(student_id))

		examdtls = cursor.fetchall()

		if examdtls != ():
			examdtls = examdtls
		else:

			examdtls = []	
				
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Student Wise Exam List Details",
	                            "status": "success",
	                            "total":total_count
								},
	             "responseList": examdtls}), status.HTTP_200_OK

#----------------------------------------------------------#
@name_space.route("/SectionWiseQuestionStatusByStudentIdSectionIdExamId/<int:exam_id>/<int:section_id>/<int:student_id>")	
class SectionWiseQuestionStatusByStudentIdSectionIdExamId(Resource):
	def get(self,exam_id,section_id,student_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		queDtls = {}
		studentsectionDtls = []

		cursor.execute("""SELECT count(`question_id`)as count FROM 
			`question` WHERE `section_id`=%s and `exam_id`=%s""",
			(section_id,exam_id))

		countDtls = cursor.fetchone()
		total_count = countDtls.get('count')
		
		cursor.execute("""SELECT `question_id` FROM `question` WHERE 
			`exam_id`=%s and `section_id`=%s""",(exam_id,section_id))

		examdtls = cursor.fetchall()
		if examdtls != ():
			for qid in range(len(examdtls)):
				cursor.execute("""SELECT`question_id`,question_duration  FROM `student_question_mapping` sqm 
				 	WHERE `student_id`=%s and `exam_id`=%s and `section_id`=%s""",
					(student_id,exam_id,section_id))

				studentdtls = cursor.fetchone()
				if studentdtls == None:
					queDtls['student_id'] = student_id
					queDtls['question_id'] = examdtls[qid]['question_id']
					queDtls['question_status'] = "notvisited"
					queDtls['question_duration'] = 0.001
					
					studentsectionDtls.append(queDtls.copy())
				else:
					
					cursor.execute("""SELECT distinct(sqm.`question_id`),`question_status`,
						question_duration,sqm.`student_id`
						FROM `student_question_mapping` sqm Left join `student_examsection_mapping` ssm on 
						sqm.`section_id`=ssm.`section_id` WHERE sqm.`student_id`=%s and sqm.`question_id`=%s 
						and sqm.`exam_id`=%s and sqm.`section_id`=%s""",
						(student_id,examdtls[qid]['question_id'],exam_id,section_id))

					sectiondtls = cursor.fetchone()

					if sectiondtls != None:
						studentsectionDtls.append(sectiondtls)
						
					else:
						queDtls['student_id'] = student_id
						queDtls['question_id'] = examdtls[qid]['question_id']
						queDtls['question_status'] = "notanswered"
						queDtls['question_duration'] = 0.001
						
						studentsectionDtls.append(queDtls.copy())	
					
		else:
			studentsectionDtls = []

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Section Wise Student Questions Details",
	                            "status": "success",
	                            "total":total_count
								},
	             "responseList": studentsectionDtls}), status.HTTP_200_OK

#--------------------------------------------------------------#
@name_space.route("/ExamWiseSectionQuestionStatusDetailsByStudentIdExamId/<int:exam_id>/<int:student_id>")	
class ExamWiseSectionQuestionStatusDetailsByStudentIdExamId(Resource):
	def get(self,exam_id,student_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		cursor.execute("""SELECT count(`section_id`)as count FROM 
			`exam_section_master` WHERE `exam_id`=%s""",(exam_id))

		seccountDtls = cursor.fetchone()
		total_seccount = seccountDtls.get('count')
		
		cursor.execute("""SELECT count(`section_id`)as count FROM 
			`student_examsection_mapping` WHERE `exam_id`=%s and 
			`student_id`=%s and `section_status`='completed'""",
			(exam_id,student_id))

		secStatusDtls = cursor.fetchone()
		
		if secStatusDtls:
			Status_count = secStatusDtls.get('count')
		else:
			Status_count = 0

		cursor.execute("""SELECT section_id,name,exam_id,duration 
			as 'exam_section_duration' FROM `exam_section_master` WHERE 
			`exam_id`=%s""",(exam_id))

		sectionDtls = cursor.fetchall()
		for sid,sect in enumerate(sectionDtls):
			section_id = sectionDtls[sid]['section_id']
			
			cursor.execute("""SELECT `section_id`,`section_status`,`section_duration` 
				FROM `student_examsection_mapping` WHERE `exam_id`=%s and `section_id`=%s 
				and `student_id`=%s""",(exam_id,section_id,student_id))

			chksecDtls = cursor.fetchone()
			if chksecDtls == None:
				sectionDtls[sid]['section_status'] = "notcompleted"
				sectionDtls[sid]['section_duration'] = 0.001
			else:
				sectionDtls[sid]['section_status'] = chksecDtls['section_status']
				sectionDtls[sid]['section_duration'] = chksecDtls['section_duration']

			cursor.execute("""SELECT `question_id` FROM `question` WHERE 
				`exam_id`=%s and `section_id`=%s""",(exam_id,section_id))

			quesCountdtls = cursor.fetchall()
			sectionDtls[sid]['totalQuestion'] = len(quesCountdtls)

			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			url = BASE_URL + 'studentexam_section/MyElsaNewStudentExamSection/SectionWiseQuestionStatusByStudentIdSectionIdExamId/{}/{}/{}'.format(exam_id,section_id,student_id)
			questionDetails = requests.get(url)
			
			try:
				queDetails = questionDetails.json()
				queresponse = json.dumps(queDetails['responseList'])
				queres = json.loads(queresponse)
				questionList = queres
				sectionDtls[sid]['questionList'] = questionList

			except ValueError:
				questionList = []
				sectionDtls[sid]['questionList'] = questionList
			
			
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Exam Wise Section Questions Details",
	                            "status": "success",
	                            "totalSection":total_seccount,
             					"totalCompletedSection":Status_count
								},
	             "responseList": sectionDtls}), status.HTTP_200_OK

#----------------------------------------------------------#
@name_space.route("/QuestionDetailsByQuestionIdStudentId/<int:question_id>/<int:student_id>")	
class QuestionDetailsByQuestionIdStudentId(Resource):
	def get(self,question_id,student_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT `question_id`,set_id FROM `question` 
			where `question_id`=%s""",(question_id))

		setdtls = cursor.fetchone()
				
		if setdtls != () and setdtls['set_id'] == 0:
			
			cursor.execute("""SELECT `question_id`,exam_id,section_id,quetion_type,
				set_id,marks,negative_marks,difficulty_level,option_available,
				question_format_type,calculator_available,`solution` FROM `question` where 
				`question_id`=%s""",(question_id))

			questiondtls = cursor.fetchone()
			
			if questiondtls == None:
				questiondtls = []
				
			else:
				cursor.execute("""SELECT `question_resource_id`,`resource_type`,
					`description`,sequence as 'que_sequence' FROM `question_resource_mapping` 
					WHERE `question_id`=%s""",(question_id))
				questionlist = cursor.fetchall()
				if questionlist == None:
					questiondtls['question'] = []
					
				else:
					questiondtls['question'] = questionlist

				cursor.execute("""SELECT `option_id`,`answer`,`question_duration` 
					FROM `student_question_mapping` WHERE `question_id`=%s and 
					`student_id`=%s and `exam_id`=%s and `section_id`=%s""",
					(question_id,student_id,questiondtls['exam_id'],questiondtls['section_id']))
				durationDtls = cursor.fetchone()
				if durationDtls:
					questiondtls['student_answer'] = durationDtls['answer']
					questiondtls['student_answeroption_id'] = durationDtls['option_id']
					
					questiondtls['question_duration'] = durationDtls['question_duration']
				else:
					questiondtls['student_answer'] = ""
					questiondtls['student_answeroption_id'] = 0

					questiondtls['question_duration'] = 0.001

				cursor.execute("""SELECT `question_id`FROM `question` where 
					`question_id`>%s and exam_id=%s and section_id=%s limit 1""",
					(question_id,questiondtls['exam_id'],questiondtls['section_id']))

				nextquestionid = cursor.fetchone()

				if nextquestionid:
					next_questionid = nextquestionid['question_id']
				else:
					cursor.execute("""SELECT `section_id` FROM `exam_section_master` WHERE 
						`exam_id`=%s and `section_id`>%s limit 1""",(questiondtls['exam_id'],
						questiondtls['section_id']))
					nextsectionid = cursor.fetchone()
					if nextsectionid:
						cursor.execute("""SELECT `question_id`FROM `question` where 
							`question_id`>%s and exam_id=%s and section_id=%s limit 1""",
							(question_id,questiondtls['exam_id'],nextsectionid['section_id']))

						nextquestionid = cursor.fetchone()
						
						if nextquestionid:
							next_questionid = nextquestionid['question_id']
						else:
							next_questionid = 0
					else:
						next_questionid = 0

				cursor.execute("""SELECT q.`question_id`,Option_ID,`Option`,Content_file_path,
					Content_FileName,File_Type FROM `question` q
					inner join options op on q.`question_id`=op.`Question_ID` where
					q.`Question_ID`=%s""",(question_id))
				optdtls = cursor.fetchall()
				if optdtls:
					questiondtls['option'] = optdtls

				else:
					questiondtls['option'] = []

		else:
			cursor.execute("""SELECT `question_id`,exam_id,section_id,quetion_type,
				`set_id`,marks,negative_marks,difficulty_level,option_available,
				question_format_type,calculator_available,`solution` FROM `question` where 
				`question_id`=%s""",(question_id))

			questiondtls = cursor.fetchone()

			if questiondtls == None:
				questiondtls = []
				
			else:
				cursor.execute("""SELECT `set_resource_id`,`resource_type`,
					`description`,sequence as 'que_sequence' FROM `questionset_resource_mapping` 
					WHERE `question_id`=%s""",(question_id))
				questionlist = cursor.fetchall()
				if questionlist == None:
					questiondtls['question'] = []
					
				else:
					questiondtls['question'] = questionlist

				cursor.execute("""SELECT `option_id`,`answer`,`question_duration` 
					FROM `student_question_mapping` WHERE `question_id`=%s and 
					`student_id`=%s and `exam_id`=%s and `section_id`=%s""",
					(question_id,student_id,questiondtls['exam_id'],questiondtls['section_id']))
				durationDtls = cursor.fetchone()
				if durationDtls:
					questiondtls['student_answer'] = durationDtls['answer']
					questiondtls['student_answeroption_id'] = durationDtls['option_id']
					
					questiondtls['question_duration'] = durationDtls['question_duration']
				else:
					questiondtls['student_answer'] = ""
					questiondtls['student_answeroption_id'] = 0
					
					questiondtls['question_duration'] = 0.001


				cursor.execute("""SELECT `question_id` FROM `question` where 
					`question_id`>%s and exam_id=%s and section_id=%s limit 1""",
					(question_id,questiondtls['exam_id'],questiondtls['section_id']))

				nextquestionid = cursor.fetchone()

				if nextquestionid:
					next_questionid = nextquestionid['question_id']
				else:
					cursor.execute("""SELECT `section_id` FROM `exam_section_master` WHERE 
						`exam_id`=%s and `section_id`>%s limit 1""",(questiondtls['exam_id'],
						questiondtls['section_id']))
					nextsectionid = cursor.fetchone()

					if nextsectionid:
						cursor.execute("""SELECT `question_id`FROM `question` where 
							`question_id`>%s and exam_id=%s and section_id=%s limit 1""",
							(question_id,questiondtls['exam_id'],nextsectionid['section_id']))

						nextquestionid = cursor.fetchone()
						
						if nextquestionid:
							next_questionid = nextquestionid['question_id']
						else:
							next_questionid = 0
					else:
						next_questionid = 0

				cursor.execute("""SELECT q.`question_id`,Option_ID,`Option`,Content_file_path,
					Content_FileName,File_Type FROM `question` q
					inner join options op on q.`question_id`=op.`Question_ID` where
					q.`Question_ID`=%s""",(question_id))
				optdtls = cursor.fetchall()
				if optdtls != ():
					questiondtls['option'] = optdtls

				else:
					questiondtls['option'] = []

		
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Section Wise Questions Details",
	                            "status": "success",
	                            "next_questionid": next_questionid
								},
	             "responseList": questiondtls}), status.HTTP_200_OK
