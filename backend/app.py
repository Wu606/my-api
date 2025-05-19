from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import jieba
from collections import Counter
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import jieba
from collections import Counter
from paddleocr import PaddleOCR
import os

# OCR 相关
import cv2
import numpy as np
from paddleocr import PaddleOCR


app = Flask(__name__)
CORS(app)

API_KEY = "sk-e8b9608b5a14425d9e5979cdfcc1f4cc"
API_URL = "https://api.deepseek.com/v1/chat/completions"

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    prompt = data.get("prompt", "")
    mode = data.get("mode", "default")

    if not prompt and mode != "daily":
        return jsonify({"error": "缺少提示词"}), 400

    if mode == "article":
        prompt = f"请写一篇关于“{prompt}”的中文文章，300字左右。"
    elif mode == "poem":
        prompt = f"请写一首关于“{prompt}”的古诗。"
    elif mode == "rewrite":
        prompt = f"请将下面这句话改写得更文艺幽默一点：{prompt}"
    elif mode == "daily":
        prompt = "请给我一句 AI 每日金句或者励志鸡汤。"

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


@app.route("/wordcloud_from_text", methods=["POST"])
def wordcloud_from_text():
    data = request.get_json()
    text = data.get("text", "")

    if not text.strip():
        return jsonify({"error": "文本为空"}), 400

    print("✅ 收到上传文本内容，开始分词")
    words = jieba.lcut(text)
    filtered = [w for w in words if len(w.strip()) > 1 and w.isalpha()]
    freq = Counter(filtered)
    top_words = freq.most_common(30)
    result = [{"text": word, "count": count} for word, count in top_words]

    print("✅ 返回关键词：", result)
    return jsonify({"result": result})

ocr = PaddleOCR(use_angle_cls=True, lang='ch')  # 初始化OCR模型（仅执行一次）


@app.route("/ocr_image", methods=["POST"])
def ocr_image():
    print("📷 正在接收图片文件")
    image = request.files.get("image")
    if not image:
        print("❌ 没收到图片")
        return jsonify({"error": "缺少图片"}), 400


    content = image.read()
    npimg = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    result = ocr.ocr(img, cls=True)
    text = "\n".join([line[1][0] for line in result[0]])

    # 分词并计算词频
    words = jieba.lcut(text)
    filtered = [w for w in words if len(w.strip()) > 1 and w.isalpha()]
    freq = Counter(filtered)
    top_words = freq.most_common(30)
    result = [{"text": word, "count": count} for word, count in top_words]

    return jsonify({"result": result})




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
