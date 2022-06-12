import json
import PySimpleGUI as sg
from riotwatcher import LolWatcher, ApiError
import webbrowser as web
import sys

class Input:
    def __init__(self):
        with open('config.json', 'r') as f:
            f = json.load(f)
        self.name = f['name']
        self.api_key = f['api_key']
        self.region = f['region']
        self.data, self.gamestart = self.get_game_data()

    def create_window(self):
        sg.theme('DarkBlack')
        region_list = ['BR1', 'EUN1', 'EUW1', 'JP1', 'KR', 'LA1', 'LA2', 'NA1', 'OC1', 'RU', 'TR1']
        layout = [[sg.Text('', key='errormsg', size=(15,1))],
              [sg.Text('API Key', size=(15, 1)), sg.InputText(key='apikey', default_text=self.api_key)],
              [sg.Text('IGN', size=(15, 1)), sg.InputText(key='ign', default_text=self.name)],
              [sg.Text('Region', size=(15,1)), sg.Combo(region_list, s=(7,11), default_value=self.region, key='region')],
              [sg.Button('Submit'), sg.Button('Cancel'), sg.Button('Get API Key')]
             ]
        return sg.Window('Input', layout)

    def get_input(self):
        window = self.create_window()
        spectate_data = None
        while True:
            event, values = window.read(timeout=100)
            if event == sg.WIN_CLOSED or event == 'Cancel':
                break
            if event == 'Get API Key':
                web.open('https://developer.riotgames.com/login')
            if event == 'Submit':
                try:
                    lol_watcher = LolWatcher(values['apikey'])
                    summonername = values['ign']
                    region = values['region']
                    summonerId = lol_watcher.summoner.by_name(region, summonername)['id']
                except ApiError as err:
                    if err.response.status_code == 404:
                        window['errormsg'].update('Invalid IGN')
                        continue
                    elif err.response.status_code == 403:
                        window['errormsg'].update('Invalid/Expired API Key')
                        continue
                    else:
                        raise
                self.update_config(values['ign'], values['apikey'], values['region'])
                try:
                    spectate_data = lol_watcher.spectator.by_summoner(region, summonerId)
                    break
                except ApiError as err:
                    if err.response.status_code == 404:
                        window['errormsg'].update('Not Ingame')
                    else:
                        raise
        window.close()
        return spectate_data if spectate_data else sys.exit()

    def get_game_data(self):
        spectator = self.get_input()
        # Find player's team
        for participant in spectator['participants']: 
            if participant['summonerName'] == self.name:
                teamid = participant['teamId']
                break
        players = [] # [{}, {}..]
        for participant in spectator['participants']:

            # Only players on the opposing team.
            if participant['teamId'] != teamid:

                # Check for Cosmic Insight rune.
                insight = 8347 in participant['perks']['perkIds']
                
                # Populate the list.
                players.append({'champion' : str(participant['championId']),
                        'spell1' : str(participant['spell1Id']),
                        'spell2' : str(participant['spell2Id']),
                        'insight' : insight})    

        # Start time in Epoch Seconds.
        gamestart = int(spectator['gameStartTime'] / 1000)
        return players, gamestart

    def update_config(self, name: str, api_key: str, region: str):
        self.name = name
        self.api_key = api_key
        self.region = region
        with open('config.json', 'w') as f:
            json.dump({'name' : self.name,
                        'api_key' : self.api_key,
                        'region' : self.region},
                        f)


if __name__ == '__main__':

    i = Input()
    print(i.data)