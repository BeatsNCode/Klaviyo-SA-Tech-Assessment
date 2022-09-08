import requests
import os
from twilio.rest import Client

from dotenv import load_dotenv
load_dotenv()

# Loading Klaviyo credentials
klaviyo_public_api_key = 'Qg3FLb'
klaviyo_private_api_key = os.getenv('KLAVIYO_PRIVATE_API_KEY')

# Loading Kickbox Auth token
kickbox_api_key = os.getenv('KICKBOX_API_KEY')

# Loading Twilio credentials, to be used in the Phone Number Lookup Process
twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
twilio_api_key = os.getenv('TWILIO_API_KEY')
client = Client(twilio_account_sid, twilio_api_key)


# First, the Klaviyo List V2 API API will be leveraged to pull data on all members of a list
klaviyo_list_id = 'UwaMMy'

klaviyo_list_members_url = f'https://a.klaviyo.com/api/v2/group/{klaviyo_list_id}/members/all?api_key={klaviyo_private_api_key}'

headers = {"Accept": "application/json"}

response = requests.get(klaviyo_list_members_url, headers=headers)

response_dict = response.json()
list_data = response_dict['records']

email = 'jre.augustin@gmail.com'

# Next, create a function that will run an Email Address through the Kickbox Email Verification API
def kickbox_verify_email(email):
    kickbox_verify_url = f'https://api.kickbox.com/v2/verify?email={email}&apikey={kickbox_api_key}'
    kickbox_response = requests.get(kickbox_verify_url)
    kickbox_results = kickbox_response.json()
    return kickbox_results

# Then, create a function that will run a Phone Number through Twilio's Lookup API
def twilio_phone_lookup(phone_number):
    phone_lookup = client.lookups \
                     .v1 \
                     .phone_numbers(f'{phone_number}') \
                     .fetch(type=['carrier'])
    return phone_lookup.carrier

# The Profile ID, Email and Phone Number will be collected next, to begin the validation process
# Profile ID will serve a unique identifier when storing the results from a lookup
# Email Address will be validated through Kickbox's Email Verification API
# Phone Number will be validated through Twilio's Lookup API
# profile_id = ''
email = ''
phone_number = ''

for profile in list_data:
    profile_id = profile.get('id')
    email = profile.get('email')
    phone_number = profile.get('phone_number')

    if phone_number != None:
        twilio_data = twilio_phone_lookup(phone_number)
        print(twilio_data)

    if email != None:
        kickbox_data = kickbox_verify_email(email)
        print(kickbox_data)
    



