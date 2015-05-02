# Import smtplib for the actual sending function
import smtplib
# Import the email modules we'll need
from email.mime.text import MIMEText
import os

# do stuff


def run(modulename=''):
    send = content(modulename)
    # print send
    # usage(send)
    # send_email(send)
    # usage(send)


def usage(send=''):
    # Open a plain text file for reading.  For this example, assume that
    # the text file contains only ASCII characters.
    # textfile = '/home/sebastianw/Desktop/b.txt'
    # fp = open(textfile, 'rb')
    # Create a text/plain message
    # msg = MIMEText(fp.read())
    msg = MIMEText(send)
    # fp.close()

    # me == the sender's email address
    # you == the recipient's email address
    me = 'weber.seb@gmail.com'
    you = 'sebastianweber@live.com'
    # msg['Subject'] = 'webr_bot %s' % textfile
    msg['Subject'] = send
    msg['From'] = me
    msg['To'] = you

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    # s = smtplib.SMTP('localhost')
    # s.sendmail(me, [you], msg.as_string())
    # s.quit()


def content(modulename):
    user = os.getenv('USER')
    return modulename + ' -- ' + user


def send_email(send=''):

    gmail_user = "weber.seb@gmail.com"
    gmail_pwd = "t0m@h@wk"
    FROM = 'weber.seb@gmail.com'
    TO = ['sebastianweber@live.com']  # must be a list
    SUBJECT = send
    TEXT = send

    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
            """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        # server = smtplib.SMTP(SERVER)
        server = smtplib.SMTP("smtp.gmail.com", 587)  # or port 465 doesn't seem to work!
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        # server.quit()
        server.close()
        print 'successfully sent the mail'
    except:
        print "failed to send mail"


# send_email()
