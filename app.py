import requests
import os
import kickbox
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()

klaviyo_public_api_key = 'Qg3FLb'

klaviyo_private_api_key = os.getenv('KLAVIYO_PRIVATE_API_KEY')

kickbox_api_key = os.getenv('KICKBOX_API_KEY')

twilio_api_key = os.getenv('TWILIO_API_KEY')


# First, the Klaviyo List V2 API API will be leveraged to pull data on all members of a list
klaviyo_list_id = 'UwaMMy'

klaviyo_list_url = f'https://a.klaviyo.com/api/v2/group/{klaviyo_list_id}/members/all?api_key={klaviyo_private_api_key}'
print(klaviyo_list_url)

headers = {"Accept": "application/json"}

response = requests.get(klaviyo_list_url, headers=headers)

response_dict = response.json()
list_data = response_dict['records']


# The Profile ID, Email and Phone Number will be collected next, to begin the validation process
# Profile ID will serve a unique identifier when storing the results from a lookup
# Email Address will be validated through Kickbox's Email Validation API
# Phone Number will be validate through Twilio's API

profile_id = ''
email = ''
phone_number = ''


for profile in list_data:
    profile_id = profile.get('id')
    email = profile.get('email')
    phone_number = profile.get('phone_number')

    print(profile_id)
