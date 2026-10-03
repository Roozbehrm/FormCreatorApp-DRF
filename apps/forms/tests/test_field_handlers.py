import pytest

from apps.core.exceptions import DomainError
from apps.forms.fields.base import FieldRegistry
from apps.forms.models import Field, FieldOption


@pytest.mark.django_db
def test_all_seven_handlers_registered(form):
    types = {"text", "textarea", "number", "select", "checkbox", "rating", "date"}
    assert types.issubset(FieldRegistry.all())


@pytest.mark.django_db
def test_text_validation(form):
    field = Field.objects.create(form=form, type="text", label="Name", config={"min_length": 3, "max_length": 5})
    assert FieldRegistry.get("text").validate_answer(field, "John").value == "John"
    with pytest.raises(DomainError):
        FieldRegistry.get("text").validate_answer(field, "a")


@pytest.mark.django_db
def test_number_validation(form):
    field = Field.objects.create(
        form=form,
        type="number",
        label="Age",
        config={"min": 1, "max": 10, "is_integer": True},
    )
    assert FieldRegistry.get("number").validate_answer(field, 5).value == 5.0
    with pytest.raises(DomainError):
        FieldRegistry.get("number").validate_answer(field, 11)


@pytest.mark.django_db
def test_select_validation(form):
    field = Field.objects.create(form=form, type="select", label="Color", config={"multiple": False})
    FieldOption.objects.create(field=field, label="Red", value="red")
    assert FieldRegistry.get("select").validate_answer(field, "red").option_values == ["red"]
    with pytest.raises(DomainError):
        FieldRegistry.get("select").validate_answer(field, "blue")


@pytest.mark.django_db
def test_checkbox_validation(form):
    field = Field.objects.create(
        form=form,
        type="checkbox",
        label="Tags",
        config={"min_selected": 1, "max_selected": 2},
    )
    FieldOption.objects.create(field=field, label="A", value="a")
    FieldOption.objects.create(field=field, label="B", value="b")
    assert FieldRegistry.get("checkbox").validate_answer(field, ["a"]).option_values == ["a"]
    with pytest.raises(DomainError):
        FieldRegistry.get("checkbox").validate_answer(field, ["a", "b", "c"])


@pytest.mark.django_db
def test_rating_and_date_validation(form):
    rating = Field.objects.create(
        form=form,
        type="rating",
        label="Score",
        config={"max_value": 5, "allow_half": True},
    )
    assert FieldRegistry.get("rating").validate_answer(rating, 4.5).value == 4.5
    date_field = Field.objects.create(form=form, type="date", label="Date", config={"include_time": False})
    assert FieldRegistry.get("date").validate_answer(date_field, "2026-10-03").value == "2026-10-03"
    with pytest.raises(DomainError):
        FieldRegistry.get("date").validate_answer(date_field, "not-a-date")


def test_invalid_config_rejected():
    with pytest.raises(DomainError):
        FieldRegistry.get("text").validate_config({"unknown": True})
