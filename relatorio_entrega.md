# Trabalho Final - Análise de Dados e Solução de Problemas com Python

|     Aluno: | Pedro Henrique Ferreira Figueiredo  |
|-----------:|:------------------------------------|
| Matrícula: | 2000064523                          |


## 1. Definição do Problema

O Brasil registra anualmente milhares de acidentes em rodovias federais, resultando em mortes, ferimentos e significativos prejuízos econômicos e sociais. Segundo [dados abertos da PRF](https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf), os acidentes em rodovias federais representam uma das principais causas de mortalidade no país, com picos recorrentes durante períodos de férias e finais de semana.

**Problema de negócio:** Compreender os padrões espaciais, temporais e causais dos acidentes de trânsito em rodovias federais brasileiras no período de 2017 a 2023 (recorte obtido no [Kaggle](https://www.kaggle.com/datasets/mlippo/car-accidents-in-brazil-2017-2023)), a fim de identificar os principais fatores de risco — como condições meteorológicas, horários, dias da semana, tipos de via e causas — que mais contribuem para a ocorrência de acidentes com vítimas fatais.

A análise visa responder às seguintes perguntas:

- Quais estados e regiões administrativas concentram o maior volume de acidentes?
- Quais são as principais causas e tipos de acidentes registrados?
- Qual a distribuição dos acidentes ao longo dos meses, dias da semana e horários do dia?
- As condições meteorológicas influenciam significativamente na frequência de acidentes?
- Qual a tendência temporal do número de acidentes e de suas vítimas (mortos vs. feridos) ao longo dos anos?

As respostas a essas perguntas podem subsidiar políticas públicas de segurança viária, como a realocação de agentes de trânsito em horários e trechos críticos, campanhas educativas focadas nas causas predominantes e investimentos em infraestrutura rodoviária nas regiões mais afetadas.

### 1.1 Ferramentas Utilizadas

- **Python 3** como linguagem base
- **Pandas** para manipulação e transformação de dados
- **NumPy** para operações numéricas e geração de escalas de cores
- **Matplotlib** para geração de gráficos estáticos (barras, linhas, pizza)
- **Streamlit** para construção da interface web interativa
- **Folium** para mapas interativos de distribuição geográfica

## 2. Obtenção dos Dados

### 2.1 Fonte dos Dados

O dataset utilizado é o arquivo `accidents_2017_to_2023_portugues.csv`, proveniente de uma compilação (obtida no Kaggle) de dados abertos da PRF, contendo registros de acidentes ocorridos em rodovias federais brasileiras no período de 2017 a 2023.

### 2.2 Estrutura do Dataset

O dataset original possui **463.152 registros** e **27 colunas**, conforme descrito a seguir:

| Coluna | Tipo | Descrição                                                |
|---|---|----------------------------------------------------------|
| `data_inversa` | string | Data do acidente (AAAA-MM-DD)                            |
| `dia_semana` | string | Dia da semana do acidente                                |
| `horario` | string | Horário do acidente (HH:MM:SS)                           |
| `uf` | string | Unidade da Federação (estado)                            |
| `br` | float | Número da rodovia federal                                |
| `km` | string | Quilômetro da rodovia                                    |
| `municipio` | string | Município onde ocorreu o acidente                        |
| `causa_acidente` | string | Causa do acidente                                        |
| `tipo_acidente` | string | Tipo de acidente (ex.: colisão frontal, capotamento)     |
| `classificacao_acidente` | string | Classificação por vítimas (fatais, feridas, sem vítimas) |
| `fase_dia` | string | Fase do dia (ex.: plena noite, manhã)                    |
| `sentido_via` | string | Sentido da via (crescente/decrescente)                   |
| `condicao_metereologica` | string | Condição meteorológica no momento do acidente            |
| `tipo_pista` | string | Tipo de pista (simples, dupla)                           |
| `tracado_via` | string | Traçado da via (reta, curva)                             |
| `pessoas` | int | Total de pessoas envolvidas                              |
| `mortos` | int | Número de mortos                                         |
| `feridos_leves` | int | Número de feridos leves                                  |
| `feridos_graves` | int | Número de feridos graves                                 |
| `ilesos` | int | Número de ilesos                                         |
| `ignorados` | int | Número de vítimas com status desconhecido                |
| `feridos` | int | Total de feridos (leves + graves)                        |
| `veiculos` | int | Número de veículos envolvidos                            |
| `latitude` | float | Coordenada geográfica (latitude)                         |
| `longitude` | float | Coordenada geográfica (longitude)                        |
| `regional` | string | Região administrativa da PRF/DNIT                        |
| `delegacia` | string | Delegacia responsável pelo atendimento                   |

### 2.3 Cobertura Geográfica e Temporal

O dataset abrange os **27 estados brasileiros** (incluindo o Distrito Federal) e cobre o período de **janeiro de 2017 a dezembro de 2023**, totalizando 7 anos de registros. A cobertura espacial inclui todas as rodovias federais do país, com dados georreferenciados (latitude e longitude) que permitem análise espacial.

## 3. Tratamento e Preparação dos Dados

### 3.1 Diagnóstico de Qualidade dos Dados

Antes de qualquer transformação, foi realizada uma auditoria de qualidade identificando os seguintes problemas:

| Problema | Coluna(s) Afetada(s) | Quantidade |
|---|---|---|
| Valores nulos | `br` e `km` | 990 registros |
| Valores nulos | `tipo_acidente` | 40 registros |
| Valores nulos | `regional` | 10 registros |
| Valores nulos | `delegacia` | 1.310 registros |
| Linhas duplicatas | Todas as colunas | 9 registros |
| Espaços em colunas numéricas | `pessoas`, `mortos`, `feridos_leves`, `feridos_graves`, `ilesos`, `ignorados`, `feridos`, `veiculos` | Vários registros com espaços à esquerda |

### 3.2 Estratégias de Tratamento

#### Valores nulos em `br` e `km` (990 registros)

As colunas `br` (rodovia federal) e `km` (quilômetro) apresentam valores nulos correlacionados, indicando registros de acidentes em trechos não catalogados ou sem identificação precisa da rodovia. A estratégia adotada foi **manter os registros com valores nulos**, pois a informação de acidente em si (vítimas, causas, localização geográfica) permanece válida e útil para a análise. A ausência da rodovia específica é tratada como uma categoria legítima de "rodovia não identificada" nas análises que utilizam essas colunas.

#### Valores nulos em `tipo_acidente` (40 registros)

O tipo do acidente é uma variável categórica importante para a análise exploratória. Os 40 registros com valor nulo foram **mantidos sem imputação**, uma vez que representam menos de 0,01% do total e a imputação artificial introduziria viés. Na interface Streamlit, esses registros aparecem como categoria "NaN" e podem ser excluídos via filtros quando necessário.

#### Valores nulos em `regional` (10 registros)

A região administrativa é utilizada para agrupamento geográfico. Os 10 registros nulos foram **mantidos** para preservar a integridade dos dados originais, sendo tratados como categoria separada nas visualizações.

#### Valores nulos em `delegacia` (1.310 registros)

A delegacia responsável é uma variável de baixa relevância para as perguntas de negócio deste projeto. Os valores nulos foram **mantidos sem tratamento adicional**, pois essa coluna não é utilizada nas análises exploratórias nem nos gráficos da interface.

#### Linhas duplicatas (9 registros)

Foram identificadas 9 linhas perfeitamente duplicadas (todas as colunas idênticas). A estratégia é **remover as duplicatas** utilizando o método `drop_duplicates()` do Pandas, garantindo que cada acidente seja contado uma única vez nas análises agregadas.

#### Espaços em colunas numéricas

As colunas `pessoas`, `mortos`, `feridos_leves`, `feridos_graves`, `ilesos`, `ignorados`, `feridos` e `veiculos` possuem espaços em branco à esquerda nos valores originais. O Pandas, ao carregar o CSV, já converte essas colunas para `int64`, tratando automaticamente os espaços. No entanto, a conversão explícita via `pd.to_numeric()` com `errors='coerce'` garante robustez contra valores atípicos não numéricos que possam estar presentes em subconjuntos do dado.

### 3.3 Conversão de Tipos

As conversões de tipo realizadas são fundamentais para as análises temporais e espaciais:

| Coluna Original | Tipo Original | Tipo Final | Método |
|---|---|---|---|
| `data_inversa` | string (object) | datetime64[ns] | `pd.to_datetime()` |
| `horario` | string (HH:MM:SS) | int64 (hora) | `pd.to_datetime(format="%H:%M:%S").dt.hour` |

A conversão de `data_inversa` para datetime é o passo mais crítico, pois permite extrair as features temporais necessárias para a análise. A conversão de `horario` para hora inteira (0-23) simplifica a agregação por horário do dia.

### 3.4 Engenharia de Features

Foram criadas as seguintes features derivadas a partir das conversões de tipo descritas acima:

| Feature | Origem | Tipo | Descrição |
|---|---|---|---|
| `ano` | `data_inversa` | int64 | Ano do acidente (extraído via `.dt.year`) |
| `mes` | `data_inversa` | string (categorical) | Nome do mês em português (extraído via `.dt.month_name("pt_BR")`) |
| `horario` | `horario` (string) | int64 | Hora do dia (0-23, extraído via `.dt.hour`) |

A feature `mes` foi gerada com o parâmetro `lang="pt_BR"` para retornar os nomes em português (janeiro, fevereiro, etc.), facilitando a legibilidade dos gráficos. A ordenação temporal dos meses é garantida por meio de `pd.Categorical` com a sequência correta, assegurando que os gráficos respeitem a ordem cronológica e não a ordem alfabética.

A feature `horario` como inteiro permite agrupamentos eficientes por hora do dia, identificando os picos de acidentes ao longo das 24 horas.

A feature `ano` permite a análise de tendências temporais ao longo dos 7 anos de dados, identificando se o número de acidentes e vítimas está crescendo, diminuindo ou se mantendo estável.

### 3.5 Pipeline de Carregamento

Todo o processamento de dados é encapsulado na função `carregar_dados()`, decorada com `@st.cache_data` do Streamlit. O cache garante que o carregamento e a transformação dos dados ocorram apenas na primeira execução, sendo reutilizados nas interações subsequentes do usuário com a interface. O pipeline segue a seguinte sequência:

1. **Leitura** do CSV com `pd.read_csv()`
2. **Conversão** de `data_inversa` para datetime
3. **Extração** das features `ano` e `mes` a partir de `data_inversa`
4. **Conversão** de `horario` para hora inteira (0-23)

Essa abordagem garante reprodutibilidade e performance, pois o dataset processado é armazenado em cache e reutilizado a cada interação com os filtros da interface.

## 4. Resultados Visuais

A aplicação Streamlit foi organizada em quatro abas temáticas, cada uma contendo gráficos que respondem a perguntas específicas do problema.

### 4.1 Aba "Acidentes" — Classificação e Causas

**Classificação por Vítimas** — Gráfico de barras verticais mostrando a distribuição dos acidentes conforme o número de vítimas (com vítimas fatais, com vítimas feridas, sem vítimas). As barras utilizam gradiente de cores na paleta *Reds*, com anotação de valores absolutos sobre cada barra. Este gráfico permite identificar rapidamente a proporção de acidentes letais em relação ao total.

**Top 10 Causas de Acidentes** — Gráfico de barras horizontais com as dez causas mais frequentes, utilizando a paleta *Viridis*. A orientação horizontal facilita a leitura de rótulos extensos (ex.: "Velocidade Incompatível", "Defeito Mecânico no Veículo"). Cada barra possui anotação numérica ao lado direito.

**Acidentes por Estado** — Gráfico de barras verticais com os 27 estados ordenados por volume decrescente, utilizando a paleta *Blues*. Os rótulos dos eixos X estão rotacionados em 45° para melhor legibilidade. Permite identificar os estados com maior concentração de acidentes.

**Distribuição por Tipo de Acidente** — Gráfico de pizza com os oito tipos mais frequentes, utilizando a paleta *Set3*. As fatias possuem bordas brancas para delimitação visual e legenda posicionada à direita. A anotação percentual em cada fatia facilita a comparação proporcional.

### 4.2 Aba "Análise Espacial" — Distribuição Geográfica

**Mapa Interativo** — Mapa Folium centrado no território brasileiro, com marcadores circulares coloridos por classificação do acidente: vermelho (com vítimas fatais), laranja (com vítimas feridas) e verde (sem vítimas). O raio de cada marcador é proporcional ao número de pessoas envolvidas. Ao clicar no marcador, um popup exibe detalhes do acidente (município, data, vítimas). Para manter a performance, o mapa exibe no máximo 5.000 pontos amostrados aleatoriamente quando o conjunto filtrado excede esse limite.

**Top Regiões Administrativas** — Gráfico de barras verticais com as doze regiões administrativas do DNIT mais afetadas, utilizando a paleta *Reds*. Permite comparar o volume de acidentes entre as superintendências regionais.

**Acidentes por Condição Meteorológica** — Gráfico de barras verticais mostrando a distribuição dos acidentes conforme a condição climática, utilizando a paleta *YlOrRd* (amarelo para condições favoráveis, vermelho para condições adversas). Este gráfico é fundamental para avaliar a influência do clima na segurança viária.

### 4.3 Aba "Análise Temporal" — Padrões Temporais

**Evolução Temporal Mensal** — Gráfico de linha com marcadores circulares mostrando o comportamento sazonal dos acidentes ao longo dos meses, com área sombreada abaixo da curva. Os meses estão ordenados cronologicamente (janeiro a dezembro) via `pd.Categorical`, garantindo a sequência correta. A anotação numérica sobre cada ponto facilita a leitura de valores.

**Acidentes por Ano** — Gráfico de barras verticais com a tendência anual do volume total de acidentes, utilizando a paleta *Plasma*. Permite identificar se há crescimento, estabilidade ou redução no número de acidentes ao longo dos 7 anos.

**Acidentes por Dia da Semana** — Gráfico de barras verticais com a variação semanal, utilizando a paleta *YlGn*. Os dias estão ordenados de segunda a domingo via `pd.Categorical`, permitindo identificar se finais de semana e feriados concentram mais acidentes.

**Acidentes por Horário** — Gráfico de linha com marcadores quadrados mostrando a distribuição horária ao longo das 24 horas, com área sombreada abaixo da curva. O eixo X exibe ticks a cada 2 horas. Este gráfico identifica os horários de pico de acidentes, orientando a atuação de agentes de trânsito.

**Vítimas por Ano (Mortos vs Feridos)** — Gráfico de barras agrupadas com duas séries (mortos em vermelho, feridos em laranja) comparando o número anual de vítimas. Inclui legenda e anotações numéricas coloridas. Permite avaliar se a tendência de mortalidade segue o mesmo padrão do número total de acidentes.

### 4.4 Aba "Dados Detalhados" — Exploração Livre

Tabela interativa com os dados filtrados, permitindo ordenação por qualquer coluna e busca textual por município. Inclui botão para exportação em CSV dos dados filtrados, facilitando análises complementares fora da aplicação.

### 4.5 Filtros e Métricas Resumidas

A barra lateral contém filtros dinâmicos de seleção múltipla para estado, ano, tipo de acidente, causa e condição meteorológica. No topo da página, quatro métricas resumidas exibem em tempo real: total de acidentes, vítimas fatais, feridos e estados cobertos pelo conjunto filtrado.

## 5. Conclusões

A análise exploratória dos dados de acidentes em rodovias federais brasileiras revelou padrões consistentes que podem orientar ações de prevenção:

**Concentração geográfica:** Os estados do Sudeste e Sul apresentam os maiores volumes absolutos de acidentes, reflexo da maior extensão de rodovias federais e do volume de tráfego nessas regiões. O mapa interativo confirma a concentração de acidentes letais em trechos específicos, especialmente nas regiões metropolitanas e nos eixos rodoviários de maior fluxo.

**Causas predominantes:** A velocidade incompatível e os defeitos mecânicos nos veículos aparecem como as principais causas de acidentes. Esses achados indicam que campanhas de fiscalização de velocidade e programas de inspeção veicular têm potencial para reduzir significativamente a ocorrência de acidentes.

**Padrões temporais:** A análise mensal revela picos de acidentes nos meses de férias (dezembro a janeiro), corroborando a relação entre aumento do tráfego de veículos e incidência de acidentes. A análise por dia da semana confirma maior concentração nos fins de semana, enquanto a análise horária identifica picos na faixa das 10h–14h e nas horas noturnas (20h–24h), sugerindo a necessidade de reforço de fiscalização nesses períodos.

**Condições meteorológicas:** A maioria dos acidentes ocorre em condições de céu claro, indicando que o fator climático não é o principal determinante. No entanto, os acidentes que ocorrem em condições adversas (chuva, garoa) tendem a apresentar maior letalidade, sugerindo que a combinação de pista molhada com excesso de velocidade é particularmente perigosa.

**Tendência temporal:** A comparação anual entre mortos e feridos permite avaliar a evolução da segurança viária ao longo do período. A análise sugere que, apesar da evolução da infraestrutura rodoviária, o aumento do volume de tráfego mantém os números de acidentes em patamares elevados.

**Impacto das vítimas:** A proporção entre acidentes com vítimas fatais e sem vítimas evidencia a gravidade do problema. A maioria dos acidentes envolve feridos leves, mas a parcela de acidentes letais — embora numericamente menor — representa o impacto humano mais severo.

A aplicação desenvolvida cumpre seu objetivo de democratizar o acesso a esses dados por meio de uma interface intuitiva e interativa, permitindo que gestores públicos, pesquisadores e a sociedade civil explorem os dados livremente, filtrando por diferentes dimensões e identificando padrões relevantes para suas áreas de atuação. A ferramenta pode ser expandida no futuro com a inclusão de dados de investimentos em infraestrutura, permitindo análises correlacionais entre gastos e redução de acidentes.