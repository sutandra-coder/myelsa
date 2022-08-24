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

'''def mysql_connection():
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
                                 db='creamson_logindb',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection
myelsa_registration = Blueprint('myelsa_registration_api', __name__)
api = Api(myelsa_registration,  title='MyElsa API',
          description='MyElsa API')
name_space = api.namespace('myELSARegistration',
                           description='myELSA Registration')


addUser = api.model('addUserDto', {
	"address": fields.String(),
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
    "fathers_Name":fields.String()
    })

update_userprofile = api.model('update_userprofile', {
    "imageURL": fields.String(),
    "city": fields.String(),
    "dateOfBirth": fields.String(),
    "emailId": fields.String(),
    "firstName": fields.String(),
    "gender": fields.String(),
    "institutionUserName": fields.String(),
    "institutionUserRole": fields.String(),
    "institutionUserId": fields.Integer(),
    "lastName": fields.String(),
    "pincode": fields.String(),
    "primaryContactNumber": fields.String(),
    "state": fields.String(),
    "streetAddress": fields.String(),
    "board": fields.String(),
    "class": fields.String(),
    "institutionName": fields.String(),
    "fathers_Name":fields.String(),
    "institutionName": fields.String(),
    "fathers_Name":fields.String()
    })
#-----------------------------------------------------#

@name_space.route("/registration")
class registration(Resource):
	@api.expect(addUser)
	def post(self):
		details = request.get_json()
		connection = mysql_connection()
		cursor = connection.cursor()
		current_date = date.today()
		userEnrollDate = str(current_date)
		nextyear_date = current_date.replace(year=current_date.year + 1)
		userEndDate = str(nextyear_date)
		add_user = {"addUserDto": {
						"address": "",
						"city": details['city'],
						"dateOfBirth": details['dateOfBirth'],
						"emailId": details['emailId'],
						"firstName": details['firstName'],
						"gender": details['gender'],
						"institutionUserName": details['institutionUserName'],
						"institutionUserPassword": details['institutionUserPassword'],
						"institutionUserRole": details['institutionUserRole'],
						"institutionUserStatus": details['institutionUserStatus'],
						"lastName": details['lastName'],
						"middleName": details['middleName'],
						"pincode": details['pincode'],
						"primaryContactNumber": details['primaryContactNumber'],
						"secondaryContactNumber": details['secondaryContactNumber'],
						"state": details['state'],
						"streetAddress": details['streetAddress'],
						"userEndDate": userEndDate,
						"userEnrollDate": userEnrollDate,
						"userTaxId": details['userTaxId'],
						"userUniqueId": details['userUniqueId'],
						"institutionStudentDtlDtoNew": {
							"board": details['board'],
							"sTUDENTNAME": details['firstName'] + ' ' + details['lastName'],
							"cLASS": details['class'],
							"fathers_Name":details.get('fathers_Name')
							},
						"institutionTeacherDtlDtoNew": {
							"cLASS": "",
							"cLASSTEACHERFLAG": "",
							"iNSTITUTIONID": 0,
							"sEC": "",
							"sUBJECT": "",
							"tEACHERTYPE": ""
							}
						},
					"institutionDto": {
						"institutionName": details['institutionName']
						},
					"validateLicenseDto": {
						"institutionId": details['institutionId'],
						"licenseKey": details['licenseKey']
						}}
		post_url = 'http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com:8080/NewSignUpService/RegistrationService'
		payload = json.dumps(add_user)
		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		post_response = requests.post(post_url, data=payload, headers=headers)
		r = post_response.json()
		cursor.execute("""SELECT `INSTITUTION_USER_ID` FROM `institution_user_credential` 
			WHERE `INSTITUTION_USER_NAME`= %s""",(details['institutionUserName']))
		user_id = cursor.fetchone()
		if user_id:
			r['user_id'] = user_id['INSTITUTION_USER_ID']
		else:
			r['user_id'] = 0
		return ({"attributes": {"status_desc": "Registration Details",
                                "status": "success"
                                },
                 "responseList": r}), status.HTTP_200_OK

#-----------------------------------------------------#
@name_space.route("/UpdateUserProfile")
class UpdateUserProfile(Resource):
    @api.expect(update_userprofile)
    def put(self):
        details = request.get_json()
        connection = mysql_connection()
        cursor = connection.cursor()
        
        InstitutionUserRole = details.get('institutionUserRole')
        InstitutionUserId = details.get('institutionUserId')
        DateOfBirth = details.get('dateOfBirth')
        EmailId = details.get('emailId')
        FirstName = details.get('firstName')
        Gender = details.get('gender')
        InstitutionUserName = details.get('institutionUserName')
        LastName = details.get('lastName')
        PrimaryContactNumber = details.get('primaryContactNumber')
        ImageURL = details.get('imageURL')
        Pincode = details.get('pincode')
        City = details.get('city')
        State = details.get('state')
        StreetAddress = details.get('streetAddress')
        Fathers_Name = details.get('fathers_Name')
        Board = details.get('board')
        Class_name = details.get('class') 
        InstitutionName = details.get('institutionName')
        
        if InstitutionUserRole == 'S1':
            cursor.execute("""SELECT institution_dtls.`Institution_ID`, 
                institution_user_credential.`INSTITUTION_USER_ID`,`INSTITUTION_USER_ROLE`,
                `FIRST_NAME`,`LAST_NAME`,GENDER,`INSTITUTION_USER_NAME`, 
                `INSTITUTION_USER_PASSWORD`,DATE_OF_BIRTH,CITY,GENDER,
                PINCODE,STATE,STREET_ADDRESS,`PRIMARY_CONTACT_NUMBER`,
                institution_user_credential.`IMAGE_URL`,
                institution_user_credential_master.`INSTITUTION_NAME`,
                `CLASS`,`Board`,`institution_user_credential`.`LAST_UPDATE_TIMESTAMP` FROM 
                `institution_user_credential` inner join `institution_user_credential_master` 
                on institution_user_credential.`INSTITUTION_USER_ID`=
                institution_user_credential_master.`INSTITUTION_USER_ID` 
                INNER JOIN `institution_dtls` on institution_user_credential_master.`INSTITUTION_ID`
                 =institution_dtls.`INSTITUTION_ID` INNER join `student_dtls` on 
                 institution_user_credential.`INSTITUTION_USER_ID`=student_dtls.
                 `INSTITUTION_USER_ID_STUDENT` where institution_user_credential.
                 `INSTITUTION_USER_ID`=%s and `INSTITUTION_USER_ROLE`='S1'""",
                 (InstitutionUserId))
            user_dtls = cursor.fetchone()
            # print(user_dtls)
            if user_dtls:
                
                if not DateOfBirth:
                    DateOfBirth = user_dtls.get('DATE_OF_BIRTH')
                    
                if not EmailId:
                    EmailId = user_dtls.get('EMAIL_ID')
                    
                if not FirstName:
                    FirstName = user_dtls.get('FIRST_NAME')

                if not Gender:
                    Gender = user_dtls.get('GENDER')    
                    
                if not InstitutionUserName:
                    InstitutionUserName = user_dtls.get('INSTITUTION_USER_NAME')
                    
                if not LastName:
                    LastName = user_dtls.get('LAST_NAME')
                   
                if not PrimaryContactNumber:
                    PrimaryContactNumber = user_dtls.get('PRIMARY_CONTACT_NUMBER')
                
                if not ImageURL:
                    ImageURL = user_dtls.get('IMAGE_URL')
                
                if not Pincode:
                    Pincode = user_dtls.get('PINCODE')
                        
                if not City:
                    City = user_dtls.get('CITY')
                    
                if not State:
                    State = user_dtls.get('STATE')
                    
                if not StreetAddress:
                    StreetAddress = user_dtls.get('STREET_ADDRESS')
                    
                if not Fathers_Name:
                    Fathers_Name= user_dtls.get('Fathers_Name')
                    
                if not Board:
                    Board = user_dtls.get('Board')
                    
                if not Class_name:
                    Class_name = user_dtls.get('CLASS')
                    
                if not InstitutionName:
                    InstitutionName= user_dtls.get('INSTITUTION_NAME')

                
            update_credential = ("""UPDATE `institution_user_credential` SET 
                `CITY`=%s,`DATE_OF_BIRTH`=%s,`EMAIL_ID`=%s,`FIRST_NAME`=%s,
                `GENDER`=%s,`IMAGE_URL`=%s,`INSTITUTION_USER_NAME`=%s,
                `LAST_NAME`=%s,`PINCODE`=%s,
                `PRIMARY_CONTACT_NUMBER`=%s,`STATE`=%s,`STREET_ADDRESS`=%s 
                WHERE `INSTITUTION_USER_ID`=%s""")
            updatecredentialdata = cursor.execute(update_credential,(City,
                DateOfBirth,EmailId,FirstName,Gender,ImageURL,InstitutionUserName,
                LastName,Pincode,PrimaryContactNumber,
                State,StreetAddress,InstitutionUserId))
            
            update_credentialmaster = ("""UPDATE `institution_user_credential_master` SET 
                `INSTITUTION_NAME`=%s WHERE `INSTITUTION_USER_ID`=%s""")
            updatecredentialmasterdata = cursor.execute(update_credentialmaster,
                (InstitutionName,InstitutionUserId))
            
            update_studentdtls = ("""UPDATE `student_dtls` SET `Fathers_Name`=%s 
                WHERE `INSTITUTION_USER_ID_STUDENT`=%s""")
            updatestudentdata = cursor.execute(update_studentdtls,
                (Fathers_Name,InstitutionUserId))
            
            update_clsboard = ("""UPDATE `student_dtls` SET `CLASS`=%s,
                `Board`=%s WHERE `INSTITUTION_USER_ID_STUDENT`=%s""")
            updatedata = cursor.execute(update_clsboard,
                (Class_name,Board,InstitutionUserId))

            if updatecredentialdata or updatecredentialmasterdata or updatestudentdata or updatedata:
                msg = "Updated"
            else:
                msg = "Unable to Update"

        elif InstitutionUserRole == 'TA':
            cursor.execute("""SELECT institution_dtls.`Institution_ID`, 
                institution_user_credential.`INSTITUTION_USER_ID`,`INSTITUTION_USER_ROLE`,
                `FIRST_NAME`,`LAST_NAME`,GENDER,`INSTITUTION_USER_NAME`, 
                `INSTITUTION_USER_PASSWORD`,DATE_OF_BIRTH,CITY,GENDER,
                PINCODE,STATE,STREET_ADDRESS,`PRIMARY_CONTACT_NUMBER`,
                institution_user_credential.`IMAGE_URL`,
                institution_user_credential_master.`INSTITUTION_NAME`,
                `institution_user_credential`.`LAST_UPDATE_TIMESTAMP` FROM 
                `institution_user_credential` inner join `institution_user_credential_master` 
                on institution_user_credential.`INSTITUTION_USER_ID`=
                institution_user_credential_master.`INSTITUTION_USER_ID` 
                INNER JOIN `institution_dtls` on institution_user_credential_master.`INSTITUTION_ID`
                 =institution_dtls.`INSTITUTION_ID` INNER join `teacher_dtls` on 
                 institution_user_credential.`INSTITUTION_USER_ID`=teacher_dtls.
                 `INSTITUTION_USER_ID_TEACHER` where institution_user_credential.
                 `INSTITUTION_USER_ID`=%s and `INSTITUTION_USER_ROLE`='TA'""",
                 (InstitutionUserId))
            user_dtls = cursor.fetchone()
            # print(user_dtls)
            if user_dtls:
                
                if not DateOfBirth:
                    DateOfBirth = user_dtls.get('DATE_OF_BIRTH')
                    
                if not EmailId:
                    EmailId = user_dtls.get('EMAIL_ID')
                    
                if not FirstName:
                    FirstName = user_dtls.get('FIRST_NAME')

                if not Gender:
                    Gender = user_dtls.get('GENDER')    
                    
                if not InstitutionUserName:
                    InstitutionUserName = user_dtls.get('INSTITUTION_USER_NAME')
                    
                if not LastName:
                    LastName = user_dtls.get('LAST_NAME')
                   
                if not PrimaryContactNumber:
                    PrimaryContactNumber = user_dtls.get('PRIMARY_CONTACT_NUMBER')
                
                if not ImageURL:
                    ImageURL = user_dtls.get('IMAGE_URL')
                
                if not Pincode:
                    Pincode = user_dtls.get('PINCODE')
                        
                if not City:
                    City = user_dtls.get('CITY')
                    
                if not State:
                    State = user_dtls.get('STATE')
                    
                if not StreetAddress:
                    StreetAddress = user_dtls.get('STREET_ADDRESS')
                        
                if not InstitutionName:
                    InstitutionName= user_dtls.get('INSTITUTION_NAME')

            update_credential = ("""UPDATE `institution_user_credential` SET 
                `CITY`=%s,`DATE_OF_BIRTH`=%s,`EMAIL_ID`=%s,`FIRST_NAME`=%s,
                `GENDER`=%s,`IMAGE_URL`=%s,`INSTITUTION_USER_NAME`=%s,
                `LAST_NAME`=%s,`PINCODE`=%s,
                `PRIMARY_CONTACT_NUMBER`=%s,`STATE`=%s,`STREET_ADDRESS`=%s 
                WHERE `INSTITUTION_USER_ID`=%s""")
            updatecredentialdata = cursor.execute(update_credential,(City,
                DateOfBirth,EmailId,FirstName,Gender,ImageURL,InstitutionUserName,
                LastName,Pincode,PrimaryContactNumber,
                State,StreetAddress,InstitutionUserId))
            
            update_credentialmaster = ("""UPDATE `institution_user_credential_master` SET 
                `INSTITUTION_NAME`=%s WHERE `INSTITUTION_USER_ID`=%s""")
            updatecredentialmasterdata = cursor.execute(update_credentialmaster,
                (InstitutionName,InstitutionUserId))
            
            
            if updatecredentialdata or updatecredentialmasterdata:
                msg = "Updated"
            else:
                msg = "Unable to Update"
        else:
            msg = "Unable to Update"
            
        connection.commit()
        cursor.close() 

        return ({"attributes": {"status_desc": "Update User Profile Details.",
                            "status": "success",
                            "msg": msg
                            },
                            "responseList":details}), status.HTTP_200_OK

#-----------------------------------------------------#
