# 🛫 Operação Torre 1978

## 📡 Sobre o projeto
Simulação em **linha de comando (CLI)** da operação de uma torre de controle em 1978.  
O sistema manipula arquivos de dados (`csv`/`txt`), mantém filas de pouso e decolagem, aplica regras de negócio (prioridades, clima, NOTAM, habilitação de pilotos) e gera **logs** e **relatórios** auditáveis.

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

### Preparar ambiente
```bash
cd ~/aero70
python3 -m venv .venv
source .venv/bin/activate
Subcomandos disponíveis
bash
Copiar código
python3 torre/torre.py importar-dados
python3 torre/torre.py listar --por=prioridade
python3 torre/torre.py enfileirar decolagem --voo ALT123
python3 torre/torre.py autorizar pouso --pista 10/28
python3 torre/torre.py status
python3 torre/torre.py relatorio
Use --help para mais detalhes:

bash
Copiar código
python3 torre/torre.py --help
📑 Regras implementadas
Prioridade global: EMERGENCIA > pousos > decolagens.

Ordenação interna: prioridade 3→0 e depois horário.

Compatibilidade: aeronave precisa de pista suficiente e ABERTA; NOTAM ativo fecha.

Clima: VIS < 6KM → apenas 1 operação por vez.

Pilotos: licença vencida ou habilitação incorreta → voo negado.

Duplicidade: voo já em fila → recusa.

📝 Logs e relatórios
logs/torre.log: registra cada comando, autorizado ou negado.

relatorios/operacao_YYYYMMDD.txt: resumo do turno (autorizadas, negadas, emergências atendidas, média de espera).



