import json

from utils import historico as hist


def test_registrar_grava_entrada_mais_recente_primeiro(tmp_path, monkeypatch):
    monkeypatch.setattr(hist, "_PATH", str(tmp_path / "historico.json"))

    hist.registrar("scraper", "sucesso", "1 imagem baixada")
    hist.registrar("logs", "erro", "falha de conexao")

    entradas = hist.listar(10)
    assert len(entradas) == 2
    assert entradas[0]["modulo"] == "logs"
    assert entradas[0]["status"] == "erro"
    assert entradas[1]["modulo"] == "scraper"


def test_listar_retorna_lista_vazia_se_arquivo_nao_existe(tmp_path, monkeypatch):
    monkeypatch.setattr(hist, "_PATH", str(tmp_path / "nao_existe.json"))
    assert hist.listar(10) == []


def test_listar_retorna_lista_vazia_se_json_invalido(tmp_path, monkeypatch):
    path = tmp_path / "historico.json"
    path.write_text("{nao e json valido", encoding="utf-8")
    monkeypatch.setattr(hist, "_PATH", str(path))
    assert hist.listar(10) == []


def test_listar_respeita_limite_n(tmp_path, monkeypatch):
    monkeypatch.setattr(hist, "_PATH", str(tmp_path / "historico.json"))
    for i in range(5):
        hist.registrar("scraper", "sucesso", f"execucao {i}")
    assert len(hist.listar(3)) == 3


def test_registrar_respeita_max_entries(tmp_path, monkeypatch):
    path = tmp_path / "historico.json"
    monkeypatch.setattr(hist, "_PATH", str(path))
    monkeypatch.setattr(hist, "MAX_ENTRIES", 3)

    for i in range(5):
        hist.registrar("scraper", "sucesso", f"execucao {i}")

    dados = json.loads(path.read_text(encoding="utf-8"))
    assert len(dados) == 3
    # a mais recente (execucao 4) deve ser a primeira
    assert dados[0]["detalhes"] == "execucao 4"


def test_ultima_retorna_entrada_mais_recente_do_modulo(tmp_path, monkeypatch):
    monkeypatch.setattr(hist, "_PATH", str(tmp_path / "historico.json"))
    hist.registrar("scraper", "sucesso", "primeira")
    hist.registrar("logs", "sucesso", "outra")
    hist.registrar("scraper", "erro", "mais recente")

    entrada = hist.ultima("scraper")
    assert entrada is not None
    assert entrada["detalhes"] == "mais recente"


def test_ultima_retorna_none_se_modulo_nao_encontrado(tmp_path, monkeypatch):
    monkeypatch.setattr(hist, "_PATH", str(tmp_path / "historico.json"))
    hist.registrar("scraper", "sucesso", "x")
    assert hist.ultima("amaweb") is None
