import os
from pathlib import Path
import secrets

from flask import Flask, redirect, render_template, request, session, url_for

from storage import save_record


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("HORIZONTE_SECRET_KEY") or secrets.token_hex(32),
        MAX_CONTENT_LENGTH=16 * 1024,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Strict",
        TEMPLATES_AUTO_RELOAD=True,
        SEND_FILE_MAX_AGE_DEFAULT=0,
        LOGO_PRINCIPAL="img/logos/logo-principal.svg",
        LOGO_SECUNDARIO="img/logos/logo-secundario.svg",
    )
    if test_config:
        app.config.update(test_config)

    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = app.make_default_options_response()
            response.status_code = 204
            return response

    @app.after_request
    def add_cors_and_disable_cache(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Max-Age"] = "86400"
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.context_processor
    def logo_sources():
        sources = {}
        for name in ("PRINCIPAL", "SECUNDARIO"):
            relative = Path(app.config[f"LOGO_{name}"])
            # Las imágenes copiadas tienen prioridad sobre los SVG de ejemplo.
            for extension in (".png", ".webp", ".jpg", ".jpeg", ".svg"):
                candidate = relative.with_suffix(extension)
                path = Path(app.static_folder) / candidate
                if path.is_file():
                    sources[f"logo_{name.lower()}_src"] = url_for(
                        "static", filename=candidate.as_posix(), v=path.stat().st_mtime_ns,
                    )
                    break
            else:
                sources[f"logo_{name.lower()}_src"] = url_for(
                    "static", filename=relative.as_posix(),
                )
        return sources

    def show_form(error=None, values=None, status=200):
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_urlsafe(32)
        return render_template(
            "index.html",
            error=error,
            values=values or {},
            csrf_token=session["csrf_token"],
        ), status

    @app.get("/")
    def index():
        return show_form()

    @app.post("/guardar")
    def guardar():
        token = request.form.get("csrf_token", "")
        expected = session.get("csrf_token", "")
        if not expected or not secrets.compare_digest(token.encode(), expected.encode()):
            return show_form("La sesión del formulario venció. Inténtalo nuevamente.", status=400)

        allowed = {"csrf_token", "visitante", "referencia"}
        if set(request.form) != allowed or any(len(request.form.getlist(key)) != 1 for key in allowed):
            return show_form("Envía únicamente los dos campos de prueba.", status=400)

        values = {key: request.form[key].strip() for key in ("visitante", "referencia")}
        for key, limit in (("visitante", 60), ("referencia", 40)):
            value = values[key]
            if not value or len(value) > limit or any(ord(char) < 32 or ord(char) == 127 for char in value):
                return show_form(
                    "Completa visitante (hasta 60 caracteres) y referencia (hasta 40), en una sola línea.",
                    values, 400,
                )

        try:
            save_record(None, **values)
        except OSError:
            app.logger.error("No se pudo enviar los datos a Telegram.")
            return show_form("No se pudo guardar. Inténtalo otra vez.", values, 503)

        return redirect(url_for("gracias"), code=303)

    @app.get("/gracias")
    def gracias():
        return render_template("gracias.html")

    @app.errorhandler(413)
    def too_large(_error):
        return show_form("El formulario supera el tamaño permitido.", status=413)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=True)
