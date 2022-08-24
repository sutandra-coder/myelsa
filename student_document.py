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
                                    db='creamson_logindb',
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)
    return connection

def connect_lablang():
    connection = pymysql.connect(host='creamsonservices.com',
                                 user='creamson_langlab',
                                 password='Langlab@123',
                                 db='creamson_user_library',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection'''

def mysql_connection():
    connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
                                    user='admin',
                                    password='cbdHoRPQPRfTdC0uSPLt',
                                    db='creamson_logindb',
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)
    return connection

def connect_lablang():
    connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
                                 user='admin',
                                 password='cbdHoRPQPRfTdC0uSPLt',
                                 db='creamson_user_library',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection
#----------------------database-connection---------------------#

student_document_details = Blueprint('student_document_details_api', __name__)
api = Api(student_document_details,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('Studentdocument',description='Student Document')

#-----------------------student-document-model-----------------------#

studentdocument = api.model('studentdocument', {
    "institution_user_id":fields.Integer(),
    "document_label":fields.String(), 
    "document_filepath":fields.String(),
    "document_filetype":fields.String(),
    "last_upadte_id":fields.Integer()
    })

#-----------------------student-document-model------------------------------------#

#-----------------------student-document-update-model--------------------------------------#
update_studentdocument = api.model('update_studentdocument', {
    "institution_user_id":fields.Integer(),
    "document_label":fields.String(), 
    "document_filepath":fields.String(),
    "document_filetype":fields.String(),
    "last_upadte_id":fields.Integer()
})
#-----------------------student-document-update-model--------------------------------------#

#-----------------------student-dtls-update-model-------------------------------#
update_studentdtls = api.model('update_studentdtls', {
    "Course_applied_for":fields.String(),
    "Social_category":fields.String(),
    "Physical_status":fields.String(),
    "Religion":fields.String(),
    "Mother_tongue":fields.String(),
    "DateOfBirth": fields.String(),
    "EmailId": fields.String(),
    "FirstName": fields.String(),
    "InstitutionUserName": fields.String(),
    "InstitutionUserPassword": fields.String(),
    "LastName": fields.String(),
    "MiddleName": fields.String(),
    "PrimaryContactNumber": fields.String()
    
})
#-----------------------student-dtls-update-model-------------------------------#

#-----------------------nios-student-registration-model---------------------------#

address=api.model('address', {
    "ADDRESS_TYPE":fields.String(),
    "DISTRICT":fields.String(),
    "PO":fields.String(),
    "LANDMARK":fields.String(),
    "nios_state": fields.String(),
    "nios_streetAddress": fields.String(),
    "nios_city": fields.String(),
    "nios_pincode": fields.String()
    })

subject=api.model('subject', {
    "SUBJECT":fields.String(),
    "SUBJECT_CODE":fields.String(),
    })

personalDtls = api.model('personalDtlsDto', {
    "course_applied_for":fields.String(),
    "medium_of_study":fields.String(),
    "session":fields.String(),
    "aadhaar_no":fields.String(),
    "mothers_name":fields.String(),
    "social_category":fields.String(),
    "physical_status":fields.String(),
    "religion":fields.String(),
    "previous_nios_candidate":fields.String(),
    "prev_nios_ref_number":fields.String(),
    "prev_nios_enroll_no":fields.String(),
    "study_centre_area_preference":fields.String(),
    "mother_tongue":fields.String(),
    "father_qualification":fields.String(),
    "mother_qualification":fields.String(),
    "PASS_OUT_YEAR":fields.Integer(),
    "ROLL_NO":fields.Integer(),
    "PERCENTAGE":fields.Integer(),
    "REFERENCE_MEDIUM":fields.String(),
    "address_details":fields.List(fields.Nested(address)),
    "subject_details":fields.List(fields.Nested(subject))
    # "SUBJECT":fields.String(),
    # "SUBJECT_CODE":fields.String(),
    # "ADDRESS_TYPE":fields.String(),
    # "DISTRICT":fields.String(),
    # "PO":fields.String(),
    # "LANDMARK":fields.String()
    
    })
addUser = api.model('addUserDto', {
    "city": fields.String(),
    "dateOfBirth": fields.String(),
    "emailId": fields.String(),
    "firstName": fields.String(),
    "gender": fields.String(),
    "institutionUserName": fields.String(),
    "institutionUserPassword": fields.String(),
    "institutionUserRole": fields.String(),
    "institutionUserStatus": fields.String(),
    "lastName": fields.String(),
    "middleName": fields.String(),
    "pincode": fields.String(),
    "primaryContactNumber": fields.String(),
    "secondaryContactNumber": fields.String(),
    "state": fields.String(),
    "streetAddress": fields.String(),
    "userEndDate": fields.String(),
    "userEnrollDate": fields.String(),
    "userTaxId": fields.String(),
    "userUniqueId": fields.String(),
    "board": fields.String(),
    "studentname": fields.String(),
    "class": fields.String(),
    "institutionName": fields.String(),
    "institutionId": fields.Integer(),
    "licenseKey": fields.String(),
    "fathers_Name":fields.String(),
    "personal_details":fields.Nested(personalDtls)
    })
#-----------------------nios-student-registration-model---------------------------#

#-----------------------post-student-document---------------------------------------#

@name_space.route("/insertStudent_document_details")
class insertStudent_document_details(Resource):
    @api.expect(studentdocument)
    def post(self):
        details = request.get_json()
        connection = mysql_connection()
        cursor = connection.cursor()
        # currentDate = date.today().strftime("%d%b%y")
        
        institution_user_id = details['institution_user_id']
        document_label = details['document_label']
        document_filepath = details['document_filepath']
        document_filetype = details['document_filetype']
        last_upadte_id = details['last_upadte_id']


        student_document_query = ("""INSERT INTO `student_document`(`institution_user_id`,
         `document_label`, `document_filepath`, `document_filetype`,
          `last_upadte_id`) VALUES (%s,%s,%s,%s,%s)""")
        student_document_data = (institution_user_id,document_label,document_filepath,
            document_filetype,last_upadte_id)

        documentdata = cursor.execute(student_document_query,student_document_data)

        url = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/app_notify/AppCommunicationAPI/appMessage'
        headers = {'Content-type':'application/json', 'Accept':'application/json'}
        
        if institution_user_id == last_upadte_id :

            cursor.execute("""SELECT `INSTITUTION_USER_ID`,concat(`FIRST_NAME`,' ',`LAST_NAME`)as
                fullname FROM `institution_user_credential` WHERE 
                `INSTITUTION_USER_ID` =%s""",(institution_user_id))

            userList = cursor.fetchone()
            if userList:
                fullname =userList.get('fullname')
                # print(fullname)

            cursor.execute("""SELECT `INSTITUTION_ID` FROM `institution_user_credential_master` WHERE
                 `INSTITUTION_USER_ID` =%s AND `INSTITUTION_ID`!=1 and 
                 `INSTITUTION_USER_ROLE` LIKE 'S1'""",(institution_user_id))
            institution = cursor.fetchone()
            institutionid =institution.get('INSTITUTION_ID')
            # print(institutionid)

            cursor.execute("""SELECT `INSTITUTION_USER_ID` FROM 
                `institution_user_credential_master` WHERE `INSTITUTION_ID` =%s AND 
                `INSTITUTION_USER_ROLE` LIKE 'TA'""",(institutionid))
            teacher_id = cursor.fetchall()
            for j in range(len(teacher_id)):
                teacherid = teacher_id[j]['INSTITUTION_USER_ID']
                print(teacherid)
                cursor.execute("""SELECT `INSTITUTION_USER_ID`,concat(`FIRST_NAME`,' ',`LAST_NAME`)as
                    teachername FROM `institution_user_credential` WHERE 
                    `INSTITUTION_USER_ID` =%s""",(teacherid))

                teacherList = cursor.fetchone()
                if teacherList != None:
                    teachername =teacherList.get('teachername')
                    # print(teachername)
            

            
                data ={
                        "appParams": {},
                        "userId": teacherid,
                        "sourceapp": "SDINT00T",
                        "toMail": "",
                        "role": "T1",
                        "toNumber": 0,
                        "mailParams": {"teachername":teachername,
                                       "fullname":fullname}
                    }
                # print(data)

                response = requests.post(url, data=json.dumps(data), headers=headers).json()
                # print(response)
        else:
            cursor.execute("""SELECT `INSTITUTION_USER_ID`,concat(`FIRST_NAME`,' ',`LAST_NAME`)as
                fullname FROM `institution_user_credential` WHERE 
                `INSTITUTION_USER_ID` =%s""",(institution_user_id))

            userList = cursor.fetchone()

            cursor.execute("""SELECT `INSTITUTION_USER_ID`,concat(`FIRST_NAME`,' ',`LAST_NAME`)as
                teachername FROM `institution_user_credential` WHERE 
                `INSTITUTION_USER_ID` =%s""",(last_upadte_id))

            username = cursor.fetchone()
            teachername =username.get('teachername')
            # print(teachername)
            if userList:
                fullname =userList.get('fullname')
                # print(fullname)
                data ={
                        "appParams": {},
                        "userId": institution_user_id,
                        "sourceapp": "SDINT00S",
                        "toMail": "",
                        "role": "S1",
                        "toNumber": 0,
                        "mailParams": {"fullname":fullname,
                                       "teachername":teachername}
                    }
                

                response = requests.post(url, data=json.dumps(data), headers=headers).json()
                # print(response)
        connection.commit()
        if documentdata:
            return ({"attributes": {"status_desc": "Added Student Document",
                                    "status": "success"
                                    }
                     }), status.HTTP_200_OK

#-----------------------post-student-document---------------------------------------#

#-----------------------get-student-document---------------------------------------#
@name_space.route("/getStudentDocumnetStudentId/<int:student_id>")
class getStudentDocumnetStudentId(Resource):
    def get(self,student_id):
        connection = mysql_connection()
        cursor = connection.cursor()

        cursor.execute("""SELECT `student_document_id`,`institution_user_id`,
            `document_label`,`document_filepath`,`document_filetype`,
            `last_upadte_id`,`last_update_ts` FROM `student_document` WHERE 
            `institution_user_id`=%s""",(student_id))
        get_documnet = cursor.fetchall()
        for i in range(len(get_documnet)):
            get_documnet[i]['last_update_ts'] = get_documnet[i]['last_update_ts'].isoformat()
        
        return ({"attributes": {"status_desc": "Student Document Details",
                                "status": "success"
                                    },
                "responseList":get_documnet}), status.HTTP_200_OK
#-----------------------get-student-document---------------------------------------#

#-----------------------update-student-document---------------------------------------#
@name_space.route("/updateStudentDocumentByDocumentID/<int:student_document_id>")
class updateStudentDocumentByDocumentID(Resource):
    @api.expect(update_studentdocument)
    def put(self,student_document_id):
        details = request.get_json()
        connection = mysql_connection()
        cursor = connection.cursor()
        
        Institution_user_id = details.get('institution_user_id')
        Document_label = details.get('document_label')
        Document_filepath = details.get('document_filepath')
        Document_filetype = details.get('document_filetype')
        Last_upadte_id = details.get('last_upadte_id')

        cursor.execute("""SELECT `institution_user_id`, `document_label`, 
            `document_filepath`, `document_filetype`,  `last_upadte_id` FROM 
            `student_document` WHERE `student_document_id`=%s""",(student_document_id))
        student_docdtls = cursor.fetchone()
        print(student_docdtls)

        if student_docdtls:
            if not Institution_user_id:
                Institution_user_id = student_docdtls.get('institution_user_id')
                print(Institution_user_id)
            if not Document_label:
                Document_label = student_docdtls.get('document_label')
                print(Document_label)
            if not Document_filepath:
                Document_filepath = student_docdtls.get('document_filepath')
                print(Document_filepath)
            if not Document_filetype:
                Document_filetype = student_docdtls.get('document_filetype')
                print(Document_filetype)
            if not Last_upadte_id:
                Last_upadte_id = student_docdtls.get('last_upadte_id')
                print(Last_upadte_id)

        update_student_document = ("""UPDATE `student_document` SET `institution_user_id`=%s,
            `document_label`= %s,`document_filepath`= %s,`document_filetype`= %s,
            `last_upadte_id`= %s WHERE `student_document_id`= %s""")
        student_document_data = (Institution_user_id,Document_label,Document_filepath,
            Document_filetype,Last_upadte_id,student_document_id)
        cursor.execute(update_student_document,student_document_data)

        url = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/app_notify/AppCommunicationAPI/appMessage'
        headers = {'Content-type':'application/json', 'Accept':'application/json'}
        if Institution_user_id == Last_upadte_id :

            cursor.execute("""SELECT `INSTITUTION_USER_ID`,concat(`FIRST_NAME`,' ',`LAST_NAME`)as
                fullname FROM `institution_user_credential` WHERE 
                `INSTITUTION_USER_ID` =%s""",(Institution_user_id))

            userList = cursor.fetchone()
            if userList:
                fullname =userList.get('fullname')
                # print(fullname)

            cursor.execute("""SELECT `INSTITUTION_ID` FROM `institution_user_credential_master` WHERE
                 `INSTITUTION_USER_ID` =%s AND `INSTITUTION_ID`!=1 and 
                 `INSTITUTION_USER_ROLE` LIKE 'S1'""",(Institution_user_id))
            institution = cursor.fetchone()
            institutionid =institution.get('INSTITUTION_ID')
            # print(institutionid)

            cursor.execute("""SELECT `INSTITUTION_USER_ID` FROM 
                `institution_user_credential_master` WHERE `INSTITUTION_ID` =%s AND 
                `INSTITUTION_USER_ROLE` LIKE 'TA'""",(institutionid))
            teacher_id = cursor.fetchall()
            for j in range(len(teacher_id)):
                teacherid = teacher_id[j]['INSTITUTION_USER_ID']
                print(teacherid)
                cursor.execute("""SELECT `INSTITUTION_USER_ID`,concat(`FIRST_NAME`,' ',`LAST_NAME`)as
                    teachername FROM `institution_user_credential` WHERE 
                    `INSTITUTION_USER_ID` =%s""",(teacherid))

                teacherList = cursor.fetchone()
                if teacherList != None:
                    teachername =teacherList.get('teachername')
                    # print(teachername)
            

            
                data ={
                        "appParams": {},
                        "userId": teacherid,
                        "sourceapp": "SDUPT00T",
                        "toMail": "",
                        "role": "T1",
                        "toNumber": 0,
                        "mailParams": {"teachername":teachername,
                                       "fullname":fullname}
                    }
                # print(data)

                response = requests.post(url, data=json.dumps(data), headers=headers).json()
                # print(response)
        else:
            cursor.execute("""SELECT `INSTITUTION_USER_ID`,concat(`FIRST_NAME`,' ',`LAST_NAME`)as
                fullname FROM `institution_user_credential` WHERE 
                `INSTITUTION_USER_ID` =%s""",(Institution_user_id))

            userList = cursor.fetchone()

            cursor.execute("""SELECT `INSTITUTION_USER_ID`,concat(`FIRST_NAME`,' ',`LAST_NAME`)as
                teachername FROM `institution_user_credential` WHERE 
                `INSTITUTION_USER_ID` =%s""",(Last_upadte_id))

            username = cursor.fetchone()
            teachername =username.get('teachername')
            # print(teachername)
            if userList:
                fullname =userList.get('fullname')
                # print(fullname)
                data ={
                        "appParams": {},
                        "userId": Institution_user_id,
                        "sourceapp": "SDUPT00S",
                        "toMail": "",
                        "role": "S1",
                        "toNumber": 0,
                        "mailParams": {"fullname":fullname,
                                       "teachername":teachername}
                    }
                

                response = requests.post(url, data=json.dumps(data), headers=headers).json()
                # print(response)
        return ({"attributes": {"status_desc": "Student Document Update Details.",
                            "status": "success"
                            },
                            "responseList":details}), status.HTTP_200_OK
#-----------------------update-student-document---------------------------------------#

#-----------------------nios-student-deatils-by-ins-id---------------------------------------#
@name_space.route("/getStudentRestrationDtlsInstitutionId/<int:institution_id>")
class getStudentRestrationDtlsInstitutionId(Resource):
    def get(self,institution_id):
        connection = mysql_connection()
        cursor = connection.cursor()

        cursor.execute("""SELECT institution_user_personal_details.`institution_id`,
            institution_user_personal_details.`institution_user_id`,
        `course_applied_for`,`medium_of_study`,`session`,
        concat(`FIRST_NAME`,' ',`LAST_NAME`)as name,`PRIMARY_CONTACT_NUMBER`,`father_name`,
        `mothers_name`,`social_category`,`physical_status`,`religion`,`prev_nios_enroll_no`,
        `previous_nios_candidate`,`prev_nios_ref_number`,`study_centre_area_preference`,
        `mother_tongue`,`father_qualification`, `mother_qualification`,
        `CLASS`,`BOARD`,`PASS_OUT_YEAR`,`ROLL_NO`,`PERCENTAGE`,`REFERENCE_MEDIUM`,
        `LAST_UPDATE_TIMESTAMP` 
        FROM `institution_user_personal_details` inner join `academic_detail` on
        institution_user_personal_details.`institution_user_id`= academic_detail.`institution_user_id`
        inner join `student_reference` on
        institution_user_personal_details.`institution_user_id`= student_reference.`institution_user_id`
        WHERE institution_user_personal_details.`institution_id`= %s""",
        (institution_id))
        get_studentdtls = cursor.fetchall()

        for i in range(len(get_studentdtls)):
            get_studentdtls[i]['LAST_UPDATE_TIMESTAMP'] = get_studentdtls[i]['LAST_UPDATE_TIMESTAMP'].isoformat()
            user_id = get_studentdtls[i]['institution_user_id']

            cursor.execute("""SELECT `SUBJECT_ID`,`INSTITUTION_ID`,`SUBJECT`,`SUBJECT_CODE`
             FROM `student_subject` WHERE `INSTITUTION_ID`=%s and
             `INSTITUTION_USER_ID`=%s""",(institution_id,user_id))
            get_subjectdtls = cursor.fetchall()

            if get_subjectdtls:
                get_studentdtls[i]['subject'] = get_subjectdtls
            
            else:
                get_studentdtls[i]['subject'] =[]
                
            cursor.execute("""SELECT `ADDRESS_TYPE`,`ADDRESS_LINE`,`CITY`,`DISTRICT`,`PIN`,
                `PO`,`STATE`,`LANDMARK` FROM `nios_student_address` WHERE 
                `INSTITUTION_ID`=%s and institution_user_id= %s""",(institution_id,user_id))
            get_addressdtls = cursor.fetchall()
            
            if get_addressdtls:
                get_studentdtls[i]['address'] = get_addressdtls
            
            else:
                get_studentdtls[i]['address'] =[]
        return ({"attributes": {"status_desc": "Student Registration Details",
                                "status": "success"
                                    },
                "responseList":get_studentdtls}), status.HTTP_200_OK
#-----------------------nios-student-deatils-by-ins-id---------------------------------------#

#-----------------------nios-student-deatils-by-user-id---------------------------------------#
@name_space.route("/getStudentRestrationDtlsUserId/<int:uesr_id>")
class getStudentRestrationDtlsUserId(Resource):
    def get(self,uesr_id):
        connection = mysql_connection()
        cursor = connection.cursor()

        cursor.execute("""SELECT institution_user_personal_details.`institution_id`,
            institution_user_personal_details.`institution_user_id`,
        `course_applied_for`,`medium_of_study`,`session`,
        concat(`FIRST_NAME`,' ',`LAST_NAME`)as name,`PRIMARY_CONTACT_NUMBER`,`father_name`,
        `mothers_name`,`social_category`,`physical_status`,`religion`,`prev_nios_enroll_no`,
        `previous_nios_candidate`,`prev_nios_ref_number`,`study_centre_area_preference`,
        `mother_tongue`,`father_qualification`, `mother_qualification`,
        `CLASS`,`BOARD`,`PASS_OUT_YEAR`,`ROLL_NO`,`PERCENTAGE`,`REFERENCE_MEDIUM`,
        `LAST_UPDATE_TIMESTAMP` 
        FROM `institution_user_personal_details` inner join `academic_detail` on
        institution_user_personal_details.`institution_user_id`= academic_detail.`institution_user_id`
        inner join `student_reference` on
        institution_user_personal_details.`institution_user_id`= student_reference.`institution_user_id`
        WHERE institution_user_personal_details.`institution_user_id`= %s""",
        (uesr_id))
        get_studentdtls = cursor.fetchall()

        for i in range(len(get_studentdtls)):
            get_studentdtls[i]['LAST_UPDATE_TIMESTAMP'] = get_studentdtls[i]['LAST_UPDATE_TIMESTAMP'].isoformat()
            
            cursor.execute("""SELECT `SUBJECT_ID`,`INSTITUTION_ID`,`SUBJECT`,`SUBJECT_CODE`
             FROM `student_subject` WHERE `INSTITUTION_USER_ID`=%s""",(uesr_id))
            get_subjectdtls = cursor.fetchall()

            if get_subjectdtls:
                get_studentdtls[i]['subject'] = get_subjectdtls
            
            else:
                get_studentdtls[i]['subject'] =[]
            cursor.execute("""SELECT `ADDRESS_TYPE`,`ADDRESS_LINE`,`CITY`,`DISTRICT`,`PIN`,
                `PO`,`STATE`,`LANDMARK` FROM `nios_student_address` WHERE 
                institution_user_id= %s""",(uesr_id))
            get_addressdtls = cursor.fetchall()
            
            if get_addressdtls:
                get_studentdtls[i]['address'] = get_addressdtls
            
            else:
                get_studentdtls[i]['address'] =[]
        return ({"attributes": {"status_desc": "Student Registration Details",
                                "status": "success"
                                    },
                "responseList":get_studentdtls}), status.HTTP_200_OK
#------------------------nios-student-deatils-by-user-id---------------------------------------#

#-----------------------update-student-dtls----------------------------------------#
@name_space.route("/updateStudentDtlsByStudentID/<int:student_id>")
class updateStudentDtlsByStudentID(Resource):
    @api.expect(update_studentdtls)
    def put(self,student_id):
        details = request.get_json()
        connection = mysql_connection()
        cursor = connection.cursor()
        
        DateOfBirth = details.get('DateOfBirth')
        EmailId = details.get('EmailId')
        FirstName = details.get('FirstName')
        InstitutionUserName = details.get('InstitutionUserName')
        InstitutionUserPassword = details.get('InstitutionUserPassword')
        LastName = details.get('LastName')
        MiddleName = details.get('MiddleName')
        PrimaryContactNumber = details.get('PrimaryContactNumber')
        Social_category = details.get('Social_category')
        Physical_status = details.get('Physical_status')
        Religion = details.get('Religion')
        Mother_tongue= details.get('Mother_tongue')
        Course_applied_for= details.get('Course_applied_for')
        
        cursor.execute("""SELECT `course_applied_for`,`DATE_OF_BIRTH`, `EMAIL_ID`, `FIRST_NAME`, 
            `INSTITUTION_USER_NAME`, `INSTITUTION_USER_PASSWORD`,`LAST_NAME`,
            `MIDDLE_NAME`,`PRIMARY_CONTACT_NUMBER`,`social_category`, `physical_status`,
            `religion`,`mother_tongue` FROM `institution_user_personal_details` where
            `institution_user_id`= %s""",(student_id))
        student_dtls = cursor.fetchone()
        # print(student_dtls)
        if student_dtls:
            
            if not Course_applied_for:
                Course_applied_for = student_dtls.get('course_applied_for')
                # print(Course_applied_for)
            if not DateOfBirth:
                DateOfBirth = student_dtls.get('DATE_OF_BIRTH')
                # print(DateOfBirth)
            if not EmailId:
                EmailId = student_dtls.get('EMAIL_ID')
                # print(EmailId)
            if not FirstName:
                FirstName = student_dtls.get('FIRST_NAME')
                # print(FirstName)
            if not InstitutionUserName:
                InstitutionUserName = student_dtls.get('INSTITUTION_USER_NAME')
                # print(InstitutionUserName)
            if not InstitutionUserPassword:
                InstitutionUserPassword = student_dtls.get('INSTITUTION_USER_PASSWORD')
                # print(InstitutionUserPassword)
            if not LastName:
                LastName = student_dtls.get('LAST_NAME')
                # print(LastName)
            if not MiddleName:
                MiddleName = student_dtls.get('MIDDLE_NAME')
                # print(MiddleName)
            if not PrimaryContactNumber:
                PrimaryContactNumber = student_dtls.get('PRIMARY_CONTACT_NUMBER')
                # print(PrimaryContactNumber)
            if not Social_category:
                Social_category = student_dtls.get('social_category')
                # print(Social_category)
            if not Physical_status:
                Physical_status = student_dtls.get('physical_status')
                # print(Physical_status)
            if not Religion:
                Religion = student_dtls.get('religion')
                # print(Religion)
            if not Mother_tongue:
                Mother_tongue= student_dtls.get('mother_tongue')
                # print(Mother_tongue)

        update_student_document = ("""UPDATE `institution_user_personal_details` SET 
            `course_applied_for`= %s,`DATE_OF_BIRTH`= %s,
            `EMAIL_ID`= %s,`FIRST_NAME`= %s,`INSTITUTION_USER_NAME`= %s,
            `INSTITUTION_USER_PASSWORD`= %s,`LAST_NAME`= %s,`MIDDLE_NAME`= %s,
            `PRIMARY_CONTACT_NUMBER`= %s,`social_category`= %s,`physical_status`= %s,
            `religion`= %s,`mother_tongue`= %s where `institution_user_id`= %s""")
        student_document_data = (Course_applied_for,DateOfBirth,EmailId ,
            FirstName,InstitutionUserName,InstitutionUserPassword,LastName,MiddleName,
            PrimaryContactNumber,Social_category,Physical_status,Religion,Mother_tongue,student_id)

        updatedata = cursor.execute(update_student_document,student_document_data)
        return ({"attributes": {"status_desc": "Student Document Update Details.",
                            "status": "success"
                            },
                            "responseList":details}), status.HTTP_200_OK

#-----------------------update-student-dtls---------------------------------------#

#-----------------------nios-student-registration---------------------------------------#
@name_space.route("/niosStudentRegistration")
class niosStudentRegistration(Resource):
    @api.expect(addUser)
    def post(self):

        details = request.get_json()
        r = {}
        connection = mysql_connection()
        cursor = connection.cursor()
        
        personal_details = details['personal_details']
        address_details = personal_details['address_details']
        subject_details = personal_details['subject_details']

        add_user = details
        add_user.pop('personal_details',None)
        # add_user.pop('address_details',None)
        
        city = details.get('city')
        
        dateOfBirth = details.get('dateOfBirth',None)
        if not dateOfBirth:
            dateOfBirth = None
        emailId = details.get('emailId')
        firstName = details.get('firstName')
        gender = details.get('gender')
        institutionUserName = details.get('institutionUserName')
        institutionUserPassword = details.get('institutionUserPassword')
        institutionUserRole = details.get('institutionUserRole')
        institutionUserStatus = details.get('institutionUserStatus')
        lastName = details.get('lastName')
        middleName = details.get('middleName')
        pincode = details.get('pincode')
        primaryContactNumber = details.get('primaryContactNumber')
        secondaryContactNumber = details.get('secondaryContactNumber')
        state = details.get('state')
        streetAddress = details.get('streetAddress')
        userEndDate = details.get('userEndDate')
        userEnrollDate = details.get('userEnrollDate')
        userTaxId = details.get('userTaxId')
        userUniqueId = details.get('userUniqueId')
        board = details.get('board')
        studentname = details.get('studentname')
        u_class = details.get('class')
        institutionName = details.get('institutionName')
        institutionId = details.get('institutionId')
        licenseKey = details.get('licenseKey')
        fathers_Name = details.get('fathers_Name')
        course_applied_for = personal_details.get('course_applied_for')
        medium_of_study = personal_details.get('medium_of_study')
        mothers_name = personal_details.get('mothers_name')
        session = personal_details.get('session')
        aadhaar_no = personal_details.get('aadhaar_no') 
        social_category = personal_details.get('social_category')
        physical_status = personal_details.get('physical_status')
        religion = personal_details.get('religion')
        previous_nios_candidate = personal_details.get('previous_nios_candidate')
        prev_nios_ref_number = personal_details.get('prev_nios_ref_number')
        prev_nios_enroll_no= personal_details.get('prev_nios_enroll_no')
        study_centre_area_preference= personal_details.get('study_centre_area_preference')
        mother_tongue= personal_details.get('mother_tongue')
        father_qualification= personal_details.get('father_qualification')
        mother_qualification= personal_details.get('mother_qualification')
        PASS_OUT_YEAR= personal_details.get('PASS_OUT_YEAR')
        ROLL_NO= personal_details.get('ROLL_NO')
        PERCENTAGE= personal_details.get('PERCENTAGE')
        # ADDRESS_TYPE= personal_details.get('ADDRESS_TYPE')
        # DISTRICT= personal_details.get('DISTRICT')
        # PO= personal_details.get('PO')
        # LANDMARK= personal_details.get('LANDMARK')
        REFERENCE_MEDIUM= personal_details.get('REFERENCE_MEDIUM')

        cursor.execute("""SELECT `institution_user_id` FROM `institution_user_personal_details` 
            WHERE `INSTITUTION_USER_NAME` =%s""",(institutionUserName))
        user_id = cursor.fetchone()
        print(user_id)
        if not user_id:
            details_insert_query = ("""INSERT INTO `institution_user_personal_details`(`course_applied_for`, 
                `medium_of_study`, `session`,`DATE_OF_BIRTH`, `EMAIL_ID`, `FIRST_NAME`,
                 `GENDER`,`INSTITUTION_USER_NAME`, `INSTITUTION_USER_PASSWORD`,
                 `LAST_NAME`, `MIDDLE_NAME`, `PRIMARY_CONTACT_NUMBER`, 
                 `SECONDARY_CONTACT_NUMBER`,`aadhaar_no`,`USER_TAX_ID`, `USER_UNIQUE_ID`,
                 `father_name`, `mothers_name`,
                 `social_category`, `physical_status`, `religion`, 
                 `previous_nios_candidate`, `prev_nios_ref_number`, `prev_nios_enroll_no`,
                `study_centre_area_preference`, `mother_tongue`, `father_qualification`,
                `mother_qualification`) 
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,%s,%s)""")
            print(dateOfBirth)
            insert_data = (course_applied_for,medium_of_study,session,
                dateOfBirth,emailId,firstName,gender,institutionUserName,
                institutionUserPassword,lastName,middleName,primaryContactNumber,
                secondaryContactNumber,aadhaar_no,userTaxId,userUniqueId,
                fathers_Name,mothers_name,
                social_category,physical_status,religion,previous_nios_candidate,
                prev_nios_ref_number,prev_nios_enroll_no,study_centre_area_preference,
                mother_tongue,father_qualification,mother_qualification)
            cursor.execute(details_insert_query,insert_data)

            post_url = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/myelsa_registration/myELSARegistration/registration'
            payload = json.dumps(add_user)
            headers = {'Content-type':'application/json', 'Accept':'application/json'}
            post_response = requests.post(post_url, data=payload, headers=headers)
            r = post_response.json()
            print(r)
            res_user_id = r['responseList']['user_id']
            idx = cursor.lastrowid

            update_peronalDtls = ("""UPDATE `institution_user_personal_details` 
                SET `institution_user_id` = %s where `ID` = %s""")
            update_data = (res_user_id,idx)

            cursor.execute(update_peronalDtls,update_data)

            update_insDtls = ("""UPDATE `institution_user_personal_details` 
                SET `institution_id` = %s where `ID` = %s""")
            update_insdata = (institutionId,idx)

            cursor.execute(update_insDtls,update_insdata)

            academic_insert_query = ("""INSERT INTO `academic_detail`(`INSTITUTION_USER_ID`, 
                `INSTITUTION_ID`, `CLASS`, `BOARD`, `PASS_OUT_YEAR`,`ROLL_NO`, `PERCENTAGE`)
            VALUES (%s,%s,%s,%s,%s,%s,%s)""")
            academic_data = (res_user_id,institutionId,u_class,board,PASS_OUT_YEAR,ROLL_NO,
                PERCENTAGE)
            cursor.execute(academic_insert_query,academic_data)

            for address in address_details:
                ADDRESS_TYPE= address.get('ADDRESS_TYPE')
                DISTRICT= address.get('DISTRICT')
                PO= address.get('PO')
                LANDMARK= address.get('LANDMARK')
                nios_state= address.get('nios_state')
                nios_streetAddress= address.get('nios_streetAddress')
                nios_city= address.get('nios_city')
                nios_pincode= address.get('nios_pincode')
                if nios_streetAddress !='' and nios_streetAddress != None:
                    address_insert_query = ("""INSERT INTO `nios_student_address`
                        (`INSTITUTION_USER_ID`, `INSTITUTION_ID`, `ADDRESS_TYPE`, `ADDRESS_LINE`, 
                        `CITY`, `DISTRICT`, `PIN`, `PO`, `STATE`, `LANDMARK`)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
                    address_data = (res_user_id,institutionId,ADDRESS_TYPE,nios_streetAddress,
                        nios_city,DISTRICT,nios_pincode,PO,nios_state,LANDMARK)
                    cursor.execute(address_insert_query,address_data)

            reference_insert_query = ("""INSERT INTO `student_reference`(`INSTITUTION_USER_ID`,
             `INSTITUTION_ID`, `REFERENCE_MEDIUM`)
             VALUES (%s,%s,%s)""")
            reference_data = (res_user_id,institutionId,REFERENCE_MEDIUM)
            cursor.execute(reference_insert_query,reference_data)

            for subject in subject_details:
                SUBJECT= subject.get('SUBJECT')
                SUBJECT_CODE= subject.get('SUBJECT_CODE')
                if SUBJECT !='' and SUBJECT != None and SUBJECT_CODE !='' and SUBJECT_CODE !=None:
                    subject_insert_query = ("""INSERT INTO `student_subject`(`INSTITUTION_USER_ID`,
                     `INSTITUTION_ID`,`SUBJECT`,`SUBJECT_CODE`)
                     VALUES (%s,%s,%s,%s)""")
                    subject_data = (res_user_id,institutionId,SUBJECT,SUBJECT_CODE)
                    cursor.execute(subject_insert_query,subject_data)   

            connection.commit()
            cursor.close()
            
            return r
        else:
            # print("hi")
            res_user_id = user_id['institution_user_id']
            connection.commit()
            cursor.close()
            return ({"attributes": {"status_desc": "Registration Details",
                                "status": "success"
                                },
                "responseList": {"STATUS": "Exists",
                                "user_id": res_user_id
                                }}), status.HTTP_200_OK

#-----------------------nios-student-registration---------------------------------------#

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)



