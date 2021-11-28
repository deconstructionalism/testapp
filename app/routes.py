from flask import current_app
from flask.blueprints import Blueprint

root_blueprint = Blueprint("root", __name__, url_prefix="/")


@root_blueprint.route("/")
def index():
    """Display all routes in app at root"""

    # get view html for each route
    html_list = []
    for item in current_app.url_map._rules:

        # do not show the static files route
        if item.rule.startswith("/static"):
            continue

        # assemble html for each route
        rule = item.rule.replace("<", "[").replace(">", "]")
        methods = ", ".join(
            filter(lambda x: x not in ["HEAD", "OPTIONS"], item.methods)
        )
        endpoint = f"app.{item.endpoint}"
        html_list.append(
            f"<p><code>{rule} <b>{methods}</b> -> {endpoint}</code></p>"
        )

    # sort the route html
    html_list.sort()

    # generate the final html with title
    html = f"<h1>Marshall Summarizer App Routes</h1>{''.join(html_list)}"

    return html
