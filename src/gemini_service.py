import requests
import json
import random
from . import config
import time

# --- Default Fallbacks ---
DEFAULT_QUOTE = "Keep pushing! You’re closer than you think. 💪"
DEFAULT_HINTS = ["Try to break the problem down into smaller pieces.", "Think about the data structures that might be useful here."]

def call_gemini_api(prompt_text, expect_json=False):
    """
    A generic function to call the Gemini API using 'requests'.
    This uses the gemini-2.5-flash model for speed and efficiency.
    """
    if not config.GEMINI_API_KEY:
        print("GEMINI_API_KEY not set. Skipping Gemini call.")
        return None

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={config.GEMINI_API_KEY}"

    gen_config = {
        "temperature": 0.7 
    }

    if expect_json:
        gen_config["responseMimeType"] = "application/json"
        gen_config["responseSchema"] = {
            "type": "ARRAY",
            "items": { "type": "STRING" }
        }

    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": gen_config 
    }
    

    try:
        response = requests.post(api_url, json=payload, headers={'Content-Type': 'application/json'})
        response.raise_for_status() # Raise an error for bad responses
        
        result = response.json()
        text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        
        if not text:
            print(" Gemini API returned an empty response.")
            return None
        
        return text
        
    except requests.exceptions.RequestException as e:
        print(f" Error calling Gemini API: {e}")
        return None
    except (KeyError, IndexError):
        print(f" Error parsing Gemini response: {result}")
        return None

def get_motivational_quote():
    """
    Calls Gemini to get a motivational quote from a famous movie.
    """
    #adding salt to prevent server side caching of api response
    current_time_salt = time.time()

    prompt = """Give me one, and only one, inspiring motivational quote from a famous movie. Include the movie title and who said it in the follwing manner.
    eg:
    There is a difference between knowing the path and walking the path.
    - Morpheus (The Matrix).
    The format should match 100%.
    Make sure it's fresh and not overused. The quote should be concise, impactful, and suitable for encouraging someone to keep going with their coding practice.
    Add a touch of creativity to make it stand out!
    Use the following unique salt to ensure variety: {current_time_salt}
    """
    
    quote = call_gemini_api(prompt)
    
    if quote:
        return quote.strip().strip('"')
    else:
        return DEFAULT_QUOTE

def generate_optimal_hints(question, hint_count):
    """
    Uses Gemini to generate new, optimal hints based on LeetCode's data.
    """
    
    title = question['title']
    difficulty = question['difficulty']
    tags = ", ".join([tag['name'] for tag in question.get('topicTags', [])])
    original_hints = "\n".join([f"- {h}" for h in question.get('hints', [])])

    prompt = f"""
    You are an expert LeetCode & Data structures coach. A user is stuck on the following problem:
    - Problem: "{title}"
    - Difficulty: {difficulty}
    - Topic Tags: {tags}
    
    The original, cryptic hints provided by LeetCode are:
    {original_hints}
    
    Please generate exactly {hint_count} new, short, and intuitive hints to help the user.
    These new hints should be more helpful than the originals. Guide them towards the right data structure or algorithm without giving away the full solution.
    
    Return your {hint_count} hints as a JSON array of strings.
    """
    
    # We expect a JSON response (an array of strings)
    response_text = call_gemini_api(prompt, expect_json=True)
    
    if response_text:
        try:
            hints = json.loads(response_text)
            if isinstance(hints, list) and len(hints) > 0:
                return hints
            else:
                print(" Gemini did not return a valid list of hints.")
        except json.JSONDecodeError:
            print(f" Failed to decode Gemini's JSON hint response: {response_text}")
    
    # Fallback if anything fails
    return DEFAULT_HINTS[:hint_count]
