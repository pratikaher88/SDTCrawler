from rest_framework import serializers
from .models import URL_Details,Quote

class ListURLDetailsSerializer(serializers.ModelSerializer):

	class Meta:
		model = URL_Details
		fields = ['site_name','total_violations','total_verify','total_pass']

class ListCrawledURLsSerializer(serializers.ModelSerializer):

	class Meta:
		model = Quote
		fields = ['text']

