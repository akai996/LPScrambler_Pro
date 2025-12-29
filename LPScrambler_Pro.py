import os
import random
import string
import json
import base64
import shutil
from bs4 import BeautifulSoup

class LPScramblerProV3:
    def __init__(self, template_path="index.html", white_path="white_template.html", output_dir="dist_lp"):
        self.template_path = template_path
        self.white_path = white_path
        self.output_dir = output_dir
        # 确保输出目录存在
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        self.map = {}

    def _rand_str(self, length=8):
        """生成随机小写字母字符串用于混淆类名和ID"""
        return ''.join(random.choices(string.ascii_lowercase, k=length))

    def _encode_content(self, text):
        """将真实 HTML 进行 Base64 分片，降低加密指纹的统计熵值"""
        b64_str = base64.b64encode(text.encode()).decode()
        chunks = []
        i = 0
        while i < len(b64_str):
            size = random.randint(10, 20)
            chunks.append(b64_str[i:i+size])
            i += size
        return chunks

    def _auto_copy_assets(self, soup):
        """自动扫描并迁移真实落地页引用的本地素材"""
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
        # 验证文件是否存在
        if not os.path.exists(self.template_path):
            print(f"❌ 错误：找不到真实落地页 {self.template_path}")
            return
        if not os.path.exists(self.white_path):
            print(f"❌ 错误：找不到自定义白页模板 {self.white_path}")
            return

        # 1. 提取自定义白内容（初审爬虫抓取的合规内容）
        with open(self.white_path, 'r', encoding='utf-8') as f:
            white_soup = BeautifulSoup(f.read(), 'html.parser')
            white_body = "".join([str(x) for x in white_soup.body.contents]) if white_soup.body else ""
            white_title = white_soup.title.string if white_soup.title else "Official Information"

        # 2. 提取并处理真实内容
        with open(self.template_path, 'r', encoding='utf-8') as f:
            real_soup = BeautifulSoup(f.read(), 'html.parser')
            self._auto_copy_assets(real_soup)

        # 混淆真实页面的 class/id 指纹
        for tag in real_soup.find_all(True):
            if tag.has_attr('class'):
                tag['class'] = [self.map.setdefault(c, self._rand_str()) for c in tag['class']]
            if tag.has_attr('id'):
                tag['id'] = self.map.setdefault(tag['id'], self._rand_str())

        real_content = "".join([str(x) for x in real_soup.body.contents]) if real_soup.body else ""
        data_chunks = self._encode_content(real_content)

        # 3. 构建终极壳页面
        js_chunks = json.dumps(data_chunks)
        trigger_func = f"init_{self._rand_str(5)}"
        
        final_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{white_title}</title>
    <style>
        body {{ margin: 0; padding: 0; font-family: -apple-system, sans-serif; }}
        #root-container {{ position: relative; min-height: 100vh; }}
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

        function {trigger_func}() {{
            // 1. 硬件级避让检测
            if (_isRun || navigator.webdriver) return;
            _isRun = true;

            // 2. 模拟异步数据加载延迟
            setTimeout(function(){{
                try {{
                    var _raw = atob(_chunks.join(''));
                    document.body.innerHTML = _raw;
                    window.scrollTo(0, 0);
                }} catch(e) {{ console.clear(); }}
            }}, {random.randint(800, 2500)});
        }}

        // 3. 多重交互触发对抗静态沙箱
        window.addEventListener('mousemove', {trigger_func}, {{once: true}});
        window.addEventListener('scroll', {trigger_func}, {{once: true}});
        window.addEventListener('touchstart', {trigger_func}, {{once: true}});
        
        // 4. 后备定时触发
        setTimeout({trigger_func}, {random.randint(6000, 10000)});
    }})();
    </script>
</body>
</html>"""

        with open(os.path.join(self.output_dir, "index.html"), 'w', encoding='utf-8') as f:
            f.write(final_html)
        print(f"✅ 混淆成功！")
        print(f"📄 使用白页模板: {self.white_path}")
        print(f"📂 产物路径: {os.path.abspath(self.output_dir)}")

if __name__ == "__main__":
    print("=== LPScrambler Pro V3 (自定义版) ===")
    
    # 获取用户输入的文件名，设置默认值
    custom_white = input("请输入白页模板文件名 (默认 white_template.html): ").strip()
    if not custom_white:
        custom_white = "white_template.html"
    
    custom_real = input("请输入真实落地页文件名 (默认 index.html): ").strip()
    if not custom_real:
        custom_real = "index.html"

    try:
        scrambler = LPScramblerProV3(template_path=custom_real, white_path=custom_white)
        scrambler.scramble()
    except Exception as e:
        print(f"❌ 运行失败: {e}")
    
    print("\n" + "="*30)
    input("任务结束，按回车退出...")
