"""
Flask routes for Locations.
"""

from flask import render_template, request, redirect, url_for, current_app, flash
from ..location import bp


@bp.route("/locations", methods=['GET', 'POST'])
def list_locations():
    """List all locations."""
    print('HIIIII')
    app = current_app.config["APP_CONTAINER"]

    result = app.location_controller.handle_list()
    if not result.is_success:
        error = app.location_presenter.present_error(result.error.message)
        flash(error.message, "error")
        return redirect(url_for("todo.index"))

    return render_template("locations.html", locations=result.success)


@bp.route("/locations/new", methods=["GET", "POST"])
def new_location():
    """Create a new location."""
    if request.method == "POST":
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
            error = location_presenter.present_error(result.error.message)
            flash(error.message, "error")
            return redirect(url_for("todo.index"))

        # Use view model directly from controller response
        location = result.success
        flash(f'Project "{location.name}" created successfully', "success")
        return redirect(url_for("todo.index"))

    return render_template("locations.html")