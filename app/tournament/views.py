# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, flash, url_for, current_app
from flask_login import login_required, current_user

from . import bp
from .forms import CreateTournamentForm, EditTournamentForm
from .. import db
from ..decorators import manager_required
from ..models import Tournament, TournamentStatus, Participant
from ..texts import REGISTRATION_CLOSED, REGISTRATION_OPENED, REGISTERED_TO_TOURNAMENT, REGISTRATION_NOT_OPEN


@bp.route("/create", methods = ["GET", "POST"])
@manager_required
def create_tournament():
    title = u"Créer un tournoi"
    form = CreateTournamentForm(request.form)
    if form.validate_on_submit():
        tournament = Tournament(name = form.name.data,
                                started_at = form.start_date.data,
                                number_rounds = form.number_rounds.data)
        db.session.add(tournament)
        db.session.commit()
        flash("Le tournoi {} a été créé".format(form.name.data), "info")
        return redirect(url_for(".view_tournament", tournament_id = tournament.id))
    else:
        return render_template("tournament/create_tournament.html", title = title,
                               form = form)


@bp.route("/<tournament_id>/edit", methods = ["GET", "POST"])
@manager_required
def edit_tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    title = u"Tournoi {}".format(tournament.name)
    form = EditTournamentForm(request.form)
    if request.method == "GET":
        form.name.data = tournament.name
        form.number_rounds.data = tournament.number_rounds
        form.start_date.data = tournament.started_at
    if form.validate_on_submit():
        tournament.name = form.name.data
        tournament.started_at = form.start_date.data
        tournament.number_rounds = form.number_rounds.data
        db.session.add(tournament)
        db.session.commit()
        flash(u"Le tournoi {} a été mis à jour".format(form.name.data), "info")
        return redirect(url_for(".edit_tournament", tournament_id = tournament_id))
    else:
        return render_template("tournament/edit_tournament.html", title = title,
                               form = form, tournament = tournament)


@bp.route("/<tournament_id>")
@login_required
def view_tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    title = u"Tournoi {}".format(tournament.name)
    return render_template("tournament/view_tournament.html", title = title,
                           tournament = tournament)


@bp.route("/")
@login_required
def view_tournaments():
    title = "Tournois"
    page = request.args.get("page", 1, type = int)
    pagination = (Tournament.query.order_by(Tournament.started_at.desc())
                  .paginate(page, per_page = current_app.config["TOURNAMENTS_PER_PAGE"], error_out = False))
    return render_template("tournament/view_tournaments.html", title = title,
                           pagination = pagination)


@bp.route("/<tournament_id>/open_registrations")
@manager_required
def open_registrations(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    tournament.status = TournamentStatus.REGISTRATION_OPEN
    db.session.add(tournament)
    db.session.commit()
    flash(REGISTRATION_OPENED, "info")
    return redirect(url_for(".view_tournament", tournament_id = tournament.id))


@bp.route("/<tournament_id>/close_registrations")
@manager_required
def close_registrations(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    tournament.status = TournamentStatus.ONGOING
    db.session.add(tournament)
    db.session.commit()
    flash(REGISTRATION_CLOSED, "info")
    return redirect(url_for(".view_tournament", tournament_id = tournament.id))


@bp.route("/<tournament_id>/register")
@manager_required
def register(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    if not tournament.is_open_to_registration():
        flash(REGISTRATION_NOT_OPEN, "warning")
        return redirect(url_for(".view_tournament", tournament_id = tournament.id))

    participant = Participant(tournament_id = tournament_id,
                              user_id = current_user.id)
    db.session.add(participant)
    db.session.commit()
    flash(REGISTERED_TO_TOURNAMENT, "info")
    return redirect(url_for(".view_tournament", tournament_id = tournament.id))
