"""
Flask routes for Locations.
"""

from flask import render_template, request, redirect, url_for, current_app, flash

from ..location import bp


@bp.route("/locations")
def list_locations():
    """List all locations."""
    app = current_app.config["APP_CONTAINER"]

    result = app.location_controller.handle_list()
    # if not result.is_success:
    #     error = app.location_presenter.present_error(result.error.message)
    #     flash(error.message, "error")
    #     return redirect(url_for("todo.index"))

    return render_template("locations/locations.html", locations=result.success)


@bp.route("/locations/new", methods=["POST"])
def new_location():
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
        error = app.location_presenter.present_error(result.error.message)
        flash(error.message, "error")
        return redirect(url_for("location.list_locations"))

    # Use view model directly from controller response
    # location = result.success
    # flash(f'Location "{location.name}" created successfully', "success")

    return redirect(url_for("location.list_locations"))

@bp.route("/locations/deactivate", methods=['POST'])
def deactivate():
    id = request.form['id']

    app = current_app.config['APP_CONTAINER']
    result = app.location_controller.handle_deactivate(id)

    if not result.is_success:
        error = app.location_presenter.present_error(result.error.message)
        flash(error.message, "error")
        return redirect(url_for("location.list_locations"))

    return redirect(url_for('location.list_locations'))

@bp.route("/locations/activate", methods=['POST'])
def activate():
    id = request.form['id']

    app = current_app.config['APP_CONTAINER']
    result = app.location_controller.handle_activate(id)

    if not result.is_success:
        error = app.location_presenter.present_error(result.error.message)
        flash(error.message, "error")
        return redirect(url_for("location.list_locations"))

    return redirect(url_for('location.list_locations'))


@bp.route("/locations/edit", methods=["POST"])
def edit_location():
    """Edit location data."""
    id = request.form["id"]
    name = request.form["name"]
    street_address = request.form["street_address"]
    city = request.form["city"]
    state = request.form["state"]
    zipcode = request.form["zipcode"]
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
        error = app.location_presenter.present_error(result.error.message)
        flash(error.message, "error")
        return redirect(url_for("location.list_locations"))

    # # Use view model directly from controller response
    # # location = result.success
    # # flash(f'Location "{location.name}" created successfully', "success")

    return redirect(url_for("location.list_locations"))