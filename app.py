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
def get_profile_results(klaviyo_id, email, email_deliv_result, kickbox_score, phone, carrier, type):
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


# Create function that will suppress undeliverable email addresses in Klaviyo
def suppress_email_address(email):
    klaviyo_suppression_list_url = f'https://a.klaviyo.com/api/v1/people/exclusions?api_key={klaviyo_private_api_key}'

    payload = {'email': f'{email}'}
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
        }

    response = requests.post(klaviyo_suppression_list_url, data=payload, headers=headers)
    return response

# Create a function to suppress phone numbers that are not of the 'mobile' type
def suppress_phone_number(phone):
    url = f'https://a.klaviyo.com/api/v2/list/{klaviyo_list_id}/subscribe?api_key={klaviyo_private_api_key}'

    payload = {'profiles': [
            {
                'phone_number': f'{phone}',
                "sms_consent": False
            }
        ]}
    headers = {"Accept": "application/json",
               "Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    return response

# Next, leverage Klaviyo's Track API to create an event in-app to track profiles that have been scanned
def track_scanned_profile_event(event, customer_properties, properties):
    url = "https://a.klaviyo.com/api/track"

    payload = {
        'token': f'{klaviyo_public_api_key}',
        'event': event,
        'customer_properties': customer_properties,
        'properties': properties
    }

    print(f"'Track Event Payload': {payload}")
    headers = {"Accept": "text/html",
               "Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(url, json=payload)
    print(response.text)
    print(response.status_code)
    return response

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

    # Non existing phone numbers will be skipped as they will return an error from Twilio
    if phone_number != 'None':
        twilio_data = twilio_phone_lookup(phone_number)

    carrier_name = twilio_data['name']
    number_type = twilio_data['type']

    # For phone-only profiles, email address will be skipped from the Kickbox Verify process
    if email != 'None':
        kickbox_data = kickbox_verify_email(email)

    kickbox_result = kickbox_data['result']
    sendex_score = kickbox_data['sendex']

    # Create dictionary to store Profile Data for future use
    lookup_results = get_profile_results(profile_id, email, kickbox_result, sendex_score, phone_number, carrier_name, number_type)

    # List elements to be passed to SQLite database as rows
    lookup_results_list = [profile_id, \
                           email, \
                           kickbox_result, \
                           sendex_score, \
                           phone_number, \
                           carrier_name, \
                           number_type]

    # Store and push Profile Lookup Data (Email + Phone) to 'scanned_profiles_database.db'
    cursor.execute(f"INSERT OR IGNORE INTO scanned_profiles VALUES ('{lookup_results_list[0]}', \
                                                                    '{lookup_results_list[1]}', \
                                                                    '{lookup_results_list[2]}', \
                                                                    '{lookup_results_list[3]}', \
                                                                    '{lookup_results_list[4]}', \
                                                                    '{lookup_results_list[5]}', \
                                                                    '{lookup_results_list[6]}')")


    # If an Email Address is not 'deliverable' according to kickbox, suppress in Klaviyo
    email_deliverability_probability = lookup_results.get('Kickbox Result')

    # Possible values are `deliverable`, `non-deliverable`, `risky` and `Unknown`
    # Kickbox recommends sending a DOI email to email addresses that come up as `Unknown`,
    # However, for the sake of this exercise, they will also be suppressed
    if email_deliverability_probability != 'deliverable':
        # suppress email address in Klaviyo
        suppress_email_address(email)

        print(f'[{profile_id}] {email} has a Kickbox Sendex Score of {sendex_score}/1 - deliverability probability: {email_deliverability_probability}')

    # If a Phone Number is present on the profile, or the phone number is not of the 'mobile' type, suppress in Klaviyo.
    # Possible values for `Number Type` are `Mobile`, `Landline` and `VOIP`, and some VOIP lines are able to receive SMS,
    # However, given how inconsistent deliveries can be, and for the sake of this exercise, they will be supppresssed for SMS.
    if phone_number != 'None' and number_type != 'mobile':
        # suppress phone number in Klaviyo
        suppress_phone_number(phone_number)

        print(f'[{profile_id}] {phone_number} is of the {number_type} type and is suppressed from SMS')

    # Setting up customer_properties for Track Request
    customer_properties = {'$email': f'{email}', 
                           '$phone_number': f'{phone_number}'}

    
    print(' ') # extra line for logging purposes

    # Setting up event properties for Track Request
    properties = lookup_results

    # Create custom 'Scanned Profile' metric for each profile from List
    track_scanned_profile_event('Scanned Profile', customer_properties, properties)

# Close SQLite session
connection.commit()
connection.close()
