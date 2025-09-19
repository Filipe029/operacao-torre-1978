#!/usr/bin/env python3
from pathlib import Path
import argparse
import sys
import csv
from datetime import datetime

BASE = Path.home() / "aero70"
DADOS = BASE / "dados"
LOGS = BASE / "logs"
REL = BASE / "relatorios"

def log(msg: str):
    LOGS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with (LOGS / "torre.log").open("a", encoding="utf-8") as f:
        f.write(f"[{stamp}] {msg}\n")

def validar_arquivos_obrigatorios() -> bool:
    obrig = [
        DADOS / "planos_voo.csv",
        DADOS / "pistas.txt",
        DADOS / "metar.txt",
        DADOS / "notam.txt",
        DADOS / "frota.csv",
        DADOS / "pilotos.csv",
    ]
    faltando = [str(p) for p in obrig if not p.exists()]
    if faltando:
        log(f"ERRO importar-dados: faltam arquivos: {faltando}")
        print("Erro: arquivos obrigatórios ausentes:", ", ".join(faltando))
        return False
    return True

def cmd_importar_dados(_args):
    if not validar_arquivos_obrigatorios():
        sys.exit(1)
    # Aqui: validar contratos, detectar duplicidades, pré-calcular filas iniciais.
    log("OK importar-dados")
    print("Importação validada. Filas prontas para uso.")

def cmd_listar(args):
    planos = DADOS / "planos_voo.csv"
    if not planos.exists():
        print("planos_voo.csv não encontrado. Rode 'importar-dados' antes.")
        sys.exit(1)
    with planos.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    chave = args.por or "voo"
    try:
        rows.sort(key=lambda r: r.get(chave, ""))
    except Exception:
        pass
    # Tabela minimalista sem libs externas
    headers = ["voo","origem","destino","etd","eta","aeronave","tipo","prioridade","pista_pref"]
    print(" | ".join(headers))
    print("-" * 80)
    for r in rows:
        print(" | ".join([r.get(h,"") for h in headers]))

def cmd_enfileirar(args):
    # Implementar: validações piloto/aeronave; adicionar a dados/fila_decolagem.txt ou dados/fila_pouso.txt
    log(f"enfileirar {args.operacao} --voo {args.voo}")
    print(f"Voo {args.voo} enviado para fila de {args.operacao} (stub).")

def cmd_autorizar(args):
    # Implementar: retirar primeiro elegível, checar pista/metar/notam e autorizar/negado com motivo
    log(f"autorizar {args.operacao} --pista {args.pista}")
    print(f"Autorização para {args.operacao} na pista {args.pista} (stub).")

def cmd_status(_args):
    # Implementar: imprimir status de pistas, tamanho das filas, próximos 3 voos e ocorrências ativas
    print("Status da torre (stub).")
    log("status")

def cmd_relatorio(_args):
    # Implementar: gerar relatorios/operacao_YYYYMMDD.txt com métricas do turno
    hoje = datetime.now().strftime("%Y%m%d")
    alvo = REL / f"operacao_{hoje}.txt"
    alvo.parent.mkdir(parents=True, exist_ok=True)
    alvo.write_text("Relatório do turno (stub)\n", encoding="utf-8")
    print(f"Relatório gerado em {alvo}")
    log(f"relatorio -> {alvo.name}")

def build_parser():
    p = argparse.ArgumentParser(prog="torre", description="Operação Torre 1978 - CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("importar-dados", help="Valida arquivos e prepara filas")
    s.set_defaults(func=cmd_importar_dados)

    s = sub.add_parser("listar", help="Lista voos com ordenação")
    s.add_argument("--por", choices=["voo","etd","tipo","prioridade"], default="voo")
    s.set_defaults(func=cmd_listar)

    s = sub.add_parser("enfileirar", help="Enfileira voo para decolagem ou pouso")
    s.add_argument("operacao", choices=["decolagem","pouso"])
    s.add_argument("--voo", required=True)
    s.set_defaults(func=cmd_enfileirar)

    s = sub.add_parser("autorizar", help="Autoriza operação para uma pista")
    s.add_argument("operacao", choices=["decolagem","pouso"])
    s.add_argument("--pista", required=True)
    s.set_defaults(func=cmd_autorizar)

    s = sub.add_parser("status", help="Mostra status das pistas, filas e ocorrências")
    s.set_defaults(func=cmd_status)

    s = sub.add_parser("relatorio", help="Gera sumário do turno")
    s.set_defaults(func=cmd_relatorio)

    return p

def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()


