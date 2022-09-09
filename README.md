# List Scanner 
##### Klaviyo SA Tech Assessment

In this challenge, the goal is to create a integration using Twilio's Lookup API and Kickbox's Email Verification API, to periodically validate any list's Email and Phone Number data. While Double Opt-in is a best practice in the List Collection domain, it is not always an option customers are looking to consider as part of their subscriber collection strategy. For this reason, I see some benefits in this potential fallback, as it allows a user to validate profile data on the back-end, with little impact to the user experience.

#### Visual Representation of this solution
![List Scann](https://user-images.githubusercontent.com/84048784/189366623-5314108f-4675-4113-bd0c-338bd4c98f05.jpg)

#### This solution will:
- Pull Profile data from a specific Klaviyo List
- Pull Email and Phone Number from Profile
- Run Email Address through the Kickbox Email Verification API
- If Email is not marked as `deliverable` by Kickbox, add to Klaviyo's Suppression List
- Else, do nothing
- Run Phone Number through Twilio's Lookup API
- If Phone Number type is not `mobile`, according to Twilio, suppress number for SMS
- Else, do nothing
- Add Email and Phone Number results to database of previously scanned profiles
- Track event in Klaviyo, based on lookup results

###### Klaviyo Account ID Used for Testing: `Qg3FLb`
###### List ID Used for Testing: `UwaMMy`

To test functionality of this solution, add new profiles into `SA Tech Assessment List`, and include both `Email` and `Phone Number`. Another way to test this tool is to add these examples into the CSV file located in `csv_file` folder, and uploading file to `SA Tech Assessment List`.

When adding a phone number to a Klaviyo profile, make sure the country code is present `(+1617 xxx-xxxx)`. For more context, visit https://help.klaviyo.com/hc/en-us/articles/360046055671-Accepted-phone-number-formats-for-SMS-in-Klaviyo.  

### Install and Setup Instructions

1. Fork and Clone this repository into your local machine. Otherwise, download Zip folder into local machine.

2. Create a Twilio account on https://twilio.com, and retrieve the `Account SID` and `Auth Token`. 

3. Create a Kickbox account on https://kickbox.com, and generate an API key in `Production Mode`. 

4. Generate a `Private API key` in Klaviyo https://www.klaviyo.com/account#api-keys-tab. It will be used to access and update list data using the List V2      API. Additionally, use `Public API key` for `Track` requests.

5. Download Twilio's helper library from https://www.twilio.com/docs/python/install and run:
   ```
   pip3 install twilio
   ```
6. Download `python-dotenv` library on https://pypi.org/project/python-dotenv. `.env` file will be used to hide sensitive data such as private keys.
   ```
   pip3 install python-dotenv
   ```
7. You can now run the script, by using the following command in your Terminal:
   ```
   python3 app.py
   ```

#### Future State
Future iterations of this tool would allow the end user to check if a specific data point, `Email` or `Phone`, has already been scanned. Additionally, it would be possible to retrieve this information from the existing database of previously scanned profiles and take action accordingly (i.e. suppress). Lookups can be costly if there aren't mechanisms in place that would prevent the script from running repeatedly for the same email and phone number.

Additionally, with more time, I would also host this script on the cloud, perhaps on `Heroku`(https://www.heroku.com) or `PythonAnywhere`(https://www.pythonanywhere.com). That way, I could set up a scheduler that would run this script once every hour. 



   
