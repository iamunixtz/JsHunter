#!/usr/bin/env python3

import requests
import re
import argparse
import json
import signal
import sys
import os
from colorama import Fore, Style, init

# Initialize Colorama
init(autoreset=True)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner = r"""
     ____.         _______  .__            __        
    |    | ______  \      \ |__| ____     |__|____   
    |    |/  ___/  /   |   \|  |/    \    |  \__  \  
/\__|    |\___ \  /    |    \  |   |  \   |  |/ __ \_
\________/____  > \____|__  /__|___|  /\__|  (____  /
              \/          \/        \/\______|    \/ 
    """
    
    # Get the terminal width
    terminal_width = os.get_terminal_size().columns
    banner_lines = banner.strip().splitlines()

    # Print the banner with Instagram colors
    for i, line in enumerate(banner_lines):
        if i % 4 == 0:
            color = Fore.MAGENTA  # Purple
        elif i % 4 == 1:
            color = Fore.LIGHTMAGENTA_EX  # Pink
        elif i % 4 == 2:
            color = Fore.YELLOW  # Yellow
        else:
            color = Fore.LIGHTYELLOW_EX  # Orange
        print(color + line.center(terminal_width))

    quote = f"{Fore.CYAN}JSNinja - \"Hunting Bugs in JavaScript!\"{Style.RESET_ALL}"
    print(quote.center(terminal_width))

def extract_links_from_js(js_content):
    url_pattern = r'(https?://[^\s\'"<>]+)'
    return re.findall(url_pattern, js_content)

def extract_secrets(js_content):
    secret_patterns = {

    'General API Key': r'(?i)\bAPI\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'API Token': r'(?i)\bAPI\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'API Access Key': r'(?i)\bAPI\s*Access\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'API Secret': r'(?i)\bAPI\s*Secret\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'API Key (v1)': r'(?i)\bAPI\s*Key\s*\(v1\)\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'API Key (v2)': r'(?i)\bAPI\s*Key\s*\(v2\)\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'OAuth API Key': r'(?i)OAuth\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'OAuth Access Token': r'(?i)OAuth\s*Access\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'Bearer API Token': r'(?i)Bearer\s*API\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'API Key for Service': r'(?i)\bAPI\s*Key\s*for\s*Service\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'REST API Key': r'(?i)REST\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'API Access Token': r'(?i)\bAPI\s*Access\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'Public API Key': r'(?i)Public\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'Private API Key': r'(?i)Private\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'API Key (Secure)': r'(?i)API\s*Key\s*\(Secure\)\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'Custom API Key': r'(?i)Custom\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'API Authorization Key': r'(?i)API\s*Authorization\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'API Auth Key': r'(?i)API\s*Auth\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'API Access Credentials': r'(?i)API\s*Access\s*Credentials\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'API User Key': r'(?i)API\s*User\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'API Client Key': r'(?i)API\s*Client\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'API Service Key': r'(?i)API\s*Service\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'API Request Key': r'(?i)API\s*Request\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'API Authentication Token': r'(?i)API\s*Authentication\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'API Key (User)': r'(?i)API\s*Key\s*\(User\)\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'App API Key': r'(?i)App\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'API Gateway Key': r'(?i)API\s*Gateway\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'Webhook API Key': r'(?i)Webhook\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'API Key for Integration': r'(?i)API\s*Key\s*for\s*Integration\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'API Key for App': r'(?i)API\s*Key\s*for\s*App\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'API Key for Service (v2)': r'(?i)API\s*Key\s*for\s*Service\s*\(v2\)\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'Zoom API Key': r'(?i)Zoom\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Zoom OAuth Access Token': r'(?i)Zoom\s*OAuth\s*Access\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{40})[\'"]?',
    'Trello API Key': r'(?i)Trello\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Twilio API Key': r'(?i)Twilio\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Unity Analytics API Key': r'(?i)Unity\s*Analytics\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Vercel API Key': r'(?i)Vercel\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Wix API Key': r'(?i)Wix\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Xero API Key': r'(?i)Xero\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Yandex API Key': r'(?i)Yandex\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Zoho API Key': r'(?i)Zoho\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'AirTable API Key': r'(?i)AirTable\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Postmark API Key': r'(?i)Postmark\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Mailtrap API Key': r'(?i)Mailtrap\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Sendinblue API Key': r'(?i)Sendinblue\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'MongoDB Atlas API Key': r'(?i)MongoDB\s*Atlas\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Okta API Token': r'(?i)Okta\s*API\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Plaid API Key': r'(?i)Plaid\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Intercom API Key': r'(?i)Intercom\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Veeva Vault API Key': r'(?i)Veeva\s*Vault\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Freshservice API Key': r'(?i)Freshservice\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Freshchat API Key': r'(?i)Freshchat\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Kaltura API Key': r'(?i)Kaltura\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Pusher API Key': r'(?i)Pusher\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Sentry API Key': r'(?i)Sentry\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Segment API Key': r'(?i)Segment\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Twitch API Key': r'(?i)Twitch\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Mixpanel API Key': r'(?i)Mixpanel\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Shopify API Key': r'(?i)Shopify\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Twilio API SID': r'(?i)Twilio\s*AccountSID\s*[:=]?\s*[\'"]?([A-Za-z0-9]{34})[\'"]?',
    'Mailgun API Key': r'(?i)Mailgun\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Heroku API Token': r'(?i)Heroku\s*API\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'GitHub OAuth Token': r'(?i)GitHub\s*OAuth\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{36})[\'"]?',
    'GitHub SSH Key': r'(?i)GitHub\s*SSH\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9/+=]{40})[\'"]?',
    'Google API Key': r'(?i)Google\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{39})[\'"]?',
    'AWS Secret Access Key': r'(?i)AWS\s*Secret\s*Access\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9/+=]{40})[\'"]?',
    'Google Cloud API Key': r'(?i)Google\s*Cloud\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{39})[\'"]?',
    'Amazon Cognito Identity Pool Key': r'(?i)Amazon\s*Cognito\s*Identity\s*Pool\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Auth0 API Key': r'(?i)Auth0\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Xero OAuth Token': r'(?i)Xero\s*OAuth\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'DigitalOcean API Key': r'(?i)DigitalOcean\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Trello OAuth Token': r'(?i)Trello\s*OAuth\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{40})[\'"]?',
    'Mastodon API Key': r'(?i)Mastodon\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{40})[\'"]?',
    'Auth0 API Token': r'(?i)Auth0\s*API\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Strava API Key': r'(?i)Strava\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Braintree API Key': r'(?i)Braintree\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Vimeo API Key': r'(?i)Vimeo\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Wistia API Key': r'(?i)Wistia\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'ABTasty API Key': r'(?i)ABTasty\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32})[\'"]?',
    'Algolia API Key': r'(?i)Algolia\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Amplitude API Keys': r'(?i)Amplitude\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Asana Access Token': r'(?i)Asana\s*Access\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{30})[\'"]?',
    'AWS Access Key ID': r'(?i)AWS\s*Access\s*Key\s*ID\s*[:=]?\s*[\'"]?([AIAZ0-9]{20})[\'"]?',
    'AWS Secret Key': r'(?i)AWS\s*Secret\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9/+=]{40})[\'"]?',
    'Azure Application Insights APP ID': r'(?i)Azure\s*Application\s*Insights\s*APP\s*ID\s*[:=]?\s*[\'"]?([A-Za-z0-9\-]{36})[\'"]?',
    'Azure API Key': r'(?i)Azure\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{40})[\'"]?',
    'Bazaarvoice Passkey': r'(?i)Bazaarvoice\s*Passkey\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Bing Maps API Key': r'(?i)Bing\s*Maps\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Bit.ly Access Token': r'(?i)Bit\.ly\s*Access\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Branch.io Key': r'(?i)Branch\.io\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Branch.io Secret': r'(?i)Branch\.io\s*Secret\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'BrowserStack Access Key': r'(?i)BrowserStack\s*Access\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Buildkite Access Token': r'(?i)Buildkite\s*Access\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'ButterCMS API Key': r'(?i)ButterCMS\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32})[\'"]?',
    'Calendly API Key': r'(?i)Calendly\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Contentful Access Token': r'(?i)Contentful\s*Access\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'captchaKey': r'(?i)captchaKey\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
    'CircleCI Access Token': r'(?i)CircleCI\s*Access\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Cloudflare API Key': r'(?i)Cloudflare\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Cypress Record Key': r'(?i)Cypress\s*Record\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'DataDog API Key': r'(?i)DataDog\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Delighted API Key': r'(?i)Delighted\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Deviant Art Access Token': r'(?i)Deviant\s*Art\s*Access\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{40})[\'"]?',
    'Deviant Art Secret': r'(?i)Deviant\s*Art\s*Secret\s*[:=]?\s*[\'"]?([A-Za-z0-9]{40})[\'"]?',
    'Dropbox API Key': r'(?i)Dropbox\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Facebook Access Token': r'(?i)Facebook\s*Access\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Facebook AppSecret': r'(?i)Facebook\s*AppSecret\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Firebase API Key': r'(?i)Firebase\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{39})[\'"]?',
    'Firebase Cloud Messaging (FCM)': r'(?i)Firebase\s*Cloud\s*Messaging\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{40})[\'"]?',
    'FreshDesk API Key': r'(?i)FreshDesk\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Github Client ID': r'(?i)GitHub\s*Client\s*ID\s*[:=]?\s*[\'"]?([A-Za-z0-9]{20})[\'"]?',
    'Github Client Secret': r'(?i)GitHub\s*Client\s*Secret\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'GitHub Token': r'(?i)GitHub\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{36})[\'"]?',
    'GitHub Private SSH Key': r'(?i)GitHub\s*Private\s*SSH\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9/+=]{40})[\'"]?',
    'GitLab Personal Access Token': r'(?i)GitLab\s*Personal\s*Access\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'GitLab Runner Registration Token': r'(?i)GitLab\s*Runner\s*Registration\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Google Cloud Service Account Credentials': r'(?i)Google\s*Cloud\s*Service\s*Account\s*Credentials\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{39})[\'"]?',
    'Google Maps API Key': r'(?i)Google\s*Maps\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{39})[\'"]?',
    'Google Recaptcha Key': r'(?i)Google\s*Recaptcha\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9_-]{40})[\'"]?',
    'Grafana Access Token': r'(?i)Grafana\s*Access\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Help Scout OAUTH': r'(?i)Help\s*Scout\s*OAUTH\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Heroku API Key': r'(?i)Heroku\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'HubSpot API Key': r'(?i)HubSpot\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Infura API Key': r'(?i)Infura\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Instagram Access Token': r'(?i)Instagram\s*Access\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Instagram Basic Display API': r'(?i)Instagram\s*Basic\s*Display\s*API\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Instagram Graph API': r'(?i)Instagram\s*Graph\s*API\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Ipstack API Key': r'(?i)Ipstack\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Iterable API Key': r'(?i)Iterable\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'JumpCloud API Key': r'(?i)JumpCloud\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Keen.io API Key': r'(?i)Keen\.io\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'LinkedIn OAUTH': r'(?i)LinkedIn\s*OAUTH\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Lokalise API Key': r'(?i)Lokalise\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Loqate API Key': r'(?i)Loqate\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'MailChimp API Key': r'(?i)MailChimp\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'MailGun Private Key': r'(?i)MailGun\s*Private\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Mapbox API Key': r'(?i)Mapbox\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Microsoft Azure Tenant': r'(?i)Microsoft\s*Azure\s*Tenant\s*[:=]?\s*[\'"]?([A-Za-z0-9]{36})[\'"]?',
    'Microsoft SAS': r'(?i)Microsoft\s*Shared\s*Access\s*Signature\s*[:=]?\s*[\'"]?([A-Za-z0-9]{40})[\'"]?',
    'Microsoft Teams Webhook': r'(?i)Microsoft\s*Teams\s*Webhook\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'New Relic Personal API Key': r'(?i)New\s*Relic\s*Personal\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'New Relic REST API': r'(?i)New\s*Relic\s*REST\s*API\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'NPM token': r'(?i)NPM\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{36})[\'"]?',
    'OpsGenie API Key': r'(?i)OpsGenie\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'PagerDuty API token': r'(?i)PagerDuty\s*API\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Paypal client id': r'(?i)Paypal\s*Client\s*ID\s*[:=]?\s*[\'"]?([A-Za-z0-9]{30})[\'"]?',
    'Paypal client secret key': r'(?i)Paypal\s*Client\s*Secret\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Pendo Integration Key': r'(?i)Pendo\s*Integration\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'PivotalTracker API Token': r'(?i)PivotalTracker\s*API\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Razorpay API Key': r'(?i)Razorpay\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Razorpay API Secret Key': r'(?i)Razorpay\s*API\s*Secret\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Salesforce API Key': r'(?i)Salesforce\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'SauceLabs Access Key': r'(?i)SauceLabs\s*Username\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'SendGrid API Token': r'(?i)SendGrid\s*API\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Shodan API Key': r'(?i)Shodan\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Slack API Token': r'(?i)Slack\s*API\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Slack Webhook': r'(?i)Slack\s*Webhook\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Sonarcloud API Key': r'(?i)Sonarcloud\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Spotify Access Token': r'(?i)Spotify\s*Access\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Square API Key': r'(?i)Square\s*API\s*Key\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Stripe Live Token': r'(?i)Stripe\s*Live\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Telegram Bot API Token': r'(?i)Telegram\s*Bot\s*API\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Travis CI API token': r'(?i)Travis\s*CI\s*API\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Twilio Account SID': r'(?i)Twilio\s*Account\s*SID\s*[:=]?\s*[\'"]?([A-Za-z0-9]{34})[\'"]?',
    'Twilio Auth Token': r'(?i)Twilio\s*Auth\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Twitter API Secret': r'(?i)Twitter\s*API\s*Secret\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Twitter Bearer Token': r'(?i)Twitter\s*Bearer\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    'Visual Studio App Center API Token': r'(?i)Visual\s*Studio\s*App\s*Center\s*API\s*Token\s*[:=]?\s*[\'"]?([A-Za-z0-9]{32})[\'"]?',
    }

    found_secrets = {}
    for key, pattern in secret_patterns.items():
        matches = re.findall(pattern, js_content)
        if matches:
            unique_matches = list(set(matches))
            found_secrets[key] = unique_matches

    # Add pattern for object notation
    object_pattern = r'(?i)const\s+[A-Z_]+_KEYS\s*=\s*\{([^}]+)\}'
    object_matches = re.findall(object_pattern, js_content)
    
    for match in object_matches:
        for line in match.split(','):
            line = line.strip()
            for key in secret_patterns.keys():
                if key.lower().replace(' ', '_') in line.lower():
                    value = re.search(r'\:\s*[\'"]?([^\'", ]+)[\'"]?', line)
                    if value:
                        found_secrets[key] = found_secrets.get(key, []) + [value.group(1)]

    return found_secrets


def signal_handler(sig, frame):
    choice = input(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Do you want to close JSNinja? (Y/N): ").strip().lower()
    if choice == 'y':
        print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} Closing JSNinja...")
        sys.exit(0)
    else:
        print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} Continuing execution...")

def main(input_file, output_file, look_for_secrets, look_for_urls, single_url):
    clear_screen()
    print_banner()

    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

    js_links = []
    if single_url:
        js_links.append(single_url)
    else:
        with open(input_file, 'r') as file:
            js_links = file.readlines()

    extracted_links = []
    all_secrets = {}

    for js_link in js_links:
        js_link = js_link.strip()
        if not js_link:
            continue
        
        try:
            response = requests.get(js_link, verify=False)
            response.raise_for_status()

            if look_for_urls:
                links = extract_links_from_js(response.text)
                extracted_links.extend(links)
                print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} {Fore.YELLOW}Extracted {len(links)} links from {js_link}{Style.RESET_ALL}")

                for link in links:
                    print(f"{Fore.GREEN}[+] {link}{Style.RESET_ALL}")
                if not links:
                    print(f"{Fore.RED}[INFO]{Style.RESET_ALL} {Fore.YELLOW}No URLs found in {js_link}{Style.RESET_ALL}")

            if look_for_secrets:
                secrets = extract_secrets(response.text)
                if secrets:
                    all_secrets[js_link] = secrets
                    print(f"{Fore.GREEN}[+] Secrets found in {js_link}: {json.dumps(secrets, indent=2)}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}[INFO]{Style.RESET_ALL} {Fore.YELLOW}No secrets found in {js_link}{Style.RESET_ALL}")

        except requests.exceptions.SSLError as ssl_err:
            print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} SSL error while fetching {js_link}: {str(ssl_err)}")
        except requests.RequestException as e:
            print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Failed to fetch {js_link}: {str(e)}")

    if extracted_links and look_for_urls:
        with open(output_file, 'w') as out_file:
            for link in extracted_links:
                out_file.write(link + '\n')
        print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} {Fore.YELLOW}Links saved to {output_file}{Style.RESET_ALL}")

    if all_secrets and look_for_secrets:
        secrets_output_file = output_file.replace('.txt', '_secrets.json')
        with open(secrets_output_file, 'w') as secrets_file:
            json.dump(all_secrets, secrets_file, indent=2)
        print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} {Fore.YELLOW}Secrets saved to {secrets_output_file}{Style.RESET_ALL}")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTSTP, signal_handler)

    parser = argparse.ArgumentParser(description='Extract links and secrets from JavaScript files.')
    parser.add_argument('input_file', nargs='?', help='File containing JavaScript links')
    parser.add_argument('-o', '--output_file', default='extracted_links.txt', help='File to save extracted links')
    parser.add_argument('-u', '--url', help='Single JavaScript URL to fetch')
    parser.add_argument('--secrets', action='store_true', help='Look for secrets in JavaScript content')
    parser.add_argument('--urls', action='store_true', help='Extract URLs from JavaScript content')
    args = parser.parse_args()

    if args.url and args.input_file:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Please provide either an input file or a single URL, not both.")
        sys.exit(1)

    main(args.input_file, args.output_file, args.secrets, args.urls, args.url)
