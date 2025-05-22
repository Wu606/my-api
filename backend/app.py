# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import requests
# import jieba
# from collections import Counter
#
# app = Flask(__name__)
# CORS(app)
#
# API_KEY = "sk-e8b9608b5a14425d9e5979cdfcc1f4cc"
# API_URL = "https://api.deepseek.com/v1/chat/completions"
#
# @app.route("/generate", methods=["POST"])
# def generate():
#     data = request.get_json()
#     prompt = data.get("prompt", "")
#     mode = data.get("mode", "default")
#
#     if not prompt and mode != "daily":
#         return jsonify({"error": "缺少提示词"}), 400
#
#     if mode == "article":
#         prompt = f"请写一篇关于“{prompt}”的中文文章，300字左右。"
#     elif mode == "poem":
#         prompt = f"请写一首关于“{prompt}”的古诗。"
#     elif mode == "rewrite":
#         prompt = f"请将下面这句话改写得更文艺幽默一点：{prompt}"
#     elif mode == "daily":
#         prompt = "请给我一句 AI 每日金句或者励志鸡汤。"
#
#     headers = {
#         "Authorization": f"Bearer {API_KEY}",
#         "Content-Type": "application/json"
#     }
#
#     body = {
#         "model": "deepseek-chat",
#         "messages": [{"role": "user", "content": prompt}],
#         "temperature": 0.7,
#         "max_tokens": 300
#     }
#
#     try:
#         response = requests.post(API_URL, headers=headers, json=body)
#         result = response.json()
#         content = result['choices'][0]['message']['content']
#         return jsonify({"result": content})
#     except Exception as e:
#         return jsonify({"error": "生成失败", "detail": str(e)}), 500
#
# # @app.route("/wordcloud_from_text", methods=["POST"])
# # def wordcloud_from_text():
# #     data = request.get_json()
# #     text = data.get("text", "")
# #
# #     if not text.strip():
# #         return jsonify({"error": "文本为空"}), 400
# #
# #     print("✅ 收到上传文本内容，开始分词")
# #     words = jieba.lcut(text)
# #     filtered = [w for w in words if len(w.strip()) > 1 and w.isalpha()]
# #     freq = Counter(filtered)
# #     top_words = freq.most_common(30)
# #     result = [{"text": word, "count": count} for word, count in top_words]
# #
# #     print("✅ 返回关键词：", result)
# #     return jsonify({"result": result})
# @app.route("/wordcloud_from_text", methods=["POST"])
# def wordcloud_from_text():
#     data = request.get_json()
#     print("🧪 接收到请求数据：", data)   # 加这一句
#     text = data.get("text", "")
#
#     if not text.strip():
#         print("❌ 文本为空！")
#         return jsonify({"error": "文本为空"}), 400
#
#     print("✅ 收到上传文本内容，开始分词")
#     words = jieba.lcut(text)
#     filtered = [w for w in words if len(w.strip()) > 1 and w.isalpha()]
#     print("📌 分词结果：", filtered)
#     freq = Counter(filtered)
#     top_words = freq.most_common(30)
#     result = [{"text": word, "count": count} for word, count in top_words]
#
#     print("✅ 返回关键词：", result)
#     return jsonify({"result": result})
#
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import jieba
from collections import Counter
from docx import Document  # Word 文件处理
import base64
import tempfile
import os

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
    print("🧪 接收到请求数据：", data)
    text = data.get("text", "")

    if not text.strip():
        print("❌ 文本为空！")
        return jsonify({"error": "文本为空"}), 400

    print("✅ 收到上传文本内容，开始分词")
    return jsonify({"result": extract_keywords(text)})


@app.route("/wordcloud_from_word", methods=["POST"])
def wordcloud_from_word():
    """
    接收 base64 编码的 .docx 文件内容，提取文字生成词云
    """
    data = request.get_json()
    encoded = data.get("file", "")

    if not encoded:
        return jsonify({"error": "未提供文件内容"}), 400

    try:
        # 解码并写入临时 Word 文件
        word_bytes = base64.b64decode(encoded)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(word_bytes)
            tmp_path = tmp.name

        # 读取 Word 文本内容
        doc = Document(tmp_path)
        text = "\n".join([p.text for p in doc.paragraphs])

        os.remove(tmp_path)

        if not text.strip():
            return jsonify({"error": "Word 文件为空"}), 400

        print("✅ Word 文件读取成功，开始分词")
        return jsonify({"result": extract_keywords(text)})

    except Exception as e:
        return jsonify({"error": "Word 文件处理失败", "detail": str(e)}), 500


def extract_keywords(text):
    """通用分词 + 统计函数"""
    words = jieba.lcut(text)
    filtered = [w for w in words if len(w.strip()) > 1 and w.isalpha()]
    freq = Counter(filtered)
    top_words = freq.most_common(30)
    result = [{"text": word, "count": count} for word, count in top_words]
    print("✅ 返回关键词：", result)
    return result


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
