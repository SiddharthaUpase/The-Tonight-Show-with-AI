import requests
import json
import os
import re
from app.utils.helpers import save_to_cache, load_from_cache

LINKEDIN_DATA_API_KEY = os.getenv('LINKEDIN_DATA_API_KEY')
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')

def extract_username(linkedin_url: str) -> str:
    """Extract username from LinkedIn URL."""
    pattern = r'linkedin\.com/in/([^/]+)'
    match = re.search(pattern, linkedin_url)
    if match:
        return match.group(1)
    raise ValueError("Invalid LinkedIn URL format")

def get_linkedin_data(linkedin_url: str, use_cache: bool = False) -> dict:
    """Fetch LinkedIn data using RapidAPI."""
    username = extract_username(linkedin_url)
    print(f"\n=== Getting LinkedIn data for: {username} ===")
    cache_file = f"{username}_linkedin_data.json"
    
    if use_cache:
        cached_data = load_from_cache(cache_file)
        if cached_data:
            print("Using cached LinkedIn data")
            return extract_linkedin_details(cached_data)  # Return extracted data from cache
    
    url = "https://linkedin-data-api.p.rapidapi.com/"
    
    headers = {
        "x-rapidapi-key": "dd9ef829a8mshaa9e8522911bc7cp1ac9c3jsn9f1c90cc81f5",
        "x-rapidapi-host": "linkedin-data-api.p.rapidapi.com"
    }
    
    querystring = {"username": username}
    
    try:
        print(f"Making RapidAPI request for profile: {username}")
        response = requests.get(url, headers=headers, params=querystring)
        
        if response.status_code == 200:
            print("Successfully retrieved LinkedIn data")
            data = response.json()
            save_to_cache(data, cache_file)
            return extract_linkedin_details(data)  # Return extracted data
        elif response.status_code == 429:
            print(f"RapidAPI rate limit exceeded: {response.text}")
            cached_data = load_from_cache(cache_file)
            if cached_data:
                print("Using cached data due to rate limit")
                return extract_linkedin_details(cached_data)  # Return extracted data from cache
            raise Exception("Rate limit exceeded and no cache available")
        else:
            print(f"RapidAPI request failed: Status {response.status_code}")
            print(f"Error response: {response.text}")
            cached_data = load_from_cache(cache_file)
            if cached_data:
                print("Using cached data as fallback")
                return extract_linkedin_details(cached_data)  # Return extracted data from cache
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Network error during API call: {str(e)}")
        cached_data = load_from_cache(cache_file)
        if cached_data:
            print("Using cached data after network error")
            return extract_linkedin_details(cached_data)  # Return extracted data from cache
        raise

def download_profile_picture(profile_data: dict, output_path: str = "profile.jpg") -> str:
    """Download LinkedIn profile picture."""
    try:
        if isinstance(profile_data, dict) and 'data' in profile_data:
            profile_data = profile_data['data']
        
        profile_pic_url = profile_data.get('profile_picture')
        if not profile_pic_url:
            return None
            
        response = requests.get(profile_pic_url)
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return output_path
        else:
            return None
            
    except Exception as e:
        return None

def extract_linkedin_details(linkedin_data: dict) -> dict:
    """Extract relevant details from LinkedIn data."""
    positions = linkedin_data.get("position", [])
    educations = linkedin_data.get("educations", [])
    
    extracted_data = {
        "personal_details": {
            "first_name": linkedin_data.get("firstName", ""),
            "last_name": linkedin_data.get("lastName", ""),
            "full_name": f"{linkedin_data.get('firstName', '')} {linkedin_data.get('lastName', '')}",
            "location": linkedin_data.get("geo", {}).get("full", "")
        },
        "profile_picture": linkedin_data.get("profilePicture", ""),
        "headline": linkedin_data.get("headline", ""),
        "professional_background": {
            "current_role": {
                "title": positions[0].get("title", "") if positions else "",
                "company_name": positions[0].get("companyName", "") if positions else "",
                "company_industry": positions[0].get("companyIndustry", "") if positions else ""
            },
            "previous_work_experience": {
                "previous_company": positions[1].get("companyName", "") if len(positions) > 1 else "",
                "previous_role": positions[1].get("title", "") if len(positions) > 1 else "",
                "key_contributions": positions[1].get("description", "") if len(positions) > 1 else ""
            }
        },
        "education": {
            "degrees": [
                {
                    "degree": educations[0].get("degree", "") if educations else "",
                    "school": educations[0].get("schoolName", "") if educations else ""
                },
                {
                    "degree": educations[1].get("degree", "") if len(educations) > 1 else "",
                    "school": educations[1].get("schoolName", "") if len(educations) > 1 else ""
                }
            ]
        },
        "summary": linkedin_data.get("summary", ""),
        "skills": [skill.get("name", "") for skill in linkedin_data.get("skills", [])]
    }

    return extracted_data 