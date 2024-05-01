def carregar_kgml(caminho_kgml):
    import xml.etree.ElementTree as ET
    tree = ET.parse(caminho_kgml)
    root = tree.getroot()
    return root

def extrair_elementos_graficos(root, tipo='rectangle'):
    elementos = []
    for entry in root.findall(".//graphics"):
        if entry.get('type') == tipo:
            dados_elemento = {
                'x': entry.get('x'),
                'y': entry.get('y'),
                'width': entry.get('width'),
                'height': entry.get('height')
            }
            elementos.append(dados_elemento)
    return elementos

def imprimir_elementos_graficos(caminho_kgml):
    root = carregar_kgml(caminho_kgml)
    retangulos = extrair_elementos_graficos(root)
    for ret in retangulos:
        print(ret)
    print("Total de elementos gráficos:", len(retangulos))

def criar_image_maps(coordenadas, imagem="./first_time_running_KC/maps/differential_Methane metabolism.png", arquivo_saida="image_maps.html", titulo_imagem = "Methane metabolism"):
    def coords_to_area(coords):
        x1 = int(coords['x'])
        y1 = int(coords['y'])
        x2 = x1 + int(coords['width'])
        y2 = y1 + int(coords['height'])
        return f"{x1},{y1},{x2},{y2}"

    html = f"<!DOCTYPE html>\\n<html lang='en'>\\n<head>\\n    <meta charset='UTF-8'>\\n    <title>Image Maps</title>\\n</head>\\n<body>\\n    <h2>{titulo_imagem}</h2>\\n    <img src='{imagem}' usemap='#potentialMap' alt='{titulo_imagem}'>\\n    <map name='potentialMap'>\\n"

    for coord in coordenadas:
        area_str = coords_to_area(coord)
        html += f'        <area shape="rect" coords="{area_str}" href="your_link_here" alt="Description here">\\n'

    html += "</map>\\n</body>\\n</html>"

    with open(arquivo_saida, 'w') as file:
        file.write(html)

    print(f"HTML com mapas de imagem gerado com sucesso e salvo como {arquivo_saida}!")


# Execução do script
if __name__ == '__main__':
    caminho_kgml = './resources_directory/kc_kgmls/ko00680.xml'
    root = carregar_kgml(caminho_kgml)
    retangulos = extrair_elementos_graficos(root)
    criar_image_maps(retangulos, imagem="put.png", arquivo_saida="image_maps.html", titulo_imagem="Methane Metabolism Map")