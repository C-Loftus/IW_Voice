import multiprocessing
from threading import Thread
from numpy import result_type
import pyautogui
import enum
from typing import List

from torch.cuda import current_device


class mode(enum.Enum):
    COMMAND = 1
    DICTATION = 2
    SHELL = 3
    SLEEP = 4




def handle_transcription(transcription, current_mode):
    # Only use the first index since we are only parsing one wav file
    transcription = transcription[0]

    changed, switched_mode = _check_switch_request(transcription, current_mode)

    if changed is True:
        current_mode = switched_mode
    else:
        if current_mode == mode.COMMAND:
            _run_command(transcription)
        elif current_mode == mode.DICTATION:
            _run_dictation(transcription)
        elif current_mode == mode.SHELL:
            _run_shell(transcription)
        elif current_mode == mode.SLEEP:
            pass
        else:
            raise Exception("Invalid mode") 
    
    return current_mode

def _check_switch_request(transcription, curr_mode):
    changed = True
    if 'command mode' in transcription:
        switch = mode.COMMAND
    elif 'dictation mode' in transcription:
        switch = mode.DICTATION
    elif 'shell mode' in transcription:
        switch = mode.SHELL
    elif 'sleep mode' in transcription:
        return mode.SLEEP
    # don't change anything if no switch is requested
    else:
        changed = False
        switch = curr_mode

    return changed, switch

def _run_dictation(transcription):
    pyautogui.typewrite(transcription)


def _run_shell(transcription, safety_time=10):
    
    '''
    it is dangerous to run shell commands based off voice input.
    However, it is also very useful since the user can run any command
    in their .basrc/config.fish/etc. This is very convenient

    it is impossible to check every unsafe command in the shell since the 
    user can alias commands and what exactly is not safe  depends on the user's
    machine. The best way is to automatically create a nonblocking pop up, 
    that if not interacted with, will automatically close and execute the command.  
      
    If you need low latency, just using the terminal may be preferred.

    If you want convenience and safety, this may be better. 
    '''

    import time
    import subprocess
    from multiprocessing import Process
    from os import environ

    shell = environ['SHELL']
    message = 'Are you sure you want to run command \'{}\' in current shell {}? \n \
         Unless canceled, the command will be run automatically {} seconds after \
             this window first appeared'\
         .format(transcription, shell, safety_time)

    q = multiprocessing.Queue()

    alert_thread = Process(target=_alert_wrapper, args=(message, q))
    alert_thread.start()

    # wait until the safety time is over
    time.sleep(safety_time)

    alert_thread.terminate()

    # check to see if the queue returned a message that would indicate a cancel
    try:
        result = q.get(block=False)
        #  we only need to check for cancel since that is the only thing it can return
        if result == 'CANCEL':
            print(f'Cancelled command: {transcription}')
    # An exception means the queue was empty and the user did not cancel
    except:
        subprocess.call([shell, '-i', '-c', transcription])
         

# This has to be wrapped in a process because alert is blocking
def _alert_wrapper(message, q):
    result = pyautogui.alert(text=message, title='Safety Check Shell Command', button='CANCEL')
    q.put(result)

def _run_command(transcription, alphabet):
    '''
    Command Format:

    (modifiers)* (alphabet)* || (focus/close/open) (editor/terminal/browser)
    
    '''

    modifiers = {'ctrl', 'alt', 'shift', 'super'}
    window_actions = {'focus', 'open', 'close'}
    applications = {'editor', 'terminal', 'browser'}
    
    cmdList: List[str] = []
    currentCmd = []

    currCmdHasAction = False

    for word in transcription:


        # modifiers only begin cmds or follow other modifiers
        if word in modifiers:
            lastTerm = currentCmd[-1]
            if lastTerm not in modifiers:
                cmdList.append(currentCmd)
                currentCmd = [word]
            if lastTerm in modifiers:
                currentCmd.append(word)

        # There can only be one cmd term for every cmd
        # i.e. it doesn't make sense to have 'close focus browser'
        if word in window_actions:
            if currCmdHasAction:
                cmdList.append(currentCmd)
                currCmdHasAction = False
                currentCmd = [word]

            else:
                currCmdHasAction = True    
                currentCmd.append(word)

        
        elif word in alphabet:
            currentCmd.append(alphabet[word])

        elif word in applications:
            currentCmd.append(word)


class command_list:
    current_command = []
    command_list = []

    def __init__(self):
        return

    def add_to_current_command(self, command: str):
        self.current_command.append(command)  

    def finish_this_command(self, command: str):
        self.command_list.append(command)
        self.current_command = []


if __name__ == '__main__':
    # print(_run_dictation("command mode"))
    # print(_run_dictation("test command"))
    # _run_shell("echo test", safety_time=10)Hello world!
