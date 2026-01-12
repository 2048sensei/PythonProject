import os
import fitz  # PyMuPDF
import jieba  # 新增：用于中文分词
from collections import Counter  # 新增：用于统计词频
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)
@app.route('/')
def hello():
    return "<h1>翎的实验室：服务器已就绪！</h1><p>牧，请使用前端页面上传 PDF 哦。</p>"
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# 1. 解析 PDF 文本
def parse_pdf(filepath):
    doc = fitz.open(filepath)
    all_text = ""
    for page in doc:
        all_text += page.get_text() + "\n"
    doc.close()
    return all_text


# 2. 核心逻辑：提取高频词并生成 ECharts 数据
def generate_knowledge_graph(text):
    # --- A. 简单的字符串处理：分词与统计 ---
    # 使用 jieba 进行中文分词
    words = jieba.lcut(text)

    # 过滤掉单字、换行符和常见的无意义词（这里可以根据需要扩展停用词表）
    # 比如：'的', '是', '在' 等通常没有分析价值
    stop_words = {'的', '了', '和', '是', '在', '也', '就', '与', '对于', '等', '之', '上', '下', '\n', ' '}
    filtered_words = [w for w in words if len(w) > 1 and w not in stop_words]

    # 提取前 10 个高频词
    word_counts = Counter(filtered_words)
    top10_words = word_counts.most_common(10)  # 格式: [('词A', 10), ('词B', 8)...]

    # --- B. 生成 ECharts 需要的 JSON 格式 (nodes, links) ---
    # 既然是模拟知识图谱，我们可以创建一个中心节点（PDF文档本身），然后连接到这10个关键词

    nodes = []
    links = []

    # 添加中心节点
    nodes.append({
        "name": "当前文档",
        "symbolSize": 30,  # 中心节点大一点
        "category": 0,  # 类别索引
        "draggable": True  # 允许拖拽
    })

    # 遍历高频词生成子节点和连线
    for word, freq in top10_words:
        # 节点大小可以根据词频动态变化，最小 15
        size = 15 + (freq * 2)
        nodes.append({
            "name": word,
            "value": freq,  # 鼠标悬停显示出现的次数
            "symbolSize": min(size, 60),  # 限制最大圆圈
            "category": 1,
            "draggable": True
        })

        # 建立连接：中心 -> 关键词
        links.append({
            "source": "当前文档",
            "target": word
        })

    return {"nodes": nodes, "links": links}


@app.route('/upload', methods=['POST'])
def upload_and_parse():
    if 'file' not in request.files:
        return jsonify({'error': '未找到文件部分'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400

    if file and file.filename.lower().endswith('.pdf'):
        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)

        try:
            # 1. 提取文字
            extracted_text = parse_pdf(save_path)

            # 2. 生成图谱数据 (这是本次新增的核心)
            graph_data = generate_knowledge_graph(extracted_text)

            return jsonify({
                'message': '解析成功！',
                'content': extracted_text[:200] + "...",  # 只返回前200字预览，避免太长
                'echarts_data': graph_data  # 把算好的 nodes 和 links 给前端
            }), 200
        except Exception as e:
            return jsonify({'error': f'处理失败: {str(e)}'}), 500

    return jsonify({'error': '请上传 PDF 文件'}), 400


if __name__ == '__main__':
    # 必须是 0.0.0.0，否则穿透流量进不来
    app.run(debug=True, host='0.0.0.0', port=5000)
