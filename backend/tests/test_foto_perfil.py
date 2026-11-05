import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from flask_jwt_extended import JWTManager, create_access_token
from PIL import Image
from werkzeug.datastructures import FileStorage

from controllers.perfil_controller import PerfilController
from db_instance import db
from models.usuario_model import UsuarioModel
from routes.perfil_routes import perfil_routes


def imagen(formato="PNG"):
    archivo = io.BytesIO()
    with Image.new("RGB", (16, 16), "blue") as foto:
        foto.save(archivo, format=formato)
    return archivo.getvalue()


class FotoPerfilTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_admin_estadisticas_mensuales import AdminEstadisticasMensualesTest
        cls.fixture = AdminEstadisticasMensualesTest
        cls.fixture.setUpClass()
        cls.fixture.app.config["JWT_SECRET_KEY"] = "test-only-profile-photo-secret-key"
        JWTManager(cls.fixture.app)
        cls.fixture.app.register_blueprint(perfil_routes)

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory(prefix="trukly-foto-test-")
        self.addCleanup(self.temporal.cleanup)
        self.carpeta = Path(self.temporal.name)
        carpeta_patch = patch.object(PerfilController, "CARPETA_PERFILES", str(self.carpeta))
        carpeta_patch.start()
        self.addCleanup(carpeta_patch.stop)
        self.anterior = self.carpeta / "anterior.png"
        self.anterior.write_bytes(imagen())
        self.usuario = db.session.get(UsuarioModel, 1)
        self.usuario.estado = "activo"
        self.usuario.foto_perfil = "/uploads/perfiles/anterior.png"
        db.session.commit()
        token = create_access_token(identity="1", additional_claims={"rol": "chofer"})
        self.headers = {"Authorization": "Bearer " + token}
        self.client = self.fixture.app.test_client()

    def tearDown(self):
        db.session.rollback()
        db.session.remove()

    def subir(self, contenido=None, nombre="foto.png"):
        return self.client.post("/api/perfil/foto", headers=self.headers,
            data={"foto": (io.BytesIO(contenido if contenido is not None else imagen()), nombre)},
            content_type="multipart/form-data")

    def comprobar_anterior(self):
        db.session.refresh(self.usuario)
        self.assertEqual(self.usuario.foto_perfil, "/uploads/perfiles/anterior.png")
        self.assertTrue(self.anterior.exists())
        self.assertEqual([p.name for p in self.carpeta.iterdir()], ["anterior.png"])

    def test_rechaza_archivos_falsos_vacios_corruptos_y_extension_incorrecta(self):
        for contenido, nombre in [(b"Esto no es una foto", "foto.png"), (b"", "foto.png"),
                (imagen()[:-20], "foto.png"), (imagen("JPEG")[:-10], "foto.jpg"),
                (imagen(), "foto.jpg"), (imagen(), "foto.svg")]:
            with self.subTest(nombre=nombre, longitud=len(contenido)):
                r = self.subir(contenido, nombre)
                self.assertEqual(r.status_code, 400, r.get_json())
                self.comprobar_anterior()

    def test_rechaza_archivo_mayor_a_tres_mb(self):
        r = self.subir(b"x" * (3 * 1024 * 1024 + 1))
        self.assertEqual(r.status_code, 400, r.get_json())
        self.comprobar_anterior()

    def test_acepta_png_jpeg_y_webp_y_se_pueden_servir(self):
        for formato, extension in [("PNG", "png"), ("JPEG", "jpg"), ("JPEG", "JPEG"), ("WEBP", "webp")]:
            with self.subTest(formato=formato, extension=extension):
                anterior = self.carpeta / Path(self.usuario.foto_perfil).name
                contenido = imagen(formato)
                r = self.subir(contenido, "foto." + extension)
                self.assertEqual(r.status_code, 200, r.get_json())
                self.assertFalse(anterior.exists())
                ruta = r.get_json()["foto_perfil"]
                nueva = self.carpeta / Path(ruta).name
                self.assertEqual(nueva.read_bytes(), contenido)
                respuesta = self.client.get(ruta)
                self.assertEqual(respuesta.status_code, 200)
                self.assertEqual(respuesta.data, contenido)
                respuesta.close()

    def test_error_de_commit_conserva_anterior_y_limpia_nueva(self):
        with patch.object(db.session, "commit", side_effect=RuntimeError("Prueba")), patch("controllers.perfil_controller.logger"):
            r = self.subir()
        self.assertEqual(r.status_code, 500, r.get_json())
        self.comprobar_anterior()

    def test_error_de_escritura_conserva_anterior_y_limpia_archivo_parcial(self):
        def fallar(archivo, ruta):
            Path(ruta).write_bytes(b"parcial")
            raise OSError("Prueba")
        with patch.object(FileStorage, "save", fallar), patch("controllers.perfil_controller.logger"):
            r = self.subir()
        self.assertEqual(r.status_code, 500, r.get_json())
        self.comprobar_anterior()

    def test_fallo_al_crear_carpeta_es_controlado(self):
        with patch("controllers.perfil_controller.os.makedirs", side_effect=OSError("Prueba")), patch("controllers.perfil_controller.logger"):
            r = self.subir()
        self.assertEqual(r.status_code, 500, r.get_json())
        self.comprobar_anterior()

    def test_fallo_limpiando_anterior_no_deshace_nueva_confirmada(self):
        with patch.object(PerfilController, "_eliminar_foto_anterior", side_effect=OSError("Prueba")), patch("controllers.perfil_controller.logger"):
            r = self.subir()
        self.assertEqual(r.status_code, 200, r.get_json())
        db.session.refresh(self.usuario)
        self.assertEqual(self.usuario.foto_perfil, r.get_json()["foto_perfil"])
        self.assertTrue((self.carpeta / Path(self.usuario.foto_perfil).name).exists())

    def test_rechaza_dimensiones_excesivas_antes_de_decodificar(self):
        foto = unittest.mock.MagicMock()
        foto.format = "PNG"
        foto.width, foto.height = 6000, 6000
        foto.__enter__.return_value = foto
        with patch("services.foto_perfil_service.Image.open", return_value=foto):
            r = self.subir()
        self.assertEqual(r.status_code, 400, r.get_json())
        foto.load.assert_not_called()
        self.comprobar_anterior()
