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
import math 
app = Flask(__name__)
cors = CORS(app)

def connect_b2c():
	connection = pymysql.connect(host='creamsonservices.com',
									user='creamson_langlab',
									password='Langlab@123',
									db='creamson__lang_lab_b2c',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor)
	return connection

mycomm_controller = Blueprint('cce_controller_api', __name__)
api = Api(mycomm_controller,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('CCEController',description='CCE Controller')
name_space1 = api.namespace('moduleAssessmentController',description='Assessment Controller')
BASE_URL = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/'
# BASE_URL = 'http://127.0.0.1:5000/'
studentActivityAndContentModel = api.model('studentActivityAndContent Model', {
												"studentActivityFileName": fields.String(),
												"studentActivityPath": fields.String(),
												"activityId": fields.Integer(required=True),
												"activityMappingId": fields.Integer(required=True),
												"contentMasterId": fields.Integer(required=True),
												"studentActivityEndTs": fields.String(),
												"fileTypeId": fields.Integer(),
												"lastUpdateId": fields.Integer(),
												"lastUpdateTs": fields.String(),
												"level": fields.Integer(required=True),
												"studentActivityStartTs": fields.String(),
												"status": fields.String(),
												"studentId":fields.Integer(required=True) 
											})

studentFilepath = api.model('studentFilepath', 
								{"studentActivityFilepath": fields.String(),
									"session_id":fields.Integer(required=True,default=0),
									"level":fields.Integer(required=True),
									"activityId": fields.Integer(required=True),
									"contentMasterId": fields.Integer(required=True),
									"studentId":fields.Integer(required=True)
									})

answer_details = api.model('answer details', {
	"question_id":fields.Integer(required=True),
	"option_id":fields.Integer(required=True),
	"answer":fields.String(),
	})

submit_answers = api.model('Submit Answers', {
	"answer_details":fields.List(fields.Nested(answer_details)),
	"status":fields.String(required=True),
	"level":fields.Integer(required=True),
	"time_taken":fields.String(required=True),
	"marks":fields.Integer(required=True),
	"assessment_id":fields.Integer(required=True),
	"student_id":fields.Integer(required=True)
	})


@name_space.route("/postStudentActivityDetails")
class postStudentActivityDetails(Resource):
	@api.expect(studentActivityAndContentModel)
	def post(self):
		connection = connect_b2c()
		cursor = connection.cursor()

		details = request.get_json()

		activity_mapping_id = details['activityMappingId']
		content_master_id = details['contentMasterId']
		file_type_id = details['fileTypeId']
		last_update_id = details['lastUpdateId']
		last_update_ts = details['lastUpdateTs']
		lastTS = datetime.fromtimestamp(last_update_ts/1000).strftime('%Y-%m-%d %H:%M:%S')
		level = details['level']
		u_status = details['status']
		student_activity_end_ts = details['studentActivityEndTs']
		endTS = datetime.fromtimestamp(student_activity_end_ts/1000).strftime('%Y-%m-%d %H:%M:%S')
		student_activity_path = details['studentActivityPath']
		student_id = details['studentId']
		student_activity_start_ts = details['studentActivityStartTs']
		startTS = datetime.fromtimestamp(student_activity_start_ts/1000).strftime('%Y-%m-%d %H:%M:%S')
		student_activity_file_name = details['studentActivityFileName']

		stdntActContInsertQuery = ("""INSERT INTO `student_activity_n_content_tracking`(`activity_mapping_id`, 
			`content_master_id`, `file_type_id`, `last_update_id`, `last_update_ts`, `level`, `status`, 
			`student_activity_end_ts`, `student_activity_path`, `student_id`, 
			`student_activity_start_ts`, `student_activity_file_name`) 
			VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

		stdntActContData = (activity_mapping_id,content_master_id,file_type_id,student_id,lastTS,
			level,u_status,endTS,student_activity_path,student_id,startTS,student_activity_file_name)

		cursor.execute(stdntActContInsertQuery,stdntActContData)

		sacId = cursor.lastrowid

		details['sacId'] = sacId
		if u_status.lower() == 'c':
			getPercenatgeIncrease = requests.get(BASE_URL + 'mycommunication/CCEController/getPercenatgeIncreaseAndContentMasterNoByActivityIdAndLevel/{}/{}'.format(activity_mapping_id,level)).json()
			getActivityPercentageByStudentId = requests.get(BASE_URL + 'mycommunication/CCEController/getActivityPercentageByStudentId/{}/{}/{}'.format(student_id,activity_mapping_id,level)).json()
			activityPercentage = getActivityPercentageByStudentId.get('responseList')
			if not activityPercentage:
				activityProgressInsertQuery = ("""INSERT INTO `student_activity_progress`(`activity_id`, 
					`student_id`, `activity_progress_percentage`, `last_update_id`, `last_update_ts`, 
					`level`) VALUES (%s,%s,%s,%s,%s,%s)""")

				progressData = (activity_mapping_id,student_id,getPercenatgeIncrease.get('responseList',0),
					student_id,lastTS,level)

				cursor.execute(activityProgressInsertQuery,progressData)
			else:
				if int(activityPercentage) < 100:
					totalProgress = int(activityPercentage) + math.ceil(getPercenatgeIncrease.get('responseList',0))
				else:
					totalProgress = int(activityPercentage)
				if totalProgress >= 100:
					totalProgress = 100
				activityProgressUpdateQuery = ("""UPDATE `student_activity_progress` 
					SET `activity_progress_percentage` = %s, `last_update_ts` = %s 
					WHERE `activity_id` = %s and `student_id` = %s and `level` = %s""")

				progressDataUpdate = (totalProgress,lastTS,activity_mapping_id,student_id,level)

				cursor.execute(activityProgressUpdateQuery,progressDataUpdate)
			connection.commit()
			getOverallActivityPercentageByStudentId = requests.get(BASE_URL + 'mycommunication/CCEController/getOverallActivityPercentageByStudentIdAndLevel/{}/{}'.format(student_id,level)).json()
			
			overallPercent = getOverallActivityPercentageByStudentId.get('responseList')

			getLevelByStudentId = requests.get(BASE_URL + 'mycommunication/CCEController/getLevelByStudentId/{}'.format(student_id)).json()
			
			oldLevel = getLevelByStudentId.get('responseList')
			newLevel = 1
			if oldLevel == 0:
				oldLevel += 1
				levelInsertQuery = ("""INSERT INTO `student_level_tracking`(`Last_Update_TS`, 
					`New_Level`, `Old_Level`, `Student_ID`) VALUES (%s,%s,%s,%s)""")

				levelData = (lastTS,newLevel,oldLevel,student_id)

				cursor.execute(levelInsertQuery,levelData)
			else:
				if overallPercent == 400:
					oldLevel += 1
					newLevel = oldLevel + 1
					levelUpdateQuery = ("""UPDATE `student_level_tracking` SET `New_Level` = %s, 
						`Old_Level` = %s,`Last_Update_TS` = %s WHERE `Student_ID` =%s""")
					levelUpdateData = (newLevel,oldLevel,lastTS,student_id)
					cursor.execute(levelUpdateQuery,levelUpdateData)
					details['newLevel'] = newLevel
				else:
					newLevel = oldLevel
		
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Activity Content Successfully Completed",
								"status": "success"
								},
				"responseList": details}), status.HTTP_200_OK

@name_space.route("/getPercenatgeIncreaseAndContentMasterNoByActivityIdAndLevel/<int:activity_id>/<int:level>")
class getActivityPercentageIncrease(Resource):
	def get(self,activity_id,level):
		connection = connect_b2c()
		cursor = connection.cursor()

		cursor.execute("""SELECT 100/count(cr.`Content_Master_ID`) as 'percentage' 
			from content_rule cr,activity_mapping am 
			where am.`Activity_Mapping_ID`=cr.`Activity_Mapping_ID` 
			and am.`Activity_ID`= %s and cr.`Level`= %s""",(activity_id,level))

		percentDtls = cursor.fetchone()
		percent = float(round(percentDtls.get('percentage'),2))

		return ({"attributes": {"status_desc": "Activity Percent Increase Info.",
								"status": "success"
								},
				"responseList": percent}), status.HTTP_200_OK

@name_space.route("/getActivityPercentageByStudentId/<int:student_id>/<int:activity_id>/<int:level>")
class getActivityPercentageByStudentId(Resource):
	def get(self,student_id,activity_id,level):
		connection = connect_b2c()
		cursor = connection.cursor()

		cursor.execute("""SELECT `activity_progress_percentage` as 'percentage' FROM `student_activity_progress` 
			WHERE `student_id` = %s AND `activity_id` = %s 
			AND `level` = %s""",(student_id,activity_id,level))

		percentDtls = cursor.fetchone()
		
		if not percentDtls:
			percent = None
		else:
			percent = int(percentDtls.get('percentage',0))
		return ({"attributes": {"status_desc": "Overall Percent Info.",
								"status": "success"
								},
				"responseList": percent}), status.HTTP_200_OK


@name_space.route("/getOverallActivityPercentageByStudentIdAndLevel/<int:student_id>/<int:level>")
class getOverallActivityPercentageByStudentIdAndLevel(Resource):
	def get(self,student_id,level):
		connection = connect_b2c()
		cursor = connection.cursor()

		cursor.execute("""SELECT sum(`activity_progress_percentage`) as 'percentage' FROM `student_activity_progress` 
			WHERE `student_id` = %s and `level` = %s""",(student_id,level))

		percentDtls = cursor.fetchone()

		if not percentDtls.get('percentage'):
			percent = 0
		else:
			percent = int(percentDtls.get('percentage',0))

		return ({"attributes": {"status_desc": "Overall Percent Info.",
								"status": "success"
								},
				"responseList": percent}), status.HTTP_200_OK

@name_space.route("/getLevelByStudentId/<int:student_id>")
class getLevelByStudentId(Resource):
	def get(self,student_id):
		connection = connect_b2c()
		cursor = connection.cursor()
		levelDtls = {}
		cursor.execute("""SELECT `Old_Level` FROM `student_level_tracking` 
			WHERE `Student_ID` = %s""",(student_id))

		levelDtls = cursor.fetchone()
		if not levelDtls:
			level = 0
		else:
			level = int(levelDtls.get('Old_Level',0))
		return ({"attributes": {"status_desc": "Level Info.",
								"status": "success"
								},
				"responseList": level}), status.HTTP_200_OK


@name_space.route("/getActivityPercentageByStudentIdAndLevel/<int:student_id>/<int:level>")
class getActivityPercentageByStudentIdAndLevel(Resource):
	def get(self,student_id,level):
		connection = connect_b2c()
		cursor = connection.cursor()

		cursor.execute("""SELECT act.`activity_id`, ( SELECT `Activity_Desc` FROM `activity` ac 
			WHERE ac.`Activity_ID` = act.`activity_id` ) AS 'activityDesc', 
			`activity_progress_percentage` AS 'percentage' FROM `student_activity_progress` sap 
			RIGHT JOIN `activity_mapping` act ON sap.`activity_id` = act.`activity_id` 
			AND `student_id` = %s AND `level` = %s 
			WHERE act.`Dashboard_Activity_Id` = 1""",(student_id,level))

		percentDtls = cursor.fetchall()
		for pid, per in enumerate(percentDtls):
			if per.get('percentage') == None:
				per['percentage'] = 0
			print(per.get('percentage'))
		return ({"attributes": {"status_desc": "Activity Percent Info.",
								"status": "success"
								},
				"responseList": percentDtls}), status.HTTP_200_OK


@name_space.route("/getListOfCompletedModuleByStudentId/<int:student_id>")
class getListOfCompletedModuleByStudentId(Resource):
	def get(self,student_id):
		connection = connect_b2c()
		cursor = connection.cursor()
		complete = []
		incomplete = []
		cursor.execute("""SELECT level,sum(`activity_progress_percentage`)/4 as 'percent',
			IF(sum(`activity_progress_percentage`)=400,'C','I') as 'Status' FROM `student_activity_progress` sap 
			WHERE `student_id` = %s group by `level`""",(student_id))

		percentDtls = cursor.fetchall()
		for pid,per in enumerate(percentDtls):
			per['percent'] = int(per.get('percent',0))
			if per.get('Status') == 'C':
				complete.append(per)
			else:
				incomplete.append(per)

		moduleDtls = {'complete':complete,
						'incomplete':incomplete}
		return ({"attributes": {"status_desc": "List of Modules",
								"status": "success"
								},
				"responseList": complete}), status.HTTP_200_OK


@name_space.route("/getModuleDtlsByStudentId/<int:student_id>")
class getModuleDtlsByStudentId(Resource):
	def get(self,student_id):
		connection = connect_b2c()
		cursor = connection.cursor()
		complete = []
		incomplete = []
		cursor.execute("""SELECT MAX(`last_update_ts`) as 'completionDate', level, 
			sum(`activity_progress_percentage`)/4 as 'percent',
			IF(sum(`activity_progress_percentage`)=400,'C','I') as 'Status' FROM `student_activity_progress` sap 
			WHERE `student_id` = %s group by `level`""",(student_id))

		percentDtls = cursor.fetchall()
		for pid,per in enumerate(percentDtls):
			per['completionDate'] = per.get('completionDate').isoformat().replace('T',' ')
			level = per.get('level',0)
			activityDtls = requests.get(BASE_URL + 'mycommunication/CCEController/getActivityPercentageByStudentIdAndLevel/{}/{}'.format(student_id,level)).json()
			per['activityDtls'] = activityDtls.get('responseList')
			per['percent'] = int(per.get('percent',0))
			per['assessmentPercent'] = 0
			if per.get('Status') == 'C':
				cursor.execute("""SELECT `Last_Update_TS` as 'completionDate',`Marks` FROM `student_assessment_tracking` 
					WHERE `Student_Id` = %s and `level` = %s 
					and `Last_Update_TS` = (SELECT max(`Last_Update_TS`) 
					FROM `student_assessment_tracking` WHERE `Student_Id` = %s 
					and `level` = %s )""",(student_id,level,student_id,level))

				assessmentResult = cursor.fetchone()
				if assessmentResult:
					per['completionDate'] = assessmentResult.get('completionDate').isoformat().replace('T',' ')
					per['assessmentPercent'] = assessmentResult.get('Marks',0)
				complete.append(per)
			else:
				incomplete.append(per)

		moduleDtls = {'complete':complete,
						'incomplete':incomplete}
		return ({"attributes": {"status_desc": "List of Modules",
								"status": "success"
								},
				"responseList": moduleDtls}), status.HTTP_200_OK

@name_space.route("/getOverallProgressbyStudentId/<int:student_id>")
class getOverallProgress(Resource):
	def get(self,student_id):
		connection = connect_b2c()
		cursor = connection.cursor()

		cursor.execute("""SELECT DISTINCT am.`activity_mapping_id` as 'activity_id', act.`Activity_Desc` as 'activityDesc',
			(COUNT(DISTINCT sat.`content_master_id`)/COUNT(DISTINCT cr.`Content_Master_ID`))*100 as 'percentage' 
			FROM `activity_mapping` am LEFT JOIN `student_activity_n_content_tracking` sat 
			ON am.`Activity_Mapping_ID` = sat.`Activity_Mapping_ID` AND `student_id` = %s 
			AND `status` = 'c' INNER JOIN `content_rule` cr 
			ON am.`Activity_Mapping_ID` = cr.`Activity_Mapping_ID` 
			INNER JOIN `activity` act on am.`Activity_ID` = act.`Activity_ID`
			WHERE am.`Dashboard_Activity_Id` = 1 GROUP BY am.`Activity_Mapping_ID` 
			ORDER BY am.`Activity_Mapping_ID` ASC""",(student_id))

		contentDtls = cursor.fetchall()
		for pid,per in enumerate(contentDtls):
			per['percentage'] = int(per.get('percentage',0))
		assessmentDtls = []
		overallprogress = {'contentProgress':contentDtls,
							'assessmentProgress':assessmentDtls}
		return ({"attributes": {"status_desc": "Content And Assessment Progress Details",
								"status": "success"
								},
				"responseList": overallprogress}), status.HTTP_200_OK


@name_space1.route("/getAssessmentsAfterModuleCompletion/<int:level>")
class getAssessmentsAfterModuleCompletion(Resource):
	def get(self,level):
		connection = connect_b2c()
		cursor = connection.cursor()

		cursor.execute("""SELECT `assessment_id` FROM `level_assessment_mapping` 
			WHERE `level` = %s""",(level))

		assessmentDtls = cursor.fetchone()
		if assessmentDtls:
			assessment_id = assessmentDtls['assessment_id']

			getUrl = 'http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com:8080/AssessmentModuleB2C/assessment/{}'.format(assessment_id)

			getResponse = requests.get(getUrl).json()
			cid = getResponse['attributes']['content-id']
			print(cid)

			return getResponse
		else:
			return {"attributes": {"status_desc": "No assessment found for provided level",
									"status": "not-found"},
					"responseList": {}
					}

@name_space.route("/postStudentFilepath")
class postStudentFilepath(Resource):
	@api.expect(studentFilepath)
	def post(self):
		connection = connect_b2c()
		cursor = connection.cursor()

		details = request.get_json()

		session_id = details.get('session_id')
		studentActivityFilepath = details.get('studentActivityFilepath','')
		level = details.get('level')
		activityId = details.get('activityId')
		contentMasterId = details.get('contentMasterId')
		studentId = details.get('studentId')

		fileInsertQuery = ("""INSERT INTO `student_activity_filepath`(`session_id`, `student_id`, 
				`activity_filepath`) VALUES (%s,%s,%s)""")

		if session_id == 0:
			sessionInsertQuery = ("""INSERT INTO `session_mapping`( `student_id`, `Level`, 
				`Content_master_ID`, `activity_id`) VALUES (%s,%s,%s,%s)""")
			sessionData = (studentId,level,contentMasterId,activityId)

			cursor.execute(sessionInsertQuery,sessionData)

			session_id = cursor.lastrowid

			
		fileData = (session_id,studentId,studentActivityFilepath)
		cursor.execute(fileInsertQuery,fileData)
		connection.commit()
		cursor.close()
		return {"attributes": {"status_desc": "File Upload Details",
								"status": "success"},
				"responseList": {"session_id":session_id}
				}



@name_space1.route("/postStudentAssessmentAnswer")
class postStudentAssessmentAnswer(Resource):
	@api.expect(submit_answers)
	def post(self):
		connection = connect_b2c()
		cursor = connection.cursor()

		details = request.get_json()

		answer_details = details['answer_details']
		completion_status = details['status']
		level = details['level']
		time_taken = details['time_taken']
		marks = details['marks']
		assessment_id = details['assessment_id']
		student_id = details['student_id']

		trackingInsertQuery = ("""INSERT INTO `student_assessment_tracking`(`Student_Id`, `level`, 
			`Time_taken`, `Marks`, `Status`, `Assessment_Id`) VALUES (%s,%s,%s,%s,%s,%s)""")
		trackingData = (student_id,level,time_taken,marks,completion_status,assessment_id)

		cursor.execute(trackingInsertQuery,trackingData)
		tracking_id = cursor.lastrowid
		for a, ans in enumerate(answer_details):
			question_id = ans['question_id']
			option_id = ans['option_id']
			answer = ans['answer']
			submit_answer_insert_query = ("""INSERT INTO `student_answers`(`Assessment_ID`, 
				`Student_ID`, `Question_ID`, `Option_ID`, `Answer`,`assessment_tracking_id`) 
				VALUES (%s,%s,%s,%s,%s,%s)""")

			submit_data = (assessment_id,student_id,question_id,option_id,answer,tracking_id)

			cursor.execute(submit_answer_insert_query,submit_data)


		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Submit Answer",
								"status": "success"},
				"responseList": 'Answers Submitted Successfully'}), status.HTTP_200_OK

