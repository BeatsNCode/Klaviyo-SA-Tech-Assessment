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



