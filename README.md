# triggerSignal_and_stimulusMoving
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
