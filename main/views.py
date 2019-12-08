from uuid import uuid4
from urllib.parse import urlparse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST, require_http_methods
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from scrapyd_api import ScrapydAPI
import random, requests
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect
from rest_framework import generics
from .serializers import ListURLDetailsSerializer,ListCrawledURLsSerializer


# from main.utils import URLUtil
# from main.models import ScrapyItem
from main.models import Quote, URL_Details

# connect scrapyd service
scrapyd = ScrapydAPI('http://localhost:6800')

scrapy_error = "Scrapyd returned a 500 error: <html><head><title>Processing Failed</title></head><body><b>Processing Failed</b></body></html>"

def is_valid_url(url):
    validate = URLValidator()
    try:
        validate(url)  # check if url format is valid
    except ValidationError:
        return False

    return True


@csrf_exempt
@require_http_methods(['POST', 'GET'])  # only get and post
def crawl(request):
    # Post requests are for new crawling tasks
    if request.method == 'POST':

        url = request.POST.get('url', None)  # take url comes from client. (From an input may be?)

        if not url:
            return JsonResponse({'error': 'Missing  args'})

        if not is_valid_url(url):
            return JsonResponse({'error': 'URL is invalid'})

        domain = urlparse(url).netloc  # parse the url and extract the domain
        unique_id = str(uuid4())  # create a unique ID.

        # This is the custom settings for scrapy spider.
        # We can send anything we want to use it inside spiders and pipelines.
        # I mean, anything
        settings = {
            'unique_id': unique_id,  # unique ID for each record for DB
            'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        }

        # Here we schedule a new crawling task from scrapyd.
        # Notice that settings is a special argument name.
        # But we can pass other arguments, though.
        # This returns a ID which belongs and will be belong to this task
        # We are goint to use that to check task's status.
        task = scrapyd.schedule('default', 'icrawler',
                                settings=settings, url=url, domain=domain)

        return JsonResponse({'task_id': task, 'unique_id': unique_id, 'status': 'started'})

    # Get requests are for getting result of a specific crawling task
    elif request.method == 'GET':
        # We were passed these from past request above. Remember ?
        # They were trying to survive in client side.
        # Now they are here again, thankfully. <3
        # We passed them back to here to check the status of crawling
        # And if crawling is completed, we respond back with a crawled data.
        task_id = request.GET.get('task_id', None)
        unique_id = request.GET.get('unique_id', None)

        if not task_id or not unique_id:
            return JsonResponse({'error': 'Missing args'})

        # Here we check status of crawling that just started a few seconds ago.
        # If it is finished, we can query from database and get results
        # If it is not finished we can return active status
        # Possible results are -> pending, running, finished
        status = scrapyd.job_status('default', task_id)
        if status == 'finished':
            try:
                # this is the unique_id that we created even before crawling started.
                item = ScrapyItem.objects.get(unique_id=unique_id)
                return JsonResponse({'data': item.to_dict['data']})
            except Exception as e:
                return JsonResponse({'error': str(e)})
        else:
            return JsonResponse({'status': status})


def displayModelObjects(request):

    objects_quote = Quote.objects.all()

    return render(request,'display_quotes.html', {'details': objects_quote })



def calculateScoreandDisplay(request):

    calculated_objects = URL_Details.objects.all()

    if calculated_objects.count() <= 0 :



        array_urls = Quote.objects.values_list('text', flat=True)
        array_urls = list(array_urls)
        
        score_urls = random.sample(array_urls, 10)

        for value in iter(score_urls):



            url = "http://axe.checkers.eiii.eu/export-jsonld/pagecheck2.0/?url=" + value

            r = requests.get(url=url)
            data = r.json()


            total_violations = 0
            total_verify = 0
            total_pass = 0

            for violations in data['result-blob']['violations']:

                if any("wcag" in w for w in violations['tags']):

                    total_violations += len(violations['nodes'])


            for incomplete in data['result-blob']['incomplete']:

                if any("wcag" in w for w in incomplete['tags']):

                    total_verify += len(incomplete['nodes'])


            for passes in data['result-blob']['passes']:

                if any("wcag" in w for w in passes['tags']):

                    total_pass += len(passes['nodes'])

            
            calculated_score = URL_Details(site_name=value, total_violations = total_violations,total_verify = total_verify
                                                ,total_pass = total_pass)
            calculated_score.save()

    return render(request,'calculate_scores.html', {'details': calculated_objects })

def displayCalculatedScores(request): 


    url_details = URL_Details.objects.all()

    return render(request,'calculate_scores.html', {'details': url_details })


def sendRequestToAPI(request):

    Quote.objects.all().delete()

    try:
        task = scrapyd.schedule('default', 'toscrape-css')

    except Exception :
        pass
        # print(e)
        # if e == scrapy_error: 
        #     print("Hello")
        # 
    # objects_quote = Quote.objects.all()
    # return render(request,'display_quotes.html', {'details': objects_quote })
    return redirect(reverse('display-results'))
        



def clearQuote(request):

    Quote.objects.all().delete()

    return None


@require_http_methods(['POST', 'GET']) 
def findDetails(request):

    if request.method == 'POST':
        
        website_name = request.POST.get('website_name')

        print("Website Name",website_name)
        
        domain = urlparse(website_name).netloc
        
        print("Domain",domain)

        Quote.objects.all().delete()
        URL_Details.objects.all().delete()

        # task = 1

        try:
            task = scrapyd.schedule('default', 'toscrape-css',url=website_name,domain=domain)

        except Exception :
            pass
        
        
        return render(request,'crawling_started.html')


        # calculateScoreandDisplay(request)

        # status = scrapyd.job_status('default', task)

        # print(status)
    
    return render(request,'find_details.html')


	# return render(request,'find_details.html',{'id':1})


    # return render(request,'find_details.html')


def csd():

    array_urls = Quote.objects.values_list('text', flat=True)
    array_urls = list(array_urls)
    
    score_urls = random.sample(array_urls, 10)

    for value in iter(score_urls):



        url = "http://axe.checkers.eiii.eu/export-jsonld/pagecheck2.0/?url=" + value

        r = requests.get(url=url)
        data = r.json()


        total_violations = 0
        total_verify = 0
        total_pass = 0

        for violations in data['result-blob']['violations']:

            if any("wcag" in w for w in violations['tags']):

                total_violations += len(violations['nodes'])


        for incomplete in data['result-blob']['incomplete']:

            if any("wcag" in w for w in incomplete['tags']):

                total_verify += len(incomplete['nodes'])


        for passes in data['result-blob']['passes']:

            if any("wcag" in w for w in passes['tags']):

                total_pass += len(passes['nodes'])

        
        calculated_score = URL_Details(site_name=value, total_violations = total_violations,total_verify = total_verify
                                            ,total_pass = total_pass)
        calculated_score.save()

    return render(request,'calculate_scores.html', {'details': calculated_objects })



class ListURLDetailsView(generics.ListAPIView):
    queryset = URL_Details.objects.all()
    serializer_class = ListURLDetailsSerializer


class ListCrawledURLsView(generics.ListAPIView):
        queryset = Quote.objects.all()
        serializer_class = ListCrawledURLsSerializer

