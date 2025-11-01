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
model = genai.GenerativeModel('gemini-pro')

def match_jobs_with_ai(search_request: Dict[str, Any], jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Match jobs with the search request using Gemini AI
    Returns a list of jobs with similarity scores
    """
    try:
        # Prepare the prompt for Gemini
        prompt = f"""You are an AI job matching assistant. 
        Rate the relevance of each job based on the following search criteria:
        
        Search Criteria:
        - Title: {search_request.get('title', 'Not specified')}
        - Skills: {', '.join(search_request.get('skills', []))}
        - Experience: {search_request.get('experience', 'Not specified')} years
        - Location: {search_request.get('location', 'Not specified')}
        
        For each job, provide a relevance score from 0 to 1 based on how well it matches the criteria.
        Consider the job title, required skills, experience level, and location in your assessment.
        
        Jobs to evaluate:
        """
        
        # Add job details to the prompt
        for i, job in enumerate(jobs):
            job_skills = [skill['name'] for skill in job.get('skills', [])]
            prompt += f"""
            Job {i+1}:
            - Title: {job.get('title')}
            - Company: {job.get('company')}
            - Location: {job.get('location')}
            - Experience Required: {job.get('experience_min', 0)} years
            - Skills: {', '.join(job_skills) if job_skills else 'Not specified'}
            - Description: {job.get('description', '')[:200]}...
            
            Relevance Score (0-1): """
        
        # Get response from Gemini
        print(prompt)
        response = model.generate_content(prompt)
        
        # Parse the response to extract scores
        scores = []
        for line in response.text.split('\n'):
            if 'Relevance Score' in line or ':' in line:
                try:
                    score = float(line.split(':')[-1].strip())
                    scores.append(min(max(score, 0), 1))  # Ensure score is between 0 and 1
                except (ValueError, IndexError):
                    continue
        
        # Add scores to jobs
        for i, job in enumerate(jobs):
            job['match_score'] = scores[i] if i < len(scores) else 0.0
        
        # Sort jobs by match score in descending order
        return sorted(jobs, key=lambda x: x.get('match_score', 0), reverse=True)
        
    except Exception as e:
        print(f"Error in AI job matching: {str(e)}")
        # Fallback: return jobs with default score
        for job in jobs:
            job['match_score'] = 0.5
        return jobs