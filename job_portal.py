import json
import requests
import xmltodict
# import urllib2
import os
import smtplib
import imghdr
import io
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime
from flask import Blueprint
from flask import Flask
from flask import request
from flask_api import status
from flask_cors import CORS
from flask_restplus import Api
from flask_restplus import Resource
from flask_restplus import fields
from flaskext.mysql import MySQL
from jinja2._compat import izip

app = Flask(__name__)
cors = CORS(app)
mysql = MySQL()
job_portal = Blueprint('job_portal_api', __name__)
api = Api(job_portal, version='1.0', title='MyElsa API', description='MyElsa API')
name_space1 = api.namespace('CEM', description=':JobPortal-CEM')
name_space2 = api.namespace('CVScore', description=':JobPortal-CVScore')

app.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app.config['MYSQL_DATABASE_DB'] = 'creamson_job_portal'
app.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'
mysql.init_app(app)

app.config['CORS_HEADERS'] = 'Content-Type'
EMAIL_ADDRESS = 'jobcommunications@creamsonservices.com'
EMAIL_PASSWORD = 'jobcomm@123'
GUPSHUP_USERID = '2000188641'
GUPSHUP_PASSWORD = 'UDLMDQEUP'

queue_model = api.model('Queue Model', {
	"user_type":fields.List(fields.String()),
	"ageing":fields.Integer(default = 0),
	"last_contact_type":fields.List(fields.String()),
	"last_contacted":fields.Integer(default = 0),
	"mail_subject":fields.String(),
	"mail_body":fields.String(),
	"image_url":fields.String(),
	"sms_body":fields.String(),
	"whatsapp_body":fields.String(),
	})


email_model = api.model('Email Model', {
	"mail_subject":fields.String(),
	"mail_body":fields.String(),
	"image_url":fields.String(),
	"user_id":fields.List(fields.Integer()),
	})

email_model2 = api.model('Email Model V2', {
	"mail_subject":fields.String(),
	"mail_body":fields.String(),
	"image_url":fields.String(),
	"user_id":fields.List(fields.Integer()),
	"user_mail_id":fields.List(fields.String())
	})

sms_model = api.model('SMS Model', {
	"sms_body":fields.String(),
	"image_url":fields.String(),
	"user_id":fields.List(fields.Integer()),
	})

cv_score_model = api.model('CV Score',{
						"first_name":fields.String(),
						"last_name":fields.String(),
						"download_id":fields.Integer(required=True), 
						"source_emailid":fields.String(), 
						"cv_filepath":fields.String(), 
						"source_app":fields.String()
						})

def getUsers(user_type,ageing):
	connection = mysql.connect()
	cursor = connection.cursor()
	users_details = []

	if user_type == '':
		user_type = 'unpaid','paid'
	else:
		user_type = tuple(user_type)
	if ageing > 0:
		cursor.execute("""SELECT `cv_user_id`,`first_name`,`mobile_no`,`email_id`,`cv_filepath` 
			FROM `cv_master` WHERE `user_type` in %s 
			and date(`last_update_ts`) between subdate(CURRENT_DATE,%s) and CURRENT_DATE""",(user_type,ageing))
		users = cursor.fetchall()
		if users:
			desc = cursor.description
			col_names = [col[0] for col in desc]
			users_details = [dict(izip(col_names,row)) for row in users]
	else:
		cursor.execute("""SELECT `cv_user_id`,`first_name`,`mobile_no`,`email_id`,`cv_filepath`
			FROM `cv_master` WHERE `user_type` in %s""",(user_type,))
		users = cursor.fetchall()
		if users:
			desc = cursor.description
			col_names = [col[0] for col in desc]
			users_details = [dict(izip(col_names ,row)) for row in users]


	cursor.close()
	print(users_details)
	return users_details


def getLastContactFromMailQueue(users_details,last_contacted):
	connection = mysql.connect()
	cursor = connection.cursor()
	mail_list = []
	if users_details:
		for idx, user in enumerate(users_details):
			user_id = users_details[idx]['cv_user_id']
			if last_contacted > 0:
				print(user_id)
				cursor.execute("""SELECT `user_id` FROM `mail_queue`
					WHERE `user_id` = %s and date(`last_update_ts`) 
					BETWEEN subdate(CURRENT_DATE,%s) and CURRENT_DATE""",(user_id,last_contacted))
				m_id = cursor.fetchone()
				if m_id:
					for i,j in enumerate(m_id):
						mail_list.append(m_id[0])
			else:
				cursor.execute("""SELECT `user_id` FROM `mail_queue`
					WHERE `user_id` = %s""",(user_id,))

				m_id = cursor.fetchone()
				if m_id:
					for i,j in enumerate(m_id):
						mail_list.append(m_id[0])

	print(mail_list)
	return mail_list



def getLastContactFromSMSQueue(users_details,last_contacted):
	connection = mysql.connect()
	cursor = connection.cursor()
	sms_list = []
	if users_details:
		for idx, user in enumerate(users_details):
			user_id = users_details[idx]['cv_user_id']
			if last_contacted > 0:
				cursor.execute("""SELECT `user_id` FROM `sms_queue`
					WHERE `user_id` = %s and date(`last_update_ts`) 
					BETWEEN subdate(CURRENT_DATE,%s) and CURRENT_DATE""",(user_id,last_contacted))
				sms_id = cursor.fetchone()
				if sms_id:
					for i,j in enumerate(sms_id):
						sms_list.append(sms_id[0])
			else:
				cursor.execute("""SELECT `user_id` FROM `sms_queue`
					WHERE `user_id` = %s""",(user_id,))

				sms_id = cursor.fetchone()
				if sms_id:
					for i,j in enumerate(sms_id):
						sms_list.append(sms_id[0])

	print(sms_list)
	return sms_list


def getLastContactFromWhatsAppQueue(users_details,last_contacted):
	connection = mysql.connect()
	cursor = connection.cursor()
	whatsapp_list = []
	if users_details:
		for idx, user in enumerate(users_details):
			user_id = users_details[idx]['cv_user_id']
			if last_contacted > 0:
				cursor.execute("""SELECT `user_id` FROM `whatsapp_queue`
					WHERE `user_id` = %s and date(`last_update_ts`) 
					BETWEEN subdate(CURRENT_DATE,%s) and CURRENT_DATE""",(user_id,last_contacted))
				msg_id = cursor.fetchone()
				if msg_id:
					for i,j in enumerate(msg_id):
						whatsapp_list.append(msg_id[i][0])
			else:
				cursor.execute("""SELECT `user_id` FROM `whatsapp_queue`
					WHERE `user_id` = %s""",(user_id,))

				msg_id = cursor.fetchone()
				if msg_id:
					for i,j in enumerate(msg_id):
						whatsapp_list.append(msg_id[i][0])

	print(whatsapp_list)
	return whatsapp_list


def getemailcomm(from_date, to_date):
    connection = mysql.connect()
    cursor = connection.cursor()
    mail_list = []
    cursor.execute("""SELECT `sender_mail_id`,`mail_subject`,`mail_body`,`user_mail_id`,
    	`delivery_status`,`user_id`,`image_path`,`source_app`,`read_recipient` 
    	FROM `mail_queue` WHERE date(`last_update_ts`) BETWEEN %s AND %s""", (from_date, to_date))
    getmail = cursor.fetchall()
    if getmail:
        desc = cursor.description
        col_names = [col[0] for col in desc]
        mail_list = [dict(izip(col_names, row)) for row in getmail]
        for i in range(len(mail_list)):
            user_id = mail_list[i]['user_id']
            cursor.execute(
                """SELECT Concat(`first_name`,' ',`last_name`) FROM `cv_master` 
                WHERE `cv_user_id` =%s""", (user_id))
            user_name = cursor.fetchone()
            if user_name:
                mail_list[i]['user_name'] = user_name[0]
            else:
                mail_list[i]['user_name'] = ''
    return mail_list

def getsmscomm(from_date, to_date):
    connection = mysql.connect()
    cursor = connection.cursor()
    sms_list = []
    cursor.execute("""SELECT `sms_body`,`sender_mobile_no`,`user_mobile_no`,`image_path`,
    	`user_id`,`delivery_status` FROM `sms_queue` WHERE date(`last_update_ts`) 
    	BETWEEN %s AND %s""", (from_date, to_date))
    getsms = cursor.fetchall()
    if getsms:
        desc = cursor.description
        col_names = [col[0] for col in desc]
        sms_list = [dict(izip(col_names, row)) for row in getsms]
        for i in range(len(sms_list)):
            user_id = sms_list[i]['user_id']
            cursor.execute(
                """SELECT Concat(`first_name`,' ',`last_name`) FROM `cv_master` 
                WHERE `cv_user_id` =%s""", (user_id))
            user_name = cursor.fetchone()
            if user_name:
                sms_list[i]['user_name'] = user_name[0]
            else:
                sms_list[i]['user_name'] = ''
    return sms_list

def getwhatsappcomm(from_date, to_date):
    connection = mysql.connect()
    cursor = connection.cursor()
    whatsapp_list = []
    cursor.execute("""SELECT `sender_phone_no`,`user_phone_no`,`msg_body`,`msg_title`,`image_path`,`delivery_status`,`user_id` FROM `whatsapp_queue` WHERE date(`last_update_ts`) BETWEEN %s AND %s""", (from_date, to_date))
    getwhatsapp = cursor.fetchall()
    if getwhatsapp:
        desc = cursor.description
        col_names = [col[0] for col in desc]
        whatsapp_list = [dict(izip(col_names, row))
                         for row in getwhatsapp]
    for i in range(len(whatsapp_list)):
        user_id = whatsapp_list[i]['user_id']
        cursor.execute(
            """SELECT Concat(`first_name`,' ',`last_name`) FROM `cv_master` WHERE `cv_user_id` =%s""", (user_id))
        user_name = cursor.fetchone()
        if user_name:
            whatsapp_list[i]['user_name'] = user_name[0]
        else:
            whatsapp_list[i]['user_name'] = ''
    return whatsapp_list

@name_space1.route("/postCommunication/<string:contact_type>")
class postCommunication(Resource):
	@api.expect(queue_model)
	def post(self,contact_type):
		details = request.get_json()
		user_type = (details['user_type'])
		print(user_type)
		ageing = details['ageing']
		last_contact_type = details['last_contact_type']
		last_contacted = details['last_contacted']
		mail_subject = details['mail_subject']
		mail_body = details['mail_body']
		image_url = details['image_url']
		sms_body = details['sms_body']
		whatsapp_body = details['whatsapp_body']

		last_mail_queue = []
		last_sms_queue = []
		last_whatsapp_queue = []
		total_last_contacted = []

		users_details = getUsers(user_type,ageing)

		if len(last_contact_type) == 0 or len(last_contact_type) == 3:
			print('inside if')
			last_mail_queue = getLastContactFromMailQueue(users_details,last_contacted)
			last_sms_queue =  getLastContactFromSMSQueue(users_details,last_contacted)
			last_whatsapp_queue = getLastContactFromWhatsAppQueue(users_details,last_contacted)

		elif len(last_contact_type) > 0 and len(last_contact_type) < 3:
			print('inside elif')
			for con_type in last_contact_type:
				# print(con_type)
				if con_type.lower() == 'email':
					last_mail_queue = getLastContactFromMailQueue(users_details,last_contacted)
				elif con_type.lower() == 'sms':
					last_sms_queue =  getLastContactFromSMSQueue(users_details,last_contacted)
				elif con_type.lower() == 'whatsapp':
					last_whatsapp_queue = getLastContactFromWhatsAppQueue(users_details,last_contacted)


		total_last_contacted.extend(last_mail_queue)
		total_last_contacted.extend(last_sms_queue)
		total_last_contacted.extend(last_whatsapp_queue)

		total_last_contacted = list(set(total_last_contacted))
		# for u_id in total_last_contacted:
		if contact_type.lower() == 'email':
			# email_req_url = 'http://127.0.0.1:5000/cem_queue/CEM/postCommunicationByEmail'
			email_req_url = 'http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com/flaskapp/job_portal/CEM/postCommunicationByEmail'	
			email_payload = {"mail_subject":mail_subject,
			"mail_body":mail_body,
			"image_url":image_url,
			"user_id":total_last_contacted}

			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			response = requests.post(email_req_url, data=json.dumps(email_payload), headers=headers)
		elif contact_type.lower() == 'sms':
			sms_req_url = 'http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com/flaskapp/job_portal/CEM/postCommunicationBySMS'
			# email_req_url = 'http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com/flaskapp/job_portal/CEM/postCommunicationByEmail'	
			sms_payload = {"sms_body":sms_body,
							"image_url":image_url,
							"user_id":total_last_contacted}

			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			response = requests.post(sms_req_url, data=json.dumps(sms_payload), headers=headers)
		else:
			return ({"attributes": {"status_desc": "User Details.",
								"status": "failure"
								},
				"responseList":'Input Email or SMS as contact type'}), status.HTTP_200_OK

		return ({"attributes": {"status_desc": "User Details.",
								"status": "success"
								},
				"responseList":len(total_last_contacted)}), status.HTTP_200_OK



@name_space1.route("/postCommunicationByEmail")
class postCommunicationByEmail(Resource):
	@api.expect(email_model)
	def post(self):
		connection = mysql.connect()
		cursor = connection.cursor()
		details = request.get_json()
		mail_subject = details['mail_subject']
		mail_body = details['mail_body']
		image_url = details['image_url']
		user_id = details['user_id']
		sender_mail_id = EMAIL_ADDRESS
		mail_queue = []
		for u_id in user_id:
			cursor.execute("""SELECT `first_name`, `last_name`, 
				`mobile_no`,`email_id`,`date_of_registration`,`cv_filepath`,
				`source_emailid`,`user_type`, `source_app`
				FROM `cv_master` WHERE `cv_user_id` = %s""",(u_id))


			user_dtls = cursor.fetchone()

			cursor.execute("""SELECT  `grade`, `grade_headline`, `percentile`, 
				`brevity_score`, `impact_score`, `depth_score`, `tip_short`, 
				`tip_long`, `rez_id` FROM `cv_score_master` 
				WHERE `user_id` = %s""",(u_id))

			score_dtls = cursor.fetchone()
			print(user_dtls)
			if user_dtls and score_dtls:
				first_name = user_dtls[0]
				last_name = user_dtls[1]
				userName = first_name + ' ' + last_name
				phoneNo = user_dtls[2]
				mailId = user_dtls[3]
				dateOfRegistration = user_dtls[4]
				userType = user_dtls[7]
				sourceApp = user_dtls[8]
				grade = score_dtls[0]
				grade_headline = score_dtls[1]
				percentile = score_dtls[2]
				brevity_score = score_dtls[3]
				impact_score = score_dtls[4]
				depth_score = score_dtls[5]
				tip_short = score_dtls[6]
				tip_long = score_dtls[7]
				rez_id = score_dtls[8]
				body_text = mail_body.format(userName = userName,phoneNo = phoneNo, 
					mailId = mailId,dateOfRegistration = dateOfRegistration,userType = userType,
					grade = grade,gradeHeadline =grade_headline,percentile=percentile,
					brevityScore=brevity_score,impactScore=impact_score,depthScore=depth_score,
					tipShort = tip_short,tipLong=tip_long,rezId=rez_id)
				# open('cv.html','w').write(body_text)

				mail_insert_query = ("""INSERT INTO `mail_queue`(`sender_mail_id`, `mail_subject`, 
					`mail_body`, `user_mail_id`, `delivery_status`, `user_id`, `image_path`, 
					`source_app`, `read_recipient`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
				mail_data = (sender_mail_id,mail_subject,body_text,mailId,'N',u_id,image_url,sourceApp,'N')

				cursor.execute(mail_insert_query,mail_data)
				mail_queue.append({"user_id":u_id,
									"mail_id":mailId,
									"mail":body_text})
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Mail Queue Details.",
								"status": "success"
								},
				"responseList":mail_queue}), status.HTTP_200_OK

@name_space1.route("/sendMailFromQueue")
class sendMailFromQueue(Resource):
	def get(self):
		connection = mysql.connect()
		cursor = connection.cursor()
		details = request.get_json()

		cursor.execute("""SELECT `mail_subject`,`mail_body`,`user_mail_id`,`image_path` 
			FROM `mail_queue` WHERE `delivery_status` = 'N'""")

		queue_list = cursor.fetchall()
		if queue_list:
			for i in range(len(queue_list)):
				msg = MIMEMultipart()
				msg['Subject'] = queue_list[i][0]
				msg['From'] = EMAIL_ADDRESS
				msg['To'] = queue_list[i][2]
				html = queue_list[i][1]
				part1 = MIMEText(html, 'html')
				msg.attach(part1)
				if queue_list[i][3]:
					f = urllib2.urlopen(queue_list[i][3])
					image_file = io.BytesIO(f.read())
					fp = io.BufferedReader(image_file)
					img = MIMEImage(fp.read())
					file_type = queue_list[i][3].split('/')[-1].split('.')[-1]
					file_name = queue_list[i][3].split('/')[-1]
					f.close()
					img.add_header('Content-Disposition', 'attachment', filename=file_name)
					msg.attach(img)
				
				try:
					print(queue_list[i][2])
					smtp = smtplib.SMTP('mail.creamsonservices.com', 587)
					smtp.starttls()
					smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
					print(queue_list[i][2])
					smtp.sendmail(EMAIL_ADDRESS, queue_list[i][2], msg.as_string())
					print(queue_list[i][2])
					
					res = {"status":'success'}
					print(res)
				except Exception as e:
					raise e
					res = {"status":'failure'}
		smtp.quit()

		return ({"attributes": {"status_desc": "Send Mail Details.",
								"status": "success"
								},
				"responseList":res}), status.HTTP_200_OK


@name_space2.route("/sendMail")
class sendMail(Resource):
	@api.expect(email_model2)
	def post(self):
		connection = mysql.connect()
		cursor = connection.cursor()
		details = request.get_json()
		mail_subject = details['mail_subject']
		mail_body = details['mail_body']
		image_url = details['image_url']
		user_id = details['user_id']
		user_mail_id = details['user_mail_id']

		
		# email_req_url = 'http://127.0.0.1:5000/job_portal/CEM/postCommunicationByEmail'
		email_req_url = 'http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com/flaskapp/job_portal/CEM/postCommunicationByEmail'	
		email_payload = {"mail_subject":mail_subject,
			"mail_body":mail_body,
			"image_url":image_url,
			"user_id":user_id}

		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		response = requests.post(email_req_url, data=json.dumps(email_payload), headers=headers)

		user_mail_id = json.loads(response.text)["responseList"][0]['mail_id']
		mail_body = json.loads(response.text)["responseList"][0]['mail']
		length = len(user_id)

		if user_id:
			for i in range(length):
				msg = MIMEMultipart()
				msg['Subject'] = mail_subject
				msg['From'] = EMAIL_ADDRESS
				msg['To'] = user_mail_id

				html = mail_body
				part1 = MIMEText(html, 'html')
				msg.attach(part1)

				if image_url:
					f = urllib2.urlopen(image_url)
					image_file = io.BytesIO(f.read())
					fp = io.BufferedReader(image_file)
					img = MIMEImage(fp.read())
					file_type = image_url.split('/')[-1].split('.')[-1]
					file_name = image_url.split('/')[-1]
					f.close()
					img.add_header('Content-Disposition', 'attachment', filename=file_name)
					msg.attach(img)
				
				try:
					smtp = smtplib.SMTP('mail.creamsonservices.com', 587)
					smtp.starttls()
					smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
					smtp.sendmail(EMAIL_ADDRESS, user_mail_id, msg.as_string())
					res = {"status":'success'}

				except Exception as e:
					raise e
					res = {"status":'failure'}
				smtp.quit()

		return ({"attributes": {"status_desc": "Send Mail Details.",
								"status": "success"
								},
				"responseList":res}), status.HTTP_200_OK


@name_space1.route("/postCommunicationBySMS")
class postCommunicationBySMS(Resource):
	@api.expect(sms_model)
	def post(self):
		connection = mysql.connect()
		cursor = connection.cursor()
		details = request.get_json()
		sms_body = details['sms_body']
		image_url = details['image_url']
		user_id = details['user_id']
		sms_queue = []
		for u_id in user_id:
			cursor.execute("""SELECT `first_name`, `last_name`, 
				`mobile_no`,`email_id`,`date_of_registration`,`cv_filepath`,
				`source_emailid`,`user_type`, `source_app`
				FROM `cv_master` WHERE `cv_user_id` = %s""",(u_id))


			user_dtls = cursor.fetchone()

			cursor.execute("""SELECT  `grade`, `grade_headline`, `percentile`, 
				`brevity_score`, `impact_score`, `depth_score`, `tip_short`, 
				`tip_long`, `rez_id` FROM `cv_score_master` 
				WHERE `user_id` = %s""",(u_id))

			score_dtls = cursor.fetchone()
			print(user_dtls)
			if user_dtls and score_dtls:
				first_name = user_dtls[0]
				last_name = user_dtls[1]
				userName = first_name + ' ' + last_name
				phoneNo = user_dtls[2]
				mailId = user_dtls[3]
				dateOfRegistration = user_dtls[4]
				userType = user_dtls[7]
				sourceApp = user_dtls[8]
				grade = score_dtls[0]
				grade_headline = score_dtls[1]
				percentile = score_dtls[2]
				brevity_score = score_dtls[3]
				impact_score = score_dtls[4]
				depth_score = score_dtls[5]
				tip_short = score_dtls[6]
				tip_long = score_dtls[7]
				rez_id = score_dtls[8]
				body_text = sms_body.format(userName = userName,phoneNo = phoneNo, 
					mailId = mailId,dateOfRegistration = dateOfRegistration,userType = userType,
					grade = grade,gradeHeadline =grade_headline,percentile=percentile,
					brevityScore=brevity_score,impactScore=impact_score,depthScore=depth_score,
					tipShort = tip_short,tipLong=tip_long,rezId=rez_id)
				print(body_text)

				sms_insert_query = ("""INSERT INTO `sms_queue`(`sms_body`, `sender_mobile_no`, 
					`user_mobile_no`, `image_path`, `user_id`, `delivery_status`, `source_app`) 
					VALUES (%s,%s,%s,%s,%s,%s,%s)""")
				sms_data = (body_text,'',phoneNo,image_url,u_id,'N',sourceApp)

				cursor.execute(sms_insert_query,sms_data)
				sms_queue.append({"user_id":u_id,
									"sms":body_text})
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "SMS Queue Details.",
								"status": "success"
								},
				"responseList":sms_queue}), status.HTTP_200_OK

@name_space1.route("/sendSMS")
class sendSMS(Resource):
	def get(self):
		connection = mysql.connect()
		cursor = connection.cursor()
		url = "http://enterprise.smsgupshup.com/GatewayAPI/rest"
		method = 'sendMessage'
		send_to = 'send_to'
		msg_type = 'TEXT'
		auth_scheme = 'PLAIN'
		smsformat = 'JSON'
		sms_response = []
		cursor.execute("""SELECT `sms_body`,`user_mobile_no`,`image_path`,`user_id` 
			FROM `sms_queue` WHERE `delivery_status` = 'N'""")

		sms_queue = cursor.fetchall()
		if sms_queue:
			for i in range(len(sms_queue)):
				sms_body = sms_queue[i][0]
				user_mobile_no = sms_queue[i][1]
				image_path = sms_queue[i][2]
				user_id = sms_queue[i][3]
				payload ="method={}&send_to={}&msg={}&msg_type={}&userid={}&auth_scheme={}&password={}&format={}".format(method,user_mobile_no,sms_body,
					msg_type,GUPSHUP_USERID,auth_scheme,GUPSHUP_PASSWORD,smsformat)
				postUrl = url+'?'+payload
				print(payload)
				response = requests.request("POST", postUrl)
				print(response.text)

				response = json.loads(response.text)['data']['response_messages']
				sms_response.append(response[0])

		return ({"attributes": {"status_desc": "Sent SMS Details.",
								"status": "success"
								},
				"responseList":sms_response}), status.HTTP_200_OK


@name_space2.route("/postCVToGetCVScore")
class postCVToGetCVScore(Resource):
	@api.expect(cv_score_model)
	def post(self):
		connection = mysql.connect()
		cursor = connection.cursor()
		details = request.get_json()
		filepath = details['cv_filepath']
		download_id = details['download_id'] 
		source_emailid = details['source_emailid']
		source_app = details['source_app']
		first_name = details['first_name']
		last_name = details['last_name']
		user_type = 'unpaid'
		url = 'http://rezscore.in/a/f32d75/grade'
		if filepath.startswith('http'):
			filep = urllib2.urlopen(filepath).read()
			file = {'resume': filep}
			r = requests.post(url, files=file)
		else:
			filename = filepath.split('\\')[-1]
			r = requests.post(url, files={'resume': (filename)})
		# print(resume)
		
		# print(r.text)
		text = r.text
		response_json = json.loads(json.dumps(xmltodict.parse(text)))

		try:
			rezscore_res = response_json['rezscore']['score']
			grade = rezscore_res['grade']
			grade_headline = rezscore_res['grade_headline']
			percentile = rezscore_res['percentile']
			brevity_score = rezscore_res['brevity_score']
			impact_score = rezscore_res['impact_score']
			depth_score = rezscore_res['depth_score']
			email = rezscore_res['email']
			phone = rezscore_res['phone']
			rez_id = rezscore_res['rez_id']
			tip = response_json['rezscore']['advice']['tip']
			if isinstance(tip, dict):
				tip_short = tip['short']
				tip_long = tip['long']
			else:
				tip_short = tip[0]['short']['#text']
				tip_long = tip[0]['long']
			date_of_registration = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
		except:
			pass

		cv_master_insert = ("""INSERT INTO `cv_master`(`first_name`,`last_name`,`mobile_no`, 
			`email_id`, `date_of_registration`, `cv_filepath`, `jp_username`, 
			`jp_password`, `source_app`, `source_emailid`, `download_id`, `user_type`) 
			VALUES  (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

		cv_master_data = (first_name,last_name,phone,email,date_of_registration,filepath,phone,phone,
			source_app,source_emailid,download_id,user_type)
		cursor.execute(cv_master_insert,cv_master_data)

		user_id = cursor.lastrowid

		score_insert_query = ("""INSERT INTO `cv_score_master`(`user_id`, `grade`, `grade_headline`, 
			`percentile`, `brevity_score`, `impact_score`, `depth_score`, `tip_short`, 
			`tip_long`, `rez_id`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")


		score_data = (user_id,grade,grade_headline,percentile,brevity_score,impact_score,
			depth_score,tip_short,tip_long,rez_id)

		cursor.execute(score_insert_query,score_data)

		connection.commit()
		cursor.close()
		print(rezscore_res)

		output_json = {"score":{
							"grade":grade,
							"grade_headline": grade_headline,
							"percentile": percentile,
							"brevity_score":brevity_score,
							"impact_score": impact_score,
							"depth_score": depth_score,
							"email": email,
							"phone": phone,
							"rez_id":rez_id,
							},

						"tip": {
							"short": tip_short,
							"long": tip_long
						},
						"user_id":user_id
					}
		mail_sub = 'Career'
		mail_body = 'Hi {},\nYour resume score is available. \
		Check your resume score and increase the chances of getting a new job. \
		Link'.format(first_name)
		try:
			email_url = 'http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com/flaskapp/job_portal/CVScore/sendMail'
			email_payload = {"mail_subject":mail_sub,
							"mail_body":mail_body,
							"image_url":"",
							"user_id":[user_id],
							"user_mail_id":[email]}

			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			# response = requests.post(email_url, data=json.dumps(email_payload), headers=headers)
		
		except Exception as e:
			raise e

		return ({"attributes": {"status_desc": "User Resume Details.",
								"status": "success"
								},
				"responseList":output_json}), status.HTTP_200_OK


@name_space1.route("/getCommunicationHistory/<string:from_date>/<string:to_date>/<string:contact_type>")
class getCommunicationHistory(Resource):
    def get(self, from_date, to_date, contact_type):
        ct = contact_type.split(',')

        if ct[0] == '0' or len(ct) == 3:
            email_res = getemailcomm(from_date, to_date)
            sms_res = getsmscomm(from_date, to_date)
            whatapp_res = getwhatsappcomm(from_date, to_date)
            return ({"attributes": {
                    "status_desc": "Communication History",
                    "status": "success"
                    },
                "responseList": [{'email': email_res},
                    		{'sms': sms_res},
                   			{'whatsapp': whatapp_res}
            					]
            		}), status.HTTP_200_OK

        elif len(ct) == 1:
            for c in ct:
                c = c.lower()
                if c == 'email':
                    email_res = getemailcomm(from_date, to_date)
                    print(email_res)
                    return ({"attributes": {
                        "status_desc": "Communication History",
                        "status": "success"
                    },
                        "responseList": [{'email': email_res}
                    				]}), status.HTTP_200_OK

                elif c == 'sms':
                    sms_res = getsmscomm(from_date, to_date)
                    return ({"attributes": {
                        "status_desc": "Communication History",
                        "status": "success"
                    },
                        "responseList": [{'sms': sms_res}
                    					]}), status.HTTP_200_OK

                elif c == 'whatsapp':
                    whatapp_res = getwhatsappcomm(from_date, to_date)

                    return ({"attributes": {
                        "status_desc": "Communication History",
                        "status": "success"
                    },
                        "responseList": [{'whatsapp': whatapp_res}
                    					]}), status.HTTP_200_OK

        elif len(ct) == 2:
            for e, c in enumerate(ct):
                c = c.lower().strip()
                ct[e] = c
            if 'email' in ct and 'sms' in ct:
                email_res = getemailcomm(from_date, to_date)
                sms_res = getsmscomm(from_date, to_date)
                return ({"attributes": {
                    "status_desc": "Communication History",
                    "status": "success"
                },
                    "responseList": [{'email': email_res},
                    				{'sms': sms_res}
                					]}), status.HTTP_200_OK

            elif 'email' in ct and 'whatsapp' in ct:
                sms_res = getsmscomm(from_date, to_date)
                whatapp_res = getwhatsappcomm(from_date, to_date)

                return ({"attributes": {
                    "status_desc": "Communication History",
                    "status": "success"
                },
                    "responseList": [{'email': email_res},
                    				{'whatsapp': whatapp_res}
                					]}), status.HTTP_200_OK

            elif 'whatsapp' in ct and 'sms' in ct:
                whatapp_res = getwhatsappcomm(from_date, to_date)
                sms_res = getsmscomm(from_date, to_date)

                return ({"attributes": {
                    "status_desc": "Communication History",
                    "status": "success"
                },
                    "responseList": [{'whatsapp': whatapp_res},
                    				{'sms': sms_res}
                					]}), status.HTTP_200_OK

        return ({"attributes": {
                    "status_desc": "Communication History",
                    "status": "success"
                },
                    "responseList": [{'email': []},
                    				{'sms': []},
				                    {'whatsapp': []}
                					]}), status.HTTP_200_OK



@name_space1.route("/getCVDashboardHistory/<string:from_date>/<string:to_date>")
class getCVDashboardHistory(Resource):
    def get(self, from_date, to_date):
    	connection = mysql.connect()
    	cursor = connection.cursor()
    	cv_list = []
    	if from_date == '0' and to_date == '0':
    		cursor.execute("""SELECT `cv_user_id`, concat(`first_name`,' ',`last_name`) username, 
				`mobile_no`,`email_id`,`date_of_registration`,`cv_filepath`,`source_app`,
				`source_emailid`,`user_type`FROM `cv_master`""")

    		cvs = cursor.fetchall()
    		if cvs:
    			desc = cursor.description
    			col_names = [col[0] for col in desc]
    			cv_list = [dict(izip(col_names, row)) for row in cvs]

    	else:
    		cursor.execute("""SELECT `cv_user_id`, concat(`first_name`,' ',`last_name`) username, 
				`mobile_no`,`email_id`,`date_of_registration`,`cv_filepath`,`source_app`,
				`source_emailid`,`user_type`FROM `cv_master` where date(`last_update_ts`) 
				BETWEEN %s and %s""",(from_date,to_date))

    		cvs = cursor.fetchall()

    		if cvs:
    			desc = cursor.description
    			col_names = [col[0] for col in desc]
    			cv_list = [dict(izip(col_names, row)) for row in cvs]

    	if cv_list:
    		for i in range(len(cv_list)):
    			cv_list[i]['date_of_registration'] = cv_list[i]['date_of_registration'].isoformat()

    	cursor.close()
    	
    	return ({"attributes": {
		            "status_desc": "CV Dashboard History",
		            "status": "success"
		        },
		            "responseList": cv_list}), status.HTTP_200_OK


@name_space1.route("/getCVDashboardHistoryByUserID/<string:user_id>/<string:contact_type>")
class getCVDashboardHistoryByUserID(Resource):
	def get(self, user_id, contact_type):
		connection = mysql.connect()
		cursor = connection.cursor()
		com_type = contact_type.split(',')
		mail_list = []
		sms_list = []
		whatsapp_list = []
		for i in range(len(com_type)):
			com_type[i] = com_type[i].lower()
		print(com_type)
		for i in range(len(com_type)):
			if 'email' in com_type[i]:
				cursor.execute("""SELECT `sender_mail_id`,`mail_subject`,`mail_body`,
		    		`user_mail_id`,`image_path`,`source_app` 
		    		FROM `mail_queue` WHERE `user_id` = %s""",(user_id))
				mail_com = cursor.fetchall()
				if mail_com:
					desc = cursor.description
					col_names = [col[0] for col in desc]
					mail_list = [dict(izip(col_names, row)) for row in mail_com]

			elif 'sms' in com_type[i]:
				cursor.execute("""SELECT `sms_body`,`sender_mobile_no`,`user_mobile_no`,
		    		`image_path`,`source_app` FROM `sms_queue` WHERE `user_id` = %s""",(user_id))
				sms_com = cursor.fetchall()
				if sms_com:
					desc = cursor.description
					col_names = [col[0] for col in desc]
					sms_list = [dict(izip(col_names, row)) for row in sms_com]

			elif 'whatsapp' in com_type[i]:
				cursor.execute("""SELECT `sender_phone_no`,`user_phone_no`,`msg_body`,`msg_title`,
		    		`image_path`,`source_app` FROM `whatsapp_queue` WHERE `user_id` = %s""",(user_id))

				whatsapp_com = cursor.fetchall()
				if whatsapp_com:
					desc = cursor.description
					col_names = [col[0] for col in desc]
					whatsapp_list = [dict(izip(col_names, row)) for row in whatsapp_com]
			else:
				cursor.execute("""SELECT `sender_mail_id`,`mail_subject`,`mail_body`,
	    			`user_mail_id`,`image_path`,`source_app`
	    			FROM `mail_queue` WHERE `user_id` = %s""",(user_id))
				mail_com = cursor.fetchall()
				if mail_com:
					desc = cursor.description
					col_names = [col[0] for col in desc]
					mail_list = [dict(izip(col_names, row)) for row in mail_com]

				cursor.execute("""SELECT `sms_body`,`sender_mobile_no`,`user_mobile_no`,
	    			`image_path`,`source_app` FROM `sms_queue` WHERE `user_id` = %s""",(user_id))
				sms_com = cursor.fetchall()
				if sms_com:
					desc = cursor.description
					col_names = [col[0] for col in desc]
					sms_list = [dict(izip(col_names, row)) for row in sms_com]

				cursor.execute("""SELECT `sender_phone_no`,`user_phone_no`,`msg_body`,`msg_title`,
	    			`image_path`,`source_app` FROM `whatsapp_queue` WHERE `user_id` = %s""",(user_id))

				whatsapp_com = cursor.fetchall()
				if whatsapp_com:
					desc = cursor.description
					col_names = [col[0] for col in desc]
					whatsapp_list = [dict(izip(col_names, row)) for row in whatsapp_com]



		# print(mail_list,sms_list)
		return ({"attributes": {"status_desc": "CV Dashboard Communication History",
                    			"status": "success"},
                    			"responseList": [{'email': mail_list},
                    				{'sms': sms_list},
                    				{'whatsapp': whatsapp_list}]}), status.HTTP_200_OK



if __name__ == '__main__':
	app.run(host='0.0.0.0')