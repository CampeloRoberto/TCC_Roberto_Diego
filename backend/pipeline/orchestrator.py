"""Ponto de entrada do ETL: `python -m pipeline.orchestrator --run-now [--sample]`.

Modo atual (local-first): disparo manual via CLI, só ANVISA. CMED entra no
mesmo ciclo mensal quando `cmed_extractor.py` for implementado; RENAME fica
fora do ciclo (disparo manual separado, sem cadência fixa).

# TODO: habilitar modo agendado via `schedule` quando o projeto migrar para
# execução automática (ex.: `schedule.every().month.do(run_anvisa)` rodando
# em loop/daemon) — por enquanto só o caminho --run-now está implementado,
# propositalmente, para manter tudo local e sob controle manual.
"""

from __future__ import annotations

import argparse

from pipeline.extractors.anvisa_extractor import AnvisaExtractor
from pipeline.loaders.models import SessionLocal
from pipeline.loaders.postgres_loader import load_anvisa_dataframe


def run_anvisa(use_sample: bool) -> None:
    df = AnvisaExtractor(use_sample=use_sample).extract()
    n_ativos = int((df["situacao_registro"] == "Ativo").sum())
    print(
        f"[anvisa] extraídos {len(df)} registros únicos "
        f"({n_ativos} ativos, {len(df) - n_ativos} inativos)"
    )

    session = SessionLocal()
    try:
        resultado = load_anvisa_dataframe(df, session)
    finally:
        session.close()

    print(
        f"[anvisa] {resultado['processadas']} processados, "
        f"{resultado['alteradas']} inseridos ou alterados em fato_medicamento "
        f"(o resto não mudou desde a última carga)"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Orquestrador do ETL do SUS Med")
    parser.add_argument("--run-now", action="store_true", help="roda o pipeline imediatamente (padrão)")
    parser.add_argument("--sample", action="store_true", help="usa o fixture local em vez de baixar da ANVISA")
    args = parser.parse_args()

    # --run-now é o comportamento padrão nesta fase manual; a flag existe para
    # deixar explícito na linha de comando e para não quebrar quando o modo
    # agendado for ligado (ele vai querer um caminho sem --run-now).
    run_anvisa(use_sample=args.sample)


if __name__ == "__main__":
    main()
