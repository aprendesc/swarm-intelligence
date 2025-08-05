import os

folders = [
    "data",
    "doc",
    "img",
    "models",
    "scripts",
    "swarmintelligence",
    "wandb"
]

files_with_content = {
            ".gitignore": "*.pyc\n__pycache__/\n.env\n*.log\n",
            "__init__.py": "# Inicializador de paquete\n",
            "changelog": "# Changelog\n\n## [0.1.0] - Proyecto inicial\n",
            "Dockerfile": ("FROM python:3.10-slim\n"
                "WORKDIR /app\n"
                "COPY . .\n"
                "RUN pip install --no-cache-dir -r requirements.txt\n"
                "CMD [\"python\", \"scripts/main.py\"]\n"),
            "MANIFEST": "include README.md\ninclude requirements.txt\n",
            "pyproject": ("[project]\n"
                "name = \"mi_proyecto\"\n"
                "version = \"0.1.0\"\n"
                "description = \"Proyecto de ejemplo con swarm intelligence\"\n"
                "authors = [\n"
                "    {name = \"Tu Nombre\", email = \"tu@email.com\"}\n"
                "]\n"),
            "README": "# Proyecto de Swarm Intelligence\n\nEste proyecto implementa algoritmos de inteligencia de enjambre.\n",
            "requirements": "# Requisitos del proyecto\nnumpy\npandas\nmatplotlib\n"
        }

def main():
    #CREATE LOCAL FOLDERS
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

    #CREATE LOCAL FILES
    for file_name, content in files_with_content.items():
        if not os.path.exists(file_name):
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(content)

    #CREATE REPOSITORY

    #INSTALL REQUIREMENTS

    #TERRAFORM CLOUD

if __name__ == "__main__":
    main()

