from flask import Flask, render_template, request, redirect, url_for
import json
import os
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def home():
    blogs = load_blogs()
    return render_template('home.html', blogs=blogs)

# Función para cargar los blogs desde el archivo JSON
def load_blogs():
    if os.path.exists('static/data.json'):
        with open('static/data.json', 'r', encoding='utf-8') as f:
            return json.load(f)['blogs']
    return []

# Función para guardar los blogs en el archivo JSON
def save_blogs(blogs):
    with open('static/data.json', 'w', encoding='utf-8') as f:
        json.dump({'blogs': blogs}, f, ensure_ascii=False, indent=2)

@app.route('/article/<int:blog_id>')
def article(blog_id):
    blogs = load_blogs()
    blog = next((blog for blog in blogs if blog['id'] == blog_id), None)
    if blog:
        return render_template('index.html', blog=blog)
    else:
        return "Blog not found", 404

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    blogs = load_blogs()
    blog_id = request.args.get('blog_id')

    # Si se pasa un blog_id, estamos editando
    blog_to_edit = next((blog for blog in blogs if str(blog['id']) == blog_id), None) if blog_id else None

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        date = request.form['date']
        topic = request.form['topic']
        content = request.form['content']
        footer = request.form['footer']

        # Procesar el contenido HTML y convertirlo en JSON
        soup = BeautifulSoup(content, 'html.parser')
        content_json = []
        for tag in soup.find_all(['p', 'blockquote', 'ul', 'li', 'strong', 'em']):
            if tag.name == 'p':
                inner_content = []
                for inner_tag in tag.children:
                    if inner_tag.name == 'strong':
                        inner_content.append(f"<strong>{inner_tag.get_text()}</strong>")
                    elif inner_tag.name == 'em':
                        inner_content.append(f"<em>{inner_tag.get_text()}</em>")
                    else:
                        inner_content.append(inner_tag if isinstance(inner_tag, str) else inner_tag.get_text())
                content_json.append("".join(inner_content))
            elif tag.name == 'blockquote':
                content_json.append({
                    "type": "quote",
                    "content": tag.get_text().strip()
                })
            elif tag.name == 'ul':
                items = [li.get_text().strip() for li in tag.find_all('li')]
                content_json.append({
                    "type": "list",
                    "items": items
                })

        if blog_to_edit:
            # Actualizar el blog existente
            blog_to_edit['title'] = title
            blog_to_edit['author'] = author
            blog_to_edit['date'] = date
            blog_to_edit['topic'] = topic
            blog_to_edit['content'] = content_json
            blog_to_edit['footer'] = footer
        else:
            # Crear un nuevo blog
            new_blog = {
                "id": len(blogs) + 1,
                "title": title,
                "date": date,
                "author": author,
                "topic": topic,
                "content": content_json,
                "footer": footer
            }
            blogs.append(new_blog)

        # Guardar los cambios
        save_blogs(blogs)
        return redirect(url_for('home'))

    return render_template('upload.html', blog=blog_to_edit)

if __name__ == '__main__':
    app.run()