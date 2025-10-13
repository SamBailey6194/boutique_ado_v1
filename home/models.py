from django.db import models
from custom_storages import MediaStorage


class MyModel(models.Model):
    file = models.FileField(storage=MediaStorage(), upload_to='uploads/')

    def __str__(self):
        return self.file.name
