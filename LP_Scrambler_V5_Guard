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
        self.traffic_param = traffic_param  # URL 白名单参数
        
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
                    clean_src = urllib.parse.urlparse(src).path
                    src_path = os.path.join(os.path.dirname(self.template_path) if os.path.dirname(self.template_path) else ".", clean_src)
                    if os.path.exists(src_path):
                        dest_path = os.path.join(self.output_dir, clean_src)
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        shutil.copy(src_path, dest_path)

    def _generate_junk_code(self):
        """生成随机 AST 噪声代码"""
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
            print(f"❌ 错误：文件缺失。")
            return

        # 1. 处理白页 (含素材迁移)
        with open(self.white_path, 'r', encoding='utf-8') as f:
            white_soup = BeautifulSoup(f.read(), 'html.parser')
            self._auto_copy_assets(white_soup) # 【双向迁移】防止白页样式崩坏
            white_body = "".join([str(x) for x in white_soup.body.contents]) if white_soup.body else ""
            white_title = white_soup.title.string if white_soup.title else "Official Site"

        # 2. 处理真页
        with open(self.template_path, 'r', encoding='utf-8') as f:
            real_soup = BeautifulSoup(f.read(), 'html.parser')
            self._auto_copy_assets(real_soup)

        # 3. 混淆 ID/Class
        for tag in real_soup.find_all(True):
            if tag.has_attr('class'):
                tag['class'] = [self.map.setdefault(c, self._rand_str()) for c in tag['class']]
            if tag.has_attr('id'):
                tag['id'] = self.map.setdefault(tag['id'], self._rand_str())

        # 4. 加密内容
        real_content = "".join([str(x) for x in real_soup.body.contents]) if real_soup.body else ""
        encoded_data, key = self._xor_cipher(real_content)

        # 【新增】加密 URL 白名单参数 (防止源码泄露 "gclid")
        has_param_check = False
        param_data_enc, param_key_enc = [], 0
        if self.traffic_param:
            has_param_check = True
            param_data_enc, param_key_enc = self._xor_cipher(self.traffic_param)

        # 5. 生成随机参数
        v_root_id = self._rand_str(10)
        v_min_height = random.randint(205, 235)
        v_scroll_pos = random.randint(450, 680)
        v_delay_time = random.randint(2800, 4800)

        # 6. 生成 JS 变量
        v_data, v_key, v_res, v_check = [self._rand_str(6) for _ in range(4)]
        v_dom_target, v_prop_key = self._rand_str(5), self._rand_str(5)
        
        # 参数校验相关的变量名
        v_p_data, v_p_key, v_p_str = self._rand_str(5), self._rand_str(5), self._rand_str(5)

        junk_func_1, junk_code_1 = self._generate_junk_code()
        junk_func_2, junk_code_2 = self._generate_junk_code()

        # 构建 URL 检查的 JS 逻辑
        url_check_logic = ""
        if has_param_check:
            url_check_logic = f"""
            var {v_p_data} = {json.dumps(param_data_enc)};
            var {v_p_key} = {param_key_enc};
            // 运行时解密参数名 (如 "gclid")
            var {v_p_str} = {v_p_data}.map(function(c){{ return String.fromCharCode(c ^ {v_p_key}); }}).join('');
            
            // 【核心卫士】检查 URL 是否包含该参数
            if (window.location.href.indexOf({v_p_str}) === -1) {{
                return; // 如果没有参数，直接终止，不做任何事情
            }}
            """

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
        
        {junk_code_1}
        {junk_code_2}

        function _unlock() {{
            if (_r || navigator.webdriver || document.visibilityState !== 'visible') return;
            
            // 【流量来源校验区域】
            {url_check_logic}

            _r = true;
            try {{
                var {v_res} = {v_data}.map(function(c){{ return String.fromCharCode(c ^ {v_key}); }}).join('');
                
                // 隐形 DOM 注入
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
        
        print(f"✅ V5.4 流量卫士版 (URL白名单+隐身) 构建完成！")
        if self.traffic_param:
            print(f"🛡️ 流量锁已开启: 仅允许带 [{self.traffic_param}] 参数的访问触发解密。")
        else:
            print(f"⚠️ 警告: 未设置流量参数，任何滚动行为都将触发解密。")
        print(f"📂 产物路径: {os.path.abspath(self.output_dir)}")

if __name__ == "__main__":
    print("=== LPScrambler Pro V5.4 (Traffic Guard Edition) ===")
    
    is_ci = os.environ.get('GITHUB_ACTIONS') == 'true'
    
    if is_ci:
        w_name = "white_template.html"
        r_name = "index.html"
        t_param = "gclid" # CI 环境下默认锁定 gclid
    else:
        w_name = input("白页文件名 (默认 white_template.html): ").strip() or "white_template.html"
        r_name = input("真页文件名 (默认 index.html): ").strip() or "index.html"
        print("-" * 30)
        print("【流量锁设置】")
        print("输入 'gclid'  -> 仅允许谷歌广告点击流量")
        print("输入 'key=123' -> 仅允许特定后缀访问")
        print("直接回车     -> 不限制 (不推荐)")
        t_param = input("请输入允许参数: ").strip()

    try:
        LPScramblerProV5Guard(template_path=r_name, white_path=w_name, traffic_param=t_param).scramble()
    except Exception as e:
        print(f"❌ 运行失败: {e}")
    
    if not is_ci:
        input("\n任务结束，按回车退出...")
