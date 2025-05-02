# Import packages
from psychopy import core, event, visual, parallel
import time
import csv
import os

debug = True # Set to True if parallel ports not plugged for coding/debugging other parts of exp

### Experiment details/parameters
## equipment parameters
port_buffer_duration = 1 #needs about 0.5s buffer for port signal to reset 
pain_response_duration = float("inf")
response_hold_duration = 1 # How long the rating screen is left on the response (only used for Pain ratings)
familiarisation_iti = 3

# parallel port triggers
port_address = 0x3ff8 
pain_trig = 2 
eda_trig = 1

## within experiment parameters 
experimentcode = "familiarisation"
P_info = {"PID": ""}
info_order = ["PID"]

rating_scale_pos = (0,-350)
rating_text_pos = (0,-250) 
text_height = 30 

# Participant info input
while True:
    try:
        P_info["PID"] = input("Enter participant ID: ")
        if not P_info["PID"]:
            print("Participant ID cannot be empty.")
            continue
            
        data_filename = P_info["PID"] + "_responses.csv"
        script_directory = os.path.dirname(os.path.abspath(__file__))  #Set the working directory to the folder the Python code is opened from
        
        #set a path to a "data" folder to save data in
        data_folder = os.path.join(script_directory, "data")
        
        # if data folder doesn"t exist, create one
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
            
        #set file name within "data" folder
        data_filepath = os.path.join(data_folder,data_filename)
        
        if os.path.exists(data_filepath):
            print(f"Data for participant {P_info['PID']} already exists. Choose a different participant ID.") ### to avoid re-writing existing data
        
        else:
            break  # Exit the loop if the participant ID is valid
        
    except KeyboardInterrupt:
        print("Participant info input canceled.")
        break  # Exit the loop if the participant info input is canceled
    
# get date and time of experiment start
datetime = time.strftime("%Y-%m-%d_%H.%M.%S")

if debug == None:
    pport = parallel.ParallelPort(address=port_address) #Get from device Manager
    pport.setData(0)
    
elif debug == True:
    pport = None #Get from device Manager

# set up screen
win = visual.Window(
    size=(1920, 1080), fullscr= True, screen=0,
    allowGUI=False, allowStencil=False,
    monitor="testMonitor", color=[0, 0, 0], colorSpace="rgb1",
    blendMode="avg", useFBO=True,
    units="pix")

# fixation stimulus
fix_stim = visual.TextStim(win,
                            text = "x",
                            color = "white",
                            height = 50,
                            font = "Roboto Mono Medium")


# Define trials
trial_order = []

# familiarisation trials
num_familiarisation = 10

for i in range(1, num_familiarisation + 1):
    trial = {
        "phase": "familiarisation",
        "blocknum": None,
        "stimulus": None,
        "outcome": None,
        "trialname": "familiarisation_" + str(i),
        "trialtype": "familiarisation",
        "exp_response": None,
        "pain_response": None,
        "iti" : None
    } 
    trial_order.append(trial)
    
    # # text stimuli
instructions_text = {
    "welcome": "Welcome to the experiment! Please read the following instructions carefully.", 
    
    "familiarisation_1": ("Firstly, you will be familiarised with the thermal stimuli. This familiarisation procedure is necessary to ensure that participants are able to tolerate "
    "the heat pain delivered in this experiment. The thermal stimulus is delivered through the thermode attached to your forearm, which delivers heat pain by selectively stimulating pain fibres.\n\n"
    "As the density of pain fibres can vary between individuals, the pain experienced and the efficacy of TENS for participants who will receive TENS stimulation can also vary. "
    "As such, this familiarisation procedure will demonstrate the range of how painful the thermal stimulus could be for any participant."),
    
    "familiarisation_2": ("In the familiarisation procedure, you will experience the thermal stimuli at a range of intensities. The machine will start at a low intensity, and incrementally increase each level. "
    "After receiving each thermal stimulus, please give a pain rating for that level of heat by clicking and dragging your mouse on a scale from 1 to 10 where 1 is not painful and 10 is very painful. "
    "The familiarisation procedure will take you through 10 increasing levels of heat intensities. \n\n Although the higher levels of heat intensities may be more uncomfortable or painful, please note that "
    "the maximum level of heat is safe and unlikely to cause you any actual harm. If, however, you find the thermal stimuli intolerable at any stage, please let the experimenter know and we will terminate the experiment immediately. "
    "This procedure will proceed at your pace, so feel free to take your time to rest between heat levels."),
        
    "familiarisation_finish": "Thank you for completing the familiarisation protocol. we will now proceed to the next phase of the experiment",
    
    "termination" : "The experiment has been terminated. Please ask the experimenter to help remove the devices.",
    
    "familiarisation_finish": "Thank you for completing the familiarisation protocol. we will now proceed to the next phase of the experiment",
}

response_instructions = {
    "pain": "How painful was the heat?",
    "familiarisation": "When you are ready to receive the thermal stimulus, press the SPACEBAR to activate the thermal stimulus. "
    }

trial_text = {
     "pain": visual.TextStim(win,
            text=response_instructions["pain"],
            height = text_height,
            pos = rating_text_pos
            )
}

# #Test questions
rating_stim = { "familiarisation": visual.Slider(win,
                                    pos = rating_scale_pos,
                                    ticks=[0,50,100],
                                    labels=(1,5,10),
                                    granularity=0.1,
                                    size=(600,60),
                                    style=["rating"],
                                    autoLog = False,
                                    labelHeight = 30)}


rating_stim["familiarisation"].marker.size = (30,30)
rating_stim["familiarisation"].marker.color = "yellow"
rating_stim["familiarisation"].validArea.size = (660,100)

fam_rating = rating_stim["familiarisation"]
                                
# pre-draw countdown stimuli (numbers 10-1)
countdown_text = {}
for i in range(0,11):
    countdown_text[str(i)] = visual.TextStim(win, 
                            color="white", 
                            height = 50,
                            text=str(i))
    
    #### Make trial functions
    
#create instruction trials
def instruction_trial(instructions,
                      holdtime=0,
                      key = "space",
                      buttontext = "\n\nPress spacebar to continue"): 
    termination_check()
    
    visual.TextStim(win,
                    text = instructions,
                    height = text_height,
                    color = "white",
                    pos = (0,0),
                    wrapWidth= 960
                    ).draw()
    win.flip()
    core.wait(holdtime)
    visual.TextStim(win,
                    text = instructions,
                    height = text_height,
                    color = "white",
                    pos = (0,0),
                    wrapWidth= 960
                    ).draw()
    
    visual.TextStim(win,
                    text = buttontext,
                    height = text_height,
                    color = "white",
                    pos = (0,-400)
                    ).draw()
    win.flip()
    event.waitKeys(keyList=key)
    win.flip()
    
    core.wait(2)
    
# Create functions
    # Save responses to a CSV file
def save_data(data):
    for trial in trial_order:
        trial['datetime'] = datetime
        trial['experimentcode'] = experimentcode
        trial["PID"] = P_info["PID"]
        
    # Extract column names from the keys in the first trial dictionary
    colnames = list(trial_order[0].keys())

    # Open the CSV file for writing
    with open(data_filepath, mode="w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=colnames)
        
        # Write the header row
        writer.writeheader()
        
        # Write each trial"s data to the CSV file
        for trial in data:
            writer.writerow(trial)
    
def exit_screen(instructions):
    win.flip()
    visual.TextStim(win,
            text = instructions,
            height = text_height,
            color = "white",
            pos = (0,0)).draw()
    win.flip()
    event.waitKeys()
    win.close()
    
def termination_check(): #insert throughout experiment so participants can end at any point.
    keys_pressed = event.getKeys(keyList=["escape"])  # Check for "escape" key during countdown
    if "escape" in keys_pressed:
        if pport != None:
            pport.setData(0) # Set all pins to 0 to shut off context, TENS, shock etc.
        # Save participant information

        save_data(trial_order)
        exit_screen(instructions_text["termination"])
        core.quit()

def show_fam_trial(current_trial):
    termination_check()
    # Wait for participant to ready up for shock
    visual.TextStim(win,
        text=response_instructions["familiarisation"],
        height = 35,
        pos = (0,0),
        wrapWidth= 800
        ).draw()
    win.flip()
    event.waitKeys(keyList = ["space"])
    
    # show fixation stimulus + deliver shock
    if pport != None:
        pport.setData(0)

    fix_stim.draw()
    win.flip()
    
    if pport != None:
        pport.setData(pain_trig+eda_trig)
        core.wait(port_buffer_duration)
        pport.setData(0)
    
    # Get pain rating
    while fam_rating.getRating() is None: # while mouse unclicked
        termination_check()
        trial_text["pain"].draw()
        fam_rating.draw()
        win.flip()
         
    pain_response_end_time = core.getTime() + response_hold_duration # amount of time for participants to adjust slider after making a response
    
    while core.getTime() < pain_response_end_time:
        termination_check()
        trial_text["pain"].draw()
        fam_rating.draw()
        win.flip()

    current_trial["pain_response"] = fam_rating.getRating()
    fam_rating.reset()
    
    win.flip()
    core.wait(familiarisation_iti)
    
exp_finish = None  

    # Run experiment
while not exp_finish:
    termination_check()
    instruction_trial(instructions_text["familiarisation_1"],10)
    instruction_trial(instructions_text["familiarisation_2"],10)
    for trial in list(filter(lambda trial: trial['phase'] == "familiarisation", trial_order)):
        show_fam_trial(trial)
    instruction_trial(instructions_text["familiarisation_finish"],2)
    
    # save trial data
    save_data(trial_order)
    
    exp_finish = True
    
win.close()