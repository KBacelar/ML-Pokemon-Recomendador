# Wrapper para executar a avaliação a partir da raiz do projeto

import subprocess
import sys
import os

script_dir = os.path.join(os.path.dirname(__file__), 'avaliacao', 'scripts')
script_path = os.path.join(script_dir, 'executar_avaliacao_completa.py')

resultado = subprocess.run([sys.executable, script_path], cwd=script_dir)
sys.exit(resultado.returncode)
