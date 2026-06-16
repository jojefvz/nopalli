"""
Flask routes for Dispatches.
"""
from datetime import date

from flask import abort, jsonify, render_template, request, redirect, url_for, current_app, flash

from src.infrastructure.web.routes.dispatch import bp
from src.infrastructure.web.routes.dispatch.utilities import parse_new_dispatch_plan


@bp.get("/dispatches/new")
@bp.post("/dispatches/new")
def create_dispatch():
    """Create a new dispatch."""
    if request.method == 'POST':
        print("HTTP FORM", request.form)

        plan = parse_new_dispatch_plan(request.form)
        print("PARSED PLAN", plan)

        app = current_app.config["APP_CONTAINER"]
        result = app.dispatch_controller.handle_create(
            broker_id=request.form['broker_id'],
            driver_id=request.form['driver_id'],
            plan=plan,
        )

        if not result.is_success:
            flash(f'Error: {result.error.message}', 'error')
            return render_template(("dispatches/dispatches.html"))
        else:
            flash(f'Created Dispatch Ref. {result.success.reference}', 'success')
    return render_template(("dispatches/new_dispatch.html"))


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


@bp.get("/dispatches/<dispatch_id>/edit/")
@bp.post("/dispatches/<dispatch_id>/edit/")
def edit_dispatch(dispatch_id):
    """Edit a dispatch."""
    app = current_app.config["APP_CONTAINER"]

    if request.method == 'GET':
        result = app.dispatch_controller.handle_get_dispatch(dispatch_id)
        if not result.is_success:
            abort(404)
        return render_template("dispatches/edit_dispatch.html", dispatch=result.success)

    print("INCOMING EDIT FORM:", request.form)
    plan = parse_new_dispatch_plan(request.form)
    print("NEW PLAN:", plan)
    result = app.dispatch_controller.handle_edit(
        dispatch_id=dispatch_id,
        broker_id=request.form['broker_id'],
        driver_id=request.form['driver_id'],
        plan=plan,
    )

    if not result.is_success:
        flash(f'Error: {result.error.message}', 'error')
        return redirect(url_for('dispatch.edit_dispatch', dispatch_id=dispatch_id))

    flash(f'Edited Dispatch Ref. {result.success.reference}', 'success')
    return redirect(url_for('dispatch.index'))

    
@bp.post("/dispatches/<dispatch_id>/start_dispatch/")
def start_dispatch(dispatch_id):
    """Start a dispatch."""
    app = current_app.config["APP_CONTAINER"]

    result = app.dispatch_controller.handle_start_dispatch(dispatch_id)
    
    if not result.is_success:
        return jsonify({"error": result.error.message}), 400
    
    return jsonify(result.success), 200
    

@bp.get("/dispatches/<board_date>/loadboard/")
def loadboard(board_date):
    """List loadboard dispatches."""
    app = current_app.config["APP_CONTAINER"]

    result = app.dispatch_controller.handle_loadboard_list(date=board_date)
    
    if not result.is_success:
        error = app.dispatch_presenter.present_error(result.error.message)
        flash(error.message, "error")
        return redirect(url_for("home.home"))

    return render_template("dispatches/loadboard.html", dispatches=result.success, board_date=board_date)

@bp.post("/dispatches/<dispatch_id>/tasks/<task_priority>/start/")
def start_task(dispatch_id, task_priority):
        
    app = current_app.config['APP_CONTAINER']
    result = app.dispatch_controller.handle_start_task(dispatch_id, task_priority)

    board_date = request.form['board_date']

    if not result.is_success:
        flash(f'Error: {result.error.message}', 'error')
    
    flash(f'Started Task for Dispatch: {result.success.reference}', 'success')
    return redirect(url_for('dispatch.loadboard', board_date=board_date))

@bp.post("/dispatches/<dispatch_id>/tasks/<task_priority>/revert/")
def revert_task(dispatch_id, task_priority):
        
    app = current_app.config['APP_CONTAINER']
    result = app.dispatch_controller.handle_revert_task(dispatch_id, task_priority)

    board_date = request.form['board_date']

    if not result.is_success:
        flash(f'Error: {result.error.message}', 'error')
    
    flash(f'Reverted Task for Dispatch: {result.success.reference}', 'success')
    return redirect(url_for('dispatch.loadboard', board_date=board_date))

@bp.post("/dispatches/<dispatch_id>/tasks/<task_priority>/complete/")
def complete_task(dispatch_id, task_priority):
        
    app = current_app.config['APP_CONTAINER']
    result = app.dispatch_controller.handle_complete_task(dispatch_id, task_priority)

    board_date = request.form['board_date']

    if not result.is_success:
        flash(f'Error: {result.error.message}', 'error')
    
    flash(f'Completed Task for Dispatch: {result.success.reference}', 'success')
    return redirect(url_for('dispatch.loadboard', board_date=board_date))