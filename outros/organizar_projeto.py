import os
import re
import shutil

# Configurações de Nomes
MAIN_FILE = 'main.tex'
DIRS = ['capitulos', 'imagens', 'apendices', 'provas_pdf']

def create_structure():
    """Cria as pastas se não existirem."""
    for d in DIRS:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"Pasta '{d}' criada.")

def move_images():
    """Move arquivos de imagem para a pasta imagens."""
    extensions = ('.png', '.jpg', '.jpeg')
    files = [f for f in os.listdir('.') if f.lower().endswith(extensions)]
    
    for f in files:
        shutil.move(f, os.path.join('imagens', f))
        print(f"Imagem movida: {f}")

def move_pdfs():
    """Move PDFs (provavelmente provas) para a pasta provas_pdf."""
    # Atenção: não mover o output do latex (geralmente main.pdf)
    files = [f for f in os.listdir('.') if f.lower().endswith('.pdf') and f != 'main.pdf']
    
    for f in files:
        shutil.move(f, os.path.join('provas_pdf', f))
        print(f"PDF movido: {f}")

def clean_filename(title):
    """Transforma título da seção em nome de arquivo seguro."""
    # Remove acentos e caracteres especiais básicos
    title = title.lower()
    title = re.sub(r'[áàãâ]', 'a', title)
    title = re.sub(r'[éê]', 'e', title)
    title = re.sub(r'[í]', 'i', title)
    title = re.sub(r'[óõô]', 'o', title)
    title = re.sub(r'[úü]', 'u', title)
    title = re.sub(r'[ç]', 'c', title)
    title = re.sub(r'[^a-z0-9]', '_', title)
    return re.sub(r'_+', '_', title).strip('_')

def parse_tex():
    if not os.path.exists(MAIN_FILE):
        print(f"Erro: {MAIN_FILE} não encontrado.")
        return

    with open(MAIN_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Separar Preâmbulo
    if '\\begin{document}' in content:
        preambulo, body = content.split('\\begin{document}', 1)
        # Adicionar configurações necessárias no preâmbulo
        if '\\graphicspath' not in preambulo:
            preambulo += "\n% Configuração adicionada pelo script\n\\graphicspath{{./imagens/}}\n\\usepackage{pdfpages}\n"
        
        with open('preambulo.tex', 'w', encoding='utf-8') as f:
            f.write(preambulo)
        print("Arquivo 'preambulo.tex' gerado.")
    else:
        print("Erro: \\begin{document} não encontrado.")
        return

    # 2. Processar o Corpo e Dividir por Seções
    # Remove o \end{document} final para processamento
    body = body.replace('\\end{document}', '')
    
    # Regex para encontrar seções: \section{Titulo} ou \section[..]{Titulo}
    # O padrão procura \section, ignora opcional [..], captura o título em {..}
    pattern = re.compile(r'\\section(?:\[.*?\])?\{(.*?)\}', re.DOTALL)
    
    parts = pattern.split(body)
    
    # A primeira parte é o que vem antes da primeira seção (Capa, TOC, Intro)
    intro_content = parts[0].strip()
    new_main_content = "\\input{preambulo}\n\n\\begin{document}\n\n"
    
    if intro_content:
        with open('capitulos/00_intro.tex', 'w', encoding='utf-8') as f:
            f.write(intro_content)
        new_main_content += "\\input{capitulos/00_intro}\n"

    # O resto vem em pares: Título, Conteúdo
    # parts[1] = Título 1, parts[2] = Conteúdo 1, parts[3] = Título 2...
    chapter_count = 1
    
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        # Limpar quebras de linha dentro do título se houver
        title_clean = title.replace('\n', ' ')
        
        text_content = "\\section{" + title + "}\n" + parts[i+1]
        
        filename = f"{chapter_count:02d}_{clean_filename(title_clean)}.tex"
        filepath = os.path.join('capitulos', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text_content)
            
        new_main_content += f"\\input{{capitulos/{filename}}}\n"
        print(f"Capítulo gerado: {filename}")
        chapter_count += 1

    # 3. Adicionar Apêndice e Fechamento no novo Main
    new_main_content += "\n% --- Apêndices ---\n\\appendix\n\\input{apendices/provas_antigas}\n\n"
    new_main_content += "\\end{document}"

    with open('main_organizado.tex', 'w', encoding='utf-8') as f:
        f.write(new_main_content)
    print("Arquivo 'main_organizado.tex' gerado (use este para compilar).")

    # 4. Criar o arquivo de template para as provas
    with open('apendices/provas_antigas.tex', 'w', encoding='utf-8') as f:
        f.write("\\section{Provas Antigas}\n")
        f.write("Os arquivos originais das provas encontram-se na pasta 'provas_pdf'.\n")
        f.write("% Descomente as linhas abaixo para incluir os PDFs se eles existirem:\n")
        f.write("% \\includepdf[pages=-, scale=0.9, pagecommand={}]{provas_pdf/Nome_do_Arquivo.pdf}\n")

if __name__ == "__main__":
    print("Iniciando organização do projeto LaTeX...")
    create_structure()
    move_images()
    move_pdfs()
    parse_tex()
    print("Concluído! Abra 'main_organizado.tex' para compilar.")