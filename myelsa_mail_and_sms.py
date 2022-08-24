from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests
import pymysql
import smtplib
import imghdr
import io
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
# from urllib.request import urlopen
# import urllib2
app = Flask(__name__)
cors = CORS(app)
myelsa_sms_mail = Blueprint('myelsa_sms_mail_api', __name__)
api = Api(myelsa_sms_mail, version='1.0', title='MyElsa API',
    description='MyElsa API')
name_space = api.namespace('CommunicationAPI', description='SMS And Email')

def mysql_connection():
    connection = pymysql.connect(host='creamsonservices.com',
                                 user='creamson_langlab',
                                 password='Langlab@123',
                                 db='creamson_communication',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

def mysql_connection1():
    connection = pymysql.connect(host='creamsonservices.com',
                                 user='creamson_langlab',
                                 password='Langlab@123',
                                 db='creamson_logindb',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

app.config['CORS_HEADERS'] = 'Content-Type'

EMAIL_ADDRESS = 'communications@creamsonservices.com'
EMAIL_PASSWORD = 'CReam7789%$intELLi'


class DictModel(fields.Raw):
	def format(self, value):
		dictmodel = {}
		return dictmodel

communication_model = api.model('communication_model', {
	"sourceapp":fields.String(),
	"appParams": DictModel(),
	"mailParams":DictModel(),
	"role":fields.String(),
	"toMail":fields.String(),
	"toNumber":fields.String(),
	"userId": fields.Integer(),
		})


@name_space.route("/postCommunication")
class postCommunication(Resource):
	@api.expect(communication_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		conn = mysql_connection1()
		cur = conn.cursor()

		details = request.get_json()

		sourceapp = details['sourceapp']
		appParams = details['appParams']
		mailParams = details['mailParams']
		role = details['role']
		toMail = details['toMail']
		toNumber = details['toNumber']
		userId = details['userId']
		body_text = ''
		sms_body_text = ''
		cursor.execute("""SELECT `application_name`,`title`,`Recipient`,`email`,`Email_Body`,`Subject`,`sms`,
			`SMS_Body`,`App_Description`,`from_mailid`,`from_number`,`Dashboard_Id`,`email`,`sms` 
			FROM `configuration` WHERE `application_name` = %s""",(sourceapp))


		config_info = cursor.fetchone()

		mail_body = config_info['Email_Body']
		sms_body = config_info['SMS_Body']
		if userId > 0:
			cur.execute("""SELECT
						    `CITY`,
						    `DATE_OF_BIRTH`,
						    `EMAIL_ID`,
						    `FIRST_NAME`,
						    `GENDER`,
						    `IMAGE_URL`,
						    `LAST_NAME`,
						    `MIDDLE_NAME`,
						    `PINCODE`,
						    `PRIMARY_CONTACT_NUMBER`,
						    `SECONDARY_CONTACT_NUMBER`,
						    `STATE`,
						    `STREET_ADDRESS`,
						    `USER_TAX_ID`,
						    `USER_UNIQUE_ID`,
						    `address`,
						    `INSTITUTION_USER_NAME`
						FROM
						    `institution_user_credential`
						WHERE
						    `INSTITUTION_USER_ID` = %s""",(userId))

			user_info = cur.fetchone()
			city = user_info['CITY']
			DATE_OF_BIRTH = user_info['DATE_OF_BIRTH'] 
			EMAIL_ID = user_info['EMAIL_ID']
			FIRST_NAME = user_info['FIRST_NAME']
			GENDER = user_info['GENDER']
			IMAGE_URL = user_info['IMAGE_URL']
			LAST_NAME = user_info['LAST_NAME']
			MIDDLE_NAME = user_info['MIDDLE_NAME']
			PINCODE = user_info['PINCODE']
			PRIMARY_CONTACT_NUMBER = user_info['PRIMARY_CONTACT_NUMBER']
			SECONDARY_CONTACT_NUMBER = user_info['SECONDARY_CONTACT_NUMBER']
			STATE = user_info['STATE']
			STREET_ADDRESS = user_info['STREET_ADDRESS']
			USER_TAX_ID = user_info['USER_TAX_ID']
			USER_UNIQUE_ID = user_info['USER_UNIQUE_ID']
			address = user_info['address']
			fullName = FIRST_NAME + ' ' + LAST_NAME
			phoneno = user_info['INSTITUTION_USER_NAME']
			
			body_text = mail_body
			sms_body_text = sms_body
			
			for k,v in mailParams.items():
				body_text = mail_body.replace('{{'+k+'}}',v)
				sms_body_text = sms_body_text.replace('{{'+k+'}}',v)
			
			body_text = body_text.format(username = FIRST_NAME)
			sms_body_text = sms_body_text.format(username = FIRST_NAME)

			config_info['Email_Body'] = body_text
			config_info['SMS_Body'] = sms_body_text
			print(config_info['SMS_Body'])
			if config_info['email'] == 1:
				mail_res = send_email(config_info = config_info, user_info = user_info)
			if config_info['sms'] == 1:
				sms_res = send_sms(config_info = config_info, user_info = user_info)
		# elif userId == 0:
		# 	cur.execute("""SELECT
		# 				    `CITY`,
		# 				    `DATE_OF_BIRTH`,
		# 				    `EMAIL_ID`,
		# 				    `FIRST_NAME`,
		# 				    `GENDER`,
		# 				    `IMAGE_URL`,
		# 				    `LAST_NAME`,
		# 				    `MIDDLE_NAME`,
		# 				    `PINCODE`,
		# 				    `PRIMARY_CONTACT_NUMBER`,
		# 				    `SECONDARY_CONTACT_NUMBER`,
		# 				    `STATE`,
		# 				    `STREET_ADDRESS`,
		# 				    `USER_TAX_ID`,
		# 				    `USER_UNIQUE_ID`,
		# 				    `address`,
		# 				    `INSTITUTION_USER_NAME`
		# 				FROM
		# 				    `institution_user_credential`""")

		# 	user_info = cur.fetchall()
		# 	for i in range(len(user_info)): 
		# 		city = user_info[i]['CITY']
		# 		DATE_OF_BIRTH = user_info[i]['DATE_OF_BIRTH'] 
		# 		EMAIL_ID = user_info[i]['EMAIL_ID']
		# 		FIRST_NAME = user_info[i]['FIRST_NAME']
		# 		GENDER = user_info[i]['GENDER']
		# 		IMAGE_URL = user_info[i]['IMAGE_URL']
		# 		LAST_NAME = user_info[i]['LAST_NAME']
		# 		MIDDLE_NAME = user_info[i]['MIDDLE_NAME']
		# 		PINCODE = user_info[i]['PINCODE']
		# 		PRIMARY_CONTACT_NUMBER = user_info[i]['PRIMARY_CONTACT_NUMBER']
		# 		SECONDARY_CONTACT_NUMBER = user_info[i]['SECONDARY_CONTACT_NUMBER']
		# 		STATE = user_info[i]['STATE']
		# 		STREET_ADDRESS = user_info[i]['STREET_ADDRESS']
		# 		USER_TAX_ID = user_info[i]['USER_TAX_ID']
		# 		USER_UNIQUE_ID = user_info[i]['USER_UNIQUE_ID']
		# 		address = user_info[i]['address']
		# 		fullName = FIRST_NAME + ' ' + LAST_NAME
		# 		phoneno = user_info[i]['INSTITUTION_USER_NAME']

		# 		body_text = mail_body
		# 		sms_body_text = sms_body

		# 		for k,v in mailParams.items():
		# 			body_text = body_text.replace('{'+k+'}',v)
		# 			sms_body_text = sms_body_text.replace('{'+k+'}',v)

		# 		body_text = body_text.format(username = FIRST_NAME)

		# 		sms_body_text = sms_body_text.format(username = FIRST_NAME)
				
		# 		config_info['Email_Body'] = body_text

		# 		config_info['SMS_Body'] = sms_body_text
		# 		if config_info['email'] == 1:
		# 			mail_res = send_email(config_info = config_info, user_info = user_info[i])
		# 		if config_info['sms'] == 1:
		# 			sms_res = send_sms(config_info = config_info, user_info = user_info[i])
		else:
			if mailParams:
				for k,v in mailParams.items():
					mail_body = mail_body.replace('{{'+k+'}}',v)
					sms_body = sms_body.replace('{{'+k+'}}',v)
			body_text = mail_body
			sms_body_text = sms_body
			user_info = {}
			user_info['EMAIL_ID'] = toMail
			user_info['INSTITUTION_USER_NAME'] = toNumber
			config_info['Email_Body'] = body_text 
			config_info['SMS_Body'] = sms_body_text
			if config_info['email'] == 1:
				mail_res = send_email(config_info = config_info, user_info = user_info)
			if config_info['sms'] == 1:
				sms_res = send_sms(config_info = config_info, user_info = user_info)
		cursor.close()
		cur.close()
		if config_info['email'] == 1 and config_info['sms'] == 0: 
			return ({"attributes": {"status_desc": "Communication Status",
									"status": "success"
									},
					"responseList":{"mail_res":mail_res}}), status.HTTP_200_OK

		elif config_info['sms'] == 1 and config_info['email'] == 0: 
			return ({"attributes": {"status_desc": "Communication Status",
									"status": "success"
									},
					"responseList":{"sms_res":sms_res}}), status.HTTP_200_OK

		else:
			return ({"attributes": {"status_desc": "Communication Status",
									"status": "success"
									},
					"responseList":{"mail_res":mail_res,
									"sms_res":sms_res}}), status.HTTP_200_OK


def send_email(**kwagrs):
	connection = mysql_connection()
	cursor = connection.cursor()
	config_info = kwagrs['config_info']
	user_info = kwagrs['user_info']
	res = 'Failure. Wrong MailId or SourceApp.'

	if user_info['EMAIL_ID'] and config_info['application_name']:
		msg = MIMEMultipart()
		msg['Subject'] = config_info['Subject']
		msg['From'] = EMAIL_ADDRESS
		msg['To'] = user_info['EMAIL_ID']

		html = config_info['Email_Body']
		part1 = MIMEText(html, 'html')
		msg.attach(part1)
		try:
			smtp = smtplib.SMTP('mail.creamsonservices.com', 587)
			smtp.starttls()
			smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
			smtp.sendmail(EMAIL_ADDRESS, user_info['EMAIL_ID'], msg.as_string())
			
			res = {"status":'Success'}
			sent = 'Y'
			
		except Exception as e:
			res = {"status":'Failure'}
			sent = 'N'
			# raise e
		smtp.quit()
		mailmessage_insert_query = ("""INSERT INTO `mails`(`tomail`, `subject`, `body`, 
			`sourceapp`, `sent`) VALUES (%s,%s,%s,%s,%s)""")
		mail_data = (user_info['EMAIL_ID'],config_info['Subject'],html,
			config_info['application_name'],sent)
		cursor.execute(mailmessage_insert_query,mail_data)
	connection.commit()
	cursor.close()
	
	return res


def send_sms(**kwagrs):
	connection = mysql_connection()
	cursor = connection.cursor()
	config_info = kwagrs['config_info']
	user_info = kwagrs['user_info']
	res = {"status":'Failure. Wrong MailId or SourceApp.'}
	url = "http://cloud.smsindiahub.in/vendorsms/pushsms.aspx?"
	user = 'creamsonintelli'
	password = 'denver@1234'
	msisdn = user_info['INSTITUTION_USER_NAME']
	sid = 'CRMLTD'
	msg = config_info['SMS_Body']
	fl = '0'
	gwid = '2'
	payload ="user={}&password={}&msisdn={}&sid={}&msg={}&fl={}&gwid={}".format(user,password,
		msisdn,sid,msg,fl,gwid)
	postUrl = url+payload
	print(msisdn,msg)
	if user_info['INSTITUTION_USER_NAME'] and config_info['application_name']:
		response = requests.request("POST", postUrl)

		sms_response = json.loads(response.text)['ErrorMessage']
		res = {"status":sms_response}
	if res['status'] == 'Success':
		sent = 'Y'
	else:
		sent = 'N'
	smsmessage_insert_query = ("""INSERT INTO `smsmessages`(`tonumber`, `message`, `sourceapp`,`sent`) 
		VALUES (%s,%s,%s,%s)""")
	sms_data = (msisdn,msg,config_info['application_name'],sent)
	cursor.execute(smsmessage_insert_query,sms_data)
	connection.commit()
	cursor.close()
	return res