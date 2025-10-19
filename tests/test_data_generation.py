from __future__ import annotations

from unittest.mock import MagicMock

from tian_hanzi.core.deck_pipeline import DeckBuildConfig, DeckBuilder


def test_deck_build_config_defaults():
    config = DeckBuildConfig()
    assert tuple(config.hsk_levels) == (1, 2, 3)
    assert config.hsk_data_dir == "data/HSK-3.0"
    assert config.output_dir == "data"


def test_deck_builder_builds_exports(tmp_path, monkeypatch):
    dictionary = MagicMock()
    dictionary.definition_lookup.return_value = [
        {"pinyin": "ni3", "definition": "you"},
        {"definition": "surname Ni"},
    ]
    decomposer = MagicMock()
    decomposer.decompose.return_value = {"radical": ["亻"], "graphical": []}
    decomposer.get_radical_meaning.return_value = "person"

    builder = DeckBuilder(
        DeckBuildConfig(hsk_levels=(1,), hsk_data_dir="tests/data", output_dir=str(tmp_path)),
        dictionary=dictionary,
        decomposer=decomposer,
        stroke_counter=lambda value: 1,
    )

    monkeypatch.setattr(
        builder.repository,
        "load_vocabulary",
        MagicMock(
            return_value=[
                {
                    "word": "你",
                    "hsk_level": 1,
                    "frequency_position": 1,
                    "pinyin": "ni3",
                    "meaning": "you",
                    "is_surname": False,
                }
            ]
        ),
    )
    monkeypatch.setattr(builder.repository, "load_hanzi_levels", MagicMock(return_value={"你": 1}))
    monkeypatch.setattr(builder.repository, "extract_hanzi_from_vocabulary", MagicMock(return_value={"你"}))

    exports = builder.build()

    assert exports["vocabulary"][0]["word"] == "你"
    assert exports["hanzi"][0]["components"] == "亻"
    assert exports["components"][0]["radical"] == "亻"
    assert tmp_path.joinpath("vocabulary.csv").exists()
    assert tmp_path.joinpath("hanzi.csv").exists()
    assert tmp_path.joinpath("radicals.csv").exists()
