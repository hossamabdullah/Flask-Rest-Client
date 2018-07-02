import json
from app import app
from flask import request, jsonify
from flask_restful import Api, Resource, reqparse
from werkzeug.datastructures import FileStorage
import os


api = Api(app)

from models import Pet
from Utils import Util

class PetInsertionAPI(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id', location='json', required=True, help="id is required")
        self.parser.add_argument('category', type=dict, location='json', required=True, help="category is required and it has to be of type dict")
        self.parser.add_argument('name', location='json', required=True, help="name is required")
        self.parser.add_argument('photoUrls', location='json', action='append', required=True, help="photoUrls is required")
        self.parser.add_argument('tags', type=dict, location='json', action='append', required=True, help="tags is required and it has to be of type dict")
        self.parser.add_argument('status', location='json', required=True, help="status is required")

    def post(self):
        args = self.parser.parse_args()

        if(not Util._isValidStatus(args["status"])):
            return app.config["INVALID_STATUS"], 405

        pet = Pet(**args).save()
        pet = Util._formatPetToJson(pet)
        return pet, 200
        pass

    def put(self):
        args = self.parser.parse_args()

        if(not Util._isValidStatus(args["status"])):
            return app.config["INVALID_STATUS"], 405
        try:
            id = int(args['id'])
        except ValueError:
            return app.config["INVALID_ID_ERROR"], 400

        try:
            Pet.objects.get(id= id)
            pet = Pet(**args).save()
            pet = Util._formatPetToJson(pet)
            return pet,200
        except Pet.DoesNotExist:
            return app.config["NOT_FOUND_ERROR"], 404
        pass

class PetStatusAPI(Resource):
    def get(self):
        # preparing query
        status = request.args.getlist("status")

        allPets = []
        for stat in status:
            if(not Util._isValidStatus(stat)):
                return app.config["INVALID_STATUS"], 400
            pets = Pet.objects(status = stat)
            allPets.extend(pets)

        # prepare result for response
        petsList = []
        for pet in allPets:
            pet = Util._formatPetToJson(pet)
            petsList.append(pet)

        return petsList, 200
        pass



class PetQueryingAPI(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', location='form')
        self.parser.add_argument('status', location='form')


    def get(self, id):
        id = Util._isValidId(id)
        if not id:
            return app.config["INVALID_ID_ERROR"], 400

        try:
            pet = Pet.objects.get(id=id)
            pet = Util._formatPetToJson(pet)
            return pet, 200
        except Pet.DoesNotExist:
            return app.config["NOT_FOUND_ERROR"], 404
        pass

    def post(self, id):
        args = self.parser.parse_args()

        id = Util._isValidId(id)
        if not id:
            return app.config["INVALID_ID_ERROR"], 400

        if(not Util._isValidStatus(args["status"])):
            return app.config["INVALID_STATUS"], 405

        try:
            pet = Pet.objects.get(id= id)
            pet.name = args["name"]
            pet.status = args["status"]
            pet.save()
            pet = Util._formatPetToJson(pet)
            return pet, 200
        except Pet.DoesNotExist:
            return app.config["NOT_FOUND_ERROR"], 404
        pass

    def delete(self, id):
        api_key = request.headers.get('api_key')
        if(not (api_key == app.config["API_KEY"])):
            return app.config["INVALID_API_KEY"], 400

        id = Util._isValidId(id)
        if not id:
            return app.config["INVALID_ID_ERROR"], 400

        try:
            pet = Pet.objects.get(id= id)
            res = pet.delete()
            return app.config["DELETE_SUCCESS"], 200
        except Pet.DoesNotExist:
            return app.config["NOT_FOUND_ERROR"], 404
        pass

class PetImageAPI(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('additionalMetadata')
        self.parser.add_argument('file', type=FileStorage, location='files', required=True, help="Please upload a file.")

    def post(self, id):
        args = self.parser.parse_args()

        #validate Id
        id = Util._isValidId(id)
        if not id:
            return app.config["INVALID_ID_ERROR"], 400


        #checking if pet with id exists
        try:
            pet = Pet.objects.get(id= id)
        except Pet.DoesNotExist:
            return app.config["NOT_FOUND_ERROR"], 404

        #checking if the file is image
        if(not (self._isValidImage(args["file"].content_type))):
            return "Invalid Image File please sent image in one of the following formats (gif, jpg, jpeg, png, webp, svg)", 400

        #save the file on local system
        fileName = self._saveFile()

        #update the document
        self._updateDocument(fileName, pet)

        #send the response
        response = {"code":200,
                    "type": args["file"].content_type,
                    "message": "file was uploaded to "+fileName}
        return response, 200
        pass

    def _isValidImage(self, contentType):
        if((contentType == "image/gif")
        or (contentType == "image/jpeg")
        or (contentType == "image/jpg")
        or (contentType == "image/png")
        or (contentType == "image/webp")
        or (contentType == "image/svg+xml") ):
            return True;
        else:
            return False;

    def _updateDocument(self, fileName, pet):
        fileLink = app.config["IMAGES_LINK"]+fileName
        pet.photoUrls.append(fileLink)
        pet.save()

    def _saveFile(self):
        args = self.parser.parse_args()
        path = os.path.join(app.instance_path, '..', app.config["IMAGES_FILE_PATH"])
        fileName = args["file"].filename
        fileName = self._getUniqueFileName(path, fileName)
        filePath = path+fileName

        args["file"].save(filePath)
        return fileName

    def _getUniqueFileName(self, path, fileName):
        while os.path.isfile(path+fileName):
            index = fileName.rfind(".")
            fileName = fileName[:index]+"1."+fileName[index+1:]
        return fileName

api.add_resource(PetImageAPI, '/pet/<string:id>/uploadImage', endpoint = 'PetImageAPI')
api.add_resource(PetQueryingAPI, '/pet/<string:id>', endpoint = 'PetQueryingAPI')
api.add_resource(PetStatusAPI, '/pet/findByStatus', endpoint = 'PetStatusAPI')
api.add_resource(PetInsertionAPI, '/pet', endpoint = 'PetInsertionAPI')
