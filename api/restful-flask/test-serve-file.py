from flask import Flask
from flask_restful import Api, Resource
from pathlib import Path

app = Flask(__name__)
api = Api(app)

files = [
	{
		"ticker" : "maker" ,
		"fpath" : str(Path.home())+"/git/pubCryptoAnalysis/api/coin-market-book/raw-data/maker.txt"
	},
	{
		"ticker" : "dai" ,
		"fpath" : str(Path.home())+"/git/pubCryptoAnalysis/api/coin-market-book/raw-data/dai.txt"
	}
]

class Payload(Resource):
	
	def get(self, payload) :
		for file in files :
			if payload == file["ticker"] :
				return Path(file["fpath"]).read_bytes(), 200
		return "File not found", 404
	
	def post(self) :
		return "POST Methods not Allowed", 400

	def put(self) :
		return "PUT Methods not Allowed", 400
	
	def delete(self, name) :
		return "DELETE Methods not Allowed", 400


api.add_resource(Payload , "/payload/<string:ticker>")

app.run(host='0.0.0.0', debug=True)
