import pytest


@pytest.mark.django_db
def test_form_crud_is_scoped_to_authenticated_owner(api_client, user, other_user, form):
    from apps.forms.models import Form

    other_form = Form.objects.create(owner=other_user, title="Other owner's form")
    api_client.force_authenticate(user=user)

    listing = api_client.get("/api/v1/forms/")
    own_detail = api_client.get(f"/api/v1/forms/{form.uuid}/")
    other_detail = api_client.get(f"/api/v1/forms/{other_form.uuid}/")

    assert listing.status_code == 200
    assert [item["uuid"] for item in listing.data["results"]] == [str(form.uuid)]
    assert own_detail.status_code == 200
    assert other_detail.status_code == 404