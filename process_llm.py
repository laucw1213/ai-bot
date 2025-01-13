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
        prompt = """Analyze the contents of this repository and create a user guide. Focus:
        1. Main functions and uses
        2. Code Structure
        3. Installation and usage
        4. Important Features
        5. Notes

        Please write in plain language, targeting end users.
        Organize the analysis into a structured markdown format.

        Warehouse contents:
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