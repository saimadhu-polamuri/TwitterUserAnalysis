# Quick Python script to analysis twitter user Behaviour.
__autor__ = 'saimadhu Polamuri'
__website__ = 'www.dataaspirant.com'
__createdon__ = '21-jan-2015'

import tweepy
import re
import commands
import os
import datetime
import json
import string
import operator
import nltk
import pandas as pd
import plotly.plotly as py
from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
from dateutil.parser import *
from datetime import *
from dateutil import parser
import collections
from collections import Counter
from math import ceil
from textblob import TextBlob
from collections import Counter
from textblob.np_extractors import ConllExtractor
from plotly.graph_objs import *

py.sign_in(plotly_username, access_token)
consumer_key = your_consumer_key
consumer_secret = your_consumer_secret
access_token = your_access_token
access_token_secret = your_access_token_secret

class UserAnalytics():

    """ Analysing user and getting some user statistics  """

    def __init__(self,api,profile_screen_name):

        """ Initial funtion to get profile_screen_name details """

        self.api = api
        self.profile_screen_name = profile_screen_name
        self.user = self.api.get_user(screen_name = self.profile_screen_name)
        self.now =  parse(commands.getoutput("date"))
        self.today =  self.get_datetime(self.now.ctime())

    def user_latest_tweets(self):

        """ Function to get user latest tweets """

        time_line = self.user.timeline()
        recent_tweets_list = []
        tweet_counter = 0
        for single_tweet in time_line:
            if (single_tweet.text[0] != '@' and single_tweet.text[:2] != 'RT'):
                recent_tweets_list.append(self.tweet_purely(single_tweet.text))
        
        return recent_tweets_list

    def avg_tweets_month(self):

        """ Returns the average tweets per month """

        tweets_and_dates_dict = {}
        time_line = self.user.timeline()
        for single_tweet in time_line:
            tweets_and_dates_dict[single_tweet.created_at] = self.tweet_purely(single_tweet.text)
        od = collections.OrderedDict(sorted(tweets_and_dates_dict.items()))
        datetime_list = od.keys()
        datetime_list.reverse()
        result = self.time_difference_seconds(datetime_list[0],datetime_list[-1]) / (len(datetime_list)-1)

        return result,datetime_list

    def get_datetime(self,date):

        """ Returns date from string """

        self.date = date

        result = parser.parse(self.date,dayfirst=True)

        return result

    def user_followers_following_statistics(self):

        """ Function to analysis user follower and following data to get some statistics """

        statistics_dict = {}
        statistics_dict['user_following_count'] = self.user.friends_count
        statistics_dict['user_followers_count'] = self.user.followers_count
        statistics_dict['created_date'] = self.user.created_at
        datetime_data = self.get_months(self.user.created_at)
        statistics_dict['number_of_seconds'] = datetime_data['seconds']
        statistics_dict['number_of_monts'] = datetime_data['months']

        return statistics_dict

    def get_months(self,user_created_date):

        """ Function to return number of months passed after user created twitter account """

        self.user_created_date = user_created_date

        datetime = {}
        result = relativedelta(self.today,self.user_created_date)
        total_days = (result.years * 365) + (result.months * 30) + result.days
        total_seconds = (result.years*31556926)+(result.months*2629744)+(result.days*86400)+(result.hours*3600)+(result.minutes*60)+(result.seconds)
        datetime['seconds'] = total_seconds
        datetime['months'] = total_days /30

        return datetime

    def tweet_purely (self,tweet_text):

        """ Function to pure tweet text """

        self.tweet_text = tweet_text

        s = unicode(self.tweet_text).encode('ascii','ignore')
        
        return s.encode("utf-8")

    def seconds_ymwdhms(self,seconds,granularity = 5):

        """ return years, months, weeks, days, hours, min, sec from seconds """

        self.seconds = seconds
        self.granularity = granularity

        result = []
        intervals = (
            ('years',31556926), # 60 *  60 * 24 * 30 * 12
            ('months',2629744), # 60 *  60 * 24 * 30
            ('weeks', 604800),  # 60 * 60 * 24 * 7
            ('days', 86400),    # 60 * 60 * 24
            ('hours', 3600),    # 60 * 60
            ('minutes', 60),
            ('seconds', 1),
            )
        for name, count in intervals:
            value = self.seconds // count
            if value:
                self.seconds -= value * count
                if value == 1:
                    name = name.rstrip('s')
                result.append("{} {}".format(value, name))
        
        return ', '.join(result[:self.granularity])

    def time_difference_seconds(self, first_datetime, second_datetime):

        """  return the difference between two times in seconds """

        self.first_datetime = first_datetime
        self.second_datetime = second_datetime

        result = relativedelta(self.first_datetime,self.second_datetime)
        total_days = (result.years * 365) + (result.months * 30) + result.days
        total_seconds = (result.years*31556926)+(result.months*2629744)+(result.days*86400)+(result.hours*3600)+(result.minutes*60)+(result.seconds)
        
        return total_seconds

    def convert_datetime_format(self,datetime):

        """ Converts datetime to specific format """

        self.datetime = datetime

        d = datetime.strptime(str(self.datetime), '%Y-%m-%d %H:%M:%S')
        
        return d.strftime('%Y %b %d %H:%M:%S')

    def expected_next_tweet(self,last_tweet_datetime,avg_tweets_seconds):

        """ returns user expected next tweet datetime """

        self.last_tweet_datetime = last_tweet_datetime
        self.avg_tweets_seconds = avg_tweets_seconds

        next_tweet_time =  last_tweet_datetime+ timedelta(seconds= avg_tweets_seconds)
        
        return self.convert_datetime_format(next_tweet_time)

    def favorite_week(self, tweets_datetime_list):

        """ Returns user favorite week """
        
        self.tweets_datetime_list = tweets_datetime_list

        weekdays_list = []
        for single_datetime in self.tweets_datetime_list:
            weekdays_list.append(self.datetime_weekday(single_datetime))
        weeks_count = Counter(weekdays_list)
        weekdays_count_dict = {}
        for key, value in zip(weeks_count.keys(),weeks_count.values()):
            weekdays_count_dict[key] = value
        
        return sorted([(value,key) for (key,value) in weekdays_count_dict.items()])[-1][1],weekdays_count_dict

    def datetime_weekday(self,datetime):

        """ Returns weekday for a given datetime """

        self.datetime = datetime

        return datetime.strptime(str(self.datetime),'%Y-%m-%d %H:%M:%S').strftime('%A')

    def tweet_sentiment_score(self,tweet):

        """ Returns single tweet sentiment score """

        self.tweet = tweet

        Blob_review = TextBlob(self.tweet)
        sentiment_value = Blob_review.sentiment
        sentiment_polarity_value = sentiment_value.polarity
        sentiment_value= ceil(sentiment_polarity_value*1000)/1000.0
        
        return sentiment_value

    def tweet_cleanup(self,tweet):

        """ Function to remove website links, special characters and twitter users names in Tweets """
        
        self.tweet = tweet

        URLless_string = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', self.tweet)
        twitteruser_remove_string = re.sub(r'@[A-Za-z0-9_]+', '', URLless_string)
        chars = re.escape(string.punctuation)
        pure_tweet = re.sub(r'['+chars+']', '',twitteruser_remove_string)
        final_string = ((pure_tweet.rstrip()).strip()).lower()
        
        return final_string

    def tweets_sentiment_score(self, tweets_list):

        """ Returns tweets sentiment score and percentage of positive tweets , negative tweets , neutral tweets """

        self.tweets_list = tweets_list

        sentiment_score_list = []
        for tweet in self.tweets_list:
            sentiment_score_list.append(self.tweet_sentiment_score(self.tweet_cleanup(tweet)))
        
        return sentiment_score_list

    def sentiment_percentage(self, sentiment_score_list):

        """ Returns sentiment percentage like percentage of Positive tweets , Negative tweets and Neutral tweets """

        self.sentiment_score_list = sentiment_score_list
        self.lenght_score_list = len(sentiment_score_list)

        pos_count =  sum(x > 0 for x in self.sentiment_score_list)
        neg_count = sum(x <  0 for x in self.sentiment_score_list)
        zero_count = self.sentiment_score_list.count(0)
        total_sentiment = sum([x for x in self.sentiment_score_list])
        effective_count = self.lenght_score_list - zero_count
        sentiment_results = {}
        sentiment_results['sentiment_positiveness'] = (ceil((pos_count / float(self.lenght_score_list)* 100 )*100)/100.0)
        sentiment_results['sentiment_negativeness'] = (ceil((neg_count / float(self.lenght_score_list)* 100 )*100)/100.0)
        sentiment_results['sentiment_neutralness'] = (ceil((zero_count / float(self.lenght_score_list)* 100 )*100)/100.0)
        sentiment_results['overall_sentiment'] = (ceil((total_sentiment / float(effective_count)* 100 )*100)/100.0)
        
        return sentiment_results

    def frequently_used_words(self,tweets_list):

        """ Returns most frequently used words from all tweets for user """

        self.tweets_list = tweets_list

        total_words_list = []
        words_frequence_dict = {}
        for single_tweet in self.tweets_list:
            clean_tweet = self.tweet_cleanup(single_tweet)
            for single_word in clean_tweet.split():
                if len(single_word) >2 and self.find_IN_partsofspeech(single_word): 
                    total_words_list.append(single_word)
        word_counts = Counter(total_words_list)
        for key,value in zip(word_counts.keys()[0:],word_counts.values()[0:]):
            words_frequence_dict[key] = value
        sorted_dict = sorted(words_frequence_dict.items(), key=operator.itemgetter(1))
        sorted_dict.reverse()
        
        return sorted_dict[:5],total_words_list

    def find_IN_partsofspeech(self,word):
    
        """ Function to find the give word partsofspeech and return the False value if it existed in specific remove partsofspeech list """

        self.word = word

        remove_partsofspeech_list = ['IN','CC','CD','DT','MD','PRP','VBP']
        
        return False if TextBlob(self.word).tags[0][1] in remove_partsofspeech_list else True

    def high_sentiment_words(self,words_list):

        """ Returns high sentiment words from list of words """

        self.words_list = words_list

        sentiment_words_dict = {}
        for word in self.words_list:
            sentiment_words_dict[word] = self.tweet_sentiment_score(word)
        sorted_dict = sorted(sentiment_words_dict.items(), key=operator.itemgetter(1))
        sorted_dict.reverse()
       
        return sorted_dict[:5]

    def remove_dict_element(self,dict_values,key_value):

        """ Removes key and key value for given dict """

        self.dict_values = dict_values
        self.key_value = key_value

        del self.dict_values[self.key_value]
        
        return self.dict_values

    def bar_graph(self,values_dict,title_name,x_axis_name,y_axies_name):

        """ Creates bar graph """

        self.values_dict = values_dict
        self.title_name = title_name
        self.x_axis_name = x_axis_name
        self.y_axies_name = y_axies_name

        trace1 = Bar(
            x =  self.values_dict.keys(),
            y = self.values_dict.values(),
            name = self.title_name,
            )
        data = Data([trace1])
        layout = Layout(
            title = self.title_name,
            autosize=False,
            width=1000,
            height=500,
            xaxis=XAxis(
                title = self.x_axis_name,
                showgrid=False,
                zeroline=False
            ),
            yaxis=YAxis(
                title = self.y_axies_name,
                showline=False
            ),
        )
        fig = Figure(data=data, layout=layout)
        plot_url = py.plot(fig, filename='grouped-bar')
        
        return plot_url
    

    def user_sentiment_label(self,results):

        """ Returns sentiment label for user from user sentiment_percentage_dict """

        self.results = results

        label_dict = {'sentiment_positiveness': 'POSITIVE','sentiment_negativeness': 'NEGATIVE', 'sentiment_neutralness': 'NEUTRAL'}
        sorted_dict = sorted(self.results.items(), key=operator.itemgetter(1))
        sorted_dict.reverse()
        label_key = sorted_dict[0][0]
        
        return label_dict[label_key]

def main():

    """ Main Function for creating UserAnalytics instance to use all the functions in UserAnalytics """

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    screen_name = 'saimadhup'
    useranalytics = UserAnalytics(api,screen_name)
    recent_tweets = useranalytics.user_latest_tweets()
    print recent_tweets
    statistics_ = useranalytics.user_followers_following_statistics()
    print statistics_
    avg_tweets_seconds,tweets_datetime_list = useranalytics.avg_tweets_month()
    avg_datetime_to_tweet = useranalytics.seconds_ymwdhms(avg_tweets_seconds)
    expected_next_tweet = useranalytics.expected_next_tweet(tweets_datetime_list[0],avg_tweets_seconds)
    print avg_datetime_to_tweet
    print expected_next_tweet
    print tweets_datetime_list
    user_favorite_weekday,weekdays_count_dict = useranalytics.favorite_week(tweets_datetime_list)
    print user_favorite_weekday
    print weekdays_count_dict
    sentiment_score_list = useranalytics.tweets_sentiment_score(recent_tweets)
    print sentiment_score_list
    sentiment_percentage_dict = useranalytics.sentiment_percentage(sentiment_score_list)
    print sentiment_percentage_dict
    frequent_words,total_words = useranalytics.frequently_used_words(recent_tweets)
    print frequent_words
    print useranalytics.high_sentiment_words(total_words)
    tweets_week_graph = useranalytics.bar_graph(weekdays_count_dict,'Weekdays Vs Tweets','weeks','Tweets')
    tweets_sentiment_graph = useranalytics.bar_graph(useranalytics.remove_dict_element(sentiment_percentage_dict,'overall_sentiment'),'overal sentiment percentage','sentiment label','sentiment percentage')
    useranalytics.user_sentiment_label(useranalytics.remove_dict_element(sentiment_percentage_dict,'overall_sentiment'))

if __name__ == "__main__":
    main()