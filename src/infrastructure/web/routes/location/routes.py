"""
Flask routes for Locations.
"""

from flask import flash, jsonify, redirect, render_template, request, current_app, url_for

from src.infrastructure.web.routes.location import bp


@bp.post("/locations")
def create_location():
    """Create a new location."""
    name = request.form["name"]
    street_address = request.form["street_address"]
    city = request.form["city"]
    state = request.form["state"]
    zipcode = request.form["zipcode"]

    app = current_app.config["APP_CONTAINER"]
    result = app.location_controller.handle_create(
        name,
        street_address,
        city,
        state,
        zipcode
    )

    if not result.is_success:
        flash(f'Error: {result.error.message}', 'error')
    else:
        flash(f'Created location: {result.success.name}', 'success')
    return redirect(url_for('location.index'))


@bp.get("/locations")
def index():
    """List all locations."""
    app = current_app.config["APP_CONTAINER"]

    result = app.location_controller.handle_list()

    return render_template("locations/locations.html", locations=result.success)


@bp.post("/locations/<id>/edit")
def edit_location(id):
    """Edit location data."""
    name = request.form['name']
    street_address = request.form['street_address']
    city = request.form['city']
    state = request.form['state']
    zipcode = request.form['zipcode']

    app = current_app.config["APP_CONTAINER"]
    result = app.location_controller.handle_edit(
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
        flash(f'Edited location: {result.success.name}', 'success')
    return redirect(url_for('location.index'))


@bp.post("/locations/<id>/deactivation")
def deactivate(id):
    app = current_app.config['APP_CONTAINER']
    result = app.location_controller.handle_deactivate(id)

    if not result.is_success:
        flash(f'Error: {result.error.message}', 'error')
    else:
        flash(f'Deactivated location: {result.success.name}', 'success')
    return redirect(url_for('location.index'))


@bp.post("/locations/<id>/activation")
def activate(id):
    app = current_app.config['APP_CONTAINER']
    result = app.location_controller.handle_activate(id)

    if not result.is_success:
        flash(f'Error: {result.error.message}', 'error')
    else:
        flash(f'Activated location: {result.success.name}', 'success')
    return redirect(url_for('location.index'))
