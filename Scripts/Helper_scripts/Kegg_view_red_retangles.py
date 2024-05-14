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

def criar_image_maps(coordenadas, imagem="./KEGGCharter/original_kegg_map.png", arquivo_saida="image_maps.html", titulo_imagem="Methane metabolism"):
    def coords_to_div(coords):
        x = int(coords['x'])*2.08
        y = int(coords['y'])*2.08
        width = int(coords['width'])*2.08
        height = int(coords['height'])*2.08
        return f"<div style='position: absolute; left: {x}px; top: {y}px; width: {width}px; height: {height}px; background-color: tomato; opacity: 0.5;'></div>"

    html = f"""<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <title>Image Maps</title>
    <style>
        #image-container {{
            position: relative;
            width: fit-content;
        }}
        #image-container img {{
            display: block;  /* This ensures there's no gap under the image */
        }}
    </style>
</head>
<body>
    <h2>{titulo_imagem}</h2>
    <div id="image-container">
        <img src='{imagem}' usemap='#potentialMap' alt='{titulo_imagem}'>
        <map name='potentialMap'>
"""

    for coord in coordenadas:
        html += coords_to_div(coord)
        area_str = f"{int(coord['x'])},{int(coord['y'])},{int(coord['x']) + int(coord['width'])},{int(coord['y']) + int(coord['height'])}"
        html += f'            <area shape="rect" coords="{area_str}" href="your_link_here" alt="Description here">\n'

    html += "        </map>\n    </div>\n</body>\n</html>"

    with open(arquivo_saida, 'w') as file:
        file.write(html)

    print(f"HTML com mapas de imagem e quadrados coloridos gerado com sucesso e salvo como {arquivo_saida}!")



# Execução do script
if __name__ == '__main__':
    caminho_kgml = './resources_directory/kc_kgmls/ko00680.xml'
    root = carregar_kgml(caminho_kgml)
    retangulos = extrair_elementos_graficos(root)
    criar_image_maps(retangulos, imagem="./maps/differential_ko00680.png", arquivo_saida="image_maps.html", titulo_imagem="Methane Metabolism Map")
    