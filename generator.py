"""
generator.py

Generates HTML documents from Markdown files.
"""
import os
import re
import json

INPUT_PATH = "markdown/"
OUTPUT_PATH = "html/"

PAGE_TEMPLATE_PATH = "html-templates/page-template.html"
POSTCARD_TEMPLATE_PATH = "html-templates/postcard-template.html"

GAMES_JSON_PATH = "json/games.json"
WEBSITES_JSON_PATH = "json/websites.json"

def convert_markdown_to_html(md_content):
    """
    Returns the result of converting `md_content` to usable HTML.
    """
    reduced_md_content = re.sub(r'\n{2,}', '\n', md_content)

    md_blocks = reduced_md_content.strip().split('\n')

    html_elements = []
    for md_block in md_blocks:
        if md_block.startswith('# '): # header
            header_level = md_block.count("#")
            header_text = md_block.strip("# ")
            if header_level == 1:
                title = header_text

            html_elements.append(f'<h{header_level}>{header_text}</h{header_level}>')
        elif re.match(r'!\[.*\]\(.*\)', md_block): # image
            alt_text = re.search(r'!\[([^\]]*)\]', md_block).group(1)
            img_src = re.search(r'\(([^)]*)\)', md_block).group(1)

            html_elements.append(f'<img class="landscape-image" src="{img_src}" alt="{alt_text}">')
        else: # paragraph
            md_block = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', md_block) # bold text
            md_block = re.sub(r'\*(.*?)\*', r'<i>\1</i>', md_block) # italic text

            # internal links: convert all instances of [text](url) where url ends with "/index.md"
            md_block = re.sub(r'\[([^\]]*)\]\(([^)]*)/index.md\)', r'<a href="\2">\1</a>', md_block)

            # external links: convert all other instances of [text](url)
            md_block = re.sub(r'\[([^\]]*)\]\(([^)]*)\)', r'<a href="\2" target="_blank">\1</a>', md_block)
            
            html_elements.append(f'<p>{md_block}</p>')

    return '\n'.join(html_elements), title

def load_content(file_path):
    """
    Returns a copy of the content of the file at `file_path` as a string.
    """
    with open(file_path, "r") as file:
        return file.read()
    
def load_json_data(json_path):
    """
    Returns a copy of the data from the JSON file at `json_path`.
    """
    with open(json_path, "r") as json_file:
        return json.load(json_file)

def fill_template(template_path, replacement_dict):
    """
    Returns a copy of the content at `template_path` with its placeholders
    replaced as specified in `replacement_dict`. Requires that placeholders
    are in the form `{{ PLACEHOLDER_NAME }}`.
    """
    template_content = load_content(template_path)

    for placeholder_name, replacement in replacement_dict.items():
        template_content = re.sub(r'\{\{\s*' + placeholder_name + r'\s*\}\}', replacement, template_content)
    
    return template_content

def apply_special_page_rules(article_content, trail):
    """
    Returns `article_content` after `trail`-specific rules have been applied
    for designated special pages. Finalizes the HTML content by adding HTML
    elements that have no Markdown equivalents.

    This function can be expanded as necessary to handle all special pages.
    """
    if trail == []:
        article_content = re.sub(r'<h1[^>]*>.*?</h1>', '', article_content)
    elif trail == ["games"]:
        game_data = load_json_data(GAMES_JSON_PATH)

        for game in game_data:
            filled_postcard_template = fill_template(POSTCARD_TEMPLATE_PATH, game)
            article_content += filled_postcard_template
    elif trail == ["websites"]:
        website_data = load_json_data(WEBSITES_JSON_PATH)

        for website in website_data:
            filled_postcard_template = fill_template(POSTCARD_TEMPLATE_PATH, website)
            article_content += filled_postcard_template

    return article_content

def determine_placeholder_replacements(article_content, title, trail):
    """
    Returns a dictionary that maps placeholder names to their replacements.
    """
    replacement_dict = {}
    
    replacement_dict["ARTICLE_CONTENT"] = article_content
    replacement_dict["CANONICAL_PATH"] = "/" + "/".join(trail) if len(trail) > 0 else ""
    replacement_dict["REL"] = len(trail) * "../"
    replacement_dict["PAGE_TITLE"] = title + " — " if len(trail) > 0 else ""

    return replacement_dict

def write_html_content(html_content, path):
    """
    Writes `html_content` to a new HTML file in `path`.
    """
    file_name = "index.html"
    file_path = os.path.join(path, file_name)
    with open(file_path, "w") as html_file:
        html_file.write(html_content)

def generate_html_from_md_file(input_path, output_path):
    """
    Generates HTML content corresponding to the content of the Markdown file
    at `input_path`, and writes it to `output_path` as a new HTML file.
    """
    md_content = load_content(input_path)
        
    article_content, title = convert_markdown_to_html(md_content)
    trail = input_path.split("/")[1:-1]
    article_content = apply_special_page_rules(article_content, trail)

    replacement_dict = determine_placeholder_replacements(article_content, title, trail)
    page_content = fill_template(PAGE_TEMPLATE_PATH, replacement_dict)

    write_html_content(page_content, output_path)

def generate_html_from_folder(input_path, output_path):
    """
    Processes the folder at `input_path` and all of its subfolders
    recursively. Generates a corresponding HTML document for every markdown
    file it finds.

    Essentially, this function copies over the entire folder structure of
    `input_path` to `output_path`, but with every markdown file replaced with
    a corresponding HTML document that is ready for my website to use.
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for entry in os.listdir(input_path):
        entry_path = os.path.join(input_path, entry)

        if os.path.isfile(entry_path) and entry.endswith(".md"):
            generate_html_from_md_file(entry_path, output_path)
        elif os.path.isdir(entry_path):
            new_output_path = os.path.join(output_path, entry)
            generate_html_from_folder(entry_path, new_output_path)

if __name__ == "__main__":
    generate_html_from_folder(INPUT_PATH, OUTPUT_PATH)