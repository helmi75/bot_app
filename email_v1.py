# smtplib module send mail

import smtplib
"""
TO = 'helmichiha@gmail.com'
SUBJECT = 'TEST MAIL'
TEXT = 'Here is a message from python.'

# Gmail Sign In
gmail_sender = 'aitmoummad.anisse@gmail.com'
gmail_passwd = 'syyllodqlltlvtht'

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
    print ('email sent')
except:
    print ('error sending mail')

server.quit()

"""

def send_mail(sub_acount, pair_symbol, exeption_type, ex_value, stack_trace):
    TO = 'aitmoummad.anisse@gmail.com'
    SUBJECT = f'Error sub account : {sub_acount}'
    TEXT = f'\nsubaccout problem : {sub_acount}\nPair_symbol problem : {pair_symbol}\nException type : {exeption_type}\nException message : {ex_value}\nStack trace : {stack_trace} '
    
    
    # Gmail Sign In 
    gmail_sender = 'aitmoummad.anisse@gmail.com' 
    gmail_passwd = 'syyllodqlltlvtht'

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
        print ('email sent')
    except:
        print ('error sending mail')

    server.quit()


