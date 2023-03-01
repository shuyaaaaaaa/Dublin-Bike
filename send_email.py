import smtplib

def email_error(error):
    # Set up the SMTP server and login email account
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    username = 'dagg.george@gmail.com'
    password = 'zhxtastjtfrbmbwq'
    #try connect to smtp server and login
    try:
        smtp_conn = smtplib.SMTP(smtp_server, smtp_port)
        smtp_conn.starttls()
        smtp_conn.login(username, password)
    except Exception as e:
        print(f'Error connecting to server: {str(e)}')
        exit()

    # Compose the email message
    from_address = 'dagg.george@gmail.com'
    to_address = ['george.dagg@ucdconnect.ie', 'cian.belton@ucdconnect.ie', 'shuya.ikeo@ucdconnect.ie']
    subject = 'ERROR - Requires Attention'
    body = 'The following error has been detected:', error
    message = f'Subject: {subject}\n\n{body}'

    try:
    # Send the email
        smtp_conn.sendmail(from_address, to_address, message)
        print('Email sent successfully')
    except Exception as e:
        print(f'Error sending email: {str(e)}')

    # Close the SMTP connection
    finally:
        smtp_conn.quit()
