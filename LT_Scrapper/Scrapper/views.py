from concurrent.futures import ThreadPoolExecutor
from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib import messages
import openai
import json
import requests
import os

# for scrappers
from linkedin_api import Linkedin

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

import undetected_chromedriver as uc

from selenium_stealth import stealth
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from time import sleep
from bs4 import BeautifulSoup


def signin():
    # Call the sign-in API to obtain the access token
    signin_api_url = 'https://raiderly-backend-467cbb45badd.herokuapp.com/api/auth/signin'
    signin_data = {
        "email": "user@raiderly.com",
        "password": "12345678"
    }

    signin_response = requests.post(signin_api_url, json=signin_data)

    if signin_response.status_code == 200:
        access_token = signin_response.json().get('data', {}).get('accessToken')
        return access_token


def fetch_linkedin(linkedin):
    linkedin_user = linkedin
    # api = Linkedin("alphaprogramming55@gmail.com", "zachaudhary1122")
    api = Linkedin(os.environ['LINKEDIN_EMAIL'], os.environ['LINKEDIN_PASSWORD'])
    posts = api.get_profile_posts(linkedin_user)
    num_posts = 2
    content_texts = []
    for i in range(num_posts):
        post = posts[i]
        commentary_element = post['commentary']
        text_content = commentary_element['text']['text']
        content_texts.append(text_content)
    concatenated_text = '\n'.join(content_texts)

    return concatenated_text
    

def fetch_twitter(twitter):
    twitter_user = twitter
    
    chrome_options = uc.ChromeOptions()
    # Add headless argument here
    chrome_options.add_argument('--headless')  # This line enables headless mode

    # Rest of your existing options
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    
    sleep(3)
    driver.get("https://twitter.com/i/flow/login")
    sleep(5)
    username = driver.find_element(By.XPATH,"//input[@name='text']")
    username.send_keys("alphaprogramming55@gmail.com")
    next_button = driver.find_element(By.XPATH,"//span[contains(text(),'Next')]")
    next_button.click()
    # sleep(5)
    # password = driver.find_element(By.XPATH,"//input[@name='password']")
    # password.send_keys('iklmermu15772900')
    # log_in = driver.find_element(By.XPATH,"//span[contains(text(),'Log in')]")
    # log_in.click()
    
    usual_scenario_executed = False

    try:
        # Try to find the "usual" element
        sleep(5)
        unusual = driver.find_element(By.XPATH, "//input[@name='text']")
        unusual.send_keys('zachaudhary1122')
        
        next_button = driver.find_element(By.XPATH, "//span[contains(text(),'Next')]")
        next_button.click()
        
        # Set the flag to True if the "usual" scenario is executed
        usual_scenario_executed = True
        
    except:
        # Handle the case where "usual" element is not found
        sleep(5)
        password = driver.find_element(By.XPATH, "//input[@name='password']")
        password.send_keys('iklmermu15772900')
        
        log_in = driver.find_element(By.XPATH, "//span[contains(text(),'Log in')]")
        log_in.click()
        pass
    finally:
        # Run the "password" scenario only if the "usual" scenario was not executed
        if usual_scenario_executed:
            sleep(5)
            password = driver.find_element(By.XPATH, "//input[@name='password']")
            password.send_keys('iklmermu15772900')
            
            log_in = driver.find_element(By.XPATH, "//span[contains(text(),'Log in')]")
            log_in.click()
    
    sleep(5)
    # account_name = "babarazam258"
    driver.get(f"https://twitter.com/{twitter_user}")

    # Function to wait and scroll until desired number of tweets are loaded
    def wait_for_tweets(driver, tweet_count):
        loaded_tweets = 0
        attempts = 0
        while loaded_tweets < tweet_count and attempts < 10:  # Avoid infinite loops
            current_tweets = driver.find_elements(By.XPATH, ".//div[@data-testid='tweetText']")
            loaded_tweets = len(current_tweets)
            if loaded_tweets > 0 and loaded_tweets < tweet_count:
                ActionChains(driver).move_to_element(current_tweets[-1]).perform()
                sleep(2)  # Wait for more tweets to load
            elif loaded_tweets == 0:
                sleep(2)  # Wait and retry if no tweets are loaded yet
            attempts += 1

    # Wait for at least 5 tweets to load
    wait_for_tweets(driver, 5)

    # Now fetch the tweets
    tweets = driver.find_elements(By.XPATH, ".//div[@data-testid='tweetText']")

    content_texts = []
    # for tweet in tweets[:5]:  # This will fetch the first 3 tweets
    for index, tweet in enumerate(tweets[:3], start=1): 
        tweet_html = tweet.get_attribute('outerHTML')
        soup = BeautifulSoup(tweet_html, 'html.parser')
        text = soup.get_text()
        content_texts.append(text)
    concatenated_text = '\n'.join(content_texts)
    # Close the browser and end the session
    driver.quit()
    return concatenated_text


def communication_tones(f_com_tone):
    tone_mapping = {
    "Einstein Focus" : "Tone: Embraces an analytical and precise approach, ideal for delivering messages that are data-driven, logical, and intellectually stimulating, much like a scientific discourse.",
    "Shakespearean Elegance" : "Tone: Offers an eloquent and poetic style, perfect for crafting messages that are rich in literary flair and expressive language, captivating the reader like a classic play.",
    "Churchillian Resolve" : "Tone: Utilizes a persuasive and impactful manner, suitable for strong, decisive messaging that leaves a lasting impression, akin to a stirring wartime speech.",
    "Monroe Magnetism" : "Tone: Captures a charismatic and captivating charm, great for engaging and enchanting the audience with a blend of allure and approachability, reminiscent of a silver screen icon.",
    "Jobsian Vision" : "Tone: Reflects a visionary and inspiring style, ideal for forward-thinking and innovative messages that motivate and excite, similar to a groundbreaking product launch.",
    "Gandhian Empathy" : "Tone: Focuses on empathy and sincerity, perfect for messages that require understanding, compassion, and a gentle touch, echoing the peaceful resolve of a renowned activist.",
    "Hemingway Economy" : "Tone: Adopts a concise and straightforward approach, best for clear, no-nonsense communication that gets straight to the point, mirroring the style of a famed novelist.",
    "Da Vinci Creativity" : "Tone: Encourages a creative and inventive style, suitable for messages that are imaginative and out-of-the-box, drawing parallels to the works of a renowned Renaissance polymath.",
    "Chaplins Charm" : "Tone: Ensures an approachable, humorous, and heartfelt tone, excellent for warm, inviting, and personal messages that resonate with empathy, light humour, and understanding.",
    "Cleopatra Command" : "Tone: Exudes a bold and authoritative presence, ideal for assertive and commanding messages that convey leadership and confidence, reminiscent of an iconic ruler.",
    }
    
    try:
        matched_tone = tone_mapping.get(f_com_tone)
        return matched_tone
    except:
        return Response({"error": "Error to select tone :( Please try again...!"}, status = matched_tone.status_code)


def prompt_generator(f_name, f_category,f_interests,f_outreach, f_com_tone, f_usp, f_prev_interactions, f_urgency_level, f_entity_name, f_links, f_action_calls):
    #Generate a prompt based on user input
    name = f_name
    category = f_category
    interests = f_interests
    
    outreach = f_outreach
    com_tone = communication_tones(f_com_tone)
    usp = f_usp
    prev_interactions = f_prev_interactions
    urgency_level = f_urgency_level
    entity_name = f_entity_name
    links = f_links
    action_calls = f_action_calls
    
    
    
    main_prompt = {
        "role": "user",
        "content": f'''
        
        Generate a professional email based on the following details:\n
        Name: {name}\n
        Category: {category}\n
        Interests: {interests}\n
        Purpose of Outreach: {outreach}\n
        Tone of Communication: {com_tone}\n
        Key Points to Highlight: {usp}\n
        Previous Interactions: {prev_interactions}\n
        Urgency Level: {urgency_level}\n
        User's Company/Project Name: {entity_name}\n
        Attachments or Links: {links}\n
        Call to Action: {action_calls}\n
        
        '''
        }
    
    custom_prompt_instruction = {
        "role": "system",
        "content": f''' 
        Act as a professional email writer to {category}. Always start email with {category} interest, which you take 
        from interest(which is actually the {category} social media posts data only to know about the interest of {category}) data. 
        then write professional email which we can send from company/startup,{entity_name} to the {category}\n

        Explanation of Variables in the Prompt:\n
        Name: This is a name of writer who is writing email to the {category}.\n
        Category: Determines whether the email is for an {category}.\n
        Interests: To know the interest of {category} from his social media posts.\n
        Purpose of Outreach: Specifies the goal of the email.\n
        Tone of Communication: Sets the desired tone of the email based on the provided tone.\n
        Key Points to Highlight: Unique selling points or key aspects to be highlighted in the email.\n
        Previous Interactions: Indicates any previous contact with the recipient.\n
        Urgency Level: Suggests the level of urgency to be conveyed in the email.
        User's Company/Project Name: To personalize the message by including the user’s company or project name.\n
        Attachments or Links: Any relevant attachments or links to be included.\n
        Call to Action: A field to specify a preferred call to action for the end of the email 
        (e.g., Requesting a meeting, Asking for a response, Proposing a collaboration).\n

        FOLLOW THESE POINTS WHILE WRITING THE EMAIL:\n
        1- {name} is writing the email for the {category} for the specific purpose from {entity_name}\n
        2- From Interests, you should only take the {category} interest.\n 

        MAIN INSTRUCTION: \n
        1- We are writing this email for {category}.\n
        2- The main purpose of this email is to introduce and to build interest to our new product/service/company to {category} for different purposes.\n
        3- Linking these to the purpose of outreach. Ensure the email is crafted in the chosen tone, highlights the key points
        and ends with a clear call to action, all while maintaining a professional level suitable for corporate or industrial communication.\n

        FORMAT: \n
        Start of the email is ( Hello [Company Name],)\n
        End should be\n
        Sincerely,\n
        [{name}]\n
        {entity_name}\n

        IMPORTANT NOTE:\n
        1- Don't explain/add the {category} posts data in email. Only mention the {category} interest in relevant field.
        '''
        }
    
    
    # Set your OpenAI API key
    openai.api_key = "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"
    # Make a request to the OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[custom_prompt_instruction, main_prompt]
        # max_tokens=100  # Adjust as needed
    )
    # Get the generated text from the API response
    email = response['choices'][0]['message']['content']
    
    return email




@api_view(['POST'])
def test(request):
    # IDs for getting the relevant usernames of twitter and linkedin
    influencer_id = request.data.get("influencer_id")
    investor_id = request.data.get("investor_id")
    # Params for the Prompt creation
    f_category = request.data.get("category")
    f_outreach = request.data.get("outreach")
    f_com_tone = request.data.get("com_tone")
    f_usp = request.data.get("usp")
    f_prev_interactions = request.data.get("prev_interactions")
    f_urgency_level = request.data.get("urgency_level")
    f_entity_name = request.data.get("entity_name")
    f_links = request.data.get("links")
    f_action_calls = request.data.get("action_calls")

    # Process to email generation
    signin_response = signin()
    if not signin_response:
        return Response({"error": "Failed to sign in and obtain access token"}, status=signin_response.status_code)

    with ThreadPoolExecutor() as executor:
        if influencer_id and not investor_id:
            future = executor.submit(handle_influencer, influencer_id, signin_response, f_category, f_outreach, f_com_tone, f_usp, f_prev_interactions, f_urgency_level, f_entity_name, f_links, f_action_calls)
        elif investor_id and not influencer_id:
            future = executor.submit(handle_investor, investor_id, signin_response, f_category, f_outreach, f_com_tone, f_usp, f_prev_interactions, f_urgency_level, f_entity_name, f_links, f_action_calls)
        else:
            return Response({"response": "kindly select one"}, status=status.HTTP_400_BAD_REQUEST)

        result = future.result()
        return Response(result)

def handle_influencer(influencer_id, access_token, f_category, f_outreach, f_com_tone, f_usp, f_prev_interactions, f_urgency_level, f_entity_name, f_links, f_action_calls):
    influencer_api_url = f'https://raiderly-backend-467cbb45badd.herokuapp.com/api/influencer/{influencer_id}'
    headers = {'Authorization': f'Bearer {access_token}'}

    influencer_response = requests.get(influencer_api_url, headers=headers)
    if influencer_response.status_code != 200:
        return {"error": "Failed to fetch influencer data"}, influencer_response.status_code

    influencer_data = influencer_response.json().get('data', {})
    twitter = influencer_data.get('twitter', 'N/A')
    linkedin = influencer_data.get('linkedin', 'N/A')
    f_name = influencer_data.get('name', 'N/A')

    linkedin_post_data = fetch_linkedin(linkedin)
    print("Linkedin Scraping Done!")
    twitter_post_data = fetch_twitter(twitter)
    print("Twitter Scraping Done!")
    f_interests = f"\n---------Linkedin Interests: {linkedin_post_data} \n\n, Twitter Interests: {twitter_post_data}\n----------\n"
    print("Send To Email Process...!")
    generated_prompt = prompt_generator(f_name, f_category, f_interests, f_outreach, f_com_tone, f_usp, f_prev_interactions, f_urgency_level, f_entity_name, f_links, f_action_calls)
    return {"Email": generated_prompt}

def handle_investor(investor_id, access_token, f_category, f_outreach, f_com_tone, f_usp, f_prev_interactions, f_urgency_level, f_entity_name, f_links, f_action_calls):
    investor_api_url = f'https://raiderly-backend-467cbb45badd.herokuapp.com/api/investor/{investor_id}'
    headers = {'Authorization': f'Bearer {access_token}'}

    investor_response = requests.get(investor_api_url, headers=headers)
    if investor_response.status_code != 200:
        return {"error": "Failed to fetch investor data"}, investor_response.status_code

    investor_data = investor_response.json().get('data', {})
    twitter = investor_data.get('twitter', 'N/A')
    linkedin = investor_data.get('linkedin', 'N/A')
    f_name = investor_data.get('name', 'N/A')

    linkedin_post_data = fetch_linkedin(linkedin)
    print("Linkedin Scraping Done!")
    twitter_post_data = fetch_twitter(twitter)
    print("Twitter Scraping Done!")
    f_interests = f"\n---------Linkedin Interests: {linkedin_post_data} \n\n, Twitter Interests: {twitter_post_data}\n----------\n"
    print("Send To Email Process...!")
    generated_prompt = prompt_generator(f_name, f_category, f_interests, f_outreach, f_com_tone, f_usp, f_prev_interactions, f_urgency_level, f_entity_name, f_links, f_action_calls)
    return {"Email": generated_prompt}



