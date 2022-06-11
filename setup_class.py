import requests
import json
from os.path import exists
import os

class Setup:
    """Updates to reflect current LoL patch. Downloads new Champion and SummonerSpell images.
    Methods: get_data.
    """    
    def __init__(self):
        self.data = self.update_game_info()
        self.download_champion_images()
        self.download_spell_images()
        self.create_config_file()
        
    def create_config_file(self):
        if not exists('config.json'):
            cfg = {'name' : '',
                'api_key' : ''}
            with open('config.json', 'w') as f:
                json.dump(cfg, f)

    def update_game_info(self):
        # Download relevant data in Json format
        current_version = requests.get('https://ddragon.leagueoflegends.com/realms/na.json').json()['v']
        champion_data = requests.get(f'http://ddragon.leagueoflegends.com/cdn/{current_version}/data/en_US/champion.json').json()
        spell_data = requests.get('https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/summoner-spells.json').json()

        #Format and return
        return {'champ_id_list' : [int(champion_data['data'][champ]['key']) for champ in champion_data['data']], # List of champion IDs.
                'champ_id_to_name_dict' : {int(champion_data['data'][champ]['key']): champion_data['data'][champ]['name'] for champ in champion_data['data']}, # Dict {id : name}
                'spell_id_to_cd_dict' : {int(spell['id']): int(spell['cooldown']) for spell in spell_data}, # Dict {id : cooldown}
                'spell_id_to_icon_url_dict' : {int(spell['id']): spell['iconPath'][21:].lower() for spell in spell_data}, # Dict {id : iconPath}. Path reformatted for later mapping to api url.
                'spell_id_to_name_dict' : {int(spell['id']): spell['name'] for spell in spell_data}} # Dict {id : name}

    def download_champion_images(self):
        # Create champion folder if not already done.
        if not exists('champions'):
            os.mkdir('champions')
        for champion_id in self.data['champ_id_list']:
            # Avoid re-downloading champion images.
            if exists(f'champions/{champion_id}.png'):
                continue
            try:
                url = f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/{champion_id}.png'
                image = requests.get(url).content
                with open(f'champions/{champion_id}.png', 'wb') as f:
                    f.write(image)
            # Should only error if the DDragon hasn't been updated upon new champion release.
            except:
                print(f'''Champion image doesn't exist for : {champion_id}''' )

    def download_spell_images(self):
        # Create spell folder if not already done.
        if not exists('spells'):
            os.mkdir('spells')
        # Need to map URL in each spell's JSON to this. 
        base_url = 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default'
        for spell_id in self.data['spell_id_to_icon_url_dict']:
            # Avoid re-downloading spell images.
            if exists(f'spells/{spell_id}.png'):
                continue
            try:
                url = base_url + self.spell_icon_url_dict[spell_id]
                image = requests.get(url).content
                with open(f'spells/{spell_id}.png', 'wb') as f:
                    f.write(image)
            # Should only error if the DDragon hasn't been updated upon new champion release.
            except:
                print(f'''Spell image doesn't exist for : {spell_id}''' )

    def get_data(self):
        return self.data


if __name__ == '__main__':
    data = Setup().get_data()
    print(data)


    




    

