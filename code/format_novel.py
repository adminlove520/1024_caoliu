def format_novel(input_file_path, output_file_path):
    with open(input_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    formatted_lines = []
    in_dialogue = False

    for line in lines:
        stripped_line = line.strip()
        print(f"Processing line: '{line}'")  # Debugging line
        
        if stripped_line.startswith('##'):
            # Chapter heading
            formatted_lines.append('\n' + stripped_line + '\n')
            in_dialogue = False
            print(f"Chapter heading: {stripped_line}")  # Debugging line
        elif stripped_line.startswith('"') and stripped_line.endswith('"'):
            # Dialogue line
            if not in_dialogue:
                formatted_lines.append('\n')
            formatted_lines.append(stripped_line)
            in_dialogue = True
            print(f"Dialogue line: {stripped_line}")  # Debugging line
        elif stripped_line:
            # Normal paragraph
            if in_dialogue:
                formatted_lines.append('\n')
            formatted_lines.append('    ' + stripped_line)
            in_dialogue = False
            print(f"Normal paragraph: {stripped_line}")  # Debugging line
        else:
            # Blank line
            formatted_lines.append('\n')
            print("Blank line")  # Debugging line

    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.writelines(formatted_lines)

# 使用示例
input_file_path = 'd:\\safeProject\\setuBot\\code\\[現代奇幻] 淫乱的护士 .txt'
output_file_path = 'd:\\safeProject\\setuBot\\code\\formatted_淫乱的护士.txt'
format_novel(input_file_path, output_file_path)