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

def connect_logindb():
    connection = pymysql.connect(host='creamsonservices.com',
                                    user='creamson_langlab',
                                    password='Langlab@123',
                                    db='creamson_logindb',
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)
    return connection'''

def mysql_connection():
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
#----------------------database-connection---------------------#

library = Blueprint('library_api', __name__)
api = Api(library,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('Library&Liveclass',description='Get Library')


BASE_URL = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/'
#-----------------------assessment-by-contentid-----------------------------#

@name_space.route("/getassessmentbyContentId/<int:contentid>")
class getassessmentbyContentId(Resource):
    def get(self,contentid):
        connection = mysql_connection()
        cursor = connection.cursor()
        cursor.execute("""SELECT `Assessment_ID`,`Assesment_Desc`,`feature_flag`,`teacher_id`,assessment.`subject_id`,`subject_name`,assessment.`topic_id`,`topic_name`,
            `Content_File_Path`,`Content_FileName`,`FileType_Id`,`assessment_duration` FROM `assessment`,`topic`,
            `subject` WHERE `Assessment_ID` in(SELECT `Assessment_ID` FROM 
            `content_assessment_mapping` WHERE `Content_ID`=%s) and assessment.`topic_id`= 
            topic.`topic_id` and assessment.`subject_id`= subject.`subject_id` order by Assessment_ID asc
            """,(contentid))
        get_assessment = cursor.fetchall()
        for aid, ass in enumerate(get_assessment):
            if ass.get('assessment_duration'):
                ass['assessment_duration'] = str(ass.get('assessment_duration'))
        connection.commit()
        cursor.close()
        return ({"attributes": {"status_desc": "Assessment Details",
                                "status": "success"
                                    },
                "responseList":get_assessment}), status.HTTP_200_OK
   
#-----------------------assessment-by-contentid-----------------------------#

#-----------------------assessment-by-studentid-----------------------------#
@name_space.route("/getassessmentbyStudentId/<int:student_id>")
class getassessmentbyStudentId(Resource):
    def get(self,student_id):
        connection = mysql_connection()
        cursor = connection.cursor()

        cursor.execute("""SELECT assessment.`Assessment_ID`,`Assesment_Desc`,`status`, 
            `feature_flag`,`teacher_id`, assessment. `subject_id`,`subject_name`,assessment. 
            `topic_id`,`topic_name`, `Content_File_Path`, `Content_FileName`,`FileType_Id`,
            concat(`student_assesssment_filepath`,`student_assesssment_filename`) 
            as 'student_assessment_filepath', `student_assessment_filetype`,`total_marks`,`teacher_feedback`
            ,`assessment_duration` FROM `assessment`inner join `topic` on assessment.`topic_id`=topic.`topic_id` 
            INNER JOIN `student_assessment_mapping` ON assessment.`Assessment_ID`=
            student_assessment_mapping.`assessment_id` INNER JOIN `subject` on assessment.
            `subject_id` = subject.`subject_id` WHERE `student_id`=%s order by `Assessment_ID` 
            asc""",(student_id))
        get_assessment = cursor.fetchall()
        for aid, ass in enumerate(get_assessment):
            if ass.get('assessment_duration'):
                ass['assessment_duration'] = str(ass.get('assessment_duration'))
        
        connection.commit()
        cursor.close()
        return ({"attributes": {"status_desc": "Assessment Details",
                                "status": "success"
                                    },
                "responseList":get_assessment}), status.HTTP_200_OK
#-----------------------assessment-by-studentid-----------------------------#

#-----------------------assessment-by-liceclassid-----------------------------#
@name_space.route("/getassessmentbyLiveclassId/<int:liveclass_id>")
class getassessmentbyLiveclassId(Resource):
    def get(self,liveclass_id):
        connection = mysql_connection()
        cursor = connection.cursor()

        
        cursor.execute("""SELECT `Assessment_ID`,`Assesment_Desc`,`feature_flag`,`teacher_id`,assessment.
            `subject_id`,`subject_name`,assessment.`topic_id`,`topic_name`,
            `Content_File_Path`,`Content_FileName`,`FileType_Id` FROM `assessment`,`topic`,
            `subject`  WHERE `Assessment_ID` in(SELECT `Assessment_ID` FROM 
            `content_assessment_mapping` WHERE `Content_ID` in(SELECT `content_id` FROM 
            `content_liveclass_mapping` WHERE `liveclass_id`=%s))and assessment.`topic_id`= 
            topic.`topic_id` and assessment.`subject_id`= subject.`subject_id` 
             order by `Assessment_ID` asc""",(liveclass_id))
        get_assessment = cursor.fetchall()
        # for aid, ass in enumerate(get_assessment):
        #     if ass.get('assessment_duration'):
        #         ass['assessment_duration'] = str(ass.get('assessment_duration'))
        
        connection.commit()
        cursor.close()
        return ({"attributes": {"status_desc": "Assessment Details",
                                "status": "success"
                                    },
                "responseList":get_assessment}), status.HTTP_200_OK
#-----------------------assessment-by-liceclassid-----------------------------#

#-----------------------assessment-by-teacherid-----------------------------#
@name_space.route("/getassessmentbyTeacherId/<int:teacher_id>")
class getassessmentbyTeacherId(Resource):
    def get(self,teacher_id):
        connection = mysql_connection()
        cursor = connection.cursor()

        cursor.execute("""SELECT `Assessment_ID`,`Assesment_Desc`,`teacher_id`,subject.
            `subject_id`,`subject_name`,topic.`topic_id`,`topic_name`,
            `Content_File_Path`,`Content_FileName`,`FileType_Id`,`feature_flag` ,`assessment_duration`
            FROM `assessment`,`topic`, `subject` WHERE `teacher_id`=%s and assessment.`topic_id`
            = topic.`topic_id` and assessment.`subject_id`= subject.`subject_id` order by 
            Assessment_ID asc""",(teacher_id))
        get_assessment = cursor.fetchall()
        for aid, ass in enumerate(get_assessment):
            if ass.get('assessment_duration'):
                ass['assessment_duration'] = str(ass.get('assessment_duration'))
        
        connection.commit()
        cursor.close()
        return ({"attributes": {"status_desc": "Assessment Details",
                                "status": "success"
                                    },
                "responseList":get_assessment}), status.HTTP_200_OK
#-----------------------assessment-by-teacherid-----------------------------#

#-----------------------studentlist-by-contentid-----------------------------#
@name_space.route("/getstudentlistbyContentId/<int:contentid>")
class getstudentlistbyContentId(Resource):
    def get(self,contentid):
        connection = mysql_connection()
        cursor = connection.cursor()

        nextconnection = connect_logindb()
        nextcursor = nextconnection.cursor()
        

        cursor.execute("""SELECT `student_id` FROM `content_student_mapping` WHERE 
         `content_id`=%s order by student_id asc""",(contentid))
        get_student = cursor.fetchall()
        
        for i, sid in enumerate(get_student):
            nextcursor.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name, 
                `image_url` as student_image FROM `institution_user_credential` 
                WHERE `INSTITUTION_USER_ID` = %s""",(sid.get('student_id')))
            student_name = nextcursor.fetchone()
            if student_name:
                sid['student_name']  = student_name.get('name')
                sid['student_image'] = student_name.get('student_image')
        return ({"attributes": {"status_desc": "Student Details",
                                "status": "success"},
                "responseList": get_student}), status.HTTP_200_OK
#-----------------------studentlist-by-contentid-----------------------------#

#-----------------------contentlist-by-liveclassid-----------------------------#
@name_space.route("/getcontentlistbyLiveclassId/<int:liveclass_id>")
class getcontentlistbyLiveclassId(Resource):
    def get(self,liveclass_id):
        connection = mysql_connection()
        cursor = connection.cursor()

        cursor.execute("""SELECT content_library.`content_id`,`pre_post_flag`,`content_name`,
            `content_filepath`,`content_filename`,`content_filetype`,`teacher_id`,subject. 
            `subject_id`,`subject_name`,topic.`topic_id`,`topic_name` FROM `content_library` 
            LEFT JOIN `content_liveclass_mapping` on content_library.`content_id`= 
            content_liveclass_mapping.`content_id` LEFT JOIN `topic` ON content_library.
            `topic_id`=topic.`topic_id` LEFT JOIN `subject` on topic.`subject_id`=subject.
            `subject_id` WHERE `liveclass_id`=%s and `content_name`!='Prelive-Dummy' and 
            `content_name`!='Postlive-Dummy'order by `content_id` asc""",(liveclass_id))
        getcontent = cursor.fetchall()
        
        return ({"attributes": {"status_desc": "Student Details",
                                "status": "success"},
                "responseList": getcontent}), status.HTTP_200_OK
#-----------------------contentlist-by-liveclassid-----------------------------#

#-----------------------student-notificationlist-by-liveclassid-----------------------------#
@name_space.route("/getLiveClassNotificationforStudent/<int:liveclass_id>")
class getLiveClassNotificationforStudent(Resource):
    def get(self,liveclass_id):
        connection = mysql_connection()
        cursor = connection.cursor()

        nextconnection = connect_logindb()
        nextcursor = nextconnection.cursor()

        cursor.execute("""SELECT `liveclass_id`,`meeting_id` FROM `liveclass_mapping` WHERE 
            `liveclass_id` = %s""",(liveclass_id))
        zoomDtls = cursor.fetchall()
        meetList = []
        if zoomDtls:
            for zid, zoom in enumerate(zoomDtls):
                # print(zoom['meeting_id'])
                nextcursor.execute("""SELECT `NOTIFICATION_TRACKING_ID`,`MEETING_ID`,
                    `MEETING_GROUP`,`MEETING_GROUP_ID` FROM `notification_tracking_dtls` 
                    WHERE `MEETING_ID`=%s""",(zoom['meeting_id']))
                meetingDtls = nextcursor.fetchall()

                
                if meetingDtls:
                    for mid,meet in enumerate(meetingDtls):
                        if meet['MEETING_GROUP'] == 'I':
                            if meet['MEETING_GROUP_ID'] :
                                nextcursor.execute("""SELECT `INSTITUTION_USER_ID`as Student_id,concat(`FIRST_NAME`,' ',
                                  `LAST_NAME`)as student_name,`IMAGE_URL` FROM `institution_user_credential`  
                                  WHERE `INSTITUTION_USER_ID` = %s""",(meet['MEETING_GROUP_ID']))
                                meetList = nextcursor.fetchall()       
                        else:
                            nextcursor.execute("""SELECT `Group_ID`,`Group_Description` 
                                FROM `group_master` WHERE `Group_ID`= %s""",
                                (meet['MEETING_GROUP_ID']))

                            meetList = nextcursor.fetchall()

        return ({"attributes": {"status_desc": "Notification Details",
                                "status": "success"
                                    },
                "responseList":meetList}), status.HTTP_200_OK
#-----------------------student-notificationlist-by-liveclassid-----------------------------#

#-----------------------contentdetails-----------------------------#
@name_space.route("/contentDetails/<int:teacher_id>")
class contentDetails(Resource):
    def get(self,teacher_id):
        connection = mysql_connection()
        cursor = connection.cursor()

        nextconnection = connect_logindb()
        nextcursor = nextconnection.cursor()
        
        cursor.execute("""SELECT count(`content_id`)as total FROM `content_library` 
            WHERE `teacher_id`=%s""",(teacher_id))

        totalcontent_count = cursor.fetchone()
        total_content = totalcontent_count['total']
        # print(total_content)

        cursor.execute("""SELECT COUNT(`Student_ID`)as total FROM `student_content_tracking`
         WHERE `Content_ID` in(SELECT `content_id` FROM `content_library` WHERE 
         `teacher_id`=%s)""",(teacher_id))

        count_seencontent = cursor.fetchone()
        total_seencontent = count_seencontent['total']
        # print(total_seencontent)

        cursor.execute("""SELECT student_content_tracking.`content_id`,
            content_library.`topic_id`, `topic_name`,subject.`subject_id`,
            `subject_name`,`Student_ID`as student_id,
            `content_name`,`content_filepath`,`content_filename`,
            `content_filename` FROM `content_library` INNER join 
            `student_content_tracking` on content_library.`content_id`
            = student_content_tracking.`Content_ID` INNER JOIN `topic` 
            on content_library.`topic_id`= topic.`topic_id` INNER JOIN 
            `subject` on topic.`subject_id`= subject. `subject_id` where 
            content_library.`teacher_id`=%s order by student_content_tracking.`content_id`
            asc""",(teacher_id))
        studentid = cursor.fetchall()
        # print(studentid)
        for i in range(len(studentid)):
         student_id= studentid[i]['student_id']
         # print(student_id)
         nextcursor.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`)as 
                name FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` 
                = %s""",(student_id))
         studentname = nextcursor.fetchall()
         # print(studentname)

         studentid[i]['student_dtls'] = studentname
        return ({"attributes": {"status_desc": "Content Details",
                                "status": "success"
                                },
                 "responseList":  {
                                   "content": total_content,
                                  
                                   "seen": total_seencontent,

                                   "seencontent_dtls": studentid
                                  },
                }), status.HTTP_200_OK
#-----------------------contentdetails-----------------------------#

#-----------------------liveclassdetails-------------------------------------------#
@name_space.route("/liveclassdetailsByUserid/<int:teacher_id>")
class liveclassdetailsByUserid(Resource):
    def get(self,teacher_id):
        connection = mysql_connection()
        cursor = connection.cursor()

        nextconnection = connect_logindb()
        nextcursor = nextconnection.cursor()

        cursor.execute("""SELECT count(`liveclass_id`)as total FROM `liveclass_mapping` WHERE 
         `teacher_id`=%s""",(teacher_id))

        totalliveclass = cursor.fetchone()
        liveclass = totalliveclass['total']
        # print(total)

        cursor.execute("""SELECT count(`Student_ID`)as total FROM 
            `student_liveclass_tracking` WHERE `liveclass_id` in(SELECT `liveclass_id` FROM
            `liveclass_mapping` WHERE `teacher_id` = %s)""",(teacher_id))

        attendliveclass = cursor.fetchone()
        attended = attendliveclass['total']
        # print(attended)

        cursor.execute("""SELECT liveclass_mapping.`liveclass_id`,`Student_ID` FROM 
            `liveclass_mapping` INNER JOIN `student_liveclass_tracking` ON 
            liveclass_mapping.`liveclass_id` = student_liveclass_tracking.`liveclass_id`
             WHERE liveclass_mapping.`teacher_id`= %s""",(teacher_id))

        attendliveclass_dtls = cursor.fetchall()
        liveList = []
        for aid, attened in enumerate(attendliveclass_dtls):
            # print(attened['Student_ID'])
            nextcursor.execute("""SELECT concat(`FIRST_NAME`,'',`LAST_NAME`)as name,
                `IMAGE_URL`,`PRIMARY_CONTACT_NUMBER` FROM `institution_user_credential`
                 WHERE `INSTITUTION_USER_ID`= %s""",(attened['Student_ID']))
            studentDtls = nextcursor.fetchall()

            for sid,live in enumerate(studentDtls):
                live['liveclass_id'] = attened.get('liveclass_id')
                live['Student_ID'] = attened.get('Student_ID')
                live['name'] = live.get('name')
                live['IMAGE_URL'] = live.get('IMAGE_URL')
                live['PRIMARY_CONTACT_NUMBER'] = live.get('PRIMARY_CONTACT_NUMBER')
                liveList.append(live)

        return ({"attributes": {"status_desc": "Liveclass Details",
                                "status": "success"
                                },
                 "responseList":  {
                                   "Total Liveclass": liveclass,
                                  
                                   "Attended Liveclass": attended,

                                   "Attended Liveclass Dtls": liveList
                                  },
                }), status.HTTP_200_OK
#-----------------------liveclassdetails---------------------------------------------#

#---------------------------assessmentDetailsByUserId-------------------------------------------#
@name_space.route("/assessmentdetailsByUserid/<int:teacher_id>")
class assessmentdetailsByUserid(Resource):
    def get(self,teacher_id):
        connection = mysql_connection()
        cursor = connection.cursor()

        nextconnection = connect_logindb()
        nextcursor = nextconnection.cursor()

        cursor.execute("""SELECT count(`Assessment_ID`)as total FROM `assessment` WHERE 
            `teacher_id`=%s""",(teacher_id))

        totalassessmnet = cursor.fetchone()
        totalassessment = totalassessmnet['total']
        # print(total)

        cursor.execute("""SELECT count(`student_id`)as total FROM 
            `student_assessment_mapping` WHERE `assessment_id` in(SELECT `Assessment_ID` 
            FROM `assessment` WHERE `teacher_id`= %s)""",(teacher_id))

        assignedstudent = cursor.fetchone()
        assign = assignedstudent['total']
        # print(assigned)

        cursor.execute("""SELECT assessment.`Assessment_ID`,`Assesment_Desc`,assessment.
            `topic_id`,`topic_name`,subject.`subject_id`, `subject_name`,`feature_flag`,
            `student_id`,`status`,`total_marks`,`assessment_duration` FROM `assessment` INNER JOIN 
            `student_assessment_mapping` ON assessment.`Assessment_ID`=
            student_assessment_mapping.`assessment_id` INNER JOIN `topic` on assessment.
            `topic_id`= topic.`topic_id` INNER JOIN `subject` on topic.`subject_id`= 
            subject. `subject_id` where `teacher_id`=%s order by assessment.`Assessment_ID` 
            asc""",(teacher_id))

        assignedassessment_dtls = cursor.fetchall()
        assessmentList = []
        for aid, assigned in enumerate(assignedassessment_dtls):
            if assigned.get('assessment_duration'):
                assigned['assessment_duration'] = str(assigned.get('assessment_duration'))
            # print(assigned['student_id'])
            nextcursor.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`)as name,
                `IMAGE_URL` FROM `institution_user_credential`
                 WHERE `INSTITUTION_USER_ID`= %s""",(assigned['student_id']))
            studentDtls = nextcursor.fetchall()

            for sid,assessment in enumerate(studentDtls):
                assessment['Assessment_ID'] = assigned.get('Assessment_ID')
                assessment['Assesment_Desc'] = assigned.get('Assesment_Desc')
                assessment['topic_id'] = assigned.get('topic_id')
                assessment['subject_id'] = assigned.get('subject_id')
                assessment['topic_name'] = assigned.get('topic_name')
                assessment['subject_name'] = assigned.get('subject_name')
                assessment['feature_flag'] = assigned.get('feature_flag')
                assessment['student_id'] = assigned.get('student_id')
                assessment['status'] = assigned.get('status')
                assessment['total_marks'] = assigned.get('total_marks')
                assessment['name'] = assessment.get('name')
                assessment['IMAGE_URL'] = assessment.get('IMAGE_URL')
                assessment['assessment_duration'] = assigned.get('assessment_duration')
                assessmentList.append(assessment)

        return ({"attributes": {"status_desc": "Assessment Details",
                                "status": "success"
                                },
                 "responseList":  {
                                   "Total Assessment": totalassessment,
                                  
                                   "Assigned Assessment": assign,

                                   "Assigned Assessment Dtls": assessmentList
                                  },
                }), status.HTTP_200_OK
#-----------------------assessmentDetailsByUserId---------------------------------------------#


@name_space.route("/getStudentlistByLiveclassId/<int:liveclass_id>")
class getStudentlistByLiveclassId(Resource):
    def get(self,liveclass_id):
        connection = mysql_connection()
        cursor = connection.cursor()
        nextconnection = connect_logindb()
        nextcursor = nextconnection.cursor()

        cursor.execute("""SELECT `student_id` FROM `liveclass_student_mapping` WHERE 
            `liveclass_id` = %s""",(liveclass_id))

        studentList = cursor.fetchall()
        headers = {'Content-type':'application/json', 'Accept':'application/json'}
        getConURL = BASE_URL+"library_dtls/Library&Liveclass/getcontentlistbyLiveclassId/{}".format(liveclass_id)
        contentListDtls = requests.get(getConURL,headers=headers).json().get('responseList')

        if studentList:
            for sid, student in enumerate(studentList):
                nextcursor.execute("""SELECT `INSTITUTION_USER_ID`as Student_id,concat(`FIRST_NAME`,' ',
                    `LAST_NAME`)as student_name,`PRIMARY_CONTACT_NUMBER`,
                    `IMAGE_URL` FROM `institution_user_credential`  
                    WHERE `INSTITUTION_USER_ID` = %s order by student_name asc""",(student.get('student_id')))
                studentDtls = nextcursor.fetchone()
                studentList[sid] = studentDtls
                cursor.execute("""SELECT `Status`FROM `student_liveclass_tracking` 
                    WHERE `Student_ID`=%s and liveclass_id = %s""",(student.get('student_id'),liveclass_id))
                attenddtls = cursor.fetchone()
                if attenddtls:
                    studentDtls['status']=attenddtls.get('Status')

                else:
                   studentDtls['status']='A'
                studentDtls['contentDtls'] = []
                studentDtls['assessmentDtls'] = []
                
                if contentListDtls:
                    for cid, con in enumerate(contentListDtls):
                        cursor.execute("""SELECT `Duration`,`Status` FROM `student_content_tracking` 
                            WHERE `Student_ID` = %s 
                            AND `Content_ID` = %s""",(student.get('student_id'),con.get('content_id')))

                        conDtls = cursor.fetchone()

                        if conDtls:
                            studentDtls['contentDtls'].append({"duration":conDtls.get('Duration',0),
                                                            "status":"seen",
                                                            "contentId":con.get('content_id'),
                                                            "content_name":con.get('content_name')
                                                            })
                        else:
                             studentDtls['contentDtls'].append({"duration":0,
                                                            "status":"unseen",
                                                            "contentId":con.get('content_id'),
                                                            "content_name":con.get('content_name')
                                                            })
                        
                        getassessmentURL = BASE_URL+"library_dtls/Library&Liveclass/getassessmentbyContentId/{}".format(con.get('content_id'))
                        assessmentListDtls = requests.get(getassessmentURL, headers=headers).json().get('responseList')
                        
                        if assessmentListDtls:
                            for aid, ass in enumerate(assessmentListDtls):
                                cursor.execute("""SELECT `status`,`total_marks` 
                                    FROM `student_assessment_mapping` WHERE `student_id` = %s 
                                    AND `assessment_id` = %s""",(student.get('student_id'),ass.get('Assessment_ID')))

                                assessDtls = cursor.fetchone()
                                if assessDtls:
                                    if not ass.get('Assesment_Desc'):
                                        ass['Assesment_Desc'] = con.get('content_name')
                                    if assessDtls.get('status') == 'a':
                                        assessDtls['status'] = 'assigned'
                                    elif assessDtls.get('status') == 'i':
                                        assessDtls['status'] = 'incomplete'
                                    elif assessDtls.get('status') == 'c':
                                        assessDtls['status'] = 'complete'
                                    if not assessDtls.get('total_marks'):
                                        assessDtls['total_marks'] = 0
                                    studentDtls['assessmentDtls'].append({"total_marks":assessDtls.get('total_marks',0),
                                                                    "status":assessDtls.get('status'),
                                                                    "assessmentId":ass.get('Assessment_ID'),
                                                                    "assessment_desc":ass.get('Assesment_Desc')
                                                                    })
            studentList = sorted(studentList, key = lambda i: i['student_name']) 
                       

        return ({"attributes": {"status_desc": "Live Class Details",
                                "status": "success"
                                    },
                "responseList":studentList}), status.HTTP_200_OK

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
