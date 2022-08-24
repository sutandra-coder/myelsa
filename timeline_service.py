from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask import Blueprint

timeline = Blueprint('timeline',__name__)

app = Flask(__name__)
cors = CORS(app)
mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app.config['MYSQL_DATABASE_DB'] = 'creamson__lang_lab_b2c'
app.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'
mysql.init_app(app)

app.config['CORS_HEADERS'] = 'Content-Type'


@timeline.route('/getTimelineDetails/<student_id>')
@cross_origin()
def getTimelineDetails(student_id):
	# details = request.get_json()
	connection = mysql.connect()
	cursor = connection.cursor()
	try:
		cursor.execute("""SELECT a.`Activity_Desc`,am.`activity_mapping_id`
			FROM`activity`a, activity_mapping am, content_master cm,student_activity_n_content_tracking st,
			filetype f WHERE st.`content_master_id`=cm.`content_master_id` and
			st.`file_type_id`=f.`filetype_id` and a.`Activity_ID`=am.`Activity_ID` and 
			st.`activity_mapping_id`=am.`Activity_Mapping_ID` and 
			cm.`Activity_Mapping_ID`=am.`Activity_Mapping_ID` and
			st.`student_id`=%s GROUP by a.`Activity_Desc`""",(student_id))
		timeline_desc = cursor.description
		desc_names = [col[0] for col in timeline_desc]
		timeline_data = [dict(izip(desc_names, row)) for row in cursor.fetchall()]
		print(len(timeline_data[0]))
		session_id = []
		for i in range(len(timeline_data)):
			cursor.execute("""SELECT cm.`Content_Master_Name`,
				cm.`Content_Master_ID`,st.`student_id`,st.`Session_ID`,st.`level`,
				st.`student_activity_file_name`,st.`student_activity_path`,f.`FileType_Desc` 
				FROM`activity`a, activity_mapping am, content_master cm,student_activity_n_content_tracking st,
				filetype f WHERE st.`content_master_id`=cm.`content_master_id` and
				st.`file_type_id`=f.`filetype_id` and a.`Activity_ID`=am.`Activity_ID` and 
				st.`activity_mapping_id`=am.`Activity_Mapping_ID` and 
				cm.`Activity_Mapping_ID`=am.`Activity_Mapping_ID` and
				st.`student_id`=%s and st.`activity_mapping_id` =%s
				GROUP by st.`Session_ID`""",(student_id,timeline_data[i]['activity_mapping_id']))
			desc = cursor.description
			names = [col[0] for col in desc]
			# session_id.append([dict(izip(names, row)) for row in cursor.fetchall()])
			timeline_data[i]['session_dtls'] = [dict(izip(names, row)) for row in cursor.fetchall()]
	except:
		pass
	cursor.close()
	if timeline_data:
		return jsonify({"attributes": {
	    				"status_desc": "Timeline Activity Details.",
	    				"status": "success"
	    				},
	    				"responseList":{"ActivityDtls":timeline_data}})
	else:
		return jsonify({"attributes": {
	    				"status_desc": "Timeline Activity Details.",
	    				"status": "failure"
	    				},
	    				"responseList":{"ActivityDtls":timeline_data}})


if __name__ == '__main__':
	app.run(host='0.0.0.0',debug=True)