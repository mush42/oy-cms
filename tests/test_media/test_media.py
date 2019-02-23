import pytest
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from oy.boot.sqla import db
from oy.contrib.media.models import Image, Document
from oy.contrib.media import Media
from oy.contrib.media.utils import UnsupportedFileTypeError


ASSETS_DIR = Path(__file__).parent / "assets"
TEMP_DIR = TemporaryDirectory()


def test_media(app, client, db):
    config = {
        "SERVE_MEDIA_FILES": True,
        "DEPOT_MEDIA_STORAGES": dict(
            media_storage={"depot.storage_path": TEMP_DIR.name}
        ),
    }

    app.config.update(config)
    Media(app)
    imgfile = ASSETS_DIR / "image.jpg"
    docfile = ASSETS_DIR / "document.pdf"
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

    # Some housekeeping
    TEMP_DIR.cleanup()
