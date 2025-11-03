import os
from django.conf import settings
import google.generativeai as genai
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

genai.configure(api_key=GEMINI_API_KEY)


# Initialize the Gemini model
model = genai.GenerativeModel('gemini-2.5-flash')
response = model.generate_content("Explain how AI works in a few words")


def match_jobs_with_ai(search_request: Dict[str, Any], jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Match jobs with the search request using a scoring system
    Returns a list of jobs with match scores
    """
    try:
        matched_jobs = []
        
        for job in jobs:
            score = 0.0
            reasons = []
            
            # 1. Title match (30% weight)
            if search_request.get('title'):
                title_similarity = calculate_similarity(
                    search_request['title'].lower(),
                    job.get('title', '').lower()
                )
                score += title_similarity * 0.3
                reasons.append(f"Title similarity: {title_similarity:.2f}")
            
            # 2. Skills match (40% weight)
            if search_request.get('skills'):
                job_skills = {s['name'].lower() for s in job.get('skills', [])}
                search_skills = {s.lower() for s in search_request['skills']}
                
                if job_skills and search_skills:
                    skill_match_ratio = len(job_skills.intersection(search_skills)) / len(search_skills)
                    score += skill_match_ratio * 0.4
                    reasons.append(f"Skills match: {skill_match_ratio:.2f}")
            
            # 3. Experience match (20% weight)
            if search_request.get('experience') is not None:
                exp_required = job.get('experience_min', 0)
                exp_have = search_request['experience']
                
                if exp_have >= exp_required:
                    exp_score = 1.0  # Full score if meets or exceeds
                elif exp_required > 0:
                    exp_score = exp_have / exp_required  # Partial score based on ratio
                else:
                    exp_score = 0.5  # Default score if no experience required
                
                score += exp_score * 0.2
                reasons.append(f"Experience score: {exp_score:.2f}")
            
            # 4. Location match (10% weight)
            if search_request.get('location'):
                location_match = search_request['location'].lower() in job.get('location', '').lower()
                score += 0.1 if location_match else 0
                reasons.append(f"Location match: {location_match}")
            
            # Ensure score is between 0 and 1
            score = max(0, min(1, score))
            
            # Add match details to job
            job['match_score'] = round(score, 2)
            job['match_reasons'] = reasons
            
            # Only include jobs that meet minimum criteria
            if score >= 0.4:  # Adjust threshold as needed
                matched_jobs.append(job)
        
        # Sort by score in descending order
        return sorted(matched_jobs, key=lambda x: x['match_score'], reverse=True)
        
    except Exception as e:
        print(f"Error in job matching: {str(e)}")
        # Fallback: return jobs with default score
        for job in jobs:
            job['match_score'] = 0.5
            job['match_reasons'] = ["Error in matching"]
        return jobs

def calculate_similarity(str1: str, str2: str) -> float:
    """Calculate similarity ratio between two strings"""
    from difflib import SequenceMatcher
    return SequenceMatcher(None, str1, str2).ratio()