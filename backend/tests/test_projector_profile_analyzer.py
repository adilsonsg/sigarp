from app.services.projector_profile_analyzer import ProjectorProfileAnalyzer

SENAR_SAMPLE = "\n".join(
    [
        "4.12. TABELA DE ITENS - ITEM 12: IMPRESSORA LASER",
        "4.12.1. Impressora laser com Wi-Fi e resolução 1200 x 1200.",
        "4.19. CABO HDMI",
        "Suporte a resolução Full HD 1080p.",
        "4.21. TABELA DE ITENS - ITEM 21: PROJETOR MULTIMÍDIA",
        "4.21.7. Especificações: tecnologia 3LCD de 3 chips.",
        "4.21.8. Brilho mínimo de 3.200 lumens.",
        "Tipo de lâmpada: UHE com potência de 200 W.",
        "4.21.9. Duração da lâmpada até 10.000 horas.",
        "4.21.10. Padrões de vídeo: 720p, 1080i e 1080p.",
        "4.21.11. Garantia mínima de 12 meses.",
        "Modelo de referência: Epson PowerLite E24 ou equivalente superior.",
        "4.22. Critério de tiragem/pedido mínimo para fornecimento:",
        "ITEM DESCRITIVO PEDIDO INICIAL",
        "21 PROJETOR MULTIMÍDIA (DATA SHOW) 05",
        "5. OBJETIVOS DA CONTRATAÇÃO",
        "21 - Projetor multimídia",
        "Descrição Detalhada: Projetor Multimídia Distância Mínima Tela: 0,35M,",
        "Tipo Lâmpada: Uhe, Potência Lâmpada: 250W, Tipo: Interativo,",
        "Luminosidade Mínima: 3.200LM, Tipo Tecnologia: 3lcd,",
        "Resolução: 1.280 X 800, Tipo Controle: Remoto, Sem Fio",
        "Tratamento Diferenciado: Não",
        "22 - Outro equipamento",
        "Tabela geral",
        "21",
        "PROJETOR MULTIMÍDIA - MODELO DE REFERÊNCIA: EPSON POWER LITE E24",
        "OU EQUIVALENTE TÉCNICO SUPERIOR.",
        "UND. 15",
        "8.1.1. Os produtos deverão ser entregues no prazo de até 30 dias",
        "corridos para o item 21 - Projetor Multimídia.",
    ]
)


def test_isolates_projector_section_without_cross_item_contamination() -> None:
    result = ProjectorProfileAnalyzer.analyze_document(SENAR_SAMPLE)
    item = result["melhor_item"]

    assert item["numero_item"] == 21
    assert item["quantidade_total"] == 15
    assert item["quantidade_pedido_inicial"] == 5
    assert item["modelo_referencia"].lower().startswith("epson power")
    assert item["fonte_luz"] == "LAMPADA_UHE"
    assert item["laser"] is False
    assert item["resolucao_nativa"]["texto"] == "1280 x 800"
    assert item["full_hd_nativo"] is False
    assert item["luminosidade_lumens"] == 3200
    assert item["wifi"] is True
    assert item["interativo"] is True
    assert item["garantia_meses"] == 12
    assert item["prazo_entrega_dias"] == 30
    assert result["avaliacao"]["adequacao"] == "INCOMPATIVEL"


def test_does_not_copy_laser_or_full_hd_from_other_items() -> None:
    result = ProjectorProfileAnalyzer.analyze_document(SENAR_SAMPLE)
    item = result["melhor_item"]

    assert item["laser"] is False
    assert item["full_hd_nativo"] is False
    failed = result["avaliacao"]["requisitos_nao_atendidos"]
    assert "fonte_luz_laser" in failed
    assert "full_hd_nativo" in failed


def compliant_projector_text(model: str) -> str:
    return "\n".join(
        [
            "4.1. TABELA DE ITENS - ITEM 1: PROJETOR INTERATIVO",
            f"4.1.1. Modelo de referência: {model} ou equivalente.",
            "Quantidade total: 20. Fonte de luz laser,",
            "resolução nativa 1920 x 1080, Wi-Fi integrado, interativo,",
            "ultracurta distância, luminosidade 4100 lumens.",
            "4.2. Próximo item",
        ]
    )


def test_marks_objective_technical_profile_as_adequate() -> None:
    result = ProjectorProfileAnalyzer.analyze_document(
        compliant_projector_text("Fabricante Alfa Modelo X")
    )

    assert result["avaliacao"]["adequacao"] == "ADEQUADA"
    assert result["perfil"]["versao"] == "1.0.0"
    assert "brightlink" not in result["melhor_item"]


def test_equivalent_manufacturers_receive_identical_assessment() -> None:
    first = ProjectorProfileAnalyzer.analyze_document(
        compliant_projector_text("Fabricante Alfa Modelo X")
    )
    second = ProjectorProfileAnalyzer.analyze_document(
        compliant_projector_text("Fabricante Beta Modelo Y")
    )

    assert (
        first["melhor_item"]["modelo_referencia"]
        != second["melhor_item"]["modelo_referencia"]
    )
    assert first["avaliacao"] == second["avaliacao"]
    assert first["perfil"] == second["perfil"]
    assert not any(
        term in str(first["perfil"]).lower()
        for term in ["fabricante", "marca", "brightlink", "epson"]
    )


def test_profile_file_has_no_commercial_criteria() -> None:
    profile_text = ProjectorProfileAnalyzer.PROFILE_PATH.read_text(
        encoding="utf-8"
    ).lower()

    forbidden_terms = [
        "brightlink",
        "epson",
        "fabricante",
        "fornecedor",
        "marca",
        "modelo",
    ]
    assert all(term not in profile_text for term in forbidden_terms)
