# DJ_ToDo

Um simples aplicativo de To-Do desenvolvido em Django com um pipeline de CI/CD.

## 🚀 Tecnologias
- Django
- flake8
- black
- bandit
- SQLite
- Poetry
- GitHub Actions

## 🔧 Como rodar o projeto
```bash
git clone https://github.com/joaopflausino/DJ_ToDo.git
cd DJ_ToDo
poetry install
poetry run python manage.py migrate
poetry run python manage.py runserver
```

## 🔄 CI/CD
O projeto usa **GitHub Actions** para:
- Executar testes automatizados
- Verificar qualidade do código
- Implantar em ambiente configurado
