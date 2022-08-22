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
from pytz import timezone
from time import strftime
import pytz
import requests
import calendar
import json
from threading import Thread
import time

app = Flask(__name__)
cors = CORS(app)

myelsa_liveclass = Blueprint('myelsa_liveclass_api', __name__)
api = Api(myelsa_liveclass,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('MyelsaNewLiveClassSection',description='Myelsa New Liveclass Section')


map_liveclass_section = api.model('map_liveclass_section', {
	"liveclass_id":fields.Integer(),
	"section_id":fields.Integer(),
	"module_id":fields.Integer(),
	"goal_id":fields.Integer(),
	"course_id":fields.Integer(),
	"teacher_id":fields.Integer(),
	"institution_id":fields.Integer()
	})

remove_mapliveclass = api.model('remove_mapliveclass', {
	"mapping_id":fields.Integer(),
	"section_id":fields.Integer(),
	"module_id":fields.Integer(),
	"course_id":fields.Integer()
	})
goal_track_section = api.model('goal_track_section',{
	"user_id":fields.Integer(),
	"goal_id":fields.Integer(),
	"institution_id":fields.Integer()
	})
#--------------------------------------------------------#
@name_space.route("/MapLiveclassSection")
class MapAssignmentSection(Resource):
	@api.expect(map_liveclass_section)
	def post(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()
		
		liveclass_id = details.get('liveclass_id')
		section_id = details.get('section_id')
		module_id = details.get('module_id')
		goal_id = details.get('goal_id')
		course_id = details.get('course_id')
		teacher_id = details.get('teacher_id')
		institution_id = details.get('institution_id')
    

		mapp_query = ("""INSERT INTO `course_liveclass_mapping`(`liveclass_id`,
			`section_id`,goal_id,`module_id`,`course_id`,`teacher_id`,`institution_id`) 
			VALUES (%s,%s,%s,%s,%s,%s,%s)""")

		mapp_data = cursor.execute(mapp_query,(liveclass_id,section_id,goal_id,
			module_id,course_id,teacher_id,institution_id))

		if mapp_data:
			msg = "Mapped"
			
		else:
			msg = "Not Mapped"

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Map LiveClass Section",
                                "status": "success",
                                "msg": msg
                                },
	             "responseList": details}), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/CountingLiveClassByTeacherIdInstitutionId/<int:teacher_id>/<int:institution_id>")
class CountingLiveClassByTeacherIdInstitutionId(Resource):
	def get(self,teacher_id,institution_id):
		connection = connect_userLibrary()
		cursor = connection.cursor()
		
		tdate = date.today()
		date_format='%Y-%m-%d %H:%M:%S'
		today = datetime.now(tz=pytz.utc)
		today = today.astimezone(timezone('Asia/Kolkata'))
		now = datetime.strftime(today,'%Y-%m-%d %H:%M:%S')
		todays = datetime.strptime(now,'%Y-%m-%d %H:%M:%S')
		print(todays)

		cursor.execute("""SELECT count(`liveclass_id`)as total FROM `liveclass_mapping` 
			WHERE`teacher_id`=%s and `institution_id`=%s""",(teacher_id,institution_id))

		totalliveclassData = cursor.fetchone()
		if totalliveclassData:
			totalliveclass = totalliveclassData['total']
		else:
			totalliveclass = 0

		cursor.execute("""SELECT count(`liveclass_id`)as total FROM `liveclass_mapping` 
			WHERE date(`start_date`)=%s and `end_date`>=%s and `teacher_id`=%s and 
			`institution_id`=%s""",(tdate,todays,teacher_id,institution_id))

		todaysliveclassData = cursor.fetchone()
		if todaysliveclassData:
			todaysliveclass = todaysliveclassData['total']
		else:
			todaysliveclass = 0

		cursor.execute("""SELECT count(`liveclass_id`)as total FROM `liveclass_mapping` 
			WHERE `start_date`>=%s and `end_date`>=%s and `teacher_id`=%s and 
			`institution_id`=%s""",(tdate,todays,teacher_id,institution_id))

		upcomingliveclassData = cursor.fetchone()
		if upcomingliveclassData:
			upcomingliveclass = upcomingliveclassData['total']
		else:
			upcomingliveclass = 0

		cursor.execute("""SELECT count(`liveclass_id`)as total FROM `liveclass_mapping` 
			WHERE `start_date`<%s and `end_date`<%s and `teacher_id`=%s and 
			`institution_id`=%s""",(todays,todays,teacher_id,institution_id))

		completediveclassData = cursor.fetchone()
		if completediveclassData:
			completedliveclass = completediveclassData['total']
		else:
			completedliveclass = 0

		cursor.close()

		return ({"attributes": {
	    				"status_desc": "LiveClass Count Details",
	    				"status": "success"
	    				},
				"responseList":{
								"totalLiveClass": totalliveclass,
								"todaysLiveClass": todaysliveclass,
								"upcomingLiveClass": upcomingliveclass,
								"completedLiveClass": completedliveclass
								} 
								}), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/GetLiveClassDetailsBySectionId/<int:section_id>")
class GetLiveClassDetailsBySectionId(Resource):
	def get(self, section_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		conn = connect_userLibrary()
		cur = conn.cursor()
		
		classlist = {}
		liveclassList = []
		cursor.execute("""SELECT `liveclass_id` FROM `course_liveclass_mapping` 
			WHERE `section_id`=%s""",(section_id))
		
		livesectiondata = cursor.fetchall()
		if livesectiondata != ():
			for livid in livesectiondata:
				cur.execute("""SELECT `liveclass_id`,`meeting_id`,`zoom_meeting_id`,
					`zoom_uuid`,`zoom_join_url`,`webex_meetingkey`,`webex_hosturl`,
					`webex_attendeeurl`,`webex_meeting_pwd`,`google_meet_url`,
					`start_date`,`end_date`,`location`,`subject`,`description`,
					`platform`,`teacher_id` FROM 
					`liveclass_mapping` WHERE `liveclass_id`=%s and 
					`meeting_status`='created' order by start_date desc""",(livid['liveclass_id']))
				liveclassDtls = cur.fetchone()
				
				if liveclassDtls:
					liveclassDtls['start_date'] = liveclassDtls['start_date'].isoformat()
					liveclassDtls['end_date'] = liveclassDtls['end_date'].isoformat()
				else:
					liveclassDtls['start_date'] = "0000-00-00 00:00:00"
					liveclassDtls['end_date'] = "0000-00-00 00:00:00"
				 
				cur.execute("""SELECT `content_id` FROM `content_library` WHERE 
					`content_id` in(SELECT `content_id` FROM `content_liveclass_mapping` 
					WHERE `liveclass_id` = %s) and `content_name` in 
					('prelive-Dummy','postlive-Dummy') limit 1""",(livid['liveclass_id']))

				assessmentDtls = cur.fetchone()
				assessmentFlag = 'N'
				classlist['assessmentFlag'] = assessmentFlag
				if assessmentDtls:
					assessmentFlag = 'Y'
					classlist['assessmentFlag'] = assessmentFlag

				cur.execute("""SELECT `content_id` FROM `content_library` WHERE 
					`content_id` in(SELECT `content_id` FROM `content_liveclass_mapping` 
					WHERE `liveclass_id` = %s) and `content_name` not in 
					('prelive-Dummy','postlive-Dummy') limit 1""",(livid['liveclass_id']))

				contentDtls = cur.fetchone()
				contentFlag = 'N'
				classlist['contentFlag'] = contentFlag
				
				if contentDtls:
					contentFlag = 'Y'
					classlist['contentFlag'] = contentFlag
				
				cur.execute("""SELECT `Student_ID`,`liveclass_id`,`Status` 
					FROM `student_liveclass_tracking` WHERE `Student_ID`=%s
					and liveclass_id=%s""",
					(liveclassDtls.get('teacher_id'),livid['liveclass_id']))

				teacherclassDtls = cur.fetchone()
				if teacherclassDtls:
					classlist['class_start'] = teacherclassDtls.get('Status')
				else:
					classlist['class_start'] = 'scheduled'

				classlist['liveclass_id'] = liveclassDtls.get('liveclass_id')
				classlist['TEACHER_ID'] = liveclassDtls.get('teacher_id')
				classlist['DESCRIPTION'] = liveclassDtls.get('description')
				classlist['MEETING_ID'] = liveclassDtls.get('meeting_id')
				classlist['LOCATION'] = liveclassDtls.get('location')
				classlist['SUBJECT'] = liveclassDtls.get('subject')
				classlist['START_DATE'] = liveclassDtls['start_date']
				classlist['END_DATE'] = liveclassDtls['end_date']
				classlist['assessmentFlag'] = assessmentFlag
				classlist['contentFlag'] = contentFlag
				classlist['platform'] = liveclassDtls.get('platform')
				classlist['zoom_meeting_id'] = liveclassDtls.get('zoom_meeting_id')
				classlist['zoom_uuid'] = liveclassDtls.get('zoom_uuid')
				classlist['zoom_join_url'] = liveclassDtls.get('zoom_join_url')
				
				if liveclassDtls.get('platform') == 'zoom':
					
					classlist['zoom_meeting_id'] = liveclassDtls.get('zoom_meeting_id')
					classlist['zoom_uuid'] = liveclassDtls.get('zoom_uuid')
					classlist['zoom_join_url'] = liveclassDtls.get('zoom_join_url')
					
				elif liveclassDtls.get('platform') == 'webex':
					classlist['zoom_uuid'] = ""
					classlist['zoom_meeting_id'] = liveclassDtls.get('webex_meetingkey')
					classlist['webex_meeting_pwd'] = liveclassDtls.get('webex_meeting_pwd')
					classlist['zoom_join_url'] = liveclassDtls.get('webex_attendeeurl')
					classlist['webex_attendeeurl'] = liveclassDtls.get('webex_attendeeurl')
					
				elif liveclassDtls.get('platform') == 'google':
	
					classlist['zoom_meeting_id'] = ""
					classlist['zoom_uuid'] = ""
					classlist['zoom_join_url'] = liveclassDtls.get('google_meet_url')
					
				elif clas.get('platform') == 'safemeet':
	
					classlist['zoom_meeting_id'] = ""
					classlist['zoom_uuid'] = ""
					classlist['zoom_join_url'] = liveclassDtls.get('safemeet_url')
					
				liveclassList.append(classlist.copy())
		else:
			totalliveclass = len(livesectiondata)
			liveclassList = []

		cur.close()
		cursor.close()

		return ({"attributes": {
    				"status_desc": "LiveClass Details",
    				"status": "success"
    				},
			"responseList":liveclassList }), status.HTTP_200_OK
	
#--------------------------------------------------------#
@name_space.route("/ScheduleStatusWiseLiveClassListByTeacherIdInstitutionId/<int:teacher_id>/<int:institution_id>")
class ScheduleStatusWiseLiveClassListByTeacherIdInstitutionId(Resource):
	def get(self,teacher_id,institution_id):
		connection = connect_userLibrary()
		cursor = connection.cursor()
		
		tdate = date.today()
		date_format='%Y-%m-%d %H:%M:%S'
		today = datetime.now(tz=pytz.utc)
		today = today.astimezone(timezone('Asia/Kolkata'))
		now = datetime.strftime(today,'%Y-%m-%d %H:%M:%S')
		todays = datetime.strptime(now,'%Y-%m-%d %H:%M:%S')
		
		
		cursor.execute("""SELECT `liveclass_id`,`meeting_id`,`start_date`,
			`end_date`,`subject` FROM `liveclass_mapping` 
			WHERE date(`start_date`)=%s and `end_date`>=%s or 
			`start_date`>=%s and `end_date`>=%sand `teacher_id`=%s and 
			`institution_id`=%s""",(tdate,todays,tdate,todays,teacher_id,institution_id))

		liveclassData = cursor.fetchall()
		if liveclassData == ():
			liveclassData = []
		else:
			for lid in liveclassData:
				lid['start_date'] = lid['start_date'].isoformat()
				lid['end_date'] = lid['end_date'].isoformat()
		
		cursor.close()

		return ({"attributes": {
	    				"status_desc": "LiveClass Details",
	    				"status": "success"
	    				},
				"responseList": liveclassData}), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/TodaysLiveClassListByCourseIdInstitutionId/<int:course_id>/<int:institution_id>")
class TodaysLiveClassListByCourseIdInstitutionId(Resource):
	def get(self,course_id,institution_id):
		connection = connect_userLibrary()
		cursor = connection.cursor()
		conn = connect_elsalibrary()
		cur = conn.cursor()

		tdate = date.today()
		liveclassList = []

		cur.execute("""SELECT `liveclass_id` FROM `course_liveclass_mapping` 
			WHERE `course_id`=%s""",(course_id))

		liveclassData = cur.fetchall()
		if liveclassData == ():
			liveclassList = []
		else:
			for lid in liveclassData:
				cursor.execute("""SELECT `liveclass_id`,`meeting_id`,`start_date`,
					`end_date`,`subject` FROM `liveclass_mapping` WHERE 
					liveclass_id=%s and date(`start_date`)=%s and 
					date(`end_date`)=%s and `institution_id`=%s""",
					(lid['liveclass_id'],tdate,tdate,institution_id))

				todaysliveclass = cursor.fetchone()
				if todaysliveclass:
					todaysliveclass['start_date'] = todaysliveclass['start_date'].isoformat()
					todaysliveclass['end_date'] = todaysliveclass['end_date'].isoformat()
				
					liveclassList.append(todaysliveclass)


		cursor.close()
		cur.close()

		return ({"attributes": {
	    				"status_desc": "Todays LiveClass Details",
	    				"status": "success"
	    				},
				"responseList": liveclassList}), status.HTTP_200_OK

#--------------------------------------------------------#
@name_space.route("/RemoveLiveClassMapping")
class RemoveLiveClassMapping(Resource):
	@api.expect(remove_mapliveclass)
	def put(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()

		mapping_id = details.get('mapping_id')
		Module_id = details.get('module_id')
		Section_id = details.get('section_id')
		Course_id = details.get('course_id')


		cursor.execute("""SELECT `section_id`,`module_id`,`course_id` 
			FROM `course_liveclass_mapping` where `mapping_id`=%s""",(mapping_id))
		mappingdtls = cursor.fetchone()

		if not Module_id and Module_id !=0:
			Module_id = mappingdtls.get("module_id")

		if not Section_id and Section_id !=0:
			Section_id = mappingdtls.get("section_id")

		if not Course_id and Course_id !=0:
			Course_id = mappingdtls.get("course_id")

		update_query = ("""UPDATE `course_liveclass_mapping` SET `section_id`=%s,
			`module_id`=%s,`course_id`=%s WHERE `mapping_id`=%s""")
		
		updatedata = cursor.execute(update_query,(Section_id,Module_id,
			Course_id,mapping_id))

		if updatedata:
			msg = "Removed"
		else:
			msg = "Unremoved"

		cursor.execute("""SELECT `section_id`,`module_id`,`course_id` 
			FROM `course_liveclass_mapping` where `mapping_id`=%s""",(mapping_id))
		mappingdtl = cursor.fetchone()
		
		if mappingdtl['section_id'] == 0 and mappingdtl['module_id'] ==0 and mappingdtl['course_id'] == 0:
			
			delete_query = ("""DELETE FROM `course_liveclass_mapping` WHERE `mapping_id`=%s""")
			delData = (mapping_id)
			cursor.execute(delete_query,delData)

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Remove Liveclass Mapping",
								"status": "success"},
				"responseList": msg}), status.HTTP_200_OK


#-----------------------------------------------------Ritam created api-------------------------------------------------------------------#
#-----------------------------------------------------GET API------------------------------------------------------------------------------#

@name_space.route("/LiveClassListByUserIdAndInstitutionId/<int:user_id>/<int:institution_id>")
class LiveClassListByUserIdAndInstitutionId(Resource):
	def get(self,user_id,institution_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		labconn = connect_userLibrary()
		labcur = labconn.cursor()
		details=[]
		detail=[]
		goals=()
		liveclasses=()
		notrecommendedliveclasses=()
		noliveclass=[]
		
		
		cursor.execute("""SELECT `goal_id` FROM `user_goal_tracking` WHERE `user_id`=%s AND `institution_id`=%s""",(user_id,institution_id))
		goal_id = cursor.fetchall()
		if goal_id != ():
			for i in goal_id:
				details.append(i['goal_id'])
			goals = tuple(details)


		cursor.execute("""SELECT `liveclass_id` FROM `course_liveclass_mapping` WHERE `goal_id`in (%s)""",(goals))
		liveclass_id=cursor.fetchall()
		if liveclass_id != ():
			for i in liveclass_id:
				detail.append(i['liveclass_id'])
			liveclasses = tuple(detail)
		
		labcur.execute("""SELECT `creamson_user_library`.`liveclass_mapping`.`start_date`,`creamson_user_library`.`liveclass_mapping`.`end_date`,`creamson_user_library`.`liveclass_mapping`.`description`,`myelsa_user_library`.`subject`.`subject_name` FROM `creamson_user_library`.`liveclass_mapping` INNER JOIN `myelsa_user_library`.`subject` ON `creamson_user_library`.`liveclass_mapping`.`institution_id`=`myelsa_user_library`.`subject`.`institution_id` WHERE `creamson_user_library`.`liveclass_mapping`.`liveclass_id` in (%s) AND `myelsa_user_library`.`subject`.`subject_id` in (%s)""",(liveclasses,goals))

		liveclasslist = labcur.fetchall()
		
		if liveclasslist == ():
				liveclasslist = []
		else:
			for lid in liveclasslist:
				lid['start_date'] = lid['start_date'].isoformat()
				lid['end_date'] = lid['end_date'].isoformat()
		

		cursor.execute("""SELECT `liveclass_id` FROM `course_liveclass_mapping` WHERE `goal_id` NOT in (%s) AND `institution_id`= %s""",(goals,institution_id))
		not_recommended_live_classlist=cursor.fetchall()
		if not_recommended_live_classlist != ():
			for i in not_recommended_live_classlist:
				noliveclass.append(i['liveclass_id'])
			notrecommendedliveclasses = tuple(noliveclass)
		labcur.execute("""SELECT `creamson_user_library`.`liveclass_mapping`.`start_date`,`creamson_user_library`.`liveclass_mapping`.`end_date`,`creamson_user_library`.`liveclass_mapping`.`description`,`myelsa_user_library`.`subject`.`subject_name` FROM `creamson_user_library`.`liveclass_mapping` INNER JOIN `myelsa_user_library`.`subject` ON `creamson_user_library`.`liveclass_mapping`.`institution_id`=`myelsa_user_library`.`subject`.`institution_id` WHERE `creamson_user_library`.`liveclass_mapping`.`liveclass_id` in (%s) AND `myelsa_user_library`.`subject`.`subject_id` NOT in (%s)""",(notrecommendedliveclasses,goals))

		notrecommendedliveclasslist = labcur.fetchall()
		if notrecommendedliveclasslist == ():
			notrecommendedliveclasslist = []
		else:
			for lid in notrecommendedliveclasslist:
				lid['start_date'] = lid['start_date'].isoformat()
				lid['end_date'] = lid['end_date'].isoformat()

		cursor.close()
		labcur.close()


		return ({"attributes": {"status_desc": "Liveclass List",
	                            "status": "success"
	                            },
	             "recommended": liveclasslist,
	             "not recommended": notrecommendedliveclasslist}), status.HTTP_200_OK

#---------------------------------------------------------------POST API-------------------------------------------------------------------------------#

@name_space.route("/InsertIntoGoalTracker")
class InsertIntoGoalTracker(Resource):
	@api.expect(goal_track_section)
	def post(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()

		user_id = details['user_id']
		goal_id = details['goal_id']
		institution_id = details['institution_id']

		goal_query = ("""INSERT INTO `user_goal_tracking`(`user_id`,
			`goal_id`,`institution_id`) 
			VALUES (%s,%s,%s)""")

		goal_data = cursor.execute(goal_query,(user_id,goal_id,institution_id))

		if goal_data:
			msg = "Inserted"
			
		else:
			msg = "Not Inserted"

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Goal Tracking Section",
                                "status": "success",
                                "msg": msg
                                },
	             "responseList": details}), status.HTTP_200_OK

#------------------------------------------------------------#
@name_space.route("/LiveClassListFilterByGoalUserIdAndInstitutionId/<int:user_id>/<int:institution_id>")
class LiveClassListFilterByGoalUserIdAndInstitutionId(Resource):
	def get(self,user_id,institution_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		labconn = connect_userLibrary()
		labcur = labconn.cursor()
		details = []
		detail = []
		nonliveclass = []
		liveclass = []
		liveclasslist=()
		goals =()
		recommendedlc = []
		nonrecommendedlc = []
		
		
		cursor.execute("""SELECT s.`subject_id`,`subject_name`,`liveclass_id` FROM `subject` s inner join `course_liveclass_mapping` clm on s.`subject_id`=clm.`goal_id` 
			WHERE `subject_id` not in(SELECT `goal_id` FROM `user_goal_tracking` where `user_id`=%s and `institution_id`=%s)  and s.`institution_id`=%s""",
			(user_id,institution_id,institution_id))
		nongoalList = cursor.fetchall()
		
		if nongoalList == ():
			nonrecommendedliveclass= []
		else:
			for lid in nongoalList:
				nonliveclass.append(lid['liveclass_id'])
			nonliveclass = tuple(nonliveclass)

			if len(nonliveclass) >1:
				labcur.execute("""SELECT `start_date`,`end_date`,`description`,`liveclass_id`,`zoom_join_url` FROM `liveclass_mapping` 
					WHERE `liveclass_id` In {}""".format(nonliveclass))
				liveclassDtls = labcur.fetchall()

				if liveclassDtls == ():
					nonrecommendedliveclass = []

				else:
					for lcid in liveclassDtls:
						cursor.execute("""SELECT `goal_id`,subject_name FROM `course_liveclass_mapping` clm inner join `subject` s on clm.`goal_id`=s.`subject_id`
							WHERE `liveclass_id`= %s""",format(lcid['liveclass_id']))
						subData = cursor.fetchone()
						if subData:
							lcid['subject_name'] = subData['subject_name']
						else:
							lcid['subject_name'] = ""
						lcid['start_date'] = lcid['start_date'].isoformat()
						lcid['end_date'] = lcid['end_date'].isoformat()

					nonrecommendedliveclass = liveclassDtls
			else:
				labcur.execute("""SELECT `start_date`,`end_date`,`description`,`liveclass_id`,`zoom_join_url` FROM `liveclass_mapping` 
					WHERE `liveclass_id`=%s""",format(nonliveclass[0]))
				liveclassDtls = labcur.fetchone()
				
				if liveclassDtls == None:
					nonrecommendedliveclass = []

				else:
					cursor.execute("""SELECT `goal_id`,subject_name FROM `course_liveclass_mapping` clm inner join `subject` s on clm.`goal_id`=s.`subject_id`
						WHERE `liveclass_id`= %s""",format(liveclassDtls['liveclass_id']))
					subData = cursor.fetchone()
					if subData:
						liveclassDtls['subject_name'] = subData['subject_name']
					else:
						liveclassDtls['subject_name'] = ""
					liveclassDtls['start_date'] = liveclassDtls['start_date'].isoformat()
					liveclassDtls['end_date'] = liveclassDtls['end_date'].isoformat()
					nonrecommendedlc.append(liveclassDtls.copy())
					nonrecommendedliveclass = nonrecommendedlc
					
				
		cursor.execute("""SELECT `goal_id` FROM `user_goal_tracking` WHERE `user_id`=%s AND `institution_id`=%s""",(user_id,institution_id))
		goalList = cursor.fetchall()
		
		if goalList == ():
			recommendedliveclass = []
			
		else:	
			for i in goalList:
				details.append(i['goal_id'])
			goals = tuple(details)

			if len(goals) >1:

				cursor.execute("""SELECT `liveclass_id` FROM `course_liveclass_mapping` WHERE `goal_id` IN {} and `institution_id`=%s""".format(goals),institution_id)
				liveclassData=cursor.fetchall()

				if liveclassData == ():
					recommendedliveclass = []
				else:
					for lid in liveclassData:
						liveclass.append(lid['liveclass_id'])
					liveclass = tuple(liveclass)

					if len(liveclass) >1:
						labcur.execute("""SELECT `start_date`,`end_date`,`description`,`liveclass_id`,`zoom_join_url` FROM `liveclass_mapping` 
							WHERE `liveclass_id` In {}""".format(liveclass))
						liveclassDtls = labcur.fetchall()

						if liveclassDtls == ():
							recommendedliveclass = []

						else:
							for lcid in liveclassDtls:
								cursor.execute("""SELECT `goal_id`,subject_name FROM `course_liveclass_mapping` clm inner join `subject` s on clm.`goal_id`= s.`subject_id`
									WHERE `liveclass_id`= %s""",format(lcid['liveclass_id']))
								subData = cursor.fetchone()
								if subData:
									lcid['subject_name'] = subData['subject_name']
								else:
									lcid['subject_name'] = ""
								lcid['start_date'] = lcid['start_date'].isoformat()
								lcid['end_date'] = lcid['end_date'].isoformat()

							recommendedliveclass = liveclassDtls
					else:
						labcur.execute("""SELECT `start_date`,`end_date`,`description`,`liveclass_id`,`zoom_join_url` FROM `liveclass_mapping` 
							WHERE `liveclass_id`=%s""",format(liveclass[0]))
						liveclassDtls = labcur.fetchone()

						if liveclassDtls == None:
							recommendedliveclass = []

						else:
							cursor.execute("""SELECT `goal_id`,subject_name FROM `course_liveclass_mapping` clm inner join `subject` s on clm.`goal_id`=s.`subject_id`
								WHERE `liveclass_id`= %s""",format(liveclassDtls['liveclass_id']))
							subData = cursor.fetchone()
							if subData:
								liveclassDtls['subject_name'] = subData['subject_name']
							else:
								liveclassDtls['subject_name'] = ""
							liveclassDtls['start_date'] = liveclassDtls['start_date'].isoformat()
							liveclassDtls['end_date'] = liveclassDtls['end_date'].isoformat()
							recommendedlc.append(liveclassDtls.copy())
							recommendedliveclass = recommendedlc
							
			else:
				cursor.execute("""SELECT `liveclass_id` FROM `course_liveclass_mapping` WHERE `goal_id`= %s""",format(goals[0]))
				liveclassData=cursor.fetchall()

				if liveclassData == ():
					recommendedliveclass = []
				else:
					for lid in liveclassData:
						liveclass.append(lid['liveclass_id'])
					liveclasslist = tuple(liveclass)
					

					if len(liveclass) >1:
						labcur.execute("""SELECT `start_date`,`end_date`,`description`,`liveclass_id`,`zoom_join_url` FROM `liveclass_mapping` 
							WHERE `liveclass_id` in %s""",format(liveclasslist))
						liveclassDtls = labcur.fetchall()

						if liveclassDtls == ():
							recommendedliveclass = []

						else:
							for lcid in liveclassDtls:
								cursor.execute("""SELECT `goal_id`,subject_name FROM `course_liveclass_mapping` clm inner join `subject` s on clm.`goal_id`= s.`subject_id`
									WHERE `liveclass_id`= %s""",format(lcid['liveclass_id']))
								subData = cursor.fetchone()
								if subData:
									lcid['subject_name'] = subData['subject_name']
								else:
									lcid['subject_name'] = ""
								lcid['start_date'] = lcid['start_date'].isoformat()
								lcid['end_date'] = lcid['end_date'].isoformat()

							recommendedliveclass = liveclassDtls
					else:
						labcur.execute("""SELECT `start_date`,`end_date`,`description`,`liveclass_id`,`zoom_join_url` FROM `liveclass_mapping` 
							WHERE `liveclass_id`=%s""",format(liveclasslist[0]))
						liveclassDtls = labcur.fetchone()

						if liveclassDtls == None:
							recommendedliveclass = []

						else:
							cursor.execute("""SELECT `goal_id`,subject_name FROM `course_liveclass_mapping` clm inner join `subject` s on clm.`goal_id`=s.`subject_id`
								WHERE `liveclass_id`= %s""",format(liveclassDtls['liveclass_id']))
							subData = cursor.fetchone()
							if subData:
								liveclassDtls['subject_name'] = subData['subject_name']
							else:
								liveclassDtls['subject_name'] = ""
							liveclassDtls['start_date'] = liveclassDtls['start_date'].isoformat()
							liveclassDtls['end_date'] = liveclassDtls['end_date'].isoformat()

							recommendedlc.append(liveclassDtls.copy())
							recommendedliveclass = recommendedlc
			
		cursor.close()
		labcur.close()
		return ({"attributes": {"status_desc": "Liveclass List",
                            "status": "success"
                            },
             "recommended": recommendedliveclass,
             "not_recommended": nonrecommendedliveclass}), status.HTTP_200_OK
#--------------------------------------------------------------------#

#------------------------------------------------------------------------liveclasslist get api--------------------------------------------------------------------#

@name_space.route("/LiveClassListByUserId/<int:user_id>")
class LiveClassListByUserId(Resource):
	def get(self,user_id):
		connection = connect_userLibrary()
		cursor = connection.cursor()
		details = []
		liveclasslist = []

		cursor.execute("""SELECT `liveclass_id` FROM `liveclass_student_mapping` WHERE `student_id` = %s""",(user_id))
		liveclassidlist = cursor.fetchall()

		for i in liveclassidlist:
			details.append(i["liveclass_id"])
		liveclasses = tuple(details)

		if len(liveclasses)==1:
			cursor.execute("""SELECT `start_date`,`end_date`,`zoom_join_url`,`zoom_meeting_id`,`description`,`liveclass_id` FROM `liveclass_mapping` WHERE `liveclass_id` IN (%s)""",(liveclasses))
			liveclasslist= cursor.fetchall()


			if liveclasslist == ():
				liveclasslist = []
			else:
				for lid in liveclasslist:
					lid['start_date'] = lid['start_date'].isoformat()
					lid['end_date'] = lid['end_date'].isoformat()

			cursor.close()

			return ({"attributes": {"status_desc": "Liveclass List",
	                            "status": "success"
	                            },
	             "responseList": liveclasslist}), status.HTTP_200_OK

		elif len(liveclasses)>1:
			cursor.execute("""SELECT `start_date`,`end_date`,`zoom_join_url`,`zoom_meeting_id`,`description`,`liveclass_id` FROM `liveclass_mapping` WHERE `liveclass_id` IN {}""".format(liveclasses))
			liveclasslist= cursor.fetchall()


			if liveclasslist == ():
				liveclasslist = []
			else:
				for lid in liveclasslist:
					lid['start_date'] = lid['start_date'].isoformat()
					lid['end_date'] = lid['end_date'].isoformat()

			cursor.close()

			return ({"attributes": {"status_desc": "Liveclass List",
	                            "status": "success"
	                            },
	             "responseList": liveclasslist}), status.HTTP_200_OK

#-------------------------------------------------------------liveclass_student_mapping post api-------------------------------------------------------------#
register_liveclass_section = api.model('register_liveclass_section',{
	"liveclass_id" : fields.Integer(),
	"student_id" : fields.Integer(),
	"platform" : fields.String()
	})


@name_space.route("/registeraliveclass")
class registeraliveclass(Resource):
	@api.expect(register_liveclass_section)
	def post(self):
		connection = connect_userLibrary()
		cursor = connection.cursor()
		details = request.get_json()
		detail=[]

		liveclass_id = details["liveclass_id"]
		student_id = details["student_id"]
		platform = details["platform"]

		cursor.execute("""SELECT `liveclass_id` FROM `liveclass_student_mapping` WHERE `student_id` = %s""",(student_id))
		liveclasses = cursor.fetchall()

		for i in liveclasses:
			detail.append(i["liveclass_id"])
		existedliveclass = tuple(detail)

		if liveclass_id in existedliveclass:
			msg = "already registered"
			return ({"attributes": {"status_desc": "liveclass Mapping Section",
                                "status": "success",
                                "msg": msg
                                
                                },
	              "responseList": details}), status.HTTP_200_OK
		else:
			liveclass_query = ("""INSERT INTO `liveclass_student_mapping`(`liveclass_id`,`student_id`,`platform`) VALUES (%s,%s,%s)""")

			liveclass_data = cursor.execute(liveclass_query,(liveclass_id,student_id,platform))

			if liveclass_data:
				msg = "Inserted"
			else:
				msg = "Not Inserted"

			connection.commit()
			cursor.close()

			return ({"attributes": {"status_desc": "liveclass Mapping Section",
                                "status": "success",
                                "msg": msg
                                },
	             "responseList": details}), status.HTTP_200_OK