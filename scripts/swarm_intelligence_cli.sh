#!/bin/bash
# ==========================================
# Script para iniciar el proyecto swarm-intelligence
# ==========================================

# Cambiar al directorio del proyecto
cd "C:/Users/$USERNAME/Desktop/proyectos/swarm-intelligence" || exit

# Configurar PYTHONPATH
export PYTHONPATH="/c/Users/$USERNAME/Desktop/proyectos/swarm-intelligence:/c/Users/$USERNAME/Desktop/proyectos/eigenlib"

# Activar el entorno virtual
source ".venv/Scripts/activate"

# Cargar variables de entorno desde el archivo .env (ignorando comentarios)
export $(grep -v '^#' .env | xargs)

# Asegurar salida no bufferizada en Python
export PYTHONUNBUFFERED=1

# Ejecutar la CLI de swarmml
python swarmintelligence/modules/cli.py