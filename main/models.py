from django.db import models
from django.core.validators import URLValidator


class Quote(models.Model):
    """
    The scrapped data will be saved in this model
    """
    text = models.TextField()
    author = models.CharField(max_length=512)


class URL_Details(models.Model):

    site_name = models.CharField(max_length=500,validators=[URLValidator()])
    total_violations = models.CharField(max_length=100, blank = True)
    total_verify = models.CharField(max_length=100, blank = True)
    total_pass = models.CharField(max_length=100, blank = True)

# class FeedbackInfoInputModel(models.Model):

#     site_name = models.CharField(max_length=500,validators=[URLValidator()])

