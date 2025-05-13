
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

API_KEY = "sk-e8b9608b5a14425d9e5979cdfcc1f4cc"
API_URL = "https://api.deepseek.com/v1/chat/completions"

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()

    prompt = data.get("prompt", "")
    mode = data.get("mode", "default")  # 支持多模式请求

    if not prompt and mode != "daily":
        return jsonify({"error": "缺少提示词"}), 400

    # 根据功能模式处理 prompt
    if mode == "article":
        prompt = f"请写一篇关于“{prompt}”的中文文章，300字左右。"
    elif mode == "poem":
        prompt = f"请写一首关于“{prompt}”的古诗。"
    elif mode == "rewrite":
        prompt = f"请将下面这句话改写得更文艺幽默一点：{prompt}"
    elif mode == "daily":
        prompt = "请给我一句 AI 每日金句或者励志鸡汤。"
    # mode == "chat" 时不处理 prompt

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 300
    }

    try:
        response = requests.post(API_URL, headers=headers, json=body)
        result = response.json()
        content = result['choices'][0]['message']['content']
        return jsonify({"result": content})
    except Exception as e:
        return jsonify({"error": "生成失败", "detail": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
