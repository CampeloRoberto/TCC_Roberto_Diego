from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    database_url: str = "postgresql+psycopg://susmed:susmed@localhost:5432/susmed"

    anvisa_csv_url: str = "https://dados.anvisa.gov.br/dados/DADOS_ABERTOS_MEDICAMENTOS.csv"
    anvisa_use_sample: bool = False

    cmed_pmc_page_url: str = "https://www.gov.br/anvisa/pt-br/assuntos/medicamentos/cmed/precos"
    cmed_xlsx_url: str | None = None  # override manual — evita depender de scraping em testes/CI
    cmed_use_sample: bool = False

    raw_data_dir: Path = BACKEND_DIR / "data" / "raw"


settings = Settings()
