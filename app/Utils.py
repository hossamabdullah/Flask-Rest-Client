from app import app
import json 

class Util:
    @staticmethod
    def _isValidId(id):
        try:
            id = int(id)
            return id;
        except ValueError:
            return False;

    @staticmethod
    def _isValidStatus(stat):
        exist = False;
        for petState in app.config["STATUS"]:
            if(stat == petState):
                exist = True
                break
        if(exist):
            return True
        else:
            return False

    @staticmethod
    def _formatPetToJson(pet):
        return json.loads(pet.to_json())
