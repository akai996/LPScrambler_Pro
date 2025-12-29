import os
import random
import string
import json
import base64
import shutil
from bs4 import BeautifulSoup

class LPScramblerProV4:
    def __init__(self, template_path="index.html", white_path="white_template.html", output_dir="dist_lp"):
        self.template_path = template_path
        self.white_path = white_path
        self.output_dir = output_dir
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        self.map = {}

    def _rand_str(self, length=8):
        return ''.join(random.choices(string.ascii_lowercase, k=length))

    def _encode_content(self, text):
        b64_str = base64.b64encode(text.encode()).decode()
        chunks = []
        i = 0
        while i < len(b64_str):
            size = random.randint(15, 25) # 稍微调大分片以平衡性能
            chunks.append(b64_str[i:i+size])
            i += size
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
        if not os.path.exists(self.template_path) or not os.path.exists(self.white_path):
            print(f"❌ 错误：文件缺失。")
            return

        with open(self.white_path, 'r', encoding='utf-8') as f:
            white_soup = BeautifulSoup(f.read(), 'html.parser')
            white_body = "".join([str(x) for x in white_soup.body.contents]) if white_soup.body else ""
            white_title = white_soup.title.string if white_soup.title else "Information"

        with open(self.template_path, 'r', encoding='utf-8') as f:
            real_soup = BeautifulSoup(f.read(), 'html.parser')
            self._auto_copy_assets(real_soup)

        for tag in real_soup.find_all(True):
            if tag.has_attr('class'):
                tag['class'] = [self.map.setdefault(c, self._rand_str()) for c in tag['class']]
            if tag.has_attr('id'):
                tag['id'] = self.map.setdefault(tag['id'], self._rand_str())

        real_content = "".join([str(x) for x in real_soup.body.contents]) if real_soup.body else ""
        data_chunks = self._encode_content(real_content)

        js_chunks = json.dumps(data_chunks)
        reveal_func = f"reveal_{self._rand_str(5)}"
        scroll_handler = f"onScroll_{self._rand_str(5)}"
        
        final_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{white_title}</title>
    <style>
        body {{ margin: 0; padding: 0; font-family: -apple-system, sans-serif; }}
        #root-container {{ position: relative; min-height: 200vh; }} /* 增加高度以允许滚动 */
    </style>
</head>
<body>
    <div id="root-container">
        {white_body}
    </div>

    <script>
    (function(){{
        var _chunks = {js_chunks};
        var _isRun = false;
        var _triggered = false;

        function {reveal_func}() {{
            if (_isRun || navigator.webdriver) return; // 再次校验环境指纹
            _isRun = true;
            try {{
                var _raw = atob(_chunks.join(''));
                document.body.innerHTML = _raw;
                window.scrollTo(0, 0);
            }} catch(e) {{ console.clear(); }}
        }}

        function {scroll_handler}() {{
            // 门槛 1: 滚动高度必须超过 500 像素
            if (!_triggered && window.scrollY > 500) {{
                _triggered = true;
                // 门槛 2: 达到滚动高度后，必须停留 3 秒以上（模拟深度阅读行为）
                setTimeout({reveal_func}, 3000); 
            }}
        }}

        // 仅监听滚动事件，废弃自动计时器触发，强制物理交互
        window.addEventListener('scroll', {scroll_handler});
        
        // 手机端触摸滑动支持
        window.addEventListener('touchmove', {scroll_handler});

    }})();
    </script>
</body>
</html>"""

        with open(os.path.join(self.output_dir, "index.html"), 'w', encoding='utf-8') as f:
            f.write(final_html)
        print(f"✅ 深度行为混淆完成！")
        print(f"📂 产物路径: {os.path.abspath(self.output_dir)}")

if __name__ == "__main__":
    print("=== LPScrambler Pro V4 (深度行为触发版) ===")
    cw = input("白页模板名 (默认 white_template.html): ").strip() or "white_template.html"
    cr = input("真实落地页文件名 (默认 index.html): ").strip() or "index.html"
    try:
        LPScramblerProV4(template_path=cr, white_path=cw).scramble()
    except Exception as e:
        print(f"❌ 运行失败: {e}")
    input("按回车退出...")
