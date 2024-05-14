import os
import pandas as pd
from PIL import Image
import xml.etree.ElementTree as ET

# Definir os caminhos dos ficheiros
#o utilizador deve colocar o caminho na diretoria até ao ficheiro pretendido
kgml = '/home/duartevelho1/Projeto/resources_directory/kc_kgmls/ko00680.xml'
keggcharter_input_tsv = '/home/duartevelho1/Projeto/keggcharter_input.tsv'
potential_png1 = '/home/duartevelho1/Projeto/first_time_running_KC/maps/potential_Methane metabolism.png'
diferential_png2 = '/home/duartevelho1/Projeto/first_time_running_KC/maps/differential_Methane metabolism.png'

# Carregar o ficheiro KGML
tree = ET.parse(kgml)
root = tree.getroot()

# Carregar o ficheiro TSV
dados_tsv = pd.read_csv(keggcharter_input_tsv, delimiter='\t')

# Carregar as imagens PNG
imagem1 = Image.open(potential_png1)
imagem2 = Image.open(diferential_png2)

# Agora você pode manipular esses dados e imagens conforme necessário no seu código.
# Imprimir uma parte do ficheiro TSV
print(dados_tsv)

# Mostrar uma das imagens
imagem2.show()
