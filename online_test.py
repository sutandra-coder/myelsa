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
import collections

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

def logindb_connection():
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

def logindb_connection():
    connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
                                 user='admin',
                                 password='cbdHoRPQPRfTdC0uSPLt',
                                 db='creamson_logindb',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection
    
#----------------------database-connection---------------------#

online_test = Blueprint('online_test_api', __name__)
api = Api(online_test,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('OnlineTest',description='Online Test')

#-----------------------submit-que-opt-ans-model-----------------------------------#

submitqueoptans = api.model('submitqueoptans', {
    "Assessment_ID":fields.Integer(),
    "Student_ID": fields.Integer(),
    "Question_ID": fields.Integer(),
    "Option_ID": fields.String(),
    "Answer": fields.String(),
    "answersheet_filepath": fields.String(),
    "filetype": fields.String(),
    "student_remark": fields.String(),
    "marks": fields.String(),
    "teacher_remark": fields.String(),
    "last_update_id":fields.Integer()
    })

submitqueoptansDtls=api.model('submitqueoptansDtls', {
    "submitqueoptans":fields.List(fields.Nested(submitqueoptans))
    })
#-----------------------submit-que-opt-ans-model---------------------------------------#

#-----------------------submit-student-marks-model---------------------------------#
submitmarks = api.model('submitmarks', {
    "Online_Test_ID":fields.Integer(),
    "Student_ID": fields.Integer(),
    "Marks": fields.String(),
    "Last_Updated_ID": fields.Integer()
    })

submitmarksDtls=api.model('submitmarksDtls', {
    "submitmarks":fields.List(fields.Nested(submitmarks))
    })
#-----------------------submit-student-marks-model---------------------------------#

#-----------------------submit-que-opt-ans-model-----------------------------------#
submitassmarks = api.model('submitassmarks', {
    "Online_Test_ID":fields.Integer(),
    "Online_assesment_ID": fields.Integer(),
    "Student_ID": fields.Integer(),
    "Marks": fields.String(),
    "Last_Updated_ID": fields.Integer()
    })

submitassmarksDtls=api.model('submitassmarksDtls', {
    "submitassmarks":fields.List(fields.Nested(submitassmarks))
    })
#-----------------------submit-que-opt-ans-model---------------------------------------#

#-----------------------student-online-test-model-------------------------------------#
submitonlinetest = api.model('submitonlinetest', {
    "submitqueoptans":fields.List(fields.Nested(submitqueoptans)),
    "submitmarks":fields.List(fields.Nested(submitmarks)),
    "submitassmarks":fields.List(fields.Nested(submitassmarks))
    })
#-----------------------student-online-test-model---------------------------------------#

#------------------------------------------------------------#
onlinetestFeeMapping = api.model('onlinetestFeeMapping', {
    "Online_Test_ID":fields.Integer(),
    "is_paid_course":fields.String(),
    "total_fee":fields.Integer(),
    "installment_available":fields.String(),
    "installment_type":fields.String(),
    "no_of_installments":fields.Integer()
    })
#--------------------------------------------------------------#

#-----------------------------------------------------------#
upadateonlinetestFees = api.model('upadateonlinetestFees', {
    "is_paid_course":fields.String(),
    "total_fee":fields.Integer(),
    "installment_available":fields.String(),
    "installment_type":fields.String(),
    "no_of_installments":fields.Integer()
    })
#--------------------------------------------------------------#

#-----------------------------------------------------------#
CourseCollaboration = api.model('CourseCollaboration', {
    "course_id":fields.Integer(),
    "teacher_id":fields.Integer()
    })
#--------------------------------------------------------------#

#-----------------------------------------------------------#
Collaboration = api.model('Collaboration', {
    "Collaboration":fields.List(fields.Nested(CourseCollaboration))
    })
#--------------------------------------------------------------#


#-----------------------get-onlinetest-by-student-id-status--------------------------------#
@name_space.route("/getOnlineTestDtlsByStudentId/<int:student_id>/<string:online_status>")
class getOnlineTestDtlsByStudentId(Resource):
    def get(self,student_id,online_status):
        connection = mysql_connection()
        cursor = connection.cursor()

        cursor.execute("""SELECT DISTINCT(online_test.`Online_Test_ID`),
            online_test.`Institution_ID`, online_test.`Institution_user_ID`,`Title`, 
            `Total_Marks`, `duration`,`Description`, online_test_student_mapping.`Institution_user_ID`as 
            student_id,`status`, online_test.`Subject_id`,`subject_name`, 
            online_test.`Topic_id`,`topic_name`, `Class`, `Board`, `attendance`,`platform`, 
            online_test.`Last_update_ID`, online_test.`Last_update_TS`,`start_time`,`end_time`,`introduction_text` 
            FROM `online_test` 
            inner join `subject` on online_test.`Subject_id`= subject.`subject_id` 
            inner join `topic` on online_test.`Topic_id`= topic.`topic_id` inner join 
            `online_test_student_mapping` on online_test.`Online_Test_ID`=
            online_test_student_mapping.`Online_Test_ID` 
            LEFT JOIN `onlinetest_introduction` ino on `online_test`.`introduction_id` = ino.`introduction_id`
            WHERE  
            online_test_student_mapping.`Institution_user_ID`=%s and 
            online_test_student_mapping.`status`=%s order by 
            online_test_student_mapping.`Last_update_TS`""",(student_id,online_status))
        testdtls = cursor.fetchall()
        for j in range(len(testdtls)):
            testdtls[j]['Last_update_TS'] = testdtls[j]['Last_update_TS'].isoformat()
            if testdtls[j]['start_time'] == '0000-00-00 00:00:00':
                testdtls[j]['start_time'] = '0000-00-00 00:00:00'
            else:
                testdtls[j]['start_time'] = testdtls[j]['start_time'].isoformat()
            if testdtls[j]['end_time'] == '0000-00-00 00:00:00':
                testdtls[j]['end_time'] = '0000-00-00 00:00:00'
            else:
                testdtls[j]['end_time'] = testdtls[j]['end_time'].isoformat()
            online_test_id= testdtls[j]['Online_Test_ID']
            cursor.execute("""SELECT `Marks` FROM `online_test_student_marks` 
                WHERE `Student_ID`=%s and `Online_Test_ID`=%s
                order by `Last_Updated_TS` Desc""",(student_id,online_test_id))
            marksdtls = cursor.fetchone()
            if marksdtls == None:
                marks =0
                testdtls[j]['Marks']=0
            else:
                marks = marksdtls['Marks']
                testdtls[j]['Marks']=marksdtls['Marks']

        cursor.close() 
            
        return ({"attributes": {"status_desc": "Online Test Details",
                            "status": "success"
                                },
            "responseList":testdtls}), status.HTTP_200_OK
#-----------------------get-onlinetest-by-student-id-status--------------------------------#

#-----------------------count-onlinetest-by-student-id---------------------------------------#
@name_space.route("/countOfAttemptedNonAttemptedOnlineTestByStudentId/<int:student_id>")
class countOfAttemptedNonAttemptedOnlineTestByStudentId(Resource):
    def get(self,student_id):
        connection = mysql_connection()
        cursor = connection.cursor()

        cursor.execute("""SELECT count(DISTINCT(`online_test_id`))as total FROM 
        	`online_test_student_mapping` WHERE `Institution_user_ID`=%s and `status`='y'
        	""",(student_id))
        Attempted = cursor.fetchone()
        total_Attempted = Attempted['total']

        cursor.execute("""SELECT count(DISTINCT(`online_test_id`))as total FROM 
        	`online_test_student_mapping` WHERE `Institution_user_ID`=%s and `status`='n'
        	""",(student_id))
        nonAttempted = cursor.fetchone()
        total_nonAttempted = nonAttempted['total']

        cursor.close() 
        return ({"attributes": {"status_desc": "Online Test Details",
                            "status": "success"
                                },
            "responseList":{
         				  	"Attempted": total_Attempted,
                         	"nonAttempted" : total_nonAttempted
                         	}
                        }), status.HTTP_200_OK
#-----------------------count-onlinetest-by-student-id---------------------------------------#

#-----------------------get-Online-Test-Dtls-by-onlinetest-id-------------------------------#
@name_space.route("/getOnlineTestDtlsByOnlinetestId/<int:online_test_id>")
class getOnlineTestDtlsByOnlinetestId(Resource):
    def get(self,online_test_id):
        connection = mysql_connection()
        cursor = connection.cursor()

        cursor.execute("""SELECT distinct(otam.`assessment_id`),
            `Mapping_ID`,`online_test_id`,`Assesment_Desc`,
            q.`Question_ID`,q.`Question`,q.`Content_file_path`,q.`Content_FileName`,
            q.`File_Type_ID`,q.`marks`,q.`negative_marks`, ast.`Assessment_Type_Desc`, 
            q.`Question_Addition_TS`, q.`Last_Update_ID` FROM `question` q,`online_test_assesment_mapping`                       otam,`assessment` a,
            `assessment_question_mapping` aqm, `assessment_type` ast, `options` op
            WHERE `online_test_id` = %s and
            otam.`assessment_id`=aqm.`Assessment_ID`
            and aqm.`Assessment_ID` = a.`Assessment_ID` and
            aqm.`Question_ID`= q.`Question_ID` and q.`Question_Type` = ast.`Assessment_Type_ID` 
            and q.`Question_ID` = op.`Question_ID` GROUP by q.`Question_ID` order by otam.`assessment_id`,aqm.`Question_ID`""",
            (online_test_id))
        question_dtls = cursor.fetchall()
        if question_dtls:
            for j in range(len(question_dtls)):
                question_dtls[j]['Question_Addition_TS'] =question_dtls[j]['Question_Addition_TS'].isoformat()
                cursor.execute("""SELECT `Option_ID`, `Question_ID`, `Option`, 
                    `Option_Sequence_ID`, `Content_file_path`, `Content_FileName`, 
                    `File_Type_ID` FROM `options` WHERE 
                    `Question_ID` = %s""",(question_dtls[j]['Question_ID']))
                options = cursor.fetchall()
                # print(options)
                question_dtls[j]['options'] = options

                cursor.execute("""SELECT answer.`Question_ID`,
                    GROUP_CONCAT(answer.`Option_ID`) as Option_ID,GROUP_CONCAT(`Option`)
                    as answer FROM `answer` INNER join `options` on 
                    answer.`Option_ID`= options.`Option_ID` WHERE answer.`Question_ID`=%s""",
                    (question_dtls[j]['Question_ID']))
                answers = cursor.fetchall()
                # print(options)
                question_dtls[j]['answers'] = answers
        else:
            question_dtls = []
        cursor.close()          
        return ({"attributes": {"status_desc": "Online Test Details.",
                            "status": "success"
                            },
                            "responseList":question_dtls}), status.HTTP_200_OK      
     
#-----------------------get-Online-Test-Dtls-by-onlinetest-id-------------------------------#

#-----------------------get-history-by-online-test-id-student-id--------------------------------#
@name_space.route("/getOnlineTestDtlsByStudentIdOnlineTestId/<int:student_id>/<int:online_test_id>")
class getOnlineTestDtlsByStudentIdOnlineTestId(Resource):
    def get(self,student_id,online_test_id):
        connection = mysql_connection()
        cursor = connection.cursor()

        cursor.execute("""SELECT DISTINCT(online_test.`Online_Test_ID`),
            online_test.`Institution_ID`, online_test.`Institution_user_ID`,`Title`, 
            `Total_Marks`, `duration`,`Description`, online_test_student_mapping.`Institution_user_ID`as 
            student_id,`status`,
            online_test.`Subject_id`,`subject_name`, 
            online_test.`Topic_id`,`topic_name`, `Class`, `Board`, 
            online_test.`Last_update_ID`, online_test.`Last_update_TS` FROM `online_test` 
            inner join `subject` on online_test.`Subject_id`= subject.`subject_id` 
            inner join `topic` on online_test.`Topic_id`= topic.`topic_id` inner join 
            `online_test_student_mapping` on online_test.`Online_Test_ID`=
            online_test_student_mapping.`Online_Test_ID` WHERE 
            online_test_student_mapping.`Institution_user_ID`= %s and 
            online_test_student_mapping.`online_test_id`= %s""",
            (student_id,online_test_id))
        testdtls = cursor.fetchall()
        # print(testdtls)
        for j in range(len(testdtls)):
            testdtls[j]['Last_update_TS'] = testdtls[j]['Last_update_TS'].isoformat()
            cursor.execute("""SELECT `Institution_user_ID`,`No_Of_attempts` FROM 
                `online_test_student_mapping` WHERE `Institution_user_ID`= %s and 
                `online_test_id`= %s""",(student_id,online_test_id))
            attemptdtls = cursor.fetchall()
            # print(attemptdtls)
            testdtls[j]['No_Of_attempts']=attemptdtls
            cursor.execute("""SELECT `Student_ID`,`Marks`  FROM `online_test_student_marks` 
                WHERE `Student_ID`=%s and `Online_Test_ID`=%s""",(student_id,online_test_id))
            marksdtls = cursor.fetchall()
            testdtls[j]['Marks']=marksdtls
            
        return ({"attributes": {"status_desc": "Online Test History",
                            "status": "success"
                                },
            "responseList":testdtls}), status.HTTP_200_OK

#-------------------get-history-by-online-test-id-student-id--------------------------------#

#-------------------post-online-test-que-opt-ans--------------------------------------------#
@name_space.route("/submitOnlineTestQuetionAnswer")
class submitOnlineTestQuetionAnswer(Resource):
    @api.expect(submitqueoptansDtls)
    def post(self):
        details = request.get_json()
        connection = mysql_connection()
        cursor = connection.cursor()
        # currentDate = date.today().strftime("%d%b%y")
        
        queoptans = details['submitqueoptans']
        for que in queoptans:
            assessment_ID = que.get('Assessment_ID')
            student_ID = que.get('Student_ID')
            question_ID = que.get('Question_ID')
            option_ID = que.get('Option_ID')
            answer = que.get('Answer')
            Answersheet_filepath = que.get('answersheet_filepath')
            Filetype = que.get('filetype')
            Student_remark = que.get('student_remark')
            marks = que.get('marks')
            teacher_remark = que.get('teacher_remark')
            Last_update_id = que.get('last_update_id')

            if not Answersheet_filepath:
                Answersheet_filepath=""
            
            if not Filetype:
                Filetype=""
            
            if not Student_remark:
                Student_remark=""

            if not Last_update_id:
                Last_update_id=student_ID

            cursor.execute("""SELECT ques.`Question_Type`, ast.`Assessment_Type_Desc`, ques.`Question_ID`,
                ques.`Question`, ques.`Content_Id`, ques.`passage_id`, ques.`Content_file_path`, 
                ques.`Content_FileName`, ques.`File_Type_ID`, ques.`negative_marks`,ques.`marks`,
                GROUP_CONCAT((select op1.`option` from options op1 where op1.`option_ID` = ans.`Option_ID`) SEPARATOR '|') answer, 
                GROUP_CONCAT(ans.`Option_ID` SEPARATOR '|') as 'correct_optionId', GROUP_CONCAT(ans.`Additional_Text` SEPARATOR '|') as 'Additional_Text'
                FROM `question` ques, `answer` ans, `options` op, 
                `assessment_type` ast WHERE ques.`Question_ID` = ans.`Question_ID` 
                AND ans.`Option_ID` = op.`Option_ID`  AND ast.`Assessment_Type_ID` = ques.`Question_Type` 
                AND ques.`Question_ID` = %s""",(question_ID))

            correctAnsDtls = cursor.fetchone()
            question_type = correctAnsDtls.get('Assessment_Type_Desc')

            if question_type == 'MSQ':
                if option_ID:
                    studentAns = option_ID.split(',')
                    correctAns = correctAnsDtls.get('correct_optionId').split('|')
                    if collections.Counter(studentAns) == collections.Counter(correctAns):
                        # print(correctAns,studentAns)
                        marks = correctAnsDtls.get('marks')
                    else:
                        marks = correctAnsDtls.get('negative_marks')
                # else:
                #     marks = correctAnsDtls.get('negative_marks')

            student_ans_query = ("""INSERT INTO `student_answers`(`Assessment_ID`, 
                `Student_ID`, `Question_ID`, `Option_ID`, `Answer`, `answersheet_filepath`,
                `filetype`, `student_remark`, `marks`, `teacher_remark`,`last_update_id`) 
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
            student_ans_data = (assessment_ID,student_ID,question_ID,
                option_ID,answer,Answersheet_filepath, 
                Filetype,Student_remark,marks,teacher_remark,Last_update_id)

            submitdata = cursor.execute(student_ans_query,student_ans_data)

            
            connection.commit()


            
        if submitdata:
            return ({"attributes": {"status_desc": "Student Answer Submitted",
                                "status": "success"
                                }
                 }), status.HTTP_200_OK
        else:
            return ({"attributes": {"status_desc": "Student Answer Submitted",
                                "status": "not success"
                                }
                 }), status.HTTP_200_OK

#-------------------post-online-test-que-opt-ans--------------------------------------------#

#-------------------post-online-test-student-marks--------------------------------------------#
@name_space.route("/submitOnlineTestStudentMarks")
class submitOnlineTestStudentMarks(Resource):
    @api.expect(submitmarksDtls)
    def post(self):
        details = request.get_json()
        connection = mysql_connection()
        cursor = connection.cursor()
        # currentDate = date.today().strftime("%d%b%y")
        
        marks = details['submitmarks']
        for mar in marks:
            online_Test_ID = mar.get('Online_Test_ID')
            student_ID = mar.get('Student_ID')
            marks = mar.get('Marks')
            last_Updated_ID = mar.get('Last_Updated_ID')

            if not last_Updated_ID:
                last_Updated_ID = student_ID


            student_marks_query = ("""INSERT INTO `online_test_student_marks`(`Online_Test_ID`,
             `Student_ID`, `Marks`, `Last_Updated_ID`) VALUES (%s,%s,%s,%s)""")
            student_marks_data = (online_Test_ID,student_ID,marks,last_Updated_ID)

            marksdata = cursor.execute(student_marks_query,student_marks_data)

            updateStudentStatus = ("""UPDATE `online_test_student_mapping` SET `status` = %s WHERE 
                `online_test_id` = %s AND `Institution_user_ID` = %s""")
            statusData = ('y',online_Test_ID,student_ID)
            cursor.execute(updateStudentStatus,statusData)

            connection.commit()
            
        if marksdata:
            return ({"attributes": {"status_desc": "Student Answer Submitted",
                                "status": "success"
                                }
                 }), status.HTTP_200_OK
        else:
            return ({"attributes": {"status_desc": "Student Marks Submitted",
                                "status": "not success"
                                }
                 }), status.HTTP_200_OK

#-------------------post-online-test-student-marks--------------------------------------------#

#-------------------post-online-assessment-student-marks------------------------------------#
@name_space.route("/submitOnlineAssessmentStudentMarks")
class submitOnlineAssessmentStudentMarks(Resource):
    @api.expect(submitassmarksDtls)
    def post(self):
        details = request.get_json()
        connection = mysql_connection()
        cursor = connection.cursor()
        # currentDate = date.today().strftime("%d%b%y")
        
        assmarks = details.get('submitassmarks')
        if assmarks:
            for ass in assmarks:
                online_Test_ID = ass.get('Online_Test_ID')
                online_assesment_ID = ass.get('Online_assesment_ID')
                student_ID = ass.get('Student_ID')
                marks = ass.get('Marks')
                last_Updated_ID = ass.get('Last_Updated_ID')

                if not last_Updated_ID:
                    last_Updated_ID =student_ID


                ass_marks_query = ("""INSERT INTO `online_assesment_student_marks`(
                    `Online_Test_ID`, `Online_assesment_ID`,`Student_ID`, `Marks`, `Last_Updated_ID`) 
                    VALUES (%s,%s,%s,%s,%s)""")
                ass_marks_data = (online_Test_ID,online_assesment_ID,student_ID,marks,last_Updated_ID)

                assmarksdata = cursor.execute(ass_marks_query,ass_marks_data)
                connection.commit()
            
        return ({"attributes": {"status_desc": "Student Assessment Marks Submitted",
                            "status": "success"}}), status.HTTP_200_OK

#-------------------post-online-assessment-student-marks------------------------------------#

#--------------------------------student-online-test------------------------------------#
def submitmarks(details):
    connection = mysql_connection()
    cursor = connection.cursor()
    
    # mark = details
    # print(mark)
    post_url_marks = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/online_test/OnlineTest/submitOnlineTestStudentMarks'
    payload_marks = json.dumps(details)
    headers_marks = {'Content-type':'application/json', 'Accept':'application/json'}
    marks_response = requests.post(post_url_marks, data=payload_marks, headers=headers_marks)
    r = marks_response.json()
    res = r['attributes']['status_desc']
    # print(res)
    
    # assmark = details

    post_url_ass = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/online_test/OnlineTest/submitOnlineAssessmentStudentMarks'
    payload_ass = json.dumps(details)
    headers_ass = {'Content-type':'application/json', 'Accept':'application/json'}
    ass_response = requests.post(post_url_ass, data=payload_ass, headers=headers_ass)
    
    cursor.close()
    return 'success'

    
class Compute(Thread):
    def __init__(self, request, funcname):
        Thread.__init__(self)
        self.request = request
        self.funcname = funcname

    def run(self):
        time.sleep(5)
        if self.funcname == 'SubmitOnlineTest':
            details = self.request
            submitmarks(details)
        else:
            pass 

@name_space.route("/SubmitOnlineTest")
class SubmitOnlineTest(Resource):
    @api.expect(submitonlinetest)
    def post(self):
        connection = mysql_connection()
        cursor = connection.cursor()
        details = request.get_json()
        
        # queopt = details
        # print(queoptans)
        post_url_answer = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/online_test/OnlineTest/submitOnlineTestQuetionAnswer'
        payload_answer = json.dumps(details)
        headers_answer = {'Content-type':'application/json', 'Accept':'application/json'}
        ans_response = requests.post(post_url_answer, data=payload_answer, headers=headers_answer)
        r = ans_response.json()
        res = r['attributes']['status_desc']
        cursor.close()
        # submitmarks(details)

        sendrReq = (details)
        thread_a = Compute(sendrReq,'SubmitOnlineTest')
        thread_a.start()

        return ({"attributes": {"status_desc": "Online Test Submitted",
                                    "status": "success"
                                    },
                    "responseList": res}), status.HTTP_200_OK

#--------------------------------student-online-test------------------------------------#

#-----------------------------------------------------------------------------------------#
@name_space.route("/getPaidOnlineTestDtlsByInstitutionIdTeacherId/<int:instituiton_id>/<int:teacher_id>")
class getPaidOnlineTestDtlsByInstitutionIdTeacherId(Resource):
    def get(self,instituiton_id,teacher_id):
        connection = mysql_connection()
        cursor = connection.cursor()

        cursor.execute("""SELECT onlinetest_fee_mapping.`Online_Test_ID`,`Institution_user_ID`,
            `fee_id`,`subject_name`,`topic_name`,`Title`,`duration`,`Description`,
            `Total_Marks`,online_test.`Subject_id`,online_test.`Topic_id`,
            `is_paid_course`,`total_fee`,`installment_available`,`installment_type`,
            onlinetest_fee_mapping.`last_update_ts` FROM `online_test` inner join 
            `onlinetest_fee_mapping` on `online_test`.`Online_Test_ID`=
            `onlinetest_fee_mapping`.`Online_Test_ID`  inner join `subject` on 
            online_test.`Subject_id`= subject.`subject_id` 
            inner join `topic` on online_test.`Topic_id`= topic.`topic_id` 
            WHERE online_test.`Institution_ID`=%s and `Institution_user_ID`=%s""",
            (instituiton_id,teacher_id))
        onlinetestfeedtls = cursor.fetchall()
        
        for j in range(len(onlinetestfeedtls)):
            onlinetestfeedtls[j]['last_update_ts'] = onlinetestfeedtls[j]['last_update_ts'].isoformat()
        
        cursor.close()    
        return ({"attributes": {"status_desc": "Paid Online Test Details",
                            "status": "success"
                                },
            "responseList":onlinetestfeedtls}), status.HTTP_200_OK

#------------------------------------------------------------------------------------------#

#------------------------------------------------------------------------------------------#
@name_space.route("/CreateOnlineTestFees")
class CreateOnlineTestFees(Resource):
    @api.expect(onlinetestFeeMapping)
    def post(self):
        details = request.get_json()
        connection = mysql_connection()
        cursor = connection.cursor()
        
        Online_Test_ID = details['Online_Test_ID']
        is_paid_course = details['is_paid_course']
        total_fee = details['total_fee']
        installment_available = details['installment_available']
        installment_type = details['installment_type']
        no_of_installments = details['no_of_installments']

        onlinetestfee_query = ("""INSERT INTO `onlinetest_fee_mapping`(`Online_Test_ID`,
            `is_paid_course`, `total_fee`, `installment_available`, `installment_type`,
            `no_of_installments`) VALUES (%s,%s,%s,%s,%s,%s)""")
        onlinetestfee_data = (Online_Test_ID,is_paid_course,total_fee,installment_available,
            installment_type,no_of_installments)

        onlinetestfeedata = cursor.execute(onlinetestfee_query,onlinetestfee_data)
        OnlinetestfeeId = cursor.lastrowid
        details['OnlinetestfeeId'] = OnlinetestfeeId

        connection.commit()
        cursor.close()

        return ({"attributes": {"status_desc": "Onlinetest Fee Submitted",
                                "status": "success"
                                },
                    "responseList":details}), status.HTTP_200_OK

#------------------------------------------------------------------------------------------#

#-----------------------------------------------------------------------#
@name_space.route("/updateOnlineTestFeesByFeeID/<int:fee_id>")
class updateOnlineTestFeesByFeeID(Resource):
    @api.expect(upadateonlinetestFees)
    def put(self,fee_id):
        details = request.get_json()
        connection = mysql_connection()
        cursor = connection.cursor()
        
        Is_paid_course = details.get('is_paid_course')
        Total_fee = details.get('total_fee')
        Installment_available = details.get('installment_available')
        Installment_type = details.get('installment_type')
        No_of_installments = details.get('no_of_installments')
        

        cursor.execute("""SELECT `is_paid_course`,`total_fee`,`installment_available`,
            `installment_type`,`no_of_installments` FROM `onlinetest_fee_mapping` WHERE 
            `fee_id`=%s""",(fee_id))
        student_docdtls = cursor.fetchone()
        # print(student_docdtls)

        if student_docdtls:
            if not Is_paid_course:
                Is_paid_course = student_docdtls.get('is_paid_course')
                
            if not Total_fee:
                Total_fee = student_docdtls.get('total_fee')
                
            if not Installment_available:
                Installment_available = student_docdtls.get('installment_available')
                
            if not Installment_type:
                Installment_type = student_docdtls.get('installment_type')
                
            if not No_of_installments:
                No_of_installments = student_docdtls.get('no_of_installments')
                

        update_onlinetestfee = ("""UPDATE `onlinetest_fee_mapping` SET `is_paid_course`=%s ,
            `total_fee`=%s,`installment_available`=%s,`installment_type`=%s,
            `no_of_installments`=%s WHERE `fee_id`=%s""")
        onlinetestfee_data = (Is_paid_course,Total_fee,Installment_available,
           Installment_type,No_of_installments,fee_id)
        cursor.execute(update_onlinetestfee,onlinetestfee_data)
        cursor.close()

        return ({"attributes": {"status_desc": "Online Test Fees Details Updated",
                            "status": "success"
                            },
                            "responseList":details}), status.HTTP_200_OK

#--------------------------------------------------------------------------------------#

#----------------------------------------------------------------------------#

@name_space.route("/OnlinTestFeesDelete/<int:fee_id>")
class courseFeesDelete(Resource):
    def delete(self, fee_id):
        connection = mysql_connection()
        cursor = connection.cursor()
        
        onlinetest_fees_delete_query = ("""DELETE FROM `onlinetest_fee_mapping` WHERE `fee_id`= %s""")
        delData = (fee_id)
        
        cursor.execute(onlinetest_fees_delete_query,delData)
        connection.commit()
        cursor.close()
        
        return ({"attributes": {"status_desc": "Delete Online Test Fees Details",
                                "status": "success"},
                "responseList": 'Deleted Successfully'}), status.HTTP_200_OK


#-------------------------------------------------------------------------------#

#------------------------------------------------------------------------------------------#
@name_space.route("/CourseCollaboration")
class CourseCollaboration(Resource):
    @api.expect(Collaboration)
    def post(self):
        details = request.get_json()
        connection = mysql_connection()
        cursor = connection.cursor()
        
        Collaboration = details['Collaboration']
        collaboration = Collaboration

        for col in collaboration:
            course_id = col['course_id']
            teacher_id = col['teacher_id']

            course_collaboration_query = ("""INSERT INTO `course_collaboration`(`course_id`, `teacher_id`) 
             VALUES (%s,%s)""")
            course_collaboration_data = (course_id,teacher_id)

            course_collaborationdata = cursor.execute(course_collaboration_query,course_collaboration_data)
            
        connection.commit()
        cursor.close()

        return ({"attributes": {"status_desc": "Course Collaboration Data Submitted",
                                "status": "success"
                                },
                    "responseList":details}), status.HTTP_200_OK

#------------------------------------------------------------------------------------------#

#------------------------------------------------------------------------------------------#

@name_space.route("/DeleteCourseCollaboration/<int:collaboration_id>")
class DeleteCourseCollaboration(Resource):
    def delete(self,collaboration_id):
        connection = mysql_connection()
        cursor = connection.cursor()
        
        collaboration_delete_query = ("""DELETE FROM `course_collaboration` WHERE 
            `collaboration_id`=%s""")
        delData = (collaboration_id)
        
        cursor.execute(collaboration_delete_query,delData)
        connection.commit()
        cursor.close()
        
        return ({"attributes": {"status_desc": "Delete Collaboration Details",
                                "status": "success"},
                "responseList": 'Deleted Successfully'}), status.HTTP_200_OK
#------------------------------------------------------------------------------------------#

#-----------------------------------------------------------------------------------------#
@name_space.route("/getPaidOnlineTestDtlsByInstitutionIdStudentId/<int:student_id>/<string:online_status>")
class getPaidOnlineTestDtlsByInstitutionIdTeacherId(Resource):
    def get(self,student_id,online_status):
        connection = mysql_connection()
        cursor = connection.cursor()
        availableOnlinetestdtls = []
        assignedOnlinetestdtls = []
        institution_id = None
        cursor.execute("""SELECT DISTINCT(online_test.`Online_Test_ID`),
            online_test_student_mapping.`Institution_user_ID`, `subject_name`,`topic_name`,
            `Title`,`Description`,`Total_Marks`,online_test.`Institution_ID`,`Class`,`Board`,
            `duration`,`status`, online_test.`Subject_id`,
            online_test.`Topic_id`, online_test.`last_update_ts` FROM `online_test` 
            INNER JOIN `online_test_student_mapping` on online_test.`Online_Test_ID`= 
            `online_test_student_mapping`.`online_test_id` inner join `subject` on 
            online_test.`Subject_id`= subject.`subject_id` inner join `topic` on 
            online_test.`Topic_id`= topic.`topic_id` WHERE 
            online_test_student_mapping.`Institution_user_ID`=%s and `status`=%s""",
            (student_id,online_status))
        assignedOnlinetestdtls = cursor.fetchall()
        
        for j in range(len(assignedOnlinetestdtls)):
            assignedOnlinetestdtls[j]['last_update_ts'] = assignedOnlinetestdtls[j]['last_update_ts'].isoformat()
            institution_id = assignedOnlinetestdtls[0]['Institution_ID']
        if institution_id:
            cursor.execute("""SELECT DISTINCT(online_test.`Online_Test_ID`),
                online_test.`Institution_user_ID`,`fee_id`,`subject_name`,`topic_name`,`Title`,
                `Description`,`Total_Marks`,online_test.`Institution_ID`,`Class`,`Board`,
                `duration`,online_test.`Subject_id`,online_test.`Topic_id`,`is_paid_course`,
                `total_fee`,`installment_available`,`installment_type`,`no_of_installments`,
                online_test.`last_update_ts` FROM `online_test` INNER join `subject` on 
                online_test.`Subject_id`= subject.`subject_id` INNER join `topic` on 
                online_test.`Topic_id`= topic.`topic_id` INNER JOIN `online_test_student_mapping` 
                on online_test.`Online_Test_ID`= `online_test_student_mapping`.`online_test_id` 
                left join `onlinetest_fee_mapping` on `online_test`.`Online_Test_ID`=
                `onlinetest_fee_mapping`.`Online_Test_ID` where 
                online_test.`Online_Test_ID` not in(SELECT `online_test_id` FROM 
                `online_test_student_mapping` where `Institution_user_ID`=%s) and 
                online_test.`Institution_ID`=%s""",(student_id,institution_id))
            availableOnlinetestdtls = cursor.fetchall()
        
        if availableOnlinetestdtls:
        
            for j in range(len(availableOnlinetestdtls)):
                availableOnlinetestdtls[j]['last_update_ts'] = availableOnlinetestdtls[j]['last_update_ts'].isoformat()
                if availableOnlinetestdtls[j]['is_paid_course'] ==None:
                    availableOnlinetestdtls[j]['is_paid_course'] ='n'
                if availableOnlinetestdtls[j]['total_fee'] ==None:
                    availableOnlinetestdtls[j]['total_fee'] =0
                if availableOnlinetestdtls[j]['installment_available'] ==None:
                    availableOnlinetestdtls[j]['installment_available'] =''
                if availableOnlinetestdtls[j]['installment_type'] ==None:
                    availableOnlinetestdtls[j]['installment_type'] =""
                if availableOnlinetestdtls[j]['no_of_installments'] ==None:
                    availableOnlinetestdtls[j]['no_of_installments'] = 0
                else:
                    availableOnlinetestdtls[j]['is_paid_course'] = availableOnlinetestdtls[j]['is_paid_course']
                    availableOnlinetestdtls[j]['total_fee'] = availableOnlinetestdtls[j]['total_fee']
                    availableOnlinetestdtls[j]['installment_available'] = availableOnlinetestdtls[j]['installment_available']
                    availableOnlinetestdtls[j]['installment_type'] = availableOnlinetestdtls[j]['installment_type']
                    availableOnlinetestdtls[j]['no_of_installments'] = availableOnlinetestdtls[j]['no_of_installments']
        totalOnlineTest =len(availableOnlinetestdtls)
        totalAssigned = len(assignedOnlinetestdtls)
        
        OnlineTestdtls = {
                            "assignedOnlineTest":assignedOnlinetestdtls,
                            "availableOnlineTest":availableOnlinetestdtls
                        }

        return ({"attributes": {"status_desc": "Student OnlineTest Details",
                                "status": "success",
                                "total_OnlinetTest_available":totalOnlineTest,
                                "total_OnlinetTest_assigned":totalAssigned},
                "responseList": OnlineTestdtls}), status.HTTP_200_OK


#---------------------------------------------------------------------------------------#

#---------------------------------------------------------------------------------------#
@name_space.route("/getCourseCollaboratorsDtlsByCourseId/<int:course_id>")
class getCourseCollaboratorsDtlsByCourseId(Resource):
    def get(self,course_id):
        connection = mysql_connection()
        cursor = connection.cursor()

        conn = logindb_connection()
        cur = conn.cursor()

        cursor.execute("""SELECT `course_id`,`institution_id`,`course_title`,
            `course_description`,`course_image`,`course_filetype`,`teacher_id` 
            FROM `instituition_course_master` WHERE `course_id`=%s""",(course_id))
        collaborationdtls = cursor.fetchone()

        cursor.execute("""SELECT `collaboration_id`,`course_id`,`teacher_id` FROM 
            `course_collaboration` WHERE `course_id`=%s""",(course_id))
        collaboratorsdtls = cursor.fetchall()

        collaborationdtls['collaboratorsdtls'] = collaboratorsdtls
        for i in range(len(collaboratorsdtls)):
            teacher_id = collaboratorsdtls[i]['teacher_id']
            
            cur.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`)as 'name' 
                FROM `institution_user_credential` WHERE 
                `INSTITUTION_USER_ID`=%s""",(teacher_id))
            teacherdtls = cur.fetchone()
            collaborator_name = teacherdtls['name']
            collaboratorsdtls[i]['collaborator_name'] = collaborator_name

        cur.close() 
        cursor.close() 
            
        return ({"attributes": {"status_desc": "Collaborators Details",
                            "status": "success"
                                },
            "responseList":collaborationdtls}), status.HTTP_200_OK
            
#---------------------------------------------------------------------------------------#
