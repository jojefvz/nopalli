"""
Flask routes for Drivers.
"""

from flask import jsonify, render_template, request, current_app, url_for, redirect, flash

from src.infrastructure.web.routes.driver import bp


@bp.post("/drivers")
def create_driver():
    """Create a new driver."""
    name = request.form["name"]

    app = current_app.config["APP_CONTAINER"]
    result = app.driver_controller.handle_create(name)

    if not result.is_success:
        flash(f'Error: {result.error.message}', 'error')
    else:
        flash(f'Successfully created driver: {result.success.name}', 'success')
    return redirect(url_for('driver.index'))


@bp.get("/drivers")
def index():
    """List all drivers."""
    app = current_app.config["APP_CONTAINER"]

    result = app.driver_controller.handle_list()

    return render_template("drivers/drivers.html", drivers=result.success)


@bp.post("/drivers/<id>/edit")
def edit_driver(id):
    """Edit driver data."""
    name = request.form['name']
    app = current_app.config["APP_CONTAINER"]
    result = app.driver_controller.handle_edit(id, name)

    if not result.is_success:
        flash(f'Error: {result.error.message}', 'error')
    else:
        flash(f'Successfully edited driver: {result.success.name}', 'success')
    return redirect(url_for('driver.index'))


@bp.post("/drivers/<id>/sit-out")
def sit_out(id):
    app = current_app.config['APP_CONTAINER']
    result = app.driver_controller.handle_sit_out(id)

    if not result.is_success:
        flash(f'Error: {result.error.message}', 'error')
    else:
        flash(f'Successfully sat out driver: {result.success.name}', 'success')
    return redirect(url_for('driver.index'))


@bp.route("/drivers/<id>/make-available", methods=['POST'])
def make_available(id):
    app = current_app.config['APP_CONTAINER']
    result = app.driver_controller.handle_make_available(id)

    if not result.is_success:
        flash(f'Error: {result.error.message}', 'error')
    else:
        flash(f'Successfully made available driver: {result.success.name}', 'success')
    return redirect(url_for('driver.index'))


@bp.post("/drivers/<id>/deactivation")
def deactivate(id):
    app = current_app.config['APP_CONTAINER']
    result = app.driver_controller.handle_deactivate(id)

    if not result.is_success:
        flash(f'Error: {result.error.message}', 'error')
    else:
        flash(f'Successfully deactivated driver: {result.success.name}', 'success')
    return redirect(url_for('driver.index'))


@bp.post("/drivers/<id>/activation")
def activate(id):
    app = current_app.config['APP_CONTAINER']
    result = app.driver_controller.handle_activate(id)

    if not result.is_success:
        flash(f'Error: {result.error.message.message}', 'error')
    else:
        flash(f'Successfully activated driver: {result.success.name}', 'success')
    return redirect(url_for('driver.index'))


@bp.get("/api/drivers/available-operating")
def get_available_and_operating():
    """List all drivers."""
    app = current_app.config["APP_CONTAINER"]

    result = app.driver_controller.handle_available_and_operating_drivers()

    return jsonify(result.success)