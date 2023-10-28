import pytest
from datpl.processing import DataProcessor


valid_words = ["jabłko", "banan", "wiśnia", "gruszka"]


@pytest.fixture
def data_processor_instance():
    return DataProcessor(valid_words)


def test_clean():
    assert DataProcessor.clean("Jabłko") == "jabłko"
    assert DataProcessor.clean("1@3") == ""
    assert DataProcessor.clean("  word  ") == "word"


def test_validate(data_processor_instance):
    assert data_processor_instance.validate("jabłko") == ("jabłko", "")
    assert data_processor_instance.validate("wiśnia") == ("wiśnia", "")
    assert data_processor_instance.validate("pear") == ("", "pear")


def test_validate_non_string_input(data_processor_instance):
    with pytest.raises(ValueError):
        data_processor_instance.validate(123)


def test_process_words(data_processor_instance):
    words = ["jabłko", "wiśnia", "banan", "gruszka", "pear", "1@3"]
    result = data_processor_instance.process_words(words)
    assert result["valid_words"] == ["jabłko", "wiśnia", "banan", "gruszka"]
    assert result["invalid_words"] == ["pear"]


def test_process_dataset(data_processor_instance):
    dataset = {
        "participant1": ["jabłko", "banan", "wiśnia"],
        "participant2": ["gruszka", "pear", "1@3"],
    }
    result = data_processor_instance.process_dataset(dataset)
    assert result["participant1"]["valid_words"] == ["jabłko", "banan",
                                                     "wiśnia"]
    assert result["participant1"]["invalid_words"] == []
    assert result["participant2"]["valid_words"] == ["gruszka"]
    assert result["participant2"]["invalid_words"] == ["pear"]


def test_extract_valid_words(data_processor_instance):
    dataset = {
        "participant1": {
            "valid_words": ["jabłko", "banan", "wiśnia"], "invalid_words": []
        },
        "participant2": {
            "valid_words": ["gruszka"], "invalid_words": ["pear"]
        },
    }
    result = DataProcessor.extract_valid_words(dataset)
    assert result["participant1"] == ["jabłko", "banan", "wiśnia"]
    assert result["participant2"] == ["gruszka"]


if __name__ == "__main__":
    pytest.main()
