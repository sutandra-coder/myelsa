from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests

app = Flask(__name__)
cors = CORS(app)
mysql = MySQL()
user_tracking = Blueprint('user_tracking_api', __name__)
api = Api(user_tracking, version='1.0', title='myElsa User Tracking',
    description='myElsa User Tracking')
name_space = api.namespace('UserTracking', description=':User Tracking')

app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'cbdHoRPQPRfTdC0uSPLt'
app.config['MYSQL_DATABASE_DB'] = 'creamson_logindb'
app.config['MYSQL_DATABASE_HOST'] = 'myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com'
mysql.init_app(app)

app.config['CORS_HEADERS'] = 'Content-Type'

tracking_model = api.model('UserTracking', {
	"institution_user_id":fields.Integer(required=True),
	"type":fields.String(required=True),
	"start_time":fields.Date(required=False)
	})
vote_for_teacher_model = api.model('VoteYourTeacher', {
	"user_id":fields.Integer(required=True),
	"firstname":fields.String(),
	"lastname":fields.String(),
	"mobileno":fields.Integer(),
	"emailid":fields.String(),
	"schoolname":fields.String(),
	"gratitude_note":fields.String(),
	"template_id":fields.Integer(required=True)
	})


vote_for_teacher_model_for_portal = api.model('VoteYourTeacherForPortal', {
	"student_firstname":fields.String(required=True),
	"student_lastname":fields.String(required=True),
	"student_phoneno":fields.String(required=True),
	"firstname":fields.String(),
	"lastname":fields.String(),
	"mobileno":fields.Integer(),
	"emailid":fields.String(),
	"schoolname":fields.String(),
	"gratitude_note":fields.String(),
	"template_id":fields.Integer(required=True)
	})

@name_space.route("/trackUser")
class validateCoupon(Resource):
	@api.expect(tracking_model)
	def post(self):
		details = request.get_json()
		connection = mysql.connect()
		cursor = connection.cursor()
		try:
			user_tracking_insert_query = ("""INSERT INTO `institution_user_tracking`(`institution_user_id`, 
				`type`,`start_time`) VALUES (%s,%s,%s)""")
			user_tracking_data = (details['institution_user_id'],details['type'],details['start_time'])
			cursor.execute(user_tracking_insert_query,user_tracking_data)
		except:
			pass

		return ({"attributes": {
	    				"status_desc": "User Tracking Details.",
	    				"status": "success"
	    				},
	    				"responseList":{"TrackingDtls":details}}), status.HTTP_200_OK


@name_space.route("/verifyUsername/<string:username>/<string:password>")
class verifyUsername(Resource):
	def get(self,username,password):
		connection = mysql.connect()
		cursor = connection.cursor()
		cursor.execute("""SELECT `EMPLOYEE_ID`,`ADMIN_ROLE`,`USERNAME` FROM 
			`creamson_employee_admin_dtls` WHERE `USERNAME` = %s and `PASSWORD` = %s""",(username,password))
		emp_dtls = cursor.fetchall()
		cursor.close()
		if emp_dtls:
			emp_id = emp_dtls[0][0]
			emp_role = emp_dtls[0][1]
			emp_username = emp_dtls[0][2]
			emp_details = {"emp_id":emp_id,
					"emp_role":emp_role,
					"emp_username":emp_username}

			return ({"attributes": {
	    				"status_desc": "Login Details.",
	    				"status": "success",
	    				"message":"Login Success"
	    				},
	    				"responseList":emp_details}), status.HTTP_200_OK
		else:
				
			return ({"attributes": {
		    				"status_desc": "Login Details.",
		    				"status": "success",
		    				"message":"Invalid Username or Password"
		    				},
		    				"responseList":[]}), status.HTTP_200_OK
		


@name_space.route("/voteForYourTeacherPost")
class voteForYourTeacherPost(Resource):
	@api.expect(vote_for_teacher_model)
	def post(self):
		details = request.get_json()
		connection = mysql.connect()
		cursor = connection.cursor()
		user_id = details['user_id']
		firstname = details['firstname']
		lastname = details['lastname']
		mobileno = details['mobileno']
		emailid = details['emailid']
		schoolname = details['schoolname']
		gratitude_note = details['gratitude_note']
		note = gratitude_note.split(" ")
		if len(note) >= 5:
			note = " ".join(note[:5])
		else:
			note = gratitude_note
		template_id = details['template_id']
		cursor.execute("""INSERT INTO `vote_for_teacher`(`user_id`, `firstname`, `lastname`, 
			`mobile_no`, `email_id`, `school_name`, `gratitude_note`, `template_id`) 
			VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""",(user_id,firstname,lastname,mobileno,
				emailid,schoolname,gratitude_note,template_id))
		vote_id = cursor.lastrowid
		
		cursor.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as student_name, `image_url`  
    		FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(user_id))


		student_name = cursor.fetchone()
		if student_name:
			name = student_name[0]
			image_url = student_name[1]

		connection.commit()
		cursor.close()
		details['user_vote_id'] = vote_id
		url = 'http://creamsonservices.com:8080/CommunicationModule2/sendMailMessage'
		data = {
				  'mailDetails': [
				    {
				      'appParams': {},
				      'mailParams': {"firstName":firstname,
				      				"StudentName":name,
				      				"msg":'"'+note+'"'},
				      'role': 'S1',
				      'toMail': emailid,
				      'toNumber': mobileno,
				      'userId': ''
				    }
				  ],
				  'sourceApp': 'Vote4Tchr'
				}
		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		response = requests.post(url, data=json.dumps(data), headers=headers)
		return ({"attributes": {
	    				"status_desc": "User Voting Details.",
	    				"status": "success"
	    				},
	    				"responseList":details}), status.HTTP_200_OK

@name_space.route("/getUserTeacherVotingDetails/<int:user_id>")
class getUserTeacherVotingDetails(Resource):
	def get(self,user_id):
		connection = mysql.connect()
		cursor = connection.cursor()
		details = {}
		cursor.execute("""SELECT `firstname`, `lastname`, `mobile_no`, `email_id`, 
			`school_name`, `gratitude_note`, `template_id` FROM `vote_for_teacher` 
			WHERE `user_id` = %s""",(user_id))
		voted_id = cursor.fetchall()
		cursor.close()
		print(voted_id)
		if voted_id: 
			firstname = voted_id[0][0]
			lastname = voted_id[0][1]
			mobile_no = voted_id[0][2]
			email_id = voted_id[0][3]
			school_name = voted_id[0][4]
			gratitude_note = voted_id[0][5]
			template_id = voted_id[0][6]
			details['firstname'] = firstname
			details['lastname'] = lastname
			details['mobile_no'] = mobile_no
			details['email_id'] = email_id
			details['school_name'] = school_name
			details['gratitude_note'] = gratitude_note
			details['template_id'] = template_id
			
			return ({"attributes": {
	    				"status_desc": "Student Voting Details.",
	    				"status": "success",
	    				"message": "You have already voted once.",
	    				"voted_for": firstname + " " +lastname
	    				},
	    				"responseList":details}), status.HTTP_200_OK
		else:
			return ({"attributes": {
	    				"status_desc": "Student Voting Details.",
	    				"status": "success",
	    				"message": "Write a note for your Teacher",
	    				"voted_for": ""
	    				},
	    				"responseList":details}), status.HTTP_200_OK



@name_space.route("/getEmpDtls/<int:emp_id>/<string:emp_role>")
class getEmpDtls(Resource):
    def get(self,emp_id,emp_role):
        connection = mysql.connect()
        cursor = connection.cursor()
        emp_details = {}
        col_names= []
        if emp_role == "member":
            cursor.execute("""SELECT `EMPLOYEE_ID`,`ADMIN_ROLE`,`USERNAME` 
            	FROM `creamson_employee_admin_dtls` WHERE `EMPLOYEE_ID` = %s """, (emp_id))
            emp_dtls = cursor.fetchall()
            if emp_dtls:
                emp_id = emp_dtls[0][0]
                emp_role = emp_dtls[0][1]
                username = emp_dtls[0][2]
                emp_details = [{"EMPLOYEE_ID":emp_id,
                                "ADMIN_ROLE":emp_role,
                                "USERNAME":username}]
            
        else:
            cursor.execute("""SELECT `EMPLOYEE_ID`,`ADMIN_ROLE`,`USERNAME` FROM `creamson_employee_admin_dtls`""")
            emp_dtls = cursor.fetchall()
            desc = cursor.description
            col_names = [col[0] for col in desc]
            emp_details = [dict(izip(col_names, row)) for row in emp_dtls]
            cursor.close()
        return ({"attributes": {
	    				"status_desc": "Login Details.",
	    				"status": "success",
	    				},
	    				"responseList":emp_details}), status.HTTP_200_OK

@name_space.route("/getInactiveUserListByInstitutionId/<int:institution_id>")
class getInactiveUserListByInstitutionId(Resource):
    def get(self,institution_id):
    	connection = mysql.connect()
    	cursor = connection.cursor()
    	cursor.execute("""SELECT DISTINCT a.`PHONE_NUMBER`, concat(a.`FIRST_NAME`," ",a.`LAST_NAME`) Name
    		FROM `institution_user_otp` a WHERE a.`INSTITUTION_ID` = %s and a. `PHONE_NUMBER` not 
    		in (SELECT ic.`INSTITUTION_USER_NAME` FROM `institution_user_credential` ic,
    		`institution_user_credential_master` icm 
    		WHERE icm.`INSTITUTION_USER_ID` = ic.`INSTITUTION_USER_ID` 
    		and icm.`INSTITUTION_ID` = %s)""",(institution_id,institution_id))

    	inactive_dtls = cursor.fetchall()
    	if inactive_dtls:
    		desc = cursor.description
    		col_names = [col[0] for col in desc]
    		inactive_users = [dict(izip(col_names,row)) for row in inactive_dtls]
    	return ({"attributes": {
	    				"status_desc": "Inactive Student Details.",
	    				"status": "success",
	    				},
	    				"responseList":inactive_users}), status.HTTP_200_OK


@name_space.route("/getVoteForTeacherTemplates/<string:dashboard_desc>")
class getVoteForTeacherTemplates(Resource):
	def get(self,dashboard_desc):
		connection = mysql.connect()
		cursor = connection.cursor()
		templates_list = []
		cursor.execute("""SELECT `id`,`template_path` FROM `greeting_templates` 
			WHERE `dashboard_desc` = %s""",(dashboard_desc))

		temps = cursor.fetchall()
		if temps:
			desc = cursor.description
			col_names = [cols[0] for cols in desc]
			templates_list = [dict(izip(col_names,row)) for row in temps]

		return ({"attributes": {
	    				"status_desc": "Template Details.",
	    				"status": "success"
	    				},
	    				"responseList":templates_list}), status.HTTP_200_OK



@name_space.route("/voteForYourTeacherPostForPortal")
class voteForYourTeacherPostForPortal(Resource):
	@api.expect(vote_for_teacher_model_for_portal)
	def post(self):
		details = request.get_json()
		connection = mysql.connect()
		cursor = connection.cursor()
		student_firstname = details['student_firstname']
		student_lastname = details['student_lastname']
		student_phoneno = details['student_phoneno']
		# user_id = details['user_id']
		firstname = details['firstname']
		lastname = details['lastname']
		mobileno = details['mobileno']
		emailid = details['emailid']
		schoolname = details['schoolname']
		gratitude_note = details['gratitude_note']
		note = gratitude_note.split(" ")
		if len(note) >= 5:
			note = " ".join(note[:5])
		else:
			note = gratitude_note
		template_id = details['template_id']
		cursor.execute("""INSERT INTO `vote_for_teacher`(`student_firstname`,
			`student_lastname`,`student_phoneno`, `firstname`, `lastname`, 
			`mobile_no`, `email_id`, `school_name`, `gratitude_note`, `template_id`) 
			VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(student_firstname,student_lastname,
				student_phoneno,firstname,lastname,mobileno,emailid,schoolname,
				gratitude_note,template_id))

		connection.commit()
		vote_id = cursor.lastrowid
		cursor.close()
		details['user_vote_id'] = vote_id
		url = 'http://creamsonservices.com:8080/CommunicationModule2/sendMailMessage'
		data = {
				  'mailDetails': [
				    {
				      'appParams': {},
				      'mailParams': {"firstName":firstname,
				      				"StudentName":student_firstname +" "+ student_lastname,
				      				"msg":'"'+note+'"'},
				      'role': 'S1',
				      'toMail': emailid,
				      'toNumber': mobileno,
				      'userId': ''
				    }
				  ],
				  'sourceApp': 'Vote4Tchr'
				}
		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		response = requests.post(url, data=json.dumps(data), headers=headers)
		return ({"attributes": {
	    				"status_desc": "User Voting Details.",
	    				"status": "success"
	    				},
	    				"responseList":details}), status.HTTP_200_OK

@name_space.route("/getUserVotingDetailsForPortal/<string:student_phoneno>")
class getUserTeacherVotingDetails(Resource):
	def get(self,student_phoneno):
		connection = mysql.connect()
		cursor = connection.cursor()
		details = {}
		cursor.execute("""SELECT `firstname`, `lastname`, `mobile_no`, `email_id`, 
			`school_name`, `gratitude_note`, `template_id` FROM `vote_for_teacher` 
			WHERE `student_phoneno` = %s""",(student_phoneno))
		voted_id = cursor.fetchall()
		cursor.close()
		print(voted_id)
		if voted_id: 
			firstname = voted_id[0][0]
			lastname = voted_id[0][1]
			mobile_no = voted_id[0][2]
			email_id = voted_id[0][3]
			school_name = voted_id[0][4]
			gratitude_note = voted_id[0][5]
			template_id = voted_id[0][6]
			details['firstname'] = firstname
			details['lastname'] = lastname
			details['mobile_no'] = mobile_no
			details['email_id'] = email_id
			details['school_name'] = school_name
			details['gratitude_note'] = gratitude_note
			details['template_id'] = template_id
			
			return ({"attributes": {
	    				"status_desc": "Student Voting Details.",
	    				"status": "success",
	    				"message": "You have already voted once.",
	    				"voted_for": firstname + " " +lastname
	    				},
	    				"responseList":details}), status.HTTP_200_OK
		else:
			return ({"attributes": {
	    				"status_desc": "Student Voting Details.",
	    				"status": "success",
	    				"message": "Write a note for your Teacher",
	    				"voted_for": ""
	    				},
	    				"responseList":details}), status.HTTP_200_OK


@name_space.route("/getNoofVotesForTeacher/<string:teacher_phoneno>/<string:teacher_emailid>")
class getNoofVotesForTeacher(Resource):
	def get(self,teacher_phoneno,teacher_emailid):
		connection = mysql.connect()
		cursor = connection.cursor()
		if teacher_phoneno != '' and teacher_emailid == '0':
			cursor.execute("""SELECT count(`id`) NoOfVotes FROM `vote_for_teacher` 
				WHERE `mobile_no` = %s""",(teacher_phoneno))

			votesdtls = cursor.fetchone()
		elif teacher_phoneno == '0' and teacher_emailid != '':
			cursor.execute("""SELECT count(`id`) NoOfVotes FROM `vote_for_teacher` 
				WHERE `email_id` = %s""",(teacher_emailid))

			votesdtls = cursor.fetchone()
		elif teacher_phoneno != '' and teacher_emailid != '':
			cursor.execute("""SELECT count(id) NoOfVotes FROM `vote_for_teacher` 
				WHERE `mobile_no` = %s or `email_id` = %s""",(teacher_phoneno,teacher_emailid))

			votesdtls = cursor.fetchone()

		else:
			votesdtls = (0)

		if votesdtls:
			votesdtls = votesdtls[0]


		return ({"attributes": {
	    				"status_desc": "Teacher Vote Count Details.",
	    				"status": "success",
	    				"VoteCount": votesdtls
	    				},
	    				"responseList":[]}), status.HTTP_200_OK

if __name__ == '__main__':
	app.run(host='0.0.0.0')