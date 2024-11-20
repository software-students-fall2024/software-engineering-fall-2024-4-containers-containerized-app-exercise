from app import create_app


class Tests:

    app = create_app()

    def test_sanity_check(self):
        expected = True
        actual = True
        assert actual == expected, "Expected true to be equal to true"

    def test_home(self):
        response = self.app.test_client().get("/")
        assert response.status_code == 200
        assert b"ASL Translator" in response.data

    def test_upload_snapshot_nodata(self):
        response = self.app.test_client().post("/upload_snapshot", json={})
        assert response.status_code == 400
        assert b"No image data received" in response.data

    def test_upload_snapshot_invalid_data(self):
        response = self.app.test_client().post(
            "/upload_snapshot", json={"image": "invalid"}
        )
        assert response.status_code == 500

    def test_history_route(self):
        response = self.app.test_client().get("/history")
        assert response.status_code in [200, 500]
