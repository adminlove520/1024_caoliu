import os


def format_novel(input_file_path, output_file_path):
    """格式化小说文本文件，处理章节标题、对话和段落"""
    try:
        with open(input_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        formatted_lines = []
        in_dialogue = False

        for line in lines:
            stripped_line = line.strip()
            
            if stripped_line.startswith('##'):
                # 章节标题
                formatted_lines.append('\n' + stripped_line + '\n')
                in_dialogue = False
            elif stripped_line.startswith('"') and stripped_line.endswith('"'):
                # 对话行
                if not in_dialogue:
                    formatted_lines.append('\n')
                formatted_lines.append(stripped_line)
                in_dialogue = True
            elif stripped_line:
                # 普通段落
                if in_dialogue:
                    formatted_lines.append('\n')
                formatted_lines.append('    ' + stripped_line)
                in_dialogue = False
            else:
                # 空行
                formatted_lines.append('\n')

        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.writelines(formatted_lines)
        
        print(f"小说格式化成功: {output_file_path}")
        return True
        
    except Exception as e:
        print(f"小说格式化失败: {e}")
        return False


if __name__ == "__main__":
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 使用示例
    input_file_path = os.path.join(current_dir, '[現代奇幻] 淫乱的护士 .txt')
    output_file_path = os.path.join(current_dir, 'formatted_淫乱的护士.txt')
    
    # 检查输入文件是否存在
    if os.path.exists(input_file_path):
        format_novel(input_file_path, output_file_path)
    else:
        print(f"输入文件不存在: {input_file_path}")
        # 提示用户输入文件路径
        custom_input = input("请输入要格式化的小说文件路径 (留空退出): ")
        if custom_input:
            custom_output = custom_input.replace('.txt', '_formatted.txt')
            format_novel(custom_input, custom_output)