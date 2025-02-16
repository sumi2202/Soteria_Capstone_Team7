import random #for generating the code
import requests #accessing Abstract API
import yagmail #sending emails

#Used to check if the email is real and valid
def email_validation(email):

    #Accessing Abstract API
    response = requests.get(f"https://emailvalidation.abstractapi.com/v1/?api_key=aad2d070bffe40e79e97886c2470fcde&email={email}")

    output_log = response.json()

    #Checking for valid email
    if output_log["is_valid_format"]["value"] and not output_log["is_disposable_email"]["value"]:
        return True
    else:
        return False


#Used to generate the code
def generate_code():
    return str(random.randint(100001, 999999)) #returning a random 6 digit integer


#Used to send the email with the code
def send_code(email, code):

    try:
        account = yagmail.SMTP("soteria.solutionsteam@gmail.com", "wlcp eymb hhyu pppw")
        email_subject = "Soteria - Your One Time Passcode Has Arrived!" #Subject Line of Email

        # Body of Email
        email_body = f""" 
        Hello,
        
        Your 6 digit passcode is: <b>{code}</b>.
        
        Please refrain from sharing this code.
        
        Thank you for choosing Soteria.
        
        Thank you,
        Soteria Team
        
        <b><i>Securing the web, one test at a time.</i></b>
        """

        #Sending the email
        account.send(to=email, subject=email_subject, contents=email_body)

    except Exception as error:
        print(f"Could not send: {error}")



# ** DELETE THIS AFTER FRONTEND IS DONE **
#Main Functions for Testing Purposes
if __name__ == '__main__':
    email_input= input("Please enter your email to send the code: ")

    if email_validation(email_input):
        code = generate_code()
        send_code(email_input, code)

        user_code = input("Please enter the 6 digit passcode: ")

        if user_code == code:
            print("MFA is Successful!")
        else:
            print("Incorrect code!")


    else:
        print("Email not valid.")




