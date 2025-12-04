import smtplib
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SENDER_EMAIL = "vaishnaviaghav1206@gmail.com"
SENDER_PASSWORD = "jhsshgfnviuoweut"
RECEIVER_EMAIL = "vaishaghav9175@gmail.com"

msg = MIMEText("This is a test email from your Fortify project.")
msg["Subject"] = "Email Test"
msg["From"] = SENDER_EMAIL
msg["To"] = RECEIVER_EMAIL

server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
server.starttls()
server.login(SENDER_EMAIL, SENDER_PASSWORD)
server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
server.quit()

print("Test email sent.")
