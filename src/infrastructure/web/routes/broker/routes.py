"""
Flask routes for Brokers.
"""

from flask import render_template, request, redirect, url_for, current_app, flash

from ..broker import bp


@bp.route("/brokers")
def list_brokers():
    """List all brokers."""
    app = current_app.config["APP_CONTAINER"]

    result = app.broker_controller.handle_list()
    # if not result.is_success:
    #     error = app.broker_presenter.present_error(result.error.message)
    #     flash(error.message, "error")
    #     return redirect(url_for("todo.index"))

    return render_template("brokers/brokers.html", brokers=result.success)


@bp.route("/brokers/new", methods=["POST"])
def new_broker():
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
        error = app.broker_presenter.present_error(result.error.message)
        flash(error.message, "error")
        return redirect(url_for("broker.list_brokers"))

    # Use view model directly from controller response
    # broker = result.success
    # flash(f'Location "{broker.name}" created successfully', "success")

    return redirect(url_for("broker.list_brokers"))

@bp.route("/brokers/deactivate", methods=['POST'])
def deactivate():
    id = request.form['id']

    app = current_app.config['APP_CONTAINER']
    result = app.broker_controller.handle_deactivate(id)

    if not result.is_success:
        error = app.broker_presenter.present_error(result.error.message)
        flash(error.message, "error")
        return redirect(url_for("broker.list_brokers"))

    return redirect(url_for('broker.list_brokers'))

@bp.route("/brokers/activate", methods=['POST'])
def activate():
    id = request.form['id']

    app = current_app.config['APP_CONTAINER']
    result = app.broker_controller.handle_activate(id)

    if not result.is_success:
        error = app.broker_presenter.present_error(result.error.message)
        flash(error.message, "error")
        return redirect(url_for("broker.list_brokers"))

    return redirect(url_for('broker.list_brokers'))


@bp.route("/brokers/edit", methods=["POST"])
def edit_broker():
    """Edit broker data."""
    id = request.form["id"]
    name = request.form["name"]
    street_address = request.form["street_address"]
    city = request.form["city"]
    state = request.form["state"]
    zipcode = request.form["zipcode"]
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
        error = app.broker_presenter.present_error(result.error.message)
        flash(error.message, "error")
        return redirect(url_for("broker.list_brokers"))

    # # Use view model directly from controller response
    # # broker = result.success
    # # flash(f'Location "{broker.name}" created successfully', "success")

    return redirect(url_for("broker.list_brokers"))