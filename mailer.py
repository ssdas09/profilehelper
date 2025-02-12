import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Gmail credentials
# GMAIL_USER = "your_email@gmail.com"
# GMAIL_PASSWORD = "your_password"  # Use App Password if 2FA is enabled
#
# # Email details
# TO_EMAIL = "recipient@example.com"
# SUBJECT = "Invoice Report - PDF Attachment"
# BODY = "Hello,\n\nPlease find the attached PDF file.\n\nBest regards."

# PDF file to attach


def send_email(gmail_user,to_email,subject,body,password,PDF_PATH):
    msg = MIMEMultipart()
    msg["From"] = gmail_user
    msg["To"] = to_email
    msg["Subject"] = subject

    # Attach the email body
    msg.attach(MIMEText(body, "plain"))

    # Attach PDF file
    if os.path.exists(PDF_PATH):
        with open(PDF_PATH, "rb") as attachment:
            part = MIMEBase("application", "pdf")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(PDF_PATH)}"')
        msg.attach(part)
    else:
        print(f"File {PDF_PATH} not found!")

    # Send email via Gmail SMTP
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Secure the connection
            server.login(gmail_user, password)
            server.sendmail(gmail_user, to_email, msg.as_string())
        print("Email sent successfully with PDF attachment!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    send_email()
