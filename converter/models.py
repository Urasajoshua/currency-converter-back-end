from django.db import models


class Currency(models.Model):
    code = models.CharField(max_length=3,unique=True)
    rate = models.FloatField()
    
class updatedLog(models.Model):
    updated_at=models.DateTimeField(auto_now=True)
