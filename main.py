import flask

from flask import Flask, render_template, request
from database import dbase
from data import default_season, default_league

app = Flask(__name__)
navs = {"Новини": '/news/', "Чемпіонат": '/champ/', "Історія матчів": '/history/', 'Ліги': '/leagues/'}
admin_navs = navs.copy()
admin_navs['Команди'] = '/admin/commands/'
admin_navs['Матчі'] = '/admin/matches/'
admin_navs['Новини'] = '/admin/news/'
admin_navs['Ліги'] = '/admin/leagues/'
@app.route('/')
def home():
    return flask.redirect('/champ/')

@app.route('/news/')
def news():
    news = dbase.get_all_news()
    return render_template('news.html', navs=navs, news=news)

@app.route('/history/')
def history():
    args = request.args
    season = args.get('season')
    league = args.get('league')
    if not season:
        season = default_season
    if not league:
        league = default_league
    matches_ = dbase.take_matches(season=season, league=league)
    matches = []
    for match in matches_:
        response = {}
        id_home = match.get('id_home')
        id_quest = match.get('id_out')
        goal_home = match.get('goal_home')
        goal_quest = match.get('goal_out')
        home_name = dbase.take_command(id=id_home).get('name')
        quest_name = dbase.take_command(id=id_quest).get('name')
        response['goal_home'] = goal_home
        response['goal_quest'] = goal_quest
        response['home_name'] = home_name
        response['quest_name'] = quest_name
        result = match.get('result')
        if result == 1:
            response['color_quest'] = 'red'
            response['color_home'] = 'green'
        elif result == 0:
            response['color_quest'] = 'green'
            response['color_home'] = 'red'
        else:
            response['color_quest'] = 'blue'
            response['color_home'] = 'blue'
        matches.append(response)
    matches = reversed(matches)
    return render_template('history.html', matches=matches, navs=navs, season=season)


@app.route('/champ/')
def champ():
    args = request.args
    season = args.get('season')
    league = args.get('league')
    if not league:
        league = default_league
    if not season:
        season = default_season
    # Отримання даних про таблицю з якогось джерела
    table_data = dbase.take_table_champ(season=season, league=league)
    leagues = dbase.take_leagues()
    current_league = dbase.take_league(id=league)
    current_league = current_league.get('name')
    # Передача даних у шаблон HTML для відображення
    return render_template('live_table.html', table_data=table_data, navs=navs, season=season, leagues=leagues, current_league=current_league)

@app.route('/leagues/')
def leagues():
    leagues = dbase.take_leagues()
    return render_template('leagues.html', leagues=leagues, navs=navs)

@app.route('/admin/')
def admin():
    global admin_navs
    print(request)
    return render_template('admin.html', navs=admin_navs)

@app.route('/admin/<path>/', methods=['GET', 'POST'])
def admin_functions(path):
    global admin_navs
    print(request)
    print(path)
    if path == 'commands':
        league = default_league
        if request.method == 'POST':
            form = dict(request.form)
            print(form)
            add = form.get('add')
            remove = form.get('remove')
            name = form.get('name')
            short = form.get('short')
            league = form.get('league')
            if add:
                if name and short:
                    dbase.add_command(name=name, short_name=short, league=league)
            elif remove:
                id = remove
                dbase.remove_command(id=id)
        commands = dbase.take_commands(league=league)
        print(commands, '\n')
        return render_template('commands.html', navs=admin_navs, commands=commands)
    elif path == 'matches':
        league = default_league
        leagues = dbase.take_leagues()
        if request.method == 'POST':
            form = dict(request.form)
            id_home = form.get('id_home')
            id_out = form.get('id_out')
            goal_home = form.get('goal_home')
            goal_out = form.get('goal_out')
            season = form.get('season')
            league = form.get('league')
            dbase.add_match(id_home=id_home, id_out=id_out, goal_home=goal_home, goal_out=goal_out, season=season, type=1, league=league)
            return flask.redirect('/champ/')
        commands = dbase.take_commands(league=league)
        return render_template('matches.html', navs=admin_navs, commands=commands, leagues=leagues)

    elif path == 'news':
        if request.method == 'POST':
            form = dict(request.form)
            title = form.get('title')
            description = form.get('description')
            if title and description:
                dbase.add_news(title=title, description=description)
        news = dbase.get_all_news()
        return render_template('news.html', navs=navs, news=news, isAdmin=True)

    elif path == 'leagues':

        if request.method == 'POST':
            form = dict(request.form)
            add = form.get('add')
            remove = form.get('remove')
            if add:
                name = form.get('name')
                if name:
                    dbase.add_league(name=name)
            if remove:
                dbase.remove_league(id=remove)
        leagues = dbase.take_leagues()
        return render_template('leagues.html', leagues=leagues, navs=navs, isAdmin=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)