##Nesta abordagem, tentamos trabalhar com o React diretamente no HTML gerado pelo seu script Python
import json
import csv
import xml.etree.ElementTree as ET

def load_json_to_dict(filepath: str) -> dict[str, any]:
    """
    Carrega um arquivo JSON a partir de um caminho especificado e retorna o conteúdo como um dicionário.

    Parameters
    ----------
    filepath : str
        O caminho para o ficheiro JSON.

    Returns
    -------
    dict
        O conteúdo do ficheiro JSON como um dicionário.
    """
    with open(filepath, 'r') as file:
        data = json.load(file)
    return data


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

    tree = ET.parse(caminho_kgml)
    root = tree.getroot()
    
    titulo_pathway = root.get('title', 'Título não encontrado')
    return titulo_pathway


def extrair_numero_pathway(caminho_kgml: str) -> str:
    """
    Extrai o número da pathway de um arquivo KGML.

    Parameters
    ----------
    caminho_kgml : str
        O caminho para o arquivo KGML.

    Returns
    -------
    str
        O número da pathway.
    """

    tree = ET.parse(caminho_kgml)
    root = tree.getroot()
    
    numero_pathway = root.get('number', 'Número não encontrado')
    return numero_pathway


def extrair_elementos_graficos_com_id(root, tipo: str = 'rectangle') -> list[dict[str, str]]:
    """
    Extrai elementos gráficos de um tipo específico do documento XML da raiz e inclui seus IDs, 
    coordenadas e um link associado a cada ID.

    Parameters
    ----------
    root : xml.etree.ElementTree.Element
        A raiz do documento XML.

    tipo : str
        Tipo de elemento gráfico a ser extraído (o padrão é 'rectangle').

    Returns
    -------
    list[dict[str, str]]
        Lista de dicionários que contém dados sobre os elementos gráficos, incluindo os seus IDs,
        as coordenadas (x, y, width, height) e um link associado.
    """
    elementos_id = []
    
    for entry in root.findall(".//entry"):
        graphics = entry.find(".//graphics")
        
        if graphics is not None and graphics.get('type') == tipo:
            link_suffix = entry.get('link')
            if link_suffix and not link_suffix.startswith('http'):
                link = f"https://www.kegg.jp/dbget-bin/www_bget?{link_suffix}"
            else:
                link = link_suffix  
            
            dados_elemento = {
                'id': entry.get('id'),  
                'x': graphics.get('x'),
                'y': graphics.get('y'),
                'width': graphics.get('width'),
                'height': graphics.get('height'),
                'link': link
            }
            elementos_id.append(dados_elemento)
    
    return elementos_id


def enriquecer_elementos_graficos(elementos_graficos_com_id: list[dict[str, str]], caminho_tsv: str, caminho_json_taxon: str, caminho_json_kos: str) -> list[dict[str, str]]:
    """
    Enriquece os elementos gráficos com os dados provenientes de um arquivo TSV e dois arquivos JSON.

    Parameters
    ----------
    elementos_graficos : list[dict[str, str]]
        Lista de dicionários com dados sobre os elementos gráficos.

    caminho_tsv : str
        Caminho para o arquivo TSV que contém mapeamentos de ID para nomes (EC ou KO).

    caminho_json_taxon : str
        Caminho para o arquivo JSON que contém mapeamentos de ID para taxon.

    caminho_json_kos : str
        Caminho para o arquivo JSON que contém mapeamentos de ID para KOs.

    Returns
    -------
    list[dict[str, str]]
        Lista de dicionários com dados sobre os elementos gráficos enriquecidos com informações adicionais.
    """
    id_to_name = {}
    with open(caminho_tsv, 'r') as file:
        reader = csv.reader(file, delimiter='\t')
        next(reader)  
        for linha in reader:
            if linha:
                id_to_name[linha[0]] = linha[1]

    id_to_taxon = load_json_to_dict(caminho_json_taxon)
    id_to_kos = load_json_to_dict(caminho_json_kos)

    for elemento in elementos_graficos_com_id:
        elemento_id = elemento['id']
        elemento['EC_KO'] = id_to_name.get(elemento_id, ["Unknown"])
        elemento['taxon'] = id_to_taxon.get(elemento_id, ["Unknown"])
        elemento['kos'] = id_to_kos.get(elemento_id, ["Unknown"])

    return elementos_graficos_com_id


def imprimir_elementos_graficos(caminho_kgml : str) -> None:
    """
    Carrega um ficheiro KGML, extrai elementos gráficos rectangulares e imprime-os.

    Parameters
    ----------
    caminho_kgml : str 
        O caminho para o ficheiro KGML.

    Returns
    -------
    None
    """

    root = carregar_kgml(caminho_kgml)
    retangulos = extrair_elementos_graficos_com_id(root)
    for ret in retangulos:
        print(ret)
    print("Total de elementos gráficos:", len(retangulos))


def ler_arquivos_tsv(caminho_differential : str, caminho_potential : str) -> dict:
    """
    Carrega dados de dois arquivos TSV e retorna um dicionário com identificadores únicos 
    como chaves e as respectivas taxas como valores. Se um identificador
    aparecer em ambos os arquivos, o valor do segundo arquivo substituirá o do primeiro.

    Parameters
    ----------
    caminho_differential : str
        O caminho para o arquivo TSV que contém os dados diferenciais.
    caminho_potential : str
        O caminho para o arquivo TSV que contém os dados potenciais.

    Returns
    -------
    dict
        Um dicionário onde cada chave é um identificador (int) dos dados e o valor é a taxa (str) associada.
    """
    dados = {}
    
    with open(caminho_differential, 'r') as file:
        reader = csv.reader(file, delimiter='\t')
        next(reader, None)  
        for linha in reader:
            if linha:
                box_id = int(linha[0])  
                taxa = linha[1]         
                dados[box_id] = taxa
    
    with open(caminho_potential, 'r') as file:
        reader = csv.reader(file, delimiter='\t')
        next(reader, None)  
        for linha in reader:
            if linha:
                box_id = int(linha[0])  
                taxa = linha[1]         
                dados[box_id] = taxa  

    return dados


def criar_caixas_coloridas(id : str, colors_dict : dict[str, list[str]]) -> str:
    """
    Gera uma string HTML que representa várias subcaixas alinhadas horizontalmente,
    cada uma colorida conforme especificado no dicionário para um ID específico.
    As subcaixas são criadas com uma borda preta para melhor visualização.

    Parameters
    ----------
        id : str 
            O identificador que aponta para a lista de cores no dicionário.

        colors_dict : dict[str, list[str]] 
            Um dicionário mapeando identificadores para listas de strings de cores.

    Returns
    -------
        str 
            Uma string HTML que representa uma linha de subcaixas coloridas, cada uma com borda preta.
    """
    colors = colors_dict.get(str(id), ["#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"])  # Cor padrão se não houver entrada
    # Criação das caixas com borda preta
    boxes_html = ''.join([
        f'<div style="background-color: {color}; width: 25%; height: 50px; display: inline-block; border: 1px solid black;"></div>'
        for color in colors
    ])
    return f'<div style="width: 100%; height: 50px; display: flex;">{boxes_html}</div>'


def criar_pagina_detalhe(id : str, link : str, ec_ko : str, KO : list[str], Taxon : list[str], colors_dict : dict[str, list[str]]):
    """
    Cria uma página HTML detalhada para um ID específico com base nos dados fornecidos e nas cores definidas no dicionário.
    
    Parameters
    ----------
        id : str 
            O identificador do elemento, usado para criar caixas coloridas específicas e nomear o arquivo HTML.
        link : str
            O URL para o qual o botão na página HTML deve redirecionar.
        ec_ko : str 
            O número EC ou KO que será usado como título da página.
        KO : list[str] 
            Lista de números K que serão exibidos na página.
        Taxon : list[str] 
            Lista de nomes de taxons associados que serão exibidos na página.
        colors_dict : dict[str, list[str]] 
            Dicionário mapeando identificadores para listas de cores, usado para colorir caixas na página.

    Effects
    -------
        Cria um arquivo HTML na diretoria atual com o nome baseado no pathway e no ID fornecido.
    """
    numero_pathway = extrair_numero_pathway(caminho_kgml)
    titulo_pathway = extrair_titulo_pathway(caminho_kgml)
    color_boxes = criar_caixas_coloridas(id, colors_dict)

    imagem_url_differential = "./KEGGCharter/first_time_running_KC/maps/differential_ko00680_legend.png"
    imagem_url_potential = "./KEGGCharter/first_time_running_KC/maps/potential_ko00680_legend.png"

    detalhe_html = f"""
    <!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='UTF-8'>
        <title>EC_Number {ec_ko}</title>
        <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 50px;
            background-color: #f4f4f4;
        }}
        .grid-container {{
            display: grid;
            grid-template-columns: 5fr 5fr;
            gap: 0px 10px;
        }}
        #botao {{
            grid-row-start: 1;
            grid-row-end: 1;
            grid-column-start: 1;
            grid-column-end: 1;
        }}
        #titulo {{
            grid-row-start: 2;
            grid-row-end: 2;
            grid-column-start: 1;
            grid-column-end: 5;
        }}
        #information {{
            grid-row-start: 5;
            grid-row-end: 5;
            grid-column-start: 1;
            grid-column-end: 4;
        }}
        #img_differential {{
            grid-row-start: 3;
            grid-row-end: 5;
            grid-column-start: 5;
            grid-column-end: 5;
        }}
        #img_potential {{
            grid-row-start: 5;
            grid-row-end: 5;
            grid-column-start: 5;
            grid-column-end: 5;
        }}
        #box_differential {{
            grid-row-start: 3;
            grid-row-end: 3;
            grid-column-start: 1;
            grid-column-end: 5;
        }}
        #ECNumber {{
            grid-row-start: 1;
            grid-row-end: 1;
            grid-column-start: 5;
            grid-column-end: 5;
        }}
        </style>
    </head>
    <body>
        <div class="grid-container">
            <div class="grid-item" id = "botao">
                <button onclick="location.href='{link}';">Link KEGG</button>
            </div>
            <div class="grid-item" id = "titulo">
                <h1>{titulo_pathway} - MAP {numero_pathway}</h1>
            </div>
            <div class="grid-item" id = "information">
                Box ID - {id} <br />
                K numbers - {', '.join(KO)} <br />
                Taxon - {', '.join(Taxon)}
            </div>
            <div class="grid-item" id = "img_differential">
                <img src="{imagem_url_differential}" alt="Color Legend">
            </div>
            <div class="grid-item" id = "img_potential">
                <img src="{imagem_url_potential}" alt="Color Legend">
            </div>
            <div class="grid-item" id = "box_differential">
                {color_boxes} 
            </div>
            <div class="grid-item" id = "ECNumber">
                EC Number - {ec_ko}
            </div>
        </div>
    </body>
    </html>
    """
    with open(f"Map{numero_pathway}_Box{id}.html", 'w') as file:
        file.write(detalhe_html)


def criar_image_maps(coordenadas : list[dict[str, str]], imagem : str = "./KEGGCharter/original_kegg_map.png", arquivo_saida : str = f"image_maps.html", titulo_imagem : str = "Methane metabolism Map", colors_dict : str = './KEGGCharter/info/ko00680_boxes2quant_colors.json') -> None:
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

    colors_dict : str
    
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

    
    numero_pathway = extrair_numero_pathway(caminho_kgml)
    html = f"<!DOCTYPE html>\n<html lang='en'>\n<head>\n    <meta charset='UTF-8'>\n    <title>{titulo_imagem}</title>\n</head>\n<body>\n    <h2>{titulo_imagem}</h2>\n    <img src='{imagem}' usemap='#potentialMap' alt='{titulo_imagem}'>\n    <map name='potentialMap'>\n"
    
    for coord in coordenadas:
        id = coord['id']
        link = coord['link']
        ec_ko = coord['EC_KO']
        KO = coord['kos']
        Taxon = coord['taxon']
        criar_pagina_detalhe(id, link, ec_ko, KO, Taxon, colors_dict)  
        area_str = coords_to_area(coord)
        html += f'        <area shape="rect" coords="{area_str}" href="Map{numero_pathway}_Box{id}.html" target="_blank" alt="Element ID {id}">\n'
    
    html += "</map>\n</body>\n</html>"
    
    with open(arquivo_saida, 'w') as file:
        file.write(html)

    print(f"HTML com mapas de imagem gerado com sucesso e salvo como {arquivo_saida}!")




if __name__ == '__main__':
    caminho_kgml = './resources_directory/kc_kgmls/ko00680.xml'
    caminho_tsv = './KEGGCharter/info/ko00680_box2name.tsv'
    caminho_json_taxon = './KEGGCharter/info/ko00680_boxes2taxon.json'
    caminho_json_kos = './KEGGCharter/info/ko00680_box2kos.json'
    caminho_json_colors = './KEGGCharter/info/ko00680_boxes2quant_colors.json'  
    root = carregar_kgml(caminho_kgml)
    titulo_pathway = extrair_titulo_pathway(caminho_kgml)
    retangulos = extrair_elementos_graficos_com_id(root)
    retangulos_enriquecidos = enriquecer_elementos_graficos(retangulos, caminho_tsv, caminho_json_taxon, caminho_json_kos)
    colors_dict = load_json_to_dict(caminho_json_colors)  
    criar_image_maps(retangulos_enriquecidos, imagem="./KEGGCharter/original_kegg_map.png", arquivo_saida=f"image_maps_{titulo_pathway}.html", titulo_imagem=f"{titulo_pathway} Map", colors_dict=colors_dict)


#main para ver output da função enriquecer_elementos_graficos
#def main():
    # Carregar os dados gráficos do XML (substituir pelo caminho real do arquivo XML de exemplo)
#    caminho_kgml = './resources_directory/kc_kgmls/ko00680.xml'
#    root = carregar_kgml(caminho_kgml)
#    elementos_graficos_com_id = extrair_elementos_graficos_com_id(root)

    # Enriquecimento dos dados
#    elementos_enriquecidos = enriquecer_elementos_graficos(
#        elementos_graficos_com_id, './KEGGCharter/info/ko00680_box2name.tsv', './KEGGCharter/info/ko00680_boxes2taxon.json', './KEGGCharter/info/ko00680_box2kos.json'
#    )

    # Imprimir os elementos gráficos enriquecidos
#    for elemento in elementos_enriquecidos:
#        print(elemento)

#if __name__ == '__main__':
#    main()