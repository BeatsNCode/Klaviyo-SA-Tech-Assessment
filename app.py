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


# First, the Klaviyo List V2 API API will be leveraged to pull profile data, specifically `Email` and `Phone Number`
klaviyo_list_id = 'UwaMMy'

klaviyo_list_url = f'https://a.klaviyo.com/api/v2/group/{klaviyo_list_id}/members/all?api_key={klaviyo_private_api_key}'

headers = {"Accept": "application/json"}

response = requests.get(klaviyo_list_url, headers=headers)

list_data = response.text
print(list_data)