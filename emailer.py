from flask import Flask, jsonify, request, abort
import requests

#app initialization
app = Flask(__name__)

#configuration class
class Config(object):
    DEBUG = False
    API_KEY = 'kfhskjhfsjfgeoiuitoigjjgljlgjjslkjslsj'  #insert mailgun api key here. This is obsolete.
    POST_URL = '' #the post url is in this format https://api.mailgun.net/v3/sandboxc7882e137eb74tyfb6aa06g064cae005.mailgun.org/messages. Get it from mailgun

#config app
app.config.from_object(Config)

#Service routes
@app.route('/mailapi/send', methods=['POST'])
def send_email():
    #get json payload and forward to mailgun
    #Validate the json payload beforehand since this is not meant to be a publicly exposed endpoint. An error will be returned if something goes wrong
    payload = request.get_json()
    resp_obj_list = []
    for receiver in payload['targets']:
        #prepare html + payload
        compiled_html = payload['html_template'].format(inserted_content=receiver['html_content'])
        resp = requests.post(
            app.config['POST_URL'],
            auth=("api", app.config['API_KEY']),
            data={"from": "Mailing Services <mailgun@sandboxc8592e137eb74bcgb6aa09g64cae713.mailgun.org>",
                  "to": [receiver['email_target']],
                  "subject": "Placeholder subject",
                  "text": receiver['html_content'],
                  "recipient-variables": '{"rec":{"content":"'+ receiver['html_content'] +'"}}',
                  "html":compiled_html
                  }) # in the data dict, the from should reflect the sandbox details in your mailgun account. receipient variables is for html emails to dynamically add content  
        resp_obj_list.append(resp)


    #assert that all responses are 200
    count = [1 if item.status_code == 200 else 0 for item in resp_obj_list]
    if sum(count) != len(count):
        message = 'Failed to send all messages. Sent: '+ str(sum(count)) + '/' + str(len(count))
        return jsonify({'message':message}), 400
    else:
        message = 'Successfully sent all emails. Sent: '+str(sum(count)) + '/' + str(len(count))
        return jsonify({'message':message}),200
