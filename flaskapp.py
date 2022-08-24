from flask import Flask, request, jsonify, json
from flaskext.mysql import MySQL
from jinja2._compat import izip
from datetime import datetime
from flask_api import status
from flask_cors import CORS, cross_origin
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
# from tally_service import tally_api
from timeline_service import timeline
from young_ruskin_bond import yrb
# from yrb_swagger import youngRB_blueprint
# from validate_coupon import coupon
# from downloads_service import analysis
from user_tracking_service import user_tracking
# from board_and_class_registrations import myelsa_registrations
# from tally_service import tally_dms
from daily_notifications import daily_notifications
from onboard_teacher import onboarding_teachers
# from ocr_service import ocr_service
from reading_service import reading_service
from text_to_speech import text_to_speech
#from similarity_analysis import simi
from user_product_time_dis import time_discount
from student_favorite import student_favorite
from elsa_avatar import avatar
from avatar_polls import avatar_polls
from grammar_contentdetails import grammar_content_details
from speech_to_text_service import speech_to_text
from student_mock_test import mock_test
from coupon_validation import coupon_validation
from insert_coins import insert_coins
from contentwise_progress import contentwise_progress
from mock_test_ques import mock_ques
from product_rating import product_rating
from string_to_audio import string_to_audio
from curriculum_preview_portal import cur_pre_portal
from parents_section import parents_service
from report_analysis import report_analysis
from admin_section import admin_section
from mock_test_tracking import mock_test_tracking
from job_portal import job_portal
import pymysql
from myelsa_spellbee import spellbee
from jobportal_otp import otp_jobportal
from myelsa_mail_and_sms import myelsa_sms_mail
from yrb_admin_portal import yrb_admin_portal
from myelsa_registration_api import myelsa_registration
from teacher_portal import teacher_portal
from subscription_from_sales_app import sales_app_subcription
from fee_management import fee_management
from logindb_services import logindb_controller
from engagement_portal import engagement_portal
from bookfair_section import games_section
from myCommunication_section import mycomm_controller
from communication_portal import mycommunication_controller
from student_subscription import student_subscription
from cash_transactions import cash_transaction
from user_library import user_library
from zoom_videocall import live_classes
from imsecure import sms_backup
from mylibrary import my_Library
from user_assessments import user_library_assessments
from userlibrary_dtls import library
from add_teacher_to_institution import teacher_to_institution
from aws_resources import aws_resources
from student_document import student_document_details
from push_notifications import myelsa_app_notify
from voicechat_section import voicechat_section
from demo_onboarding import demo_onboarding
from online_test import online_test
from myelsa_online_test import myelsa_online_test
from onlinetest_section import onlinetest_section
from myelsa_course import myelsa_course
from myelsa_class_manager import myelsa
from instamojo_payments import instamojo_payments
from course_coupon import course_coupon_dtls
from userlibrary_questions import user_library_questions
from course_section import course_section
from meprotect_mail import meprotect_mail
from myelsa_help_section import myelsa_helpsection
from academy_login_section import academy_signin  
from academy_course_section import academy_course_details
from myelsa_academy import myelsa_academy  
from myelsa_contest import myelsa_contest
from skywalk_api import skywalk_section
from myelsa_third_partycourse import myelsa_third_partycourse
from signup_section import signup_section
from logindb_servicesV2 import logindb_controllerV2
from class_manager_section import class_manager_api
from myelsa_new_course import myelsa_new_course
from newcourse_section import newcourse_section
from myelsa_user_library import myelsa_user_library
from myelsa_newassignment_section import myelsa_newassignment
from myelsa_liveclass import myelsa_liveclass
from skywalkinstamojo_payments import skywalkinstamojo_payments
from myelsa_examsection import exam_section
from student_examsection import student_exam_section
from event import event
from dashboard_section import dashboard_section
from myelsa_communication import myelsa_communication
from myelsa_leaderboard import myelsa_leaderboard


app = Flask(__name__)
mysql = MySQL()
cors = CORS(app,resource={
    r"/*":{
        "origins":"*"
    }
})
app.config['CORS_HEADERS'] = 'Content-Type'
last_update_ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

app.register_blueprint(skywalk_section, url_prefix='/skywalk_section')
app.register_blueprint(academy_course_details, url_prefix='/academy_course_section')
app.register_blueprint(academy_signin, url_prefix='/academy_login_section')
app.register_blueprint(myelsa_helpsection, url_prefix='/myelsa_help')
app.register_blueprint(course_section, url_prefix='/course_section')
app.register_blueprint(instamojo_payments, url_prefix='/instamojo_payments')
app.register_blueprint(onlinetest_section,url_prefix='/onlinetest_section')
app.register_blueprint(demo_onboarding,url_prefix='/demo_onboarding_data')
app.register_blueprint(voicechat_section,url_prefix='/voicechat_section')
app.register_blueprint(myelsa_app_notify,url_prefix='/app_notify')
app.register_blueprint(aws_resources,url_prefix='/aws_portal')
app.register_blueprint(teacher_to_institution, url_prefix='/register_teacher')
app.register_blueprint(user_library_assessments, url_prefix='/user_library_assessments')
app.register_blueprint(live_classes, url_prefix='/live_classes')
app.register_blueprint(timeline)
app.register_blueprint(yrb)
# app.register_blueprint(youngRB_blueprint,url_prefix='/yrb')
# app.register_blueprint(coupon,url_prefix='/coupon')
# app.register_blueprint(analysis,url_prefix='/myelsa_analysis')
app.register_blueprint(user_tracking,url_prefix='/user_tracking')
# app.register_blueprint(myelsa_registrations,url_prefix='/myelsa_registrations')
# app.register_blueprint(tally_dms,url_prefix='/tally')
app.register_blueprint(daily_notifications,url_prefix='/daily_notifications')
app.register_blueprint(onboarding_teachers,url_prefix='/onboarding_teachers')
# app.register_blueprint(ocr_service, url_prefix='/ocr')
app.register_blueprint(reading_service,url_prefix='/matchReadingAnswer')
app.register_blueprint(text_to_speech, url_prefix='/angrezdost')
app.register_blueprint(time_discount, url_prefix='/time_discount')
app.register_blueprint(student_favorite, url_prefix='/favoriteContent')
app.register_blueprint(avatar, url_prefix='/avatar')
app.register_blueprint(avatar_polls, url_prefix='/voteforavatar')
app.register_blueprint(grammar_content_details, url_prefix='/grammarcontentdetails')
app.register_blueprint(speech_to_text, url_prefix='/speech_to_text')
app.register_blueprint(mock_test, url_prefix='/student_marks')
app.register_blueprint(coupon_validation, url_prefix='/coupon_validation')
app.register_blueprint(insert_coins, url_prefix='/insert_coins')
app.register_blueprint(contentwise_progress, url_prefix='/usercontentprogress')
app.register_blueprint(mock_ques, url_prefix='/mock_test')
app.register_blueprint(product_rating, url_prefix='/product_rating')
app.register_blueprint(string_to_audio, url_prefix='/speechToTxtForPortal')
app.register_blueprint(cur_pre_portal, url_prefix='/cur_preview_portal')
app.register_blueprint(parents_service, url_prefix='/parents_section')
app.register_blueprint(report_analysis, url_prefix='/report_analysis')
app.register_blueprint(admin_section, url_prefix='/admin_section')
app.register_blueprint(mock_test_tracking, url_prefix='/mocktest_tracking')
app.register_blueprint(job_portal, url_prefix='/job_portal')
app.register_blueprint(spellbee, url_prefix='/spellbee')
app.register_blueprint(otp_jobportal, url_prefix='/generate_otp')
app.register_blueprint(myelsa_sms_mail, url_prefix='/myelsa_communication')
app.register_blueprint(yrb_admin_portal, url_prefix='/yrb_admin_portal')
app.register_blueprint(myelsa_registration, url_prefix='/myelsa_registration')
app.register_blueprint(teacher_portal, url_prefix='/teacher_portal')
app.register_blueprint(sales_app_subcription, url_prefix='/register_from_sales_app')
app.register_blueprint(fee_management, url_prefix='/fee_management')
app.register_blueprint(logindb_controller, url_prefix='/logindb_section')
app.register_blueprint(engagement_portal, url_prefix='/engagement_portal')
app.register_blueprint(games_section, url_prefix='/games_section')
app.register_blueprint(mycomm_controller, url_prefix='/mycommunication')
app.register_blueprint(mycommunication_controller, url_prefix='/communication')
app.register_blueprint(student_subscription, url_prefix='/student_subscription')
app.register_blueprint(cash_transaction, url_prefix='/cash_transaction')
app.register_blueprint(user_library, url_prefix='/user_library')
app.register_blueprint(sms_backup, url_prefix='/imsecure_sms_backup')
app.register_blueprint(my_Library, url_prefix='/my_Library')
app.register_blueprint(library, url_prefix='/library_dtls')
app.register_blueprint(student_document_details, url_prefix='/student_document_details')
app.register_blueprint(online_test, url_prefix='/online_test')
app.register_blueprint(myelsa_online_test, url_prefix='/myelsa_online_test')
app.register_blueprint(myelsa_course, url_prefix='/myelsa_course')
app.register_blueprint(myelsa, url_prefix='/myelsa')
app.register_blueprint(course_coupon_dtls, url_prefix='/course_coupon_dtls')
app.register_blueprint(user_library_questions, url_prefix='/userlibrary_questions')
app.register_blueprint(meprotect_mail, url_prefix='/meprotect_mail')
app.register_blueprint(myelsa_academy, url_prefix='/myelsa_academy')
app.register_blueprint(myelsa_contest, url_prefix='/myelsa_contest')
app.register_blueprint(myelsa_third_partycourse, url_prefix='/third_partycourse')
app.register_blueprint(signup_section, url_prefix='/signup_section')
app.register_blueprint(logindb_controllerV2, url_prefix='/logindb_sectionV2')
app.register_blueprint(class_manager_api, url_prefix='/class_manager_section')
app.register_blueprint(myelsa_new_course, url_prefix='/newcourse_section')
app.register_blueprint(newcourse_section, url_prefix='/myelsa_newcourse_section')
app.register_blueprint(myelsa_user_library, url_prefix='/myelsa_user_library')
app.register_blueprint(skywalkinstamojo_payments, url_prefix='/skywalk_payments')
app.register_blueprint(myelsa_newassignment, url_prefix='/myelsa_newassignment')
app.register_blueprint(myelsa_liveclass, url_prefix='/myelsa_liveclass')
app.register_blueprint(exam_section, url_prefix='/myelsa_exam_section')
app.register_blueprint(student_exam_section, url_prefix='/studentexam_section')
app.register_blueprint(event, url_prefix='/event')
app.register_blueprint(dashboard_section, url_prefix='/dashboard_section')
app.register_blueprint(myelsa_communication, url_prefix='/myelsa_communication_section')
app.register_blueprint(myelsa_leaderboard, url_prefix='/myelsa_leaderboard')


app.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app.config['MYSQL_DATABASE_DB'] = 'creamson_lab_lang1'
app.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'

mysql.init_app(app)
connection = mysql.connect()

@app.route('/activity_mapping_id/<activity_id>/<activity_category_id>/<activity_category_type_id>/<activity_category_sub_type_id>')
@cross_origin()
def get_activity_mapping_id(activity_id,activity_category_id,activity_category_type_id,activity_category_sub_type_id):
	connection = mysql.connect()
	cursor = connection.cursor()
	activity_mapping_id = cursor.execute("""SELECT activity_mapping_id 
			from activity_mapping where activity_id = %s and  activity_category_id = %s and activity_category_type_id = %s and 
			activity_category_sub_type_id = %s""",(activity_id,activity_category_id,activity_category_type_id,activity_category_sub_type_id))

	get_activity_mapping_id = cursor.fetchone()
	desc = cursor.description
	col_names = [col[0] for col in desc]
	activity_mapping_id = dict(zip(col_names, get_activity_mapping_id))

	if True:
		return jsonify(Status="Success",activity_id=activity_mapping_id), status.HTTP_200_OK
	else:
		return jsonify(Status="Failure"), status.HTTP_204_NO_CONTENT

@app.route('/activity')
@cross_origin()
def get_activity():
	connection = mysql.connect()
	cursor = connection.cursor()
	cursor.execute("""SELECT activity_id, activity_desc from activity""")
	activity = cursor.fetchall()
	desc = cursor.description
	col_names = [col[0] for col in desc]
	activity_desc = [dict(izip(col_names, row)) for row in activity]
	if True:
		return jsonify(Status="Success",activity_list=activity_desc), status.HTTP_200_OK
	else:
		return jsonify(Status="Failure"), status.HTTP_204_NO_CONTENT
	# return jsonify(resp)
	# return jsonify(activity_desc)

@app.route('/board')
@cross_origin()
def get_board():
	connection = mysql.connect()
	cursor = connection.cursor()
	cursor.execute("""SELECT board_id, board_desc,board_image from board""")
	board = cursor.fetchall()
	desc = cursor.description
	col_names = [col[0] for col in desc]
	board_desc = [dict(izip(col_names, row)) for row in board]
	# return jsonify(board_desc)
	if True:
		return jsonify(Status="Success",board_list=board_desc), status.HTTP_200_OK
	else:
		return jsonify(Status="Failure"), status.HTTP_204_NO_CONTENT

@app.route('/content', methods=['POST','GET'])
@cross_origin()
def create_content():
	content = request.get_json()
	connection = mysql.connect()
	cursor = connection.cursor()
	if request.method == 'POST':

		activity_mapping = cursor.execute("""INSERT INTO activity_mapping (Activity_ID, Activity_Category_ID, Activity_Category_Type_ID, 
			Activity_Category_Sub_Type_ID) SELECT '{}', '{}', '{}', '{}' FROM dual WHERE NOT EXISTS 
			(SELECT * FROM activity_mapping WHERE Activity_ID = '{}' AND Activity_Category_ID = '{}' 
			AND Activity_Category_Type_ID ='{}' AND Activity_Category_Sub_Type_ID ='{}')""".format(content['activity_id'], 
				content['activity_category_id'], content['activity_category_type_id'], 
				content['activity_category_sub_type_id'],content['activity_id'],content['activity_category_id'], 
				content['activity_category_type_id'], content['activity_category_sub_type_id']))

		activity_mapping_id = cursor.execute("""SELECT activity_mapping_id 
			from activity_mapping where activity_id = %s and  activity_category_id = %s and activity_category_type_id = %s and 
			activity_category_sub_type_id = %s""",(content['activity_id'], content['activity_category_id'], 
				content['activity_category_type_id'], content['activity_category_sub_type_id']))

		get_activity_mapping_id = cursor.fetchone()
		desc = cursor.description
		col_names = [col[0] for col in desc]
		mapping_details = dict(zip(col_names, get_activity_mapping_id))

		cursor.execute("""SELECT `Content_Master_ID` FROM `content_master` 
			WHERE `Content_Master_ID` in(SELECT `Content_Master_ID` FROM `content_rule` 
			WHERE `Activity_Mapping_ID` = %s AND `Class` = %s AND `Board_ID` = %s) 
			and `Content_Master_Name`= %s""",(get_activity_mapping_id,content['class'],
				content['board_id'],content['content_master_name']))

		con_id = cursor.fetchone()
		# print(con_id)

		if con_id == None:

			content_master_query = ("""INSERT INTO content_master (activity_mapping_id, 
				content_type, total_content_detail_count,content_master_name,
				content_image_path) VALUES (%s,%s,%s,%s,%s)""")
			content_data = (get_activity_mapping_id, content['content_type'], content['total_content_detail_count'],
				content['content_master_name'], content['content_image_path'])	
			cursor.execute(content_master_query, content_data)

			content['content_master_id'] = cursor.lastrowid
			# content['sequence'] = 0
			content_rule_query = ("""INSERT INTO content_rule (content_master_id, activity_mapping_id, class, level,
				board_id, sequence) VALUES (%s,%s,%s,%s,%s,%s)""")
			content_rule_data = (content['content_master_id'],get_activity_mapping_id,content['class'],
				content['level'],content['board_id'], content['sequence'])
			
			cursor.execute(content_rule_query, content_rule_data)
			connection.commit()
			if True:
				return jsonify(Status="Success",message = 'Content Created',content_master_created=content), status.HTTP_200_OK
			else:
				return jsonify(Status="Failure"), status.HTTP_204_NO_CONTENT
		else:
			if True:
				return jsonify(Status="Success",message = 'Content Exists',content_master_created=content), status.HTTP_200_OK
			else:
				return jsonify(Status="Failure"), status.HTTP_204_NO_CONTENT

@app.route('/getContent/<student_class>/<board>/<activity_mapping_id>', methods=['GET'])
@cross_origin()
def get_content(student_class,board,activity_mapping_id):
	connection = mysql.connect()
	cursor = connection.cursor()
	if request.method == 'GET':
		cursor.execute("""SELECT content_master_id,content_master_name FROM `content_master` 
			WHERE `Content_Master_ID` in (SELECT `Content_Master_ID` FROM `content_rule` 
			WHERE locate(%s,`Class`) and locate(%s,`Board_ID`) 
			and `Activity_Mapping_ID`= %s)""",(student_class,board,activity_mapping_id))
		
		name = cursor.fetchall()
		desc = cursor.description
		col_names = [col[0] for col in desc]
		content_master = [dict(izip(col_names, row)) for row in name]

		# return jsonify(content_master)
		if True:
			return jsonify(Status="SUCCESS",content_master_list=content_master), status.HTTP_200_OK
		else:
			return jsonify(Status="Failure"), status.HTTP_204_NO_CONTENT
	# return redirect(url_for('add_content_details', content_id = content['content_master_id']))

@app.route('/content_details/<content_id>', methods=['POST', 'GET'])
@cross_origin()
def add_content_details(content_id):
	connection = mysql.connect()
	cursor = connection.cursor()
	content_details = request.get_json()
	content_master_id = content_id
	if request.method == 'POST':
		content_details['content_master_id'] = content_master_id
		content = content_details['content']
		
		for detail in content:
			content_name = detail['content_name']
			content_image_path = detail['content_image_path']
			content_path = detail['content_path']
			content_filename = detail['content_filename']
			filetype_id = detail['filetype_id']
			detail['last_update_ts'] = last_update_ts

			cursor.execute("""SELECT `Content_Detail_Sequence_ID` FROM `content_details` 
				WHERE `Content_Master_ID` = %s 
				order by Content_Detail_Sequence_ID DESC limit 1""",(content_master_id))

			content_detail_sequence_id = cursor.fetchone()

			if content_detail_sequence_id != None:
				content_detail_sequence_id = content_detail_sequence_id[0]
			else:
				content_detail_sequence_id = 0
			content_detail_sequence_id += 1

			content_detail_query = ("""INSERT INTO content_details (content_master_id, content_detail_sequence_id, 
				content_name, content_image_path, content_path, content_filename, filetype_id, 
				last_update_ts) 
				VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""")
			content_detail_data = (content_master_id, content_detail_sequence_id, content_name, 
				content_image_path,	content_path, content_filename, filetype_id, 
				last_update_ts)

			cursor.execute(content_detail_query, content_detail_data)
			connection.commit()
		if True:
			return jsonify(Status="Success",content_details=content_details), status.HTTP_200_OK
		else:
			return jsonify(Status="Failure"), status.HTTP_204_NO_CONTENT
	if request.method == 'GET':
		cursor.execute("""SELECT * from content_details where content_master_id = %s """,(content_master_id))
		get_content_details = cursor.fetchall()
		desc = cursor.description
		col_names = [col[0] for col in desc]
		details = [dict(izip(col_names, row)) for row in get_content_details]
		if True:
			return jsonify(Status="SUCCESS",content_details=details), status.HTTP_200_OK
		else:
			return jsonify(Status="Failure"), status.HTTP_204_NO_CONTENT


@app.route('/assessment_type')
@cross_origin()
def get_assessment_type():
	connection = mysql.connect()
	cursor = connection.cursor()
	cursor.execute("""SELECT Assessment_Type_ID, Assessment_Type_Desc from assessment_type""")
	types = cursor.fetchall()
	desc = cursor.description
	column_names = [col[0] for col in desc]
	assessment_type = [dict(izip(column_names, row)) for row in types]
	if True:
		return jsonify(Status="Success",assessment_type=assessment_type), status.HTTP_200_OK
	else:
		return jsonify(Status="Failure"), status.HTTP_204_NO_CONTENT

@app.route('/filetype')
@cross_origin()
def get_filetype():
	connection = mysql.connect()
	cursor = connection.cursor()
	cursor.execute("""SELECT FileType_ID, FileType_Desc, FileType_Extension from filetype""")
	ftype = cursor.fetchall()
	descr = cursor.description
	columns = [col[0] for col in descr]
	file_type = [dict(izip(columns, row)) for row in ftype]
	if True:
		return jsonify(Status="Success",file_type=file_type), status.HTTP_200_OK
	else:
		return jsonify(Status="Failure"), status.HTTP_204_NO_CONTENT

@app.route('/new_assessment', methods=['POST'])
@cross_origin()
def create_assessment():
	connection = mysql.connect()
	cursor = connection.cursor()
	details = request.get_json()
	# content_master_id = details['content_master_id']
	# assessment_type_desc = details['assessment_type_desc']
	assessment_type_id = details['assessment_type_id']
	act_map = details['act_map']
	assessment_desc = details['assessment_desc']
	assessment_content_file_path = details['assesment_content_file_path']
	assessment_content_filename = details['assesment_content_filename']
	assessment_filetype_id = details['assesment_filetype_id']
	assessment_addition_ts = details['assessment_addition_ts']
	assessment_status = details['assessment_status']
	last_update_id = details['last_update_id']
	details['last_update_ts'] = last_update_ts

	assessment_query = ("""INSERT INTO assessment (`Assessment_Type_ID`, `Activity_Mapping_ID`, `Assesment_Desc`, 
		`Content_File_Path`, `Content_FileName`, `FileType_Id`, `Assessment_Status`,
		`Last_Update_ID`, `Last_Update_TS`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

	assessment_data = (assessment_type_id, act_map, assessment_desc, assessment_content_file_path, 
		assessment_content_filename,assessment_filetype_id, assessment_status, 
		last_update_id, last_update_ts)

	cursor.execute(assessment_query, assessment_data)
	connection.commit()
	details['assessment_id'] = cursor.lastrowid
	if True:
		return jsonify(Status="Success",assessment=details), status.HTTP_200_OK
	else:
		return jsonify(Status="Failure"), status.HTTP_204_NO_CONTENT

@app.route('/postPassage', methods=['POST'])
@cross_origin()
def add_passage():
	connection = mysql.connect()
	cursor = connection.cursor()
	details = request.get_json()
	passage_desc = details['passage_desc']
	content_file_path = details['content_file_path']
	content_master_id = details['content_master_id']
	passage_insert_query = ("""INSERT INTO `passage_dtl`(`passage_desc`, `content_file_path`, 
		`content_master_id`) VALUES(%s,%s,%s)""")
	passage_data = (passage_desc,content_file_path,content_master_id)

	cursor.execute(passage_insert_query,passage_data)
	connection.commit()
	passage_id = cursor.lastrowid
	details['passage_id'] = passage_id
	if True:
		return jsonify(Status="Success",passage=details), status.HTTP_200_OK
	else:
		return jsonify(Status="Failure"), status.HTTP_204_NO_CONTENT


@app.route('/questions', methods=['POST'])
@cross_origin()
def add_question():
	connection = mysql.connect()
	cursor = connection.cursor()
	details = request.get_json()
	escape_text = [',',"'",'"']
	for each_detail in details:
		question_type = each_detail['question_type']
		question = each_detail['question']
		question_content_file_path = each_detail['content_file_path']
		question_content_filename = each_detail['content_filename']
		question_filetype_id = each_detail['filetype_id']
		last_ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
		each_detail['last_update_ts'] = last_ts
		content_master_id = each_detail['content_master_id']
		last_update_id = each_detail['last_update_id']
		passage_id = each_detail['passage_id']
		question_query = ("""INSERT INTO question (`Question_Type`, `Question`, `Content_file_path`, 
			`Content_FileName`, `File_Type_ID`, `Content_master_Id`, passage_id, `Last_Update_ID`,`Last_Update_TS`) 
			VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) """)
		question_data = (question_type, question, question_content_file_path, 
			question_content_filename, question_filetype_id, content_master_id, passage_id, last_update_id,last_ts)
		cursor.execute(question_query, question_data)
		
		question_id = cursor.lastrowid
		options = each_detail['options']
		option = options['option']
		option_sequence_id = 1
		for ops in option:
			option_name = ops['option_name']
			ops['option_sequence_id'] = option_sequence_id
			option_content_file_path = ops['content_file_path']
			option_content_filename = ops['content_filename']
			option_filetype_id = ops['filetype_id']

			option_query = ("""INSERT INTO options ( `Question_ID`, `Option`, `Option_Sequence_ID`, `Content_file_path`, 
				`Content_FileName`, `File_Type_ID`, `Last_Update_TS`) 
				VALUES (%s,%s,%s,%s,%s,%s,%s)""")

			option_data = (question_id, option_name, option_sequence_id, option_content_file_path, option_content_filename,
				option_filetype_id, last_ts)

			cursor.execute(option_query, option_data)
			option_sequence_id += 1
			
		answer = each_detail['answer']['answer']
		answer_additional_text = each_detail['answer']['additional_text']
		cursor.execute("""SELECT `Option_ID` from options where `Question_ID` = %s 
			and `Option` = %s""",(question_id,answer))
		option_id = cursor.fetchone()
		if option_id != None:
			option_id = option_id[0]
		answer_insert_query = ("""INSERT INTO `answer`(`Question_ID`, `Option_ID`, 
			`Additional_Text`) VALUES(%s,%s,%s)""")
		answer_data = (question_id,option_id,answer_additional_text)
		cursor.execute(answer_insert_query,answer_data)
		connection.commit()
		each_detail['question_id'] = question_id
	if True:
		return jsonify(Status="Success",questions=details), status.HTTP_200_OK
	else:
		return jsonify(Status="Failure"), status.HTTP_204_NO_CONTENT



@app.route('/get_assessment')
@cross_origin()
def get_assessment():
	connection = mysql.connect()
	cursor = connection.cursor()
	cursor.execute("""SELECT Assessment_ID, Assesment_Desc from assessment""")
	assessments = cursor.fetchall()
	desc = cursor.description
	column_names = [col[0] for col in desc]
	assessment_id = [dict(izip(column_names, row)) for row in assessments]
	if True:
		return jsonify(Status="Success",assessment_id=assessment_id), status.HTTP_200_OK
	else:
		return jsonify(Status="Failure"), status.HTTP_204_NO_CONTENT


@app.route('/content_assessment_mapping', methods = ['POST'])
@cross_origin()
def content_assessment_mapping():
	connection = mysql.connect()
	cursor = connection.cursor()
	details = request.get_json()
	content_master_id = details['content_master_id']
	assessment_id = details['assessment_id']
	last_update_id = details['last_update_id']
	details['last_update_ts'] = last_update_ts
	content_detail_id = details['content_detail_id']
	# content_details = ("""SELECT content_master_id from content_details 
	# 	where content_master_id = %s""",(content_master_id))

	assessment_content_query = (""" INSERT INTO content_assessment_mapping (Content_Master_ID, Assessment_ID, content_detail_id, Last_Update_ID, Last_Update_TS) 
		values (%s,%s,%s,%s,%s)""")

	assessment_content_mapping_data = (content_master_id, assessment_id, content_detail_id, last_update_id, last_update_ts)

	cursor.execute(assessment_content_query, assessment_content_mapping_data)
	connection.commit()
	if True:
		return jsonify(Status="Success",content_assessment_mapping=details), status.HTTP_200_OK
	else:
		return jsonify(Status="Failure"), status.HTTP_204_NO_CONTENT

@app.route('/get_question')
@cross_origin()
def get_question():
	connection = mysql.connect()
	cursor = connection.cursor()
	cursor.execute("""SELECT question_ID, question from question""")
	questions = cursor.fetchall()
	desc = cursor.description
	column_names = [col[0] for col in desc]
	question_id = [dict(izip(column_names, row)) for row in questions]
	if True:
		return jsonify(Status="Success",Questions=question_id), status.HTTP_200_OK
	else:
		return jsonify(Status="Failure"), status.HTTP_204_NO_CONTENT

@app.route('/assessment_question_mapping',methods = ['POST'])
@cross_origin()
def assessment_question_mapping():
	connection = mysql.connect()
	cursor = connection.cursor()
	details = request.get_json()
	assessment_id = details['assessment_id']
	last_update_id = details['last_update_id']
	details['last_update_ts'] = last_update_ts
	ques = details['questions']
	for q in ques:
		question_id = q['question_id']

		assessment_question_query = ("""INSERT INTO assessment_question_mapping( Assessment_ID, Question_ID, 
				Last_Update_ID, Last_Update_TS) VALUES(%s,%s,%s,%s)""")

		assessment_question_mapping_data = (assessment_id, question_id, last_update_id, last_update_ts)
		cursor.execute(assessment_question_query, assessment_question_mapping_data)
		connection.commit()
	if True:
		return jsonify(Status="Success",Assessment_Question_Mapping=details), status.HTTP_200_OK
	else:
		return jsonify(Status="Failure"), status.HTTP_204_NO_CONTENT


@app.route('/uploaded_content',methods = ['POST'])
@cross_origin()
def uploaded_content():
	connection = mysql.connect()
	cursor = connection.cursor()
	details = request.get_json()
	file = details['content_file']
	file_status = details['status']
	upload_content_insert_query = ("""INSERT INTO `upload_content`(`content_file`, `status`) 
		VALUES(%s,%s)""")
	upload_data = (file,file_status)

	cursor.execute(upload_content_insert_query, upload_data)
	connection.commit()
	if True:
		return jsonify(Status="Success",UploadDtls=details), status.HTTP_200_OK
	else:
		return jsonify(Status="Failure"), status.HTTP_204_NO_CONTENT

@app.route("/getPassagedtls/<int:Content_master_Id>")
def getPassagedtls(Content_master_Id):
	connection = mysql.connect()
	cursor = connection.cursor()
	cursor.execute("""SELECT `passage_id`,`passage_desc`,`content_file_path` as passage,
		`content_master_id` FROM `passage_dtl` where `content_master_id`= %s""",(Content_master_Id))
	get_passages = cursor.fetchall()
	print(get_passages)
	if get_passages:
		desc = cursor.description
		print(desc)
		col_names = [col[0] for col in desc]
		pass_details = [dict(izip(col_names, row)) for row in get_passages]
		print(pass_details)
	else:
		pass_details = []
	cursor.close()
	if True:
		return jsonify(Status="Success",pass_details=pass_details), status.HTTP_200_OK
	else:
		return jsonify(Status="Failure"), status.HTTP_204_NO_CONTENT

@app.route('/')
def hello_world():
	return 'Hello, World!'


if __name__ == '__main__':
	app.run()
     	# app.run(host='0.0.0.0',debug=True)
