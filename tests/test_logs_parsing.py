from automations.logs import PADROES, _grep_ftl_templates, _grep_padroes


class _FakeStream:
    def __init__(self, text):
        self._text = text

    def read(self):
        return self._text.encode("utf-8")


class _FakeSSH:
    def __init__(self, stdout_text="", stderr_text=""):
        self.stdout_text = stdout_text
        self.stderr_text = stderr_text
        self.last_cmd = None

    def exec_command(self, cmd):
        self.last_cmd = cmd
        return None, _FakeStream(self.stdout_text), _FakeStream(self.stderr_text)


def test_grep_padroes_mapeia_contagem_na_ordem_dos_padroes():
    contagens_esperadas = list(range(len(PADROES)))
    fake_output = "\n".join(str(n) for n in contagens_esperadas)
    ssh = _FakeSSH(stdout_text=fake_output)

    resultado = _grep_padroes(ssh, "/caminho/arquivo.xml")

    for nome_exibicao, esperado in zip(PADROES.values(), contagens_esperadas):
        assert resultado[nome_exibicao] == esperado


def test_grep_padroes_trata_linha_faltante_ou_invalida_como_zero():
    # menos linhas do que padroes, e uma linha nao numerica
    ssh = _FakeSSH(stdout_text="3\nabc\n")
    resultado = _grep_padroes(ssh, "/caminho/arquivo.xml")
    nomes = list(PADROES.values())
    assert resultado[nomes[0]] == 3
    assert resultado[nomes[1]] == 0  # linha invalida "abc"
    assert resultado[nomes[2]] == 0  # faltando


def test_grep_ftl_templates_parseia_saida_de_uniq_c():
    fake_output = (
        '  12 [in template "portlet/view.ftl"]\n'
        '   3 [in template "layout/main.ftl"]\n'
    )
    ssh = _FakeSSH(stdout_text=fake_output)
    templates = _grep_ftl_templates(ssh, "/caminho/arquivo.xml")
    assert templates == {
        '[in template "portlet/view.ftl"]': 12,
        '[in template "layout/main.ftl"]': 3,
    }


def test_grep_ftl_templates_retorna_vazio_sem_saida():
    ssh = _FakeSSH(stdout_text="")
    assert _grep_ftl_templates(ssh, "/caminho/arquivo.xml") == {}
