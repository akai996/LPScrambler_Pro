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
        """自动迁移真实落地页的素材资源"""
        asset_tags = {'img': 'src', 'link': 'href', 'script': 'src'}
        for tag_name, attr in asset_tags.items():
            for element in soup.find_all(tag_name):
                src = element.get(attr)
                if src and not src.startswith(('http', '//', 'data:')):
                    # 路径净化处理，防止带参数的 URL 导致文件找不到
                    clean_src = urllib.parse.urlparse(src).path
                    src_path = os.path.join(os.path.dirname(self.template_path) if os.path.dirname(self.template_path) else ".", clean_src)
                    if os.path.exists(src_path):
                        dest_path = os.path.join(self.output_dir, clean_src)
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        shutil.copy(src_path, dest_path)

    def _generate_junk_code(self):
        """生成随机的垃圾代码以改变 AST 结构"""
        func_name = self._rand_str(6)
        var_a = self._rand_str(3)
        var_b = self._rand_str(3)
        num_a = random.randint(10, 99)
        num_b = random.randint(10, 99)
        op = random.choice(['+', '-', '*'])
        
        # 生成一段看起来在做计算但实际无用的 JS 函数
        js_code = f"""
        function {func_name}() {{
            var {var_a} = {num_a};
            var {var_b} = {num_b};
            return {var_a} {op} {var_b};
        }}
        """
        return func_name, js_code

    def scramble(self):
        # 0. 基础检查
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

        # 5. 生成随机行为门槛参数
        v_root_id = self._rand_str(10)          # 随机 CSS 容器 ID
        v_min_height = random.randint(205, 235) # 随机页面高度 (205vh - 235vh)
        v_scroll_pos = random.randint(450, 680) # 随机触发滚动位置
        v_delay_time = random.randint(2800, 4800) # 随机解密延迟时间

        # 6. 生成混淆的 JS 变量和逻辑噪声
        v_data, v_key, v_res, v_check = [self._rand_str(6) for _ in range(4)]
        
        # 混淆 DOM 操作相关的变量
        v_dom_target = self._rand_str(5) # 用于存储 document.body
        v_prop_key = self._rand_str(5)   # 用于存储 innerHTML 字符串
        
        # 生成两段垃圾代码 (Logic Noise)
        junk_func_1, junk_code_1 = self._generate_junk_code()
        junk_func_2, junk_code_2 = self._generate_junk_code()

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
        
        /* 注入逻辑噪声：改变 AST 结构 */
        {junk_code_1}
        {junk_code_2}

        function _unlock() {{
            // 环境自检：Webdriver 和 可见性检查
            if (_r || navigator.webdriver || document.visibilityState !== 'visible') return;
            _r = true;
            try {{
                // 解密数据
                var {v_res} = {v_data}.map(function(c){{ return String.fromCharCode(c ^ {v_key}); }}).join('');
                
                // 【核心优化】隐藏 innerHTML 操作
                // 将 'body' 和 'innerHTML' 拆分成字符串碎片进行拼接，规避关键词扫描
                var {v_dom_target} = document['bo' + 'dy'];
                var {v_prop_key} = 'inner' + 'HTML';
                
                // 执行 DOM 注入 (模拟懒加载行为)
                {v_dom_target}[{v_prop_key}] = {v_res};
                
                // 调用垃圾代码，增加逻辑混淆度
                {junk_func_1}();
                
                window.scrollTo(0, 0);
            }} catch(e) {{ console.clear(); }}
        }}

        function {v_check}() {{
            // 每次检查滚动时调用垃圾代码，制造不规律的 CPU 占用特征
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
        
        print(f"✅ V5.3 终极多态版 (AST增强+DOM隐形) 构建完成！")
        print(f"📊 特征值: 高度{v_min_height}vh | 阈值{v_scroll_pos}px | 延迟{v_delay_time}ms")
        print(f"📂 产物路径: {os.path.abspath(self.output_dir)}")
        print(f"👉 注意: 请手动将白页所需的 CSS/图片文件夹拷贝到产物目录中。")

if __name__ == "__main__":
    print("=== LPScrambler Pro V5.3 (Ultimate AST+DOM Stealth) ===")
    
    # 自动识别环境，如果是 CI 环境则不等待输入
    is_ci = os.environ.get('GITHUB_ACTIONS') == 'true'
    
    if is_ci:
        w_name = "white_template.html"
        r_name = "index.html"
    else:
        w_name = input("白页文件名 (默认 white_template.html): ").strip() or "white_template.html"
        r_name = input("真页文件名 (默认 index.html): ").strip() or "index.html"

    try:
        LPScramblerProV5Ultimate(template_path=r_name, white_path=w_name).scramble()
    except Exception as e:
        print(f"❌ 运行失败: {e}")
    
    if not is_ci:
        input("\n任务结束，按回车退出...")
