import xml.etree.ElementTree as ET

# Carregar o ficheiro KGML
caminho_kgml = '/home/duartevelho1/Projeto/resources_directory/kc_kgmls/ko00680.xml'
tree = ET.parse(caminho_kgml)
root = tree.getroot()

# Encontrar e extrair informações dos retângulos
retangulos = []
for entry in root.findall(".//graphics"):
    if entry.get('type') == 'rectangle':
        dados_retangulo = {
            'x': entry.get('x'),
            'y': entry.get('y'),
            'width': entry.get('width'),
            'height': entry.get('height')
        }
        retangulos.append(dados_retangulo)

# Imprimir os dados de cada retângulo
for ret in retangulos:
    print(ret)

print(len(retangulos))