#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Software developed by Diego Alnso San Alberto using PsychoPy2 Builder
Python code to send a trigger signal using an analog output and then display visual stimulus. Software developed by Diego Alnso San Alberto using PsychoPy2 Builder

This software send a trigger signal via a NI USB 6008 DAQ analog output (/Dev1/ao1) to a control PC and display visual stimulus (blue bars) across the screen. 
We can set the duration of the experiment at the beginning of the experiment (experiment_time) and the software will divide the time equitably among all the stimulus patterns (stimulus_time)
Information regarding the visual stimulus (time spend in the screen, angular velocity, position of the pattern in the screen...) is stored in a .txt file

The visual stimulus move as follows:
    - left to right as many times as requested in COUNTER_LOOP
    - right to left as many times as requested in COUNTER_LOOP
    - corner bottom left to corner top right as many times as requested in COUNTER_LOOP
    - corner top right to corner bottom left as many times as requested in COUNTER_LOOP
    - bottom of the screen to top of the screen as many times as requested in COUNTER_LOOP
    - top of the screen t bottom of the screen as many times as requested in COUNTER_LOOP

This experiment was created using PsychoPy2 Experiment Builder (v1.79.01), Thu 16 Feb 2017 04:27:52 PM PST
If you publish work using this script    please cite the relevant PsychoPy publications
  Peirce, JW (2007) PsychoPy - Psychophysics software in Python. Journal of Neuroscience Methods, 162(1-2), 8-13.
  Peirce, JW (2009) Generating stimuli for neuroscience using PsychoPy. Frontiers in Neuroinformatics, 2:10. doi: 10.3389/neuro.11.010.2008
"""


from __future__ import absolute_import, division
from psychopy import locale_setup, sound, gui, visual, core, data, event, logging
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle
import os  # handy system and path functions
import sys  # to get file system encoding

import time


# -- Packages, variables and functions to work with NI DAQ USB6008 --

from PyDAQmx import *
import numpy, time

#Method to send value= 5.0 volts through the USB6008 analog output /Dev1/ao1
def send_trigger_signal():
    HIGH= 5.0
    LOW= 0.0
    value= 5.0
    try: 
        analog_output = Task()
        
        # DAQmx Configure Code
        analog_output.CreateAOVoltageChan("/Dev1/ao1","",LOW,HIGH,DAQmx_Val_Volts,None)
        
        # DAQmx Start Code
        analog_output.StartTask()
        
        # DAQmx write Code
        end_t=start_t=time.time()
        print end_t-start_t
        analog_output.WriteAnalogScalarF64(1,10.0,value,None)   #Sending trigger signal (5.0V) during 1 second
        time.sleep(1)
        end_t= time.time()
        print "trigger sent during %s sec" %(end_t-start_t)
        analog_output.WriteAnalogScalarF64(1,10.0,LOW,None) #Setting output to LOW value (0.0V) 
    except DAQError as err:
        print "DAQmx Error: %s"%err

# -- --

#Class to contain position value of the stimulusi in the screen
class exp_data():
    
    def __init__(self, expDuration, expStep, expStimAngle, expStimDir, expStimTime=0, expAngSpeed=0):
        self.duration= expDuration      #Full experiment duration (in seconds)
        self.step=expStep               #Speed of the visual stimulus
        self.stimAngle= expStimAngle    #Angle used in the visual stimulus (0, pi/4 or pi/2)
        self.stimDir= expStimDir        #Direction of the stimulus (left/down to right/up or right/up to left/down)
        self.stimTime= expStimTime      #Time taken for the stimulus to cross the screen
        self.angSpeed= expAngSpeed
        self.startingTime= 0.0
        self.position= []               #List with the position values (x, y) of the center of the visual stimulus through the screen
    
    def addStimTime(self, expStimTime):
        self.stimTime= expStimTime
        
    #Method to calculate the angular speed of the stimulus crossing the screen
    def addAngSpeed(self, expStimTime):
        self.angSpeed= (2*np.pi)/expStimTime
    
    def addStartingTime(self, startTime):
        self.startingTime= startTime
    
        #Method to add visual stimulus position in the screen as a tuplue (x, y)
    def addPosition(self, x, y):
        temp_x= float(float('%.4f'%(x)))
        temp_y= float(float('%.4f'%(y)))
        self.position.append((temp_x, temp_y))

    def getPositionValue(self, index):
        return self.position[index]
    
    def getPositionList(self):
        return self.position

    def erasePositionList(self):
        self.position= []

    def saveData(self, folderPath, fileName, comment = ''):
        trialNum = 0
        fileName= fileName+'.txt'
                   
        if not(os.path.exists(folderPath)):
            os.mkdir(folderPath)
            
        #testString = "%s%s_%0.txt" %(folderPath, name)
        if os.path.isfile(fileName):
            fileUsed= open (fileName, 'a')
            headingString = '\nTrial starting at second: %s - Stimulus orientation degree: %s - Direction of the stimulus: %s \nTime taken by the stimulus to cross the screen: %s - Angular speed: %s\n' %(self.startingTime, self.stimAngle, self.stimDir, self.stimTime, self.angSpeed)
            fileUsed.write(headingString)
        else:
            fileUsed= open (fileName, 'w') 
            headingString = 'Experiment duration: %s seconds - Step used: %s\n\nTrial starting at second: %s - Stimulus orientation degree: %s - Direction of the stimulus: %s \nTime taken by the stimulus to cross the screen: %s - Angular speed: %s\n' %(self.duration, self.step, self.startingTime, self.stimAngle, self.stimDir, self.stimTime, self.angSpeed)
            fileUsed.write(headingString)
        fileUsed.write(str(self.position))
        fileUsed.write('\n')



# Ensure that relative paths start from the same directory as this script
#_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
#os.chdir(_thisDir)
_thisDir= 'C:\\Users\\Riffell Lab\\Documents\\visualStimDataFiles\\'

# Store info about the experiment session
myDlg = gui.Dlg(title="Visual stimulus trial")
myDlg.addText('Experiment info')
myDlg.addField('Duration (sec):', 150)
myDlg.addField('log file name:', 'ExperimentData')
myDlg.addText('Experiment data file saved in: %s' %(_thisDir))

expInfo={}
expInfo_data = myDlg.show()  # show dialog and wait for OK or Cancel
expInfo['duration']= expInfo_data[0]
expInfo['fileName']= expInfo_data[1]

if myDlg.OK == False:
    core.quit()  # user pressed cancel
expInfo['date'] = time.strftime("%m_%d_%y")  # add a simple timestamp


# Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
fileName = _thisDir + os.sep +expInfo_data[1] + '_%s' % (expInfo['date']) 

# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(name=expInfo_data[0], version='',
    extraInfo=expInfo_data, runtimeInfo=None,
    originPath=None,
    savePickle=True, saveWideText=True,
    dataFileName=fileName)
# save a log file for detail verbose info
logFile = logging.LogFile(fileName+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

endExpNow = False  # flag for 'escape' or other condition => quit the exp

# Start Code - component code to be run before the window creation



win = visual.Window(
    size=(1920, 1080), fullscr=True, screen=0,
    allowGUI=False, allowStencil=False,
    monitor=u'testMonitor', color=[-1,-1, -1], colorSpace='rgb',
    blendMode='avg', useFBO=True)
# store frame rate of monitor if we can measure it
expInfo['frameRate'] = win.getActualFrameRate()
if expInfo['frameRate'] != None:
    frameDur = 1.0 / round(expInfo['frameRate'])
else:
    frameDur = 1.0 / 60.0  # could not measure, so guess

# Initialize components for Routine "trial"
trialClock = core.Clock()
ISI = core.StaticPeriod(win=win, screenHz=expInfo['frameRate'], name='ISI')
#Parameters to use along the experiment
#Constants
RAD=1.1 #0.9
CTE_ANGLE=180       #Used to set the starting point of the stimulus in the screen
ANGLES= [0, 45, 90] #Angles for the stimulus
SIZE= len(ANGLES)   #Num. of angles used (valid for trial loop counter) 
COUNTER_LOOP= 5     #Num. of repeats for each stimulus movement loop
#obtain how many seconds each stimulus must be displayed
experiment_time = int(expInfo_data[0])
stimulus_time = experiment_time/6/COUNTER_LOOP         #experiment_time / 6 (number of stimulus patterns) / 5 (number of repeats for each pattern) 

#STEP= 0.01          #Velocity of the stimulus
#STEP= 0.0066445
STEP= (2.2*0.01/stimulus_time)/0.602


print "stimulus_time: %s" %stimulus_time
print "experiment_time: %s"%experiment_time
print "STEP: %s" %STEP
#Variables
index= 0            #Index for the ANGLES list
position_ptrn=[0,0] #Position of the stimulus

#******************************************************************************
#Send trigger signal and wait 10 seconds before start to display visual stimuli
#Thread creation and launch
print "STARTING DAQ with NI USB6008"
send_trigger_signal()
#time.sleep(10)     #10 second wait disabled. Laser & shutter configuration is done manually in prairie view

print"STARTING TRIAL"
print (time.strftime("%H:%M:%S"))
#******************************************************************************
# Setup the Window
# STARTING EXPERIMENT TIMER
start_time= time.time()

# Initialize components for Routine "left_to_right"
left_to_rightClock = core.Clock()

polygon = visual.Rect(
    win=win, name='polygon',
    width=[0.2, 4][0], height=[0.2, 4][1],
    ori=1.0, pos=[0,0],
    lineWidth=1, lineColor=u'blue', lineColorSpace='rgb',
    fillColor=u'blue', fillColorSpace='rgb',
    opacity=1, depth=-1.0, interpolate=True)

# Initialize components for Routine "right_to_left"
right_to_leftClock = core.Clock()

polygon_2 = visual.Rect(
    win=win, name='polygon_2',
    width=[0.2, 3][0], height=[0.2, 3][1],
    ori=1.0, pos=[0,0],
    lineWidth=1, lineColor=u'blue', lineColorSpace='rgb',
    fillColor=u'blue', fillColorSpace='rgb',
    opacity=1, depth=-1.0, interpolate=True)

# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine 

# set up handler to look after randomisation of conditions etc
trials = data.TrialHandler(nReps=SIZE, method='random', 
    extraInfo=expInfo, originPath=-1,
    trialList=[None],
    seed=None, name='trials')
thisExp.addLoop(trials)  # add the loop to the experiment
thisTrial = trials.trialList[0]  # so we can initialise stimuli with some values
# abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
if thisTrial != None:
    for paramName in thisTrial.keys():
        exec(paramName + '= thisTrial.' + paramName)

for thisTrial in trials:
    currentLoop = trials
    # abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
    if thisTrial != None:
        for paramName in thisTrial.keys():
            exec(paramName + '= thisTrial.' + paramName)
    
    # ------Prepare to start Routine "trial"-------
    t = 0
    trialClock.reset()  # clock
    frameN = -1
    continueRoutine = True
    routineTimer.add(0.300000)
    # update component parameters for each repeat
    angle= ANGLES[index]            #Used to find initial position & inclination angle of stimulus
    stimulus_angle= CTE_ANGLE-angle #Angle assigned to the stimulus
    # keep track of which components have finished
    trialComponents = [ISI]
    for thisComponent in trialComponents:
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    
    # -------Start Routine "trial"-------
    while continueRoutine and routineTimer.getTime() > 0:
        # get current time
        t = trialClock.getTime()
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *ISI* period
        if t >= 0.0 and ISI.status == NOT_STARTED:
            # keep track of start time/frame for later
            ISI.tStart = t
            ISI.frameNStart = frameN  # exact frame index
            ISI.start(0.3)
        elif ISI.status == STARTED:  # one frame should pass before updating params and completing
            ISI.complete()  # finish the static period
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in trialComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # check for quit (the Esc key)
        if endExpNow or event.getKeys(keyList=["escape"]):
            core.quit()
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # -------Ending Routine "trial"-------
    for thisComponent in trialComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    index+=1
    
    # set up handler to look after randomisation of conditions etc
    left_to_right_loop = data.TrialHandler(nReps=COUNTER_LOOP, method='random', 
        extraInfo=expInfo, originPath=-1,
        trialList=[None],
        seed=None, name='left_to_right_loop')
    thisExp.addLoop(left_to_right_loop)  # add the loop to the experiment
    thisLeft_to_right_loop = left_to_right_loop.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisLeft_to_right_loop.rgb)
    if thisLeft_to_right_loop != None:
        for paramName in thisLeft_to_right_loop.keys():
            exec(paramName + '= thisLeft_to_right_loop.' + paramName)
    
    for thisLeft_to_right_loop in left_to_right_loop:
        currentLoop = left_to_right_loop
        # abbreviate parameter names if possible (e.g. rgb = thisLeft_to_right_loop.rgb)
        if thisLeft_to_right_loop != None:
            for paramName in thisLeft_to_right_loop.keys():
                exec(paramName + '= thisLeft_to_right_loop.' + paramName)
        
        # ------Prepare to start Routine "left_to_right"-------
        t = 0
        countSteps=0
        left_to_rightClock.reset()  # clock
        frameN = -1
        continueRoutine = True
        routineTimer.add(stimulus_time)
        # update component parameters for each repeat
        #Calculate the initial positions of the stimulus
        if angle == 45:
            x= 1.5*np.cos(np.deg2rad(CTE_ANGLE+angle)) #1.5 used isntead to RAD value to avoit visual stimulus start in the screen
            y= 1.5*np.sin(np.deg2rad(CTE_ANGLE+angle))
        else:
            x= RAD*np.cos(np.deg2rad(CTE_ANGLE+angle))
            y= RAD*np.sin(np.deg2rad(CTE_ANGLE+angle))
        position_ptrn= [x,y]
        #Calculate the increment for x & y in function of stimulus angle
        if (angle == 0): 
            speed_x= STEP
            speed_y= 0
        elif (angle == 90):
            speed_x= 0
            speed_y= STEP
        else:
            #Valid only for a stimulus angle of 45 degrees
            speed_x= STEP*np.tan(np.deg2rad(CTE_ANGLE+angle))
            speed_y= STEP*np.tan(np.deg2rad(CTE_ANGLE+angle))
        obj_trial= exp_data(expInfo['duration'], STEP, angle, 'left_to_right')
        start_L2R= time.time()
#        print "start L2R time: %s" %start_L2R
#        print "position_ptrn[0] (x): %s" %position_ptrn[0]
#        print "position_ptrn[1] (y): %s" %position_ptrn[1]
        
        #add starting time and initial position of the stimulus to the object
        obj_trial.addStartingTime(start_L2R-start_time)
        obj_trial.addPosition(position_ptrn[0], position_ptrn[1])
        
        polygon.setOri(stimulus_angle)
        # keep track of which components have finished
        left_to_rightComponents = [polygon]
        for thisComponent in left_to_rightComponents:
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        
        # -------Start Routine "left_to_right"-------
        while continueRoutine and routineTimer.getTime() > 0:
            # get current time
            t = left_to_rightClock.getTime()
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            #Update the stimulus position in the screen
            position_ptrn[0]+= speed_x
            position_ptrn[1]+= speed_y
            #add position of the stimulus to the object
            obj_trial.addPosition(position_ptrn[0], position_ptrn[1])
            countSteps+=1
            
            # *polygon* updates
            if t >= 0.0 and polygon.status == NOT_STARTED:
                # keep track of start time/frame for later
                polygon.tStart = t
                polygon.frameNStart = frameN  # exact frame index
                polygon.setAutoDraw(True)
            frameRemains = 0.0 + stimulus_time - win.monitorFramePeriod * 0.75  # most of one frame period left
            if polygon.status == STARTED and t >= frameRemains:
                polygon.setAutoDraw(False)
            if polygon.status == STARTED:  # only update if drawing
                polygon.setPos(position_ptrn, log=False)
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in left_to_rightComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # check for quit (the Esc key)
            if endExpNow or event.getKeys(keyList=["escape"]):
                core.quit()
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # -------Ending Routine "left_to_right"-------
        for thisComponent in left_to_rightComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        
        #set the time required by the stimulus to cross the screen
        stimTime= time.time()-start_L2R
        obj_trial.addStimTime(stimTime)
        obj_trial.addAngSpeed(stimTime)
        #Save stimulus position list in the .txt file
        obj_trial.saveData(_thisDir, fileName, "test comment")
        #Erase stimulus position list for the next trial
        obj_trial.erasePositionList()
        
        #print "right to left trial -- angle: %s -- time: %f time in file: %f" %(angle, time.time()-start_L2R, stimTime)
        end_L2R= time.time()- start_L2R
        if (end_L2R- stimTime > .500):
            print "WARNING SAVE DATA IN FILE TOOK %f (more than 0.005 sec)" %(end_L2R- stimTime)
        else:
            time.sleep(0.005-(end_L2R-stimTime))
        
#        print "end L2R time: %s" %end_L2R
#        print "position_ptrn[0] (x): %s" %position_ptrn[0]
#        print "position_ptrn[1] (y): %s" %position_ptrn[1]
#        print "FILE SAVED --- COUNT STEPS: %s" %countSteps
        #print l2r_0.position
        thisExp.nextEntry()
        
    # completed COUNTER_LOOP repeats of 'left_to_right_loop'
    
    # set up handler to look after randomisation of conditions etc
    right_to_left_loop = data.TrialHandler(nReps=COUNTER_LOOP, method='random', 
        extraInfo=expInfo, originPath=-1,
        trialList=[None],
        seed=None, name='right_to_left_loop')
    thisExp.addLoop(right_to_left_loop)  # add the loop to the experiment
    thisRight_to_left_loop = right_to_left_loop.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisRight_to_left_loop.rgb)
    if thisRight_to_left_loop != None:
        for paramName in thisRight_to_left_loop.keys():
            exec(paramName + '= thisRight_to_left_loop.' + paramName)
    
    for thisRight_to_left_loop in right_to_left_loop:
        currentLoop = right_to_left_loop
        # abbreviate parameter names if possible (e.g. rgb = thisRight_to_left_loop.rgb)
        if thisRight_to_left_loop != None:
            for paramName in thisRight_to_left_loop.keys():
                exec(paramName + '= thisRight_to_left_loop.' + paramName)
        
        # ------Prepare to start Routine "right_to_left"-------
        t = 0
        right_to_leftClock.reset()  # clock
        frameN = -1
        continueRoutine = True
        routineTimer.add(stimulus_time)
        # update component parameters for each repeat
        #Calculate the initial positions of the stimulus
        if angle == 45:
            x= 1.5*np.cos(np.deg2rad(2*CTE_ANGLE+angle)) #1.5 used isntead to RAD value to avoit visual stimulus start in the screen
            y= 1.5*np.sin(np.deg2rad(2*CTE_ANGLE+angle))
        else:
            x= RAD*np.cos(np.deg2rad(2*CTE_ANGLE+angle))
            y= RAD*np.sin(np.deg2rad(2*CTE_ANGLE+angle))
        position_ptrn= [x,y]
        #Calculate the increment for x & y in function of stimulus angle
        if (angle == 0): 
            speed_x= STEP*(-1)
            speed_y= 0
        elif (angle == 90):
            speed_x= 0
            speed_y= STEP*(-1)
        else:
            #Valid only for a stimulus angle of 45 degrees
            speed_x= STEP*np.tan(np.deg2rad(CTE_ANGLE-angle))
            speed_y= STEP*np.tan(np.deg2rad(CTE_ANGLE-angle))
        obj_trial= exp_data(expInfo['duration'], STEP, angle, 'right_to _left')
        start_R2L= time.time()
#        print "start R2L time: %s" %start_R2L
#        print "position_ptrn[0] (x): %s" %position_ptrn[0]
#        print "position_ptrn[1] (y): %s" %position_ptrn[1]
         
        #add initial position of the stimulus to the object
        obj_trial.addStartingTime(start_R2L-start_time)
        obj_trial.addPosition(position_ptrn[0], position_ptrn[1])
        
        polygon_2.setOri(stimulus_angle)
        # keep track of which components have finished
        right_to_leftComponents = [polygon_2]
        for thisComponent in right_to_leftComponents:
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        
        # -------Start Routine "right_to_left"-------
        while continueRoutine and routineTimer.getTime() > 0:
            # get current time
            t = right_to_leftClock.getTime()
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            #Update the stimulus position in the screen
            position_ptrn[0]+= speed_x
            position_ptrn[1]+= speed_y
            
            #add position of the stimulus to the object
            obj_trial.addPosition(position_ptrn[0], position_ptrn[1])
            
            # *polygon_2* updates
            if t >= 0.0 and polygon_2.status == NOT_STARTED:
                # keep track of start time/frame for later
                polygon_2.tStart = t
                polygon_2.frameNStart = frameN  # exact frame index
                polygon_2.setAutoDraw(True)
            frameRemains = 0.0 + stimulus_time - win.monitorFramePeriod * 0.75  # most of one frame period left
            if polygon_2.status == STARTED and t >= frameRemains:
                polygon_2.setAutoDraw(False)
            if polygon_2.status == STARTED:  # only update if drawing
                polygon_2.setPos(position_ptrn, log=False)
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in right_to_leftComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # check for quit (the Esc key)
            if endExpNow or event.getKeys(keyList=["escape"]):
                core.quit()
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # -------Ending Routine "right_to_left"-------
        for thisComponent in right_to_leftComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        
        #set the time required by the stimulus to cross the screen
        stimTime= time.time()-start_R2L
        obj_trial.addStimTime(stimTime)
        obj_trial.addAngSpeed(stimTime)
        #Save stimulus position list in the .txt file
        obj_trial.saveData(_thisDir, fileName, "test comment")
        #Erase stimulus position list for the next trial
        obj_trial.erasePositionList()
        print "right to left trial -- angle: %s -- time: %f time in file: %f" %(angle, time.time()-start_R2L, stimTime)
        end_R2L= time.time()- start_R2L
        if (end_R2L-stimTime > 0.005):
            print "WARNING SAVE DATA IN FILE TOOK %f (more than 0.005 sec)" %(end_R2L- stimTime)
        else:
            time.sleep(0.005-(end_R2L-stimTime))
        
#        print "end R2L time: %s" %end_R2L
#        print "position_ptrn[0] (x): %s" %position_ptrn[0]
#        print "position_ptrn[1] (y): %s" %position_ptrn[1]
        thisExp.nextEntry()
        
    # completed COUNTER_LOOP repeats of 'right_to_left_loop'
    
    thisExp.nextEntry()
    
# completed SIZE repeats of 'trials'


#end_time=time.time()
#total_time= end_time-start_time
print "EXP duration time= %s" % (time.time()-start_time)#total_time

# these shouldn't be strictly necessary (should auto-save)
thisExp.saveAsWideText(fileName+'.csv')
thisExp.saveAsPickle(fileName)
logging.flush()
# make sure everything is closed down
thisExp.abort()  # or data files will save again on exit
win.close()
core.quit()
