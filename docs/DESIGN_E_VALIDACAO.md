# Observatório dos Leilões Minerais — redesenho de 26/09/2026

## Jornada
Entenda, explore e confira. O panorama apresenta o problema; rodadas e destinos distinguem lances e pagamentos estimados; o capítulo social acompanha a 6ª rodada sem compará-la a receita comercial; mapa, casos e história permitem investigação; CFEM e biblioteca conectam resultados e regras.

## Identidade e componentes
Paleta própria do produto, não uma especificação oficial da ANM: azul escuro #102A43, azul #174A7E, azul médio #2878B5, superfície #FFFFFF, fundo #F4F7FB e texto #172B4D. Logo original sem recoloração. Tipografia incorporada Rawline e alternativas locais Segoe UI/Arial. Escala de espaço de 8 px; títulos responsivos; texto principal 16 px; controles com altura mínima 44 px. Navegação com texto e ícones; foco visível; redução de movimento; tabelas roláveis apenas dentro de seus contêineres; metadados e fontes em detalhes sob demanda.

## Alterações
Oito capítulos, entrada narrativa, filtros persistentes, painel lateral do processo, retorno à análise, CSV do recorte, biblioteca pesquisável, catálogo JSON, matriz de fundamentos e sete etapas da CFEM. Simulação didática dos grupos de distribuição; sem inferir repasses municipais a partir das áreas. Informação social separada. Rodadas social e cancelada não são desempenho comercial zero.

## Validação executada
Playwright/Chrome: oito rotas, ausência de erros JavaScript, ausência de IDs duplicados na entrada, consultas de regressão, preservação de filtros e totais, abertura/fechamento do painel, funcionamento offline por arquivo HTML e link direto CFEM. As oito rotas ficaram com largura de documento 390 px em viewport de 390 px. Simulações somam 100% nos dois cenários; valor negativo tem mensagem; sete etapas respondem; busca documental, diálogo, Escape e exportação CSV funcionam. Teste de ciclos completos preservou R$ 4.123.128,39, cadeia 864.381/2012 → 864.218/2021 → 864.396/2024 e único caso comparativo pendente 300.320/2018.

Consultas de regressão com UF abreviada MG/PA não selecionam opção, pois o filtro usa nomes por extenso; esses dois cenários equivalem ao filtro estadual vazio. Minas Gerais foi testado adicionalmente com seleção válida e preservação ao trocar capítulos. Não é uma auditoria integral de acessibilidade ou validade jurídica.

## Limites
Não houve nova extração nem retreinamento. Pagamento estimado continua premissa, não conciliação financeira. Quantidade comercializada não equivale à extração física. Um alerta não certifica inadimplência. Titular, arrematante, recolhedor e primeiro adquirente são papéis distintos. A biblioteca registra a profundidade da leitura; não é catálogo exaustivo de atos vigentes. Os dados sociais são preliminares e não se somam automaticamente aos comerciais.

O HTML incorpora dados e recursos essenciais e tem aproximadamente 38,4 MB: permite consulta offline, mas a primeira transferência ainda pode ser lenta em rede limitada. Links documentais exigem internet. Distribuição por beneficiário e execução de despesas ainda não foram integradas.

## Fontes históricas
A distribuição histórica ilustrativa usa a redação anterior à reforma de 2017 da Lei 8.001, após Lei 9.993/2000: municípios 65%, estados/DF 23%, DNPM 9,8%, FNDCT 2% e Ibama 0,2%. Conferir também o texto com alterações em https://www.planalto.gov.br/ccivil_03/leis/l8001.htm . A escolha do cenário não implementa todas as transições de vigência.
