# -*- coding: utf-8 -*-
"""
Created on Tue Aug 12 14:37:17 2025

@author: koshy
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import undetected_chromedriver as uc
from selenium.common.exceptions import ElementNotInteractableException, TimeoutException
from bs4 import BeautifulSoup
import os
import json
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

SENDER_EMAIL = "joshuavkoshy@gmail.com"
RECIPIENT_EMAIL = "joshuavkoshy@gmail.com"

competencies = [
    "testing", "dependency injection", "api", "ci/cd", "devops", "agile", "backend", "cloud"
]

programming_languages = [
    "c#", ".net", "java", "python", "c++", "html", "css", "bootstrap",
    "javascript", "vue", "react", "node", "sql"
]

technologies = [
    "azure", "terraform", "artifactory", "git", "github",
    "cosmosdb", "postgresql", "mysql", "sqlite", "microsoft office", "flask"
]

subject = "Job Alert"
content = """
<html>
<body>
"""

def authenticate_gmail():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES
    )
    creds = flow.run_local_server(port=0)
    return creds

def write_email(score, title, company, location_agency, job_link, relevant_competencies, relevant_languages, relevant_technologies):
    global content

    # Score-based colors
    if score >= 40:
        score_color = "#28a745"  # green
        score_bg = "#d4edda"
    elif score >= 25:
        score_color = "#856404"  # gold text
        score_bg = "#fff3cd"
    else:
        score_color = "#721c24"  # red text
        score_bg = "#f8d7da"

    content += f"""
    <div style="border:1px solid #ccc; border-radius:8px; padding:15px; margin:15px 0;
                box-shadow:0 2px 6px rgba(0,0,0,0.1); font-family:Arial, sans-serif;">
        <p style="margin:0; font-size:18px; font-weight:bold;">
            <a href="{job_link}" target="_blank" style="text-decoration:none; color:#007bff;">
                {title}
            </a>
        </p>
        <p style="margin:5px 0; font-style:italic;">{company}</p>
        <p style="margin:5px 0;">{location_agency}</p>

        <div style="display:inline-block; padding:5px 12px; border-radius:20px;
                    background-color:{score_bg}; color:{score_color}; font-weight:bold;
                    margin:8px 0;">
            Score: {score}
        </div>

        <p><strong>Relevant Competencies:</strong> {', '.join(relevant_competencies) if relevant_competencies else 'N/A'}</p>
        <p><strong>Relevant Languages:</strong> {', '.join(relevant_languages) if relevant_languages else 'N/A'}</p>
        <p><strong>Relevant Technologies:</strong> {', '.join(relevant_technologies) if relevant_technologies else 'N/A'}</p>
    </div>
    """

def close_email():
    global content
    content += """
<footer>
    <p>This alert was sent by The Job Whisperer.</p>
</footer>
</body>
</html>
"""

def send_email(creds):
   message = MIMEText(content, 'html')
   message['to'] = RECIPIENT_EMAIL
   message['from'] = SENDER_EMAIL
   message['subject'] = subject
   msg = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
   
   service = build('gmail', 'v1', credentials=creds)
   sent_message = service.users().messages().send(userId='me', body=msg).execute()
   print(f"Email sent! Message ID: {sent_message['id']}")
        
def score_job(description, company, location):
    relevant_competencies = []
    relevant_languages = []
    relevant_technologies = []
    score = 0
    desc_lower = description.lower()
    
    # Competencies
    for skill in competencies:
        if skill in desc_lower:
            score += 4
            relevant_competencies.append(skill)
    
    # Programming Languages
    for lang in programming_languages:
        if lang in desc_lower:
            score += 3
            relevant_languages.append(lang)
            
    print()
    
    # Technologies
    for tech in technologies:
        if tech in desc_lower:
            score += 3
            relevant_technologies.append(tech)
            
    # Location preference
    preferred_locations = ["coppell", "irving", "las colinas", "fort worth", "dallas", "plano", "frisco", "arlington", "richardson", "mckinney", "grapevine", "southlake", "westlake", "allen", "flower mound"]
    for loc in preferred_locations:
        if loc in desc_lower or loc in location.lower():
            score += 5
            break
        
    # Company preference
    preferred_companies = ["cisco", "microsoft", "google", "gm financial", "fidelity", "meta", "netflix", "goldman sachs", "toyota", "texas instruments", "apple", "samsung", "amazon", "capital one", "wells fargo", "chase", "nvidia", "raytheon", "oracle", "tesla", "lockheed", "verizon", "at&t", "ericsson", "dell", "state farm", "amd", "visa", "bank of america", "american express", "charles schwab", "citi", "pnc"]
    if any(comp.lower() in company.lower() for comp in preferred_companies):
        score += 5
    
    return score, relevant_competencies, relevant_languages, relevant_technologies

def main():
    driver = uc.Chrome()
    
    driver.get("https://www.google.com")
    
    time.sleep(1)
    
    search = driver.find_element(By.CLASS_NAME, "gLFyf")
    
    search.clear()
    search.send_keys("software engineering internships")
    search.send_keys(Keys.RETURN)
    
    driver.implicitly_wait(5)
    
    jobs_button = driver.find_element(By.LINK_TEXT, "Jobs")
    jobs_button.click()
    
    driver.implicitly_wait(5)
    
    jobs_seen = 0
    while (jobs_seen <= 50):
        jobs = driver.find_elements(By.CLASS_NAME, "GoEOPd")
        links = driver.find_elements(By.CLASS_NAME, "MQUd2b")
        
        for job, link in zip(jobs[jobs_seen:], links[jobs_seen:]):
            description_text = ""
            title = job.find_element(By.CSS_SELECTOR, ".tNxQIb.PUpOsf")
            company = job.find_element(By.CSS_SELECTOR, ".wHYlTd.MKCbgd.a3jPc")
            location_agency = job.find_element(By.CSS_SELECTOR, ".wHYlTd.FqK3wc.MKCbgd")
            print(title.text)
            print(company.text)
            print(location_agency.text)
            print()
            
            link.click()
            
            time.sleep(2)
            
            job_link = driver.current_url
            
            # After your Selenium driver has loaded the page
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            
            # Find all elements with the LevrW class
            highlights = soup.find_all(class_="LevrW")
            for highlight in highlights:
                description_text += highlight.get_text(strip=True)
            
            visible_description = soup.find("span", class_="hkXmid")
            description_text += visible_description.get_text(strip=True)
            invisible_description = soup.find("span", class_="us2QZb")
            description_text += invisible_description.get_text(strip=True)
            
            job_analysis = score_job(description_text, company.text, location_agency.text)
            
            score = job_analysis[0]
            relevant_competencies = job_analysis[1]
            relevant_languages = job_analysis[2]
            relevant_technologies = job_analysis[3]
            
            print("Competencies: " + str(relevant_competencies))
            print("Languages: " + str(relevant_languages))
            print("Technologies: " + str(relevant_technologies))
            print(score)
            print()
            
            if (score >= 25):
                write_email(score, title.text, company.text, location_agency.text, job_link, relevant_competencies, relevant_languages, relevant_technologies)
                
            
        jobs_seen += 10

    driver.quit()
    close_email()
    creds = authenticate_gmail()
    send_email(creds)
    
if __name__ == "__main__":
    main()
