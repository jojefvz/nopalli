"""
Flask routes for Brokers.
"""

from flask import flash, jsonify, redirect, render_template, request, current_app, url_for

from src.infrastructure.web.routes.broker import bp


@bp.post("/brokers")
def create_broker():
    """Create a new broker."""
    name = request.form["name"]
    street_address = request.form["street_address"]
    city = request.form["city"]
    state = request.form["state"]
    zipcode = request.form["zipcode"]

    app = current_app.config["APP_CONTAINER"]
    result = app.broker_controller.handle_create(
        name,
        street_address,
        city,
        state,
        zipcode
    )

    if not result.is_success:
        flash(f'Error: {result.error.message}', 'error')
    else:
        flash(f'Created broker: {result.success.name}', 'success')
    return redirect(url_for('broker.index'))


@bp.get("/brokers")
def index():
    """List all brokers."""
    app = current_app.config["APP_CONTAINER"]

    result = app.broker_controller.handle_list()

    return render_template("brokers/brokers.html", brokers=result.success)


@bp.post("/brokers/<id>/edit")
def edit_broker(id):
    """Edit broker data."""
    name = request.form['name']
    street_address = request.form['street_address']
    city = request.form['city']
    state = request.form['state']
    zipcode = request.form['zipcode']

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
        flash(f'Error: {result.error.message}', 'error')
    else:
        flash(f'Edited broker: {result.success.name}', 'success')
    return redirect(url_for('broker.index'))


@bp.post("/brokers/<id>/deactivation")
def deactivate(id):
    app = current_app.config['APP_CONTAINER']
    result = app.broker_controller.handle_deactivate(id)

    if not result.is_success:
        flash(f'Error: {result.error.message}', 'error')
    else:
        flash(f'Deactivated broker: {result.success.name}', 'success')
    return redirect(url_for('broker.index'))


@bp.post("/brokers/<id>/activation")
def activate(id):
    app = current_app.config['APP_CONTAINER']
    result = app.broker_controller.handle_activate(id)

    if not result.is_success:
        flash(f'Error: {result.error.message.message}', 'error')
    else:
        flash(f'Activated broker: {result.success.name}', 'success')
    return redirect(url_for('broker.index'))

@bp.get("/api/brokers/active")
def get_active_brokers():
    app = current_app.config["APP_CONTAINER"]

    result = app.broker_controller.handle_active_brokers()

    return jsonify(result.success)