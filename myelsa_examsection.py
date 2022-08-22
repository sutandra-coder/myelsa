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

exam_section = Blueprint('exam_api', __name__)
api = Api(exam_section,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('MyElsaNewExamSection',description='MyElsa New Exam')


createexam = api.model('createexam', {
	"name":fields.String(),
	"type":fields.String(),
	"module_id":fields.Integer(),
	"section_id":fields.Integer(),
	"course_id":fields.Integer(),
	"liveclass_id":fields.Integer(),
	"teacher_id":fields.Integer(),
	"fullmarks":fields.Integer(),
	"duration":fields.Integer(),
	"topic_id":fields.Integer(),
	"subject_id":fields.Integer()
	})


examsection = api.model('examsection', {
	"exam_id":fields.Integer(),
	"name":fields.String(),
	"sectiontype":fields.String(),
	"duration":fields.Integer()
	})

questionset = api.model('questionset', {
	"teacher_id":fields.Integer(),
	"set_name":fields.String(),
	"set_description":fields.String()
	})
instructions = api.model('instructions', {
	"instruction":fields.String(),
	"instruction_filepath":fields.String(),
	"instruction_filename":fields.String(),
	"instruction_filetype":fields.String()
	})

instructiondtls = api.model('instructiondtls', {
	"exam_id":fields.Integer(),
	"instructions": fields.List(fields.Nested(instructions))
	})

add_options = api.model('options',{
	"Option":fields.String(),
	"Content_file_path":fields.String(),
	"Content_FileName":fields.String(),
	"File_Type":fields.String()
	})

add_resource = api.model('resource',{
	"resource_type":fields.String(),
	"description":fields.String(),
	"sequence":fields.Integer()
	})

add_que = api.model('questions', {
	"question_type":fields.String(),
	"question_format_type":fields.String(),
	"exam_id":fields.Integer(),
	"section_id":fields.Integer(),
	"set_id":fields.Integer(),
	"marks":fields.Integer(),
	"negative_marks":fields.Integer(),
	"difficulty_level":fields.String(),
	"solution":fields.String(),
	"option_available":fields.String(),
	"calculator_available":fields.String(),
	"teacher_id":fields.Integer(),
	"option_flag":fields.String(),
	"answer":fields.String(),
	"topic_id":fields.Integer(),
	"subject_id":fields.Integer(),
	"resources": fields.List(fields.Nested(add_resource)),
	"options": fields.List(fields.Nested(add_options))
	})

update_examdtls = api.model('update_examdtls', {
	"exam_id":fields.Integer(),
	"name":fields.String(),
	"type":fields.String(),
	"module_id":fields.Integer(),
	"section_id":fields.Integer(),
	"course_id":fields.Integer(),
	"liveclass_id":fields.Integer(),
	"fullmarks":fields.Integer(),
	"duration":fields.Integer()
	})

remove_examdtls = api.model('remove_examdtls', {
	"exam_id":fields.Integer(),
	"module_id":fields.Integer(),
	"section_id":fields.Integer(),
	"course_id":fields.Integer(),
	"liveclass_id":fields.Integer()
	})
#----------------------------------------------------#
@name_space.route("/CreateExam")
class CreateExam(Resource):
	@api.expect(createexam)
	def post(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()
		
		name = details.get('name')
		examtype = details.get('type')
		module_id = details.get('module_id')
		section_id = details.get('section_id')
		course_id = details.get('course_id')
		liveclass_id = details.get('liveclass_id')
		teacher_id = details.get('teacher_id')
		fullmarks = details.get('fullmarks')
		duration = details.get('duration')
		topic_id = details.get('topic_id')
		subject_id = details.get('subject_id')

		exam_query = ("""INSERT INTO `exam_master`(`type`,`name`,module_id,
			section_id,course_id,liveclass_id,`teacher_id`,`fullmarks`,`duration`,
			topic_id,subject_id)
			VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
		exam_data = (examtype,name,module_id,section_id,course_id,liveclass_id,
			teacher_id,fullmarks,duration,topic_id,subject_id)
		examdata = cursor.execute(exam_query,exam_data)

		if examdata:
			exam_id = cursor.lastrowid
			details['exam_id'] = exam_id
			msg = "Added"
		else:
			msg = "Not Added"
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Exam Details",
                                "status": "success",
                                "msg": msg
	                                },
	             "responseList": details}), status.HTTP_200_OK

#--------------------------------------------------------#			
@name_space.route("/ExamDtlsByTeacherId/<int:teacher_id>")	
class ExamDtlsByTeacherId(Resource):
	def get(self,teacher_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT exam_id,type,name,em.`module_id`,
        	section_id,em.`course_id`,liveclass_id,module_name,
        	em.`teacher_id`,fullmarks,duration,topic_id,subject_id,
        	em.`last_update_ts` FROM `exam_master` em Left join 
        	`module` mm on em.`module_id`=mm.`module_id` WHERE 
			em.`teacher_id`=%s""",(teacher_id))

		examdtls = cursor.fetchall()
		for i in range(len(examdtls)):
			cursor.execute("""SELECT * FROM `exam_section_master` WHERE 
				`exam_id`=%s""",(examdtls[i]['exam_id']))

			sectiondtls = cursor.fetchall()
				
			if examdtls:
				examdtls[i]['last_update_ts'] = examdtls[i]['last_update_ts'].isoformat()
				examdtls[i]['totalsection'] = len(sectiondtls)
			else:
				examdtls = []
				
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Exam Details",
		    		"status": "success"
		    	},
		    	"responseList":examdtls}), status.HTTP_200_OK

#----------------------------------------------------#
@name_space.route("/CreateExamSection")
class CreateExamSection(Resource):
	@api.expect(examsection)
	def post(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()
		
		exam_id = details.get('exam_id')
		name = details.get('name')
		sectiontype = details.get('sectiontype')
		duration = details.get('duration')

		section_query = ("""INSERT INTO `exam_section_master`(`exam_id`,
			`name`,`section_type`,duration) 
			VALUES(%s,%s,%s,%s)""")
		section_data = (exam_id,name,sectiontype,duration)
		sectiondata = cursor.execute(section_query,section_data)

		if sectiondata:
			section_id = cursor.lastrowid
			details['section_id'] = section_id

			msg = "Added"
		else:
			msg = "Not Added"

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Exam Section Details",
                                "status": "success",
                                "msg": msg
	                                },
	             "responseList": details}), status.HTTP_200_OK
			
#--------------------------------------------------------#
@name_space.route("/ExamSectionDtlsByExamId/<int:exam_id>")	
class ExamSectionDtlsByExamId(Resource):
	def get(self,exam_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT * FROM `exam_section_master` WHERE 
			`exam_id`=%s""",(exam_id))

		sectiondtls = cursor.fetchall()
		for i in range(len(sectiondtls)):
			cursor.execute("""SELECT count(`question_id`)as total,`quetion_type` 
				FROM `question` WHERE `section_id`=%s""",(sectiondtls[i]['section_id']))
			queDtls = cursor.fetchone()
			if queDtls:
				totalquestion = queDtls['total']
				sectiondtls[i]['totalquestion'] = totalquestion
				sectiondtls[i]['section_type'] = queDtls['quetion_type']
			else:
				totalquestion = 0
				sectiondtls[i]['section_type'] = ""

			if sectiondtls:
				sectiondtls[i]['last_update_ts'] = sectiondtls[i]['last_update_ts'].isoformat()
			else:
				sectiondtls = []
				
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Exam Section Details",
		    		"status": "success"
		    	},
		    	"responseList":sectiondtls}), status.HTTP_200_OK

#------------------------------------------------------#
@name_space.route("/CreateQuestionSet")
class CreateQuestionSet(Resource):
	@api.expect(questionset)
	def post(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()
		
		teacher_id = details.get('teacher_id')
		set_name = details.get('set_name')
		set_description = details.get('set_description')	
		
		set_query = ("""INSERT INTO `question_set`(`set_name`,set_description,
			`last_update_id`) VALUES(%s,%s,%s)""")
		
		setdata = cursor.execute(set_query,(set_name,set_description,teacher_id))

		if setdata:
			set_id = cursor.lastrowid
			details['set_id'] = set_id

			connection.commit()
			cursor.close()

			return ({"attributes": {
									"status_desc": "Question Set Details",
	                                "status": "success"
		                            },
		             "responseList": details}), status.HTTP_200_OK
		else:

			return ({"attributes": {"status_desc": "Question Set Details",
	                                "status": "success"
		                                },
		             "responseList": details}), status.HTTP_200_OK

#--------------------------------------------------------#			
@name_space.route("/QuestionSetListByTeacherId/<int:teacher_id>")	
class QuestionSetListByTeacherId(Resource):
	def get(self,teacher_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT * FROM `question_set` WHERE 
			`last_update_id`=%s""",(teacher_id))

		setdtls = cursor.fetchall()
		for i in range(len(setdtls)):

			if setdtls:
				setdtls[i]['last_update_ts'] = setdtls[i]['last_update_ts'].isoformat()
			else:
				setdtls = []
				
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Question Set Details",
		    		"status": "success"
		    	},
		    	"responseList":setdtls}), status.HTTP_200_OK

#------------------------------------------------------#
@name_space.route("/AddInstructions")
class AddInstructions(Resource):
	@api.expect(instructiondtls)
	def post(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()
		
		exam_id = details['exam_id']
		instruction_sequence_id = 1
		instructiondtls = details['instructions']
		for ins in range(len(instructiondtls)):
			instruction = instructiondtls[ins]['instruction']
			instruction_filepath = instructiondtls[ins]['instruction_filepath']
			instruction_filename = instructiondtls[ins]['instruction_filename']
			instruction_filetype = instructiondtls[ins]['instruction_filetype']

			instrtn_query = ("""INSERT INTO `exam_instruction`(`exam_id`,instructions,
				instruction_sequence_id,instruction_filepath,
				instruction_filename,instruction_filetype) 
				VALUES(%s,%s,%s,%s,%s,%s)""")
			
			instrtndata = cursor.execute(instrtn_query,(exam_id,instruction,
				instruction_sequence_id,instruction_filepath,
				instruction_filename,instruction_filetype))
			instruction_sequence_id += 1
			if instrtndata:
				msg = "Added"

			else:
				msg = "Not Added"
		connection.commit()
		cursor.close()

		return ({"attributes": {
								"status_desc": "Instructions Details",
                                "status": "success",
                                "msg": msg
	                            },
	             "responseList": details}), status.HTTP_200_OK

#--------------------------------------------------------#			
@name_space.route("/ExamInsructionsByExamId/<int:exam_id>")	
class ExamInsructionsByExamId(Resource):
	def get(self,exam_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT `instruction_id`,ei.`exam_id`,`instructions`,
			`instruction_sequence_id`,`instruction_filepath`,`instruction_filename`,
			`instruction_filetype`,duration,ei.`last_update_ts` FROM `exam_instruction` ei INNER JOIN 
			`exam_master` em on ei.`exam_id`=em.`exam_id` WHERE ei.`exam_id`=%s""",(exam_id))

		instdtls = cursor.fetchall()
		
		for i in range(len(instdtls)):
			instdtls[i]['last_update_ts'] = instdtls[i]['last_update_ts'].isoformat()
				
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Instructions Details",
		    		"status": "success"
		    	},
		    	"responseList":instdtls}), status.HTTP_200_OK

#------------------------------------------------------#
@name_space.route("/AddQuestions")
class AddQuestions(Resource):
	@api.expect(add_que)
	def post(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()
		
		question_type = details.get('question_type')
		question_format_type = details.get('question_format_type')
		exam_id = details.get('exam_id')
		section_id = details.get('section_id')
		set_id = details.get('set_id')
		marks = details.get('marks')
		negative_marks = details.get('negative_marks')
		difficulty_level = details.get('difficulty_level')
		solution = details.get('solution')
		option_available = details.get('option_available')
		calculator_available = details.get('calculator_available')
		teacher_id = details.get('teacher_id')
		option_flag = details.get('option_flag')
		answer = details.get('answer')
		topic_id = details.get('topic_id')
		subject_id = details.get('subject_id')
		
		if set_id != 0:
			ques_query = ("""INSERT INTO `question`(`quetion_type`,question_format_type,
				`exam_id`,`section_id`,`set_id`,`marks`,`negative_marks`,
				`difficulty_level`,`solution`,`option_available`,`calculator_available`,
				`topic_id`,`subject_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
			
			quedata = cursor.execute(ques_query,(question_type,question_format_type,exam_id,
				section_id,set_id,marks,negative_marks,difficulty_level,solution,
				option_available,calculator_available,topic_id,subject_id))

			question_id = cursor.lastrowid
			details['question_id'] = question_id

			resourcesdtls = details['resources']
			for re in range(len(resourcesdtls)):
				resource_type = resourcesdtls[re]['resource_type']
				description = resourcesdtls[re]['description']
				sequence = resourcesdtls[re]['sequence']
						
				setres_query = ("""INSERT INTO `questionset_resource_mapping`(`question_id`,
					`set_id`,`resource_type`,`description`,`sequence`) 
					VALUES(%s,%s,%s,%s,%s)""")
				
				setresdata = cursor.execute(setres_query,(question_id,set_id,
					resource_type,description,sequence))

			optionsdtls = details['options']
			Option_Sequence_ID = 1
			for op in range(len(optionsdtls)):
				option = optionsdtls[op]['Option']
				Content_file_path = optionsdtls[op]['Content_file_path']
				Content_FileName = optionsdtls[op]['Content_FileName']
				File_Type = optionsdtls[op]['File_Type']

				opt_query = ("""INSERT INTO `options`(`Question_ID`,
					`Option`,Option_Sequence_ID,Content_file_path,
					Content_FileName,File_Type) VALUES(%s,%s,%s,%s,%s,%s)""")
			
				optdata = cursor.execute(opt_query,(question_id,option,
					Option_Sequence_ID,Content_file_path,
					Content_FileName,File_Type))
				Option_Sequence_ID += 1

			if option_flag == 'y':
				cursor.execute("""SELECT `Option_ID` FROM `options` 
					WHERE `Option`=%s""",(answer))
				ansopt_id = cursor.fetchone()

				if ansopt_id:
					ansoptid = ansopt_id['Option_ID']
					ans_query = ("""INSERT INTO `answer`(`Question_ID`,
						`Option_ID`) VALUES(%s,%s)""")
				
					ansdata = cursor.execute(ans_query,(question_id,ansoptid))

					if ansdata:
						connection.commit()
						cursor.close()
						return ({"attributes": {
											"status_desc": "Question Details",
			                                "status": "success"
				                            },
				             "responseList": "Question Added"}), status.HTTP_200_OK
			else:
				answerpath = answer.split('Image/',1)
				
				filepath = answerpath[0]+ 'Image/'
				filename = answerpath[1]
				filetype = filename.split('.',1)
				
				if filetype[1] == 'jpg' or filetype[1] == 'jpeg' or filetype[1] == 'png':
					ftype = 'Image'
					
				elif filetype == 'txt':
					ftype = 'text'
					
				else:
					ftype = 'video'
					
				cursor.execute("""SELECT `Option_ID` FROM `options` 
					WHERE `Content_file_path`=%s and Content_FileName=%s 
					and File_Type=%s and Question_ID=%s""",(filepath,
						filename,ftype,question_id))
				ansopt_id = cursor.fetchone()

				if ansopt_id:
					ansoptid = ansopt_id['Option_ID']
					ans_query = ("""INSERT INTO `answer`(`Question_ID`,
						`Option_ID`) VALUES(%s,%s)""")
				
					ansdata = cursor.execute(ans_query,(question_id,ansoptid))

					if ansdata:
						connection.commit()
						cursor.close()
						return ({"attributes": {
											"status_desc": "Question Details",
			                                "status": "success"
				                            },
				             "responseList": "Question Added"}), status.HTTP_200_OK

		else:
			ques_query = ("""INSERT INTO `question`(`quetion_type`,
				`exam_id`,`section_id`,`set_id`,`marks`,`negative_marks`,
				`difficulty_level`,`solution`,`option_available`,`calculator_available`,
				`topic_id`,`subject_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
			
			quedata = cursor.execute(ques_query,(question_type,exam_id,
				section_id,set_id,marks,negative_marks,difficulty_level,
				solution,option_available,calculator_available,topic_id,subject_id))

			question_id = cursor.lastrowid
			details['question_id'] = question_id

			resourcesdtls = details['resources']
			for re in range(len(resourcesdtls)):
				resource_type = resourcesdtls[re]['resource_type']
				description = resourcesdtls[re]['description']
				sequence = resourcesdtls[re]['sequence']

				setres_query = ("""INSERT INTO `question_resource_mapping`(`question_id`,
					`resource_type`,`description`,`sequence`) VALUES(%s,%s,
					%s,%s)""")
				
				setresdata = cursor.execute(setres_query,(question_id,
					resource_type,description,sequence))

			optionsdtls = details['options']
			Option_Sequence_ID = 1
			for op in range(len(optionsdtls)):
				option = optionsdtls[op]['Option']
				Content_file_path = optionsdtls[op]['Content_file_path']
				Content_FileName = optionsdtls[op]['Content_FileName']
				File_Type = optionsdtls[op]['File_Type']

				opt_query = ("""INSERT INTO `options`(`Question_ID`,
					`Option`,Option_Sequence_ID,Content_file_path,
					Content_FileName,File_Type) VALUES(%s,%s,%s,%s,%s,%s)""")
			
				optdata = cursor.execute(opt_query,(question_id,option,
					Option_Sequence_ID,Content_file_path,
					Content_FileName,File_Type))
				Option_Sequence_ID += 1


			if option_flag == 'y':
				cursor.execute("""SELECT `Option_ID` FROM `options` 
					WHERE `Option`=%s""",(answer))
				ansopt_id = cursor.fetchone()

				if ansopt_id:
					ansoptid = ansopt_id['Option_ID']
					ans_query = ("""INSERT INTO `answer`(`Question_ID`,
						`Option_ID`) VALUES(%s,%s)""")
				
					ansdata = cursor.execute(ans_query,(question_id,ansoptid))

					if ansdata:
						connection.commit()
						cursor.close()
						return ({"attributes": {
											"status_desc": "Question Details",
			                                "status": "success"
				                            },
				             "responseList": "Question Added"}), status.HTTP_200_OK
			else:
				answerpath = answer.split('Image/',1)
				filepath = answerpath[0]+ 'Image/'
				
				filename = answerpath[1] 
				
				filetype = filename.split('.',1)
				
				if filetype[1] == 'jpg' or filetype[1] == 'jpeg' or filetype[1] == 'png':
					ftype = 'Image'
					
				elif filetype == 'txt':
					ftype = 'text'
					
				else:
					ftype = 'video'
					
				cursor.execute("""SELECT `Option_ID` FROM `options` 
					WHERE `Content_file_path`=%s and Content_FileName=%s 
					and File_Type=%s and Question_ID=%s""",(filepath,
						filename,ftype,question_id))
				ansopt_id = cursor.fetchone()

				if ansopt_id:
					ansoptid = ansopt_id['Option_ID']
					ans_query = ("""INSERT INTO `answer`(`Question_ID`,
						`Option_ID`) VALUES(%s,%s)""")
				
					ansdata = cursor.execute(ans_query,(question_id,ansoptid))

					if ansdata:
						connection.commit()
						cursor.close()
						return ({"attributes": {
											"status_desc": "Question Details",
			                                "status": "success"
				                            },
				             "responseList": "Question Added"}), status.HTTP_200_OK

#------------------------------------------------------#			
@name_space.route("/PreviewSectionByExamId/<int:exam_id>")	
class PreviewSectionByExamId(Resource):
	def get(self,exam_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT exam_id,type,name,module_name,
			em.`last_update_ts` FROM `exam_master` em inner join 
			`module` mm on em.`module_id`=mm.`module_id` WHERE 
			`exam_id`=%s""",(exam_id))

		examdtls = cursor.fetchone()
		
		if examdtls:
			examdtls['last_update_ts'] = examdtls['last_update_ts'].isoformat()
			
			cursor.execute("""SELECT section_id,name,section_type,duration 
				FROM `exam_section_master` WHERE `exam_id`=%s""",(exam_id))

			sectiondtls = cursor.fetchall()
			if sectiondtls ==():
				cursor.execute("""SELECT `question_id`,set_id FROM `question` 
					where `exam_id`=%s""",(exam_id))

				setdtls = cursor.fetchall()
				if setdtls == ():
					examdtls['question'] = []

				else:
					for chksid in range(len(setdtls)):
						
						if setdtls != () and setdtls[chksid]['set_id'] == 0:
							cursor.execute("""SELECT `question_id`,quetion_type,set_id,marks,negative_marks, 
								difficulty_level,option_available,calculator_available,
								`solution` FROM `question` where `exam_id`=%s""",(exam_id))

							questiondtls = cursor.fetchall()
							if questiondtls == ():
								examdtls['question'] = []
							else:
								for i in range(len(questiondtls)):
									examdtls['question'] = questiondtls

									cursor.execute("""SELECT `question_resource_id`,`resource_type`,
										`description`,sequence as 'que_sequence' FROM `question_resource_mapping` 
										WHERE `question_id`=%s""",(questiondtls[i]['question_id']))
									questionlist = cursor.fetchall()
									if questionlist == ():
										questiondtls[i]['queresource'] = []
										
									else:
										questiondtls[i]['queresource'] = questionlist
									
									cursor.execute("""SELECT q.`question_id`,Option_ID,`Option`,Content_file_path,
										Content_FileName,File_Type FROM `question` q
										inner join options op on q.`question_id`=op.`Question_ID` where
										q.`Question_ID`=%s""",(questiondtls[i]['question_id']))
									optdtls = cursor.fetchall()
									if optdtls:
										questiondtls[i]['option'] = optdtls

									else:
										questiondtls[i]['option'] = []

									cursor.execute("""SELECT q.`question_id`,
										op.`Option_ID`,`Option`,Content_file_path,
										Content_FileName,File_Type FROM `question` q
										inner join answer a on q.`question_id`=a.`Question_ID`
										inner join options op on a.`Option_ID`=op.`Option_ID` where
										a.`Question_ID`=%s""",(questiondtls[i]['question_id']))
									answerdtls = cursor.fetchone()
									if answerdtls:
										questiondtls[i]['answer'] = answerdtls

									else:
										questiondtls[i]['answer'] = {}

						else:
							cursor.execute("""SELECT `question_id`,quetion_type,`set_id`,marks,negative_marks, 
								difficulty_level,option_available,calculator_available,
								`solution` FROM `question` where `exam_id`=%s""",(exam_id))
							questiondtls = cursor.fetchall()

							if questiondtls == ():
								examdtls['question'] = []
							else:
								for i in range(len(questiondtls)):
									examdtls['question'] = questiondtls

									cursor.execute("""SELECT `set_resource_id`,`resource_type`,
										`description`,sequence as 'que_sequence' FROM `questionset_resource_mapping` 
										WHERE `question_id`=%s""",(questiondtls[i]['question_id']))
									questionlist = cursor.fetchall()
									if questionlist == ():
										questiondtls[i]['queresource'] = []
										
									else:
										questiondtls[i]['queresource'] = questionlist

									cursor.execute("""SELECT q.`question_id`,Option_ID,`Option`,Content_file_path,
										Content_FileName,File_Type FROM `question` q
										inner join options op on q.`question_id`=op.`Question_ID` where
										q.`Question_ID`=%s""",(questiondtls[i]['question_id']))
									optdtls = cursor.fetchall()
									if optdtls:
										questiondtls[i]['option'] = optdtls

									else:
										questiondtls[i]['option'] = []

									cursor.execute("""SELECT q.`question_id`,
										op.`Option_ID`,`Option`,Content_file_path,
										Content_FileName,File_Type FROM `question` q
										inner join answer a on q.`question_id`=a.`Question_ID`
										inner join options op on a.`Option_ID`=op.`Option_ID` where
										a.`Question_ID`=%s""",(questiondtls[i]['question_id']))
									answerdtls = cursor.fetchone()
									if answerdtls:
										questiondtls[i]['answer'] = answerdtls

									else:
										questiondtls[i]['answer'] = {}

			else:
				for secid in range(len(sectiondtls)):
					
					cursor.execute("""SELECT `question_id`,set_id FROM `question` 
						where `section_id`=%s and `exam_id`=%s""",
						(sectiondtls[secid]['section_id'],exam_id))

					setdtls = cursor.fetchall()
					if setdtls == ():
						sectiondtls[secid]['question'] = []
						examdtls['section'] = sectiondtls

					else:
						for chksid in range(len(setdtls)):
							
							if setdtls != () and setdtls[chksid]['set_id'] == 0:
								
								cursor.execute("""SELECT `question_id`,quetion_type,set_id,marks,negative_marks, 
									difficulty_level,option_available,calculator_available,
									`solution` FROM `question` where `section_id`=%s and `exam_id`=%s""",
									(sectiondtls[secid]['section_id'],exam_id))

								questiondtls = cursor.fetchall()
								
								if questiondtls == ():
									sectiondtls[secid]['question'] = []
									examdtls['section'] = sectiondtls
								else:
									for i in range(len(questiondtls)):
										sectiondtls[secid]['question'] = questiondtls
										examdtls['section'] = sectiondtls

										cursor.execute("""SELECT `question_resource_id`,`resource_type`,
											`description`,sequence as 'que_sequence' FROM `question_resource_mapping` 
											WHERE `question_id`=%s""",(questiondtls[i]['question_id']))
										questionlist = cursor.fetchall()
										if questionlist == ():
											questiondtls[i]['queresource'] = []
											
										else:
											questiondtls[i]['queresource'] = questionlist

										cursor.execute("""SELECT q.`question_id`,Option_ID,`Option`,Content_file_path,
											Content_FileName,File_Type FROM `question` q
											inner join options op on q.`question_id`=op.`Question_ID` where
											q.`Question_ID`=%s""",(questiondtls[i]['question_id']))
										optdtls = cursor.fetchall()
										if optdtls:
											questiondtls[i]['option'] = optdtls

										else:
											questiondtls[i]['option'] = []

										cursor.execute("""SELECT q.`question_id`,
											op.`Option_ID`,`Option`,Content_file_path,
											Content_FileName,File_Type FROM `question` q
											inner join answer a on q.`question_id`=a.`Question_ID`
											inner join options op on a.`Option_ID`=op.`Option_ID` where
											a.`Question_ID`=%s""",(questiondtls[i]['question_id']))
										answerdtls = cursor.fetchone()
										if answerdtls:
											questiondtls[i]['answer'] = answerdtls

										else:
											questiondtls[i]['answer'] = {}

							else:
								ursor.execute("""SELECT `question_id`,quetion_type,`set_id`,marks,negative_marks, 
									difficulty_level,option_available,calculator_available,
									`solution` FROM `question`where `section_id`=%s and `exam_id`=%s""",
									(sectiondtls[secid]['section_id'],exam_id))

								questiondtls = cursor.fetchall()

								if questiondtls == ():
									sectiondtls[secid]['question'] = []
									examdtls['section'] = sectiondtls
								else:
									for i in range(len(questiondtls)):
										sectiondtls[secid]['question'] = questiondtls
										examdtls['section'] = sectiondtls

										cursor.execute("""SELECT `set_resource_id`,`resource_type`,
											`description`,sequence as 'que_sequence' FROM `questionset_resource_mapping` 
											WHERE `question_id`=%s""",(questiondtls[i]['question_id']))
										questionlist = cursor.fetchall()
										if questionlist == ():
											questiondtls[i]['queresource'] = []
											
										else:
											questiondtls[i]['queresource'] = questionlist

										cursor.execute("""SELECT q.`question_id`,Option_ID,`Option`,Content_file_path,
											Content_FileName,File_Type FROM `question` q
											inner join options op on q.`question_id`=op.`Question_ID` where
											q.`Question_ID`=%s""",(questiondtls[i]['question_id']))
										optdtls = cursor.fetchall()
										if optdtls:
											questiondtls[i]['option'] = optdtls

										else:
											questiondtls[i]['option'] = []

										cursor.execute("""SELECT q.`question_id`,
											op.`Option_ID`,`Option`,Content_file_path,
											Content_FileName,File_Type FROM `question` q
											inner join answer a on q.`question_id`=a.`Question_ID`
											inner join options op on a.`Option_ID`=op.`Option_ID` where
											a.`Question_ID`=%s""",(questiondtls[i]['question_id']))
										answerdtls = cursor.fetchone()
										if answerdtls:
											questiondtls[i]['answer'] = answerdtls

										else:
											questiondtls[i]['answer'] = {}

		else:
			examdtls = []
			
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Preview Details",
		    		"status": "success"
		    	},
		    	"responseList":examdtls}), status.HTTP_200_OK

#------------------------------------------------------#
@name_space.route("/UpdateExamDetails")
class UpdateExamDetails(Resource):
	@api.expect(update_examdtls)
	def put(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()

		exam_id = details.get('exam_id')
		Name = details.get('name')
		Examtype = details.get('type')
		Module_id = details.get('module_id')
		Section_id = details.get('section_id')
		Course_id = details.get('course_id')
		Liveclass_id = details.get('liveclass_id')
		Fullmarks = details.get('fullmarks')
		Duration = details.get('duration')
		
		cursor.execute("""SELECT `type`,`name`,`module_id`,`section_id`,`course_id`,
			`liveclass_id`,`fullmarks`,`duration` FROM `exam_master` WHERE 
			`exam_id`=%s""",(exam_id))
		examDtls = cursor.fetchone()

		if not Name:
			Name = examDtls.get("name")

		if not Examtype:
			Examtype = examDtls.get("type")

		if not Module_id and Module_id !=0:
			Module_id = examDtls.get("module_id")

		if not Section_id and Section_id !=0:
			Section_id = examDtls.get("section_id")

		if not Course_id and Course_id !=0:
			Course_id = examDtls.get("course_id")

		if not Liveclass_id and Liveclass_id !=0:
			Liveclass_id = examDtls.get("liveclass_id")

		if not Fullmarks:
			Fullmarks = examDtls.get("fullmarks")

		if not Duration:
			Duration = examDtls.get("duration")

		update_query = ("""UPDATE `exam_master` SET `type`=%s,`name`=%s,
			`module_id`=%s,`section_id`=%s,`course_id`=%s,`liveclass_id`=%s,
			`fullmarks`=%s,`duration`=%s WHERE `exam_id`=%s""")
		
		updatedata = cursor.execute(update_query,(Examtype,Name,
			Module_id,Section_id,Course_id,Liveclass_id,Fullmarks,
			Duration,exam_id))

		if updatedata:
			msg = "Updated"
		else:
			msg = "Not Updated"

		connection.commit()
		cursor.close()
		
		return ({"attributes": {
	    				"status_desc": "Update Exam Details",
	    				"status": "success",
	    				"msg": msg
	    				},
	    				"responseList":details}), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/RemoveExamMappingDetails")
class RemoveExamMappingDetails(Resource):
	@api.expect(remove_examdtls)
	def put(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()

		exam_id = details.get('exam_id')
		Module_id = details.get('module_id')
		Section_id = details.get('section_id')
		Course_id = details.get('course_id')
		Liveclass_id = details.get('liveclass_id')
		
		cursor.execute("""SELECT `module_id`,`section_id`,`course_id`,
			`liveclass_id` FROM `exam_master` WHERE `exam_id`=%s""",(exam_id))
		examDtls = cursor.fetchone()

		if not Module_id and Module_id !=0:
			Module_id = examDtls.get("module_id")

		if not Section_id and Section_id !=0:
			Section_id = examDtls.get("section_id")

		if not Course_id and Course_id !=0:
			Course_id = examDtls.get("course_id")

		if not Liveclass_id and Liveclass_id !=0:
			Liveclass_id = examDtls.get("liveclass_id")

		update_query = ("""UPDATE `exam_master` SET `module_id`=%s,
			`section_id`=%s,`course_id`=%s,`liveclass_id`=%s WHERE 
			`exam_id`=%s""")
		
		updatedata = cursor.execute(update_query,(Module_id,Section_id,
			Course_id,Liveclass_id,exam_id))

		if updatedata:
			msg = "Removed"
		else:
			msg = "Unremoved"

		cursor.execute("""SELECT `module_id`,`section_id`,`course_id`,
			`liveclass_id` FROM `exam_master` WHERE `exam_id`=%s""",(exam_id))
		examdtls = cursor.fetchone()
		
		if examdtls['module_id'] == 0 and examdtls['section_id'] == 0 and examdtls['module_id'] ==0 and examdtls['course_id'] == 0 and examdtls['liveclass_id'] == 0:
			
			delete_query = ("""DELETE FROM `exam_master` WHERE `exam_id`=%s""")
			delData = (exam_id)
			cursor.execute(delete_query,delData)

		connection.commit()
		cursor.close()
		
		return ({"attributes": {
	    				"status_desc": "Remove Exam Details",
	    				"status": "success",
	    				"msg": msg
	    				},
	    		"responseList":details}), status.HTTP_200_OK

#--------------------------------------------------------#

#----------------------------------------------------------------------------#
@name_space.route("/GetExamBySectionIdStudentId/<int:section_id>/<int:student_id>")
class GetExamBySectionIdStudentId(Resource):
	def get(self, section_id,student_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		cursor.execute("""SELECT `exam_id`,`type`,`name`,`fullmarks`,`duration`,`last_update_ts` FROM `exam_master`
		 WHERE `section_id` = %s""",(section_id))


		examdata = cursor.fetchall()

		if examdata == ():
			examdata  = []
		else:
			for x in examdata:
				x['last_update_ts'] = x['last_update_ts'].isoformat()

				cursor.execute("""SELECT `exam_id` FROM `student_exam_mapping` WHERE `student_id` = %s AND `exam_id` = %s""",
					(student_id,x['exam_id']))

				exam_status = cursor.fetchone()

				if exam_status:
					x['exam_status'] = "Completed"
				else:
					x['exam_status'] = "Not Completed"

		cursor.close()
		
		return ({"attributes": {
	    				"status_desc": "Exam Detail By Section Id",
	    				"status": "success"
	    				},
				"responseList":examdata}), status.HTTP_200_OK

#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
@name_space.route("/GetExamByModuleIdStudentId/<int:module_id>/<int:student_id>")
class GetExamByModuleIdStudentId(Resource):
	def get(self, module_id,student_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		cursor.execute("""SELECT `exam_id`,`type`,`name`,`fullmarks`,`duration`,`last_update_ts` FROM `exam_master`
		 WHERE `module_id` = %s""",(module_id))


		examdata = cursor.fetchall()

		if examdata == ():
			examdata  = []
		else:
			for x in examdata:
				x['last_update_ts'] = x['last_update_ts'].isoformat()

				cursor.execute("""SELECT `exam_id` FROM `student_exam_mapping` WHERE `student_id` = %s AND `exam_id` = %s""",
					(student_id,x['exam_id']))

				exam_status = cursor.fetchone()

				if exam_status:
					x['exam_status'] = "Completed"
				else:
					x['exam_status'] = "Not Completed"

		cursor.close()
		
		return ({"attributes": {
	    				"status_desc": "Exam Detail By Section Id",
	    				"status": "success"
	    				},
				"responseList":examdata}), status.HTTP_200_OK

#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
@name_space.route("/GetExamByCourseIdStudentId/<int:course_id>/<int:student_id>")
class GetExamByCourseIdStudentId(Resource):
	def get(self, course_id,student_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		cursor.execute("""SELECT `exam_id`,`type`,`name`,`fullmarks`,`duration`,`last_update_ts` FROM `exam_master`
		 WHERE `course_id` = %s""",(course_id))


		examdata = cursor.fetchall()

		if examdata == ():
			examdata  = []
		else:
			for x in examdata:
				x['last_update_ts'] = x['last_update_ts'].isoformat()

				cursor.execute("""SELECT `exam_id` FROM `student_exam_mapping` WHERE `student_id` = %s AND `exam_id` = %s""",
					(student_id,x['exam_id']))

				exam_status = cursor.fetchone()

				if exam_status:
					x['exam_status'] = "Completed"
				else:
					x['exam_status'] = "Not Completed"

		cursor.close()
		
		return ({"attributes": {
	    				"status_desc": "Exam Detail By Section Id",
	    				"status": "success"
	    				},
				"responseList":examdata}), status.HTTP_200_OK

#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
@name_space.route("/GetExamByLiveClassIdStudentId/<int:liveclass_id>/<int:student_id>")
class GetExamByLiveClassIdStudentId(Resource):
	def get(self, liveclass_id,student_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		cursor.execute("""SELECT `exam_id`,`type`,`name`,`fullmarks`,`duration`,`last_update_ts` FROM `exam_master`
		 WHERE `liveclass_id` = %s""",(liveclass_id))


		examdata = cursor.fetchall()

		if examdata == ():
			examdata  = []
		else:
			for x in examdata:
				x['last_update_ts'] = x['last_update_ts'].isoformat()

				cursor.execute("""SELECT `exam_id` FROM `student_exam_mapping` WHERE `student_id` = %s AND `exam_id` = %s""",
					(student_id,x['exam_id']))

				exam_status = cursor.fetchone()

				if exam_status:
					x['exam_status'] = "Completed"
				else:
					x['exam_status'] = "Not Completed"

		cursor.close()
		
		return ({"attributes": {
	    				"status_desc": "Exam Detail By Section Id",
	    				"status": "success"
	    				},
				"responseList":examdata}), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/SectionWiseQuestionDetailsByExamIdSectionId/<int:section_id>/<int:exam_id>")	
class SectionWiseQuestionDetailsByExamIdSectionId(Resource):
	def get(self,section_id,exam_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT count(`question_id`)as count FROM 
			`question` WHERE `section_id`=%s and `exam_id`=%s""",(section_id,exam_id))

		countDtls = cursor.fetchone()
		total_count = countDtls.get('count')
		
		cursor.execute("""SELECT section_id,name,duration 
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
						
						cursor.execute("""SELECT `question_id`,quetion_type,`question_format_type`,marks,negative_marks, 
							difficulty_level,`solution` FROM `question` where `section_id`=%s 
							and `exam_id`=%s order by `question_id` ASC""",(section_id,exam_id))

						questiondtls = cursor.fetchall()
						
						if questiondtls == ():
							sectiondtls['question'] = []
							
						else:
							for i in range(len(questiondtls)):
								sectiondtls['question'] = questiondtls
								
								cursor.execute("""SELECT `question_resource_id`,`resource_type`,
									`description`,sequence as 'que_sequence' FROM `question_resource_mapping` 
									WHERE `question_id`=%s""",(questiondtls[i]['question_id']))
								questionlist = cursor.fetchall()
								if questionlist == None:
									questiondtls[i]['queresourse'] = []
									
								else:
									questiondtls[i]['queresourse'] = questionlist
					else:
						cursor.execute("""SELECT `question_id`,quetion_type,`question_format_type`,
							`set_id`,marks,negative_marks,`solution` FROM `question` where 
							`section_id`=%s and `exam_id`=%s order by `question_id` ASC""",(section_id,exam_id))

						questiondtls = cursor.fetchall()

						if questiondtls == ():
							sectiondtls['question'] = []
							
						else:
							for i in range(len(questiondtls)):
								sectiondtls['question'] = questiondtls
								
								cursor.execute("""SELECT `set_resource_id`,`resource_type`,
									`description`,sequence as 'que_sequence' FROM `questionset_resource_mapping` 
									WHERE `question_id`=%s""",(questiondtls[i]['question_id']))
								questionlist = cursor.fetchall()
								if questionlist == None:
									questiondtls[i]['queresourse'] = []
									
								else:
									questiondtls[i]['queresourse'] = questionlist

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Section Wise Questions Details",
	                            "status": "success",
	                            "total":total_count
								},
	             "responseList": sectiondtls}), status.HTTP_200_OK

#----------------------------------------------------#

