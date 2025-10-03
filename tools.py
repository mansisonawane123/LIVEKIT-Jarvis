import logging
from livekit.agents import function_tool, RunContext
import requests
from langchain_community.tools import DuckDuckGoSearchRun
import os
import smtplib
from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText
from typing import Optional

# ----------------------------------------------------------------------
# WEATHER TOOL
# ----------------------------------------------------------------------
@function_tool()
async def get_weather(
    context: RunContext,  
    city: str
) -> str:
    """
    Get the current weather for a given city.
    """
    try:
        response = requests.get(
            f"https://wttr.in/{city}?format=3",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            timeout=15
        )
        if response.status_code == 200:
            logging.info(f"Weather for {city}: {response.text.strip()}")
            return response.text.strip()   
        else:
            logging.error(f"Failed to get weather for {city}: {response.status_code}")
            return f"Could not retrieve weather for {city}."
    except Exception as e:
        logging.error(f"Error retrieving weather for {city}: {e}")
        return f"An error occurred while retrieving weather for {city}." 

# ----------------------------------------------------------------------
# SEARCH TOOL
# ----------------------------------------------------------------------
@function_tool()
async def search_web(
    context: RunContext,  
    query: str
) -> str:
    """
    Search the web using DuckDuckGo.
    """
    try:
        results = DuckDuckGoSearchRun().run(tool_input=query)
        logging.info(f"Search results for '{query}': {results}")
        return results
    except Exception as e:
        logging.error(f"Error searching the web for '{query}': {e}")
        return f"An error occurred while searching the web for '{query}'."    

# ----------------------------------------------------------------------
# EMAIL HELPER  
# ----------------------------------------------------------------------
def _send_single_email(recipient: str, subject: str, body: str, cc_email: Optional[str] = None) -> None:
    """
    Helper function to send a single email via SMTP SSL.
    """
    try:
        smtp_server = "smtp.stackmail.com"
        smtp_port = 465  # SSL port
        smtp_user = "info@wealtfly.com"
        smtp_password = "syCvK^jX:pu0"   #  Better to load from env vars

        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = recipient
        msg["Subject"] = subject

        recipients = [recipient]
        if cc_email:
            msg["Cc"] = cc_email
            recipients.append(cc_email)

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, recipients, msg.as_string())

        logging.info(f"Email successfully sent to {recipient}.")
    except Exception as e:
        logging.error(f"Failed to send email to {recipient}: {e}")
        raise e

# ----------------------------------------------------------------------
# EMAIL TOOL
# ----------------------------------------------------------------------
@function_tool()    
async def send_email(
    context: RunContext,  
    to_email: str,
    subject: str,
    message: str,
    cc_email: Optional[str] = None
) -> str:
    """
    Send an email through Stackmail (info@wealtfly.com).
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        message: Email body content
        cc_email: Optional CC email address
    """
    try:
        _send_single_email(to_email, subject, message, cc_email)
        return f"Email sent successfully to {to_email}"
    except smtplib.SMTPAuthenticationError:
        logging.error("SMTP authentication failed")
        return "Email sending failed: Authentication error. Please check your SMTP credentials."
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")
        return f"Email sending failed: SMTP error - {str(e)}"
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return f"An error occurred while sending email: {str(e)}"