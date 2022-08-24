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
from threading import Thread
import time
import utils
app = Flask(__name__)
cors = CORS(app)

#----------------------database-connection---------------------#
'''def mysql_connection():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='creamson_user_library',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

def mysql_next_connection():
    connection = pymysql.connect(host='creamsonservices.com',
                                user='creamson_langlab',
                                password='Langlab@123',
                                db='creamson_logindb',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
    return connection'''

def lab_lang():
    connection = pymysql.connect(host='creamsonservices.com',
                                user='creamson_langlab',
                                password='Langlab@123',
                                db='creamson_lab_lang1',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
    return connection

#----------------------database-connection---------------------#

def mysql_connection():
	connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
	                             user='admin',
	                             password='cbdHoRPQPRfTdC0uSPLt',
	                             db='creamson_user_library',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

def mysql_next_connection():
    connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
                                user='admin',
                                password='cbdHoRPQPRfTdC0uSPLt',
                                db='creamson_logindb',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
    return connection



my_Library = Blueprint('my_Library_api', __name__)
api = Api(my_Library,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('myLibrary',description='MY Library')

#-----------------------update-group-name-model-----------------------#

updategroupname = api.model('updategroupname', {
    "Group_Description":fields.String(),
    "Group_ID":fields.Integer(),
    "User_ID":fields.Integer()
    })

#-----------------------update-group-name-model-------------------------#

#-----------------------contentTracking-model-----------------------#

contentTracking = api.model('contentTracking', {
	"Student_ID":fields.Integer(),
	"Content_ID":fields.Integer(),
	"Student_Content_Start_TS":fields.String(),
	"Student_Content_End_TS":fields.String(),
	"Duration":fields.Integer(),
	"Student_Content_Path":fields.String(),
	"Student_Content_FileName":fields.String(),
	"Status":fields.String(),
	"file_type_id":fields.String(),
	"Last_Update_ID":fields.Integer()
	})

#-----------------------contentTracking-model-----------------------#

#-----------------------liveclassTracking-model-----------------------#

liveclassTracking = api.model('liveclassTracking', {
	"Student_ID":fields.Integer(),
	"liveclass_id":fields.Integer(),
	"Student_Content_Start_TS":fields.String(),
	"Student_Content_End_TS":fields.String(),
	"Duration":fields.Integer(),
	"Student_Content_Path":fields.String(),
	"Student_Content_FileName":fields.String(),
	"Status":fields.String(),
	"file_type_id":fields.String(),
	"Last_Update_ID":fields.Integer()
	})

#-----------------------liveclassTracking-model-----------------------#

#-----------------------assignment-group-model---------------------------#

assigngroup = api.model('assigngroup', {
	"assignment_id":fields.Integer(),
	"group_id":fields.Integer(),
	"last_update_id":fields.Integer(),
	"assignment_duedate":fields.String()
	})
assigngroupDtls=api.model('assigngroupDtls', {
	"assigngroup":fields.List(fields.Nested(assigngroup))
	})
#-----------------------assignment-group-model------------------------------#

#-----------------------update-assignment-status-model-----------------------#

updatestatus = api.model('updatestatus', {
	"Assignment_Status":fields.String(),
    "Assignment_ID":fields.Integer(),
    "Student_UserID":fields.Integer()
    })

#-----------------------update-assignment-status-model-------------------------#

#-----------------------submit-student-assignment-model-----------------------#


substuassignment = api.model('substuassignment', {
	"Assignment_ID":fields.Integer(),
	"Content_Path":fields.String(),
	"Student_Id":fields.Integer(),
	"Progress":fields.String(),
	"Content_Type":fields.String()
	})
substuassignmentDtls=api.model('substuassignmentDtls', {
	"substuassignment":fields.List(fields.Nested(substuassignment))
	})
#-----------------------submit-student-assignment-model-----------------------#

#-----------------------create-teacher-assignment-model-----------------------#
assignmentfile = api.model('assignmentfile', {
	"Assignment_ID":fields.Integer(),
	"Content_ID":fields.Integer(),
	"File_type":fields.String(),
	"File_Path":fields.String(),
	"Last_updated_ID":fields.Integer()
	})
assignmentfileDtls=api.model('assignmentfileDtls', {
	"assignmentfile":fields.List(fields.Nested(assignmentfile))
	})
#-----------------------create-teacher-assignment-model-----------------------#

#-----------------------update-assignment-file-model-----------------------#

updatefile = api.model('updatefile', {
	"Assignment_ID":fields.Integer(),
    "File_Path":fields.String(),
    "File_type":fields.String()
    })

#-----------------------update-assignment-file-model-------------------------#

#--------------------------------create-group-------------------------------#
creategroup = api.model('creategroup', {
	  "groupDescription": fields.String(),
	  "institutionID":fields.Integer(),
	  "teacherId": fields.Integer()
	  })
#--------------------------------create-group-------------------------------#
student_assignment_mapping_model = api.model('student_assignment_mapping_model', {
	"assignment_id":fields.Integer(),
	"group_id":fields.List(fields.Integer()),
	"teacher_id":fields.Integer(),
	"assignment_duedate":fields.String(),
	"student_id":fields.List(fields.Integer()),
	"is_group":fields.String()
	})

# BASE_URL = 'http://127.0.0.1:5000/'

BASE_URL = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/'
#-----------------------contentTracking--------------------------------------#
@name_space.route("/student_content_tarcking")
class teacher_content_tarcking(Resource):
	@api.expect(contentTracking)
	def post(self):
		details = request.get_json()
		connection = mysql_connection()
		cursor = connection.cursor()
		# currentDate = date.today().strftime("%d%b%y")
		
		Student_ID = details['Student_ID']
		Content_ID = details['Content_ID']
		Student_Content_Start_TS = details['Student_Content_Start_TS']
		Student_Content_End_TS = details['Student_Content_End_TS']
		Duration = details['Duration']
		Student_Content_Path = details['Student_Content_Path']
		Student_Content_FileName = details['Student_Content_FileName']
		Status = details['Status']
		Last_Update_ID = details['Last_Update_ID']
		file_type_id = details['file_type_id']

		content_tracking_query = ("""INSERT INTO `student_content_tracking`(
			`Student_ID`, `Content_ID`,`Student_Content_Start_TS`, 
			`Student_Content_End_TS`, `Duration`, `Student_Content_Path`, 
			`Student_Content_FileName`, `Status`, `Last_Update_ID`, `file_type_id`) VALUES (%s,
			%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
		content_tracking_data = (Student_ID,Content_ID,Student_Content_Start_TS,
			Student_Content_End_TS,Duration,Student_Content_Path, 
			Student_Content_FileName,Status,Last_Update_ID,file_type_id)

		trackdata = cursor.execute(content_tracking_query,content_tracking_data)
		connection.commit()
		if trackdata:
			return ({"attributes": {"status_desc": "Content Tracking Details",
	                                "status": "success"
	                                }
	                 }), status.HTTP_200_OK

#-----------------------contentTracking--------------------------------------#

#-----------------------student-liveclassTracking-----------------------------#

@name_space.route("/studentLiveclassTarcking")
class studentLiveclassTarcking(Resource):
	@api.expect(liveclassTracking)
	def post(self):
		details = request.get_json()
		connection = mysql_connection()
		cursor = connection.cursor()
		# currentDate = date.today().strftime("%d%b%y")
		
		Student_ID = details['Student_ID']
		liveclass_id = details['liveclass_id']
		Student_Content_Start_TS = details['Student_Content_Start_TS']
		Student_Content_End_TS = details['Student_Content_End_TS']
		Duration = details['Duration']
		Student_Content_Path = details['Student_Content_Path']
		Student_Content_FileName = details['Student_Content_FileName']
		Status = details['Status']
		Last_Update_ID = details['Last_Update_ID']
		file_type_id = details['file_type_id']


		liveclass_tracking_query = ("""INSERT INTO `student_liveclass_tracking`(
			`Student_ID`, `liveclass_id`,`Student_Content_Start_TS`, 
			`Student_Content_End_TS`, `Duration`, `Student_Content_Path`, 
			`Student_Content_FileName`, `Status`, `Last_Update_ID`,`file_type_id`) VALUES (%s,
			%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
		liveclass_tracking_data = (Student_ID,liveclass_id,Student_Content_Start_TS,
			Student_Content_End_TS,Duration,Student_Content_Path, 
			Student_Content_FileName,Status,Last_Update_ID,file_type_id)

		trackdata = cursor.execute(liveclass_tracking_query,liveclass_tracking_data)
		connection.commit()
		if trackdata:
			return ({"attributes": {"status_desc": "LiveClass Tracking Added",
	                                "status": "success"
	                                }
	                 }), status.HTTP_200_OK

#-----------------------student-liveclassTracking-----------------------------#

#-----------------------------update-group-name-----------------------------#
@name_space.route("/updateGroupNameByGroupID")
class updateGroupNameByGroupID(Resource):
    @api.expect(updategroupname)
    def put(self):
        details = request.get_json()
        nextconnection = mysql_next_connection()
        nextcursor = nextconnection.cursor()
        
        Group_Description = details['Group_Description']
        Group_ID = details['Group_ID']
        User_ID = details['User_ID']
        
        update_group_name = ("""UPDATE `group_master` SET `Group_Description`= %s,`Last_Update_ID`
        	=%s WHERE `Group_ID`=%s""")
        update_group_data = (Group_Description,User_ID,Group_ID)
        nextcursor.execute(update_group_name,update_group_data)

        
        return ({"attributes": {"status_desc": "Student Document Update Details.",
                            "status": "success"
                            },
                            "responseList":details}), status.HTTP_200_OK

#-----------------------------update-group-name-----------------------------#

#-----------------------get-batch-dtls-by-ins-id---------------------------------------#
@name_space.route("/getGroupDtlsInstitutionId/<int:institution_id>")
class getGroupDtlsInstitutionId(Resource):
    def get(self,institution_id):
        nextconnection = mysql_next_connection()
        nextcursor = nextconnection.cursor()

        nextcursor.execute("""SELECT `Group_ID`as groupID,`Group_Description` as groupDescription,
		    	group_master.`Institution_ID`as institutionID,
		    	(SELECT count(`Student_Id`) FROM `group_student_mapping` WHERE  
		    	group_master.`Group_ID`=group_student_mapping.`Group_ID`)as total_student,
		    	group_master.`Last_Update_ID` as lASTUPDATEID,group_master.`LAST_UPDATE_TIMESTAMP` 
		    	as lASTUPDATETIMESTAMP FROM `group_master` WHERE 
		    	group_master.`Institution_ID`= %s order by groupDescription""",(institution_id))
        grouptdtls = nextcursor.fetchall()
        print(grouptdtls)
        for j in range(len(grouptdtls)):
        	grouptdtls[j]['groupID'] = grouptdtls[j]['groupID']
        	grouptdtls[j]['lASTUPDATETIMESTAMP'] = grouptdtls[j]['lASTUPDATETIMESTAMP'].isoformat()

        return ({"attributes": {"status_desc": "Group Details",
                            "status": "success"
                                },
            "responseList":grouptdtls}), status.HTTP_200_OK
#-----------------------get-batch-dtls-by-ins-id---------------------------------------#

#-----------------------get-student-dtls-by-ins-id---------------------------------------#
@name_space.route("/getStudentDtlsInstitutionId/<int:institution_id>")
class getStudentDtlsInstitutionId(Resource):
    def get(self,institution_id):
        nextconnection = mysql_next_connection()
        nextcursor = nextconnection.cursor()

        nextcursor.execute("""SELECT `INSTITUTION_USER_ID_STUDENT`,
        	concat(`FIRST_NAME`,' ',`LAST_NAME`)as name,`CLASS`,`Board`,
        	group_master.`Group_ID`,`Group_Description`,
        	institution_user_credential.`LAST_UPDATE_TIMESTAMP` FROM `student_dtls` 
        	inner join `institution_user_credential` on 
        	student_dtls.`INSTITUTION_USER_ID_STUDENT`=
        	institution_user_credential.`INSTITUTION_USER_ID` inner join 
        	`group_student_mapping` on 
        	group_student_mapping.`Student_Id` =institution_user_credential.`INSTITUTION_USER_ID`
        	inner join `group_master` on group_student_mapping.`Group_ID` =group_master.`Group_ID`
        	WHERE student_dtls.`INSTITUTION_ID`=%s order by name""",(institution_id))
        studentdtls = nextcursor.fetchall()
        # print(studentdtls)
        for j in range(len(studentdtls)):
        	userid = studentdtls[j]['INSTITUTION_USER_ID_STUDENT']
        	# print(userid)
        	studentdtls[j]['LAST_UPDATE_TIMESTAMP'] = studentdtls[j]['LAST_UPDATE_TIMESTAMP'].isoformat()
	        
        	nextcursor.execute("""SELECT distinct(`institution_user_id`)as User_Id FROM 
        		`institution_user_tracking` WHERE `institution_user_id`=%s""",(userid))
        	trackdtls = nextcursor.fetchone()
        	# print(trackdtls)

        	if trackdtls == None:
        		studentdtls[j]['downloaded']='No'
        		# print(studentdtls[j]['downloaded'])
        	else:
        		studentdtls[j]['downloaded']='YES'
        		# print(studentdtls[j]['downloaded'])
        return ({"attributes": {"status_desc": "Student Details",
                            "status": "success"
                                },
            "responseList":studentdtls}), status.HTTP_200_OK
#-----------------------get-student-dtls-by-ins-id---------------------------------------#

#-----------------------assignment-group-mapping---------------------------------------#
def assignStudent(assignmentId,groupList,duedate):
	connection = lab_lang()
	cursor = connection.cursor()

	conn = mysql_next_connection()
	curlog = conn.cursor()

	current_date = datetime.now()
	lastUpdateTimestamp = int(str(int(time.time()))+'000')
	# print(lastUpdateTimestamp)
	cursor.execute("""SELECT `Teacher_ID`,`Title` FROM `assignment` 
		WHERE `Assignment_ID` = %s""",(assignmentId))

	assignDtls = cursor.fetchone()
	groupId = ','.join(groupList)
	if assignDtls:
		teacherId = assignDtls.get('Teacher_ID')
		assignmentDesc = assignDtls.get('Title')
		assign_student = [
								{
								"assignmentDescription": assignmentDesc,
								"assignmentId": assignmentId,
								"clas": "",
								"dUEDATE": duedate,
								"groupID": groupId,
								"iD": 0,
								"lastUpdateTs": lastUpdateTimestamp,
								"status": "w",
								"studentUserId": "",
								"teacherId": teacherId
								}
							]

		post_url = 'http://creamsonservices.com:8080/StudentAssignmentServices_base64/AssignStudents'
		payload = json.dumps(assign_student)
		# print(payload)
		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		post_response = requests.post(post_url, data=payload, headers=headers)
		curlog.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name 
					FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(teacherId))
		tidDtls = curlog.fetchone()
		notify_url = 'http://creamsonservices.com:8080/CommunicationModule2/sendMailMessage'
		# for gid, grup in enumerate(groupList):
		studentList = utils.getStudentListFromGroupid(groupList)
		for sid in studentList:
			print(sid)
			curlog.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name 
				FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(sid))
			sidDtls = curlog.fetchone()
			data = {
					  'mailDetails': [
					    {
					      'appParams': {},
					      'mailParams': {"student":sidDtls.get('name'),
					      					"assignmentname":assignmentDesc,
					      					"startdate":current_date,
					      					"teacher":tidDtls.get('name')},
					      'role': 's1',
					      'toMail': '',
					      'toNumber': '',
					      'userId': sid
					    }
					  ],
					  'sourceApp': 'AST001ALT'
					}
			
			response = requests.post(notify_url, data=json.dumps(data), headers=headers)
	cursor.close()
	return 'success'


class Compute(Thread):
	def __init__(self, request, funcname):
		Thread.__init__(self)
		self.request = request
		self.funcname = funcname

	def run(self):
		time.sleep(5)
		if self.funcname == 'groupAssignmentMapping':
			assignmentId = self.request[0]
			groupList = self.request[1]
			duedate = self.request[2]
			assignStudent(assignmentId,groupList,duedate)
		elif self.funcname == 'studentAssignmentMapping':
			assignment_id = self.request[0]
			studentList = self.request[1]
			assignment_duedate = self.request[2]
			assignAssignmentToStudents(assignment_id,studentList,assignment_duedate)
		else:
			pass 


@name_space.route("/groupAssignmentMapping")
class groupAssignmentMapping(Resource):
	@api.expect(assigngroupDtls)
	def post(self):
		labconnection = lab_lang()
		labcursor = labconnection.cursor()
		details = request.get_json()
		
		assigngroup = details['assigngroup']
		groupList = []
		for assign in assigngroup:
			Assignment_id = assign.get('assignment_id')
			Group_id = assign.get('group_id')
			Last_update_id = assign.get('last_update_id')
			duedate = assign.get('assignment_duedate')
			if not Last_update_id:
				Last_update_id= ""
				# print(Last_update_id)
			
			groupassign_query = ("""INSERT INTO `assignment_group_mapping`(`assignment_id`, 
				`group_id`, `last_update_id`) VALUES (%s,%s,%s)""")
			mappdata = (Assignment_id,Group_id,Last_update_id)

			labcursor.execute(groupassign_query,mappdata)
			groupList.append(str(Group_id))
		labconnection.commit()
		labcursor.close()
		# assignStudent(Assignment_id,groupList,duedate)
		
		sendrReq = (Assignment_id,groupList,duedate)
		thread_a = Compute(sendrReq,'groupAssignmentMapping')
		thread_a.start()
		
		return ({"attributes": {"status_desc": "Group Assignment Mapping",
								"status": "success"},
				"responseList":'Assigning to group'}), status.HTTP_200_OK
#-----------------------assignment-group-mapping---------------------------------------#

#-----------------------get-rest-of-student-dtls-in-group-by-ins-id--------------------#
@name_space.route("/getRestOfStudentDtlsByGroupIdInstitutionId/<int:group_id>/<int:institution_id>")
class getRestOfStudentDtlsByGroupIdInstitutionId(Resource):
    def get(self,institution_id,group_id):
        nextconnection = mysql_next_connection()
        nextcursor = nextconnection.cursor()

        nextcursor.execute("""SELECT `INSTITUTION_USER_ID_STUDENT`, 
        	concat(`FIRST_NAME`,' ',`LAST_NAME`)as name,`CLASS`,`Board`, 
        	institution_user_credential.`LAST_UPDATE_TIMESTAMP` FROM `student_dtls`,
        	`institution_user_credential` WHERE `INSTITUTION_USER_ID_STUDENT` not 
        	in(SELECT `Student_Id` FROM `group_student_mapping` WHERE `Group_ID` = %s) 
        	and student_dtls.`INSTITUTION_USER_ID_STUDENT`= 
        	institution_user_credential.`INSTITUTION_USER_ID` and `INSTITUTION_ID`=%s 
        	order by name""",(group_id,institution_id))
        studentdtls = nextcursor.fetchall()
        
        for j in range(len(studentdtls)):
        	userid = studentdtls[j]['INSTITUTION_USER_ID_STUDENT']
        	
        	studentdtls[j]['LAST_UPDATE_TIMESTAMP'] = studentdtls[j]['LAST_UPDATE_TIMESTAMP'].isoformat()
	        
        return ({"attributes": {"status_desc": "Student Details",
                            "status": "success"
                                },
            "responseList":studentdtls}), status.HTTP_200_OK

#-----------------------get-rest-of-student-dtls-in-group-by-ins-id--------------------#

#-----------------------get-student-dtls-by-group-id-----------------------------------#
@name_space.route("/getStudentDtlsByGroupId/<int:group_id>")
class getStudentDtlsByGroupId(Resource):
    def get(self,group_id):
        nextconnection = mysql_next_connection()
        nextcursor = nextconnection.cursor()

        nextcursor.execute("""SELECT Distinct(`INSTITUTION_USER_ID_STUDENT`),group_master.`Institution_ID`,
        	concat(`FIRST_NAME`,' ',`LAST_NAME`)as name,`CLASS`,`Board`,
        	group_master.`Group_ID`,`Group_Description`,
        	institution_user_credential.`LAST_UPDATE_TIMESTAMP` FROM `student_dtls` 
        	inner join `institution_user_credential` on 
        	student_dtls.`INSTITUTION_USER_ID_STUDENT`=
        	institution_user_credential.`INSTITUTION_USER_ID` inner join 
        	`group_student_mapping` on 
        	group_student_mapping.`Student_Id` =institution_user_credential.`INSTITUTION_USER_ID`
        	inner join `group_master` on group_student_mapping.`Group_ID` =group_master.`Group_ID`
        	AND student_dtls.`INSTITUTION_ID` = group_master.`Institution_ID` 
        	WHERE group_master.`Group_ID`=%s order by name""",(group_id))
        studentdtls = nextcursor.fetchall()
        # print(studentdtls)
        for j in range(len(studentdtls)):
        	userid = studentdtls[j]['INSTITUTION_USER_ID_STUDENT']
        	# print(userid)
        	studentdtls[j]['LAST_UPDATE_TIMESTAMP'] = studentdtls[j]['LAST_UPDATE_TIMESTAMP'].isoformat()
	        
        	nextcursor.execute("""SELECT distinct(`institution_user_id`)as User_Id FROM 
        		`institution_user_tracking` WHERE `institution_user_id`=%s""",(userid))
        	trackdtls = nextcursor.fetchone()
        	# print(trackdtls)

        	if trackdtls == None:
        		studentdtls[j]['downloaded']='No'
        		# print(studentdtls[j]['downloaded'])
        	else:
        		studentdtls[j]['downloaded']='YES'
        		# print(studentdtls[j]['downloaded'])
        return ({"attributes": {"status_desc": "Student Details",
                            "status": "success"
                                },
            "responseList":studentdtls}), status.HTTP_200_OK
#-----------------------get-student-dtls-by-group-id-----------------------------------#

#-----------------------student-assignment-mapping---------------------------------------#
@name_space.route("/submitStudentAssignment")
class submitStudentAssignment(Resource):
	@api.expect(substuassignmentDtls)
	def post(self):
		labconnection = lab_lang()
		labcursor = labconnection.cursor()
		details = request.get_json()
		
		stuassignment = details['substuassignment']
		for stu in stuassignment:
			assignment_id = stu.get('Assignment_ID')
			content_Path = stu.get('Content_Path')
			student_Id = stu.get('Student_Id')
			progress = stu.get('Progress')
			content_Type = stu.get('Content_Type')

			if not progress:
				progress= ""
				# print(progress)
			
			stuassignment_query = ("""INSERT INTO `activity_assignment_mapping`(`Assignment_ID`,
			 `Content_Path`, `Student_Id`, `Progress`,`Content_Type`) VALUES (%s,%s,%s,%s,%s)""")
			assignment_data = (assignment_id,content_Path,student_Id,progress,content_Type)

			submitdata = labcursor.execute(stuassignment_query,assignment_data)
		labconnection.commit()
		if submitdata:
			return ({"attributes": {"status_desc": "Student Asignment Submitted",
	                                "status": "success"
	                                }
	                 }), status.HTTP_200_OK
		else:[]
#-----------------------student-assignment-mapping---------------------------------------#

#-----------------------------update-student-assignment-status--------------------------#
@name_space.route("/updateStudentAssignmentStatusByAssignmentIdStudentId")
class updateStudentAssignmentStatusByAssignmentIdStudentId(Resource):
    @api.expect(updatestatus)
    def put(self):
        labconnection = lab_lang()
        labcursor = labconnection.cursor()
        details = request.get_json()
        
        Assignment_Status = details['Assignment_Status']
        Assignment_ID = details['Assignment_ID']
        Student_UserID = details['Student_UserID']

        update_query = ("""UPDATE `assignment_mapping` SET `Status`=%s WHERE 
        	`Assignment_ID`=%s and `Student_UserID`=%s""")
        update_data = (Assignment_Status,Assignment_ID,Student_UserID)
        print(update_data)

        labcursor.execute(update_query,update_data)
        labconnection.commit()
        labcursor.close()
        return ({"attributes": {"status_desc": "Student Assignment Status Updated.",
                            "status": "success"
                            },
                            "responseList":details}), status.HTTP_200_OK

#-----------------------------update-student-assignment-status--------------------------#

#-----------------------------get-student-assignment-details--------------------------#
@name_space.route("/getAssignmentDtlsByStatusAssignmentId/<string:assignment_status>/<int:student_id>")
class getAssignmentDtlsByStatusAssignmentId(Resource):
    def get(self,assignment_status,student_id):
        nextconnection = mysql_next_connection()
        nextcursor = nextconnection.cursor()

        labconnection = lab_lang()
        labcursor = labconnection.cursor()

        labcursor.execute("""SELECT assignment_mapping.`Assignment_ID`,`Result`,
        	assigment_result.`Remarks`as resultRemarks,`Paramater_Id`,`Teacher_ID`,
        	`Assignment_Type`,`Content_Master_ID`,assignment.`Remarks`,
        	`Title`,`Status`,assignment_mapping.`Last_Update_TS` 
        	FROM `assigment_result` right join `assignment` on 
        	assigment_result.`Assignment_ID`=assignment.`Assignment_ID` right join 
        	`assignment_mapping` on assignment.`Assignment_ID` = assignment_mapping.`Assignment_ID` 
        	WHERE `Student_UserID` = %s and Status = %s 
        	and assignment.`Teacher_ID`!='NULL' order by Assignment_ID Desc""",(student_id,assignment_status))
        assignment_dtls = labcursor.fetchall()
        # print(assignment_dtls)

        for j in range(len(assignment_dtls)):
        	teacherid = assignment_dtls[j]['Teacher_ID']
        	# print(teacherid)
        	assignment_id = assignment_dtls[j]['Assignment_ID']
        	print(assignment_id)
        	assignment_dtls[j]['Last_Update_TS'] = assignment_dtls[j]['Last_Update_TS'].isoformat()
	        if assignment_dtls[j]['Result'] == None:
	        	assignment_dtls[j]['Result']=""
	        else:
	        	assignment_dtls[j]['Result']=assignment_dtls[j]['Result']
	        
	        if assignment_dtls[j]['resultRemarks'] == None:
	        	assignment_dtls[j]['resultRemarks']=""
	        	# print(assignment_dtls[j]['resultRemarks'])
	        else:
	        	assignment_dtls[j]['resultRemarks']=assignment_dtls[j]['resultRemarks']
	        	# print(assignment_dtls[j]['resultRemarks'])
	        
	        if assignment_dtls[j]['Paramater_Id'] == None:
	        	assignment_dtls[j]['Paramater_Id']=""
	        else:
	        	assignment_dtls[j]['Paramater_Id']=assignment_dtls[j]['Paramater_Id']

	        if assignment_dtls[j]['Content_Master_ID'] == None:
	        	assignment_dtls[j]['Content_Master_ID']=""
	        else:
	        	assignment_dtls[j]['Content_Master_ID']=assignment_dtls[j]['Content_Master_ID']
	        
	        labcursor.execute("""SELECT `Mapping_ID`,`Content_ID`,`File_Path`,`File_type` FROM 
	        	`assignment_file_mapping` WHERE `Assignment_ID`=%s""",(assignment_id))
	        tea_filesdtls = labcursor.fetchall()
	        if tea_filesdtls:
	        	assignment_dtls[j]['Teacher_Files'] = tea_filesdtls
	        else:
	        	assignment_dtls[j]['Teacher_Files'] =[]

	        labcursor.execute("""SELECT `Student_Activity_Id`,`Content_Path`,`Content_Type`
	         FROM `activity_assignment_mapping` WHERE `Student_Id`=%s and 
	         `Assignment_ID`=%s order by `Student_Activity_Id` Desc""",(student_id,assignment_id))
	        stu_filesdtls = labcursor.fetchall()
	        if stu_filesdtls:
	        	assignment_dtls[j]['Student_Files'] = stu_filesdtls
	        else:
	        	assignment_dtls[j]['Student_Files'] =[]

	        nextcursor.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`)as 
	        	teachername FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID`
	        	=%s""",(teacherid))
        	teacherdtls = nextcursor.fetchone()
        	# print(teacherdtls)
        	if teacherdtls:
        		teachername = teacherdtls.get('teachername','')
        	else:
        		teachername = ''
        	# print(teachername)
        	assignment_dtls[j]['teachername']=teachername
	        	
        return ({"attributes": {"status_desc": "Assignment Details",
                                "status": "success"
                                },
            "responseList":assignment_dtls}), status.HTTP_200_OK
#-----------------------------get-student-assignment-details--------------------------#

#-----------------------------delete-student-assignment-------------------------------#
def deleteAssignment(Student_Activity_Id):
	labconnection = lab_lang()
	labcursor = labconnection.cursor()
        
	try:
		delStudentAssignDtls = ("""DELETE FROM `activity_assignment_mapping` WHERE 
        	`Student_Activity_Id`=%s""")

		delData = (Student_Activity_Id)
		print(delData)
		labcursor.execute(delStudentAssignDtls,delData)
		print(delStudentAssignDtls,delData)
		labconnection.commit()
		labcursor.close()
		
	except Exception as e:
		return e

	return 'selected'
	
@name_space.route("/deleteStudentAssignment/<int:Student_Activity_Id>")
class deleteStudentAssignment(Resource):
	def put(self,Student_Activity_Id):
		labconnection = lab_lang()
		labcursor = labconnection.cursor()
		res = 'Assignment Removed.'
     
		labcursor.execute("""SELECT * FROM `activity_assignment_mapping` WHERE 
			`Student_Activity_Id` = %s""",(Student_Activity_Id))

		assignmentDtls = labcursor.fetchall()
		if assignmentDtls:
			delRes = deleteAssignment(Student_Activity_Id)
				
			if delRes == 'updated':
				res = 'Assignment Removed.'

		labcursor.close()

		return ({"attributes": {"status_desc": "Student Details.",
									"status": "success"
									},
					"responseList": res}), status.HTTP_200_OK

#-----------------------------delete-student-assignment-------------------------------#

#-----------------------------get-teacher-assignment-details---------------------------#
@name_space.route("/getAssignmentDtlsByTeacherId/<int:teacher_id>")
class getAssignmentDtlsByTeacherId(Resource):
    def get(self,teacher_id):
        nextconnection = mysql_next_connection()
        nextcursor = nextconnection.cursor()

        labconnection = lab_lang()
        labcursor = labconnection.cursor()

        labcursor.execute("""SELECT assignment.`Assignment_ID`, `Teacher_ID`,`Title`,
        	`Last_Update_TS`, `Last_Update_ID` FROM 
        	`assignment`  WHERE `Teacher_ID`=%s order by Assignment_ID Desc""",(teacher_id))
        assignment_dtls = labcursor.fetchall()
        # print(assignment_dtls)

        for j in range(len(assignment_dtls)):
        	assignment_id = assignment_dtls[j]['Assignment_ID']
        	# print(assignment_id)
        	assignment_dtls[j]['Last_Update_TS'] = assignment_dtls[j]['Last_Update_TS'].isoformat()
	        
	        labcursor.execute("""SELECT `Mapping_ID`,`Content_ID`,`File_type`,`File_Path` FROM 
	        	`assignment_file_mapping` WHERE `Assignment_ID`=%s order by `Mapping_ID` Desc""",(assignment_id))
	        filesdtls = labcursor.fetchall()

	        if filesdtls:
		        assignment_dtls[j]['uploadfile_dtls'] = filesdtls
	        else:
	        	assignment_dtls[j]['uploadfile_dtls'] =[]

	        labcursor.execute("""SELECT `Assignment_ID`,`Student_UserID`,`Status` FROM 
	        	`assignment_mapping` WHERE `Assignment_ID`=%s""",(assignment_id))
	        assigndtls = labcursor.fetchall()
	        if assigndtls:
		        assignment_dtls[j]['assignStudent_dtls'] = assigndtls
	        else:
	        	assignment_dtls[j]['assignStudent_dtls'] =[]
	        for j in range(len(assigndtls)):
		        student_id = assigndtls[j]['Student_UserID']
	        	# print(student_id)
		        nextcursor.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`)as 
		        	studentname FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID`
		        	=%s""",(student_id))
	        	studentdtls = nextcursor.fetchone()
	        	# print(teacherdtls)
	        	if studentdtls != None:
	        		studentname = studentdtls['studentname']
	        	else:
	        		studentname = ''
	        	assigndtls[j]['studentname']=studentname

        return ({"attributes": {"status_desc": "Teacher Assignment Details.",
									"status": "success"
									},
					"responseList": assignment_dtls}), status.HTTP_200_OK	

#-----------------------------get-teacher-assignment-details---------------------------#

#-----------------------------create-teacher-assignment--------------------------------#
@name_space.route("/CreateAssignment")
class CreateAssignment(Resource):
	@api.expect(assignmentfileDtls)
	def post(self):
		labconnection = lab_lang()
		labcursor = labconnection.cursor()
		details = request.get_json()
		
		assignfile = details['assignmentfile']
		for ass in assignfile:
			assignment_id = ass.get('Assignment_ID')
			content_id = ass.get('Content_ID')
			file_type = ass.get('File_type')
			file_Path = ass.get('File_Path')
			last_update_Id = ass.get('Last_updated_ID')
			

			if not content_id:
				content_id= ""
				# print(content_id)
			
			if not last_update_Id:
				last_update_Id= ""
				# print(last_update_Id)
			
			assignment_query = ("""INSERT INTO `assignment_file_mapping`(`Assignment_ID`,
			 `Content_ID`, `File_type`, `File_Path`, `Last_updated_ID`) VALUES (%s,%s,%s,%s,%s)""")
			assignment_data = (assignment_id,content_id,file_type,file_Path,last_update_Id)

			submitdata = labcursor.execute(assignment_query,assignment_data)
		labconnection.commit()
		labcursor.close()
		if submitdata:
			return ({"attributes": {"status_desc": "Asignment File Uploaded",
	                                "status": "success"
	                                }
	                 }), status.HTTP_200_OK
		else:[]
#-----------------------------create-teacher-assignment--------------------------------#

#-----------------------------teacher-assignment-file---------------------------------#
@name_space.route("/updateAssignmentfileByMappingId/<int:mapping_id>")
class updateAssignmentfileByMappingId(Resource):
    @api.expect(updatefile)
    def put(self,mapping_id):
        labconnection = lab_lang()
        labcursor = labconnection.cursor()
        details = request.get_json()
        
        assignment_ID = details.get('Assignment_ID')
        file_Path = details.get('File_Path')
        file_type = details.get('File_type')

        labcursor.execute("""SELECT `Mapping_ID`, `Assignment_ID`, `File_type`,`File_Path` 
        	FROM `assignment_file_mapping` WHERE `Mapping_ID`=%s""",(mapping_id))
        filedtls = labcursor.fetchone()
        # print(filedtls)
        if filedtls:
            if not assignment_ID:
            	assignment_ID= filedtls.get('Assignment_ID')
            if not file_type:
            	file_type= filedtls.get('File_type')
				# print(File_type)

        update_query = ("""UPDATE `assignment_file_mapping` SET `Assignment_ID`=%s,
        	`File_Path`=%s,`File_type`=%s WHERE `Mapping_ID`=%s""")
        update_data = (assignment_ID,file_Path,file_type,mapping_id)
        print(update_data)

        labcursor.execute(update_query,update_data)

        return ({"attributes": {"status_desc": "Assignment File Updated.",
                            "status": "success"
                            },
                            "responseList":details}), status.HTTP_200_OK

#-----------------------------teacher-assignment-file--------------------------------#

#-----------------------------delete-student-assignment-------------------------------#
def deleteAssignmentfile(mapping_id):
	labconnection = lab_lang()
	labcursor = labconnection.cursor()
        
	try:
		delAssignfileDtls = ("""DELETE FROM `assignment_file_mapping` WHERE`Mapping_ID`=%s""")

		delData = (mapping_id)
		# print(delData)
		labcursor.execute(delAssignfileDtls,delData)
		# print(delAssignfileDtls,delData)
		labconnection.commit()
		labcursor.close()
		
	except Exception as e:
		return e

	return 'selected'

@name_space.route("/deleteUploadAssignmentfile/<int:mapping_id>")
class deleteStudentAssigndeleteUploadAssignmentfilement(Resource):
	def put(self,mapping_id):
		labconnection = lab_lang()
		labcursor = labconnection.cursor()
		res = 'Assignment File Removed.'
     
		labcursor.execute("""SELECT * FROM `assignment_file_mapping` WHERE 
			`Mapping_ID`=%s""",(mapping_id))

		assignmentfileDtls = labcursor.fetchall()
		if assignmentfileDtls:
			delRes = deleteAssignmentfile(mapping_id)
				
			if delRes == 'updated':
				res = 'Assignment File Removed.'
		else:
			[]
		labcursor.close()

		return ({"attributes": {"status_desc": "Upload File Details.",
									"status": "success"
									},
					"responseList": res}), status.HTTP_200_OK

#-----------------------------delete-student-assignment-------------------------------#

#-----------------------------assignment-dtls-by-group-id-----------------------------#
@name_space.route("/getAssignmentDtlsByAssignmentIdStudentId/<int:assignment_id>/<int:student_id>")
class getAssignmentDtlsByAssignmentIdStudentId(Resource):
    def get(self,assignment_id,student_id):
        nextconnection = mysql_next_connection()
        nextcursor = nextconnection.cursor()

        labconnection = lab_lang()
        labcursor = labconnection.cursor()

        labcursor.execute("""SELECT assignment_mapping.`Assignment_ID`,`Result`, 
        	assigment_result.`Remarks`as resultRemarks,`Paramater_Id`,`Teacher_ID`, 
        	`Assignment_Type`,assignment.`Remarks`, `Title`,
        	`Status`,assignment_mapping.`Last_Update_TS` FROM `assigment_result` 
        	right join `assignment` on assigment_result.`Assignment_ID`=
        	assignment.`Assignment_ID` right join `assignment_mapping` on 
        	assignment.`Assignment_ID` = assignment_mapping.`Assignment_ID` 
        	WHERE `Student_UserID` = %s and assignment_mapping.`Assignment_ID`=%s 
        	and assignment.`Teacher_ID`!='NULL'""",(student_id,assignment_id))
        assignment_dtls = labcursor.fetchall()
        for j in range(len(assignment_dtls)):
        	teacherid = assignment_dtls[j]['Teacher_ID']
        	# print(teacherid)
        	assignment_dtls[j]['Last_Update_TS'] = assignment_dtls[j]['Last_Update_TS'].isoformat()
	        if assignment_dtls[j]['Result'] == None:
	        	assignment_dtls[j]['Result']=""
	        else:
	        	assignment_dtls[j]['Result']=assignment_dtls[j]['Result']
	        
	        if assignment_dtls[j]['resultRemarks'] == None:
	        	assignment_dtls[j]['resultRemarks']=""
	        	# print(assignment_dtls[j]['resultRemarks'])
	        else:
	        	assignment_dtls[j]['resultRemarks']=assignment_dtls[j]['resultRemarks']
	        	# print(assignment_dtls[j]['resultRemarks'])
	        
	        if assignment_dtls[j]['Paramater_Id'] == None:
	        	assignment_dtls[j]['Paramater_Id']=""
	        else:
	        	assignment_dtls[j]['Paramater_Id']=assignment_dtls[j]['Paramater_Id']

	        labcursor.execute("""SELECT `Mapping_ID`,`Content_ID`,`File_Path`,`File_type` FROM 
	        	`assignment_file_mapping` WHERE `Assignment_ID`=%s""",(assignment_id))
	        tea_filesdtls = labcursor.fetchall()
	        if tea_filesdtls:
	        	assignment_dtls[j]['Teacher_Files'] = tea_filesdtls
	        else:
	        	assignment_dtls[j]['Teacher_Files'] =[]

	        nextcursor.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`)as 
	        	teachername FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID`
	        	=%s""",(teacherid))
        	teacherdtls = nextcursor.fetchone()
        	# print(teacherdtls)
        	if teacherdtls:
        		teachername = teacherdtls['teachername']
        	else:
        		teachername = ''
        	# print(teachername)
        	assignment_dtls[j]['teachername']=teachername

	        labcursor.execute("""SELECT count(distinct(`Assignment_ID`))as total FROM 
	          `assignment_mapping` WHERE `Student_UserID`=%s and `Status`='c'and
	          `Assignment_ID`=%s""",(student_id,assignment_id))
	        completeassign = labcursor.fetchone()
	        if completeassign:
		        com_assign = completeassign['total']
		        assignment_dtls[j]['complete_assignment']=com_assign
	        else:
	        	assignment_dtls[j]['complete_assignment']=0

	        labcursor.execute("""SELECT count(distinct(`Assignment_ID`))as total FROM 
	          `assignment_mapping` WHERE `Student_UserID`=%s and `Status`='w' and
	          `Assignment_ID`=%s""",(student_id,assignment_id))
	        incompleteassign = labcursor.fetchone()
	        if incompleteassign:
		        incom_assign = incompleteassign['total']
		        assignment_dtls[j]['incomplete_assignment']=incom_assign
	        else:
	        	assignment_dtls[j]['incomplete_assignment']=0
	        
	        labcursor.execute("""SELECT count(`Student_ID`)as total FROM `assigment_result` 
	        	WHERE `Student_ID` = %s and `Assignment_ID`=%s""",(student_id,assignment_id))
	        reviewassign = labcursor.fetchone()
	        if reviewassign:
		        rev_assign = reviewassign['total']
		        assignment_dtls[j]['review_assignment']=rev_assign
	        else:
	        	assignment_dtls[j]['review_assignment']=0
	        
	        	
        return ({"attributes": {"status_desc": "Assignment Details",
                                "status": "success"
                                },
            "responseList":assignment_dtls}), status.HTTP_200_OK

#-----------------------------assignment-dtls-by-student-id-----------------------------#

#-----------------------------assignment-dtls-by-student-id---------------------------#

@name_space.route("/getAssignmentDtlsByStudentId/<int:student_id>")
class getAssignmentDtlsByStudentId(Resource):
    def get(self,student_id):
        nextconnection = mysql_next_connection()
        nextcursor = nextconnection.cursor()

        labconnection = lab_lang()
        labcursor = labconnection.cursor()
        details = []

        labcursor.execute("""SELECT distinct(`Assignment_ID`)as 'Assignment_ID'  FROM `assignment_mapping` 
        	WHERE `Student_UserID` =%s""",(student_id))
        assignment_ids = labcursor.fetchall()
        for j in range(len(assignment_ids)):
        	details.append(assignment_ids[j]['Assignment_ID'])
        details = tuple(details)
        	# assignment_id = assignment_ids[j]['Assignment_ID']
        # print(details)
        labcursor.execute("""SELECT distinct(assignment_mapping.`Assignment_ID`),`Result`, 
        	assigment_result.`Remarks`as resultRemarks,`Paramater_Id`,`Teacher_ID`, 
        	`Assignment_Type`,assignment.`Remarks`, `Title`,
        	`Status`,assignment_mapping.`Last_Update_TS` FROM `assigment_result` 
        	right join `assignment` on assigment_result.`Assignment_ID`=
        	assignment.`Assignment_ID` right join `assignment_mapping` on 
        	assignment.`Assignment_ID` = assignment_mapping.`Assignment_ID` 
        	WHERE `Student_UserID` = %s and assignment_mapping.`Assignment_ID`in %s 
        	and assignment.`Teacher_ID`!='NULL'""",(student_id,details))
        assignment_dtls = labcursor.fetchall()
        # print(assignment_dtls)
        if assignment_dtls:
	        for j in range(len(assignment_dtls)):
	        	assignment_id = assignment_dtls[j]['Assignment_ID']
	        	# print(assignment_id)
	        	teacherid = assignment_dtls[j]['Teacher_ID']
	         	# print(teacherid)
	        	assignment_dtls[j]['Last_Update_TS'] = assignment_dtls[j]['Last_Update_TS'].isoformat()
		        if assignment_dtls[j]['Result'] == None:
		        	assignment_dtls[j]['Result']=""
		        else:
		        	assignment_dtls[j]['Result']=assignment_dtls[j]['Result']
		        
		        if assignment_dtls[j]['resultRemarks'] == None:
		        	assignment_dtls[j]['resultRemarks']=""
		        	# print(assignment_dtls[j]['resultRemarks'])
		        else:
		        	assignment_dtls[j]['resultRemarks']=assignment_dtls[j]['resultRemarks']
		        	# print(assignment_dtls[j]['resultRemarks'])
		        
		        if assignment_dtls[j]['Paramater_Id'] == None:
		        	assignment_dtls[j]['Paramater_Id']=""
		        else:
		        	assignment_dtls[j]['Paramater_Id']=assignment_dtls[j]['Paramater_Id']

		        labcursor.execute("""SELECT `Mapping_ID`,`Assignment_ID`,`Content_ID`,`File_Path`,`File_type` FROM 
		        	`assignment_file_mapping` WHERE `Assignment_ID`=%s""",(assignment_id))
		        tea_filesdtls = labcursor.fetchall()
		        if tea_filesdtls:
		        	assignment_dtls[j]['Teacher_Files'] = tea_filesdtls
		        else:
		        	assignment_dtls[j]['Teacher_Files'] =[]

		        nextcursor.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`)as 
		        	teachername FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID`
		        	=%s""",(teacherid))
	        	teacherdtls = nextcursor.fetchone()
	        	# print(teacherdtls)
	        	if teacherdtls:
	        		teachername = teacherdtls['teachername']
	        	else:
	        		teachername = ''
	        	# print(teachername)
	        	assignment_dtls[j]['teachername']=teachername

		        labcursor.execute("""SELECT count(distinct(`Assignment_ID`))as total FROM 
		          `assignment_mapping` WHERE `Student_UserID`=%s and `Status`='c'and
		          `Assignment_ID`=%s""",(student_id,assignment_id))
		        completeassign = labcursor.fetchone()
		        if completeassign:
			        com_assign = completeassign['total']
			        assignment_dtls[j]['complete_assignment']=com_assign
		        else:
		        	assignment_dtls[j]['complete_assignment']=0

		        labcursor.execute("""SELECT count(distinct(`Assignment_ID`))as total FROM 
		          `assignment_mapping` WHERE `Student_UserID`=%s and `Status`='w' and
		          `Assignment_ID`=%s""",(student_id,assignment_id))
		        incompleteassign = labcursor.fetchone()
		        if incompleteassign:
			        incom_assign = incompleteassign['total']
			        assignment_dtls[j]['incomplete_assignment']=incom_assign
		        else:
		        	assignment_dtls[j]['incomplete_assignment']=0
		        
		        labcursor.execute("""SELECT count(`Student_ID`)as total FROM `assigment_result` 
		        	WHERE `Student_ID` = %s and `Assignment_ID`=%s""",(student_id,assignment_id))
		        reviewassign = labcursor.fetchone()
		        if reviewassign:
			        rev_assign = reviewassign['total']
			        assignment_dtls[j]['review_assignment']=rev_assign
		        else:
		        	assignment_dtls[j]['review_assignment']=0
        else:[] 
	        
        return ({"attributes": {"status_desc": "Assignment Details",
                                "status": "success"
                                },
            "responseList":assignment_dtls}), status.HTTP_200_OK
#-----------------------------assignment-dtls-by-student-id---------------------------#

@name_space.route("/getAssignmentDtlsByGroupId/<int:group_id>")
class getAssignmentDtlsByGroupId(Resource):
	def get(self,group_id):
		logconnection = mysql_next_connection()
		logcursor = logconnection.cursor()

		labconnection = lab_lang()
		labcursor = labconnection.cursor()

		logcursor.execute("""SELECT distinct(`Student_Id`) FROM `group_student_mapping` 
			WHERE `Group_ID` = %s""",(group_id))

		studentList = logcursor.fetchall()

		studentIdList = [studnt.get('Student_Id') for sid, studnt in enumerate(studentList)]
		# print(studentIdList)


		labcursor.execute("""SELECT `assignment_id` FROM `assignment_group_mapping` 
			WHERE `group_id`=%s""",(group_id))

		assignmentList = labcursor.fetchall()

		assignmentIdList = [assign.get('assignment_id') for aid, assign in enumerate(assignmentList)]

		# print(assignmentIdList)
		assignmentDtlsList = []
		for aid in assignmentIdList:
			labcursor.execute("""SELECT ass.`Assignment_ID`,`Title`,`Remarks`,GROUP_CONCAT(`File_Path` SEPARATOR ',') as 'File_Path',
				GROUP_CONCAT(`File_type` SEPARATOR ',') as 'File_type',GROUP_CONCAT(`Mapping_ID` SEPARATOR ',') as 'Mapping_ID',
				GROUP_CONCAT(`Content_ID` SEPARATOR ',') as 'Content_ID',ass.`Last_Update_TS` as 'Last_Update_TS' 
				FROM `assignment` ass INNER JOIN assignment_file_mapping afm 
				on ass.`Assignment_ID` = afm.`Assignment_ID`
				WHERE ass.`Assignment_ID` = %s""",(aid))

			assignmentDtls = labcursor.fetchone()

			if assignmentDtls:
				filesList = [] 
				if assignmentDtls.get('File_Path'):
					teacherfiles = assignmentDtls.get('File_Path').split(',')
					filetypes = assignmentDtls.get('File_type').split(',')
					mappingId = assignmentDtls.get('Mapping_ID').split(',')
					contentId = assignmentDtls.get('Content_ID').split(',')
				else:
					teacherfiles = ""
					filetypes = ""
					mappingId = ""
					contentId = ""
				for fid, file in enumerate(teacherfiles):
					filesList.append({"Mapping_ID": mappingId[fid],
									"File_type": filetypes[fid],
									"Content_ID": contentId[fid],
									"File_Path": teacherfiles[fid]})

				assignmentDtls['Teacher_Files'] = filesList
				assignmentDtls.pop('File_Path',None)
				assignmentDtls.pop('File_type',None)
				assignmentDtls.pop('Mapping_ID',None)
				assignmentDtls.pop('Content_ID',None)
				assignmentDtls['Last_Update_TS'] = assignmentDtls.get('Last_Update_TS').isoformat()
				assignmentDtls['assign_students'] = len(studentIdList)

				labcursor.execute("""SELECT count(distinct(`Student_UserID`)) as total FROM 
					`assignment_mapping` WHERE `Student_UserID` in %s and `Status`='c'and
					`Assignment_ID`=%s""",(tuple(studentIdList),aid))
				
				completeDtls = labcursor.fetchone()
				
				if completeDtls:
					total_complete = completeDtls.get('total')
					assignmentDtls['complete_assignment'] = total_complete
					assignmentDtls['incomplete_assignment'] = len(studentIdList) - total_complete
				else:
					assignmentDtls['complete_assignment'] = 0
					assignmentDtls['incomplete_assignment'] = len(details)

				labcursor.execute("""SELECT COUNT(`Student_ID`) as 'review_assignment' FROM 
					`assigment_result` WHERE `Assignment_ID` = %s 
					and `Student_ID` in %s""",(aid,tuple(studentIdList)))

				reviewDtls = labcursor.fetchone()
				if reviewDtls:
					assignmentDtls['review_assignment'] = reviewDtls.get('review_assignment')
				else:
					assignmentDtls['review_assignment'] = 0
				assignmentDtlsList.append(assignmentDtls)
		return ({"attributes": {"status_desc": "Assignment Details",
								"status": "success"
								},
				"responseList":assignmentDtlsList}), status.HTTP_200_OK

#--------------------assignment-dtls-by--assignment-id--------------------------------#
@name_space.route("/getAssignmentDtlsByAssignmentId/<int:assignment_id>")
class getAssignmentDtlsByAssignmentId(Resource):
	def get(self,assignment_id):
		logconnection = mysql_next_connection()
		logcursor = logconnection.cursor()

		labconnection = lab_lang()
		labcursor = labconnection.cursor()

		labcursor.execute("""SELECT assignment_mapping.`Assignment_ID`,`Student_UserID`,
			`Result`, assigment_result.`Remarks`, `Assignment_Type`,`Title`, `Status`,
			`DUE_DATE`,assignment_mapping.`Last_Update_TS` FROM `assigment_result` 
			right join `assignment` on assigment_result.`Assignment_ID`= 
			assignment.`Assignment_ID` right join `assignment_mapping` 
			on assignment.`Assignment_ID` = assignment_mapping.`Assignment_ID` 
			WHERE assignment.`Assignment_ID`=%s""",(assignment_id))
		assignment_dtls = labcursor.fetchall()

		if assignment_dtls != ():
			for j in range(len(assignment_dtls)):
				studentid = assignment_dtls[j]['Student_UserID']
				if assignment_dtls[j]['Last_Update_TS'] == "0000-00-00 00:00:00":
					assignment_dtls[j]['Last_Update_TS'] = "0000-00-00 00:00:00"
				else:
					assignment_dtls[j]['Last_Update_TS'] = assignment_dtls[j]['Last_Update_TS'].isoformat()
				
				if assignment_dtls[j]['DUE_DATE'] == "0000-00-00 00:00:00" or assignment_dtls[j]['DUE_DATE'] == None:
					assignment_dtls[j]['DUE_DATE'] = "0000-00-00 00:00:00"
				else:
					assignment_dtls[j]['DUE_DATE'] = assignment_dtls[j]['DUE_DATE'].isoformat()
				
				if assignment_dtls[j]['Result'] == None:
					assignment_dtls[j]['Result']=""
				else:
					assignment_dtls[j]['Result']=assignment_dtls[j]['Result']

				if assignment_dtls[j]['Remarks'] == None:
					assignment_dtls[j]['Remarks']=""
				else:
					assignment_dtls[j]['Remarks']=assignment_dtls[j]['Remarks']
					
				labcursor.execute("""SELECT `Assignment_ID`,`Content_Path`,`Content_Type` 
					FROM `activity_assignment_mapping` WHERE `Assignment_ID`=%s and 
					`Student_Id`=%s """,(assignment_id,studentid))
				stu_filesdtls = labcursor.fetchall()
				if stu_filesdtls:
					assignment_dtls[j]['Student_Files'] = stu_filesdtls
				else:
					assignment_dtls[j]['Student_Files'] =[]

				labcursor.execute("""SELECT `Result`,`Remarks` FROM `assigment_result` WHERE 
					`Assignment_ID`=%s and `Student_ID`=%s""",(assignment_id,studentid))
				resultdtls = labcursor.fetchone()
				if resultdtls:
					Result = resultdtls['Result']
					Remarks = resultdtls['Remarks']
					assignment_dtls[j]['Result']=Result
					assignment_dtls[j]['Remarks']=Remarks
				else:
					assignment_dtls[j]['Result']=''
					assignment_dtls[j]['Remarks']=''
				logcursor.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`)as 
					studentname FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID`
					=%s""",(studentid))
				studentdtls = logcursor.fetchone()
				studentname = studentdtls['studentname']
				assignment_dtls[j]['studentname']=studentname

		else:
			assignment_dtls = []

		logcursor.close()
		labcursor.close()
		
		return ({"attributes": {"status_desc": "Assignment Details",
								"status": "success"
								},
				"responseList":assignment_dtls}), status.HTTP_200_OK

#--------------------assignment-dtls-by--assignment-id--------------------------------#

#--------------------delete-group-by--group-id---------------------------------#
def deleteGroup(Group_ID):
	nextconnection = mysql_next_connection()
	nextcursor = nextconnection.cursor()
        
	try:
		delGroup = ("""DELETE FROM `group_master` WHERE `Group_ID`=%s""")
		delData = (Group_ID)
		nextcursor.execute(delGroup,delData)
		nextconnection.commit()

		delGroupStudent = ("""DELETE FROM `group_student_mapping` WHERE `Group_ID`=%s""")
		delGroupStudentData = (Group_ID)
		nextcursor.execute(delGroupStudent,delGroupStudentData)
		nextconnection.commit()
		nextcursor.close()
		
	except Exception as e:
		return e

	return 'selected'

@name_space.route("/deleteGroupByGroupId/<int:Group_ID>")
class deleteGroupByGroupId(Resource):
	def put(self,Group_ID):
		nextconnection = mysql_next_connection()
		nextcursor = nextconnection.cursor()
		res = 'Group Removed.'
     
		nextcursor.execute("""SELECT * FROM `group_master` WHERE `Group_ID`=%s""",(Group_ID))

		groupDtls = nextcursor.fetchall()

		nextcursor.execute("""SELECT * FROM `group_student_mapping` WHERE `Group_ID`=%s""",
			(Group_ID))

		groupStuDtls = nextcursor.fetchall()
		if groupDtls or groupStuDtls:
			delRes = deleteGroup(Group_ID)
				
			if delRes == 'updated':
				res = 'Group Removed.'
		else:
			[]
		nextcursor.close()

		return ({"attributes": {"status_desc": "Group Details.",
									"status": "success"
									},
					"responseList": res}), status.HTTP_200_OK

#--------------------delete-group-by--group-id---------------------------------#

#-------------------------create-group-----------------------------------------#
@name_space.route("/CreateGroup")
class CreateGroup(Resource):
	@api.expect(creategroup)
	def post(self):
		details = request.get_json()
		conn = mysql_next_connection()
		cur = conn.cursor()
		
		
		groupDescription = details['groupDescription']
		institutionID= details['institutionID']
		teacherId= details['teacherId']

		createGroup_query = ("""INSERT INTO `group_master`(`Institution_ID`, 
			`Group_Description`, `Last_Update_ID`) VALUES (%s,%s,%s)""")
		createGroup_data = (institutionID,groupDescription,teacherId)

		groupdata = cur.execute(createGroup_query,createGroup_data)
		conn.commit()
		cur.close()
		if groupdata:
			return ({"attributes": {"status_desc": "Group Created",
	                                "status": "success"
	                                }
	                 }), status.HTTP_200_OK

#-------------------------create-group-----------------------------------------#


def assignAssignmentToStudents(assignment_id,student_list,due_date):
	connection = lab_lang()
	cursor = connection.cursor()

	conn = mysql_next_connection()
	curlog = conn.cursor()
	current_date = datetime.now()
	cursor.execute("""SELECT `Teacher_ID`,`Title` FROM `assignment` 
		WHERE `Assignment_ID` = %s""",(assignment_id))

	assignDtls = cursor.fetchone()
	teacherId = assignDtls.get('Teacher_ID')
	assignmentDesc = assignDtls.get('Title')

	curlog.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name 
					FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(teacherId))
	tidDtls = curlog.fetchone()

	studentInsertQuery = ("""INSERT INTO `assignment_mapping`(`Assignment_ID`, `Student_UserID`, 
			`Status`, `DUE_DATE`) VALUES (%s,%s,%s,%s)""")
	notify_url = BASE_URL + 'app_notify/AppCommunicationAPI/appMessage'
	headers = {'Content-type':'application/json', 'Accept':'application/json'}
	for sid in student_list:
		studentMapData = (assignment_id,sid,'w',due_date)
		cursor.execute(studentInsertQuery,studentMapData)
		connection.commit()
		curlog.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name 
				FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(sid))
		sidDtls = curlog.fetchone()
		data = {'appParams': {},
				'mailParams': {"student":sidDtls.get('name'),
								"assignmentname":assignmentDesc,
								"startdate":current_date,
								"teacher":tidDtls.get('name')},
				'role': 's1',
				'toMail': '',
				'toNumber': '',
				'userId': sid,
				'sourceapp': 'AST001ALT'
				}
		
		response = requests.post(notify_url, data=json.dumps(data), headers=headers)

	
	cursor.close()
	curlog.close()



@name_space.route("/studentAssignmentMapping")
class studentAssignmentMapping(Resource):
	@api.expect(student_assignment_mapping_model)
	def post(self):
		labconnection = lab_lang()
		labcursor = labconnection.cursor()

		details = request.get_json()
		assignment_id = details.get('assignment_id')
		group_id = details.get('group_id')
		teacher_id = details.get('teacher_id')
		assignment_duedate = details.get('assignment_duedate')
		student_id = details.get('student_id')
		is_group = details.get('is_group')
		studentList = []
		groupassign_query = ("""INSERT INTO `assignment_group_mapping`(`assignment_id`, 
					`group_id`, `last_update_id`) VALUES (%s,%s,%s)""")
		
		if is_group.lower() == 'y':
			for gid in group_id:
				mappdata = (assignment_id,gid,teacher_id)
				labcursor.execute(groupassign_query,mappdata)
			studentList = utils.getStudentListFromGroupid(group_id)
			studentList = list(set(studentList))
			msg = 'Assigned to group'
		elif is_group.lower() == 'n':
			studentList = student_id
			msg = 'Assigned to students'
		else:
			msg = 'is_group should be y/n'

		if studentList:
			sendrReq = (assignment_id,studentList,assignment_duedate)
			thread_a = Compute(sendrReq,'studentAssignmentMapping')
			thread_a.start()
		labconnection.commit()
		
		labcursor.close()
		return ({"attributes": {"status_desc": "Group Assignment Mapping",
								"status": "success"},
				"responseList":msg}), status.HTTP_200_OK



@name_space.route("/getAssignmentDtlsByStatusAssignmentIdV2/<string:assignment_status>/<int:student_id>",
	doc={'params':{'start': 'assignmentId','limit':'limit','page':'pageno'}})
class getAssignmentDtlsByStatusAssignmentIdV2(Resource):
	def get(self,assignment_status,student_id):
		nextconnection = mysql_next_connection()
		nextcursor = nextconnection.cursor()

		labconnection = lab_lang()
		labcursor = labconnection.cursor()

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		labcursor.execute("""SELECT count(assignment_mapping.`Assignment_ID`) as 'count'
				FROM `assigment_result` right join `assignment` on 
				assigment_result.`Assignment_ID`=assignment.`Assignment_ID` right join 
				`assignment_mapping` on assignment.`Assignment_ID` = assignment_mapping.`Assignment_ID` 
				WHERE `Student_UserID` = %s and Status = %s 
				and assignment.`Teacher_ID`!='NULL'""",(student_id,assignment_status))
		countDtls = labcursor.fetchone()
		total_count = countDtls.get('count')
		cur_count = int(page) * int(limit)

		if start == 0:
			previous_url = ''
			labcursor.execute("""SELECT assignment_mapping.`Assignment_ID`,`Result`,
				assigment_result.`Remarks`as resultRemarks,`Paramater_Id`,`Teacher_ID`,
				`Assignment_Type`,`Content_Master_ID`,assignment.`Remarks`,
				`Title`,`Status`,assignment_mapping.`Last_Update_TS` 
				FROM `assigment_result` right join `assignment` on 
				assigment_result.`Assignment_ID`=assignment.`Assignment_ID` right join 
				`assignment_mapping` on assignment.`Assignment_ID` = assignment_mapping.`Assignment_ID` 
				WHERE `Student_UserID` = %s and Status = %s 
				and assignment.`Teacher_ID`!='NULL' 
				order by Assignment_ID Desc limit %s""",(student_id,assignment_status,limit))
			assignment_dtls = labcursor.fetchall()
		else:
			
			labcursor.execute("""SELECT assignment_mapping.`Assignment_ID`,`Result`,
				assigment_result.`Remarks`as resultRemarks,`Paramater_Id`,`Teacher_ID`,
				`Assignment_Type`,`Content_Master_ID`,assignment.`Remarks`,
				`Title`,`Status`,assignment_mapping.`Last_Update_TS` 
				FROM `assigment_result` right join `assignment` on 
				assigment_result.`Assignment_ID`=assignment.`Assignment_ID` right join 
				`assignment_mapping` on assignment.`Assignment_ID` = assignment_mapping.`Assignment_ID` 
				WHERE `Student_UserID` = %s and Status = %s and assignment_mapping.`Assignment_ID` < %s
				and assignment.`Teacher_ID`!='NULL' 
				order by Assignment_ID Desc limit %s""",(student_id,assignment_status,start,limit))
			assignment_dtls = labcursor.fetchall()

			# previous = '?start=%d&limit=%d'.format(assignment_dtls[0].get('Assignment_ID'),limit)
		# print(assignment_dtls)

		for aid,assign in enumerate(assignment_dtls):
			# teacherid = assignment_dtls[j]['Teacher_ID']
			teacherid = assign.get('Teacher_ID')
			# print(teacherid)
			# assignment_id = assignment_dtls[j]['Assignment_ID']
			assignment_id = assign.get('Assignment_ID')
			assign['Last_Update_TS'] = assign.get('Last_Update_TS').isoformat()
			if assign.get('Result') == None:
				assign['Result']=""

			if  assign.get('resultRemarks') == None:
				 assign['resultRemarks']=""
				# print(assignment_dtls[j]['resultRemarks'])

			if assign.get('Paramater_Id') == None:
				assign['Paramater_Id']=""
			

			if assign.get('Content_Master_ID')== None:
				assign['Content_Master_ID']=""

			labcursor.execute("""SELECT `Mapping_ID`,`Content_ID`,`File_Path`,`File_type` FROM 
				`assignment_file_mapping` WHERE `Assignment_ID`=%s""",(assignment_id))
			tea_filesdtls = labcursor.fetchall()
			if tea_filesdtls:
				assign['Teacher_Files'] = tea_filesdtls
			else:
				assign['Teacher_Files'] =[]

			labcursor.execute("""SELECT `Student_Activity_Id`,`Content_Path`,`Content_Type`
				FROM `activity_assignment_mapping` WHERE `Student_Id`=%s and 
				`Assignment_ID`=%s order by `Student_Activity_Id` Desc""",(student_id,assignment_id))
			stu_filesdtls = labcursor.fetchall()
			if stu_filesdtls:
				assign['Student_Files'] = stu_filesdtls
			else:
				assign['Student_Files'] =[]

			nextcursor.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`)as 
				teachername FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID`
				=%s""",(teacherid))
			teacherdtls = nextcursor.fetchone()
			# print(teacherdtls)
			teachername = teacherdtls['teachername']
			# print(teachername)
			assign['teachername']=teachername


			page_next = page + 1
			if cur_count < total_count:
				next_url = '?start={}&limit={}&page={}'.format(assignment_dtls[-1].get('Assignment_ID'),limit,page_next)
			else:
				next_url = ''
	        	
		return ({"attributes": {"status_desc": "Assignment Details",
								"status": "success",
								"total":total_count,
								'previous':previous_url,
								'next':next_url
								},
		"responseList":assignment_dtls}), status.HTTP_200_OK

#-----------------------------get-teacher-assignment-details---------------------------#
@name_space.route("/getAssignmentDtlsByTeacherIdV2/<int:teacher_id>",
	doc={'params':{'start':'assinmentId','limit':'limit','page':'pageno'}})
class getAssignmentDtlsByTeacherIdV2(Resource):
    def get(self,teacher_id):
        nextconnection = mysql_next_connection()
        nextcursor = nextconnection.cursor()

        labconnection = lab_lang()
        labcursor = labconnection.cursor()

        start=int(request.args.get('start', 0))
        limit=int(request.args.get('limit', 10))
        page=int(request.args.get('page', 1))

        previous_url = ''
        next_url = ''

        labcursor.execute("""SELECT count(`Assignment_ID`)as 'count' FROM 
        	`assignment` WHERE `Teacher_ID`=%s""",(teacher_id))
        countDtls = labcursor.fetchone()

        total_count = countDtls.get('count')
        cur_count = int(page) * int(limit)
        

        if start == 0:
        	previous_url = ''

	        labcursor.execute("""SELECT assignment.`Assignment_ID`, `Teacher_ID`,`Title`,
	        	`Last_Update_TS`, `Last_Update_ID` FROM 
	        	`assignment`  WHERE `Teacher_ID`=%s order by Assignment_ID Desc
	        	limit %s""",(teacher_id,limit))
	        assignment_dtls = labcursor.fetchall()

	        for j in range(len(assignment_dtls)):
	        	assignment_id = assignment_dtls[j]['Assignment_ID']
	        	if assignment_dtls[j]['Last_Update_TS'] == '0000-00-00':
	        		assignment_dtls[j]['Last_Update_TS'] = '0000-00-00'

	        	else:
		        	assignment_dtls[j]['Last_Update_TS'] = assignment_dtls[j]['Last_Update_TS'].isoformat()
			        
		        labcursor.execute("""SELECT `Mapping_ID`,`Content_ID`,`File_type`,`File_Path` FROM 
		        	`assignment_file_mapping` WHERE `Assignment_ID`=%s order by 
		        	`Mapping_ID` Desc""",(assignment_id))
		        filesdtls = labcursor.fetchall()

		        if filesdtls:
			        assignment_dtls[j]['uploadfile_dtls'] = filesdtls
		        else:
		        	assignment_dtls[j]['uploadfile_dtls'] =[]

		        labcursor.execute("""SELECT `Assignment_ID`,`Student_UserID`,`Status` FROM 
		        	`assignment_mapping` WHERE `Assignment_ID`=%s""",(assignment_id))
		        assigndtls = labcursor.fetchall()
		        if assigndtls:
			        assignment_dtls[j]['assignStudent_dtls'] = assigndtls
		        else:
		        	assignment_dtls[j]['assignStudent_dtls'] =[]
		        for j in range(len(assigndtls)):
			        student_id = assigndtls[j]['Student_UserID']
		        	
			        nextcursor.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`)as 
			        	studentname FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID`
			        	=%s""",(student_id))
		        	studentdtls = nextcursor.fetchone()
		        	if studentdtls:
			        	studentname = studentdtls['studentname']
			        	assigndtls[j]['studentname']=studentname
			        else:
			        	assigndtls[j]['studentname']= ''
        else:
        	labcursor.execute("""SELECT assignment.`Assignment_ID`, `Teacher_ID`,`Title`,
	        	`Last_Update_TS`, `Last_Update_ID` FROM 
	        	`assignment`  WHERE `Teacher_ID`=%s and `Assignment_ID`<%s 
	        	order by Assignment_ID Desc limit %s""",(teacher_id,start,limit))
	        assignment_dtls = labcursor.fetchall()
	        

	        for j in range(len(assignment_dtls)):
	        	assignment_id = assignment_dtls[j]['Assignment_ID']
	        	
	        	if assignment_dtls[j]['Last_Update_TS'] == '0000-00-00':
	        		assignment_dtls[j]['Last_Update_TS'] = '0000-00-00'
	        		
	        	else:
	        		assignment_dtls[j]['Last_Update_TS'] = assignment_dtls[j]['Last_Update_TS'].isoformat()
		        
		        labcursor.execute("""SELECT `Mapping_ID`,`Content_ID`,`File_type`,`File_Path` FROM 
		        	`assignment_file_mapping` WHERE `Assignment_ID`=%s order by 
		        	`Mapping_ID` Desc""",(assignment_id))
		        filesdtls = labcursor.fetchall()

		        if filesdtls:
			        assignment_dtls[j]['uploadfile_dtls'] = filesdtls
		        else:
		        	assignment_dtls[j]['uploadfile_dtls'] =[]

		        labcursor.execute("""SELECT `Assignment_ID`,`Student_UserID`,`Status` FROM 
		        	`assignment_mapping` WHERE `Assignment_ID`=%s""",(assignment_id))
		        assigndtls = labcursor.fetchall()
		        if assigndtls:
			        assignment_dtls[j]['assignStudent_dtls'] = assigndtls
		        else:
		        	assignment_dtls[j]['assignStudent_dtls'] =[]
		        for j in range(len(assigndtls)):
			        student_id = assigndtls[j]['Student_UserID']
		        	
			        nextcursor.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`)as 
			        	studentname FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID`
			        	=%s""",(student_id))
		        	studentdtls = nextcursor.fetchone()
		        	
		        	if studentdtls:
			        	studentname = studentdtls['studentname']
			        	assigndtls[j]['studentname']=studentname
			        else:
			        	assigndtls[j]['studentname']= ''
        page_next = page + 1
        if cur_count < total_count:
        	next_url = '?start={}&limit={}&page={}'.format(assignment_dtls[-1].get('Assignment_ID'),limit,page_next)
        else:
        	next_url = ''
		
        nextconnection.commit()
        nextcursor.close()
        labconnection.commit()
        labcursor.close()

        return ({"attributes": {"status_desc": "Teacher Assignment Details.",
									"status": "success",
									"total":total_count,
									"previous":previous_url,
									"next":next_url
									},
					"responseList": assignment_dtls}), status.HTTP_200_OK	

#-----------------------------get-teacher-assignment-details---------------------------#



