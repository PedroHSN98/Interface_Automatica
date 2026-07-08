from core import services


def test_build_logs_repassa_parametros_para_run_logs(monkeypatch):
    chamadas = []
    monkeypatch.setattr(services, "run_logs",
                        lambda *a, **kw: chamadas.append((a, kw)))

    target = services.build_logs(["2026-01-01"], ["Elasticsearch 1"], ["Liferay 1"])
    target("fake_q", "fake_ev")

    assert len(chamadas) == 1
    args, kwargs = chamadas[0]
    assert args == (["2026-01-01"], "fake_q", "fake_ev")
    assert kwargs == {
        "servidores_elastic": ["Elasticsearch 1"],
        "servidores_liferay": ["Liferay 1"],
    }


def test_build_scraper_repassa_parametros_para_run_scraper(monkeypatch):
    chamadas = []
    monkeypatch.setattr(services, "run_scraper",
                        lambda *a: chamadas.append(a))

    target = services.build_scraper("links.txt", "saida/")
    target("fake_q", "fake_ev")

    assert chamadas == [("links.txt", "saida/", "fake_q", "fake_ev")]


def test_build_amaweb_repassa_parametros_para_run_amaweb(monkeypatch):
    chamadas = []
    monkeypatch.setattr(services, "run_amaweb",
                        lambda *a, **kw: chamadas.append((a, kw)))

    target = services.build_amaweb("urls.txt", "resultado.xlsx", 7.5)
    target("fake_q", "fake_ev")

    args, kwargs = chamadas[0]
    assert args == ("urls.txt", "resultado.xlsx", "fake_q", "fake_ev")
    assert kwargs == {"threshold": 7.5}


def test_build_relatorio_repassa_parametros_para_run_relatorio(monkeypatch):
    chamadas = []
    monkeypatch.setattr(services, "run_relatorio",
                        lambda *a: chamadas.append(a))

    target = services.build_relatorio("relatorio.xlsx")
    target("fake_q", "fake_ev")

    assert chamadas == [("relatorio.xlsx", "fake_q", "fake_ev")]
