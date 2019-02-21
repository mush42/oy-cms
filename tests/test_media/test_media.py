import pytest
from io import BytesIO
from pathlib import Path
from flask import _app_ctx_stack
from oy.boot.sqla import db
from oy.models import Image, Document
from oy.media import Media
from oy.media.filters import UnsupportedFileTypeError


THIS = Path(__file__).parent


def test_media(app, client, db):
    Media._add_serving_routes(app)
    imgfile = THIS / "assets" / "image.jpg"
    docfile = THIS / "assets" / "document.pdf"
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
