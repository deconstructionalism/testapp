from flask import abort, Blueprint, jsonify
from app.summarize.lib.differencer import update_database
from app.summarize.lib import SummarizerModels

summarize = Blueprint("summarize", __name__, url_prefix="/summarize")


@summarize.route("/", methods=["GET"])
def index_models():
    return jsonify(SummarizerModels.get_all_models())


@summarize.route("/<app_name>", methods=["GET"])
def index_app_models(app_name: str):
    app_models = SummarizerModels.get_app_models(app_name)

    return jsonify(app_models)


@summarize.route("/<app_name>/<model_name>", methods=["GET"])
def show_model(app_name: str, model_name: str):
    model = SummarizerModels.get_model(app_name, model_name)

    return jsonify(model)


@summarize.route("/<app_name>/<model_name>/<field_name>", methods=["GET"])
def show_field(app_name: str, model_name: str, field_name: str):
    field = SummarizerModels.get_field(app_name, model_name, field_name)

    return jsonify(field)


@summarize.route("/refresh", methods=["POST"])
def refresh_models():
    update_database()

    return ({"status": "success", "data": "database updated"}, 200)
