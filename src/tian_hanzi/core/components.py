"""Component analysis utilities for the deck pipeline."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from .cards import clean_surname_from_definition
from .pinyin import numbered_to_accented

__all__ = ["ComponentAnalyzer", "ComponentStatistics"]


@dataclass
class ComponentStatistics:
    usage: Counter
    weighted_by_level: dict[int, Counter]
    details: dict[str, dict]


class ComponentAnalyzer:
    """Derive component metadata for a collection of hanzi."""

    def __init__(self, decomposer, dictionary) -> None:
        self.decomposer = decomposer
        self.dictionary = dictionary

    def analyse(
        self,
        hanzi: Iterable[str],
        hanzi_to_hsk: dict[str, int],
    ) -> tuple[dict[str, dict], ComponentStatistics]:
        hanzi_data: dict[str, dict] = {}
        usage = Counter()
        by_level: dict[int, Counter] = {1: Counter(), 2: Counter(), 3: Counter()}

        for index, char in enumerate(sorted(hanzi)):
            definitions = self.dictionary.definition_lookup(char)
            if not definitions:
                continue
            pinyin = numbered_to_accented(definitions[0].get("pinyin", ""))
            combined = "; ".join(
                entry.get("definition", "") for entry in definitions if entry.get("definition")
            )
            meaning, is_surname = clean_surname_from_definition(combined)

            try:
                decomposition = self.decomposer.decompose(char)
            except Exception:
                decomposition = {}
            components = self._normalise_components(char, decomposition)
            for component in components:
                usage[component] += 1
                level = hanzi_to_hsk.get(char)
                if level in by_level:
                    by_level[level][component] += 1

            hanzi_data[char] = {
                "hanzi": char,
                "pinyin": pinyin,
                "meaning": meaning,
                "components": components,
                "component_count": len(components),
                "hsk_level": hanzi_to_hsk.get(char),
                "is_surname": is_surname,
            }
            if (index + 1) % 100 == 0:
                print(f"  Processed {index + 1} hanzi...")

        component_details = self._score_components(usage, by_level)
        stats = ComponentStatistics(usage=usage, weighted_by_level=by_level, details=component_details)
        return hanzi_data, stats

    def _normalise_components(self, char: str, decomposition: dict | None) -> list[str]:
        if not decomposition:
            return []
        components: list[str] = []
        radical_components = decomposition.get("radical", []) or []
        graphical_components = decomposition.get("graphical", []) or []

        for component in radical_components:
            if not component or component == char:
                continue
            if component == "No glyph available":
                continue
            if component not in components:
                components.append(component)

        if "No glyph available" in radical_components:
            for component in graphical_components:
                if component and component != char and component not in components:
                    components.append(component)

        return components

    def _score_components(
        self,
        usage: Counter,
        by_level: dict[int, Counter],
    ) -> dict[str, dict]:
        component_data: dict[str, dict] = {}
        for component, count in usage.items():
            try:
                meaning = self.decomposer.get_radical_meaning(component)
            except Exception:
                meaning = ""
            if not meaning or meaning == component:
                meaning = f"Component {component}"

            usage_hsk1 = by_level[1].get(component, 0)
            usage_hsk2 = by_level[2].get(component, 0)
            usage_hsk3 = by_level[3].get(component, 0)
            weighted = usage_hsk1 * 5 + usage_hsk2 * 3 + usage_hsk3
            component_data[component] = {
                "component": component,
                "meaning": meaning,
                "productivity_score": weighted,
                "usage_count": count,
                "usage_hsk1": usage_hsk1,
                "usage_hsk2": usage_hsk2,
                "usage_hsk3": usage_hsk3,
            }
        return component_data
