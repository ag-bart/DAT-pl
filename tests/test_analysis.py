import pytest
from datpl.analysis import DatComputer


valid_words = ["jabłko", "banan", "wiśnia", "gruszka"]


class MockDatabaseManager:
    def get_word_vector(self, word):

        word_vectors = {
            "jabłko": [0.1, 0.2, 0.3, 0.4, 0.5],
            "banan": [0.2, 0.3, 0.4, 0.5, 0.6],
            "wiśnia": [0.3, 0.4, 0.5, 0.6, 0.7],
            "gruszka": [0.4, 0.5, 0.6, 0.7, 0.8]
        }
        return word_vectors.get(word, [])


@pytest.fixture
def dat_computer_instance():
    database_manager = MockDatabaseManager()
    return DatComputer(database_manager)


def test_minimum_words_property(dat_computer_instance):
    assert dat_computer_instance.minimum_words == 7  # Default value

    dat_computer_instance.minimum_words = 4
    assert dat_computer_instance.minimum_words == 4

    with pytest.raises(ValueError):
        dat_computer_instance.minimum_words = "invalid"

    with pytest.raises(ValueError):
        dat_computer_instance.minimum_words = 0


def test_distance(dat_computer_instance):
    distance = dat_computer_instance.distance("jabłko", "banan")
    assert isinstance(distance, float)
    assert 0.0 <= distance <= 2.0


def test_dat(dat_computer_instance):
    dat_computer_instance.minimum_words = 3
    words = ["jabłko", "banan", "wiśnia", "gruszka"]
    distances = dat_computer_instance.dat(words)
    assert len(distances) == 3  # first 3 words, so 3 combinations of distances


def test_compute_dat_score(dat_computer_instance):
    distances = [0.1, 0.2, 0.3]
    score = dat_computer_instance.compute_dat_score(distances)
    assert isinstance(score, float)
    assert score == pytest.approx(20.0)  # Average of distances


def test_dataset_compute_dat_score(dat_computer_instance):
    dat_computer_instance.minimum_words = 4
    dataset = {
        "participant1": ["jabłko", "banan", "wiśnia", "gruszka"],
        "participant2": ["banan", "gruszka"],
    }
    result = dat_computer_instance.dataset_compute_dat_score(dataset)

    assert "participant1" in result
    assert "participant2" in result

    assert isinstance(result["participant1"].distances, list)
    assert isinstance(result["participant1"].score, float)

    assert isinstance(result["participant2"].distances, list)
    assert len(result["participant2"].distances) == 0  # Empty list
    assert result["participant2"].score is None  # Not enough words

