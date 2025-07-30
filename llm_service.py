# llm_service.py
import os
import json
from openai import AsyncOpenAI
import schemas

# Initialize the AsyncOpenAI client
# It automatically reads the OPENAI_API_KEY from the environment
client = AsyncOpenAI()

async def parse_search_query(description: str) -> schemas.SearchDescriptionParseResponse:
    """Parses a natural language job description into structured search filters."""
    prompt = f"""
    You are an expert HR assistant specializing in parsing recruitment queries.
    Analyze the following job description and extract the key search parameters.
    The user wants to find candidates.

    Description: "{description}"

    Extract the following information and return it as a JSON object with these exact keys:
    - "role": The job title or role mentioned (e.g., "backend developer", "data analyst").
    - "skills": A list of specific technical skills, tools, or programming languages (e.g., ["Python", "FastAPI", "GCP", "SQL"]).
    - "experience_years": A string representing the years of experience, like "3-5 years", "5+ years", etc.

    Your response must be only the JSON object, without any other text or explanations.
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        parsed_json = json.loads(content)
        return schemas.SearchDescriptionParseResponse(**parsed_json)
    except Exception as e:
        print(f"Error calling OpenAI for search query parsing: {e}")
        raise

async def analyze_interview_text(interview_text: str) -> schemas.InterviewAnalysis:
    """Analyzes interview text and provides a structured assessment."""
    prompt = f"""
    You are a senior technical recruiter and talent assessor. Analyze the following interview transcript/summary.
    Based *only* on the text provided, provide a detailed, structured analysis.

    Interview Text: "{interview_text}"

    Provide your analysis as a JSON object with the following structure and keys:
    - "strengths": A list of strings identifying the candidate's key strengths.
    - "weaknesses": A list of strings identifying the candidate's key weaknesses or areas for improvement.
    - "assessment_aspects": A dictionary where keys are predefined assessment categories and values are your rating (e.g., "Excellent", "Good", "Needs Improvement", "Not Assessed"). The categories are: "Core Technical Skills", "Problem-Solving Ability", "Past Project Experience", "Technical Depth", "Communication & Clarity", "Motivation & Drive", "Team Collaboration & Attitude", "Reliability & Ownership".
    - "red_flags_identified": A list of strings detailing any potential red flags. If none, return an empty list.
    - "overall_score": An integer from 0 to 100 representing your overall recommendation score for the candidate based on this interview.

    Your response must be only the JSON object.
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        parsed_json = json.loads(content)
        return schemas.InterviewAnalysis(**parsed_json)
    except Exception as e:
        print(f"Error calling OpenAI for interview analysis: {e}")
        raise