import os
import google.generativeai as genai
from pathlib import Path
from datetime import datetime

def process_with_llm():
    # Check for API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY environment variable")

    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    try:
        # Read analysis file
        print("Reading analysis.md...")
        with open('analysis.md', 'r', encoding='utf-8') as f:
            content = f.read()

        # Prepare prompt
        prompt = """Create a simple guide that ONLY explains how to use this tool. Focus on:
        1. Step-by-step instructions for using the tool
        2. What inputs the user needs to provide
        3. What outputs they will get
        4. Any specific actions they need to take

        Write in very simple, direct language.
        Only include practical usage steps.
        No technical details, setup, or background information.

        Repository contents:
        {content}
        """

        print("Generating content with Gemini...")
        response = model.generate_content(prompt.format(content=content))
        result = response.text

        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_{timestamp}.md"
        
        print(f"Saving result to {filename}...")
        Path(filename).write_text(result, encoding='utf-8')
        print("Processing complete!")

    except Exception as e:
        print(f"Error processing content: {str(e)}")
        raise

if __name__ == "__main__":
    process_with_llm()