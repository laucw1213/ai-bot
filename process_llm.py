import os
import google.generativeai as genai
from pathlib import Path
from datetime import datetime

def process_with_llm():
    # 配置 Gemini
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-pro')

    # 读取 repomix 分析结果
    with open('analysis.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # 准备提示词
    prompt = f"""分析这个 markdown 文档，重点关注：
    1. 主要功能和用途
    2. 使用方法和步骤
    3. 重要特性说明
    4. 注意事项

    请生成一个清晰的用户指南。

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

if __name__ == "__main__":
    process_with_llm()