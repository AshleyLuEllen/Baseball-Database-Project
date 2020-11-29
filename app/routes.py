from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, RegistrationForm, TeamYearSelectForm, TeamYearSelectFormS, TableSelectForm
from app.models import User, Teams, Batting, Pitching, Managers, Seriespost
from werkzeug.urls import url_parse


months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
places = ['First', 'Second', 'Third', 'Fourth', 'Fifth', 'Sixth', 'Seventh', 'Eighth', 'Ninth', 'Tenth']


def generate_tables(html, teamID, yearID):
    form = TableSelectForm()
    team_name = [t.name for t in Teams.query.filter_by(teamID=teamID, yearID=yearID).all()]
    # get the final standings table information
    final_list = []
    for t in Teams.query.filter_by(teamID=teamID, yearID=yearID).all():
        if t.WSWin == 'Y':
            final_list.append('Won the World Series.')
        if t.DivWin == 'Y':
            final_list.append('Received the Division slot.')
        if t.LgWin == 'Y':
            final_list.append('Won League.')
        if t.WCWin == 'Y':
            final_list.append('Received the Wild Card slot')
    # get the manager table information
    rank = [t.teamRank for t in Teams.query.filter_by(teamID=teamID, yearID=yearID).all()]
    rank = places[rank[0]] + ' in the division.' if int(rank[0]) < 10 else rank[0] + ' in the division.'
    standings_list = [
        {'w_l': 'WON' if s.teamIDwinner == teamID else 'LOSE' if s.teamIDloser == teamID or s.teamIDwinner == teamID else None,
         'round': 'World Series' if s.round == 'WS' else (
             'Championship Series' if s.round == 'CS' else(
                 'American League Championship Series' if s.round == 'ALCS' else(
                     'National League Championship Series' if s.round == 'NLCS' else(
                         'American East Division Series' if s.round == 'AEDIV' else(
                             'American West Division Series' if s.round == 'AWDIV' else(
                                 'Nation East Division Series' if s.round == 'NEDIV' else(
                                     'National West Division Series' if s.round == 'NWDIV' else(
                                         'American League Division Series 1' if s.round == 'ALDS1' else(
                                             'American League Division Series 2' if s.round == 'ALDS2' else(
                                                 'National League Division Series 1' if s.round == 'NLDS1' else(
                                                     'National League Division Series 2' if s.round == 'NLDS2' else(
                                                        'American League Wild Card' if s.round == 'ALWC' else(
                                                            'National League Wild Card' if s.round == 'NLWC' else '?'))))))))))))),
         'other': s.teamIDloser if s.teamIDwinner == teamID else s.teamIDwinner,
         'wins': s.wins if s.teamIDwinner == teamID else s.losses,
         'losses': s.losses if s.teamIDwinner == teamID else s.wins,
         'ties': s.ties,
        } for s in
        Seriespost.query.filter_by(yearID=yearID).all()]
    standings_list = list(filter(lambda x: x['w_l'], standings_list))
    # get the roster table information
    for standing in standings_list:
        standing['other'] = (Teams.query.filter_by(teamID=standing['other'], yearID=yearID).first()).name
    standings_list = sorted(standings_list, key=lambda x: x['w_l'], reverse=False)
    people_list = [
        {'name': f"{b.person.nameFirst} {b.person.nameLast}" if b.person.nameFirst else f"? {b.person.nameLast}",
         'birth_day': f"{months[b.person.birthMonth - 1]} {b.person.birthDay}" if b.person.birthDay and b.person.birthMonth else '',
         'birth_place': (f"{b.person.birthCity}, {b.person.birthState}, {b.person.birthCountry}"
                         if {b.person.birthState}
                         else f"{b.person.birthCity}, {b.person.birthCountry}")
         if {b.person.birthCountry} else '',
         'batting_hand': b.person.bats if b.person.bats else '',
         'throwing_hand': b.person.throws if b.person.throws else ''
         } for b in
        Batting.query.filter_by(teamID=teamID, yearID=yearID).all()]
    # get the batting table information
    batting_list = [
        {'name': f"{b.person.nameFirst} {b.person.nameLast}" if b.person.nameFirst else f"? {b.person.nameLast}",
         'plate_appearances': b.plate_appearance,
         'batting_average': f"{b.batting_avg:.3f}",
         'onbase_percentage': f"{b.onbase_percent:.3f}",
         'slugging_percentage': f"{b.slug_percent:.3f}",
         'positions_played': f"{b.appearance.positions_played}"

         } for b in
        Batting.query.filter_by(teamID=teamID, yearID=yearID).all()]
    # get the pitching table information
    pitching_list = [
        {'name': f"{p.person.nameFirst} {p.person.nameLast}" if p.person.nameFirst else f"? {p.person.nameLast}",
         'innings_pitched': f"{p.innings_pitched:.1f}",
         'wins': p.W,
         'losses': p.L,
         'saves': p.SV,
         'ERA': f"{p.ERA:.2f}" if p.ERA is not None else ''
         } for p in
        Pitching.query.filter_by(teamID=teamID, yearID=yearID).all()]
    # get the manager table information
    managers_list = [
        {'name': f"{m.person.nameFirst} {m.person.nameLast}" if m.person.nameFirst else f"? {m.person.nameLast}"
         } for m in
        Managers.query.filter_by(teamID=teamID, yearID=yearID).all()]
    return render_template(html, title='Home', teamName=team_name[0], teamID=teamID, yearID=yearID,
                           rank=rank,
                           finals=final_list,
                           standings=standings_list,
                           players=people_list, batting=batting_list,
                           pitching=pitching_list, managers=managers_list, form=form)


@app.route('/')
@app.route('/index')
@login_required
def index():
    if not current_user.favTeam:
        return redirect(url_for('profile'))
    return generate_tables('index.html', current_user.favTeam, current_user.favYear)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    form = TeamYearSelectForm()
    if form.validate_on_submit():
        current_user.favTeam = form.Team.data[-3:]
        current_user.favYear = form.Year.data
        db.session.commit()
        flash('Favorite team and year updated.')
        return redirect(url_for('profile'))
    return render_template('profile.html', title='Profile', form=form)


@app.route('/_get_years/')
def _get_years():
    teamID = request.args.get('team', type=str)[-3:]
    years = [row.yearID for row in Teams.query.filter_by(teamID=teamID).all()]
    return jsonify(years)


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = TeamYearSelectFormS()
    if form.validate_on_submit():
        teamID = form.Team.data[-3:]
        yearID = form.Year.data
        db.session.commit()
        return generate_tables('tables.html', teamID, yearID)
    return render_template('search.html', title='Search', formS=form)

