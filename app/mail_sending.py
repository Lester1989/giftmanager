import resend
import os 
resend.api_key = os.environ.get('RESEND_API_KEY')

def send_test_email():
    response = resend.Emails.send({
        "from": os.environ.get('RESEND_DOMAIN'),
        "to": "l.ester@gmx.de",
        "subject": "Hello World",
        "html": "<p>Congrats on sending your <strong>first email</strong>!</p>",
        "text": "Congrats on sending your first email!",
    })
    return response

def send_registration_mail(to_mail:str,registration_id:str):
    response = resend.Emails.send({
        "from": os.environ.get('RESEND_DOMAIN'),
        "to": to_mail,
        "subject": "Confirm your registration",
        "html": f"<p>Congrats on sending your <strong>first email</strong>!</p>", # TODO: add link to confirm registration
        "text": "Congrats on sending your first email!", # TODO: add link to confirm registration
    })
    return response

def send_password_reset_mail(to_mail:str,user_id:str,reset_id:str):
    response = resend.Emails.send({
        "from": os.environ.get('RESEND_DOMAIN'),
        "to": to_mail,
        "subject": "Reset your password",
        "html": f"<p>Congrats on sending your <strong>first email</strong>!</p>", # TODO: add link to confirm registration
        "text": "Congrats on sending your first email!", # TODO: add link to confirm registration
    })
    return response
