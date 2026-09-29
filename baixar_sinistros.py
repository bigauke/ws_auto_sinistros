import os
import requests

def baixar_sinistros_sp(pasta_destino):
    api_url = "https://dadosabertos.sp.gov.br/api/3/action/package_show?id=veiculos-envolvidos-em-sinistros"
    
    print("Obtendo metadados da API...")
    response = requests.get(api_url)
    response.raise_for_status()
    data = response.json()
    
    # Mapeamento para facilitar o filtro de datas
    meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
             "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    ano_inicio, mes_inicio = 2021, 1
    ano_fim, mes_fim = 2026, 8
    
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)

    arquivos_para_baixar = []

    # Filtrar recursos
    for resource in data.get('result', {}).get('resources', []):
        nome = resource.get('name', '')
        url = resource.get('url', '')
        
        # O padrão do nome é "Veículos Envolvidos em Sinistros - <Mês> de <Ano>"
        if " - " in nome and " de " in nome:
            partes = nome.split(" - ")[-1].split(" de ")
            if len(partes) == 2:
                mes_str, ano_str = partes[0], partes[1]
                if mes_str in meses and ano_str.isdigit():
                    mes_idx = meses.index(mes_str) + 1
                    ano = int(ano_str)
                    
                    # Checar se está dentro do período desejado
                    if (ano > ano_inicio or (ano == ano_inicio and mes_idx >= mes_inicio)) and \
                       (ano < ano_fim or (ano == ano_fim and mes_idx <= mes_fim)):
                        
                        # Formatar o nome do arquivo para ficar ordenado: veiculos_YYYY_MM.csv
                        nome_arquivo = f"veiculos_{ano}_{mes_idx:02d}.csv"
                        arquivos_para_baixar.append((nome_arquivo, url))

    print(f"Encontrados {len(arquivos_para_baixar)} arquivos para download no período especificado.")
    
    # Fazer o download de cada arquivo
    for nome_arquivo, url in arquivos_para_baixar:
        caminho_arquivo = os.path.join(pasta_destino, nome_arquivo)
        print(f"Baixando {nome_arquivo}...")
        
        r = requests.get(url, stream=True)
        r.raise_for_status()
        
        with open(caminho_arquivo, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                
    print("Download concluído com sucesso!")

if __name__ == "__main__":
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dados_sinistros')
    baixar_sinistros_sp(pasta)
