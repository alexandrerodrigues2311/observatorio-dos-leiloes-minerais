# Observatório dos Leilões Minerais

Do arremate à geração de royalties.

Aplicação estática de monitoramento pós-leilão com dados abertos da ANM. Três telas: panorama, casos para acompanhar e história do processo.

## Executar

Abra `index.html` no navegador ou execute `python -m http.server 8080` nesta pasta. Não há dependências de execução nem credenciais incorporadas.

## Conteúdo e corte

CFEM até junho de 2026; extrações cadastrais de setembro de 2026. O HTML contém dados por processo, nomes cadastrais públicos, CNPJs, relações e vigências. CPFs não são identificados: a fonte é mascarada. A publicação externa deste pacote aguarda confirmação específica sobre esse conteúdo.

Os vínculos são candidatos e precisam de conferência. Fase cadastral não certifica a fase histórica. Ausência de CFEM não comprova inadimplência. Quantidade comercializada não é valor monetário da produção. Não há modelo novo de IA treinado nesta versão.

## Fontes

- https://dadosabertos.anm.gov.br/CFEM/
- https://dadosabertos.anm.gov.br/SCM/microdados/
- https://dadosabertos.anm.gov.br/SOPLE/
- https://dadosabertos.anm.gov.br/SIGMINE/PROCESSOS_MINERARIOS/

## Publicação

Projeto estático para Vercel, sem comando de compilação. Diretório de publicação: raiz.

Proposta analítica, não serviço oficialmente homologado pela ANM. Layout orientado pelas referências GOV.BR; Rawline incorporada para uso offline.
