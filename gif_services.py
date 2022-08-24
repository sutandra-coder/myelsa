from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from database_connections import connect_gif
import requests
import calendar
import json

app = Flask(__name__)
cors = CORS(app)

gif_services = Blueprint('gif_services_api', __name__)

api = Api(gif_services, version='1.0', title='Gif API',
    	description='Gif API')
name_space = api.namespace('GifAPI', description='Gif')

BASE_URL = "http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com/flaskapp/"
#--------------------------------------------------------------------#

giftag = api.model('giftag', {
	"tag_name": fields.String(),
    "tag_desc": fields.String(),
    "tag_position": fields.String(),
    "tag_image": fields.String()
    })

gifvideo = api.model('gifvideo', {
	"tag_id": fields.String(),
    "video_name": fields.String(),
    "video_path": fields.String()
    })

#--------------------------------------------------------------------#
@name_space.route("/gifTags")
class gifTags(Resource):
    def get(self):
        connection = connect_gif()
        cursor = connection.cursor()
        
        cursor.execute("""SELECT tag_id,tag_name,tag_desc,tag_position,
        	tag_image FROM `gif_tags`""")
        tagdtls = cursor.fetchall()

        return ({"attributes": {"status_desc": "Gif Tag Details",
                                "status": "success"
                                },
                 "responseList": tagdtls
                }), status.HTTP_200_OK

#--------------------------------------------------------------------#
@name_space.route("/AddGifTags")
class AddGifTags(Resource):
	@api.expect(giftag)
	def post(self):
		connection = connect_gif()
		cursor = connection.cursor()
		details = request.get_json()

		tag_name = details.get('tag_name')
		tag_desc = details.get('tag_desc')
		tag_position = details.get('tag_position')
		tag_image = details.get('tag_image')

		cursor.execute("""SELECT tag_id FROM `gif_tags` where 
			tag_name=%s""",(tag_name))
		tagname = cursor.fetchone()

		if tagname == None:
			gifquery = ("""INSERT INTO gif_tags(tag_name,tag_desc,tag_position,
				tag_image) VALUES (%s,%s,%s,%s)""")
			gifdata = cursor.execute(gifquery,(tag_name,tag_desc,tag_position,
				tag_image))
			tag_id = cursor.lastrowid
			details['tag_id'] = tag_id
			if gifdata:

			    return ({"attributes": {"status_desc": "Gif Tag Details",
			                            "status": "success"
			                            },
			             "responseList": details}), status.HTTP_200_OK

		else:
			return ({"attributes": {"status_desc": "Gif Tag Details",
			                            "status": "success"
			                            },
			             "responseList": "Already Exists Gif Tag"}), status.HTTP_200_OK

#--------------------------------------------------------------------#
@name_space.route("/UploadedVideoDetailsByGifTagId/<int:tag_id>")
class UploadedVideoDetailsByGifTagId(Resource):
    def get(self,tag_id):
        connection = connect_gif()
        cursor = connection.cursor()
        
        cursor.execute("""SELECT gt.`tag_id`,tag_name,vm.`video_id`,
        	video_name,video_path FROM video_tag_mapping vtm inner join 
        	`gif_tags` gt on vtm.`tag_id`= gt.`tag_id` inner join 
        	`video_master` vm on vtm.`video_id` = vm.`video_id` where
        	vtm.`tag_id`=%s""",(tag_id))
        videodtls = cursor.fetchall()

        return ({"attributes": {"status_desc": "Gif Video Details",
                                "status": "success"
                                },
                 "responseList": videodtls
                }), status.HTTP_200_OK

#--------------------------------------------------------------------#
@name_space.route("/AddGifVideo")
class AddGifVideo(Resource):
	@api.expect(gifvideo)
	def post(self):
		connection = connect_gif()
		cursor = connection.cursor()
		details = request.get_json()

		tag_id = details.get('tag_id')
		video_name = details.get('video_name')
		video_path = details.get('video_path')

		gifvideoquery = ("""INSERT INTO video_master(video_name,video_path) 
			VALUES (%s,%s)""")
		videodata = cursor.execute(gifvideoquery,(video_name,video_path))
		video_id = cursor.lastrowid
		details['video_id'] = video_id

		gifmappquery = ("""INSERT INTO video_tag_mapping(tag_id,video_id) 
			VALUES (%s,%s)""")
		gifmappdata = cursor.execute(gifmappquery,(tag_id,video_id))
		mapping_id = cursor.lastrowid
		details['mapping_id'] = mapping_id

		if gifmappdata:

		    return ({"attributes": {"status_desc": "Gif Video Mapping Details",
		                            "status": "success"
		                            },
		             "responseList": details}), status.HTTP_200_OK
