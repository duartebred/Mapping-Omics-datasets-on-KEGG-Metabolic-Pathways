##Nesta abordagem, tentamos trabalhar com o React diretamente no HTML gerado pelo seu script Python


def carregar_kgml(caminho_kgml : str) -> None:
    """
    Loads a KGML file and returns the root of the XML document.

    Parameters
    ----------
    caminho_kgml : str
        The path to the KGML file.

    Returns
    -------
        The root of the XML document.
    """

    import xml.etree.ElementTree as ET
    tree = ET.parse(caminho_kgml)
    root = tree.getroot()
    return root

def extrair_titulo_pathway(caminho_kgml: str) -> str:
    """
    Extrai o título da pathway de um arquivo KGML.

    Parameters
    ----------
    caminho_kgml : str
        O caminho para o arquivo KGML.

    Returns
    -------
    str
        O título da pathway.
    """

    import xml.etree.ElementTree as ET

    # Carregar o arquivo KGML
    tree = ET.parse(caminho_kgml)
    root = tree.getroot()
    
    # Extrair o atributo 'title' do elemento raiz 'pathway'
    titulo_pathway = root.get('title', 'Título não encontrado')
    return titulo_pathway


def extrair_elementos_graficos_com_id(root, tipo : str = 'rectangle') -> list[dict[str, str]]:
    """
    Extracts graphic elements of a specific type from the root XML document and includes their ID.

    Parameters
    ----------
    root 
        The root of the XML document.

    tipo : str
        Type of graphic element to extract (default is 'rectangle').

    Returns
    -------
    list[dict[str, str]]
        List of dictionaries containing data on graphic elements including their IDs.
    """

    elementos_id = []
    # Encontrar todos os elementos de tipo 'entry' que têm um filho 'graphics' do tipo especificado
    for entry in root.findall(".//entry"):
        graphics = entry.find(".//graphics")
        if graphics is not None and graphics.get('type') == tipo:
            dados_elemento = {
                'id': entry.get('id'),  # Pega o 'id' do elemento 'entry'
                'x': graphics.get('x'),
                'y': graphics.get('y'),
                'width': graphics.get('width'),
                'height': graphics.get('height')
            }
            elementos_id.append(dados_elemento)
    
    return elementos_id


def imprimir_elementos_graficos(caminho_kgml : str) -> None:
    """
    Loads a KGML file, extracts rectangular graphic elements and prints them.

    Parameters
    ----------
    caminho_kgml : str 
        The path to the KGML file.

    Returns
    -------
    None
    """

    root = carregar_kgml(caminho_kgml)
    retangulos = extrair_elementos_graficos_com_id(root)
    for ret in retangulos:
        print(ret)
    print("Total de elementos gráficos:", len(retangulos))


def criar_pagina_detalhe(id):
    """
    Cria uma página HTML individual para um ID específico que se parece com o esboço fornecido.

    Parameters
    ----------
    id : str
        O ID do elemento.
    """
    detalhe_html = f"""
    <!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='UTF-8'>
        <title>Detalhes do Elemento {id}</title>
    </head>
    <body>
        <button onclick="location.href='http://example.com/KEGG';">Link KEGG</button>
        <h1>MAP 00680</h1>
        <div style="border: 2px solid black; height: 300px; width: 300px; margin: 20px auto;">
            Detalhes para ID {id}
        </div>
    </body>
    </html>
    """
    with open(f"detalhes_{id}.html", 'w') as file:
        file.write(detalhe_html)


def criar_image_maps(coordenadas : list[dict[str, str]], imagem : str = "./KEGGCharter/original_kegg_map.png", arquivo_saida : str = f"image_maps.html", titulo_imagem : str = "Methane metabolism Map") -> None:
    """
    Cria um arquivo HTML com mapas de imagem com base em coordenadas especificadas.
    
    Parameters
    ----------
    coordenadas : list[dict[str, str]]
        Creates an HTML file with image maps based on specified coordinates.

    imagem : str
        Path to the background image.

    arquivo_saida : str 
        Path of the output file where the HTML will be saved.

    titulo_imagem : str
        Title of the image to be included in the HTML.
    
    Returns
    -------
    None
    """

    def coords_to_area(coords : dict[str, str]) -> str:
        """
        Converts coordinates of a graphic element into an area string for use in HTML image maps.
        
        Parameters
        ----------
        coords : dict[str, str]
            Dictionary with the element's 'x', 'y', 'width' and 'height' coordinates.
        
        Returns
        -------
        str 
            String formatted for use in the 'coords' attribute of an HTML <area> tag.
        """

        x1 = int(coords['x'])*2.1
        y1 = int(coords['y'])*2.1
        x2 = x1 + int(coords['width'])*2.2
        y2 = y1 + int(coords['height'])*2.2
        return f"{x1},{y1},{x2},{y2}"

    html = f"<!DOCTYPE html>\n<html lang='en'>\n<head>\n    <meta charset='UTF-8'>\n    <title>{titulo_imagem}</title>\n</head>\n<body>\n    <h2>{titulo_imagem}</h2>\n    <img src='{imagem}' usemap='#potentialMap' alt='{titulo_imagem}'>\n    <map name='potentialMap'>\n"
    
    for coord in coordenadas:
        id = coord['id']
        criar_pagina_detalhe(id)  # Cria a página de detalhes com o layout especificado
        link = f"detalhes_{id}.html"  # Atualiza o link para a nova página de detalhes
        area_str = coords_to_area(coord)
        html += f'        <area shape="rect" coords="{area_str}" href="{link}" target="_blank" alt="Element ID {id}">\n'
    
    html += "</map>\n</body>\n</html>"
    
    with open(arquivo_saida, 'w') as file:
        file.write(html)

    print(f"HTML com mapas de imagem gerado com sucesso e salvo como {arquivo_saida}!")



# Execução do script
if __name__ == '__main__':
    caminho_kgml = './resources_directory/kc_kgmls/ko00680.xml'
    root = carregar_kgml(caminho_kgml)
    titulo_pathway = extrair_titulo_pathway(caminho_kgml)
    retangulos = extrair_elementos_graficos_com_id(root)
    criar_image_maps(retangulos, imagem="./KEGGCharter/original_kegg_map.png", arquivo_saida=f"image_maps_{titulo_pathway}.html", titulo_imagem=f"{titulo_pathway} Map")
    
