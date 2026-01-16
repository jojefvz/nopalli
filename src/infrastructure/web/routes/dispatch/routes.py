"""
Flask routes for Dispatches.
"""
from flask import jsonify, render_template, request, redirect, url_for, current_app, flash

from src.infrastructure.web.routes.dispatch import bp


@bp.post("/dispatches")
def create_dispatch():
    """Create a new dispatch."""
    # data = request.get_json()
    # broker_id = data.get('broker_id')
    # driver_id = data.get('driver_id')
    # plan = data.get('plan')
    data = request.form

    app = current_app.config["APP_CONTAINER"]
    result = app.dispatch_controller.handle_create(
        broker_id=data['broker_id'],
        driver_id=data['driver_id'],
        plan=data['plan'],
    )

    if not result.is_success:
        flash(f'Error: {result.error.message}', 'error')
        return redirect(url_for("dispatch.list_dispatches"))
    else:
        flash(f'Created Dispatch Ref. {result.success.reference}', 'success')
    return redirect(url_for("dispatch.list_dispatches"))


@bp.get("/dispatches")
def index():
    """List all dispatches."""
    app = current_app.config["APP_CONTAINER"]

    result = app.dispatch_controller.handle_list()
    
    if not result.is_success:
        error = app.dispatch_presenter.present_error(result.error.message)
        flash(error.message, "error")
        return redirect(url_for("home.home"))

    return render_template("dispatches/dispatches.html", dispatches=result.success)


@bp.route("/dispatches/edit", methods=["POST"])
def edit_dispatch():
    """Edit dispatch data."""
    data = request.get_json()
    id = data.get('id')
    name = data.get('name')
    street_address = data.get('street_address')
    city = data.get('city')
    state = data.get('state')
    zipcode = data.get('zipcode')

    app = current_app.config["APP_CONTAINER"]
    result = app.broker_controller.handle_edit(
        id,
        name,
        street_address,
        city,
        state,
        zipcode
    )

    if not result.is_success:
        return jsonify(result.error)

    return jsonify(result.success)


# @bp.route("/api/dispatches")
# def api_list_dispatches():
#     """List all dispatches."""
#     app = current_app.config["APP_CONTAINER"]

#     result = app.dispatch_controller.handle_list()
#     # if not result.is_success:
#     #     error = app.dispatch_presenter.present_error(result.error.message)
#     #     flash(error.message, "error")
#     #     return redirect(url_for("todo.index"))
#     print(jsonify(result.success))
#     return jsonify(result.success)
