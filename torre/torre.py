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

FILA_DECOL = DADOS / "fila_decolagem.txt"
FILA_POUSO = DADOS / "fila_pouso.txt"

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

# ---------- Utilitários de leitura simples ----------
def ler_planos() -> list[dict]:
    with (DADOS / "planos_voo.csv").open(encoding="utf-8") as f:
        return list(csv.DictReader(f))

def buscar_plano_por_voo(voo: str) -> dict | None:
    for r in ler_planos():
        if r.get("voo") == voo:
            return r
    return None

def ler_pilotos() -> list[dict]:
    with (DADOS / "pilotos.csv").open(encoding="utf-8") as f:
        return list(csv.DictReader(f))

def piloto_valido_para(plano: dict) -> tuple[bool,str]:
    # Simplificação: procura um piloto cuja habilitação bate com a aeronave e validade >= hoje
    aeronave = plano.get("aeronave","")
    hoje = datetime.now().date()
    for p in ler_pilotos():
        hab = p.get("habilitacao","")
        validade = p.get("validade","0000-00-00")
        try:
            vdate = datetime.strptime(validade, "%Y-%m-%d").date()
        except Exception:
            vdate = hoje.replace(year=1900)
        if hab == aeronave and vdate >= hoje:
            return True, f"{p.get('matricula')} - {p.get('nome')}"
    return False, "Sem piloto válido (habilitação ou validade)"

def ler_pistas() -> dict:
    # Retorna { "10/28": "ABERTA", ... }
    pistas = {}
    with (DADOS / "pistas.txt").open(encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line: continue
            p, status = [x.strip() for x in line.split(",",1)]
            pistas[p] = status
    return pistas

def notam_fecha_pista_agora(pista: str) -> bool:
    # NOTAM: "PISTA 01/19 FECHADA 14:00-16:00 ..."
    agora = datetime.now().strftime("%H:%M")
    a_h, a_m = map(int, agora.split(":"))
    cur = a_h*60 + a_m
    with (DADOS / "notam.txt").open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("PISTA ") and "FECHADA" in line and pista in line:
                # achar janela HH:MM-HH:MM
                partes = line.split()
                janela = None
                for token in partes:
                    if "-" in token and ":" in token:
                        janela = token
                        break
                if janela:
                    ini, fim = janela.split("-")
                    ih, im = map(int, ini.split(":"))
                    fh, fm = map(int, fim.split(":"))
                    a = ih*60+im
                    b = fh*60+fm
                    if a <= cur <= b:
                        return True
    return False

def vis_restritiva_agora() -> bool:
    # Lê a última linha de metar.txt e tenta extrair "VIS XKM"
    last = ""
    with (DADOS / "metar.txt").open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                last = line.strip()
    if "VIS" in last and "KM" in last:
        try:
            frag = last.split("VIS",1)[1].strip()
            km = frag.split("KM",1)[0].strip()
            valor = int(km)
            return valor < 6
        except Exception:
            return False
    return False

def ler_fila(path: Path) -> list[str]:
    if not path.exists(): return []
    with path.open(encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip()]

def escrever_fila(path: Path, linhas: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for l in linhas:
            f.write(l + "\n")

def ja_na_fila(voo: str) -> bool:
    return any(voo in l for l in ler_fila(FILA_DECOL) + ler_fila(FILA_POUSO))

# ---------- Comandos ----------
def cmd_importar_dados(_args):
    if not validar_arquivos_obrigatorios():
        sys.exit(1)
    # Não vamos pré-calcular filas aqui; deixamos manual via enfileirar
    log("OK importar-dados")
    print("Importação validada. Filas prontas para uso.")

def cmd_listar(args):
    planos = DADOS / "planos_voo.csv"
    if not planos.exists():
        print("planos_voo.csv não encontrado. Rode 'importar-dados' antes.")
        sys.exit(1)

    with planos.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if args.por == "prioridade":
        def sortkey(r):
            tipo = r.get("tipo", "")
            prio = int(r.get("prioridade", 0))
            hora = r.get("etd", "")
            return (0 if tipo == "EMERGENCIA" else 1, -prio, hora)
        rows.sort(key=sortkey)
    else:
        rows.sort(key=lambda r: r.get(args.por, ""))

    headers = ["voo","origem","destino","etd","eta","aeronave","tipo","prioridade","pista_pref"]
    print(" | ".join(headers))
    print("-" * 80)
    for r in rows:
        print(" | ".join([r.get(h,"") for h in headers]))

def cmd_enfileirar(args):
    voo = args.voo
    oper = args.operacao  # decolagem|pouso
    plano = buscar_plano_por_voo(voo)
    if not plano:
        print(f"Erro: voo {voo} não encontrado em planos_voo.csv")
        log(f"ERRO enfileirar {oper} --voo {voo}: voo inexistente")
        sys.exit(1)

    if ja_na_fila(voo):
        print(f"Erro: voo {voo} já está em alguma fila")
        log(f"ERRO enfileirar {oper} --voo {voo}: duplicidade em filas")
        sys.exit(1)

    ok_piloto, info_piloto = piloto_valido_para(plano)
    if not ok_piloto:
        print(f"Negado: {info_piloto}")
        log(f"NEGADO enfileirar {oper} --voo {voo}: {info_piloto}")
        sys.exit(1)

    hora = datetime.now().strftime("%H:%M")
    prioridade = plano.get("prioridade","0")
    registro = f"{voo};{hora};{prioridade};"  # pista_atribuida? fica vazio por enquanto

    destino = FILA_DECOL if oper == "decolagem" else FILA_POUSO
    with destino.open("a", encoding="utf-8") as f:
        f.write(registro + "\n")

    print(f"Voo {voo} enviado para fila de {oper}")
    log(f"OK enfileirar {oper} --voo {voo} (piloto={info_piloto})")

def cmd_autorizar(args):
    oper = args.operacao
    pista = args.pista
    pistas = ler_pistas()
    if pista not in pistas:
        print(f"Negado: pista {pista} inexistente")
        log(f"NEGADO autorizar {oper} --pista {pista}: pista inexistente")
        sys.exit(1)
    if pistas[pista] != "ABERTA":
        print(f"Negado: pista {pista} FECHADA")
        log(f"NEGADO autorizar {oper} --pista {pista}: pista fechada em pistas.txt")
        sys.exit(1)
    if notam_fecha_pista_agora(pista):
        print(f"Negado: NOTAM ativo fecha a pista {pista} no horário atual")
        log(f"NEGADO autorizar {oper} --pista {pista}: NOTAM ativo")
        sys.exit(1)

    # Clima: VIS < 6KM permite apenas 1 operação por vez.
    # Implemento um bloqueio lógico simples: se vis restritiva, só autoriza uma vez por minuto.
    # Para isso, checamos se houve autorização registrada no último minuto.
    if vis_restritiva_agora():
        # Heurística: procura no log uma autorização do mesmo minuto.
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        recente = False
        if (LOGS / "torre.log").exists():
            with (LOGS / "torre.log").open(encoding="utf-8") as f:
                for line in f:
                    if ts in line and "AUTORIZADO" in line:
                        recente = True
                        break
        if recente:
            print("Negado: capacidade reduzida por VIS < 6KM (uma operação por vez)")
            log(f"NEGADO autorizar {oper} --pista {pista}: VIS<6KM capacidade")
            sys.exit(1)

    fila_path = FILA_DECOL if oper == "decolagem" else FILA_POUSO
    fila = ler_fila(fila_path)
    if not fila:
        print(f"Fila de {oper} vazia")
        log(f"autorizar {oper} --pista {pista}: fila vazia")
        sys.exit(0)

    # Retira o primeiro da fila
    linha = fila.pop(0)
    escrever_fila(fila_path, fila)
    partes = linha.split(";")
    voo = partes[0] if partes else "DESCONHECIDO"

    # Aqui caberia revalidar mais coisas (compatibilidade de aeronave/pista etc.),
    # mas isso entra na próxima iteração. Agora registramos autorização.
    print(f"AUTORIZADO: {oper} do voo {voo} na pista {pista}")
    log(f"AUTORIZADO autorizar {oper} --voo {voo} --pista {pista}")

def cmd_status(_args):
    decol = ler_fila(FILA_DECOL)
    pouso = ler_fila(FILA_POUSO)
    print("Status da torre")
    print(f"- Pistas: {', '.join([f'{p}:{s}' for p,s in ler_pistas().items()])}")
    print(f"- Fila de decolagem: {len(decol)} itens")
    for l in decol[:3]:
        print(f"  • {l}")
    print(f"- Fila de pouso: {len(pouso)} itens")
    for l in pouso[:3]:
        print(f"  • {l}")
    log("status")

def cmd_relatorio(_args):
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