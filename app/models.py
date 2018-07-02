from mongoengine import Document
from mongoengine.fields import StringField, DictField, ListField, IntField

class Pet(Document):
    id = IntField(primary_key=True)
    category = DictField()
    name = StringField()
    photoUrls = ListField(StringField())
    tags =  ListField(DictField())
    status = StringField()
