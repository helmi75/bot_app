import smtplib


def send_mail(receiver, sub_account, bot_type, value, stack_trace):
    TO = receiver
    SUBJECT = f'[IMPORTANT] COCOBOT Error : {sub_account}'
    TEXT = f'Bot {bot_type}: {sub_account} got an error:\n{value}\n{stack_trace}'

    # Gmail Sign In
    gmail_sender = 'hadjsassiscompany@gmail.com'
    gmail_passwd = 'rxqdshdenijwilcv'

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(gmail_sender, gmail_passwd)

    BODY = '\r\n'.join(['To: %s' % TO,
                        'From: %s' % gmail_sender,
                        'Subject: %s' % SUBJECT,
                        '', TEXT])

    try:
        server.sendmail(gmail_sender, [TO], BODY)
        print('email sent')
    except:
        print('error sending mail')

    server.quit()
