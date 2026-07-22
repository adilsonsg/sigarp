from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class ProjectorProfile:
    slug: str
    nome: str
    versao: str
    quantidade_minima: int
    exigir_laser: bool
    exigir_full_hd_nativo: bool
    exigir_wifi: bool
    exigir_interatividade: bool
    exigir_curta_ou_ultracurta_distancia: bool

    @classmethod
    def from_file(cls, path: Path) -> ProjectorProfile:
        payload = json.loads(path.read_text(encoding="utf-8"))
        expected = {field.name for field in cls.__dataclass_fields__.values()}
        received = set(payload)
        if received != expected:
            missing = sorted(expected - received)
            unexpected = sorted(received - expected)
            raise ValueError(
                f"Perfil técnico inválido: ausentes={missing}, "
                f"inesperados={unexpected}."
            )
        if not re.fullmatch(r"\d+\.\d+\.\d+", str(payload["versao"])):
            raise ValueError("A versão do perfil técnico deve seguir SemVer.")
        if not isinstance(payload["quantidade_minima"], int) or (
            payload["quantidade_minima"] <= 0
        ):
            raise ValueError("A quantidade mínima deve ser um inteiro positivo.")
        boolean_fields = expected - {
            "slug",
            "nome",
            "versao",
            "quantidade_minima",
        }
        if any(not isinstance(payload[field], bool) for field in boolean_fields):
            raise ValueError("Os requisitos do perfil devem ser booleanos.")
        return cls(**payload)


class ProjectorProfileAnalyzer:
    """Extract projector item data without mixing unrelated document sections."""

    SECTION_HEADING = re.compile(
        r"^\s*(?P<section>\d+(?:\.\d+)+)\.?\s*.*"
        r"(?:item\s*(?P<item>\d+))?.*projetor",
        re.IGNORECASE,
    )
    NUMBERED_HEADING = re.compile(r"^\s*(?P<section>\d+(?:\.\d+)+)\.?")
    CATALOG_ITEM = re.compile(
        r"^\s*(?P<item>\d+)\s*[-\u2013\u2014]\s*.*projetor", re.IGNORECASE
    )
    GENERIC_CATALOG_ITEM = re.compile(r"^\s*\d+\s*[-\u2013\u2014]\s+")
    PROJECTOR = re.compile(
        r"\bprojetor(?:es)?\b|\bdata[ -]?show\b|\bvideoprojetor(?:es)?\b",
        re.IGNORECASE,
    )

    PROFILE_PATH = (
        Path(__file__).resolve().parents[1] / "profiles" / "projectors_v1.json"
    )
    PROFILE = ProjectorProfile.from_file(PROFILE_PATH)

    @classmethod
    def analyze_document(cls, text: str | None) -> dict[str, Any]:
        if not text:
            return cls._empty_result()

        lines = text.splitlines()
        blocks = cls._extract_blocks(lines)
        item_numbers = sorted(
            {
                block["numero_item"]
                for block in blocks
                if block.get("numero_item") is not None
            }
        )
        initial_orders = cls._extract_initial_orders(lines, item_numbers)
        deliveries = cls._extract_delivery_days(text, item_numbers)

        items: list[dict[str, Any]] = []
        grouped: dict[int | None, list[dict[str, Any]]] = {}
        for block in blocks:
            grouped.setdefault(block.get("numero_item"), []).append(block)

        for item_number, item_blocks in grouped.items():
            item = cls._extract_item(item_number, item_blocks)
            if item_number in initial_orders:
                item["quantidade_pedido_inicial"] = initial_orders[item_number]
            if item_number in deliveries:
                item["prazo_entrega_dias"] = deliveries[item_number]
            items.append(item)

        items.sort(
            key=lambda value: (
                value.get("numero_item") is None,
                value.get("numero_item") or 0,
            )
        )
        best = cls._best_item(items)
        suitability = cls.evaluate(best)

        public_blocks = [
            {
                **{key: value for key, value in block.items() if key != "texto"},
                "texto": cls._compact(str(block.get("texto") or ""), 1200),
            }
            for block in blocks
        ]
        return {
            "perfil": cls.profile_dict(),
            "blocos_encontrados": public_blocks,
            "itens_projetor": items,
            "melhor_item": best,
            "avaliacao": suitability,
        }

    @classmethod
    def analyze_pncp_item(
        cls,
        *,
        numero_item: int | None,
        descricao: str | None,
        quantidade: float | int | None,
        unidade_medida: str | None = None,
    ) -> dict[str, Any]:
        text = descricao or ""
        block = {
            "tipo": "item_pncp",
            "numero_item": numero_item,
            "secao": None,
            "linha_inicial": None,
            "linha_final": None,
            "texto": text,
        }
        item = cls._extract_item(numero_item, [block])
        if quantidade is not None:
            item["quantidade_total"] = float(quantidade)
        item["unidade_medida"] = unidade_medida
        return item

    @classmethod
    def evaluate(cls, item: dict[str, Any] | None) -> dict[str, Any]:
        if not item:
            return {
                "adequacao": "EXIGE_ANALISE_HUMANA",
                "pontuacao": 0,
                "requisitos_atendidos": [],
                "requisitos_nao_atendidos": [],
                "requisitos_nao_comprovados": ["item_projetor_isolado"],
                "observacoes": [
                    "Não foi possível isolar uma seção técnica do projetor."
                ],
            }

        required = cls._required_statuses(item)

        met = [name for name, status in required if status is True]
        failed = [name for name, status in required if status is False]
        unknown = [name for name, status in required if status is None]

        if failed:
            adequacy = "INCOMPATIVEL"
        elif not unknown:
            adequacy = "ADEQUADA"
        elif met and len(unknown) <= 2 and not item.get("conflitos"):
            adequacy = "PARCIALMENTE_ADEQUADA"
        else:
            adequacy = "EXIGE_ANALISE_HUMANA"

        score = round((len(met) / len(required)) * 100)
        observations: list[str] = []
        if item.get("conflitos"):
            observations.append("Há valores conflitantes entre blocos do documento.")

        return {
            "adequacao": adequacy,
            "pontuacao": score,
            "requisitos_atendidos": met,
            "requisitos_nao_atendidos": failed,
            "requisitos_nao_comprovados": unknown,
            "observacoes": observations,
        }

    @classmethod
    def profile_dict(cls) -> dict[str, Any]:
        profile = cls.PROFILE
        return {
            "slug": profile.slug,
            "nome": profile.nome,
            "versao": profile.versao,
            "quantidade_minima": profile.quantidade_minima,
            "exigir_laser": profile.exigir_laser,
            "exigir_full_hd_nativo": profile.exigir_full_hd_nativo,
            "exigir_wifi": profile.exigir_wifi,
            "exigir_interatividade": profile.exigir_interatividade,
            "exigir_curta_ou_ultracurta_distancia": (
                profile.exigir_curta_ou_ultracurta_distancia
            ),
        }

    @classmethod
    def _extract_blocks(cls, lines: list[str]) -> list[dict[str, Any]]:
        blocks: list[dict[str, Any]] = []
        occupied: set[tuple[int, int]] = set()

        for index, line in enumerate(lines):
            normalized = cls._normalize(line)
            match = cls.SECTION_HEADING.match(normalized)
            if not match or not cls.PROJECTOR.search(normalized):
                continue
            if "tabela de itens" not in normalized and not re.search(
                r"\bitem\s*\d+\s*:", normalized
            ):
                continue
            section = match.group("section")
            item_number = cls._item_number_from_heading(normalized, match)
            end = cls._section_end(lines, index, section)
            key = (index, end)
            if key not in occupied:
                blocks.append(
                    cls._block(
                        lines,
                        index,
                        end,
                        kind="secao_tecnica",
                        item_number=item_number,
                        section=section,
                    )
                )
                occupied.add(key)

        for index, line in enumerate(lines):
            normalized = cls._normalize(line)
            match = cls.CATALOG_ITEM.match(normalized)
            if not match:
                continue
            end = min(len(lines), index + 45)
            for cursor in range(index + 1, end):
                if cls.GENERIC_CATALOG_ITEM.match(cls._normalize(lines[cursor])):
                    end = cursor
                    break
            key = (index, end)
            if key not in occupied:
                blocks.append(
                    cls._block(
                        lines,
                        index,
                        end,
                        kind="catalogo_pncp",
                        item_number=int(match.group("item")),
                        section=None,
                    )
                )
                occupied.add(key)

        for index, line in enumerate(lines):
            normalized = cls._normalize(line)
            if not cls.PROJECTOR.search(normalized):
                continue
            start = max(0, index - 4)
            end = min(len(lines), index + 7)
            window = "\n".join(lines[start:end])
            item_number = cls._nearby_item_number(lines, index)
            if item_number is None or not re.search(
                r"\b(?:und|unid|unidade)s?\.?\s*\d+\b",
                cls._normalize(window),
            ):
                continue
            key = (start, end)
            if any(start >= a and end <= b for a, b in occupied):
                continue
            blocks.append(
                cls._block(
                    lines,
                    start,
                    end,
                    kind="linha_tabela",
                    item_number=item_number,
                    section=None,
                )
            )
            occupied.add(key)

        full_text = "\n".join(lines)
        if (
            not blocks
            and len(full_text) <= 5000
            and cls.PROJECTOR.search(cls._normalize(full_text))
        ):
            blocks.append(
                cls._block(
                    lines,
                    0,
                    len(lines),
                    kind="descricao_curta",
                    item_number=None,
                    section=None,
                )
            )

        return blocks

    @classmethod
    def _section_end(cls, lines: list[str], start: int, section: str) -> int:
        current = tuple(int(part) for part in section.split("."))
        maximum = min(len(lines), start + 220)
        for index in range(start + 1, maximum):
            match = cls.NUMBERED_HEADING.match(cls._normalize(lines[index]))
            if not match:
                continue
            candidate = tuple(int(part) for part in match.group("section").split("."))
            if candidate[: len(current)] == current:
                continue
            if candidate > current:
                return index
        return maximum

    @classmethod
    def _extract_item(
        cls,
        item_number: int | None,
        blocks: list[dict[str, Any]],
    ) -> dict[str, Any]:
        texts = [str(block.get("texto") or "") for block in blocks]
        text = "\n".join(texts)
        normalized = cls._normalize(text)

        quantity_values = cls._quantity_values(blocks)
        initial_quantity = None
        model = cls._first_group(
            text,
            [
                r"modelo\s+de\s+refer[eê]ncia\s*:\s*([^\n.;]{3,90}?)(?=\s+ou\s+equivalente|[.;\n])",
                r"refer[eê]ncia\s*:\s*([^\n.;]{3,90}?)(?=\s+ou\s+equivalente|[.;\n])",
            ],
        )
        resolutions = cls._native_resolutions(text)
        native_resolution = resolutions[0] if resolutions else None
        supported = cls._supported_resolutions(text)
        lumens = cls._integer_values(
            normalized,
            r"(\d{1,2}(?:[\.\s]\d{3})|\d{3,5})\s*(?:ansi\s*)?(?:lm|lumens?|l[uú]mens?)\b",
        )
        lamp_watts = cls._integer_values(
            normalized,
            r"(?:potencia(?:\s+da)?\s+lampada|lampada[^\n]{0,40}potencia)\D{0,20}(\d{2,4})\s*w\b",
        )
        warranty = cls._first_int(
            normalized,
            [
                r"garantia(?:\s+minima)?(?:\s+de)?\s*(\d+)\s*mes",
                r"garantia[^\n]{0,50}(\d+)\s*mes",
            ],
        )
        minimum_distance = cls._first_float(
            normalized,
            [
                r"distancia\s+minima(?:\s+da)?\s+tela\s*:\s*(\d+(?:[\.,]\d+)?)\s*m\b",
                r"distancia\s+de\s+projecao[^\n]{0,50}(\d+(?:[\.,]\d+)?)\s*m\b",
            ],
        )

        has_laser = bool(re.search(r"\blaser\b", normalized))
        has_uhe = bool(re.search(r"\b(?:lampada\s*)?uhe\b", normalized))
        has_lamp = bool(re.search(r"\blampada\b", normalized))
        light_source = None
        conflicts: list[str] = []
        if has_laser and (has_uhe or has_lamp):
            light_source = "CONFLITANTE"
            conflicts.append("fonte_luz: laser e lâmpada")
            laser: bool | None = None
        elif has_laser:
            light_source = "LASER"
            laser = True
        elif has_uhe:
            light_source = "LAMPADA_UHE"
            laser = False
        elif has_lamp:
            light_source = "LAMPADA"
            laser = False
        else:
            laser = None

        if len(lamp_watts) > 1:
            conflicts.append("potencia_lampada_w: " + ", ".join(map(str, lamp_watts)))
        if len(resolutions) > 1:
            conflicts.append(
                "resolucao_nativa: "
                + ", ".join(value["texto"] for value in resolutions)
            )

        full_hd_native = cls._full_hd_status(native_resolution)
        wifi = cls._boolean_term(
            normalized,
            positive=[r"\bwi[ -]?fi\b", r"\bwireless\b", r"\bsem fio\b"],
            negative=[r"\bsem\s+(?:wi[ -]?fi|conectividade\s+sem fio)\b"],
        )
        interactive = cls._boolean_term(
            normalized,
            positive=[r"\binterativ[oa]s?\b"],
            negative=[r"\bsem interatividade\b", r"\bnao interativ[oa]\b"],
        )
        ultra_short = cls._boolean_term(
            normalized,
            positive=[
                r"\bultra[ -]?curta distancia\b",
                r"\bultra[ -]?short throw\b",
            ],
            negative=[],
        )
        short_throw = cls._boolean_term(
            normalized,
            positive=[r"\bcurta distancia\b", r"\bshort throw\b"],
            negative=[r"\blonga distancia\b", r"\blong throw\b"],
        )
        technology = "3LCD" if re.search(r"\b3\s*lcd\b|\b3lcd\b", normalized) else None
        evidence = {
            "blocos": [
                {
                    "tipo": block.get("tipo"),
                    "linha_inicial": block.get("linha_inicial"),
                    "linha_final": block.get("linha_final"),
                    "secao": block.get("secao"),
                    "trecho": cls._compact(str(block.get("texto") or ""), 700),
                }
                for block in blocks
            ]
        }

        return {
            "numero_item": item_number,
            "quantidade_total": max(quantity_values) if quantity_values else None,
            "quantidade_pedido_inicial": initial_quantity,
            "unidade_medida": cls._unit(text),
            "modelo_referencia": model,
            "tecnologia_projecao": technology,
            "fonte_luz": light_source,
            "laser": laser,
            "potencias_lampada_w": lamp_watts,
            "resolucao_nativa": native_resolution,
            "resolucoes_suportadas": supported,
            "full_hd_nativo": full_hd_native,
            "luminosidade_lumens": max(lumens) if lumens else None,
            "wifi": wifi,
            "interativo": interactive,
            "curta_distancia": short_throw,
            "ultracurta_distancia": ultra_short,
            "distancia_minima_tela_m": minimum_distance,
            "garantia_meses": warranty,
            "prazo_entrega_dias": None,
            "conflitos": conflicts,
            "evidencias": evidence,
        }

    @classmethod
    def _quantity_values(cls, blocks: list[dict[str, Any]]) -> list[int]:
        values: list[int] = []
        for block in blocks:
            text = cls._normalize(str(block.get("texto") or ""))
            kind = block.get("tipo")
            patterns = [r"quantidade\s+total\s*:\s*(\d+)"]
            if kind == "linha_tabela":
                patterns.extend(
                    [
                        r"\b(?:und|unid|unidade)s?\.?\s*(\d+)\b",
                        r"\bprojetor[^\n]{0,180}\b(?:und|unid)\.?\s*(\d+)\b",
                    ]
                )
            for pattern in patterns:
                for match in re.finditer(pattern, text):
                    values.append(int(match.group(1)))
        return sorted(set(values))

    @classmethod
    def _extract_initial_orders(
        cls, lines: list[str], item_numbers: list[int]
    ) -> dict[int, int]:
        if not item_numbers:
            return {}
        normalized_lines = [cls._normalize(line) for line in lines]
        starts = [
            index
            for index, line in enumerate(normalized_lines)
            if "pedido inicial" in line or "pedido minimo" in line
        ]
        result: dict[int, int] = {}
        for start in starts:
            end = min(len(lines), start + 100)
            for item_number in item_numbers:
                pattern = re.compile(rf"^\s*{item_number}\s+.*projetor.*?\s(\d+)\s*$")
                for index in range(start, end):
                    match = pattern.search(normalized_lines[index])
                    if match:
                        result[item_number] = int(match.group(1))
                        break
        return result

    @classmethod
    def _extract_delivery_days(
        cls, text: str, item_numbers: list[int]
    ) -> dict[int, int]:
        normalized = re.sub(r"\s+", " ", cls._normalize(text))
        result: dict[int, int] = {}
        for item_number in item_numbers:
            patterns = [
                (
                    rf"prazo de ate\s+(\d+)[^\n]{{0,180}}"
                    rf"item\s*{item_number}[^\n]{{0,80}}projetor"
                ),
                (
                    rf"item\s*{item_number}[^\n]{{0,80}}projetor"
                    rf"[^\n]{{0,180}}prazo de ate\s+(\d+)"
                ),
            ]
            value = cls._first_int(normalized, patterns)
            if value is not None:
                result[item_number] = value
        return result

    @classmethod
    def _native_resolutions(cls, text: str) -> list[dict[str, int | str]]:
        normalized = cls._normalize(text)
        values: list[dict[str, int | str]] = []
        dimension = r"(\d{1,2}(?:[.\s]\d{3})|\d{3,4})"
        patterns = [
            rf"resolucao\s+nativa\s*:?\s*{dimension}\s*[x\u00d7]\s*{dimension}",
            rf"\bresolucao\s*:\s*{dimension}\s*[x\u00d7]\s*{dimension}",
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, normalized):
                width = int(re.sub(r"\D", "", match.group(1)))
                height = int(re.sub(r"\D", "", match.group(2)))
                value = {
                    "largura": width,
                    "altura": height,
                    "texto": f"{width} x {height}",
                }
                if value not in values:
                    values.append(value)
        return values

    @classmethod
    def _supported_resolutions(cls, text: str) -> list[str]:
        normalized = cls._normalize(text)
        values: set[str] = set()
        for match in re.finditer(r"\b(?:480|576|720|1080|2160)[ip]\b", normalized):
            values.add(match.group(0))
        return sorted(values)

    @staticmethod
    def _full_hd_status(resolution: dict[str, Any] | None) -> bool | None:
        if not resolution:
            return None
        return int(resolution["largura"]) >= 1920 and int(resolution["altura"]) >= 1080

    @classmethod
    def _minimum_quantity_status(cls, item: dict[str, Any]) -> bool | None:
        value = item.get("quantidade_total")
        if value is None:
            return None
        return float(value) >= cls.PROFILE.quantidade_minima

    @classmethod
    def _required_statuses(cls, item: dict[str, Any]) -> list[tuple[str, bool | None]]:
        profile = cls.PROFILE
        required: list[tuple[str, bool | None]] = [
            (
                f"quantidade_minima_{profile.quantidade_minima}",
                cls._minimum_quantity_status(item),
            )
        ]
        optional_requirements = [
            (profile.exigir_laser, "fonte_luz_laser", item.get("laser")),
            (
                profile.exigir_full_hd_nativo,
                "full_hd_nativo",
                item.get("full_hd_nativo"),
            ),
            (profile.exigir_wifi, "wifi", item.get("wifi")),
            (
                profile.exigir_interatividade,
                "interativo",
                item.get("interativo"),
            ),
            (
                profile.exigir_curta_ou_ultracurta_distancia,
                "curta_ou_ultracurta_distancia",
                cls._throw_status(item),
            ),
        ]
        required.extend(
            (name, status) for enabled, name, status in optional_requirements if enabled
        )
        return required

    @staticmethod
    def _throw_status(item: dict[str, Any]) -> bool | None:
        if item.get("ultracurta_distancia") is True:
            return True
        if item.get("curta_distancia") is True:
            return True
        if (
            item.get("ultracurta_distancia") is False
            or item.get("curta_distancia") is False
        ):
            return False
        return None

    @classmethod
    def _best_item(cls, items: list[dict[str, Any]]) -> dict[str, Any] | None:
        if not items:
            return None
        return max(
            items,
            key=lambda item: sum(
                value is not None
                for key, value in item.items()
                if key not in {"evidencias", "conflitos"}
            ),
        )

    @classmethod
    def _block(
        cls,
        lines: list[str],
        start: int,
        end: int,
        *,
        kind: str,
        item_number: int | None,
        section: str | None,
    ) -> dict[str, Any]:
        return {
            "tipo": kind,
            "numero_item": item_number,
            "secao": section,
            "linha_inicial": start + 1,
            "linha_final": end,
            "texto": "\n".join(lines[start:end]).strip(),
        }

    @classmethod
    def _item_number_from_heading(
        cls, normalized: str, match: re.Match[str]
    ) -> int | None:
        explicit = match.groupdict().get("item")
        if explicit:
            return int(explicit)
        item_match = re.search(r"\bitem\s*(\d+)\b", normalized)
        return int(item_match.group(1)) if item_match else None

    @classmethod
    def _nearby_item_number(cls, lines: list[str], index: int) -> int | None:
        current = cls._normalize(lines[index])
        same_line = re.search(r"^\s*(\d{1,4})\s*[-\u2013\u2014].*projetor", current)
        if same_line:
            return int(same_line.group(1))

        for cursor in range(index - 1, max(-1, index - 5), -1):
            normalized = cls._normalize(lines[cursor])
            standalone = re.fullmatch(r"\s*(\d{1,4})\s*", normalized)
            if standalone:
                return int(standalone.group(1))
            item_match = re.search(r"\bitem\s*(\d+)\b", normalized)
            if item_match:
                return int(item_match.group(1))
        return None

    @staticmethod
    def _boolean_term(
        text: str,
        *,
        positive: list[str],
        negative: list[str],
    ) -> bool | None:
        if any(re.search(pattern, text) for pattern in negative):
            return False
        if any(re.search(pattern, text) for pattern in positive):
            return True
        return None

    @staticmethod
    def _first_group(text: str, patterns: list[str]) -> str | None:
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return re.sub(r"\s+", " ", match.group(1)).strip(" -:,")
        return None

    @staticmethod
    def _first_int(text: str, patterns: list[str]) -> int | None:
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
            if match:
                return int(match.group(1))
        return None

    @staticmethod
    def _first_float(text: str, patterns: list[str]) -> float | None:
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
            if match:
                return float(match.group(1).replace(",", "."))
        return None

    @staticmethod
    def _integer_values(text: str, pattern: str) -> list[int]:
        values: set[int] = set()
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            digits = re.sub(r"\D", "", match.group(1))
            if digits:
                values.add(int(digits))
        return sorted(values)

    @staticmethod
    def _unit(text: str) -> str | None:
        match = re.search(r"\b(UND|UNID|UNIDADE)\.?\b", text, re.IGNORECASE)
        return match.group(1).upper() if match else None

    @staticmethod
    def _compact(text: str, limit: int) -> str:
        compact = re.sub(r"\s+", " ", text).strip()
        return compact[:limit]

    @staticmethod
    def _normalize(value: str | None) -> str:
        if not value:
            return ""
        decomposed = unicodedata.normalize("NFKD", str(value).lower())
        return "".join(
            character
            for character in decomposed
            if not unicodedata.combining(character)
        )

    @classmethod
    def _empty_result(cls) -> dict[str, Any]:
        return {
            "perfil": cls.profile_dict(),
            "blocos_encontrados": [],
            "itens_projetor": [],
            "melhor_item": None,
            "avaliacao": cls.evaluate(None),
        }
