import os
import google.generativeai as genai
from pathlib import Path
from datetime import datetime

def process_with_llm():
    # 确认 API 密钥存在
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY environment variable")

    # 配置 Gemini
    genai.configure(api_key=api_key)
    
    # 使用 gemini-2.0-flash-exp 模型
    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    try:
        # 读取 repomix 分析结果
        with open('analysis.md', 'r', encoding='utf-8') as f:
            content = f.read()

        # 准备提示词
        prompt = f"""分析这个 markdown 文档，创建一个用户指南。请重点关注：
        1. 主要功能说明
        2. 使用步骤
        3. 配置说明
        4. 注意事项

        请使用清晰、简洁的语言，面向普通用户。

        文档内容：
        {content}
        """

        # 生成回答
        response = model.generate_content(prompt)
        result = response.text

        # 生成带时间戳的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_{timestamp}.md"
        
        # 保存结果
        Path(filename).write_text(result, encoding='utf-8')
        print(f"Generated analysis saved to {filename}")

    except Exception as e:
        print(f"Error processing content: {str(e)}")
        raise

if __name__ == "__main__":
    process_with_llm()