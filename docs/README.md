# 🛫 Operação Torre 1978

## 📡 Sobre o projeto
Simulação didática de uma **torre de controle em 1978**, operando via **linha de comando (CLI)**.  
O programa gerencia **planos de voo, filas de pouso/decolagem, condições de pista, clima e NOTAM**, aplicando regras de negócio para autorizar ou negar operações.

O objetivo é exercitar:
- Manipulação de arquivos (`csv` e `txt`).
- Estrutura de pastas em Linux/WSL.
- Implementação de CLI em Python com `argparse`.
- Aplicação de regras operacionais reais adaptadas para a simulação.
- Geração de **logs** e **relatórios** auditáveis.

---

## ⚙️ Estrutura de diretórios

~/aero70/
├── dados/
│ ├── planos_voo.csv # planos de voo
│ ├── pistas.txt # status das pistas
│ ├── frota.csv # aeronaves e requisitos
│ ├── pilotos.csv # pilotos e licenças
│ ├── metar.txt # boletins meteorológicos
│ ├── notam.txt # ocorrências temporárias
│ ├── fila_decolagem.txt # gerado pela CLI
│ └── fila_pouso.txt # gerado pela CLI
│
├── logs/
│ └── torre.log # log de todas as operações
│
├── relatorios/
│ └── operacao_YYYYMMDD.txt # relatório do turno
│
├── torre/
│ └── torre.py # aplicação CLI em Python
│
└── docs/
└── README.md # documentação do projeto

yaml
Copiar código

---

## 🚀 Como executar

### 1. Preparar ambiente
```bash
cd ~/aero70
python3 -m venv .venv
source .venv/bin/activate
2. Subcomandos disponíveis
bash
Copiar código
python3 torre/torre.py importar-dados
python3 torre/torre.py listar --por=prioridade
python3 torre/torre.py enfileirar decolagem --voo ALT123
python3 torre/torre.py autorizar pouso --pista 10/28
python3 torre/torre.py status
python3 torre/torre.py relatorio
Use --help em qualquer comando para detalhes:

bash
Copiar código
python3 torre/torre.py --help
📑 Regras implementadas
Prioridade:

EMERGENCIA > pousos > decolagens.

Dentro de cada grupo, prioridade numérica (3→0) e horário.

Compatibilidade:

Aeronave requer comprimento mínimo de pista (frota.csv).

Pista deve estar ABERTA em pistas.txt.

NOTAM ativo que feche pista no horário → bloqueio.

Clima:

Se VIS < 6KM (em metar.txt), apenas 1 operação por vez é autorizada.

Pilotos:

Licença vencida ou habilitação incorreta → voo negado e registrado no log.

Duplicidade:

Mesmo voo em fila ou horários conflitantes → recusa e log.

📊 Exemplos de uso
Importar dados
bash
Copiar código
python3 torre/torre.py importar-dados
Saída:

Copiar código
Importação validada. Filas prontas para uso.
Listar voos por prioridade
bash
Copiar código
python3 torre/torre.py listar --por=prioridade
Saída:

diff
Copiar código
voo | origem | destino | etd  | eta  | aeronave | tipo       | prioridade | pista_pref
------------------------------------------------------------------------------------
ALT901 | STM | PVH | 14:05 | 15:20 | EMB-110 | EMERGENCIA | 3 | 01/19
ALT123 | PVH | MAO | 13:20 | 14:45 | B727    | COMERCIAL  | 1 | 10/28
Enfileirar voo
bash
Copiar código
python3 torre/torre.py enfileirar decolagem --voo ALT123
Saída:

nginx
Copiar código
Voo ALT123 enviado para fila de decolagem
Autorizar voo com pista fechada (NOTAM)
bash
Copiar código
python3 torre/torre.py autorizar pouso --pista 01/19
Saída:

yaml
Copiar código
Negado: NOTAM ativo fecha a pista 01/19 no horário atual
📝 Logs e relatórios
logs/torre.log
Cada ação registrada com timestamp, comando e resultado.
Exemplo:

css
Copiar código
[2025-09-19 10:30:02] AUTORIZADO autorizar decolagem --voo ALT123 --pista 10/28
[2025-09-19 10:32:17] NEGADO enfileirar pouso --voo ALT901: Sem piloto válido
relatorios/operacao_YYYYMMDD.txt
Relatório do turno:

Operações autorizadas e negadas

Motivos mais comuns de negativa

Emergências atendidas

Média de espera

📌 Próximos passos
Detalhar mensagens de erro para pilotos inválidos (explicar motivo).

Calcular tempo médio de espera no relatório.

Automatizar testes com pytest.

CI/CD simples no GitHub Actions.


