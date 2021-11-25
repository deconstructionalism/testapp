from app.lib import validate_body
from app.summarize.models.commit_snapshot import CommitSnapshot
from flask import abort, Blueprint, jsonify, request
from app.summarize.lib.differencer import update_database
from app.summarize.lib import SummarizerModels
from threading import Thread

summarize = Blueprint("summarize", __name__, url_prefix="/summarize")


@summarize.route("/", methods=["GET"])
def index_resources():

    # get commit id from body params if it was passed
    commit_id = request.args.get("commit_id")

    # return current database data if no commit id is provided
    if not commit_id:
        return jsonify(SummarizerModels.get_all_resources())

    try:
        # find the commit snapshot by commit id
        commit_snapshot = CommitSnapshot.query.filter_by(
            commit_id=commit_id
        ).first()
        return jsonify(commit_snapshot.to_dict())
    except AttributeError as e:
        abort(
            404,
            description=(
                f'no database snapshot found with commit id "{commit_id}"'
            ),
        )


@summarize.route("/<app_name>", methods=["GET"])
def index_app_resources(app_name: str):
    app_resources = SummarizerModels.get_app_resources(app_name)

    return jsonify(app_resources)


@summarize.route("/<app_name>/<resource_name>", methods=["GET"])
def show_resource(app_name: str, resource_name: str):
    resource = SummarizerModels.get_resource(app_name, resource_name)

    return jsonify(resource)


@summarize.route("/<app_name>/<resource_name>/<field_name>", methods=["GET"])
def show_field(app_name: str, resource_name: str, field_name: str):
    field = SummarizerModels.get_field(app_name, resource_name, field_name)

    return jsonify(field)


class RefreshStatus:
    """
    Encodes globally accessible value, along with closure wrapped value setter
    represented the status of the refresh process spawned from `/refresh` POST
    """

    running = False

    def set(self, next: bool) -> None:
        self.running = next


refresh_status = RefreshStatus()


@summarize.route("/refresh", methods=["POST"])
@validate_body(
    {
        "type": "object",
        "properties": {"force": {"type": "boolean"}},
        "additionalProperties": False,
    }
)
def refresh_models():
    if refresh_status.running:
        return (
            {"status": "fail", "data": "refresh in progress already"},
            403,
        )

    body = request.get_json()
    force = body["force"]

    # set refresh status to true and fork a new thread for refreshing the
    # repo and updating the DB. When it completes, refresh status will be
    # set back to `False`
    refresh_status.set(True)
    thread = Thread(
        target=update_database,
        args=(lambda: refresh_status.set(False), force),
    )
    thread.start()

    return (
        {"status": "success", "data": "database refresh initiated..."},
        200,
    )
