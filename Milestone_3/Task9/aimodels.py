# aimodel.py

import openai
import google.generativeai as genai
import os

# Load environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
gemini_flash_api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini Flash API
genai.configure(api_key=gemini_flash_api_key)

def gpt_generate_response(prompt, system_message):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": system_message},
                      {"role": "user", "content": prompt}]
        )
        return completion.choices[0].message['content']
    except Exception as e:
        print(f"Error with GPT API: {e}")
        return None

def gemini_generate_response(prompt, container_model):
    try:
        model = genai.GenerativeModel(
            "gemini-1.5-flash",
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": container_model
            }
        )
        response = model.generate_content(prompt)
        print(response)
        if response and response.candidates and response.candidates[0].content.parts:
            return response.candidates[0].content.parts[0].text
    except Exception as e:
        print(f"Error with Gemini API: {e}")
        return None
