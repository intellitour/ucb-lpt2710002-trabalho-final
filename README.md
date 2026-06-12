# 🚗 Acidentes de Trânsito em Rodovias Federais Brasileiras

|     Aluno: | Pedro Henrique Ferreira Figueiredo  |
|-----------:|:------------------------------------|
| Matrícula: | 2000064523                          |

Aplicação interativa para análise de dados de acidentes em rodovias federais brasileiras no período de 2017 a 2023, com base no dataset aberto do DNIT.

Permite explorar padrões espaciais, temporais e causais dos acidentes por meio de gráficos e mapas interativos, auxiliando na identificação de fatores de risco para políticas públicas de segurança viária.

## Jeito Fácil (Docker)

Para ver o projeto executando, o jeito mais fácil é via Docker, através do comando a seguir:

```shell
docker run -p 8501:8501 ghcr.io/intellitour/ucb-lpt2710002-trabalho-final:latest
```
<sup>A imagem foi produzida à partir do `Dockerfile`, via Github Actions.</sup>

Caso queira executar localmente, veja a seguir.

## Requisitos

- Python 3.9+
- Ambiente conda com as dependências listadas em `environment.yml` (ou instalação manual via pip)

## Instalação

### Via conda (recomendado)

```bash
conda env create -f environment.yml
conda activate pedro-ucb
```

### Via pip

```bash
pip install streamlit pandas matplotlib numpy folium seaborn streamlit-folium
```

## Execução

Primeiramente, faça [download do dataset](https://bucket.getinsight.tech/public/accidents_2017_to_2023_portugues.csv) e coloque no diretório do projeto. Em seguida, execute:

```bash
streamlit run streamlit_design_matplotlib.py
```

O aplicativo será aberto automaticamente no navegador em `http://localhost:8501`.

> **Atenção:** O arquivo `accidents_2017_to_2023_portugues.csv` deve estar no mesmo diretório do script.

## Funcionalidades

- **Filtros dinâmicos** — Estado, ano, tipo de acidente, causa, condição meteorológica e fase do dia
- **Métricas resumidas** — Total de acidentes, vítimas fatais, feridos, estados cobertos e taxa de letalidade
- **Análise de acidentes** — Classificação por vítimas, causas, tipos, pista, traçado e rodovias mais perigosas
- **Análise espacial** — Mapa interativo, regiões administrativas e condições meteorológicas
- **Análise temporal** — Evolução mensal e anual, dia da semana, fase do dia, horário, heatmap meses × anos e causas por ano
- **Dados detalhados** — Tabela filtrável com busca por município e exportação em CSV

## Sobre os dados

Dados fornecidos pela [Polícia Rodoviária Federal (PRF)](https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf) e obtidos através de uma compilação disponível no [Kaggle](https://www.kaggle.com/datasets/mlippo/car-accidents-in-brazil-2017-2023).


## Entrega

Ver [Relatório da Entrega](relatorio_entrega.md).