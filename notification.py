import smtplib
from email.mime.text import MIMEText
from preferences import CREDENTIALS, COMMUTES
from helper import commute_time


def _send_(sender_name: str, subject: str, content: str):
    """
    Dummy send
    :param sender_name: name that will appear in address line
    :param subject: subject of E-Mail
    :param content: content of E-Mail
    """
    print('====')
    print(sender_name)
    print(subject)
    print(content)
    print('====')


def _send(sender_name: str, subject: str, content: str):
    """
    Send an E-mail
    :param sender_name: name that will appear in address line
    :param subject: subject of E-Mail
    :param content: content of E-Mail
    """
    sender = CREDENTIALS['mail']['address']
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = '{} <{}>'.format(sender_name, sender)
    msg['To'] = sender

    client = smtplib.SMTP(CREDENTIALS['mail']['server'])
    client.ehlo()
    client.starttls() # will connect to any certificate (might be fake)
    client.ehlo()
    client.login(sender, CREDENTIALS['mail']['pass'])
    client.send_message(msg)
    client.quit()


def notify_dev(subject, error_msg):
    """
    Send E-Mail to dev about an error
    :param subject: Subject of error
    :param error_msg: a string of errors
    """
    _send('Apartment Error', subject, error_msg)


def notify_about_home(home):
    """
    Send E-Mail
    :param home:
    """
    commutes = ["{}' {}".format(commute_time(home.address, addr), name)
                for name, addr in COMMUTES.items()]

    text = 'Address: {addr}\n' \
           'Rent: {rent}€\n' \
           'Area: {area}m²\n' \
           'Commute: {comms}\n' \
           'Rooms: {rooms}\n\n' \
           .format(addr=home.address, rent=home.rent, area=home.area,
                   rooms=home.rooms, comms=', '.join(commutes)) \
           + home.url

    _send('New Apartment', home.name, text)


