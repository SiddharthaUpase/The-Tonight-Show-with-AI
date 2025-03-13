import os
import anthropic
from app.utils.helpers import save_to_cache, load_from_cache

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

def get_roast_from_claude(summary: str, use_cache: bool = False) -> str:
    """Generate a sharp, personalized roast targeting professional history using Claude."""
    cache_file = f"roast.txt"
    
    if use_cache:
        cached_data = load_from_cache(cache_file)
        if cached_data:
            print("Using cached roast from Claude")
            return cached_data
    
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        # Optimized prompt for more brutal, concise roasts (under 1 minute when spoken)
        prompt = f"""SAVAGE PROFESSIONAL ROAST MISSION:
Create a BRUTALLY savage roast that:
- Ruthlessly mocks their career choices, job titles, and educational background
- Uses specific details from their work history for personalized, cutting insults
- Calls out any suspicious career gaps, lateral moves, or inflated titles
- Ridicules their educational choices and how they've wasted their degree
- Mocks any corporate buzzwords or pretentious language in their profile
- MUST be under 150 words total (to keep it under 1 minute when spoken)
- Start with "Oh look everyone, it's..."
- End with a devastating punchline about their future career prospects

Make it EXTREMELY brutal but still clever - don't hold back! Use industry-specific terminology to create targeted burns that would make a comedy roast audience gasp.

This will be used for a text-to-speech video, so keep it fast-paced and engaging.

LinkedIn Summary:
{summary}"""
        
        # Estimate input tokens (very rough approximation)
        input_tokens = len(prompt.split()) * 1.3  # Rough estimate: words * 1.3
        
        # Make the API call
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=400,
            temperature=0.9,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        roast = message.content[0].text
        
        # Estimate output tokens (very rough approximation)
        output_tokens = len(roast.split()) * 1.3  # Rough estimate: words * 1.3
        
        # Calculate total tokens and cost
        total_tokens = input_tokens + output_tokens
        cost_per_million = 5.0  # $5 per million tokens
        estimated_cost = (total_tokens / 1000000) * cost_per_million
        
        print(f"Estimated token usage: {int(total_tokens)} tokens")
        print(f"Estimated cost: ${estimated_cost:.6f}")
        
        save_to_cache(roast, cache_file)
        return roast
    except Exception as e:
        raise

def generate_roast(linkedin_data: dict, use_cache: bool = False) -> str:
    """Main function to generate roast from LinkedIn data."""
    return get_roast_from_claude(linkedin_data, use_cache) 