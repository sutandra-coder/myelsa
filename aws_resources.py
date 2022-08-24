from flask import Flask, request, jsonify, json
from flask_api import status
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields,reqparse
from werkzeug.datastructures import FileStorage
from werkzeug import secure_filename
from awsconfig import ACCESS_KEY,SECRET_KEY
import requests
import boto3
import os
app = Flask(__name__)
cors = CORS(app)

aws_resources = Blueprint('aws_resources_api', __name__)
api = Api(aws_resources,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('awsResourceController',description='AWS Resources')

upload_parser = api.parser()
upload_parser.add_argument('file', location='files', type=FileStorage, required=True)
UPLOAD_FOLDER = '/tmp'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

BASE_URL = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/'

# @name_space.route("/uploadToS3Bucket/<string:user_id>")
# @name_space.expect(upload_parser)
# class uploadToS3Bucket(Resource):
# 	def post(self,user_id):
# 		bucket_name = "myelsapython"
# 		s3 = boto3.client(
# 			"s3",
# 			aws_access_key_id=ACCESS_KEY,
# 			aws_secret_access_key=SECRET_KEY
# 			)
# 		bucket_resource = s3
# 		uploadedfile = request.files['file']
# 		print(uploadedfile)
# 		filename = ''
# 		userKey = user_id+'/'
# 		fpath = ''
# 		if uploadedfile:
# 			filename = secure_filename(uploadedfile.filename)
# 			result = bucket_resource.list_objects(Bucket=bucket_name, Prefix=userKey)
# 			absfilepath = os.path.join(app.config['UPLOAD_FOLDER'],filename)
# 			uploadedfile.save(absfilepath)
# 			# if result.get('Contents'):
# 			# 	userKey = result.get('Contents')[0].get('Key')
# 			uploadRes = bucket_resource.upload_file(
# 				Bucket = bucket_name,
# 				Filename=absfilepath,
# 				Key=userKey+filename)
# 			# else:
# 			# 	uploadRes = bucket_resource.upload_file(
# 			# 		Bucket = bucket_name,
# 			# 		Filename=filename,
# 			# 		Key=userKey+filename)
# 			# 	print(uploadRes)
# 			filepath = bucket_resource.list_objects(Bucket=bucket_name, Prefix=userKey+filename)
# 			if filepath.get('Contents'):
# 				fpath = filepath.get('Contents')[0].get('Key')
# 				FileSize = None
# 				os.remove(absfilepath)
# 				return {"attributes": {"status": "success"},
# 						"responseList": [{
# 						  "FilePath": "https://d1lwvo1ffrod0a.cloudfront.net/{}".format(fpath),
# 						  "FileName": filename,
# 						  "FileSize": FileSize}],
# 						"responseDataTO": {}
# 						}
# 		else:
# 			return {"attributes": {"status": "success"},
# 						"responseList": [],
# 						"responseDataTO": {}
# 					}


@name_space.route("/uploadToS3Bucket/v2/<string:user_id>")
@name_space.expect(upload_parser)
class uploadToS3BucketV2(Resource):
	def post(self,user_id):
		uploadURL = BASE_URL + 'aws_portal/awsResourceController/uploadToS3Bucket/{}'.format(user_id)
		headers = {"content-type": "multipart/form-data"}
		files = {}
		for form_file_param in request.files:
			fs = request.files[form_file_param] 
			files[form_file_param] = (fs.filename, fs.read())
		uploadRes = requests.post(uploadURL,files=files).json()
		return uploadRes

@name_space.route("/uploadToS3Bucket/<string:user_id>")
@name_space.expect(upload_parser)
class uploadToS3Bucket(Resource):
	def post(self,user_id):
		bucket_name = "myelsapython"
		s3 = boto3.client(
			"s3",
			aws_access_key_id=ACCESS_KEY,
			aws_secret_access_key=SECRET_KEY
			)
		bucket_resource = s3
		uploadedfile = request.files['file']
		print(uploadedfile)
		filename = ''
		userKey = user_id+'/'
		fpath = ''
		FileSize = None
		if uploadedfile:
			filename = secure_filename(uploadedfile.filename)
			keyname = userKey+filename
			uploadRes = bucket_resource.upload_fileobj(
				Bucket = bucket_name,
				Fileobj=uploadedfile,
				Key=keyname)
			print(uploadRes)
			# result = bucket_resource.list_objects(Bucket=bucket_name, Prefix=userKey)
			# absfilepath = os.path.join(app.config['UPLOAD_FOLDER'],filename)
			# # print(absfilepath)
			# uploadedfile.save(absfilepath)
			# 
			# uploadReq = (filename,absfilepath,keyname)
			# thread_a = Compute(uploadReq,'uploadToS3Bucket')
			# thread_a.start()
			return {"attributes": {"status": "success"},
				"responseList": [{
				  "FilePath": "https://d1lwvo1ffrod0a.cloudfront.net/{}".format(keyname),
				  "FileName": filename,
				  "FileSize": FileSize}],
				"responseDataTO": {}
				}
		else:
			return {"attributes": {"status": "success"},
						"responseList": [],
						"responseDataTO": {}
					}


@name_space.route("/uploadToS3Bucket/communicationPortal/<path:user_id>")
@name_space.expect(upload_parser)
class uploadToS3BucketV3(Resource):
	def post(self,user_id):
		bucket_name = "myelsapython"
		s3 = boto3.client(
			"s3",
			aws_access_key_id=ACCESS_KEY,
			aws_secret_access_key=SECRET_KEY
			)
		bucket_resource = s3
		uploadedfile = request.files['file']
		# print(uploadedfile)
		filename = ''
		userKey = user_id+'/'
		fpath = ''
		FileSize = None
		if uploadedfile:
			filename = secure_filename(uploadedfile.filename)
			keyname = userKey+filename
			uploadRes = bucket_resource.upload_fileobj(
				Bucket = bucket_name,
				Fileobj=uploadedfile,
				Key=keyname)
			# print(uploadRes)
			# result = bucket_resource.list_objects(Bucket=bucket_name, Prefix=userKey)
			# absfilepath = os.path.join(app.config['UPLOAD_FOLDER'],filename)
			# # print(absfilepath)
			# uploadedfile.save(absfilepath)
			# 
			# uploadReq = (filename,absfilepath,keyname)
			# thread_a = Compute(uploadReq,'uploadToS3Bucket')
			# thread_a.start()
			return {"attributes": {"status": "success"},
				"responseList": [{
				  "FilePath": "https://d1lwvo1ffrod0a.cloudfront.net/{}".format(keyname),
				  "FileName": filename,
				  "FileSize": FileSize}],
				"responseDataTO": {}
				}
		else:
			return {"attributes": {"status": "success"},
						"responseList": [],
						"responseDataTO": {}
					}

if __name__ == '__main__':
    app.run(debug=True)



