import pymysql

'''def connnect_userLibrary():
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

def connnect_userLibrary():
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


def connect_langlab():
	connection = pymysql.connect(host='creamsonservices.com',
									user='creamson_langlab',
									password='Langlab@123',
									db='creamson_lab_lang1',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor)
	return connection


def getStudentListFromGroupid(groupList):

	conn = connect_logindb()
	curLog = conn.cursor()
	studentList = []
	for gid in groupList:
		curLog.execute("""SELECT `Student_Id` FROM `group_student_mapping` 
			WHERE `Group_ID` = %s""",(gid))

		studentDtls = curLog.fetchall()

		for i, x in enumerate(studentDtls):
			studentList.append(x['Student_Id'])

	curLog.close()
	return studentList


def getGroupNameFromGroupid(groupId):

	conn = connect_logindb()
	curLog = conn.cursor()
	groupName = 'Group-'+str(groupId)
	curLog.execute("""SELECT `Group_Description` FROM `group_master` 
		WHERE `Group_ID` = %s""",(groupId))

	groupDtls = curLog.fetchone()
	if groupDtls:
		groupName = groupDtls.get('Group_Description')
		
	curLog.close()
	return groupName


def getGroupListByInstitutionId(institutionId):
	conn = connect_logindb()
	curLog = conn.cursor()

	curLog.execute("""SELECT `Group_ID` FROM `group_master` 
		WHERE `Institution_ID` = %s""",(institutionId))


	groupDtls = curLog.fetchall()

	groupList = [grp['Group_ID'] for gid, grp in enumerate(groupDtls)]
	curLog.close()
	return groupList


def getMeetingListByTeacherId(teacherId):

	conn = connect_logindb()
	curLog = conn.cursor()

	curLog.execute("""SELECT `MEETING_ID` FROM `meeting_dtls` WHERE `TEACHER_ID` = %s 
		and `LAST_UPDATE_ID` = 'zoom'""",(teacherId))

	meetingDtls = curLog.fetchall()

	meetingList = [meet['MEETING_ID'] for mid, meet in enumerate(meetingDtls)]
	curLog.close()
	return meetingList

def getLiveClassIdByMeetingId(meetingId):

	conn = connnect_userLibrary()
	curLib = conn.cursor()

	curLib.execute("""SELECT `liveclass_id` FROM `liveclass_mapping` 
		WHERE `meeting_id` = %s and `meeting_status` = 'created'""",(meetingId))

	liveclassDtls = curLib.fetchall()

	liveclassList = [live['liveclass_id'] for lid, live in enumerate(liveclassDtls)]

	curLib.close()
	return liveclassList


def getLiveClassIdByTeacherId(teacherId):

	conn = connnect_userLibrary()
	curLib = conn.cursor()

	curLib.execute("""SELECT `liveclass_id`,`meeting_id`,`platform` FROM `liveclass_mapping` 
		WHERE `teacher_id` = %s and `meeting_status` = 'created'""",(teacherId))

	liveclassDtls = curLib.fetchall()

	liveclassList = [live['liveclass_id'] for lid, live in enumerate(liveclassDtls)]
	meetingList = [live['meeting_id'] for lid, live in enumerate(liveclassDtls)]
	platformList = [live['platform'] for lid, live in enumerate(liveclassDtls)]

	curLib.close()
	return (liveclassList,meetingList,platformList)


def getAssignedGroupsByMeetingId(meetingId):

	conn = connect_logindb()
	curLog = conn.cursor()

	curLog.execute("""SELECT `MEETING_GROUP_ID` FROM `notification_tracking_dtls` WHERE 
		`MEETING_ID` = %s and `MEETING_GROUP` = 'G'""",(meetingId))

	assignedDtls = curLog.fetchall()

	assignedList = [assigned['MEETING_GROUP_ID'] for aid, assigned in enumerate(assignedDtls)]

	curLog.close()
	return assignedList


def getStudentListByLiveClassId(liveclassId):

	conn = connnect_userLibrary()
	curLib = conn.cursor()

	curLib.execute("""SELECT `student_id` FROM `liveclass_student_mapping` WHERE 
		`liveclass_id` = %s""",(liveclassId))

	studentDtls = curLib.fetchall()

	studentList = [stdnt['student_id'] for sid, stdnt in enumerate(studentDtls)]

	curLib.close()
	return studentList

def assessment_question_mapping(assessment_id,question_id):

	connection = connnect_userLibrary()
	cursor = connection.cursor()

	assQuesMapInsertQuery = ("""INSERT INTO `assessment_question_mapping`(`Assessment_ID`, 
		`Question_ID`) VALUES (%s,%s)""")

	mapData = (assessment_id,question_id)

	cursor.execute(assQuesMapInsertQuery,mapData)

	connection.commit()
	cursor.close()


def getAssignmentIdByTeacherId(teacherId):

	conn = connect_langlab()
	curLib = conn.cursor()

	curLib.execute("""SELECT `Assignment_ID` FROM `assignment` WHERE `Teacher_ID` = %s""",(teacherId))

	assignmentsDtls = curLib.fetchall()

	assignmentList = [assign['Assignment_ID'] for aid, assign in enumerate(assignmentsDtls)]

	curLib.close()
	return (assignmentList)



def getAssignedGroupsByAssignmentId(assignmentId):

	conn = connect_langlab()
	curLog = conn.cursor()

	curLog.execute("""SELECT `group_id` FROM `assignment_group_mapping` WHERE 
		`assignment_id` = %s""",(assignmentId))

	assignedDtls = curLog.fetchall()

	assignedList = [assigned['group_id'] for aid, assigned in enumerate(assignedDtls)]

	curLog.close()
	return assignedList


def getStudentListByAssigmentId(assignmentId):

	conn = connect_langlab()
	curLib = conn.cursor()

	curLib.execute("""SELECT `Student_UserID` FROM `assignment_mapping` WHERE 
		`Assignment_ID` = %s""",(assignmentId))

	studentDtls = curLib.fetchall()

	studentList = [stdnt['Student_UserID'] for sid, stdnt in enumerate(studentDtls)]

	curLib.close()
	return studentList