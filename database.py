import sqlite3
class db:
    def __init__(self):
        self.con = sqlite3.connect('database.db', timeout=10, check_same_thread=False)
        self.cur = self.con.cursor()
        self.cur.execute(f'''CREATE TABLE IF NOT EXISTS commands (
                                                        id INTEGER PRIMARY KEY,
                                                        league INTEGER,
                                                        name TEXT,
                                                        short_name TEXT);
                                                        ''')
        self.cur.execute(f'''CREATE TABLE IF NOT EXISTS matches (
                                                        id INTEGER PRIMARY KEY,
                                                        id_home INTEGER,
                                                        id_out INTEGER,
                                                        type INTEGER,
                                                        season TEXT,
                                                        result BLOB,
                                                        goal_home INTEGER,
                                                        goal_out INTEGER);
                                                        ''')
        self.cur.execute(f'''CREATE TABLE IF NOT EXISTS news (
                                                                id INTEGER PRIMARY KEY,
                                                                title TEXT,
                                                                description TEXT);
                                                                ''')
        self.cur.execute(f'''CREATE TABLE IF NOT EXISTS leagues (
                                                                id INTEGER PRIMARY KEY,
                                                                name TEXT);
                                                                ''')
        self.con.commit()
    def select_sqlite(self, table, values='*', where='', fetchall=False, cursor_dict=False):
        result = []
        if where != '':
            where = f"WHERE {where}"
        sql = f"SELECT {values} FROM {table} {where};"
        #print(sql)
        self.cur.execute(sql)
        columns = [column[0] for column in self.cur.description]
        if fetchall:
            rows = self.cur.fetchall()
            if cursor_dict:
                for row in rows:
                    result.append(dict(zip(columns, row)))
            else:
                result = rows
        else:
            result = self.cur.fetchone()
            if result:
                if cursor_dict:
                    result = dict(zip(columns, result))
        return result

    def update_sqlite(self, table, column, value, where=''):
        if where != '':
            where = f'WHERE {where}'
        self.cur.execute(f'UPDATE {table} SET {column} = "{value}" {where}')
        self.con.commit()
        return True

    def insert_sqlite(self, table, columns_list, data):
        columns = ''
        VALUES = ''
        for value in columns_list:
            columns += f'{value}, '
            VALUES += '?,'
        columns = columns[:-2]
        VALUES = VALUES[:-1]
        sql = f'INSERT INTO {table} ({columns}) VALUES({VALUES})'
        self.cur.execute(sql, data)
        self.con.commit()
        return True

    def delete_sqlite(self, table, where=''):
        if where != '':
            where = f'WHERE {where}'
        sql = f'DELETE FROM {table} {where}'
        self.cur.execute(sql)
        self.con.commit()

    def take_commands(self, league):

        result = self.select_sqlite(table='commands', fetchall=True, cursor_dict=True, where=f'league={league}')
        return result

    def add_command(self, name, short_name, league):
        columns = ['name', 'short_name', 'league']
        values = [name, short_name, league]
        self.insert_sqlite(table='commands', columns_list=columns, data=values)
        return True

    def add_match(self, id_home, id_out, goal_home, goal_out, season, type, league):
        columns = ['id_home', 'id_out', 'type', 'season', 'result', 'goal_home', 'goal_out', 'league']
        if goal_home > goal_out:
            result = True
        elif goal_home == goal_out:
            result = None
        else:
            result = False
        values = [id_home, id_out, type, season, result, goal_home, goal_out, league]
        self.insert_sqlite(table='matches', columns_list=columns, data=values)
        return True

    def take_command(self, id):
        command = self.select_sqlite(table='commands', where=f'id={id}', cursor_dict=True)
        return command

    def take_matches(self, season=None, type=None, id_command=None, league=None):
        where = ''
        if season:
            where = f'season={season}'
            if type:
                where += f' AND type={type}'
                if league:
                    where += f' AND league={league}'
            elif league:
                    where += f' AND league={league}'
        else:
            if type:
                where = f'type={type}'

                if league:
                    where += f' AND league={league}'
            elif league:
                    where += f' AND league={league}'
        matches = self.select_sqlite(table='matches', where=where, fetchall=True, cursor_dict=True)
        if id_command:
            matches = dict(filter(lambda x: x.get('id_home') == id_command or x.get('id_out') == id_command, matches))

        return matches

    def take_table_champ(self, season, league):
        commands = self.take_commands(league=league)
        response = {}
        if len(commands) < 1:
            return response
        for command in commands:
            response[command.get('id')] = {
                'point': 0,
                'name': command.get('name'),
                'short_name': command.get('short_name'),
                'W': 0,
                'D': 0,
                'L': 0,
                'matches': 0,
                'goal_in': 0,
                'goal_out': 0
            }
        matches = self.take_matches(season=season, type=0)
        if matches:
            for match in matches:
                id_home = match.get('id_home')
                id_out = match.get('id_out')
                result = match.get('result')
                goal_home = match.get('goal_home')
                goal_out = match.get('goal_out')
                response[id_home]['matches'] = response[id_home]['matches'] + 1
                response[id_home]['goal_out'] = response[id_home]['goal_out'] + goal_home
                response[id_home]['goal_in'] = response[id_home]['goal_in'] + goal_out
                response[id_out]['goal_in'] = response[id_out]['goal_in'] + goal_home
                response[id_out]['goal_out'] = response[id_out]['goal_out'] + goal_out
                response[id_out]['matches'] = response[id_out]['matches'] + 1

                if result == True:
                    response[id_home]['point'] = response[id_home]['point'] + 3
                    response[id_home]['W'] = response[id_home]['W'] + 1
                    response[id_out]['point'] = response[id_out]['point'] + 0
                    response[id_out]['L'] = response[id_out]['L'] + 1
                elif result == None:
                    response[id_home]['point'] = response[id_home]['point'] + 1
                    response[id_home]['D'] = response[id_home]['D'] + 1
                    response[id_out]['point'] = response[id_out]['point'] + 1
                    response[id_out]['D'] = response[id_out]['D'] + 1
                else:
                    response[id_home]['point'] = response[id_home]['point'] + 0
                    response[id_home]['L'] = response[id_home]['L'] + 1
                    response[id_out]['point'] = response[id_out]['point'] + 3
                    response[id_out]['W'] = response[id_out]['W'] + 1
        response = dict(sorted(response.items(), key=lambda x: (x[1].get('point'), x[1].get('goal_out')-x[1].get('goal_in'), x[1].get('goal_out'), -x[1].get('goal_in'), -x[1].get('matches')), reverse=True))
        return response

    def remove_command(self, id):
        self.delete_sqlite(table='commands', where=f'id={id}')
        return

    def add_news(self, title, description):
        columns = ['title', 'description']
        values = [title, description]
        self.insert_sqlite(table='news', columns_list=columns, data=values)

    def get_all_news(self):
        news = self.select_sqlite(table='news', fetchall=True, cursor_dict=True)
        return news

    def delete_news(self, id):
        self.delete_sqlite(table='news', where=f'id={id}')
        return

    def add_league(self, name):
        columns = ['name', ]
        values = [name, ]
        self.insert_sqlite(table='leagues', columns_list=columns, data=values)

    def remove_league(self, id):
        self.delete_sqlite(table='leagues', where=f'id={id}')

    def take_leagues(self):
        leagues = self.select_sqlite(table='leagues', fetchall=True, cursor_dict=True)
        return leagues

    def take_league(self, id):
        league = self.select_sqlite(table='leagues', where=f'id={id}', cursor_dict=True)
        return league
dbase = db()
#print(dbase.take_commands())
#dbase.add_match(id_home=4, id_out=2, goal_home=2, goal_out=2, season=1, type=0)
