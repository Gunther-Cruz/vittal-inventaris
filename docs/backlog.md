# Backlog do VITTAL Inventaris

Este backlog registra o andamento macro do projeto. Ele nao substitui os documentos tecnicos do TCC nem o checklist local de trabalho.

## Concluido

- Criar documentacao tecnica base.
- Criar Dockerfile e docker-compose.
- Criar bootstrap Flask.
- Configurar PostgreSQL como banco principal do projeto.
- Configurar SQLAlchemy.
- Configurar Alembic/Flask-Migrate.
- Criar migration real da tabela `usuario`.
- Implementar autenticacao por sessao.
- Implementar protecao CSRF.
- Implementar controle de acesso por perfil.
- Implementar criacao do primeiro coordenador por CLI.
- Implementar criacao web de usuarios por coordenador.
- Implementar testes automatizados do modulo de autenticacao e usuarios.

## Proximas etapas previstas

1. Revisar DER completo antes de novos models.
2. Implementar models iniciais do inventario conforme DER e Diagrama de Classes.
3. Gerar migrations dos models de inventario.
4. Criar repositories e services de inventario.
5. Criar controllers e telas iniciais do inventario.
6. Implementar importacao JSON quando o contrato real estiver confirmado.
7. Implementar integracao GLPI somente apos persistencia local estar consolidada.
8. Implementar dashboards e relatorios em etapa propria.

## Fora de escopo por enquanto

- Microservicos.
- React.
- JWT.
- Integracao real com GLPI.
- Models de laboratorio, estacao, gabinete, monitor e manutencao antes da validacao do DER completo.
