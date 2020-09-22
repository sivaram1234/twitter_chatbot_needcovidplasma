import tweepy
import gspread
import time
from oauth2client.service_account import ServiceAccountCredentials

#twitter bot authentication
consumer_key="---your data here--------"
consumer_secret="---your data here--------"
key="---your data here--------"
secret="---your data here--------"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(key, secret)
api = tweepy.API(auth)

# google sheets authentication
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds=ServiceAccountCredentials.from_json_keyfile_name("---your JSON here--------",scope)
client=gspread.authorize(creds)
sheet=client.open("twitterBot").sheet1
#hashtag_reply_sheet=client.open("twitterBot").sheet2

#initial variable
last_tweet_mentioned_replied_id_X=4
last_tweet_mentioned_replied_id_Y=1

last_hashtag_replied_id_X=7
last_hashtag_replied_id_Y=1

reply_message_X=2
reply_message_Y=2

insert_row_number=19

number_of_mentions_replied_X=10
number_of_mentions_replied_Y=1

number_of_hashtags_replied_X=13
number_of_hashtags_replied_Y=1


#------mentioned part
def mentioned_tweet_reply():
    print('\n')
    print("mentioned_tweet_reply function")
    tweets_mentions=api.mentions_timeline()
    last_tweet_mentioned_replied_id=sheet.cell(last_tweet_mentioned_replied_id_X,last_tweet_mentioned_replied_id_Y).value
    print(last_tweet_mentioned_replied_id)
    #print(type(last_tweet_mentioned_replied_id))
    for tweet in tweets_mentions:
        time.sleep(int(sheet.cell(17,3).value))
        #print(tweet.id)
        if(tweet.id==int(last_tweet_mentioned_replied_id)):
            print("No more new mention")
            print("Replied all recent mentioned")
            print("Updating ID in sheet")
            sheet.update_cell(last_tweet_mentioned_replied_id_X,last_tweet_mentioned_replied_id_Y,str(tweets_mentions[0].id))
            return
        else:
            print(tweet.id)
            reply_message=sheet.cell(reply_message_X,reply_message_Y).value
            if(tweet.in_reply_to_status_id!=None):
                #---------------------------------------------------------------Tweets of mentioned as reply
                try:
                    #print(tweet.id)
                    print("New mention as a reply")
                    if(tweet.in_reply_to_screen_name=="needcovidplasma"):
                        print("Updating ID in sheet")
                        sheet.update_cell(last_tweet_mentioned_replied_id_X,last_tweet_mentioned_replied_id_Y,str(tweets_mentions[0].id))
                        return
                    else:
                        reply_message="@"+tweet.in_reply_to_screen_name + reply_message
                        api.update_status(reply_message,tweet.in_reply_to_status_id)
                        sheet.update_cell(number_of_mentions_replied_X,number_of_mentions_replied_Y,str(int(sheet.cell(number_of_mentions_replied_X,number_of_mentions_replied_Y).value)+1))
                        print("Updating a row sheet")
                        new_row=[]
                        new_row.append(str(tweet.in_reply_to_status_id))
                        new_row.append(time.ctime())
                        new_row.append("Reply mention")
                        sheet.insert_row(new_row,insert_row_number)
                except tweepy.TweepError as e:
                    print(e.reason)
            else:
                #------------------------------------------------------------------Tweets of mentioned directly
                try:
                    print("New mention directly")
                    reply_message="@"+tweet.user.screen_name + reply_message
                    api.update_status(reply_message,tweet.id)
                    sheet.update_cell(number_of_mentions_replied_X,number_of_mentions_replied_Y,str(int(sheet.cell(number_of_mentions_replied_X,number_of_mentions_replied_Y).value)+1))
                    print("Updating a row sheet")
                    new_row=[]
                    new_row.append(str(tweet.id))
                    new_row.append(time.ctime())
                    new_row.append("Direct mention")
                    sheet.insert_row(new_row,insert_row_number)
                except tweepy.TweepError as e:
                    print(e.reason)
    print("Replied all recent mentioned")
    print("Updating ID in sheet")
    sheet.update_cell(last_tweet_mentioned_replied_id_X,last_tweet_mentioned_replied_id_Y,str(tweets_mentions[0].id))


#----Hashtag searching
def checkTorRT(text):
    return (text[0]=='R' and text[1]=='T')

def searchBot(h,n,sc):
    print('\n')
    print("SearchBot function")
    hashtag=h
    tweet_num=n
    search_tweets=tweepy.Cursor(api.search,hashtag).items(tweet_num)
    for tweet in search_tweets:
        text=tweet.text
        #print(text)
        second_check=sc.lower()
        text=text.lower()
        if second_check in text:
            try:
                print(tweet.id)
                reply_message=sheet.cell(reply_message_X,reply_message_Y).value
                if(checkTorRT(tweet.text)):
                    #-----------------------------This is a Retweet
                    print("This is a retweet")
                    #print(tweet.retweeted_status)
                    print(tweet.retweeted_status.id)
                    print(tweet.retweeted_status.user.screen_name)
                    reply_message="@"+tweet.retweeted_status.user.screen_name+reply_message
                    print("updating")
                    #api.update_status(reply_message,tweet.retweeted_status.id)
                    print("updated")
                    #api.retweet(tweet.retweeted_status.id)
                    #api.create_favorite(tweet.retweeted_status.id)
                    print("Updating in sheet")
                    new_row=[]
                    new_row.append(str(tweet.retweeted_status.id))
                    new_row.append(time.ctime())
                    new_row.append("#hashtag")
                    sheet.insert_row(new_row,insert_row_number)
                    sheet.update_cell(last_hashtag_replied_id_X,last_hashtag_replied_id_Y,str(tweet.retweeted_status.id))
                    sheet.update_cell(number_of_hashtags_replied_X,number_of_hashtags_replied_Y,str(int(sheet.cell(number_of_hashtags_replied_X,number_of_hashtags_replied_Y).value)+1))

                else:
                    #-----------------------------This is a Tweet
                    print("This is a tweet")
                    print(tweet.id)
                    print(tweet.user.screen_name)
                    reply_message="@"+tweet.user.screen_name+reply_message
                    api.update_status(reply_message,tweet.id)
                    #api.retweet(tweet.id)
                    #api.create_favorite(tweet.id)
                    print("Updating in sheet")
                    new_row=[]
                    new_row.append(str(tweet.id))
                    new_row.append(time.ctime())
                    new_row.append("#hashtag")
                    sheet.insert_row(new_row,insert_row_number)
                    sheet.update_cell(last_hashtag_replied_id_X,last_hashtag_replied_id_Y,str(tweet.id))
                    sheet.update_cell(number_of_hashtags_replied_X,number_of_hashtags_replied_Y,str(int(sheet.cell(number_of_hashtags_replied_X,number_of_hashtags_replied_Y).value)+1))

                time.sleep(int(sheet.cell(17,3).value))
            except tweepy.TweepError as e:
                print(e.reason)
                #print(tweet.id)
                time.sleep(2)
        else:
            print("Not a correct tweet")
            time.sleep(int(sheet.cell(17,3).value))
    print("-----------------given reply to #hastags------------\n")

#----------Bot administartion index function
bot_administration_X=7
bot_administration_Y=3
def bot_administration():
    command=sheet.cell(bot_administration_X,bot_administration_Y).value
    if(command.lower()=="start"):
        return "T"
    if(command.lower()=="stop"):
        return "F"
    return "F"

#----------Starting of the main function
#mentioned_tweet_reply()
#searchBot()
print("Starting twitter Bot\n")

i=1
while(1):
    main_command=bot_administration()
    print(main_command)
    hashtag1=sheet.cell(10,3).value
    hashtag2=sheet.cell(11,3).value
    process_halt_sec=int(sheet.cell(13,3).value)
    num_reply_rate=int(sheet.cell(15,3).value)
    if(main_command=="T"):
        print("---   Looping through twitter ----")
        status_msg="Looped "+str(i)+" time's"
        i=i+1
        sheet.update_cell(2,3,status_msg)
        time.sleep(int(sheet.cell(17,3).value))
        mentioned_tweet_reply()
        time.sleep(int(sheet.cell(17,3).value))
        searchBot(hashtag1,num_reply_rate,hashtag2)
    else:
        print("---Process halted----")
        status_msg="Process halted after "+str(i)+" time's"
        sheet.update_cell(2,3,status_msg)
    time.sleep(process_halt_sec)

print("Stoping twitter Bot")

