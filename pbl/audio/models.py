from django.db import models


class AudioStore(models.Model):
        record = models.FileField(upload_to='documents/')
        class Meta:
            db_table = 'AudioStore'
