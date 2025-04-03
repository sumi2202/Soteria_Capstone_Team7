import random
import requests
import yagmail
import logging

# Configure logging for standalone testing
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Used to check if the email is real and valid
def email_validation(email):
    try:
        response = requests.get(
            f"https://emailvalidation.abstractapi.com/v1/?api_key=aad2d070bffe40e79e97886c2470fcde&email={email}"
        )
        response.raise_for_status()
        output_log = response.json()

        # Valid if format is correct and it's not disposable
        return (
                output_log["is_valid_format"]["value"]
                and not output_log["is_disposable_email"]["value"]
        )

    except Exception as e:
        logger.error(f"[Email Validation] API call failed: {e}")
        return False


# Used to generate the code
def generate_code():
    return str(random.randint(100001, 999999))  # random 6-digit code


# Used to send the email with the code
def send_code(email, code):
    try:
        account = yagmail.SMTP("soteria.solutionsteam@gmail.com", "wlcp eymb hhyu pppw")
        email_subject = "Soteria - Your One Time Passcode Has Arrived!"
        email_body = f""" 
        Hello,

        Your 6 digit passcode is: <b>{code}</b>.

        Please refrain from sharing this code.

        Thank you for choosing Soteria.

        Thank you,
        Soteria Team

        <b><i>Securing the web, one test at a time.</i></b>
        """

        account.send(to=email, subject=email_subject, contents=email_body)
        logger.info(f"[Email] Code sent to {email}")

    except Exception as error:
        logger.error(f"[Email] Could not send: {error}")
        raise  # important to re-raise so the caller knows it failed


# ======= TEMPORARY TESTING CLI =======
if __name__ == '__main__':
    email_input = input("Enter email to send code: ")

    if email_validation(email_input):
        code = generate_code()
        try:
            send_code(email_input, code)
            user_code = input("Enter the 6-digit code you received: ")

            if user_code == code:
                print("✅ MFA Successful!")
            else:
                print("❌ Incorrect code.")
        except Exception as e:
            print(f"❌ Failed to send code: {e}")
    else:
        print("❌ Email not valid.")
