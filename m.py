import streamlit as st
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# NASA API key and URL
DEMO_KEY = '4RwLGLr48zNXNEtqmqeaUhL6AR6mYnjuXUCJ2ulm'
url = 'https://api.nasa.gov/planetary/apod'

# Streamlit UI
st.title("NASA Astronomy Picture of the Day")
date = st.date_input("Select a date", value=None)
email_option = st.radio("Do you want this APOD to be sent to your email?", ("Yes", "No"))

if date:
    params = {
        'date': date.strftime('%Y-%m-%d'),
        'api_key': DEMO_KEY,
        'thumbs': 'True',
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        json_data = response.json()
        st.write(json_data)

        image_url = json_data.get('url')
        image_data = requests.get(image_url).content

        st.image(image_url, caption=json_data.get('title'))

        with open("apod_date.jpg", 'wb') as f:
            f.write(image_data)
        st.write("Image saved as apod_date.jpg")

        if email_option == "Yes":
            email = st.text_input("Sender Email")
            password = st.text_input("Email Password", type="password")
            receiver = st.text_input("Receiver Email")
            subject = st.text_input("Subject")

            if st.button("Send Email"):
                try:
                    # Create the email
                    msg = MIMEMultipart()
                    msg['From'] = email
                    msg['To'] = receiver
                    msg['Subject'] = subject

                    body = json_data.get('explanation')
                    msg.attach(MIMEText(body, 'plain'))

                    # Attach the image
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(image_data)
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f"attachment; filename=apod_date.jpg")
                    msg.attach(part)

                    # Send the email
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(email, password)
                    text = msg.as_string()
                    server.sendmail(email, receiver, text)
                    server.quit()

                    st.success("Email has been sent to " + receiver)
                except Exception as e:
                    st.error("Error: Failed to send email. " + str(e))
    else:
        st.error("Error: Failed to fetch data from NASA APOD API.")
