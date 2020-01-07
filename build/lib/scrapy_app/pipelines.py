# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
# from main.models import Quote

from scrapy_app.settings import DATABASE_URL
import psycopg2
from scrapy_app.models import Quote, db_connect
from scrapy.exceptions import DropItem
from scrapy_app.models import Quote,URL_details, db_connect
from sqlalchemy.orm import sessionmaker
import random
import requests
from datetime import datetime
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

def retry_session(retries, session=None, backoff_factor=0.3, status_forcelist=(500, 502, 503, 504)):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

class ScrapyAppPipeline(object):

    def __init__(self):
        engine = db_connect()
        self.Session = sessionmaker(bind=engine)

    #     self.conn = psycopg2.connect(DATABASE_URL)

    # def open_spider(self,spider):
        # spider.started_on = datetime.now()





    #     session = self.Session()

    #     try:
    #         session.execute('''TRUNCATE TABLE main_quote''')
    #         session.execute('''TRUNCATE TABLE main_url_details''')
    #         session.commit()

    #     except:
    #         session.rollback()
    #         raise

    #     finally:
    #         session.close()



    def process_item(self, item, spider):
        
        session = self.Session()

        # print("JJDD",spider.job_id)

        quote = Quote()

        quote.job_data_id = spider.job_data_id

        quote.url_content = item["text"]


        try:
            session.add(quote)
            session.commit()

        except:
            session.rollback()
            raise

        finally:
            session.close()

        return item


    def close_spider(self, spider):

        # work_time = datetime.now() - spider.started_on (Time to Crawl)


        session = self.Session()

        session_retry = retry_session(retries=5)

        quote = ["%s" % v for v in session.query(
            Quote.url_content).filter_by(job_data_id=spider.job_data_id)] # removed .all() here to filter records for that code

        score_urls = random.sample(quote, 10)

        for value in iter(score_urls):

            url = "http://axe.checkers.eiii.eu/export-jsonld/pagecheck2.0/?url=" + value

            # print("URL Value",url)

            headers = {'User-Agent': 'Mozilla/5.0'}

            # r = requests.get(url=url,headers=headers)

            r = session_retry.get(url=url, headers=headers)

            if r.status_code == 504:
                continue
            # retry mechanism : test it in pycharm 

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

            
            url_details = URL_details()

            url_details.job_data_id = spider.job_data_id

            url_details.site_name = value

            url_details.total_violations = total_violations

            url_details.total_verify = total_verify

            url_details.total_pass = total_pass

            url_details.total_score = str(float("{0:.5f}".format(data['score'])))

            try:
                session.add(url_details)
                session.commit()

            except:
                session.rollback()
                raise

            # calculated_score = URL_Details(
            #     site_name=value, total_violations=total_violations, total_verify=total_verify, total_pass=total_pass)
            # calculated_score.save()

        # print("Quote",quote)    

        session.close()
    
    # work_time = datetime.now() - spider.started_on



