import os
import re
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import jsonify, request

from utils.app_logger import get_app_logger
from utils.input_sanitizer import InputSanitizer


logger = get_app_logger()


class ContactoController:

    @staticmethod
    def enviar_consulta():
        datos = request.get_json(silent=True) or {}
        datos = InputSanitizer.sanitizar_campos(
            datos,
            campos_texto=["nombre", "apellido", "empresa", "mensaje"],
            campos_email=["email"],
        )

        nombre = datos.get("nombre")
        apellido = datos.get("apellido")
        email = datos.get("email")
        empresa = datos.get("empresa")
        mensaje = datos.get("mensaje")

        if not nombre or not apellido or not email or not mensaje:
            return jsonify({
                "mensaje": "Completá nombre, apellido, email y mensaje."
            }), 400

        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            return jsonify({"mensaje": "Ingresá un email válido."}), 400

        resend_api_key = (os.getenv("RESEND_API_KEY") or "").strip()
        resend_from = (
            os.getenv("RESEND_FROM", "Trukly <onboarding@resend.dev>").strip()
        )
        mail_to = (os.getenv("MAIL_TO") or "").strip()

        if not resend_api_key or not mail_to:
            return jsonify({
                "mensaje": "El envío de consultas todavía no está configurado."
            }), 500

        asunto = "Nueva consulta desde Trukly"
        cuerpo = (
            "Recibiste una nueva consulta desde la página principal de Trukly.\n\n"
            f"Nombre: {nombre} {apellido}\n"
            f"Email: {email}\n"
            f"Empresa: {empresa or 'No indicada'}\n\n"
            f"Mensaje:\n{mensaje}\n"
        )

        payload = {
            "from": resend_from,
            "to": [mail_to],
            "subject": asunto,
            "text": cuerpo,
            "reply_to": email,
        }

        request_resend = Request(
            "https://api.resend.com/emails",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {resend_api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Trukly/1.0",
            },
            method="POST",
        )

        try:
            with urlopen(request_resend, timeout=15) as respuesta:
                if respuesta.status < 200 or respuesta.status >= 300:
                    raise RuntimeError("Resend no aceptó el email")

            return jsonify({
                "mensaje": "Consulta enviada correctamente. Te vamos a contactar pronto."
            }), 200

        except HTTPError as error:
            detalle = error.read().decode("utf-8", errors="replace")
            logger.exception(
                "Resend rechazo la consulta de contacto: %s - %s",
                error.code,
                detalle,
            )
            return jsonify({
                "mensaje": "No se pudo enviar la consulta. Revisá la configuración de Resend."
            }), 500

        except (URLError, TimeoutError, Exception):
            logger.exception("No se pudo enviar la consulta de contacto")
            return jsonify({
                "mensaje": "No se pudo enviar la consulta. Intentá nuevamente."
            }), 500
