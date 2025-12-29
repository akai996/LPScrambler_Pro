import os
import random
import string
import json
import shutil
import urllib.parse
from bs4 import BeautifulSoup

class LPScramblerProV5Ultimate:
    def __init__(self, template_path="index.html", white_path="white_template.html", output_dir="dist_lp"):
        self.template_path = template_path
        self.white_path = white_path
        self.output_dir = output_dir
        # 确保输出目录干净
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        self.map = {}

    def _rand_str(self, length=8):
        """生成随机小写字母字符串用于混淆"""
        return ''.join(random.choices(string.ascii_lowercase, k=length))

    def _xor_cipher(self, text):
        """核心多态加密：随机密钥异或运算"""
        key = random.randint(10, 250)
        encoded = [ord(c) ^ key for c in text]
        return encoded, key

    def _auto_copy_assets(self, soup):
        """自动迁移素材资源"""
        asset_tags = {'img': 'src', 'link': 'href', 'script': 'src'}
        for tag_name, attr in asset_tags.items():
            for element in soup.find_all(tag_name):
                src = element.get(attr)
                if src and not src.startswith(('http', '//', 'data:')):
                    # 路径净化处理
                    clean_src = urllib.parse.urlparse(src).path
                    src_path = os.path.join(os.path.dirname(self.template_path) if os.path.dirname(self.template_path) else ".", clean_src)
                    if os.path.exists(src_path):
                        dest_path = os.path.join(self.output_dir, clean_src)
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        shutil.copy(src_path, dest_path)

    def scramble(self):
        if not os.path.exists(self.template_path) or not os.path.exists(self.white_path):
            print(f"❌ 错误：文件缺失。请确保 {self.template_path} 和 {self.white_path} 存在。")
            return

        # 1. 提取白内容外壳
        with open(self.white_path, 'r', encoding='utf-8') as f:
            white_soup = BeautifulSoup(f.read(), 'html.parser')
            white_body = "".join([str(x) for x in white_soup.body.contents]) if white_soup.body else ""
            white_title = white_soup.title.string if white_soup.title else "Official Site"

        # 2. 提取并处理真实落地页
        with open(self.template_path, 'r', encoding='utf-8') as f:
            real_soup = BeautifulSoup(f.read(), 'html.parser')
            self._auto_copy_assets(real_soup)

        # 3. 混淆真页 ID 与 Class
        for tag in real_soup.find_all(True):
            if tag.has_attr('class'):
                tag['class'] = [self.map.setdefault(c, self._rand_str()) for c in tag['class']]
            if tag.has_attr('id'):
                tag['id'] = self.map.setdefault(tag['id'], self._rand_str())

        # 4. 执行异或加密
        real_content = "".join([str(x) for x in real_soup.body.contents]) if real_soup.body else ""
        encoded_data, key = self._xor_cipher(real_content)

        # 5. 生成随机行为门槛参数 (核心增强)
        v_root_id = self._rand_str(10)          # 随机 CSS 容器 ID
        v_min_height = random.randint(205, 235) # 随机页面高度 (205vh - 235vh)
        v_scroll_pos = random.randint(450, 680) # 随机触发滚动位置
        v_delay_time = random.randint(2800, 4800) # 随机解密延迟时间 (2.8s - 4.8s)

        # 随机化 JS 变量名
        v_data, v_key, v_res, v_check, v_timer = [self._rand_str(6) for _ in range(5)]
        
        final_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1.0">
    <title>{white_title}</title>
    <style>
        body {{ margin: 0; padding: 0; font-family: sans-serif; }}
        #{v_root_id} {{ position: relative; min-height: {v_min_height}vh; background: #fff; overflow-x: hidden; }}
    </style>
</head>
<body>
    <div id="{v_root_id}">
        {white_body}
    </div>

    <script>
    (function(){{
        var {v_data} = {json.dumps(encoded_data)}, {v_key} = {key};
        var _r = false, _t = false;

        function _unlock() {{
            if (_r || navigator.webdriver || document.visibilityState !== 'visible') return;
            _r = true;
            try {{
                var {v_res} = {v_data}.map(function(c){{ return String.fromCharCode(c ^ {v_key}); }}).join('');
                document.body.innerHTML = {v_res};
                window.scrollTo(0, 0);
            }} catch(e) {{ console.clear(); }}
        }}

        function {v_check}() {{
            if (!_t && window.scrollY > {v_scroll_pos}) {{
                _t = true;
                setTimeout(_unlock, {v_delay_time});
            }}
        }}

        window.addEventListener('scroll', {v_check});
        window.addEventListener('touchmove', {v_check});
    }})();
    </script>
</body>
</html>"""

        with open(os.path.join(self.output_dir, "index.html"), 'w', encoding='utf-8') as f:
            f.write(final_html)
        
        print(f"✅ V5.2 终极版构建完成！")
        print(f"📊 动态高度: {v_min_height}vh | 触发位置: {v_scroll_pos}px | 延迟: {v_delay_time}ms")
        print(f"📂 产物路径: {os.path.abspath(self.output_dir)}")

if __name__ == "__main__":
    print("=== LPScrambler Pro V5.2 (Ultimate Multi-Morph Edition) ===")
    w_name = input("白页文件名 (默认 white_template.html): ").strip() or "white_template.html"
    r_name = input("真页文件名 (默认 index.html): ").strip() or "index.html"
    try:
        LPScramblerProV5Ultimate(template_path=r_name, white_path=w_name).scramble()
    except Exception as e:
        print(f"❌ 运行失败: {e}")
    input("\n任务结束，按回车退出...")