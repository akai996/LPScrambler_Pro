import os
import random
import string
import json
import base64
import shutil
from bs4 import BeautifulSoup

class LPScramblerProV2:
    def __init__(self, template_path, output_dir="dist_lp"):
        self.template_path = template_path
        self.output_dir = output_dir
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        self.map = {}

    def _rand_str(self, length=8):
        return ''.join(random.choices(string.ascii_lowercase, k=length))

    def _generate_white_content(self):
        """生成合规的行业资讯填充内容，防止页面空值"""
        topics = [
            "随着互联网技术的飞速发展，信息安全已成为企业关注的重中之重。",
            "在数字化转型的浪潮中，我们始终致力于为客户提供最安全可靠的技术支持。",
            "隐私保护不仅是一项法律要求，更是我们对用户最基本的承诺。",
            "通过持续的算法优化和性能提升，我们的系统能够应对各种复杂的网络环境。"
        ]
        random.shuffle(topics)
        content = "".join([f"<p>{t}</p>" for t in topics])
        return f"<div class='{self._rand_str()}'>{content}</div>"

    def _encode_content(self, text):
        """将内容分散编码，降低 XOR 特征码的检测风险"""
        b64_str = base64.b64encode(text.encode()).decode()
        # 将 Base64 字符串拆分为 3-6 个随机片段
        num_chunks = random.randint(3, 6)
        chunk_size = len(b64_str) // num_chunks
        chunks = [b64_str[i:i+chunk_size] for i in range(0, len(b64_str), chunk_size)]
        return chunks

    def _auto_copy_assets(self, soup):
        asset_tags = {'img': 'src', 'link': 'href', 'script': 'src'}
        for tag_name, attr in asset_tags.items():
            for element in soup.find_all(tag_name):
                src = element.get(attr)
                if src and not src.startswith(('http', '//', 'data:')):
                    src_path = os.path.join(os.path.dirname(self.template_path) if os.path.dirname(self.template_path) else ".", src)
                    if os.path.exists(src_path):
                        dest_path = os.path.join(self.output_dir, src)
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        shutil.copy(src_path, dest_path)

    def scramble(self):
        if not os.path.exists(self.template_path):
            print(f"❌ 错误：找不到模板文件 {self.template_path}")
            return

        with open(self.template_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        # 1. 注入白内容（干扰爬虫抓取）
        white_div = BeautifulSoup(self._generate_white_content(), 'html.parser')
        soup.body.insert(0, white_div)

        # 2. 结构混淆
        for tag in soup.find_all(True):
            if tag.has_attr('class'):
                tag['class'] = [self.map.setdefault(c, self._rand_str()) for c in tag['class']]
            if tag.has_attr('id'):
                tag['id'] = self.map.setdefault(tag['id'], self._rand_str())

        # 3. 核心内容隐藏（分散式加载 + 交互触发）
        target_id = self.map.get('main-content')
        if target_id:
            target_node = soup.find(id=target_id)
            if target_node:
                raw_content = "".join([str(x) for x in target_node.contents])
                chunks = self._encode_content(raw_content)
                target_node.clear()

                # 生成随机变量名
                v_names = [self._rand_str(6) for _ in chunks]
                v_final = self._rand_str(5)
                
                # 定义变量定义代码块
                vars_js = "; ".join([f"var {name} = '{val}'" for name, val in zip(v_names, chunks)])
                concat_js = "+".join(v_names)

                js_logic = f"""
                (function(){{
                    {vars_js};
                    var _f = function(){{
                        if(window._done) return;
                        if(navigator.webdriver) return; // 基础对抗
                        var {v_final} = atob({concat_js});
                        document.getElementById('{target_id}').innerHTML = {v_final};
                        window._done = true;
                    }};
                    // 策略 1: 扩大随机延迟范围 (1.5s - 4.5s)
                    setTimeout(_f, {random.randint(1500, 4500)});
                    // 策略 2: 监听真实用户交互行为触发
                    window.addEventListener('mousemove', _f, {{once: true}});
                    window.addEventListener('touchstart', _f, {{once: true}});
                }})();
                """
                script_tag = soup.new_tag("script")
                script_tag.string = js_logic
                soup.body.append(script_tag)

        self._auto_copy_assets(soup)
        save_path = os.path.join(self.output_dir, "index.html")
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print(f"✨ 优化版混淆任务完成！产物路径: {save_path}")

if __name__ == "__main__":
    try:
        LPScramblerProV2("index.html").scramble()
    except Exception as e:
        print(f"❌ 运行错误: {e}")
    input("按回车键退出...")
