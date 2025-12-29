import os
import random
import string
import json
import shutil
from bs4 import BeautifulSoup

class LPScramblerProV5:
    def __init__(self, template_path="index.html", white_path="white_template.html", output_dir="dist_lp"):
        self.template_path = template_path
        self.white_path = white_path
        self.output_dir = output_dir
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        self.map = {}

    def _rand_str(self, length=8):
        """生成随机小写字母字符串用于混淆类名和ID"""
        return ''.join(random.choices(string.ascii_lowercase, k=length))

    def _xor_cipher(self, text):
        """核心多态加密逻辑：采用随机密钥进行异或运算"""
        key = random.randint(10, 250)
        encoded = [ord(c) ^ key for c in text]
        return encoded, key

    def _auto_copy_assets(self, soup):
        """扫描并自动迁移真实落地页引用的本地图片及样式资源"""
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
        # 确保单次运行指纹唯一
        if not os.path.exists(self.template_path) or not os.path.exists(self.white_path):
            print(f"❌ 错误：文件缺失。")
            return

        # 1. 提取白内容外壳
        with open(self.white_path, 'r', encoding='utf-8') as f:
            white_soup = BeautifulSoup(f.read(), 'html.parser')
            white_body = "".join([str(x) for x in white_soup.body.contents]) if white_soup.body else ""
            white_title = white_soup.title.string if white_soup.title else "Official Site"

        # 2. 提取并加密真实落地页
        with open(self.template_path, 'r', encoding='utf-8') as f:
            real_soup = BeautifulSoup(f.read(), 'html.parser')
            self._auto_copy_assets(real_soup)

        # 混淆 ID 与 Class 特征
        for tag in real_soup.find_all(True):
            if tag.has_attr('class'):
                tag['class'] = [self.map.setdefault(c, self._rand_str()) for c in tag['class']]
            if tag.has_attr('id'):
                tag['id'] = self.map.setdefault(tag['id'], self._rand_str())

        # 3. 执行 V5 XOR 多态加密
        real_content = "".join([str(x) for x in real_soup.body.contents]) if real_soup.body else ""
        encoded_data, key = self._xor_cipher(real_content)

        # 4. 构建 V5 壳页面（全指纹消除解密逻辑）
        # 随机化 JS 变量名以消除解密逻辑的特征码
        v_data, v_key, v_res, v_trig, v_check = [self._rand_str(6) for _ in range(5)]
        
        final_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{white_title}</title>
    <style>
        body {{ margin: 0; padding: 0; font-family: sans-serif; }}
        #sc-root-v5 {{ position: relative; min-height: 210vh; background: #fff; }}
    </style>
</head>
<body>
    <div id="sc-root-v5">
        {white_body}
    </div>

    <script>
    (function(){{
        var {v_data} = {json.dumps(encoded_data)}, {v_key} = {key};
        var _r = false, _t = false;

        function _execute() {{
            if (_r || navigator.webdriver || document.visibilityState !== 'visible') return;
            _r = true;
            try {{
                var {v_res} = {v_data}.map(function(c){{ return String.fromCharCode(c ^ {v_key}); }}).join('');
                document.body.innerHTML = {v_res};
                window.scrollTo(0, 0);
            }} catch(e) {{ }}
        }}

        function {v_check}() {{
            if (!_t && window.scrollY > 500) {{
                _t = true;
                setTimeout(_execute, 3200);
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
        print(f"✅ V5 尊享版指纹全消除混淆完成！")
        print(f"📂 产物路径: {os.path.abspath(self.output_dir)}")

if __name__ == "__main__":
    print("=== LPScrambler Pro V5 (Premium Edition) ===")
    w_name = input("白页模板名 (默认 white_template.html): ").strip() or "white_template.html"
    r_name = input("真页文件名 (默认 index.html): ").strip() or "index.html"
    try:
        LPScramblerProV5(template_path=r_name, white_path=w_name).scramble()
    except Exception as e:
        print(f"❌ 运行失败: {e}")
    input("\n任务结束，按回车退出...")
