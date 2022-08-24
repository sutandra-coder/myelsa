from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask import Blueprint
from flask_restplus import Api, Resource, fields

app = Flask(__name__)
app1 = Flask(__name__)
cors = CORS(app)
mysql = MySQL()
mysql1 = MySQL()
contentwise_progress = Blueprint('contentwise_progress_api', __name__)
api = Api(contentwise_progress, version='1.0', title='MyElsa API',
    description='MyElsa API')
name_space = api.namespace('ContentProgress', description=':Content Progress')

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

@name_space.route("/getContentWiseProgress/<int:activity_id>/<int:user_id>")
class getContentWiseProgress(Resource):
	def get(self,activity_id,user_id):
		connection = mysql.connect()
		cursor = connection.cursor()
		assessment_data = []
		assessmentDtls = []
		cursor.execute("""SELECT `Class`,`Board` FROM `student` WHERE `Student_UserID` = %s""",(user_id))
		userDtls = cursor.fetchone()

		cursor.execute("""SELECT `Activity_Mapping_ID` FROM `activity_mapping` WHERE `Activity_ID` = %s and 
				`Activity_Category_ID` = 0 AND `Activity_Category_Type_ID` = 0 
				AND `Activity_Category_Sub_Type_ID` = 0""",(activity_id))

		activity_mapping_id = cursor.fetchone()
		if activity_mapping_id:
			activity_mapping_id = activity_mapping_id[0]
		print(activity_mapping_id)
		if userDtls and activity_mapping_id:
			user_class = userDtls[0]
			board_desc = userDtls[1]

			print(user_class,board_desc)
			cursor.execute("""SELECT `Content_Master_ID` FROM `content_rule` WHERE `Class` = %s 
				and `Board_ID` in(SELECT `Board_ID` FROM `board` WHERE `Board_Desc` = %s)  
				and `Activity_Mapping_ID` = %s""",(user_class,board_desc,activity_mapping_id))

			all_content_id = cursor.fetchall()
			content_id = []
			print(all_content_id)
			if all_content_id:
				for con_id in all_content_id:
					content_id.append(con_id[0])

			print(content_id)
			cursor.execute("""SELECT `Student_Id`,a.`Content_Master_Id`,cm.`Content_Master_Name`,
				CAST(AVG(`Marks`) as DECIMAL(10,2)) as Marks,`Status` 
				FROM `assessment_tracking` a, `content_master` cm WHERE `Student_Id`=%s and a.`Content_Master_Id` 
				in(SELECT `Content_Master_Id` from content_rule WHERE `Activity_Mapping_ID`=%s) 
				and `status` ='i' and a.`Content_Master_Id` NOT in (SELECT `Content_Master_Id` 
				FROM `assessment_tracking` WHERE `Student_Id`=%s and a.`Content_Master_Id` 
				in(SELECT `Content_Master_Id` from `content_rule` WHERE `Activity_Mapping_ID`=%s) 
				and `status` ='c' ) and cm.`Content_Master_ID` = a.`Content_Master_ID` group by a.`Content_Master_Id` 
				UNION SELECT %s as Student_Id,cr.`Content_Master_Id`, c.`Content_Master_Name`,"" as marks,'' as 'Status' 
				FROM content_rule cr , content_master c where class =%s and board_id in (SELECT `Board_ID` FROM `board`
				WHERE `Board_Desc` = %s) and cr.`Content_Master_Id` not in(SELECT Content_Master_Id 
				from assessment_tracking WHERE `Student_Id`=%s) AND cr.`Content_Master_Id` 
				in(SELECT `Content_Master_Id` from content_rule WHERE Activity_Mapping_ID=%s) 
				and c.`Content_Master_ID`=cr.`Content_Master_ID`""",(user_id,activity_mapping_id,
					user_id,activity_mapping_id,user_id,user_class,board_desc,user_id,activity_mapping_id))

			avg_marks = cursor.fetchall()
			if avg_marks:
				for m in avg_marks:
					assessment_data.append(m)
			# print(avg_marks)
			cursor.execute("""SELECT Student_Id,a.`Content_Master_Id`,cm.`Content_Master_Name`,(`Marks`),`Status` 
				FROM `assessment_tracking` a,`content_master` cm WHERE `Student_Id`=%s and a.`Content_Master_Id` not 
				in (SELECT `Content_Master_Id` FROM `assessment_tracking` WHERE `Student_Id`=%s 
				and a.`Content_Master_Id` in(SELECT `Content_Master_Id` from content_rule 
				WHERE Activity_Mapping_ID=%s)) and status ='c' and a.`Content_Master_Id`  
				in (SELECT `Content_Master_Id` FROM `assessment_tracking` WHERE `Student_Id`=%s 
				and a.`Content_Master_Id` in(SELECT `Content_Master_Id` from content_rule WHERE 
				Activity_Mapping_ID=%s) and status ='c' and cm.`Content_Master_ID` = a.`Content_Master_ID`)  
				UNION SELECT %s as Student_Id,cr.`Content_Master_Id`, c.`Content_Master_Name`,"" as marks,'' as 'Status' 
				FROM content_rule cr , content_master c where class =%s and board_id in (SELECT `Board_ID` FROM `board`
				WHERE `Board_Desc` = %s) and cr.`Content_Master_Id` not in(SELECT Content_Master_Id 
				from assessment_tracking WHERE `Student_Id`=%s) AND cr.`Content_Master_Id` 
				in(SELECT `Content_Master_Id` from content_rule WHERE Activity_Mapping_ID=%s) 
				and c.`Content_Master_ID`=cr.`Content_Master_ID`""",
				(user_id,user_id,activity_mapping_id,user_id,activity_mapping_id,user_id,
					user_class,board_desc,user_id,activity_mapping_id))

			no_marks = cursor.fetchall()
			if no_marks:
				for m in no_marks:
					assessment_data.append(m)
			# print(no_marks)
			cursor.execute("""SELECT Student_Id,a.`Content_Master_Id`,cm.`Content_Master_Name`,
				`Marks`,`Status` FROM `assessment_tracking` a,`content_master` cm 
				WHERE `Student_Id`=%s and a.`Content_Master_Id` 
				in(SELECT `Content_Master_Id` from content_rule WHERE Activity_Mapping_ID=%s) 
				and Status = 'c' and cm.`Content_Master_ID` = a.`Content_Master_ID`
				UNION SELECT %s as Student_Id,cr.`Content_Master_Id`, c.`Content_Master_Name`,"" as marks,'' as 'Status' 
				FROM content_rule cr , content_master c where class =%s and board_id in (SELECT `Board_ID` FROM `board`
				WHERE `Board_Desc` = %s) and cr.`Content_Master_Id` not in(SELECT Content_Master_Id 
				from assessment_tracking WHERE `Student_Id`=%s) AND cr.`Content_Master_Id` 
				in(SELECT `Content_Master_Id` from content_rule WHERE Activity_Mapping_ID=%s) 
				and c.`Content_Master_ID`=cr.`Content_Master_ID`""",
				(user_id,activity_mapping_id,user_id,user_class,board_desc,user_id,activity_mapping_id))

			full_marks = cursor.fetchall()
			if full_marks:
				for m in full_marks:
					assessment_data.append(m)
			# print(assessment_data)
			assessment_data = list(set(assessment_data))
			for data in assessment_data:
				assessmentDtls.append({"Student_Id":data[0],
										"Content_Master_Id":data[1],
										"Content_Master_Name":data[2],
										"Marks":data[3],
										"Status":data[4]})

		return ({"attributes": {
		    				"status_desc": "Progress Details.",
		    				"status": "success"
		    				},
		    				"responseList":assessmentDtls}), status.HTTP_200_OK

@name_space.route("/getAssessmentProgress/<int:content_master_id>/<int:user_id>")
class getAssessmentProgress(Resource):
	def get(self,content_master_id,user_id):
		connection = mysql.connect()
		cursor = connection.cursor()

		conn = mysql1.connect()
		cur = conn.cursor()

		assessment_data = []
		assessmentDtls = []
		cursor.execute("""SELECT `Class`,`Board` FROM `student` WHERE `Student_UserID` = %s""",(user_id))
		userDtls = cursor.fetchone()
		if userDtls:
			user_class = userDtls[0]
			board_desc = userDtls[1]


		cursor.execute("""SELECT ca.`Assessment_Id`, 'na' as Status, 
			`Content_Master_Id`,a.`Assessment_Type_ID`, 
        	ad.`Assessment_Type_Desc`,'' as `marks` FROM `content_assessment_mapping` ca,assessment a, 
        	assessment_type ad WHERE `Content_Master_ID` = %s and ca.`Assessment_Id` 
        	NOT in(SELECT `Assessment_ID` FROM `assessment_tracking` WHERE `Content_Master_ID` = %s 
        	and `Student_Id` = %s) and ca.`Assessment_Id` = a.`Assessment_Id` 
        	and a.`Assessment_Type_ID` = ad.`Assessment_Type_ID`""",
        	(content_master_id,content_master_id,user_id))

		not_attempted = cursor.fetchall()
		if not_attempted:
			for m in not_attempted:
				m = list(m)
				assessment_data.append(m)


		cursor.execute("""SELECT DISTINCT ast.`Assessment_Id`,'a' as Status,
		`Content_Master_Id`, a.`Assessment_Type_ID`,ad.`Assessment_Type_Desc` FROM `assessment_tracking` ast,
		assessment a,assessment_type ad WHERE ast.`Assessment_Id` in(SELECT `Assessment_ID` 
		FROM `content_assessment_mapping` WHERE `Content_Master_ID` = %s) and `Student_Id` = %s
		and ast.`Assessment_ID` = a.`Assessment_ID` 
		and a.`Assessment_Type_ID` = ad.`Assessment_Type_ID`""",(content_master_id,user_id))
        
		attempted = cursor.fetchall()
		if attempted:
			for m in attempted:
				m = list(m)
				cursor.execute("""SELECT max(`Marks`) FROM `assessment_tracking` 
					WHERE `Assessment_Id` =%s and student_id = %s""",(m[0],user_id))

				complete_marks = cursor.fetchone()
				if complete_marks:
					complete_marks = complete_marks[0]
					m.append(complete_marks)
					assessment_data.append(m)

		cursor.execute("""SELECT `Content_Detail_ID` FROM `content_details` 
			WHERE `Content_Master_ID` = %s""",(content_master_id))

		con_dtl_id = cursor.fetchall()
		dtl_id = []
		if con_dtl_id:
			for idx in range(len(con_dtl_id)):
			
				dtl_id.append(con_dtl_id[idx][0])

		
		dtl_id = tuple(dtl_id)
		print(dtl_id)
		cur.execute("""SELECT `Coins_transaction_Id` FROM `reward_transaction` 
			WHERE `Remarks` in %s and `INSTITUTION_USER_ID` = %s""",(dtl_id,user_id))

		video_watched = cur.fetchall()
		if video_watched:
			video_msg = 'true'
		else:
			video_msg = 'false'

		for data in assessment_data:
			assessmentDtls.append({"Assessment_Id":data[0],
									"Status":data[1],
									"content_master_id":data[2],
									"Assessment_Type_ID":data[3],
									"Assessment_Type_Desc":data[4],
									"Marks":data[5]})

		cursor.close()
		return ({"attributes": {
		    				"status_desc": "Progress Details.",
		    				"status": "success",
		    				"video_msg":video_msg
		    				},
		    				"responseList":assessmentDtls}), status.HTTP_200_OK

@name_space.route("/getAssessmentQuestionAndAnswer/<int:user_id>/<int:assessment_id>")
class getAssessmentQuestionAndAnswer(Resource):
	def get(self,assessment_id,user_id):

		connection = mysql.connect()
		cursor = connection.cursor()
		assessment_data = []
		assessmentDtls = []

		cursor.execute("""SELECT sa.`Question_ID`,q.`Question`,sa.`Option_ID` as Student_Option_ID ,
			o.`Option` as Right_Answer,sa.`Answer` as Student_Answer_Flag,
			an.`Option_ID` as Right_Option_Id FROM `student_answers` sa,question q, 
			options o,answer an WHERE `Assessment_ID` = %s and student_id = %s
			and sa.`Question_ID` = q.`Question_ID` and an.`Option_ID` = o.`Option_ID` 
			and sa.`Question_ID` = an.`Question_ID`""",(assessment_id,user_id))


		answer_dtls = cursor.fetchall()
		if answer_dtls:
			desc = cursor.description
			column_names = [col[0] for col in desc]
			assessmentDtls = [dict(izip(column_names, row)) for row in answer_dtls]

		cursor.close()
		return ({"attributes": {
		    				"status_desc": "Assessment Answer Details.",
		    				"status": "success"
		    				},
		    				"responseList":assessmentDtls}), status.HTTP_200_OK


if __name__ == '__main__':
	app.run(host='0.0.0.0')