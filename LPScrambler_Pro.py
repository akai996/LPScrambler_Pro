import os
import random
import string
import json
import uuid
import shutil
import re
from bs4 import BeautifulSoup

class LPScramblerPro:
    def __init__(self, template_path, output_dir="dist_lp"):
        self.template_path = template_path
        self.output_dir = output_dir
        # 确保输出目录存在 [cite: 1]
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir) # 每次运行清空旧目录，确保不留旧指纹
        os.makedirs(self.output_dir, exist_ok=True)
        self.map = {}

    def _rand_str(self, length=8):
        """生成随机小写字母字符串用于混淆类名和ID [cite: 1]"""
        return ''.join(random.choices(string.ascii_lowercase, k=length))

    def _xor_cipher(self, text):
        """核心多态加密逻辑：采用随机密钥进行异或运算 """
        key = random.randint(10, 250)
        encoded = [ord(c) ^ key for c in text]
        return encoded, key

    def _auto_copy_assets(self, soup):
        """
        自动化资源修复逻辑：
        扫描 HTML 模板中引用的所有本地图片/资源，并自动拷贝到输出目录。
        """
        asset_tags = {'img': 'src', 'link': 'href', 'script': 'src'}
        for tag_name, attr in asset_tags.items():
            for element in soup.find_all(tag_name):
                src = element.get(attr)
                if src and not src.startswith(('http', '//', 'data:')):
                    # 仅处理本地路径
                    src_path = os.path.join(os.path.dirname(self.template_path) if os.path.dirname(self.template_path) else ".", src)
                    if os.path.exists(src_path):
                        dest_path = os.path.join(self.output_dir, src)
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        shutil.copy(src_path, dest_path)
                        print(f"📦 已自动迁移资源: {src}")

    def scramble(self):
        self.map = {} # 确保单次运行指纹唯一 [cite: 1]
        
        if not os.path.exists(self.template_path):
            print(f"❌ 错误：找不到模板文件 {self.template_path}") [cite: 3]
            return

        with open(self.template_path, 'r', encoding='utf-8') as f: [cite: 3]
            soup = BeautifulSoup(f.read(), 'html.parser')

        # 1. 结构指纹随机化 [cite: 4]
        for tag in soup.find_all(True):
            if tag.has_attr('class'): [cite: 4]
                tag['class'] = [self.map.setdefault(c, self._rand_str()) for c in tag['class']]
            if tag.has_attr('id'): [cite: 4]
                tag['id'] = self.map.setdefault(tag['id'], self._rand_str())
            
            # 注入混淆属性 [cite: 5]
            tag[f"data-v-{self._rand_str(5)}"] = ""
            tag[f"data-x-{self._rand_str(4)}"] = self._rand_str(6)

        # 2. 内容层多态加密 [cite: 5]
        target_id = self.map.get('main-content')
        if target_id:
            target_node = soup.find(id=target_id) [cite: 5, 6]
            if target_node:
                raw_content = "".join([str(x) for x in target_node.contents]) [cite: 6]
                encoded_data, key = self._xor_cipher(raw_content)
                target_node.clear() [cite: 6]

                # 随机化 JS 变量名以消除解密指纹 [cite: 6]
                v_data, v_key, v_res = self._rand_str(4), self._rand_str(4), self._rand_str(4)
                
                js_logic = f"""
                (function(){{
                    var {v_data} = {json.dumps(encoded_data)}, {v_key} = {key}; [cite: 7]
                    if(navigator.webdriver) return; 
                    setTimeout(function(){{
                        var {v_res} = {v_data}.map(function(c){{ return String.fromCharCode(c ^ {v_key}); }}).join(''); [cite: 9]
                        document.getElementById('{target_id}').innerHTML = {v_res}; [cite: 9]
                    }}, {random.randint(200, 500)}); 
                }})();
                """
                script_tag = soup.new_tag("script")
                script_tag.string = js_logic
                soup.body.append(script_tag)

        # 3. 样式特征污染 [cite: 11]
        style_tag = soup.new_tag("style")
        style_tag.string = f":root {{ --{self._rand_str()}: {random.randint(1,100)}; }}" [cite: 11]
        soup.head.append(style_tag)

        # 4. 自动化资源拷贝：确保 index.html 引用到的 bg.png, btn.png 等全部同步 [cite: 12]
        self._auto_copy_assets(soup)

        # 5. 文件保存：固定输出为 index.html 方便上传
        save_path = os.path.join(self.output_dir, "index.html")
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        
        print(f"\n✨ 混淆任务圆满完成！")
        print(f"📂 请直接使用目录: {os.path.abspath(self.output_dir)}")

if __name__ == "__main__":
    # 填入您当前的 HTML 文件名
    target_file = "index.html" 
    scrambler = LPScramblerPro(target_file) [cite: 12]
    scrambler.scramble()