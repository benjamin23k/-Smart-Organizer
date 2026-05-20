# 📂 Smart Organizer
[![CI](https://github.com/Benjamin23k/smart-organizer/actions/workflows/ci.yml/badge.svg)](https://github.com/Benjamin23k/smart-organizer/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Organizador inteligente de archivos con **modo pasivo (`run`)**, **modo activo en tiempo real (`watch`)**, reglas declarativas en `TOML`, simulación segura (`--dry-run`) y rollback automático (`--undo`).

## ✨ Características
- ✅ Organización por extensión, tamaño o reglas custom
- 👀 Modo daemon: vigila carpetas y actúa al detectar nuevos archivos
- 🔒 `--dry-run` para ver qué hará sin tocar nada
- ↩️ `--undo` para revertir la última ejecución
- 📦 Configuración limpia y validada con `pydantic`
- 🚀 CI/CD listo con GitHub Actions

## 📦 Instalación
```bash
git clone https://github.com/Benjamin23k/smart-organizer.git
cd smart-organizer
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .




---

`LICENSE`
```bash
cat > LICENSE << 'EOF'
MIT License
Copyright (c) 2026 Benjamin
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
EOF