import requests
import os
from twilio.rest import Client
import sqlite3

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

# The Klaviyo List V2 API API will be leveraged to pull data on all members of a list
klaviyo_list_id = 'UwaMMy'

klaviyo_list_members_url = f'https://a.klaviyo.com/api/v2/group/{klaviyo_list_id}/members/all?api_key={klaviyo_private_api_key}'

headers = {"Accept": "application/json"}

response = requests.get(klaviyo_list_members_url, headers=headers)

response_dict = response.json()
list_data = response_dict['records']

# Then, database will be created to track results from List Scanning process
# Numbers already added to this database will be excluded from future list scans
connection = sqlite3.connect("scanned_profiles_database.db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS scanned_profiles('Profile ID' PRIMARY KEY, \
                                                            'Email Address', \
                                                            'Kickbox Result', \
                                                            'Sendex Score (Out of 1)', \
                                                            'Phone Number', \
                                                            'Number Carrier', \
                                                            'Number Type')")


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

# Create Profile Results payload
def get_profile_results(klaviyo_id, email, email_deliv_result, kickbox_score, phone, carrier, type ):
    profile_data = {
        'Profile ID': klaviyo_id,
        'Email': email,
        'Kickbox Result': email_deliv_result,
        'Sendex Score': kickbox_score,
        'Phone Number': phone,
        'Carrier Name': carrier,
        'Number Type': type
    }
    return profile_data

# Create function that will allow pushing the lookup results into a database



# The Profile ID, Email and Phone Number will be collected next, to begin the validation process
# Profile ID will serve a unique identifier when storing the results from a lookup
# Email Address will be validated through Kickbox's Email Verification API
# Phone Number will be validated through Twilio's Lookup API
profile_id = ''
email = ''
phone_number = ''

for profile in list_data:
    profile_id = profile.get('id')
    email = profile.get('email')
    phone_number = profile.get('phone_number')

    if phone_number != None:
        twilio_data = twilio_phone_lookup(phone_number)

    carrier_name = twilio_data['name']
    number_type = twilio_data['type']

    if email != None:
        kickbox_data = kickbox_verify_email(email)

    kickbox_result = kickbox_data['result']
    sendex_score = kickbox_data['sendex']

    # Create dictionary to store Profile Data for future use
    lookup_results = get_profile_results(profile_id, email, kickbox_result, sendex_score, phone_number, carrier_name, number_type)

    lookup_results_list = [profile_id, email, kickbox_result, sendex_score, phone_number, carrier_name, number_type]

    # Store and push Profile Lookup Data (Email + Phone) to 'scanned_profiles_database.db'
    cursor.execute(f"INSERT OR IGNORE INTO scanned_profiles VALUES ('{lookup_results_list[0]}', '{lookup_results_list[1]}', '{lookup_results_list[2]}', '{lookup_results_list[3]}', '{lookup_results_list[4]}', '{lookup_results_list[5]}', '{lookup_results_list[6]}')")


    # If an Email Address is not 'deliverable' according to kickbox, suppress in Klaviyo
    # If a Phone Number is not of the 'mobile' type, suppress in Klaviyo
    # Create custom metric indicating a profile was scanned, and what the results were https://developers.klaviyo.com/en/reference/track-post
    # Create a cron job that will run this script over and over
    # Check if a profile's email and/or phone is already in the 'scanned_profiles_database.db', 
    # If profile email/phone not previously scanned, initiate scan and update database 

connection.commit()
connection.close()