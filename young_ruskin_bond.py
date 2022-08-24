from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask import Blueprint
import requests

yrb = Blueprint('yrb',__name__)

app = Flask(__name__)
cors = CORS(app)
mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app.config['MYSQL_DATABASE_DB'] = 'creamson__lang_lab_b2c'
app.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'
mysql.init_app(app)

app.config['CORS_HEADERS'] = 'Content-Type'

@yrb.route('/getYoungRBDetails/<int:student_id>')
@cross_origin()
def getYoungRBDetails(student_id):
	connection = mysql.connect()
	cursor = connection.cursor()
	try:
		cursor.execute("""SELECT `Student_ID`, `FilePath`, `FileName`, `FileType_Desc`,
			`FileType_Extension`, `Active_Submission`, `Last_Update_ID`, `Last_Update_TS` 
			FROM `young_ruskin_bond` WHERE `Student_ID` = %s """,(student_id))
		youngRB_desc = cursor.description
		desc_names = [col[0] for col in youngRB_desc]
		youngRB_data = [dict(izip(desc_names, row)) for row in cursor.fetchall()]
	except:
		pass
	cursor.close()

	return jsonify({"attributes": {
    				"status_desc": "Young Ruskin Bond Details.",
    				"status": "success"
    				},
    				"responseList":{"ActivityDtls":youngRB_data}}), status.HTTP_200_OK

@yrb.route('/postYoungRBDetails',methods=['POST'])
@cross_origin()
def postYoungRBDetails():
	details = request.get_json()
	connection = mysql.connect()
	cursor = connection.cursor()
	if request.method == 'POST':
		try:
			yrb_insert_query = ("""INSERT INTO `young_ruskin_bond`(`Student_ID`, `FilePath`, 
				 `FileName`, `FileType_Desc`, `FileType_Extension`, `Active_Submission`) 
				VALUES (%s,%s,%s,%s,%s,%s)""")
			if details['Student_ID']:
				youngRB_data = (details['Student_ID'],details['FilePath'],details['FileName'],
					details['FileType_Desc'],details['FileType_Extension'],details['Active_Submission'])
				cursor.execute(yrb_insert_query,youngRB_data)
				url = 'http://creamsonservices.com:8080/CommunicationModule2/sendMailMessage'
				data = {
						  'mailDetails': [
						    {
						      'appParams': {},
						      'mailParams': {},
						      'role': 's1',
						      'toMail': '',
						      'toNumber': '',
						      'userId': details['Student_ID']
						    }
						  ],
						  'sourceApp': 'YRBUpload'
						}
				headers = {'Content-type':'application/json', 'Accept':'application/json'}
				response = requests.post(url, data=json.dumps(data), headers=headers)
			else:
				return jsonify({"attributes": {
		    				"status_desc": "Young Ruskin Bond Details.",
		    				"status": "failure",
		    				"message": "No Student ID Found"
		    				},
		    				"responseList":{"ActivityDtls":details}}), status.HTTP_404_NOT_FOUND
		except:
			pass
		cursor.close()
		if details['Student_ID']:
			return jsonify({"attributes": {
		    				"status_desc": "Young Ruskin Bond Details.",
		    				"status": "success"
		    				},
		    				"responseList":{"ActivityDtls":details}}), status.HTTP_200_OK
		else:
			return jsonify({"attributes": {
		    				"status_desc": "Young Ruskin Bond Details.",
		    				"status": "failure"
		    				},
		    				"responseList":{"ActivityDtls":details}}), status.HTTP_404_NOT_FOUND


@yrb.route('/updateYoungRBDetails',methods=['PUT'])
@cross_origin()
def updateYoungRBDetails():
	details = request.get_json()
	student_id = details['Student_ID']
	filetype = details['FileType_Desc']
	connection = mysql.connect()
	cursor = connection.cursor()
	last_update_ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
	if request.method == 'PUT':
		try:
			if details['Student_ID'] and details['FileType_Desc']:
				yrb_update_query = ("""UPDATE `young_ruskin_bond` SET `FilePath`= %s,
					`FileName`= %s, `Last_Update_TS` = %s WHERE `Student_ID` = %s and `FileType_Desc` = %s""")
				youngRB_update_data = (details['FilePath'],details['FileName'],last_update_ts,student_id,filetype)
				cursor.execute(yrb_update_query,youngRB_update_data)
				url = 'http://creamsonservices.com:8080/CommunicationModule2/sendMailMessage'
				data = {
						  'mailDetails': [
						    {
						      'appParams': {},
						      'mailParams': {},
						      'role': 's1',
						      'toMail': '',
						      'toNumber': '',
						      'userId': details['Student_ID']
						    }
						  ],
						  'sourceApp': 'YRBUpload'
						}
				headers = {'Content-type':'application/json', 'Accept':'application/json'}
				response = requests.post(url, data=json.dumps(data), headers=headers)
			else:
				return jsonify({"attributes": {
		    				"status_desc": "Young Ruskin Bond Details.",
		    				"status": "failure",
		    				"message": "No Student or FileType ID Found"
		    				},
		    				"responseList":{"ActivityDtls":details}}), status.HTTP_404_NOT_FOUND
		except:
			pass
		cursor.close()
		if details['Student_ID']:
			return jsonify({"attributes": {
		    				"status_desc": "Young Ruskin Bond Details.",
		    				"status": "success"
		    				},
		    				"responseList":{"ActivityDtls":details}}), status.HTTP_200_OK
		else:
			return jsonify({"attributes": {
		    				"status_desc": "Young Ruskin Bond Details.",
		    				"status": "failure",
		    				"message": "No Student ID Found"
		    				},
		    				"responseList":{"ActivityDtls":details}}), status.HTTP_404_NOT_FOUND


@yrb.route('/updateActiveSubmission',methods=['PUT'])
@cross_origin()
def updateActiveSubmission():
	details = request.get_json()
	student_id = details['Student_ID']
	filetype = details['FileType_Desc']
	connection = mysql.connect()
	cursor = connection.cursor()
	last_update_ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
	if request.method == 'PUT':
		try:
			if details['Student_ID'] and details['FileType_Desc']:
				yrb_update_query = ("""UPDATE `young_ruskin_bond` SET `Active_Submission` = %s,
					`Last_Update_TS` = %s WHERE `Student_ID` = %s and `FileType_Desc` = %s""")
				youngRB_update_data = (details['Active_Submission'],last_update_ts,student_id,filetype)
				cursor.execute(yrb_update_query,youngRB_update_data)
				yrb_other_update_query = ("""UPDATE `young_ruskin_bond` SET `Active_Submission` = %s,
					`Last_Update_TS` = %s WHERE `Student_ID` = %s and `FileType_Desc` != %s""")
				youngRB_other_update_data = (0,last_update_ts,student_id,filetype)
				cursor.execute(yrb_other_update_query,youngRB_other_update_data)
				url = 'http://creamsonservices.com:8080/CommunicationModule2/sendMailMessage'
				data = {
						  'mailDetails': [
						    {
						      'appParams': {},
						      'mailParams': {},
						      'role': 's1',
						      'toMail': '',
						      'toNumber': '',
						      'userId': details['Student_ID']
						    }
						  ],
						  'sourceApp': 'YRBSubmit'
						}
				headers = {'Content-type':'application/json', 'Accept':'application/json'}
				response = requests.post(url, data=json.dumps(data), headers=headers)
			else:
				return jsonify({"attributes": {
		    				"status_desc": "Young Ruskin Bond Details.",
		    				"status": "failure",
		    				"message": "No Student or FileType ID Found"
		    				},
		    				"responseList":{"ActivityDtls":details}}), status.HTTP_404_NOT_FOUND
		except:
			pass
		cursor.close()
		if details['Student_ID']:
			return jsonify({"attributes": {
		    				"status_desc": "Young Ruskin Bond Details.",
		    				"status": "success"
		    				},
		    				"responseList":{"ActivityDtls":details}}), status.HTTP_200_OK
		else:
			return jsonify({"attributes": {
		    				"status_desc": "Young Ruskin Bond Details.",
		    				"status": "failure",
		    				"message": "No Student ID Found"
		    				},
		    				"responseList":{"ActivityDtls":details}}), status.HTTP_404_NOT_FOUND


@yrb.route('/getJoinContest')
@cross_origin()
def getJoinContest():
	connection = mysql.connect()
	cursor = connection.cursor()
	try:
		cursor.execute("""SELECT `Join ID`, `Contest_Name`, `Join_Contest` FROM `join_contest`""")
		join_desc = cursor.description
		desc_names = [col[0] for col in join_desc]
		join_data = [dict(izip(desc_names, row)) for row in cursor.fetchall()]
	except:
		pass
	cursor.close()
	
	return jsonify({"attributes": {
    				"status_desc": "Join Contest Status.",
    				"status": "success"
    				},
    				"responseList":{"JoinContestDtls":join_data}}), status.HTTP_200_OK


	
if __name__ == '__main__':
	app.run(host='0.0.0.0')