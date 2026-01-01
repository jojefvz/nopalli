"""
Flask routes for Dispatches.
"""

import json
from flask import jsonify, render_template, request, redirect, url_for, current_app, flash

from src.infrastructure.web.routes.dispatch import bp


@bp.route("/dispatches")
def list_dispatches():
    """List all dispatches."""
    app = current_app.config["APP_CONTAINER"]

    result = app.dispatch_controller.handle_list()
    
    if not result.is_success:
        error = app.dispatch_presenter.present_error(result.error.message)
        flash(error.message, "error")
        return redirect(url_for("todo.index"))

    return render_template("dispatches/dispatches.html", dispatches=result.success)


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


@bp.route("/dispatches/create", methods=["POST"])
def create_dispatch():
    """Create a new dispatch."""
    data = request.get_json()
    print(data)
    broker_ref = data['broker_ref']
    driver_ref = data['driver_ref']
    containers = data['containers']
    plan = data['plan']
    app = current_app.config["APP_CONTAINER"]

    result = app.dispatch_controller.handle_create(
        broker_ref=broker_ref,
        driver_ref=driver_ref,
        containers=containers,
        plan=plan,
    )

    print('OPERATION RESULT OUTCOME:', result.is_success)
    if not result.is_success:
        error = app.dispatch_presenter.present_error(result.error.message)
        flash(error.message, "error")
        return jsonify('FAILURE')

    # # Use view model directly from controller response
    dispatch = result.success
    flash(f'Location "{dispatch.id}" created successfully', "success")

    return jsonify('SUCCESS')


# @bp.route("/dispatches/edit", methods=["POST"])
# def edit_dispatch():
#     """Edit dispatch data."""
#     id = request.form["id"]
#     name = request.form["name"]
#     app = current_app.config['APP_CONTAINER']
#     result = app.dispatch_controller.handle_edit(id, name)

#     if not result.is_success:
#         error = app.dispatch_presenter.present_error(result.error.message)
#         flash(error.message, "error")
#         return redirect(url_for("dispatch.list_dispatches"))

#     # # Use view model directly from controller response
#     # # dispatch = result.success
#     # # flash(f'Location "{dispatch.name}" created successfully', "success")

#     return redirect(url_for("dispatch.list_dispatches"))
