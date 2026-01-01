"""
Flask routes for Drivers.
"""

from flask import jsonify, render_template, request, redirect, url_for, current_app, flash

from src.infrastructure.web.routes.driver import bp


@bp.route("/drivers")
def list_drivers():
    """List all drivers."""
    app = current_app.config["APP_CONTAINER"]

    result = app.driver_controller.handle_list()
    # if not result.is_success:
    #     error = app.driver_presenter.present_error(result.error.message)
    #     flash(error.message, "error")
    #     return redirect(url_for("todo.index"))

    return render_template("drivers/drivers.html", drivers=result.success)

@bp.route("/api/drivers")
def api_list_drivers():
    """List all drivers."""
    app = current_app.config["APP_CONTAINER"]

    result = app.driver_controller.handle_list()
    # if not result.is_success:
    #     error = app.driver_presenter.present_error(result.error.message)
    #     flash(error.message, "error")
    #     return redirect(url_for("todo.index"))
    print(jsonify(result.success))
    return jsonify(result.success)


@bp.route("/drivers/new", methods=["POST"])
def new_driver():
    """Create a new driver."""
    name = request.form["name"]
    app = current_app.config["APP_CONTAINER"]
    result = app.driver_controller.handle_create(name)

    if not result.is_success:
        error = app.driver_presenter.present_error(result.error.message)
        flash(error.message, "error")
        return redirect(url_for("driver.list_drivers"))

    # Use view model directly from controller response
    # driver = result.success
    # flash(f'Location "{driver.name}" created successfully', "success")

    return redirect(url_for("driver.list_drivers"))

@bp.route("/drivers/deactivate", methods=['POST'])
def deactivate():
    id = request.form['id']

    app = current_app.config['APP_CONTAINER']
    result = app.driver_controller.handle_deactivate(id)

    if not result.is_success:
        error = app.driver_presenter.present_error(result.error.message)
        flash(error.message, "error")
        return redirect(url_for("driver.list_drivers"))

    return redirect(url_for('driver.list_drivers'))

@bp.route("/drivers/activate", methods=['POST'])
def activate():
    id = request.form['id']

    app = current_app.config['APP_CONTAINER']
    result = app.driver_controller.handle_activate(id)

    if not result.is_success:
        error = app.driver_presenter.present_error(result.error.message)
        flash(error.message, "error")
        return redirect(url_for("driver.list_drivers"))

    return redirect(url_for('driver.list_drivers'))


@bp.route("/drivers/edit", methods=["POST"])
def edit_driver():
    """Edit driver data."""
    id = request.form["id"]
    name = request.form["name"]
    app = current_app.config['APP_CONTAINER']
    result = app.driver_controller.handle_edit(id, name)

    if not result.is_success:
        error = app.driver_presenter.present_error(result.error.message)
        flash(error.message, "error")
        return redirect(url_for("driver.list_drivers"))

    # # Use view model directly from controller response
    # # driver = result.success
    # # flash(f'Location "{driver.name}" created successfully', "success")

    return redirect(url_for("driver.list_drivers"))