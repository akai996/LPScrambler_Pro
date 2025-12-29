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
        # 确保输出目录干净，指纹唯一
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        self.map = {}

    def _rand_str(self, length=8):
        """生成随机混淆字符串"""
        return ''.join(random.choices(string.ascii_lowercase, k=length))

    def _encode_content(self, text):
        """将内容切分为 15-25 字符的分片，兼顾熵值混淆与解析速度"""
        b64_str = base64.b64encode(text.encode()).decode()
        chunks = []
        i = 0
        while i < len(b64_str):
            size = random.randint(15, 25)
            chunks.append(b64_str[i:i+size])
            i += size
        return chunks

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
        # 1. 验证输入文件
        if not os.path.exists(self.template_path) or not os.path.exists(self.white_path):
            print(f"❌ 错误：找不到文件。请确保 {self.template_path} 和 {self.white_path} 在当前文件夹。")
            return

        # 2. 提取白内容（用于初审的外壳）
        with open(self.white_path, 'r', encoding='utf-8') as f:
            white_soup = BeautifulSoup(f.read(), 'html.parser')
            white_body = "".join([str(x) for x in white_soup.body.contents]) if white_soup.body else ""
            white_title = white_soup.title.string if white_soup.title else "Official Site"

        # 3. 提取并处理真实落地页
        with open(self.template_path, 'r', encoding='utf-8') as f:
            real_soup = BeautifulSoup(f.read(), 'html.parser')
            self._auto_copy_assets(real_soup)

        # 混淆真实页面的 ID 与 Class
        for tag in real_soup.find_all(True):
            if tag.has_attr('class'):
                tag['class'] = [self.map.setdefault(c, self._rand_str()) for c in tag['class']]
            if tag.has_attr('id'):
                tag['id'] = self.map.setdefault(tag['id'], self._rand_str())

        # 提取真实内容并分片加密
        real_content = "".join([str(x) for x in real_soup.body.contents]) if real_soup.body else ""
        data_chunks = self._encode_content(real_content)

        # 4. 构建终极壳页面（深度行为触发逻辑）
        js_chunks = json.dumps(data_chunks)
        reveal_func = f"load_{self._rand_str(5)}"
        scroll_handler = f"check_{self._rand_str(5)}"
        
        final_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{white_title}</title>
    <style>
        body {{ margin: 0; padding: 0; font-family: -apple-system, sans-serif; }}
        #sc-root {{ position: relative; min-height: 200vh; background: #fff; }} /* 强制高度支持滚动 */
    </style>
</head>
<body>
    <div id="sc-root">
        {white_body}
    </div>

    <script>
    (function(){{
        var _c = {js_chunks};
        var _isRun = false;
        var _triggered = false; 
        var _triggerPos = 500; 

        function {reveal_func}() {{
            // 最终环境自检：防止在自动化驱动下释放内容
            if (_isRun || navigator.webdriver) return;
            _isRun = true;
            try {{
                var _h = atob(_c.join(''));
                document.body.innerHTML = _h;
                window.scrollTo(0, 0);
            }} catch(e) {{ console.clear(); }}
        }}

        function {scroll_handler}() {{
            // 行为门槛：滚动超过500px且仅触发一次计时器
            if (!_triggered && window.scrollY > _triggerPos) {{
                _triggered = true;
                // 深度阅读模拟：滚动达标后停留3秒才解密
                setTimeout({reveal_func}, 3000);
            }}
        }}

        // 仅通过物理滚动/触摸触发
        window.addEventListener('scroll', {scroll_handler});
        window.addEventListener('touchmove', {scroll_handler}); 
    }})();
    </script>
</body>
</html>"""

        # 5. 保存产物
        output_file = os.path.join(self.output_dir, "index.html")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_html)
        
        print(f"\n✨ 混淆任务圆满完成！")
        print(f"📄 使用白内容: {self.white_path}")
        print(f"📄 使用落地页: {self.template_path}")
        print(f"📂 产物目录: {os.path.abspath(self.output_dir)}")

if __name__ == "__main__":
    print("=== LPScrambler Pro V4 (Final Deep Reading Edition) ===")
    
    # 支持自定义文件名的交互输入
    w_name = input("请输入白内容文件名 (默认 white_template.html): ").strip() or "white_template.html"
    r_name = input("请输入真实落地页文件名 (默认 index.html): ").strip() or "index.html"
    
    # 自动容错补全后缀
    if not os.path.exists(w_name) and not w_name.endswith(".html"): w_name += ".html"
    if not os.path.exists(r_name) and not r_name.endswith(".html"): r_name += ".html"

    try:
        LPScramblerProV4(template_path=r_name, white_path=w_name).scramble()
    except Exception as e:
        print(f"❌ 运行发生致命错误: {e}")
    
    print("\n" + "="*40)
    input("执行完毕，请前往 dist_lp 目录查看。按回车退出...")
