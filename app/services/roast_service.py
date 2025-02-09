import json
import os
from openai import OpenAI
from app.utils.helpers import save_to_cache, load_from_cache

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
def get_roast_from_openai(summary: str, use_cache: bool = False) -> str:
    """Generate a sharp, personalized roast targeting professional history using OpenAI."""
    cache_file = f"roast.txt"
    
    if use_cache:
        cached_data = load_from_cache(cache_file)
        if cached_data:
            return cached_data
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        prompt = f"""SAVAGE PROFESSIONAL ROAST MISSION:
Create a devastating yet clever roast that:
- Ruthlessly dissects their career choices and educational background
- Uses specific details from their work history to craft personalized burns
- Mocks company transitions, job titles, and industry pivots
- Questions their educational choices and how they've used (or wasted) their degree
- Pokes fun at corporate buzzwords in their experience
- Maintains just enough professionalism to be shareable
- Maximum 200 words
- Start with "Oh look everyone, it's..."

Rules for maximum impact:
- Reference specific companies and roles from their history
- Call out suspicious career gaps or lateral moves
- Mock any inflated titles or responsibilities
- Draw ironic connections between their education and career path
- Use industry-specific terminology to create targeted burns
- End with a killer punchline about their future career prospects

This will be used for a text to speech video so keep it fast paced and engaging.

LinkedIn Summary:
{summary}"""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a ruthless comedy roast writer who specializes in career-focused takedowns and corporate satire."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=400
        )
        
        roast = response.choices[0].message.content
        save_to_cache(roast, cache_file)
        return roast
    except Exception as e:
        raise
def generate_roast(linkedin_data, use_cache: bool = False) -> str:
    """Main function to generate roast from LinkedIn data."""

    return get_roast_from_openai(linkedin_data, use_cache) 