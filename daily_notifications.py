from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask import Blueprint
from flask_restplus import Api, Resource, fields, Namespace
import requests


app = Flask(__name__)
app1 = Flask(__name__)
app2 = Flask(__name__)
app3 = Flask(__name__)
cors = CORS(app)
mysql = MySQL()
mysql1 = MySQL()
mysql2 = MySQL()
mysql3 = MySQL()
daily_notifications = Blueprint('notification_api', __name__)
api = Api(daily_notifications, version='1.0', title='MyElsa API',
    description='MyElsa API')
name_space = api.namespace('DailyNotifications', description='Daily Notifications')


app.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app.config['MYSQL_DATABASE_DB'] = 'creamson_lab_lang1'
app.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'
mysql.init_app(app)

app1.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app1.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app1.config['MYSQL_DATABASE_DB'] = 'creamson_logindb'
app1.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'
mysql1.init_app(app1)

app2.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app2.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app2.config['MYSQL_DATABASE_DB'] = 'creamson__lang_lab_b2c'
app2.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'
mysql2.init_app(app2)

app3.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app3.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app3.config['MYSQL_DATABASE_DB'] = 'creamson_communication'
app3.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'
mysql3.init_app(app3)

app.config['CORS_HEADERS'] = 'Content-Type'


@name_space.route("/sendWOTDNotification/<user_id>")
class sendWOTDNotification(Resource):
	def get(self,user_id):
		connection = mysql2.connect()
		cursor = connection.cursor()
		current_date = datetime.now().strftime('%Y-%m-%d')
		try:
			cursor.execute("""SELECT Video_Name,Video_Path FROM `word_of_the_day_list` WHERE `WOTD_ID` in 
				(SELECT `WOTD_ID` FROM `schedule_table` WHERE `Schedule_Date` = %s)""",(current_date))
			wotd_desc = cursor.description
			desc_names = [col[0] for col in wotd_desc]
			wotd_data = [dict(izip(desc_names, row)) for row in cursor.fetchall()]
			url = 'http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com:8080/BroadCastMessagingApp/broadCastMessage'
			data = {
					  "appName": "WOTD",
					  "endingUserId": 0,
					  "imageUrl": wotd_data[0]['Video_Path'],
					  "noOfuser": 0,
					  "startingUserId": 0,
					  "userId": user_id
					}
			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			response = requests.post(url, data=json.dumps(data), headers=headers)
			print(response.status_code)
		except:
			pass
		cursor.close()
		return ({"attributes": {
	    				"status_desc": "Word Of The Day Details.",
	    				"status": "success"
	    				},
	    				"responseList":{"WOTDDtls":wotd_data}}), status.HTTP_200_OK


@name_space.route("/usedMyELSATodayNotification/<user_id>")
class usedMyELSATodayNotification(Resource):
	def get(self,user_id):
		try:
			url = 'http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com:8080/BroadCastMessagingApp/broadCastMessage'
			data = {
					  "appName": "DAILYUSE",
					  "endingUserId": 0,
					  "imageUrl": "http://creamsonservices.com/Image/notification_images/Did_you_use_myelsa_today.png",
					  "noOfuser": 0,
					  "startingUserId": 0,
					  "userId": user_id
					}
			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			response = requests.post(url, data=json.dumps(data), headers=headers)
			response_list = json.loads(response.text)
			r_res = response_list['responseList']
			r = {"status : APP Message":r_res[0]['status : APP Message']}
			# print(response.status_code,json.loads(response_list))
		except:
			pass
		return ({"attributes": {
	    				"status_desc": "Have you used myELSA Today?",
	    				"status": "success"
	    				},
	    				"responseList":{"usedMyELSADtls":r}}), status.HTTP_200_OK

@name_space.route("/sendDailyContestNotification")
class sendDailyContestNotification(Resource):
	def get(self):
		conn = mysql1.connect()
		cur = conn.cursor()
		current_date = datetime.now().strftime('%Y-%m-%d')
		try:
			cur.execute("""SELECT `INSTITUTION_USER_ID` FROM `institution_user_credential` 
				WHERE `INSTITUTION_USER_ID` NOT in (SELECT `Student_ID` from `student_contest_tracking` 
				WHERE `Date` = %s)""",(current_date))
			student_id = [row for row in cur.fetchall()]
			idx = []
			for i in student_id:
				idx.append(i[0])
			print(idx)
			for i in range(len(idx)):
				print(idx[i])
				url = 'http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com:8080/BroadCastMessagingApp/broadCastMessage'
				data = {
						  "appName": "PLCNTST",
						  "endingUserId": 0,
						  "imageUrl": "http://creamsonservices.com/Image/notification_images/Daily_Contest.png",
						  "noOfuser": 0,
						  "startingUserId": 0,
						  "userId": idx[i]
						}
				headers = {'Content-type':'application/json', 'Accept':'application/json'}
				response = requests.post(url, data=json.dumps(data), headers=headers)
			response_list = json.loads(response.text)
			r_res = response_list['responseList']
			r = {"status : APP Message":r_res[0]['status : APP Message']}
			print(response.status_code)
		except:
			pass
		cur.close()
		return ({"attributes": {
	    				"status_desc": "Daily Contest Notification.",
	    				"status": "success"
	    				},
	    				"responseList":{"DailyContestDtls":r}}), status.HTTP_200_OK


@name_space.route("/sendWeHaveMissedYouNotification")
class sendWeHaveMissedYouNotification(Resource):
	def get(self):
		conn = mysql1.connect()
		cur = conn.cursor()
		current_date = datetime.now().strftime('%Y-%m-%d')
		try:
			cur.execute("""SELECT `INSTITUTION_USER_ID` FROM `institution_user_credential` 
				WHERE `INSTITUTION_USER_ID` NOT in (SELECT DISTINCT`INSTITUTION_USER_ID` 
				FROM `institution_user_tracking` WHERE DATE(`last_update_ts`) 
				BETWEEN subdate(CURRENT_DATE,2) AND (CURRENT_DATE))""")
			student_id = [row for row in cur.fetchall()]
			idx = []
			for i in student_id:
				idx.append(i[0])
			print(idx)
			for i in range(len(idx)):
				print(idx[i])
				url = 'http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com:8080/BroadCastMessagingApp/broadCastMessage'
				data = {
						  "appName": "MISSEDYOU",
						  "endingUserId": 0,
						  "imageUrl": "http://creamsonservices.com/Image/notification_images/we_have_missed_you.png",
						  "noOfuser": 0,
						  "startingUserId": 0,
						  "userId": idx[i]
						}
				headers = {'Content-type':'application/json', 'Accept':'application/json'}
				response = requests.post(url, data=json.dumps(data), headers=headers)
			response_list = json.loads(response.text)
			r_res = response_list['responseList']
			r = {"status : APP Message":r_res[0]['status : APP Message']}
			print(response.status_code)
		except:
			pass
		cur.close()
		return ({"attributes": {
	    				"status_desc": "We have missed you notification.",
	    				"status": "success"
	    				},
	    				"responseList":{"MissedUDtls":r}}), status.HTTP_200_OK

@name_space.route("/sendSummaryNotification")
class sendSummaryNotification(Resource):
	def get(self):
		connection = mysql.connect()
		cursor = connection.cursor()
		conn = mysql1.connect()
		cur = conn.cursor()
		current_date = datetime.now().strftime('%Y-%m-%d')
		try:
			cursor.execute("""SELECT GROUP_CONCAT(cm.`Content_Master_Name`),track.`Student_ID` 
				FROM `student_activity_n_content_tracking` track,content_master cm 
				WHERE cm.`Content_Master_ID`=track.`Content_Master_ID`
				and DATE(track. `Last_Update_TS`) = %s
				GROUP by track.`student_id`""",(current_date))
			trending_topics = [row for row in cursor.fetchall()]
			print(trending_topics)
			
			for i in range(len(trending_topics)):
				topic_name = trending_topics[i][0]
				idx = trending_topics[i][1]
				print(idx)
				cur.execute("""SELECT `FIRST_NAME` FROM `institution_user_credential` 
					WHERE `INSTITUTION_USER_ID` = %s""",(idx))
				name = cur.fetchone()[0]
				print(trending_topics[i][0],trending_topics[i][1],name)
				url = 'http://creamsonservices.com:8080/CommunicationModule2/sendMailMessage'
				data = {
						  'mailDetails': [
						    {
						      'appParams': {},
						      'mailParams': {"summary":trending_topics[i][0],
						      				"userName":name},
						      'role': 's1',
						      'toMail': '',
						      'toNumber': '',
						      'userId': trending_topics[i][1]
						    }
						  ],
						  'sourceApp': 'SUMMARY'
						}
				headers = {'Content-type':'application/json', 'Accept':'application/json'}
				response = requests.post(url, data=json.dumps(data), headers=headers)
			response_list = json.loads(response.text)
			r_res = response_list['responseList']
			r = {"status : APP Message":r_res[0]['status : APP Message']}
			print(response.status_code)
		except:
			pass
		cursor.close()
		cur.close()
		return ({"attributes": {
	    				"status_desc": "Daily Contest Notification.",
	    				"status": "success"
	    				},
	    				"responseList":{"DailyContestDtls":r}}), status.HTTP_200_OK


@name_space.route("/sendTrendingTopicNotification")
class sendTrendingTopicNotification(Resource):
	def get(self):
		connection = mysql.connect()
		cursor = connection.cursor()
		conn = mysql1.connect()
		cur = conn.cursor()
		current_date = datetime.now().strftime('%Y-%m-%d')
		try:
			cur.execute("""SELECT im.`INSTITUTION_USER_ID`, i.`FIRST_NAME` 
				FROM `institution_user_credential_master` im,`institution_user_credential` i 
				WHERE im.`INSTITUTION_USER_ROLE`='S1' and i.`INSTITUTION_USER_ID`= im.`INSTITUTION_USER_ID`""")
			userdtls = [row for row in cur.fetchall()]
			for i in range(len(userdtls)):
				user_id = userdtls[i][0]
				user_name = userdtls[i][1]
				cursor.execute("""SELECT cm.`Content_Master_Name`,track.`Content_Master_ID`,
					count(track.`Content_Master_ID`) FROM `student_activity_n_content_tracking`track,
					content_master cm WHERE cm.`Content_Master_ID`=track.`Content_Master_ID` 
					AND DATE(track.`Last_Update_TS`) = CURRENT_DATE 
					and track.`Student_ID` in (SELECT `Student_UserID` FROM `student` 
					WHERE `Class` IN (SELECT `Class` FROM `student` WHERE `Student_UserID` = %s) 
					AND `Board`in(SELECT `Board` FROM `student` WHERE `Student_UserID` = %s)) 
					GROUP BY track.`Content_Master_ID` ORDER BY COUNT(track.`Content_Master_ID`) 
					DESC LIMIT 1""",(user_id,user_id))
				contentdtls = [row for row in cursor.fetchall()]
				for j in range(len(contentdtls)):
					content_name = contentdtls[j][0]
					print(user_id,user_name,content_name)
					url = 'http://creamsonservices.com:8080/CommunicationModule2/sendMailMessage'
					data = {
							  'mailDetails': [
							    {
							      'appParams': {},
							      'mailParams': {"topic":content_name,
							      				"userName":user_name},
							      'role': 's1',
							      'toMail': '',
							      'toNumber': '',
							      'userId': user_id
							    }
							  ],
							  'sourceApp': 'TRENDING'
							}
					headers = {'Content-type':'application/json', 'Accept':'application/json'}
					response = requests.post(url, data=json.dumps(data), headers=headers)
				response_list = json.loads(response.text)
				r_res = response_list['responseList']
				r = {"status : APP Message":r_res[0]['status : APP Message']}
				print(response.status_code)
		except:
			pass
		cursor.close()
		cur.close()
		return ({"attributes": {
	    				"status_desc": "Daily Contest Notification.",
	    				"status": "success"
	    				},
	    				"responseList":{"DailyContestDtls":'r'}}), status.HTTP_200_OK

@name_space.route("/youngRuskinBondNotification/<user_id>")
class youngRuskinBondNotification(Resource):
	def get(self,user_id):
		connection = mysql1.connect()
		cursor = connection.cursor()
		product_code = 'YNGRB'
		try:
			cursor.execute("""SELECT `Dashboard_ID` FROM `product` 
				WHERE `Product_CODE` = %s""",(product_code))
			dashboard_id = cursor.fetchone()[0]
			print(dashboard_id)

			url = 'http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com:8080/BroadCastMessagingApp/broadCastMessage'
			data = {
					  "appName": product_code,
					  "endingUserId": 0,
					  "imageUrl": "",
					  "noOfuser": 0,
					  "startingUserId": 0,
					  "userId": user_id
					}
			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			response = requests.post(url, data=json.dumps(data), headers=headers)
			print(response.status_code)
		except:
			pass
		cursor.close()
		return ({"attributes": {
	    				"status_desc": "Young Ruskin Bond.",
	    				"status": "success"
	    				},
	    				"responseList":{"dashboard_id":dashboard_id}}), status.HTTP_200_OK

@name_space.route("/VoteYourTeacher/<user_id>")
class VoteYourTeacher(Resource):
	def get(self,user_id):
		
		url = 'http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com:8080/BroadCastMessagingApp/broadCastMessage'
		data = {
				  "appName": 'ThnkuTchr',
				  "endingUserId": 0,
				  "imageUrl": "https://creamsonservices.com/Image/notification_images/thankuteacher.png",
				  "noOfuser": 0,
				  "startingUserId": 0,
				  "userId": user_id
				}
		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		response = requests.post(url, data=json.dumps(data), headers=headers)
		print(response.status_code)
		return ({"attributes": {
	    				"status_desc": "Thank You Teacher Details",
	    				"status": "success"
	    				},
	    				"responseList":'Success'}), status.HTTP_200_OK


@name_space.route("/sendCredentials/<int:institution_id>/<string:institution_name>/<string:message>")
class sendCredentials(Resource):
	def get(self,institution_id,institution_name,message):
		connection = mysql1.connect()
		cursor = connection.cursor()

		cursor.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`) as 'fullname',
			`INSTITUTION_USER_ID`,`INSTITUTION_USER_NAME`,`INSTITUTION_USER_PASSWORD`,`PRIMARY_CONTACT_NUMBER` 
			FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` 
			in (SELECT `INSTITUTION_USER_ID` FROM `institution_user_credential_master` 
			WHERE `INSTITUTION_ID` = %s)""",(institution_id))

		userList = cursor.fetchall()
		resList = []
		url = 'http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com/flaskapp/myelsa_communication/CommunicationAPI/postCommunication'
		# url = 'http://127.0.0.1:5000/myelsa_communication/CommunicationAPI/postCommunication'
		
		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		

		if userList:
			for uid,user in enumerate(userList):
				print(user[0],user[1],user[2],user[3])
				data = {
						  "appParams": {},
						  "userId": -1,
						  "sourceapp": "SENDCREDS",
						  "toMail": "",
						  "role": "S1",
						  "toNumber": user[4],
						  "mailParams": {"fullname":user[0],
						  					"institution_name":institution_name,
						  					"userName":user[2],
						  					"pwd":user[3],
						  					"custmessage":message}
						}

				response = requests.post(url, data=json.dumps(data), headers=headers).json()
				print(response)
				userRes = user[2]+'-'+response['responseList']['sms_res']['status']
				resList.append(userRes)
				# open('sms_sent_to.txt','a').write(user[2]+'-'+response['responseList']['sms_res']['status']+'\n')
		return resList




@name_space.route("/workshopInvitation")
class workshopInvitation(Resource):
	def get(self):
		connection = mysql1.connect()
		cursor = connection.cursor()

		conn = mysql3.connect()
		cur = conn.cursor()

		cur.execute("""SELECT `tonumber` FROM `smsmessages` WHERE `sourceapp` = 'WRKSHPSMS'""")
		sentTo = cur.fetchall()
		sentNum = []
		for sid in range(len(sentTo)):
			sentNum.append(sentTo[sid][0])
		# print(tuple(sentNum))
		sentNumTuple = tuple(sentNum)
		userList = []
		cursor.execute("""SELECT DISTINCT icm.`INSTITUTION_USER_ID` FROM 
			`institution_user_credential_master` icm INNER JOIN `institution_user_credential` ic 
			on icm.`INSTITUTION_USER_ID` = ic.`INSTITUTION_USER_ID` INNER JOIN `teacher_dtls` td on 
			icm.`INSTITUTION_USER_ID` = td.`INSTITUTION_USER_ID_TEACHER` WHERE `INSTITUTION_USER_ROLE` 
			in ('A1', 'TA') and `PRIMARY_CONTACT_NUMBER` not in %s 
			ORDER BY icm.`INSTITUTION_USER_ID` ASC""",(sentNumTuple,))

		userList = cursor.fetchall()

		# print(userList)
		url = 'http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com/flaskapp/myelsa_communication/CommunicationAPI/postCommunication'
		# url = 'http://127.0.0.1:5000/myelsa_communication/CommunicationAPI/postCommunication'
		
		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		
		sentList = []
		try:
			if userList:
				for uid,user in enumerate(userList):
					data = {
							  "appParams": {},
							  "userId": user[0],
							  "sourceapp": "WRKSHPSMS",
							  "toMail": "",
							  "role": "T1",
							  "toNumber": "",
							  "mailParams": {}
							}

					response = requests.post(url, data=json.dumps(data), headers=headers).json()
					sentStatus = str(user[0])+'-'+response['responseList']['sms_res']['status']
					sentList.append(sentStatus)
		except:
			pass
		return sentList



if __name__ == '__main__':
	app.run(host='0.0.0.0',debug=True)
