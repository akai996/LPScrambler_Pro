import os
import random
import string
import json
import shutil
import urllib.parse
from bs4 import BeautifulSoup

class LPScramblerProV5Guard:
    def __init__(self, template_path="index.html", white_path="white_template.html", output_dir="dist_lp", traffic_param=""):
        self.template_path = template_path
        self.white_path = white_path
        self.output_dir = output_dir
        self.traffic_param = traffic_param
        
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        self.map = {}

    def _rand_str(self, length=8):
        return ''.join(random.choices(string.ascii_lowercase, k=length))

    def _xor_cipher(self, text):
        key = random.randint(10, 250)
        encoded = [ord(c) ^ key for c in text]
        return encoded, key

    # 【修复版】增加 base_path 参数，准确查找素材源路径
    def _auto_copy_assets(self, soup, base_filename):
        asset_tags = {'img': 'src', 'link': 'href', 'script': 'src'}
        base_dir = os.path.dirname(base_filename) if os.path.dirname(base_filename) else "."
        
        for tag_name, attr in asset_tags.items():
            for element in soup.find_all(tag_name):
                src = element.get(attr)
                if src and not src.startswith(('http', '//', 'data:')):
                    # 解析路径（去掉参数等）
                    clean_src = urllib.parse.urlparse(src).path
                    src_path = os.path.join(base_dir, clean_src)
                    
                    if os.path.exists(src_path):
                        dest_path = os.path.join(self.output_dir, clean_src)
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        shutil.copy(src_path, dest_path)

    def _generate_junk_code(self):
        func_name = self._rand_str(6)
        var_a, var_b = self._rand_str(3), self._rand_str(3)
        num_a, num_b = random.randint(10, 99), random.randint(10, 99)
        op = random.choice(['+', '-', '*'])
        js_code = f"""
        function {func_name}() {{
            var {var_a} = {num_a}; var {var_b} = {num_b};
            return {var_a} {op} {var_b};
        }}
        """
        return func_name, js_code

    def scramble(self):
        # 0. 基础检查
        if not os.path.exists(self.template_path) or not os.path.exists(self.white_path):
            print(f"❌ 错误：文件缺失。请确保 {self.template_path} 和 {self.white_path} 都在根目录下。")
            return

        # 1. 处理白页 (修复版：保留样式 + 正确复制素材)
        with open(self.white_path, 'r', encoding='utf-8') as f:
            white_soup = BeautifulSoup(f.read(), 'html.parser')
            # 【调用修复】传入 self.white_path
            self._auto_copy_assets(white_soup, self.white_path)
            
            white_body = "".join([str(x) for x in white_soup.body.contents]) if white_soup.body else ""
            white_title = white_soup.title.string if white_soup.title else "Official Site"
            
            # 提取 Head 中的 CSS/JS
            white_head_extras = ""
            if white_soup.head:
                for tag in white_soup.head.contents:
                    if tag.name in ['link', 'style', 'script', 'meta'] and tag.name != 'title':
                        white_head_extras += str(tag)

        # 2. 处理真页
        with open(self.template_path, 'r', encoding='utf-8') as f:
            real_soup = BeautifulSoup(f.read(), 'html.parser')
            # 【调用修复】传入 self.template_path
            self._auto_copy_assets(real_soup, self.template_path)

        # 3. 混淆 ID/Class
        for tag in real_soup.find_all(True):
            if tag.has_attr('class'):
                tag['class'] = [self.map.setdefault(c, self._rand_str()) for c in tag['class']]
            if tag.has_attr('id'):
                tag['id'] = self.map.setdefault(tag['id'], self._rand_str())

        # 4. 加密内容
        real_content = "".join([str(x) for x in real_soup.body.contents]) if real_soup.body else ""
        encoded_data, key = self._xor_cipher(real_content)

        # 加密 URL 参数
        has_param_check = False
        param_data_enc, param_key_enc = [], 0
        if self.traffic_param:
            has_param_check = True
            param_data_enc, param_key_enc = self._xor_cipher(self.traffic_param)

        # 5. 生成变量
        v_root_id = self._rand_str(10)
        v_min_height = random.randint(205, 235)
        v_scroll_pos = random.randint(450, 680)
        v_delay_time = random.randint(2800, 4800)
        v_data, v_key, v_res, v_check = [self._rand_str(6) for _ in range(4)]
        v_dom_target, v_prop_key = self._rand_str(5), self._rand_str(5)
        v_p_data, v_p_key, v_p_str = self._rand_str(5), self._rand_str(5), self._rand_str(5)

        junk_func_1, junk_code_1 = self._generate_junk_code()
        junk_func_2, junk_code_2 = self._generate_junk_code()

        url_check_logic = ""
        if has_param_check:
            url_check_logic = f"""
            var {v_p_data} = {json.dumps(param_data_enc)};
            var {v_p_key} = {param_key_enc};
            var {v_p_str} = {v_p_data}.map(function(c){{ return String.fromCharCode(c ^ {v_p_key}); }}).join('');
            if (window.location.href.indexOf({v_p_str}) === -1) {{ return; }}
            """

        final_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1.0">
    <title>{white_title}</title>
    {white_head_extras}
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
        
        {junk_code_1}
        {junk_code_2}

        function _unlock() {{
            if (_r || navigator.webdriver || document.visibilityState !== 'visible') return;
            {url_check_logic}
            _r = true;
            try {{
                var {v_res} = {v_data}.map(function(c){{ return String.fromCharCode(c ^ {v_key}); }}).join('');
                var {v_dom_target} = document['bo' + 'dy'];
                var {v_prop_key} = 'inner' + 'HTML';
                {v_dom_target}[{v_prop_key}] = {v_res};
                {junk_func_1}();
                window.scrollTo(0, 0);
            }} catch(e) {{ console.clear(); }}
        }}

        function {v_check}() {{
            {junk_func_2}();
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
        
        print(f"✅ V5.6 流量卫士版 (素材路径修复) 构建完成！")
        print(f"📂 产物路径: {os.path.abspath(self.output_dir)}")
        print(f"👉 请注意：dist_lp 只有 index.html 是正常的，因为它已经包含了白页。")

if __name__ == "__main__":
    print("=== LPScrambler Pro V5.6 (Asset Fix) ===")
    is_ci = os.environ.get('GITHUB_ACTIONS') == 'true'
    
    if is_ci:
        w_name = "white_template.html"
        r_name = "index.html"
        t_param = "gclid"
    else:
        w_name = input("白页文件名 (默认 white_template.html): ").strip() or "white_template.html"
        r_name = input("真页文件名 (默认 index.html): ").strip() or "index.html"
        t_param = input("请输入允许参数 (如 gclid): ").strip()

    try:
        LPScramblerProV5Guard(template_path=r_name, white_path=w_name, traffic_param=t_param).scramble()
    except Exception as e:
        print(f"❌ 运行失败: {e}")
    
    if not is_ci:
        input("\n任务结束，按回车退出...")
