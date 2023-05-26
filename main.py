import flask

import football_api
from flask import Flask, render_template, request
from database import dbase
from data import default_season, IP

app = Flask(__name__)
navs = { "Чемпіонат": '/champ/', "Історія матчів": '/history/'}
admin_navs = navs.copy()
admin_navs['Команди'] = '/admin/commands/'
admin_navs['Матчі'] = '/admin/matches/'
@app.route('/')
def home():
    return flask.redirect('/champ/')
@app.route('/history/')
def history():
    args = request.args
    season = args.get('season')
    if not season:
        season = default_season
    matches_ = dbase.take_matches(season=season)
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
    if not season:
        season = default_season
    # Отримання даних про таблицю з якогось джерела
    table_data = dbase.take_table_champ(season=season)

    # Передача даних у шаблон HTML для відображення
    return render_template('live_table.html', table_data=table_data, navs=navs, season=season)

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
        if request.method == 'POST':
            form = dict(request.form)
            print(form)
            add = form.get('add')
            remove = form.get('remove')
            name = form.get('name')
            short = form.get('short')
            if add:
                if name and short:
                    dbase.add_command(name=name, short_name=short)
            elif remove:
                id = remove
                dbase.remove_command(id=id)
        commands = dbase.take_commands()
        print(commands, '\n')
        return render_template('commands.html', navs=admin_navs, commands=commands)
    elif path == 'matches':
        if request.method == 'POST':
            form = dict(request.form)
            id_home = form.get('id_home')
            id_out = form.get('id_out')
            goal_home = form.get('goal_home')
            goal_out = form.get('goal_out')
            season = form.get('season')
            dbase.add_match(id_home=id_home, id_out=id_out, goal_home=goal_home, goal_out=goal_out, season=season, type=1)
            return flask.redirect('/champ/')
        commands = dbase.take_commands()
        return render_template('matches.html', navs=admin_navs, commands=commands)


if __name__ == '__main__':
    app.run(host=IP)