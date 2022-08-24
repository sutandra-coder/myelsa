from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests

app = Flask(__name__)
cors = CORS(app)

#----------------------database-connection---------------------#
def mysql_connection():
    connection = pymysql.connect(host='creamsonservices.com',
                                user='creamson_langlab',
                                password='Langlab@123',
                                db='creamson_logindb',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
    return connection

def b2b_connection():
    connection = pymysql.connect(host='creamsonservices.com',
                                user='creamson_langlab',
                                password='Langlab@123',
                                db='creamson_lab_lang1',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
    return connection

def library_connection():
    connection = pymysql.connect(host='creamsonservices.com',
                                 user='creamson_langlab',
                                 password='Langlab@123',
                                 db='creamson_user_library',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection
    
#----------------------database-connection---------------------#

engagement_portal = Blueprint('engagement_portal_api', __name__)
api = Api(engagement_portal,  title='MyElsa API',
          description='MyElsa API')
name_space = api.namespace('EngagementPortal',
                           description='Engagement Portal')

#----------------------total count----------------------#
@name_space.route("/registrationDetails")
class registrationDetails(Resource):
    def get(self):
        connection = mysql_connection()
        cursor = connection.cursor()

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID`) as `total` FROM 
            `institution_user_credential`""")
        total_reg = cursor.fetchone()
        count_reg = total_reg['total']
        # print(total)

        cursor.execute("""SELECT count(INSTITUTION_USER_ID) as total FROM `institution_user_credential_master` 
                WHERE `INSTITUTION_USER_ID` in(SELECT `INSTITUTION_USER_ID` FROM `institution_user_credential`) and `INSTITUTION_USER_ROLE`='TA'""")

        total_teacher = cursor.fetchone()
        count_tea = total_teacher['total']

        cursor.execute("""SELECT count(INSTITUTION_USER_ID) as total FROM `institution_user_credential_master` 
                WHERE `INSTITUTION_USER_ID` in(SELECT `INSTITUTION_USER_ID` FROM `institution_user_credential`) 
                and `INSTITUTION_USER_ROLE`='S1'""")

        total_student = cursor.fetchone()
        count_stu = total_student['total']

        cursor.execute("""SELECT count(INSTITUTION_USER_ID) as total FROM 
            `institution_user_credential_master` WHERE `INSTITUTION_USER_ID` in
            (SELECT `INSTITUTION_USER_ID` FROM `institution_user_credential`) and 
            `INSTITUTION_USER_ROLE`='G1'""")
        total_parent = cursor.fetchone()
        count_par = total_parent['total']

        cursor.execute("""SELECT count(`INSTITUTION_ID`)as total FROM `institution_dtls`""")
        total_ins = cursor.fetchone()
        count_ins = total_ins['total']

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID_TEACHER`) as total FROM `teacher_dtls` 
            WHERE `INSTITUTION_USER_ID_TEACHER` in(SELECT `INSTITUTION_USER_ID` FROM 
            `institution_user_credential` where date(`LAST_UPDATE_TIMESTAMP`)=CURdate())""")

        currentdate_tea = cursor.fetchone()
        curr_count_tea = currentdate_tea['total']

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID_STUDENT`)as total FROM 
            `student_dtls` WHERE `INSTITUTION_USER_ID_STUDENT` in(SELECT 
            `INSTITUTION_USER_ID` FROM `institution_user_credential` where 
            date(`LAST_UPDATE_TIMESTAMP`)=CURdate())""")

        currentdate_stu = cursor.fetchone()
        curr_count_stu = currentdate_stu['total']

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID`)as total FROM 
            `institution_user_credential_master` WHERE `INSTITUTION_USER_ID` in(SELECT 
            `INSTITUTION_USER_ID` FROM `institution_user_credential` where 
            date(`LAST_UPDATE_TIMESTAMP`)=CURdate()) and `INSTITUTION_USER_ROLE`='G1'""")

        currentdate_par = cursor.fetchone()
        curr_count_par = currentdate_par['total']

        cursor.execute("""SELECT count(`INSTITUTION_ID`)as total FROM `institution_dtls` 
            where date(`LAST_UPDATE_TIMESTAMP`)=CURdate()""")

        currentdate_ins = cursor.fetchone()
        curr_count_ins = currentdate_ins['total']

        return ({"attributes": {"status_desc": "Registration Details.",
                                "status": "success"
                                },
                "responseList": {
                                   "total_registration": count_reg,
                                  
                                   "total_teachers": count_tea,

                                   "total_students": count_stu,

                                   "total_parents": count_par,

                                   "total_instituitions": count_ins,

                                   "todays_teachers": curr_count_tea,

                                   "todays_students": curr_count_stu,

                                   "todays_parents": curr_count_par,

                                   "todays_instituitions": curr_count_ins
                                  },
                }), status.HTTP_200_OK

#---------------------------------total count--------------------------------------------#

#---------------------------------regtration-dtls-by-date--------------------------------------------#

@name_space.route("/registrationDtlsByDate/<string:Start_date>/<string:End_date>/<string:User_role>")
class registration_dtls(Resource):
    def get(self,Start_date,End_date,User_role):
        connection = mysql_connection()
        cursor = connection.cursor()

        if User_role =='S1':
            cursor.execute("""SELECT institution_dtls.`Institution_ID`, institution_dtls.
                    `INSTITUTION_NAME`,`INSTITUTION_USER_ROLE`,institution_user_credential.`INSTITUTION_USER_ID`,
                    concat(`FIRST_NAME`,' ',`LAST_NAME`) 
                    as name,`INSTITUTION_USER_NAME`, `INSTITUTION_USER_PASSWORD`,
                    `PRIMARY_CONTACT_NUMBER`,institution_user_credential.`IMAGE_URL`, 
                    institution_user_credential_master.`INSTITUTION_NAME` as school_name,`CLASS`,`Board`,
                    `institution_user_credential`.`LAST_UPDATE_TIMESTAMP`
                FROM `institution_user_credential` inner join 
                `institution_user_credential_master` on institution_user_credential.
                `INSTITUTION_USER_ID`=institution_user_credential_master.`INSTITUTION_USER_ID` 
                INNER JOIN `institution_dtls` on institution_user_credential_master.`INSTITUTION_ID`
                     =institution_dtls.`INSTITUTION_ID` INNER join `student_dtls` on 
                     institution_user_credential.`INSTITUTION_USER_ID`=student_dtls.
                     `INSTITUTION_USER_ID_STUDENT`
                where date(institution_user_credential.`LAST_UPDATE_TIMESTAMP`) 
                between %s and %s and `INSTITUTION_USER_ROLE`= %s""", 
                (Start_date,End_date,User_role))


            regdtlsbydate = cursor.fetchall()
            for i in range(len(regdtlsbydate)):
                regdtlsbydate[i]['LAST_UPDATE_TIMESTAMP'] = regdtlsbydate[i]['LAST_UPDATE_TIMESTAMP'].isoformat()
        else:
            cursor.execute("""SELECT institution_dtls.`Institution_ID`, institution_dtls.
                    `INSTITUTION_NAME`,`INSTITUTION_USER_ROLE`,institution_user_credential.`INSTITUTION_USER_ID`,
                    concat(`FIRST_NAME`,' ',`LAST_NAME`) 
                    as name,`INSTITUTION_USER_NAME`, `INSTITUTION_USER_PASSWORD`,
                    `PRIMARY_CONTACT_NUMBER`,institution_user_credential.`IMAGE_URL`, 
                    institution_user_credential_master.`INSTITUTION_NAME` as school_name,
                    `institution_user_credential`.`LAST_UPDATE_TIMESTAMP`
                FROM `institution_user_credential` inner join 
                `institution_user_credential_master` on institution_user_credential.
                `INSTITUTION_USER_ID`=institution_user_credential_master.`INSTITUTION_USER_ID` 
                INNER JOIN `institution_dtls` on institution_user_credential_master.`INSTITUTION_ID`
                     =institution_dtls.`INSTITUTION_ID` 
                where date(institution_user_credential.`LAST_UPDATE_TIMESTAMP`) 
                between %s and %s and `INSTITUTION_USER_ROLE`= %s""", 
                (Start_date,End_date,User_role))


            regdtlsbydate = cursor.fetchall()
            for i in range(len(regdtlsbydate)):
                regdtlsbydate[i]['LAST_UPDATE_TIMESTAMP'] = regdtlsbydate[i]['LAST_UPDATE_TIMESTAMP'].isoformat()
        
        return ({"attributes": {"status_desc": "user Details",
                                "status": "success"
                                },
                 "responseList": regdtlsbydate
                }), status.HTTP_200_OK

#---------------------------------regtration-dtls-by-date--------------------------------------------#

#---------------------------------User-Details-by-instituionuserid--------------------------------------------#

@name_space.route("/userUsageDtlsByuserid/<int:Userid>/<string:User_role>")
class userUsageDtlsByuserid(Resource):
    def get(self,Userid,User_role):
        connection = mysql_connection()
        cursor = connection.cursor()
        
        if User_role =='S1':
            cursor.execute("""SELECT institution_dtls.`Institution_ID`, institution_dtls.
                `INSTITUTION_NAME`,`INSTITUTION_USER_ROLE`,concat(`FIRST_NAME`,' ',`LAST_NAME`) 
                as name,`INSTITUTION_USER_NAME`, `INSTITUTION_USER_PASSWORD`,
                `PRIMARY_CONTACT_NUMBER`,institution_user_credential.`IMAGE_URL`, 
                institution_user_credential_master.`INSTITUTION_NAME` as school_name,`CLASS`,`Board`,
                `institution_user_credential`.`LAST_UPDATE_TIMESTAMP` FROM 
                `institution_user_credential` inner join `institution_user_credential_master` 
                on institution_user_credential.`INSTITUTION_USER_ID`=
                institution_user_credential_master.`INSTITUTION_USER_ID` 
                INNER JOIN `institution_dtls` on institution_user_credential_master.`INSTITUTION_ID`
                 =institution_dtls.`INSTITUTION_ID` INNER join `student_dtls` on 
                 institution_user_credential.`INSTITUTION_USER_ID`=student_dtls.
                 `INSTITUTION_USER_ID_STUDENT` where institution_user_credential.
                 `INSTITUTION_USER_ID`=%s and `INSTITUTION_USER_ROLE`=%s""", (Userid,User_role))


            regdtlsbyUserid = cursor.fetchall()
            for i in range(len(regdtlsbyUserid)):
                regdtlsbyUserid[i]['LAST_UPDATE_TIMESTAMP'] = regdtlsbyUserid[i]['LAST_UPDATE_TIMESTAMP'].isoformat()
        else:
            cursor.execute("""SELECT institution_dtls.`Institution_ID`, institution_dtls.
                    `INSTITUTION_NAME`,(SELECT count(`INSTITUTION_USER_ID`) FROM 
                    `institution_user_credential_master` WHERE 
                    institution_user_credential_master.`INSTITUTION_ID` =
                    institution_dtls.`INSTITUTION_ID` and `INSTITUTION_USER_ROLE`='S1')as 
                    total_student,`INSTITUTION_USER_ROLE`,concat(`FIRST_NAME`,' ',`LAST_NAME`) 
                    as name,`INSTITUTION_USER_NAME`, `INSTITUTION_USER_PASSWORD`,
                    `PRIMARY_CONTACT_NUMBER`,institution_user_credential.`IMAGE_URL`, 
                    institution_user_credential_master.`INSTITUTION_NAME`,
                    `institution_user_credential`.`LAST_UPDATE_TIMESTAMP` FROM 
                    `institution_user_credential` inner join `institution_user_credential_master`
                     on institution_user_credential. `INSTITUTION_USER_ID`=
                     institution_user_credential_master.`INSTITUTION_USER_ID` INNER JOIN 
                     `institution_dtls` on institution_user_credential_master.`INSTITUTION_ID` =
                     institution_dtls.`INSTITUTION_ID` where institution_user_credential.
                     `INSTITUTION_USER_ID`=%s and `INSTITUTION_USER_ROLE`=%s""",(Userid,User_role))

            regdtlsbyUserid = cursor.fetchall()
            for i in range(len(regdtlsbyUserid)):
                regdtlsbyUserid[i]['LAST_UPDATE_TIMESTAMP'] = regdtlsbyUserid[i]['LAST_UPDATE_TIMESTAMP'].isoformat()

        return ({"attributes": {"status_desc": "user Details",
                                "status": "success"
                                },
                 "responseList": regdtlsbyUserid
                }), status.HTTP_200_OK

#---------------------------------User-Details-by-instituionuserid--------------------------------------------#

#---------------------------------Uer-TrackingDetails-by-instituionuserid---------------------------------------#

@name_space.route("/7DaysTrackingDtlsByuserid/<int:Userid>")
class userTrackingDtlsByuserid(Resource):
    def get(self,Userid):
        connection = mysql_connection()
        cursor = connection.cursor()
        
        cursor.execute("""SELECT
              *,LENGTH(Track_day) - LENGTH(REPLACE(Track_day, ',', '')) +1 AS COUNT_OF_days
            FROM (SELECT institution_user_tracking.`institution_user_id`,GROUP_CONCAT(
            DISTINCT(date(institution_user_tracking.`last_update_ts`))) AS Track_day FROM 
            `institution_user_tracking`  WHERE date(`start_time`) between 
            DATE(NOW()) + INTERVAL -7 DAY and DATE(NOW()) and 
            institution_user_tracking.`institution_user_id`=%s GROUP BY
            institution_user_tracking.`institution_user_id` ORDER BY 
            (DAY(institution_user_tracking.`last_update_ts`)) ASC) AS cnt2
            HAVING COUNT_OF_days > 0""",(Userid))
        track7dtls = cursor.fetchall()

        return ({"attributes": {"status_desc": "Tracking Details",
                                "status": "success"
                                },
                 "responseList": track7dtls
                }), status.HTTP_200_OK

#---------------------------------Uer-TrackingDetails-by-instituionuserid-----------------------------------------#

#---------------------------------Uer-TrackingDetails-by-instituionuserid---------------------------------------#

@name_space.route("/30DaysTrackingDtlsByuserid/<int:Userid>")
class userTrackingDtlsByuserid(Resource):
    def get(self,Userid):
        connection = mysql_connection()
        cursor = connection.cursor()
        
        cursor.execute("""SELECT
              *,LENGTH(Track_day) - LENGTH(REPLACE(Track_day, ',', '')) +1 AS COUNT_OF_days
            FROM (SELECT institution_user_tracking.`institution_user_id`,GROUP_CONCAT(
            DISTINCT(date(institution_user_tracking.`last_update_ts`))) AS Track_day FROM 
            `institution_user_tracking`  WHERE date(`start_time`) between 
            DATE(NOW()) + INTERVAL -30 DAY and DATE(NOW()) and 
            institution_user_tracking.`institution_user_id`=%s GROUP BY
            institution_user_tracking.`institution_user_id` ORDER BY 
            (DAY(institution_user_tracking.`last_update_ts`)) ASC) AS cnt2
            HAVING COUNT_OF_days > 0""",(Userid))
        track30dtls = cursor.fetchall()

        return ({"attributes": {"status_desc": "Tracking Details",
                                "status": "success"
                                },
                 "responseList": track30dtls
                }), status.HTTP_200_OK

#---------------------------------Uer-TrackingDetails-by-instituionuserid-----------------------------------------#

#---------------------------------User-UsageDetails-by-instituionuserid-----------------------------------------#

@name_space.route("/UsageDtlsByuserid/<int:Userid>/<string:User_role>")
class UsageDtlsByuserid(Resource):
    def get(self,Userid,User_role):
        connection = mysql_connection()
        cursor = connection.cursor()
        
        nextconnection = b2b_connection()
        nextcursor = nextconnection.cursor()

        libconnection =library_connection()
        libcursor = libconnection.cursor()

        if User_role == 'S1':
            cursor.execute("""SELECT Total_earned_Coins as total FROM 
                rewards_profile WHERE INSTITUTION_USER_ID=%s""",(Userid))
            earnedConins = cursor.fetchone()
            print(earnedConins)
            if earnedConins != None:
                countConins = earnedConins['total']
                print(countConins)
            else:
                countConins =0

            cursor.execute("""SELECT Medel FROM rewards_profile WHERE INSTITUTION_USER_ID=%s
                """,(Userid))
            earnedMedel = cursor.fetchone()
            if earnedMedel !=None:
                countMedel = earnedMedel['Medel']
                print(countMedel)
            else:
                countMedel =0
            

            cursor.execute("""SELECT count(`Student_ID`)as total FROM `student_contest_tracking` 
                WHERE `Student_ID`=%s""",(Userid))
            total_contest = cursor.fetchone()
            if total_contest !=None:
                count_contest = total_contest['total']
                print(count_contest)
            else:
                count_contest =0
            

            cursor.execute("""SELECT count(`INSTITUTION_USER_ID`)as total FROM `attendance` WHERE 
                `INSTITUTION_USER_ID`=%s and `STATUS`=1""",(Userid))
            attendance = cursor.fetchone()
            if attendance !=None:
                total_attendance = attendance['total']
                print(total_attendance)
            else:
                total_attendance =0

            cursor.execute("""SELECT count(`User_Id`)as total FROM `user_behaviour` WHERE 
                `User_Id`=%s""",(Userid))
            seenVideos = cursor.fetchone()
            if seenVideos !=None:
                total_seenVideos = seenVideos['total']
                print(total_seenVideos)
            else:
                total_seenVideos =0

            nextcursor.execute("""SELECT count(`Student_Id`)as total FROM `assessment_tracking` WHERE 
                `Student_Id`=%s""",(Userid))
            givenAssessment = nextcursor.fetchone()
            if givenAssessment !=None:
                total_givenAssessment = givenAssessment['total']
                print(total_givenAssessment)
            else:
                givenAssessment =0

            nextcursor.execute("""SELECT count(`Student_UserID`)as total FROM 
                `assignment_mapping` WHERE `Student_UserID`=%s""",(Userid))
            givenAssignment = nextcursor.fetchone()
            if givenAssignment !=None:
                total_givenAssignment = givenAssignment['total']
                print(total_givenAssignment)
            else:
                total_givenAssignment =0
            

            if count_contest !=0 or countConins !=0 or countMedel !=0 or total_attendance !=0 or total_seenVideos !=0 or total_givenAssessment !=0 or total_givenAssignment !=0 : 
                return ({"attributes": {"status_desc": "Usage Details Of User",
                                        "status": "success"
                                        },
                         "responseList": {
                                            "Given_Contest": count_contest,
                                            "Earned_Coins" : countConins,
                                            "Earned_Medel" : countMedel,
                                            "Given_Attendance" : total_attendance,
                                            "Seen_Videos" : total_seenVideos,
                                            "Given_Assessment" : total_givenAssessment,
                                            "Given_Assignment" : total_givenAssignment
                                         }
                        }), status.HTTP_200_OK
            else:
                return ({"attributes": {"status_desc": "Usage Details Of User",
                                            "status": "success"
                                            },
                             "responseList": []
                            }), status.HTTP_200_OK
        else:
            cursor.execute("""SELECT Total_earned_Coins as total FROM 
                rewards_profile WHERE INSTITUTION_USER_ID=%s""",(Userid))
            earnedConins = cursor.fetchone()
            if earnedConins != None:
                countConins = earnedConins['total']
                print(countConins)
            else:
                countConins =0

            cursor.execute("""SELECT Medel FROM rewards_profile WHERE INSTITUTION_USER_ID=%s
                """,(Userid))
            earnedMedel = cursor.fetchone()
            if earnedMedel !=None:
                countMedel = earnedMedel['Medel']
                print(countMedel)
            else:
                countMedel =0

            cursor.execute("""SELECT count(`Student_ID`)as total FROM `student_contest_tracking` 
                WHERE `Student_ID`=%s""",(Userid))
            total_contest = cursor.fetchone()
            if total_contest !=None:
                count_contest = total_contest['total']
                print(count_contest)
            else:
                count_contest =0

            cursor.execute("""SELECT count(`INSTITUTION_USER_ID`)as total FROM `attendance` WHERE 
                `INSTITUTION_USER_ID`=%s and `STATUS`=1""",(Userid))
            attendance = cursor.fetchone()
            if attendance !=None:
                total_attendance = attendance['total']
                # print(total_attendance)
            else:
                total_attendance =0

            cursor.execute("""SELECT count(`User_Id`)as total FROM `user_behaviour` WHERE 
                `User_Id`=%s""",(Userid))
            seenVideos = cursor.fetchone()
            if seenVideos !=None:
                total_seenVideos = seenVideos['total']
                # print(total_seenVideos)
            else:
                total_seenVideos =0

            libcursor.execute("""SELECT count(`teacher_id`)as total FROM `assessment` 
                WHERE `teacher_id`=%s""",(Userid))
            createdAssessment = libcursor.fetchone()
            # print(createdAssessment)
            if createdAssessment !=None:
                total_createdAssessment = createdAssessment['total']
                # print(total_createdAssessment)
            else:
                total_createdAssessment =0

            nextcursor.execute("""SELECT count(`Teacher_ID`)as total FROM 
                `assignment` WHERE `Teacher_ID`=%s""",(Userid))
            createdAssignment = nextcursor.fetchone()
            if createdAssignment !=None:
                total_createdAssignment = createdAssignment['total']
                # print(total_createdAssignment)
            else:
                total_createdAssignment =0
            

            libcursor.execute("""SELECT count(`teacher_id`)as total FROM `content_library` 
                WHERE `teacher_id`=%s and `content_filetype`='video'""",(Userid))
            createdVideos = libcursor.fetchone()
            if createdVideos !=None:
                total_createdVideos = createdVideos['total']
                # print(total_createdVideos)
            else:
                total_createdVideos =0

            if count_contest !=0 or countConins !=0 or countMedel !=0 or total_attendance !=0 or total_seenVideos !=0 or total_createdAssessment !=0 or total_createdAssignment !=0 or total_createdVideos != 0: 
                return ({"attributes": {"status_desc": "Usage Details Of User",
                                        "status": "success"
                                        },
                         "responseList": {
                                            "Given_Contest": count_contest,
                                            "Earned_Coins" : countConins,
                                            "Earned_Medel" : countMedel,
                                            "Given_Attendance" : total_attendance,
                                            "Seen_Videos" : total_seenVideos,
                                            "Created_Assessment" : total_createdAssessment,
                                            "Created_Assignment" : total_createdAssignment,
                                            "Created_Videos" : total_createdVideos
                                         }
                        }), status.HTTP_200_OK
            else:
                return ({"attributes": {"status_desc": "Usage Details Of User",
                                            "status": "success"
                                            },
                             "responseList": []
                            }), status.HTTP_200_OK
#---------------------------------User-UsageDetails-by-instituionuserid-----------------------------------------#

#---------------------------------institution-dtls-by-date--------------------------------------------#
@name_space.route("/institutionDtlsByDate/<string:Start_date>/<string:End_date>")
class institutionDtlsByDate(Resource):
    def get(self,Start_date,End_date):
        connection = mysql_connection()
        cursor = connection.cursor()
        
        cursor.execute("""SELECT DISTINCT(institution_dtls.`INSTITUTION_ID`),
            `INSTITUTION_TYPE`, institution_dtls.`INSTITUTION_NAME`,
            (SELECT count(`INSTITUTION_USER_ID`) FROM `institution_user_credential_master` 
            WHERE institution_user_credential_master.`INSTITUTION_ID` = 
            institution_dtls.`INSTITUTION_ID`and `INSTITUTION_USER_ROLE`='S1')as total_student, 
            INSTITUTION_PHONE_NUMBER,`LAST_UPDATE_TIMESTAMP` FROM `institution_dtls` 
            inner join `institution_user_credential_master` on 
            institution_dtls.`INSTITUTION_ID`=
            institution_user_credential_master.`INSTITUTION_ID` 
            WHERE date(institution_dtls.`LAST_UPDATE_TIMESTAMP`) BETWEEN %s and %s""",
            (Start_date,End_date))
        institutiondtls = cursor.fetchall()
        
        for i in range(len(institutiondtls)):
                institutiondtls[i]['LAST_UPDATE_TIMESTAMP'] = institutiondtls[i]['LAST_UPDATE_TIMESTAMP'].isoformat()
        
        return ({"attributes": {"status_desc": "Institution Details",
                                "status": "success"
                                },
                 "responseList": institutiondtls
                }), status.HTTP_200_OK

#---------------------------------institution-dtls-by-date------------------------------------#

#---------------------------------previous-registration-count--------------------------#

@name_space.route("/previousRegistrationCount")
class registrationCountByCustom(Resource):
    def get(self):
        connection = mysql_connection()
        cursor = connection.cursor()

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID_TEACHER`) as total FROM 
            `teacher_dtls` WHERE `INSTITUTION_USER_ID_TEACHER` in(SELECT 
            `INSTITUTION_USER_ID` FROM `institution_user_credential` where 
            date(`LAST_UPDATE_TIMESTAMP`) = DATE(NOW()) + INTERVAL -1 DAY)""")
        teacher_yesterday = cursor.fetchone()
        count_yes_tea = teacher_yesterday['total']
        # print(total)

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID_TEACHER`) as total FROM 
            `teacher_dtls` WHERE `INSTITUTION_USER_ID_TEACHER` in(SELECT 
            `INSTITUTION_USER_ID` FROM `institution_user_credential` where 
            date(`LAST_UPDATE_TIMESTAMP`) >= DATE(NOW()) + INTERVAL -7 DAY AND 
            date(`LAST_UPDATE_TIMESTAMP`) < DATE(NOW()) + INTERVAL 0 DAY)""")

        teacher_last7 = cursor.fetchone()
        count_tea_last7 = teacher_last7['total']

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID_TEACHER`) as total FROM 
            `teacher_dtls` WHERE `INSTITUTION_USER_ID_TEACHER` in(SELECT 
            `INSTITUTION_USER_ID` FROM `institution_user_credential` where 
            date(`LAST_UPDATE_TIMESTAMP`) >= DATE(NOW()) + INTERVAL -30 DAY AND 
            date(`LAST_UPDATE_TIMESTAMP`) < DATE(NOW()) + INTERVAL 0 DAY)""")

        teacher_last30 = cursor.fetchone()
        count_tea_last30 = teacher_last30['total']

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID_STUDENT`)as total FROM 
            `student_dtls` WHERE `INSTITUTION_USER_ID_STUDENT` in(SELECT 
            `INSTITUTION_USER_ID` FROM `institution_user_credential` where 
            date(`LAST_UPDATE_TIMESTAMP`)= DATE(NOW()) + INTERVAL -1 DAY)""")
        student_yesterday = cursor.fetchone()
        count_yes_stu= student_yesterday['total']

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID_STUDENT`)as total FROM 
            `student_dtls` WHERE `INSTITUTION_USER_ID_STUDENT` in(SELECT 
            `INSTITUTION_USER_ID` FROM `institution_user_credential` where 
            date(`LAST_UPDATE_TIMESTAMP`)>= DATE(NOW()) + INTERVAL -7 DAY AND 
            date(`LAST_UPDATE_TIMESTAMP`) < DATE(NOW()) + INTERVAL 0 DAY)""")
        student_last7 = cursor.fetchone()
        count_stu_last7= student_last7['total']

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID_STUDENT`)as total FROM 
            `student_dtls` WHERE `INSTITUTION_USER_ID_STUDENT` in(SELECT 
            `INSTITUTION_USER_ID` FROM `institution_user_credential` where 
            date(`LAST_UPDATE_TIMESTAMP`)>= DATE(NOW()) + INTERVAL -30 DAY AND 
            date(`LAST_UPDATE_TIMESTAMP`) < DATE(NOW()) + INTERVAL 0 DAY)""")

        student_last30 = cursor.fetchone()
        count_stu_last30= student_last30['total']

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID_GUARDIAN`)as total FROM 
            `guardian_dtls` WHERE `INSTITUTION_USER_ID_STUDENT` in(SELECT 
            `INSTITUTION_USER_ID` FROM `institution_user_credential` where 
            date(`LAST_UPDATE_TIMESTAMP`)=DATE(NOW()) + INTERVAL -1 DAY)""")
        parent_yesterday = cursor.fetchone()
        count_yes_par= parent_yesterday['total']

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID_GUARDIAN`)as total FROM 
            `guardian_dtls` WHERE `INSTITUTION_USER_ID_STUDENT` in(SELECT 
            `INSTITUTION_USER_ID` FROM `institution_user_credential` where 
            date(`LAST_UPDATE_TIMESTAMP`)>= DATE(NOW()) + INTERVAL -7 DAY AND 
            date(`LAST_UPDATE_TIMESTAMP`) < DATE(NOW()) + INTERVAL 0 DAY)""")

        parent_last7 = cursor.fetchone()
        count_par_last7= parent_last7['total']

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID_GUARDIAN`)as total FROM 
            `guardian_dtls` WHERE `INSTITUTION_USER_ID_STUDENT` in(SELECT 
            `INSTITUTION_USER_ID` FROM `institution_user_credential` where 
            date(`LAST_UPDATE_TIMESTAMP`)>= DATE(NOW()) + INTERVAL -30 DAY AND 
            date(`LAST_UPDATE_TIMESTAMP`) < DATE(NOW()) + INTERVAL 0 DAY)""")

        parent_last30= cursor.fetchone()
        count_par_last30= parent_last30['total']

        cursor.execute("""SELECT count(`INSTITUTION_ID`)as total FROM `institution_dtls` 
            where date(`LAST_UPDATE_TIMESTAMP`)=DATE(NOW()) + INTERVAL -1 DAY""")
        institution_yesterday = cursor.fetchone()
        count_yes_ins= institution_yesterday['total']

        cursor.execute("""SELECT count(`INSTITUTION_ID`)as total FROM `institution_dtls` 
            where date(`LAST_UPDATE_TIMESTAMP`)>= DATE(NOW()) + INTERVAL -7 DAY AND 
            date(`LAST_UPDATE_TIMESTAMP`) < DATE(NOW()) + INTERVAL 0 DAY""")

        institution_last7 = cursor.fetchone()
        count_ins_last7= institution_last7['total']

        cursor.execute("""SELECT count(`INSTITUTION_ID`)as total FROM `institution_dtls` 
            where date(`LAST_UPDATE_TIMESTAMP`)>= DATE(NOW()) + INTERVAL -30 DAY AND 
            date(`LAST_UPDATE_TIMESTAMP`) < DATE(NOW()) + INTERVAL 0 DAY""")

        institution_last30= cursor.fetchone()
        count_ins_last30= institution_last30['total']

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID`)as total FROM 
            `institution_user_credential_master` WHERE `INSTITUTION_USER_ID` not in(SELECT 
            distinct(`INSTITUTION_USER_ID`) FROM `institution_user_tracking`)""")

        notUsedUser= cursor.fetchone()
        count_notUsedUser= notUsedUser['total']
        return ({"attributes": {"status_desc": "Registration Details.",
                                "status": "success"
                                },
                "responseList": {
                                   "previous_teacher": count_yes_tea,
                                  
                                   "teacher_last7days": count_tea_last7,

                                   "teacher_last30days": count_tea_last30,

                                   "previous_student": count_yes_stu,

                                   "student_last7days": count_stu_last7,

                                   "student_last30days": count_stu_last30,

                                   "previous_parent": count_yes_par,

                                   "parent_last7days": count_par_last7,

                                   "parent_last30days": count_par_last30,

                                   "previous_institution": count_yes_ins,

                                   "ins_last7days": count_ins_last7,

                                   "ins_last30days": count_ins_last30,
                                   
                                   "notUsedUser" : count_notUsedUser
                                  },
                }), status.HTTP_200_OK
        
#---------------------------------previous-registration-count--------------------------#

#---------------------------------registered-but-not-used-app-------------------------------#
@name_space.route("/notUsedUserdtls")
class notUsedUserdtls(Resource):
    def get(self):
        connection = mysql_connection()
        cursor = connection.cursor()

        cursor.execute("""SELECT institution_dtls.`Institution_ID`,
            institution_user_credential.`INSTITUTION_USER_ID`, institution_dtls.
            `INSTITUTION_NAME`,`INSTITUTION_USER_ROLE`,concat(`FIRST_NAME`,' ',`LAST_NAME`) 
            as name,`INSTITUTION_USER_NAME`, `INSTITUTION_USER_PASSWORD`,
            `PRIMARY_CONTACT_NUMBER`,institution_user_credential.`IMAGE_URL`, 
            institution_user_credential_master.`INSTITUTION_NAME` as school_name,
            `institution_user_credential`.`LAST_UPDATE_TIMESTAMP` FROM 
            `institution_user_credential` inner join `institution_user_credential_master` 
            on institution_user_credential.`INSTITUTION_USER_ID`=
            institution_user_credential_master.`INSTITUTION_USER_ID` 
            INNER JOIN `institution_dtls` on institution_user_credential_master.
            `INSTITUTION_ID`=institution_dtls.`INSTITUTION_ID` where 
            institution_user_credential_master.`INSTITUTION_USER_ID` not in(SELECT 
            distinct(`INSTITUTION_USER_ID`) FROM `institution_user_tracking`)""")
        
        notUsedUserdtls = cursor.fetchall()
        for i in range(len(notUsedUserdtls)):
                notUsedUserdtls[i]['LAST_UPDATE_TIMESTAMP'] = notUsedUserdtls[i]['LAST_UPDATE_TIMESTAMP'].isoformat()
   
        return ({"attributes": {"status_desc": "user Details",
                                "status": "success"
                                },
                 "responseList": notUsedUserdtls
                }), status.HTTP_200_OK
#---------------------------------registered-but-not-used-app-------------------------------#

#---------------------------------count-all-module-used---------------------------------#
@name_space.route("/numberOfUsedModule")
class numberOfUsedModule(Resource):
    def get(self):
        connection = mysql_connection()
        cursor = connection.cursor()

        nextconnection = b2b_connection()
        nextcursor = nextconnection.cursor()

        libconnection =library_connection()
        libcursor = libconnection.cursor()

        cursor.execute("""SELECT count(`ATTENDANCE_ID`)as total FROM `attendance`""")
        
        attendance= cursor.fetchone()
        count_attendance= attendance['total']

        cursor.execute("""SELECT count(`Tracking_ID`)as total FROM 
            `student_contest_tracking`""")
        
        contest= cursor.fetchone()
        count_contest= contest['total']

        nextcursor.execute("""SELECT count(`Assessment_Tracking_Id`)as total FROM 
            `assessment_tracking` WHERE `Assessment_Id` is not null""")
        
        assessment= nextcursor.fetchone()
        count_assessment= assessment['total']

        nextcursor.execute("""SELECT count(`Assignment_ID`)as total FROM `assignment` WHERE 
            `Assignment_Type`!='' and `Assignment_Type` is not null""")
        
        assignment= nextcursor.fetchone()
        count_assignment= assignment['total']

        nextcursor.execute("""SELECT count(`test_id`) as total  FROM `class_test`""")

        classtest= nextcursor.fetchone()
        count_classtest= classtest['total']

        libcursor.execute("""SELECT count(`liveclass_id`)as total FROM `liveclass_mapping`""")
        
        liveclass= libcursor.fetchone()
        count_liveclass= liveclass['total']

        libcursor.execute("""SELECT count(`content_id`)as total FROM `content_library` 
            WHERE `teacher_id`!=2226""")

        content_library= libcursor.fetchone()
        count_content_library= content_library['total']

        cursor.execute("""SELECT count(`id`)as total FROM 
            `activity_institution_transaction_details` WHERE `institution_user_id` not 
            in(117,2962)""")

        fees_transaction = cursor.fetchone()
        count_fees_transaction= fees_transaction['total']

        cursor.execute("""SELECT count(`User_Behaviour_Id`)as total FROM `user_behaviour`
         WHERE `Content_Detail_Id`!=0""")

        seen_videos = cursor.fetchone()
        count_seen_videos= seen_videos['total']

        return ({"attributes": {"status_desc": "Number Of Used Module",
                                "status": "success"
                                },
                 "responseList": {
                                   "used_attendance": count_attendance,
                                  
                                   "used_contest": count_contest,

                                   "used_assignment": count_assignment,

                                   "used_classtest": count_classtest,

                                   "used_liveclass": count_liveclass,

                                   "used_contentLibrary": count_content_library,

                                   "used_feesModule" :count_fees_transaction,

                                   "used_mysyllabus" : count_seen_videos

                                   },

                }), status.HTTP_200_OK
#---------------------------------count-all-module-used---------------------------------#

#---------------------------teacher-dtls-by insid-sdate-edate-----------------------------#
@name_space.route("/teacherDtlsByInsIdDate/<int:INSTITUTION_ID>/<string:Start_date>/<string:End_date>")
class teacherDtlsByInsIdDate(Resource):
    def get(self,INSTITUTION_ID,Start_date,End_date):
        connection = mysql_connection()
        cursor = connection.cursor()

        nextconnection = b2b_connection()
        nextcursor = nextconnection.cursor()

        cursor.execute("""SELECT institution_dtls.`Institution_ID`, institution_dtls.
            `INSTITUTION_NAME`,(SELECT count(`INSTITUTION_USER_ID`) FROM 
            `institution_user_credential_master` WHERE 
            institution_user_credential_master.`INSTITUTION_ID` =
            institution_dtls.`INSTITUTION_ID` and `INSTITUTION_USER_ROLE`='S1')as 
            total_student,`INSTITUTION_USER_ROLE`,institution_user_credential.`INSTITUTION_USER_ID`,
            concat(`FIRST_NAME`,' ',`LAST_NAME`) 
            as name,`PRIMARY_CONTACT_NUMBER`,
            `institution_user_credential`.`LAST_UPDATE_TIMESTAMP` FROM 
            `institution_user_credential` inner join `institution_user_credential_master`
             on institution_user_credential. `INSTITUTION_USER_ID`=
             institution_user_credential_master.`INSTITUTION_USER_ID` INNER JOIN 
             `institution_dtls` on institution_user_credential_master.`INSTITUTION_ID` =
            institution_dtls.`INSTITUTION_ID` where institution_dtls.
            `INSTITUTION_ID`=%s and date(institution_user_credential.`LAST_UPDATE_TIMESTAMP`)
            between %s and %s and `INSTITUTION_USER_ROLE`='TA' order by 
            institution_user_credential.`INSTITUTION_USER_ID` asc""",
            (INSTITUTION_ID,Start_date,End_date))
        
        teacher_dtls= cursor.fetchall()
        for i in range(len(teacher_dtls)):
            teacher_dtls[i]['LAST_UPDATE_TIMESTAMP'] = teacher_dtls[i]['LAST_UPDATE_TIMESTAMP'].isoformat()
            teacherids = teacher_dtls[i]['INSTITUTION_USER_ID']
            # print(teacherids)
            cursor.execute("""SELECT `User_Id`,GROUP_CONCAT(user_subscription.`Product_CODE`)
                as product_code,GROUP_CONCAT(`Product_Desc`)as product,subscription_enddate FROM `user_subscription` 
                INNER join `product` ON user_subscription.`Product_CODE` =product.`Product_CODE`
                WHERE `User_Id` =%s""",(teacherids))
            subscription_dtls = cursor.fetchone()
            print(subscription_dtls)

            if subscription_dtls.get('User_Id') == None:
                teacher_dtls[i]['subscription_dtls'] = []
            else:
                teacher_dtls[i]['subscription_dtls'] = subscription_dtls
            
        return ({"attributes": {"status_desc": "Teacher Details",
                                    "status": "success"
                                    },
                     "responseList": teacher_dtls}), status.HTTP_200_OK
        
#---------------------------teacher-dtls-by insid-sdate-edate---------------------------------#

#---------------------------student-dtls-by insid-sdate-edate---------------------------------#
@name_space.route("/studentDtlsByInsIdDate/<int:INSTITUTION_ID>/<string:Start_date>/<string:End_date>")
class studentDtlsByInsIdDate(Resource):
    def get(self,INSTITUTION_ID,Start_date,End_date):
        connection = mysql_connection()
        cursor = connection.cursor()

        cursor.execute("""SELECT institution_dtls.`Institution_ID`, institution_dtls.
                `INSTITUTION_NAME`,`INSTITUTION_USER_ROLE`,institution_user_credential.`INSTITUTION_USER_ID`,
                concat(`FIRST_NAME`,' ',`LAST_NAME`) 
                as name,`INSTITUTION_USER_NAME`, `INSTITUTION_USER_PASSWORD`,
                `PRIMARY_CONTACT_NUMBER`,`USER_UNIQUE_ID`,institution_user_credential.`IMAGE_URL`, 
                institution_user_credential_master.`INSTITUTION_NAME` as school_name,`CLASS`,`Board`,
                `institution_user_credential`.`LAST_UPDATE_TIMESTAMP`
            FROM `institution_user_credential` inner join 
            `institution_user_credential_master` on institution_user_credential.
            `INSTITUTION_USER_ID`=institution_user_credential_master.`INSTITUTION_USER_ID` 
            INNER JOIN `institution_dtls` on institution_user_credential_master.`INSTITUTION_ID`
                 =institution_dtls.`INSTITUTION_ID` INNER join `student_dtls` on 
                 institution_user_credential.`INSTITUTION_USER_ID`=student_dtls.
                 `INSTITUTION_USER_ID_STUDENT`
            where date(institution_user_credential.`LAST_UPDATE_TIMESTAMP`) 
            between %s and %s and institution_user_credential_master.`INSTITUTION_ID`=%s
             and `INSTITUTION_USER_ROLE`= 'S1'""",(Start_date,End_date,INSTITUTION_ID))


        studtlsbydate = cursor.fetchall()
        for i in range(len(studtlsbydate)):
            studtlsbydate[i]['LAST_UPDATE_TIMESTAMP'] = studtlsbydate[i]['LAST_UPDATE_TIMESTAMP'].isoformat()
    
        return ({"attributes": {"status_desc": "user Details",
                                "status": "success"
                                },
                 "responseList": studtlsbydate
                }), status.HTTP_200_OK
#---------------------------student-dtls-by insid-sdate-edate---------------------------------#

#--------------------------------------count-student-by-insid---------------------------------#
@name_space.route("/studentDtlsByInstitutionId/<int:INSTITUTION_ID>")
class studentDtlsByInstitutionId(Resource):
    def get(self,INSTITUTION_ID):
        connection = mysql_connection()
        cursor = connection.cursor()

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID`)as total FROM 
            `institution_user_credential_master` WHERE `INSTITUTION_ID` = %s AND 
            `INSTITUTION_USER_ROLE` LIKE 'S1'""",(INSTITUTION_ID))
        register_student = cursor.fetchone()
        count_register = register_student['total']

        cursor.execute("""SELECT count(DISTINCT(`institution_user_id`))as total FROM 
            `institution_user_tracking` WHERE `institution_user_id` in(SELECT 
            `INSTITUTION_USER_ID` FROM `institution_user_credential_master` WHERE 
            `INSTITUTION_ID` = %s AND `INSTITUTION_USER_ROLE` LIKE 'S1')""",(INSTITUTION_ID))
        
        download_student = cursor.fetchone()
        count_download = download_student['total']

        return ({"attributes": {"status_desc": "User Details",
                                "status": "success"
                                },
                 "responseList": {
                                   "registered_student": count_register,
                                   
                                   "downloaded_student" : count_download
                                },
                }), status.HTTP_200_OK

#--------------------------------------count-student-by-insid---------------------------------#

#-------------------------------------module-usage-count-by-insid----------------------------------#
@name_space.route("/countModuleUsageByInstitutionId/<int:INSTITUTION_ID>")
class countModuleUsageByInstitutionId(Resource):
    def get(self,INSTITUTION_ID):
        connection = mysql_connection()
        cursor = connection.cursor()

        nextconnection = b2b_connection()
        nextcursor = nextconnection.cursor()

        libconnection =library_connection()
        libcursor = libconnection.cursor()

        cursor.execute("""SELECT count(DISTINCT(`User_Id`))as total FROM `user_behaviour` 
            WHERE `User_Id` in(SELECT `INSTITUTION_USER_ID` FROM 
            `institution_user_credential_master` WHERE `INSTITUTION_ID` = %s AND 
            `INSTITUTION_USER_ROLE` LIKE 'S1')""",(INSTITUTION_ID))
        seen_videos = cursor.fetchone()
        count_seen_videos = seen_videos['total']

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID`)as total FROM `attendance` 
            WHERE `INSTITUTION_USER_ID` in(SELECT `INSTITUTION_USER_ID` FROM 
            `institution_user_credential_master` WHERE `INSTITUTION_ID` = %s AND 
            `INSTITUTION_USER_ROLE` LIKE 'S1') and `STATUS`=1""",(INSTITUTION_ID))
        attendance = cursor.fetchone()
        if attendance !=None:
            total_attendance = attendance['total']
            print(total_attendance)
        else:
            total_attendance =0

        cursor.execute("""SELECT `INSTITUTION_USER_ID` FROM 
            `institution_user_credential_master` WHERE `INSTITUTION_ID` = %s AND 
            `INSTITUTION_USER_ROLE` LIKE 'S1'""",(INSTITUTION_ID))
        
        student_id = cursor.fetchall()
        # print(student_id)

        details = []
        for i in range(len(student_id)):
            details.append(student_id[i]['INSTITUTION_USER_ID'])
        details = tuple(details)
        nextcursor.execute("""SELECT COUNT(DISTINCT(`Assignment_ID`)) as total FROM 
            `assignment_mapping` WHERE `Student_UserID` in (%s)""",format(details))
        assign_assignment = nextcursor.fetchone()
        if assign_assignment !=None:
            count_assign_assignment = assign_assignment['total']
        else:
            count_assign_assignment = 0
        
        cursor.execute("""SELECT `INSTITUTION_USER_ID` FROM 
            `institution_user_credential_master` WHERE `INSTITUTION_ID` = %s AND 
            `INSTITUTION_USER_ROLE` LIKE 'S1'""",(INSTITUTION_ID))
        
        student_id = cursor.fetchall()
        # print(student_id)

        details = []
        for i in range(len(student_id)):
            details.append(student_id[i]['INSTITUTION_USER_ID'])
        details = tuple(details)
        nextcursor.execute("""SELECT count(`Student_Id`)as total FROM 
            `assessment_tracking` WHERE `Student_Id` in (%s)""",format(details))
        givenAssessment = nextcursor.fetchone()
        if givenAssessment !=None:
            total_givenAssessment = givenAssessment['total']
            print(total_givenAssessment)
        else:
            givenAssessment =0

        libcursor.execute("""SELECT count(`liveclass_id`)as total FROM `student_liveclass_tracking` 
            WHERE `Student_ID` in (%s)""",format(details))
        attend_liveclass = nextcursor.fetchone()
        if attend_liveclass !=None:
            count_attend_liveclass = attend_liveclass['total']
        else:
            count_attend_liveclass = 0

        cursor.execute("""SELECT count(`Tracking_ID`)as total FROM 
            `student_contest_tracking` WHERE `Student_ID`in(SELECT `INSTITUTION_USER_ID` 
            FROM `institution_user_credential_master` WHERE `INSTITUTION_ID` = %s AND 
            `INSTITUTION_USER_ROLE` LIKE 'S1')""",(INSTITUTION_ID))
        total_contest = cursor.fetchone()
        if total_contest !=None:
            count_contest = total_contest['total']
            # print(count_contest)
        else:
            count_contest =0
        
        cursor.execute("""SELECT `INSTITUTION_USER_ID` FROM 
            `institution_user_credential_master` WHERE `INSTITUTION_ID` = %s AND 
            `INSTITUTION_USER_ROLE` LIKE 'S1'""",(INSTITUTION_ID))
        
        student_id = cursor.fetchall()
        # print(student_id)

        details = []
        for i in range(len(student_id)):
            details.append(student_id[i]['INSTITUTION_USER_ID'])
        details = tuple(details)
        nextcursor.execute("""SELECT count(`student_id`)as total FROM `classtest_student_mapping`
         WHERE `student_id` in(%s)""",format(details))

        classtest= nextcursor.fetchone()
        if classtest !=None:
            count_classtest= classtest['total']
        else:
            count_classtest = 0
        
        
        cursor.execute("""SELECT `INSTITUTION_USER_ID` FROM 
            `institution_user_credential_master` WHERE `INSTITUTION_ID` = %s AND 
            `INSTITUTION_USER_ROLE` LIKE 'TA'""",(INSTITUTION_ID))
        
        teacher_id = cursor.fetchall()
        # print(teacher_id)

        detail = []
        for i in range(len(teacher_id)):
            detail.append(teacher_id[i]['INSTITUTION_USER_ID'])
        detail = tuple(detail)
        libcursor.execute("""SELECT count(`content_id`)as total FROM `content_library` WHERE 
            `teacher_id` in (%s) and `content_filetype`='video'""",format(detail))
        
        create_videos = libcursor.fetchone()
        if create_videos !=None:
            count_create_videos = create_videos['total']
        else:
            count_create_videos = 0
        
        return ({"attributes": {"status_desc": "Number Of Usage",
                                "status": "success"
                                },
                 "responseList": {
                                   "seen_videos": count_seen_videos,
                                   
                                   "assign_assignment" : count_assign_assignment,

                                   "Given_Attendance" : total_attendance,

                                   "assign_assessment" : total_givenAssessment,

                                   "assign_classtest" : count_classtest,

                                   "attend_liveclass" : count_attend_liveclass,

                                   "Given_Contest" : count_contest,

                                   "create_videos" : count_create_videos
                                },
                }), status.HTTP_200_OK

#-------------------------------------module-usage-count-by-insid---------------------------------#

#-------------------------------------tracking-count-by-insid---------------------------------#
@name_space.route("/trackingdtlsByInstitutionId/<int:INSTITUTION_ID>")
class trackingdtlsByInstitutionId(Resource):
    def get(self,INSTITUTION_ID):
        connection = mysql_connection()
        cursor = connection.cursor()

        cursor.execute("""SELECT count(DISTINCT(`institution_user_id`))as total FROM 
            `institution_user_tracking` WHERE `institution_user_id` in(SELECT 
            `INSTITUTION_USER_ID` FROM `institution_user_credential_master` WHERE 
            `INSTITUTION_ID` = %s AND `INSTITUTION_USER_ROLE` LIKE 'S1') and 
            date(`last_update_ts`)= DATE(NOW()) + INTERVAL -1 DAY""",(INSTITUTION_ID))
        student_yesterday = cursor.fetchone()
        count_yes_stu= student_yesterday['total']

        cursor.execute("""SELECT count(DISTINCT(`institution_user_id`))as total FROM 
            `institution_user_tracking` WHERE `institution_user_id` in(SELECT 
            `INSTITUTION_USER_ID` FROM `institution_user_credential_master` WHERE 
            `INSTITUTION_ID` = %s AND `INSTITUTION_USER_ROLE` LIKE 'S1') and  
            date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY AND 
            date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(INSTITUTION_ID))
        student_last7 = cursor.fetchone()
        count_stu_last7= student_last7['total']

        cursor.execute("""SELECT count(DISTINCT(`institution_user_id`))as total FROM 
            `institution_user_tracking` WHERE `institution_user_id` in(SELECT 
            `INSTITUTION_USER_ID` FROM `institution_user_credential_master` WHERE 
            `INSTITUTION_ID` = %s AND `INSTITUTION_USER_ROLE` LIKE 'S1') and 
            date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -30 DAY AND 
            date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(INSTITUTION_ID))

        student_last30 = cursor.fetchone()
        count_stu_last30= student_last30['total']

        return ({"attributes": {"status_desc": "Tracking Count",
                                "status": "success"
                                },
                 "responseList": {
                                   "previous_student": count_yes_stu,

                                   "student_last7days": count_stu_last7,

                                   "student_last30days": count_stu_last30
                                },
                }), status.HTTP_200_OK
#-------------------------------------tracking-count-by-insid---------------------------------#

#--------------------------------all-institution details---------------------------------#
@name_space.route("/institutionDtls")
class institutionDtlsByDate(Resource):
    def get(self):
        connection = mysql_connection()
        cursor = connection.cursor()
        
        cursor.execute("""SELECT DISTINCT(institution_dtls.`INSTITUTION_ID`),
            `INSTITUTION_TYPE`, institution_dtls.`INSTITUTION_NAME`,
            (SELECT count(`INSTITUTION_USER_ID`) FROM `institution_user_credential_master` 
            WHERE institution_user_credential_master.`INSTITUTION_ID` = 
            institution_dtls.`INSTITUTION_ID`and `INSTITUTION_USER_ROLE`='S1')as total_student, 
            INSTITUTION_PHONE_NUMBER,`LAST_UPDATE_TIMESTAMP` FROM `institution_dtls` 
            inner join `institution_user_credential_master` on 
            institution_dtls.`INSTITUTION_ID`=
            institution_user_credential_master.`INSTITUTION_ID`""",)
        institutiondtls = cursor.fetchall()
        
        for i in range(len(institutiondtls)):
                institutiondtls[i]['LAST_UPDATE_TIMESTAMP'] = institutiondtls[i]['LAST_UPDATE_TIMESTAMP'].isoformat()
        
        return ({"attributes": {"status_desc": "Institution Details",
                                "status": "success"
                                },
                 "responseList": institutiondtls
                }), status.HTTP_200_OK

#--------------------------------all-institution details---------------------------------#

#----------------------regtration-count-by-institution-id------------------------------#

@name_space.route("/totalNumberOfRegistrationByInstitutionId/<int:institution_id>")
class registrationDetails(Resource):
    def get(self,institution_id):
        connection = mysql_connection()
        cursor = connection.cursor()

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID`) as `total` FROM 
            `institution_user_credential_master` where `INSTITUTION_ID`=%s""",(institution_id))
        total_reg = cursor.fetchone()
        count_reg = total_reg['total']
        # print(total)

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID`) as `total` FROM 
            `institution_user_credential_master` where `INSTITUTION_ID`=%s and 
            `INSTITUTION_USER_ROLE`='TA'""",(institution_id))

        total_teacher = cursor.fetchone()
        count_tea = total_teacher['total']

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID`) as `total` FROM 
            `institution_user_credential_master` where `INSTITUTION_ID`=%s and 
            `INSTITUTION_USER_ROLE`='S1'""",(institution_id))

        total_student = cursor.fetchone()
        count_stu = total_student['total']

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID`) as `total` FROM 
            `institution_user_credential_master` where `INSTITUTION_ID`=%s and 
            `INSTITUTION_USER_ROLE`='G1'""",(institution_id))
        total_parent = cursor.fetchone()
        count_par = total_parent['total']

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID`) as `total` FROM 
            `institution_user_credential_master` where `INSTITUTION_ID`=%s and 
            `INSTITUTION_USER_ROLE`='S1' and date(`LAST_UPDT_TS`)=CURdate() 
            and `INSTITUTION_USER_ROLE`='TA'""",(institution_id))

        currentdate_tea = cursor.fetchone()
        curr_count_tea = currentdate_tea['total']

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID`) as `total` FROM 
            `institution_user_credential_master` where `INSTITUTION_ID`=%s and 
            `INSTITUTION_USER_ROLE`='S1' and date(`LAST_UPDT_TS`)=CURdate() 
            and `INSTITUTION_USER_ROLE`='S1'""",(institution_id))

        currentdate_stu = cursor.fetchone()
        curr_count_stu = currentdate_stu['total']

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID`) as `total` FROM 
            `institution_user_credential_master` where `INSTITUTION_ID`=%s and 
            `INSTITUTION_USER_ROLE`='S1' and date(`LAST_UPDT_TS`)=CURdate() 
            and `INSTITUTION_USER_ROLE`='G1'""",(institution_id))

        currentdate_par = cursor.fetchone()
        curr_count_par = currentdate_par['total']

        
        return ({"attributes": {"status_desc": "Registration Details.",
                                "status": "success"
                                },
                "responseList": {
                                   "total_registration": count_reg,
                                  
                                   "total_teachers": count_tea,

                                   "total_students": count_stu,

                                   "total_parents": count_par,

                                   "todays_teachers": curr_count_tea,

                                   "todays_students": curr_count_stu,

                                   "todays_parents": curr_count_par
                                  },
                }), status.HTTP_200_OK

#----------------------regtration-count-by-institution-id------------------------------#

#---------------------regtration-dtls-by-date-ins-id---------------------------------#

@name_space.route("/registrationDtlsByInstitutionIdRoleDate/<int:institution_id>/<string:Start_date>/<string:End_date>/<string:User_role>")
class registrationDtlsByInstitutionIdRoleDate(Resource):
    def get(self,institution_id,Start_date,End_date,User_role):
        connection = mysql_connection()
        cursor = connection.cursor()

        if User_role =='S1':
            cursor.execute("""SELECT institution_dtls.`Institution_ID`, institution_dtls.
                    `INSTITUTION_NAME`,`INSTITUTION_USER_ROLE`,institution_user_credential.`INSTITUTION_USER_ID`,
                    concat(`FIRST_NAME`,' ',`LAST_NAME`) 
                    as name,`INSTITUTION_USER_NAME`, `INSTITUTION_USER_PASSWORD`,
                    `PRIMARY_CONTACT_NUMBER`,institution_user_credential.`IMAGE_URL`, 
                    institution_user_credential_master.`INSTITUTION_NAME` as school_name,`CLASS`,`Board`,
                    `institution_user_credential_master`.`LAST_UPDT_TS`
                FROM `institution_user_credential` inner join 
                `institution_user_credential_master` on institution_user_credential.
                `INSTITUTION_USER_ID`=institution_user_credential_master.`INSTITUTION_USER_ID` 
                INNER JOIN `institution_dtls` on institution_user_credential_master.`INSTITUTION_ID`
                     =institution_dtls.`INSTITUTION_ID` INNER join `student_dtls` on 
                     institution_user_credential.`INSTITUTION_USER_ID`=student_dtls.
                     `INSTITUTION_USER_ID_STUDENT`
                where date(institution_user_credential_master.`LAST_UPDT_TS`) 
                between %s and %s and `INSTITUTION_USER_ROLE`= %s and 
                institution_user_credential_master.`INSTITUTION_ID`=%s""", 
                (Start_date,End_date,User_role,institution_id))


            regdtlsbydate = cursor.fetchall()
            for i in range(len(regdtlsbydate)):
                regdtlsbydate[i]['LAST_UPDT_TS'] = regdtlsbydate[i]['LAST_UPDT_TS'].isoformat()
        
        elif User_role =='TA':
            cursor.execute("""SELECT institution_dtls.`Institution_ID`, institution_dtls.
                    `INSTITUTION_NAME`,`INSTITUTION_USER_ROLE`,institution_user_credential.`INSTITUTION_USER_ID`,
                    concat(`FIRST_NAME`,' ',`LAST_NAME`) 
                    as name,`INSTITUTION_USER_NAME`, `INSTITUTION_USER_PASSWORD`,
                    `PRIMARY_CONTACT_NUMBER`,institution_user_credential.`IMAGE_URL`, 
                    institution_user_credential_master.`INSTITUTION_NAME` as school_name,
                    `institution_user_credential_master`.`LAST_UPDT_TS`
                FROM `institution_user_credential` inner join 
                `institution_user_credential_master` on institution_user_credential.
                `INSTITUTION_USER_ID`=institution_user_credential_master.`INSTITUTION_USER_ID` 
                INNER JOIN `institution_dtls` on institution_user_credential_master.`INSTITUTION_ID`
                     =institution_dtls.`INSTITUTION_ID` 
                where date(institution_user_credential_master.`LAST_UPDT_TS`) 
                between %s and %s and `INSTITUTION_USER_ROLE`= %s and 
                institution_user_credential_master.`INSTITUTION_ID`=%s""", 
                (Start_date,End_date,User_role,institution_id))


            regdtlsbydate = cursor.fetchall()
            for i in range(len(regdtlsbydate)):
                regdtlsbydate[i]['LAST_UPDT_TS'] = regdtlsbydate[i]['LAST_UPDT_TS'].isoformat()
        
        else:
            cursor.execute("""SELECT institution_dtls.`Institution_ID`, institution_dtls.
                    `INSTITUTION_NAME`,`INSTITUTION_USER_ROLE`,institution_user_credential.`INSTITUTION_USER_ID`,
                    concat(`FIRST_NAME`,' ',`LAST_NAME`) 
                    as name,`INSTITUTION_USER_NAME`, `INSTITUTION_USER_PASSWORD`,
                    `PRIMARY_CONTACT_NUMBER`,institution_user_credential.`IMAGE_URL`, 
                    institution_user_credential_master.`INSTITUTION_NAME` as school_name,`RELATIONSHIP`,
                    `institution_user_credential_master`.`LAST_UPDT_TS`
                FROM `institution_user_credential` inner join 
                `institution_user_credential_master` on institution_user_credential.
                `INSTITUTION_USER_ID`=institution_user_credential_master.`INSTITUTION_USER_ID` 
                INNER JOIN `institution_dtls` on institution_user_credential_master.`INSTITUTION_ID`
                     =institution_dtls.`INSTITUTION_ID` INNER join guardian_dtls on institution_user_credential_master.`INSTITUTION_USER_ID` = guardian_dtls.INSTITUTION_USER_ID_GUARDIAN
                where date(institution_user_credential_master.`LAST_UPDT_TS`)  
                between %s and %s and `INSTITUTION_USER_ROLE`= %s and 
                institution_user_credential_master.`INSTITUTION_ID`=%s""", 
                (Start_date,End_date,User_role,institution_id))


            regdtlsbydate = cursor.fetchall()
            for i in range(len(regdtlsbydate)):
                regdtlsbydate[i]['LAST_UPDT_TS'] = regdtlsbydate[i]['LAST_UPDT_TS'].isoformat()
        
        return ({"attributes": {"status_desc": "user Details",
                                "status": "success"
                                },
                 "responseList": regdtlsbydate
                }), status.HTTP_200_OK

#---------------------regtration-dtls-by-date-ins-id---------------------------------#

#------------------count-all-module-used-by-ins-id---------------------------------#
@name_space.route("/numberOfUsedModuleByInstitutionId/<int:institution_id>")
class numberOfUsedModuleByInstitutionId(Resource):
    def get(self,institution_id):
        connection = mysql_connection()
        cursor = connection.cursor()

        nextconnection = b2b_connection()
        nextcursor = nextconnection.cursor()

        libconnection =library_connection()
        libcursor = libconnection.cursor()

        cursor.execute("""SELECT count(`ATTENDANCE_ID`)as total FROM `attendance` 
            WHERE `INSTITUTION_USER_ID` in(SELECT `INSTITUTION_USER_ID` FROM 
            `institution_user_credential_master` WHERE `INSTITUTION_ID` =%s AND 
            `INSTITUTION_USER_ROLE` LIKE 'S1') and `STATUS`=1""",(institution_id))
        
        attendance= cursor.fetchone()
        count_attendance= attendance['total']

        cursor.execute("""SELECT count(`Tracking_ID`)as total FROM 
            `student_contest_tracking` WHERE `Student_ID` 
            in(SELECT `INSTITUTION_USER_ID` FROM 
            `institution_user_credential_master` WHERE `INSTITUTION_ID` =%s AND 
            `INSTITUTION_USER_ROLE` LIKE 'S1')""",(institution_id))
        
        contest= cursor.fetchone()
        count_contest= contest['total']

        cursor.execute("""SELECT `INSTITUTION_USER_ID` FROM 
            `institution_user_credential_master` WHERE `INSTITUTION_ID` =%s AND 
            `INSTITUTION_USER_ROLE` LIKE 'S1'""",(institution_id))
        
        student_id = cursor.fetchall()
        detail = []
        for i in range(len(student_id)):
            detail.append(student_id[i]['INSTITUTION_USER_ID'])
        detail = tuple(detail)
        
        nextcursor.execute("""SELECT count(`Assessment_Tracking_Id`)as total FROM 
          `assessment_tracking` WHERE `Student_Id` in (%s) and `Assessment_Id` is not null
          """,format(detail))
        
        assessment= nextcursor.fetchone()
        count_assessment= assessment['total']

        cursor.execute("""SELECT `INSTITUTION_USER_ID` FROM 
            `institution_user_credential_master` WHERE `INSTITUTION_ID` =%s AND 
            `INSTITUTION_USER_ROLE` LIKE 'TA'""",(institution_id))
        
        teacher_id = cursor.fetchall()
        details = []
        for i in range(len(teacher_id)):
            details.append(teacher_id[i]['INSTITUTION_USER_ID'])
        details = tuple(details)
        nextcursor.execute("""SELECT count(`Assignment_ID`)as total FROM `assignment` 
            WHERE `Teacher_ID` in (%s)""",format(details))       
        assignment = nextcursor.fetchone()
        print(assignment)
        count_assignment= assignment['total']

        cursor.execute("""SELECT `INSTITUTION_USER_ID` FROM 
            `institution_user_credential_master` WHERE `INSTITUTION_ID` =%s AND 
            `INSTITUTION_USER_ROLE` LIKE 'TA'""",(institution_id))
        
        teacher_id = cursor.fetchall()
        details = []
        for i in range(len(teacher_id)):
            details.append(teacher_id[i]['INSTITUTION_USER_ID'])
        details = tuple(details)
        nextcursor.execute("""SELECT count(`test_id`)as total  FROM `class_test` where
            `teacher_id` in (%s)""",format(details))

        classtest = nextcursor.fetchone()
        print(classtest)
        count_classtest= classtest['total']

        libcursor.execute("""SELECT count(`liveclass_id`)as total FROM `liveclass_mapping`
         where `institution_id`=%s""",(institution_id))
        
        liveclass= libcursor.fetchone()
        count_liveclass= liveclass['total']

        cursor.execute("""SELECT `INSTITUTION_USER_ID` FROM 
            `institution_user_credential_master` WHERE `INSTITUTION_ID` =%s AND 
            `INSTITUTION_USER_ROLE` LIKE 'TA'""",(institution_id))
        
        teacher_id = cursor.fetchall()
        details = []
        for i in range(len(teacher_id)):
            details.append(teacher_id[i]['INSTITUTION_USER_ID'])
        details = tuple(details)
        libcursor.execute("""SELECT count(`content_id`)as total FROM `content_library` 
            WHERE `teacher_id` in (%s)""",format(details))

        content_library= libcursor.fetchone()
        count_content_library= content_library['total']

        cursor.execute("""SELECT count(`id`)as total FROM 
          `activity_institution_transaction_details` WHERE `institution_id`=%s""",(institution_id))

        fees_transaction = cursor.fetchone()
        count_fees_transaction= fees_transaction['total']

        cursor.execute("""SELECT count(`User_Behaviour_Id`)as total FROM `user_behaviour`
           WHERE `User_Id` in(SELECT `INSTITUTION_USER_ID` FROM 
           `institution_user_credential_master` WHERE `INSTITUTION_ID` =%s AND 
          `INSTITUTION_USER_ROLE` LIKE 'S1') and `Content_Detail_Id`!=0""",(institution_id))

        seen_videos = cursor.fetchone()
        count_seen_videos= seen_videos['total']
        
        nextcursor.close()
        libcursor.close()
        cursor.close()
        return ({"attributes": {"status_desc": "Number Of Used Module",
                                "status": "success"
                                },
                 "responseList": {
                                   "used_attendance": count_attendance,
                                  
                                   "used_contest": count_contest,

                                   # "used_assignment": count_assignment,

                                   # "used_classtest": count_classtest,

                                   "used_liveclass": count_liveclass,

                                   "used_contentLibrary": count_content_library,

                                   "used_feesModule" :count_fees_transaction,

                                   "used_mysyllabus" : count_seen_videos

                                   },

                }), status.HTTP_200_OK
#------------------count-all-module-used-by-ins-id---------------------------------#

#---------------------------------previous-registration-count--------------------------#

@name_space.route("/numberOfPreviousRegistrationByInstitutionId/<int:institution_id>")
class numberOfPreviousRegistrationByInstitutionId(Resource):
    def get(self,institution_id):
        connection = mysql_connection()
        cursor = connection.cursor()

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID_TEACHER`) as total FROM 
            `teacher_dtls` WHERE `INSTITUTION_USER_ID_TEACHER` in(SELECT 
            `INSTITUTION_USER_ID` FROM `institution_user_credential` where 
            date(`LAST_UPDATE_TIMESTAMP`) = DATE(NOW()) + INTERVAL -1 DAY and 
            `INSTITUTION_ID` =%s)""",(institution_id))
        teacher_yesterday = cursor.fetchone()
        count_yes_tea = teacher_yesterday['total']
        # print(total)

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID_TEACHER`) as total FROM 
            `teacher_dtls` WHERE `INSTITUTION_USER_ID_TEACHER` in(SELECT 
            `INSTITUTION_USER_ID` FROM `institution_user_credential` where 
            date(`LAST_UPDATE_TIMESTAMP`) >= DATE(NOW()) + INTERVAL -7 DAY AND 
            date(`LAST_UPDATE_TIMESTAMP`) < DATE(NOW()) + INTERVAL 0 DAY and 
            `INSTITUTION_ID` =%s)""",(institution_id))

        teacher_last7 = cursor.fetchone()
        count_tea_last7 = teacher_last7['total']

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID_TEACHER`) as total FROM 
            `teacher_dtls` WHERE `INSTITUTION_USER_ID_TEACHER` in(SELECT 
            `INSTITUTION_USER_ID` FROM `institution_user_credential` where 
            date(`LAST_UPDATE_TIMESTAMP`) >= DATE(NOW()) + INTERVAL -30 DAY AND 
            date(`LAST_UPDATE_TIMESTAMP`) < DATE(NOW()) + INTERVAL 0 DAY and 
            `INSTITUTION_ID` =%s)""",(institution_id))

        teacher_last30 = cursor.fetchone()
        count_tea_last30 = teacher_last30['total']

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID_STUDENT`)as total FROM 
            `student_dtls` WHERE `INSTITUTION_USER_ID_STUDENT` in(SELECT 
            `INSTITUTION_USER_ID` FROM `institution_user_credential` where 
            date(`LAST_UPDATE_TIMESTAMP`)= DATE(NOW()) + INTERVAL -1 DAY and 
            `INSTITUTION_ID` =%s)""",(institution_id))
        student_yesterday = cursor.fetchone()
        count_yes_stu= student_yesterday['total']

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID_STUDENT`)as total FROM 
            `student_dtls` WHERE `INSTITUTION_USER_ID_STUDENT` in(SELECT 
            `INSTITUTION_USER_ID` FROM `institution_user_credential` where 
            date(`LAST_UPDATE_TIMESTAMP`)>= DATE(NOW()) + INTERVAL -7 DAY AND 
            date(`LAST_UPDATE_TIMESTAMP`) < DATE(NOW()) + INTERVAL 0 DAY and 
            `INSTITUTION_ID` =%s)""",(institution_id))
        student_last7 = cursor.fetchone()
        count_stu_last7= student_last7['total']

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID_STUDENT`)as total FROM 
            `student_dtls` WHERE `INSTITUTION_USER_ID_STUDENT` in(SELECT 
            `INSTITUTION_USER_ID` FROM `institution_user_credential` where 
            date(`LAST_UPDATE_TIMESTAMP`)>= DATE(NOW()) + INTERVAL -30 DAY AND 
            date(`LAST_UPDATE_TIMESTAMP`) < DATE(NOW()) + INTERVAL 0 DAY and 
            `INSTITUTION_ID` =%s)""",(institution_id))

        student_last30 = cursor.fetchone()
        count_stu_last30= student_last30['total']

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID_GUARDIAN`)as total FROM 
            `guardian_dtls` WHERE `INSTITUTION_USER_ID_STUDENT` in(SELECT 
            `INSTITUTION_USER_ID` FROM `institution_user_credential` where 
            date(`LAST_UPDATE_TIMESTAMP`)=DATE(NOW()) + INTERVAL -1 DAY and 
            `INSTITUTION_ID` =%s)""",(institution_id))
        parent_yesterday = cursor.fetchone()
        count_yes_par= parent_yesterday['total']

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID_GUARDIAN`)as total FROM 
            `guardian_dtls` WHERE `INSTITUTION_USER_ID_STUDENT` in(SELECT 
            `INSTITUTION_USER_ID` FROM `institution_user_credential` where 
            date(`LAST_UPDATE_TIMESTAMP`)>= DATE(NOW()) + INTERVAL -7 DAY AND 
            date(`LAST_UPDATE_TIMESTAMP`) < DATE(NOW()) + INTERVAL 0 DAY and 
            `INSTITUTION_ID` =%s)""",(institution_id))

        parent_last7 = cursor.fetchone()
        count_par_last7= parent_last7['total']

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID_GUARDIAN`)as total FROM 
            `guardian_dtls` WHERE `INSTITUTION_USER_ID_STUDENT` in(SELECT 
            `INSTITUTION_USER_ID` FROM `institution_user_credential` where 
            date(`LAST_UPDATE_TIMESTAMP`)>= DATE(NOW()) + INTERVAL -30 DAY AND 
            date(`LAST_UPDATE_TIMESTAMP`) < DATE(NOW()) + INTERVAL 0 DAY and 
            `INSTITUTION_ID` =%s)""",(institution_id))

        parent_last30= cursor.fetchone()
        count_par_last30= parent_last30['total']

        cursor.execute("""SELECT count(`INSTITUTION_USER_ID`)as total FROM 
            `institution_user_credential_master` WHERE `INSTITUTION_USER_ID` Not in(SELECT 
            distinct(`INSTITUTION_USER_ID`) FROM `institution_user_tracking`) and 
            `INSTITUTION_ID` =%s""",(institution_id))

        notUsedUser= cursor.fetchone()
        count_notUsedUser= notUsedUser['total']

        cursor.close()
        return ({"attributes": {"status_desc": "Registration Details.",
                                "status": "success"
                                },
                "responseList": {
                                   "previous_teacher": count_yes_tea,
                                  
                                   "teacher_last7days": count_tea_last7,

                                   "teacher_last30days": count_tea_last30,

                                   "previous_student": count_yes_stu,

                                   "student_last7days": count_stu_last7,

                                   "student_last30days": count_stu_last30,

                                   "previous_parent": count_yes_par,

                                   "parent_last7days": count_par_last7,

                                   "parent_last30days": count_par_last30,

                                   "notUsedUser" : count_notUsedUser
                                  },
                }), status.HTTP_200_OK
        
#---------------------------------previous-registration-count--------------------------#

#---------------------------------registered-but-not-used-app-------------------------------#
@name_space.route("/notUsedUserDtlsByInstitutionId/<int:institution_id>")
class notUsedUserDtlsByInstitutionId(Resource):
    def get(self,institution_id):
        connection = mysql_connection()
        cursor = connection.cursor()

        cursor.execute("""SELECT institution_dtls.`Institution_ID`,
            institution_user_credential.`INSTITUTION_USER_ID`, institution_dtls.
            `INSTITUTION_NAME`,`INSTITUTION_USER_ROLE`,concat(`FIRST_NAME`,' ',`LAST_NAME`) 
            as name,`INSTITUTION_USER_NAME`, `INSTITUTION_USER_PASSWORD`,
            `PRIMARY_CONTACT_NUMBER`,institution_user_credential.`IMAGE_URL`, 
            institution_user_credential_master.`INSTITUTION_NAME` as school_name,
            `institution_user_credential`.`LAST_UPDATE_TIMESTAMP` FROM 
            `institution_user_credential` inner join `institution_user_credential_master` 
            on institution_user_credential.`INSTITUTION_USER_ID`=
            institution_user_credential_master.`INSTITUTION_USER_ID` 
            INNER JOIN `institution_dtls` on institution_user_credential_master.
            `INSTITUTION_ID`=institution_dtls.`INSTITUTION_ID` where 
            institution_user_credential_master.`INSTITUTION_USER_ID` not in(SELECT 
            distinct(`INSTITUTION_USER_ID`) FROM `institution_user_tracking`) and 
            institution_user_credential_master.`INSTITUTION_ID` =%s""",(institution_id))
        
        notUsedUserdtls = cursor.fetchall()
        for i in range(len(notUsedUserdtls)):
            notUsedUserdtls[i]['LAST_UPDATE_TIMESTAMP'] = notUsedUserdtls[i]['LAST_UPDATE_TIMESTAMP'].isoformat()
        cursor.close()
        return ({"attributes": {"status_desc": "user Details",
                                "status": "success"
                                },
                 "responseList": notUsedUserdtls
                }), status.HTTP_200_OK
#---------------------------------registered-but-not-used-app-------------------------------#

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
