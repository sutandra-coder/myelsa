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
games_section = Blueprint('bookfair_games_api', __name__)
api = Api(games_section, version='1.0', title='MyElsa API',description='MyElsa API')
name_space = api.namespace('BookfairGamesController', description=':Bookfair Game')

'''def logindb_connection():
	connection = pymysql.connect(host='creamsonservices.com',
									user='creamson_langlab',
									password='Langlab@123',
									db='creamson_logindb',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor,
									autocommit=False)
	return connection'''

def logindb_connection():
	connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
									user='admin',
									password='cbdHoRPQPRfTdC0uSPLt',
									db='creamson_logindb',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor,
									autocommit=False)
	return connection


createsession_model = api.model('createsession_model', {
		"game_id": fields.Integer(required=True),
		"status":fields.String(required=True),
		"user_phoneNo":fields.List(fields.String(required=True)),
		"created_timestamp":fields.String(required=True)
})


answer_model = api.model('answers', {
							"ques_id":fields.Integer(required=True),
							"answer":fields.String(required=True),
							"correct":fields.String(required=True),
							"score":fields.Integer(required=True),
							"option_id":fields.Integer(),
						})

postanswer_model = api.model('AnswersModel', {
								"user_id":fields.Integer(required=True),
								"game_id": fields.Integer(required=True),
								"session_id": fields.Integer(required=True),
								"start_timestamp":fields.String(required=True),
								"end_timestamp":fields.String(required=True),
								"answerDtls":fields.List(fields.Nested(answer_model))
							})

@name_space.route("/allGames")
class allGames(Resource):
	def get(self):
		connection = logindb_connection()
		cursor = connection.cursor()
		cursor.execute("""SELECT `game_id`,`game_desc` FROM `game_master`""")
		game_master_details = cursor.fetchall()
		cursor.close()
		return ({"attributes": {"status_desc": "Game Details",
								"status": "success"
								},
				"responseList": game_master_details}), status.HTTP_200_OK

@name_space.route("/getGameDetailsByGameId/<int:game_id>")
class getGameDetailsByGameId(Resource):
	def get(self,game_id):
		connection = logindb_connection()
		cursor = connection.cursor()
		cursor.execute("""SELECT `game_desc`FROM `game_master` 
		WHERE `game_id`= %s""",(game_id))
		gamedetails_by_gameid = cursor.fetchone()
		cursor.close()
		return ({"attributes": {"status_desc": "Game Details",
								"status": "success"
								},
				"responseList": gamedetails_by_gameid}), status.HTTP_200_OK

@name_space.route("/createGameSession")
class createGameSession(Resource):
	@api.expect(createsession_model)
	def post(self):

		details = request.get_json()
		connection = logindb_connection()
		cursor = connection.cursor()

		phoneNoList = details['user_phoneNo']
		userList = []
		quesDtls = []
		sessionDtls = {}
		gameDesc = ''
		if details['game_id'] == 1:
			gameDesc = 'SpellBee'
			cursor.execute("""SELECT `word_id` as 'quesId' FROM `spellbee_master` order by rand() limit 10""")
			quesDtls = cursor.fetchall()
		elif details['game_id'] == 2:
			gameDesc = 'QuizUp'
			cursor.execute("""SELECT `Contest_ID` as 'quesId' FROM `contest_table` 
				WHERE `Contest_Description` = 'QuizUp Contest' order by rand() limit 1""")
			quesDtls = cursor.fetchall()

		createSessionInsertQuery = ("""INSERT INTO `bookfair_session`(`game_id`) VALUES (%s)""")
		create_data = (details['game_id'])
		cursor.execute(createSessionInsertQuery,create_data)
		session_id = cursor.lastrowid

		sessionUserMapInsertQuery = ("""INSERT INTO `bookfair_session_user_mapping`(`user_id`, 
			`phone_no`, `session_id`, `game_id`, `status`, 
			`created_time`) VALUES (%s,%s,%s,%s,%s,%s)""")

		userQuestionIdMappingInsertQuery = ("""INSERT INTO `bookfair_user_question_mapping`(`session_mapping_id`,
			`question_id`) VALUES (%s,%s)""")

		for phid, ph in enumerate(phoneNoList):
			cursor.execute("""SELECT `INSTITUTION_USER_ID`,`IMAGE_URL`,
				concat(`FIRST_NAME`,' ',`LAST_NAME`) AS 'name' 
				FROM `institution_user_credential` WHERE `INSTITUTION_USER_NAME` = %s""",(ph)) 

			userDtls = cursor.fetchone()

			sessionUserData = (userDtls['INSTITUTION_USER_ID'],ph,session_id,details['game_id'],
				details['status'],details['created_timestamp'])

			cursor.execute(sessionUserMapInsertQuery,sessionUserData)

			sessionUserMappingId = cursor.lastrowid
			userDtls['sessionUserMappingId'] = sessionUserMappingId

			userDtls['status'] = details['status']
			userList.append(userDtls)
			if quesDtls:
				for qid, ques in enumerate(quesDtls):
					userQuesMapData = (sessionUserMappingId,ques['quesId'])
					cursor.execute(userQuestionIdMappingInsertQuery,userQuesMapData)
			
			url = 'http://creamsonservices.com:8080/CommunicationModule2/sendMailMessage'
			data = {
					  'mailDetails': [
					    {
					      'appParams': {"image-url":"string"},
					      'mailParams': {"gameName":gameDesc,
					      				"username":userDtls['name']},
					      'role': 's1',
					      'toMail': '',
					      'toNumber': '',
					      'userId': userDtls['INSTITUTION_USER_ID']
					    }
					  ],
					  'sourceApp': 'BKFRGAMES'
					}
			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			response = requests.post(url, data=json.dumps(data), headers=headers)
		sessionDtls = {'sessionID':session_id,
						'gameId':details['game_id'],
						'userDtls':userList}

		
		
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Game Session Details",
								"status": "success"
								},
				"responseList": sessionDtls}), status.HTTP_200_OK


@name_space.route("/postUserAnswers")
class postUserAnswers(Resource):
	@api.expect(postanswer_model)
	def post(self):

		details = request.get_json()
		connection = logindb_connection()
		cursor = connection.cursor()

		answerDtls = details['answerDtls']
		finalScore = 0
		answerInsertQuery = ("""INSERT INTO `bookfair_user_answer_mapping`(`question_id`, `user_id`, 
			`option_id`, `answer`, `correct`, `score`, `session_id`, 
			`game_id`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""")

		for ansid, ans in enumerate(answerDtls):

			answerData = (ans.get('ques_id'),details.get('user_id'),ans.get('option_id'),
				ans.get('answer'),ans.get('correct'),ans.get('score'),details.get('session_id'),
				details.get('game_id'))

			cursor.execute(answerInsertQuery,answerData)
			ans['submit_id'] = cursor.lastrowid

			finalScore += ans.get('score')
		gameStatus = 'end'
		
		updateStatusQuery = ("""UPDATE `bookfair_session_user_mapping` SET `status` = %s,
			final_score = %s,game_starttime = %s,game_endtime = %s WHERE session_id = %s and user_id = %s""")
		# game_endtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		statusData = (gameStatus,finalScore,details.get('start_timestamp'),details.get('end_timestamp'),
			details.get('session_id'),details.get('user_id'))
		cursor.execute(updateStatusQuery,statusData)

		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Game Session Details",
								"status": "success",
								"finalScore":finalScore
								},
				"responseList": details}), status.HTTP_200_OK

@name_space.route("/getQuestionsByUSGId/<int:user_id>/<int:session_id>/<int:game_id>")
class getQuestionsByUSGId(Resource):
	def get(self,user_id,session_id,game_id):
		
		connection = logindb_connection()
		cursor = connection.cursor()
		quesDtls = []
		
		if game_id == 1:
			cursor.execute("""SELECT `word_id`,`word`,`hint`,`synonym` FROM `spellbee_master`
				WHERE `word_id` in(SELECT `question_id` FROM `bookfair_user_question_mapping`
				WHERE `session_mapping_id` in (SELECT `mapping_id` FROM `bookfair_session_user_mapping`
				WHERE `user_id` = %s AND `session_id` = %s AND `game_id` = %s))""",(user_id,session_id,game_id))
			quesDtls = cursor.fetchall()
		elif game_id == 2:
			cursor.execute("""SELECT `question_id` FROM `bookfair_user_question_mapping`
				WHERE `session_mapping_id` in (SELECT `mapping_id` FROM `bookfair_session_user_mapping`
				WHERE `user_id` = %s AND `session_id` = %s AND `game_id` = %s)""",(user_id,session_id,game_id))
			quizup_questions_id = cursor.fetchone()

			quizup_questions_id = str(quizup_questions_id['question_id'])
			quizup_questions_by_usg_id = requests.get('http://creamsonservices.com:8080/AssessmentModule/lab-activities/GetassessmentByContestId/'+ quizup_questions_id )
			quesDtls = quizup_questions_by_usg_id.json().get('responseList')
		else:
			quesDtls = 'No Questions Available for this GameID'
		# updateStarttimeQuery = ("""UPDATE `bookfair_session_user_mapping` SET `game_starttime`= %s 
		# 							WHERE `user_id` = %s AND `session_id` = %s AND `game_id` = %s""")
		# game_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		# startTimeData = (game_start_time,user_id,session_id,game_id)
		
		# cursor.execute(updateStarttimeQuery,startTimeData)
		
		# connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Game Question Details",
								"status": "success"
								},
				"responseList": quesDtls}), status.HTTP_200_OK


@name_space.route("/getGameListByUserId/<int:user_id>")
class getGameListByUserId(Resource):
	def get(self,user_id):
		connection = logindb_connection()
		cursor = connection.cursor()
		completeGames = []
		incompleteGames = []
		allGames = {}
		cursor.execute("""SELECT `mapping_id`,`session_id`,(SELECT `game_desc` FROM `game_master` gm 
			WHERE gm.`game_id` =bsm.`game_id` ) as 'game_desc',`game_id`,`status`,
			`final_score`,`created_time` FROM `bookfair_session_user_mapping` bsm 
			WHERE `user_id` = %s and `game_id` <> 4""",(user_id))

		gameDtls = cursor.fetchall()

		for gid,game in enumerate(gameDtls):
			if isinstance(game.get('created_time'), datetime):
				game['created_time'] = game.get('created_time').isoformat()
			if game.get('status') == 'created':
				incompleteGames.append(game)
			else:
				cursor.execute("""SELECT max(`final_score`) as 'maxScore', min(`final_score`) as 'minScore'
					FROM `bookfair_session_user_mapping` WHERE `session_id` = %s""",(game.get('session_id')))

				scoreDtls = cursor.fetchone()
				maxScore = scoreDtls.get('maxScore')
				minScore = scoreDtls.get('minScore')
				if game.get('final_score') == maxScore:
					game['won'] = 'Yes'
				else:
					game['won'] = 'No'
				completeGames.append(game)

		cursor.close()
		allGames = {'incompleteGames':incompleteGames,
					'completeGames':completeGames}

		return ({"attributes": {"status_desc": "User Game List",
								"status": "success"
								},
				"responseList": allGames}), status.HTTP_200_OK


@name_space.route("/getUserScoresBySessionId")
class getUserScoresBySessionId(Resource):
	def get(self):
		connection = logindb_connection()
		cursor = connection.cursor()

		cursor.execute("""SELECT `session_id`,(SELECT `game_desc` FROM `game_master` gm 
			WHERE gm.`game_id` =bsm.`game_id` ) as 'game_desc',`game_id`,GROUP_CONCAT(`user_id`) as 'user_id', 
			GROUP_CONCAT((SELECT concat(`FIRST_NAME`, " ", `LAST_NAME`) 
			FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = `user_id`)) as 'name',
			GROUP_CONCAT(`final_score`) as 'final_score' FROM `bookfair_session_user_mapping` bsm
			WHERE `status` = 'end' and `game_id` <> 4 GROUP BY `session_id` order by `session_id` desc""")

		scoreDtls = cursor.fetchall()
		removeEle = []
		# print(scoreDtls)
		for sid, score in enumerate(scoreDtls):
			scoreList = score.get('final_score').split(',')
			userList = score.get('user_id').split(',')
			userName = score.get('name').split(',')
			maxScore = max(scoreList)
			minScore = min(scoreList)
			# print(userList)
			if len(userList) == 2:
				# print(score)
				if maxScore > minScore:
					winner = userList[scoreList.index(maxScore)]
					winnerName = userName[scoreList.index(maxScore)]
					loser = userList[scoreList.index(minScore)]
					loserName = userName[scoreList.index(minScore)]
					score['users'] = [{'user_id':winner,
									'username':winnerName,
									'score':maxScore,
									'status':'winner'},
									{'user_id':loser,
									'username':loserName,
									'score':minScore,
									'status':'loser'}]
					score.pop('final_score')
					score.pop('user_id')
					score.pop('name')
					removeEle.append(score)
				elif maxScore == minScore:
					winner = userList[0]
					winnerName = userName[0]
					loser = userList[1]
					loserName = userName[1]
					score['users'] = [{'user_id':winner,
									'username':winnerName,
									'score':maxScore,
									'status':'tie'},
									{'user_id':loser,
									'username':loserName,
									'score':minScore,
									'status':'tie'}]
					score.pop('final_score')
					score.pop('user_id')
					score.pop('name')
					removeEle.append(score)

			else:
				pass
		# print(removeEle)
		print(removeEle)
		# for i in removeEle:
		# 	# print(elid)
		# 	print(scoreDtls[i])
		# 	scoreDtls.pop(i)
		# print(scoreDtls)
		return ({"attributes": {"status_desc": "Game Score Details",
								"status": "success"
								},
				"responseList": removeEle}), status.HTTP_200_OK



@name_space.route("/getTotalWorkshopAttendantNo")
class getTotalWorkshopAttendantNo(Resource):
	def get(self):
		connection = logindb_connection()
		cursor = connection.cursor()

		cursor.execute("""SELECT count(*) as 'totalWorkshopAttendants' 
			FROM `bookfair_session` WHERE `game_id` = 4""")

		count = cursor.fetchone()
		totalCount = count.get('totalWorkshopAttendants',0)

		return ({"attributes": {"status_desc": "Total Workshop Attendants",
								"status": "success"
								},
				"responseList": totalCount}), status.HTTP_200_OK

@name_space.route("/getTotalGameRegistrations")
class getTotalGameRegistrations(Resource):
	def get(self):
		connection = logindb_connection()
		cursor = connection.cursor()

		cursor.execute("""SELECT `game_id`,(SELECT `game_desc` FROM `game_master` gm 
			WHERE gm.`game_id` =bsm.`game_id` ) as 'game_desc',count(`game_id`) as 'totalRegistrations',
			(SELECT count(*) FROM `bookfair_session_user_mapping`  WHERE `game_id` <> 4) as 'totalCount'
			FROM `bookfair_session_user_mapping` bsm  WHERE `game_id` <> 4 GROUP BY `game_id`""")

		registrationNos = cursor.fetchall()

		
		totalRegistrations = registrationNos[0].get('totalCount')
		for reid, regs in enumerate(registrationNos):
			regs.pop('totalCount')


		return ({"attributes": {"status_desc": "Total Registration Details",
								"status": "success",
								"totalCount":totalRegistrations
								},
				"responseList": registrationNos}), status.HTTP_200_OK


@name_space.route("/getRankByGameId/<int:gameID>")
class getRankByGameId(Resource):
	def get(self,gameID):

		connection = logindb_connection()
		cursor = connection.cursor()

		cursor.execute("""SELECT game_desc,User_id, (SELECT concat(`FIRST_NAME`, " ", `LAST_NAME`) 
			FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = `user_id`) AS Name,
			floor(MaxScore) AS Score, 
			CASE 
			WHEN MaxScore = @prevScore THEN @rnk 
			WHEN @prevScore := MaxScore THEN @rnk := @rnk+1 
			END 'Ranking' 
			FROM ( SELECT (SELECT `game_desc` FROM `game_master` gm 
			WHERE gm.`game_id` =bsm.`game_id` ) as 'game_desc',User_id, sum(`final_score`) AS MaxScore 
			FROM `bookfair_session_user_mapping` bsm WHERE `status` = 'end' and `game_id` = %s 
			GROUP BY User_id ORDER BY MaxScore DESC, User_id  limit 10) AS q 
			CROSS JOIN (SELECT @rnk := 0, @prevScore := 0) AS vars""",(gameID))

		rankDtls = cursor.fetchall()
		for rid, rank in enumerate(rankDtls):
			rank['Score'] = int(rank.get('Score'))
		return ({"attributes": {"status_desc": "Game Wise Leader Board Details",
								"status": "success",
								},
				"responseList": rankDtls}), status.HTTP_200_OK


@name_space.route("/getOverAllRank")
class getOverAllRank(Resource):
	def get(self):

		connection = logindb_connection()
		cursor = connection.cursor()

		cursor.execute("""SELECT User_id, (SELECT concat(`FIRST_NAME`, " ", `LAST_NAME`) 
			FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = `user_id`) AS Name,
			floor(MaxScore) AS Score, 
			CASE 
			WHEN MaxScore = @prevScore THEN @rnk 
			WHEN @prevScore := MaxScore THEN @rnk := @rnk+1 
			END 'Ranking' 
			FROM ( SELECT User_id, sum(`final_score`) AS MaxScore 
			FROM `bookfair_session_user_mapping` WHERE `status` = 'end' 
			GROUP BY User_id ORDER BY MaxScore DESC, User_id limit 10) AS q 
			CROSS JOIN (SELECT @rnk := 0, @prevScore := 0) AS vars""")

		rankDtls = cursor.fetchall()

		for rid, rank in enumerate(rankDtls):
			rank['Score'] = int(rank.get('Score'))

		return ({"attributes": {"status_desc": "Game Wise Leader Board Details",
								"status": "success",
								},
				"responseList": rankDtls}), status.HTTP_200_OK