import json, requests, random, re
from pprint import pprint

from django.views import generic
from django.http.response import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

PAGE_ACCESS_TOKEN = ""
VERIFY_TOKEN = ""
SUBSCRIPTION_KEY = ""


import http.client, urllib.request, urllib.parse, urllib.error, base64
# Azure Machine Learning - Text Analytics
headers = {
    # Request headers
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY,
}
params = urllib.parse.urlencode({
})


# This function should be outside the BotsView class
def post_facebook_message(fbid, recevied_message):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":recevied_message}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    pprint(status.json())

def post_text_analytics_message(fbid, recevied_message):
    request_url = 'https://westus.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment'
    response_msg = json.dumps({"documents":[{"language":"en", "id":fbid, "text":recevied_message}]})
    res = requests.post(request_url, headers={"Content-Type": "application/json","Ocp-Apim-Subscription-Key":SUBSCRIPTION_KEY},data=response_msg)
    pprint(res.json())
    post_facebook_message(fbid, res['documents'][0]['score'])



def post_text_analytics(fbid, recevied_message):
    try:
        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        request_msg = json.dumps({"documents":[{"language":"en", "id":fbid, "text":recevied_message}]})
        conn.request("POST", "/text/analytics/v2.0/sentiment?%s" % params, request_msg, headers)
        response = conn.getresponse()
        data = response.read()
        print(data)
        result = json.loads(data.decode('utf-8'))
        print(result['documents'][0]['score'])
        score = result['documents'][0]['score']
        answer = "None"
        if score > 0.5:
            answer = "Positive"
        elif score == 0.5:
            answer = "Neutral"
        else:
            answer = "Negative"
        print("Your sentiment is maybe %s(%f)" % (answer, score))
        post_facebook_message(fbid, "Your sentiment is maybe %s(%f)" % (answer, score))
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))


# Create your views here.
class BotView(generic.View):
    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')

    # The get method is the same as before.. omitted here for brevity
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        # Converts the text payload into a python dictionary
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events 
                if 'message' in message:
                    # Print the message to the terminal
                    pprint(message)
                    # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                    # are sent as attachments and must be handled accordingly. 
                    #post_facebook_message(message['sender']['id'], message['message']['text'])     
                    post_text_analytics(message['sender']['id'], message['message']['text'])
        return HttpResponse()
