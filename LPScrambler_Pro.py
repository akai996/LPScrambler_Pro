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
        # 确保输出目录存在，每次运行清空旧目录，确保不留旧指纹 [cite: 1]
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir) 
        os.makedirs(self.output_dir, exist_ok=True)
        self.map = {}

    def _rand_str(self, length=8):
        """生成随机小写字母字符串用于混淆类名和ID [cite: 2]"""
        return ''.join(random.choices(string.ascii_lowercase, k=length))

    def _xor_cipher(self, text):
        """核心多态加密逻辑：采用随机密钥进行异或运算 [cite: 2]"""
        key = random.randint(10, 250)
        encoded = [ord(c) ^ key for c in text]
        return encoded, key

    def _auto_copy_assets(self, soup):
        """
        自动化资源修复逻辑：
        扫描 HTML 模板中引用的所有本地图片/资源，并自动拷贝到输出目录 [cite: 3]。
        """
        asset_tags = {'img': 'src', 'link': 'href', 'script': 'src'}
        for tag_name, attr in asset_tags.items():
            for element in soup.find_all(tag_name):
                src = element.get(attr)
                if src and not src.startswith(('http', '//', 'data:')):
                    # 仅处理本地路径 [cite: 4]
                    src_path = os.path.join(os.path.dirname(self.template_path) if os.path.dirname(self.template_path) else ".", src)
                    if os.path.exists(src_path):
                        dest_path = os.path.join(self.output_dir, src)
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True) # [cite: 5]
                        shutil.copy(src_path, dest_path)
                        print(f"📦 已自动迁移资源: {src}")

    def scramble(self):
        self.map = {} # 确保单次运行指纹唯一 [cite: 6]
        
        if not os.path.exists(self.template_path):
            print(f"❌ 错误：找不到模板文件 {self.template_path}") # [cite: 6]
            return

        with open(self.template_path, 'r', encoding='utf-8') as f: # [cite: 6]
            soup = BeautifulSoup(f.read(), 'html.parser')

        # 1. 结构指纹随机化 [cite: 6]
        for tag in soup.find_all(True):
            if tag.has_attr('class'): # [cite: 6]
                tag['class'] = [self.map.setdefault(c, self._rand_str()) for c in tag['class']] # [cite: 7]
            if tag.has_attr('id'): # [cite: 7]
                tag['id'] = self.map.setdefault(tag['id'], self._rand_str())
            
            # 注入混淆属性 [cite: 7, 8]
            tag[f"data-v-{self._rand_str(5)}"] = ""
            tag[f"data-x-{self._rand_str(4)}"] = self._rand_str(6)

        # 2. 内容层多态加密 [cite: 8]
        target_id = self.map.get('main-content')
        if target_id:
            target_node = soup.find(id=target_id) # [cite: 8]
            if target_node:
                raw_content = "".join([str(x) for x in target_node.contents]) # [cite: 8]
                encoded_data, key = self._xor_cipher(raw_content) # [cite: 9]
                target_node.clear() # [cite: 9]

                # 随机化 JS 变量名以消除解密指纹 [cite: 9]
                v_data, v_key, v_res = self._rand_str(4), self._rand_str(4), self._rand_str(4)
                
                js_logic = f"""
                (function(){{
                    var {v_data} = {json.dumps(encoded_data)}, {v_key} = {key};
                    if(navigator.webdriver) return; // 
                    setTimeout(function(){{
                        var {v_res} = {v_data}.map(function(c){{ return String.fromCharCode(c ^ {v_key}); }}).join(''); // [cite: 12]
                        document.getElementById('{target_id}').innerHTML = {v_res}; // [cite: 12]
                    }}, {random.randint(200, 500)}); // [cite: 12]
                }})();
                """
                script_tag = soup.new_tag("script")
                script_tag.string = js_logic
                soup.body.append(script_tag)

        # 3. 样式特征污染 [cite: 13, 14]
        style_tag = soup.new_tag("style")
        style_tag.string = f":root {{ --{self._rand_str()}: {random.randint(1,100)}; }}" 
        soup.head.append(style_tag)

        # 4. 自动化资源拷贝 [cite: 14]
        self._auto_copy_assets(soup)

        # 5. 文件保存
        save_path = os.path.join(self.output_dir, "index.html")
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        
        print(f"\n✨ 混淆任务圆满完成！")
        print(f"📂 请直接使用目录: {os.path.abspath(self.output_dir)}")

if __name__ == "__main__":
    try:
        # [cite: 15]
        target_file = "index.html" 
        scrambler = LPScramblerPro(target_file)
        scrambler.scramble()
    except Exception as e:
        print(f"\n❌ 运行发生致命错误: {e}")
    
    # 核心防闪退逻辑：等待用户输入
    print("\n" + "="*30)
    input("程序执行完毕，按回车键(Enter)退出...")
