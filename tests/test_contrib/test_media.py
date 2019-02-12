import pytest
from io import BytesIO
from pathlib import Path
from oy.contrib.media import Media, Image, Document
from oy.contrib.media.filters import UnsupportedFileTypeError


THIS = Path(__file__).parent


def test_basic_media(app, client, db):
    media = Media(serve_files=True)
    # Should fail without `DEPOT_STORAGES` config
    with pytest.raises(LookupError):
        media.init_app(app)

    app.config["DEPOT_MEDIA_STORAGES"] = dict(
        media_storage={"depot.storage_path": str(THIS/"media")}
    )
    media.init_app(app)

    imgfile = THIS/"assets"/"image.jpg"
    docfile = THIS/"assets"/"document.pdf"
    image = Image(title="Image", uploaded_file=open(imgfile, "rb"))
    document = Document(title="Document", uploaded_file=open(docfile, "rb"))
    db.session.add_all([image, document])
    db.session.commit()

    assert image.uploaded_file.file.read() == imgfile.read_bytes()
    assert document.uploaded_file.file.read() == docfile.read_bytes()

    resp = client.get(f"/media/images/{image.file_id}")
    assert resp.status_code == 200
    assert resp.content_type == "image/jpeg"
    assert resp.body == imgfile.read_bytes()

    resp = client.get(f"/media/documents/{document.file_id}")
    assert resp.status_code == 200
    assert resp.content_type == "application/pdf"
    assert resp.body == docfile.read_bytes()

    # Shouldn't accept arbitrary files
    arbitrary_file = BytesIO()
    arbitrary_file.write(b"arbitrary data")
    with pytest.raises(UnsupportedFileTypeError):
        not_accepted_image = Image(title="Nope", uploaded_file=arbitrary_file)
