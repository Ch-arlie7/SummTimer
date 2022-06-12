from setup_class import Setup
from input_class import Input
import PySimpleGUI as sg
import time


class Game:
    def __init__(self, setup: Setup, input: Input):
        # Constants
        self.lucidity_constant = 12
        self.insight_constant = 18
        self.loading_screen_estimate_secs = 30

        # Objects containing champion/player data.
        self.setup = setup
        self.input = input
        self.gamestart = int(input.gamestart) + self.loading_screen_estimate_secs

        # Container for timers.
        self.active_timers = [
                        ['', ''], 
                        ['', ''], 
                        ['', ''], 
                        ['', ''], 
                        ['', '']]
        self.run()

    def main_window(self):
        '''self.input.data = list. Each row in layout corresponds to a player in the list.
        Map champion ID to .png file in /champions | map spell1 ID to .png in spells | map spell2 ID to .png in spells
        '''
        sg.theme('DarkBlack')
        layout = [
            [sg.Input(key='gameTimeInputMin', size=(4, 1),default_text='00'), sg.Input(key='gameTimeInputSec', size=(4, 1),default_text='00'), sg.Button('Sync', key='gameTimeButton'), sg.Text('', key='current_time', size=(9,1))],# background_color='black')],
            [sg.Button(image_filename=f"champions/{self.input.data[0]['champion']}.png"), sg.Button(image_filename=f"spells/{self.input.data[0]['spell1']}.png", key='00'), sg.Button(image_filename=f"spells/{self.input.data[0]['spell2']}.png", key='01'), sg.Checkbox('Luci', key='000')],
            [sg.Button(image_filename=f"champions/{self.input.data[1]['champion']}.png"), sg.Button(image_filename=f"spells/{self.input.data[1]['spell1']}.png", key='10'), sg.Button(image_filename=f"spells/{self.input.data[1]['spell2']}.png", key='11'), sg.Checkbox('Luci', key='100')],
            [sg.Button(image_filename=f"champions/{self.input.data[2]['champion']}.png"), sg.Button(image_filename=f"spells/{self.input.data[2]['spell1']}.png", key='20'), sg.Button(image_filename=f"spells/{self.input.data[2]['spell2']}.png", key='21'), sg.Checkbox('Luci', key='200')],
            [sg.Button(image_filename=f"champions/{self.input.data[3]['champion']}.png"), sg.Button(image_filename=f"spells/{self.input.data[3]['spell1']}.png", key='30'), sg.Button(image_filename=f"spells/{self.input.data[3]['spell2']}.png", key='31'), sg.Checkbox('Luci', key='300')],
            [sg.Button(image_filename=f"champions/{self.input.data[4]['champion']}.png"), sg.Button(image_filename=f"spells/{self.input.data[4]['spell1']}.png", key='40'), sg.Button(image_filename=f"spells/{self.input.data[4]['spell2']}.png", key='41'), sg.Checkbox('Luci', key='400')],
            [sg.Button('Exit'), sg.Button('Clear All')]
            ]
        return sg.Window('SummTimer', layout, location=(50,150), finalize=True)#, background_color='black')

    def overlay_window(self):
        '''A transparent window that displays text, which is updated regularly
        '''
        layout = [[sg.Text('|||||MOVE ME|||||',font=('Ariel', 13),key='OverlayText', background_color = 'black', text_color='white', size=(40,5))]]  
        return sg.Window('', layout, grab_anywhere=True,keep_on_top=True, no_titlebar=True, alpha_channel=1, transparent_color='black', background_color='black', location=(150, 10), finalize=True)

    def update_timer(self, spell_index: int, champ_index: int, lucidity: bool):
        '''Modifies relevant [x][y] index in self.active_timers when a summoner spell is used.
        '''
        # spell_index is always 0 or 1: in data file, they're listed as spell1 and spell2.
        spell = self.input.data[champ_index][f'spell{spell_index+1}']
        # bool, true when they have Cosmic Insight rune.
        insight = self.input.data[champ_index]['insight']
        base_cd = int(self.setup.data['spell_id_to_cd_dict'][int(spell)])

        # Unleashed Teleport's cooldown reduces at the 14 minute mark. '12' is teleport's ID.
        if ((time.time() - self.gamestart) // 60) >= 14 and spell == '12': 
            base_cd = 240
        # Haste, affected by Lucidity Boots and Cosmic Insight, reduces a spell's cooldown.
        haste = 0
        if lucidity:
            haste += self.lucidity_constant
        if insight:
            haste += self.insight_constant    
        cd = (base_cd * (100/(100 + haste)))
        # Current time - game_start_time = number of seconds the game has been active for. + cd = ingame time that ability will be off cd.
        ingame_uptime_in_secs = int(time.time() - self.gamestart + cd)
        # Update.
        self.active_timers[champ_index][spell_index] = ingame_uptime_in_secs

    def cull_outdated_timers(self):
        '''Loop over all entries in active timers. If Current time > timer -> ability no longer on cooldown -> deleted
        '''
        current_time = time.time() - self.gamestart
        for x in range(len(self.active_timers)):
            for y in range(len(self.active_timers[0])):
                if type(self.active_timers[x][y]) != str and self.active_timers[x][y] <= current_time:
                    self.active_timers[x][y] = ''

    def convert_sec_to_mins(self, seconds: int)->str:
        '''Helper Function for string building
        '''
        minutes = str(seconds // 60).zfill(2)
        seconds = str(seconds % 60).zfill(2)
        return f'{minutes}:{seconds}'

    def build_overlay_string(self):
        output = ''
        # Looping over each enemy champion's dictionary.
        for i, champ in enumerate(self.input.data):
            # Convert champion ID to champion Name.
            champion = self.setup.data['champ_id_to_name_dict'][int(champ['champion'])]
            # first iteration: [0][0] ie, first champion's first spell.
            spell1 = self.active_timers[i][0]
            # If spell1 is on cooldown
            if type(spell1) != str:
                # Convert spell1 from number (in seconds) to 'Spell Name: mins:seconds'
                spell1 = f"{self.setup.data['spell_id_to_name_dict'][int(champ['spell1'])]}: {self.convert_sec_to_mins(self.active_timers[i][0])}"
            spell2 = self.active_timers[i][1]
            # If spell2 is on cooldown
            if type(spell2) != str:
                # Convert spell2 from number (in seconds) to 'Spell Name: mins:seconds'
                spell2 = f"{self.setup.data['spell_id_to_name_dict'][int(champ['spell2'])]}: {self.convert_sec_to_mins(self.active_timers[i][1])}"
            # Combine both spells into one string. Note that if it's not on cd, it remains as '', so doesn't affect output.
            champ_timers = f'{champion}: {spell1} {spell2}'
            # Add line to string output.
            output += champ_timers + '\n'
        return output        


    def run(self):
        window_main = self.main_window()
        window_overlay = self.overlay_window()

        loop_timer = int(time.time())
        while True:
            window, event, values = sg.read_all_windows(timeout=300)

            if event == sg.WIN_CLOSED or event == 'Exit':
                window.close()
                break
            # This is a 'clever' way to isolate only summoner spell clicks, as their keys are length 2. 
            # Look at how they work in the layout. Champion 1's spells are: '00' '01'. Therefore the first digit refers to the champion's index in the self.input.data list. 
            # Add 1 to the second digit to get the correct spell number. '00' is champ0's first spell, '01' is champ0's second spell.
            # The first digit in Lucidity is used to isolate champ index. '022' = champ 0. 
            if len(event) == 2:
                champ_index, spell_index = int(event[0]), int(event[1])
                lucidity = values['{}00'.format(champ_index)]
                self.update_timer(spell_index, champ_index, lucidity)
                timer_string = self.build_overlay_string()
                window_overlay['OverlayText'].update(timer_string)

            # Update timers every second, to remove outdated ones and update the clock on main input UI. 
            current_time = int(time.time())
            if current_time - loop_timer == 1:
                self.cull_outdated_timers()
                timer_string = self.build_overlay_string()
                window_overlay['OverlayText'].update(timer_string)
                window_main['current_time'].update(self.convert_sec_to_mins(current_time - self.gamestart))
                loop_timer = current_time


            # Reset timers completely.
            if event == 'Clear All':
                self.active_timers = [
                                ['', ''], 
                                ['', ''], 
                                ['', ''], 
                                ['', ''], 
                                ['', '']]
                timer_string = self.build_overlay_string()
                window_overlay['OverlayText'].update(timer_string)

            # GameStart in the API doesn't account for loading screen time. Without syncing here, it's just an estimate.
            # Takes mins:secs input, converts to seconds, then adjusts the estimated game start time. 
            if event == 'gameTimeButton':
                mins, secs = values['gameTimeInputMin'], values['gameTimeInputSec']  
                if mins == '':
                    mins = '00'
                if secs == '':
                    secs = '00'
                timeInSeconds = (int(mins) * 60) + int(secs)   
                self.gamestart = int(time.time()) - timeInSeconds
                window_main['current_time'].update(self.convert_sec_to_mins(current_time - self.gamestart))

        window.close()

            
            



            

            

            


    


