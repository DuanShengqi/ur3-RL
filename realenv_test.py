##################################################################
# This file is the real training environment.
# Include the state transfer. All the image processing are not here.
# Modified by xfyu on May 19, 2018.
##################################################################
#!/usr/bin/env python
import os
import random
import time
import cv2
import numpy
import pycontrol as ur
#################################################################
# Important global parameters
#################################################################
# PATH = "/home/robot/RL" # current working path
PATH = os.path.split(os.path.realpath(__file__))[0]
PIC_NAME = 'pic.jpg'
# IMAGE_PATH = '/home/robot/RL/grp1'
SUCCESS_REWARD = 100
FAILURE_REWARD = -100
ACTION_REWARD = 1
MAX_STEPS = 20
# maximum and minimum limitations, a little different from collectenv.py
# only part of the data is used: from 150.jpg to 180.jpg
MAX_ANGLE = 69.0
MIN_ANGLE = 30.0
CHANGE_POINT_RANGE = 1.5
# actions,just symbols
COARSE_POS = 0.3*8.7
FINE_POS = 0.3
TERMINAL = 0
FINE_NEG = -0.3
COARSE_NEG = -0.3*8.7

class FocusEnv():
    def __init__(self):
	# COARSE NEG, FINE NEG, TERMINAL, FINE POS, COARSE POS
	self.actions = [COARSE_NEG, FINE_NEG, TERMINAL, FINE_POS, COARSE_POS]
	self.cur_state = 0.0 # initial with 0
	ur.system_init()

    def __del__(self):
	ur.system_close()

    def reset(self):
    	# record the final state of last episode
    	last_state = self.cur_state
    	last_state = round(last_state, 2) # just in case
	# randomly decide the new initial state
	state = random.random() * (MAX_ANGLE - MIN_ANGLE)
	self.cur_state = MIN_ANGLE + state
	self.cur_state = round(self.cur_state, 2)
	self.cur_step = 0
	# move from 0 to the initial state and take a pic
	# return the angle of first state and the name of the pic
	self.move(last_state, self.cur_state)
	ur.camera_take_pic(PIC_NAME)

	return self.cur_state, os.path.join(PATH, PIC_NAME)

    '''
    step - regulations of transfering between states

    Input: input_action
    Return: next_state - the total angle of next state
    	    next_image_path - the image path of next state(the dictionary is not accessible from outside)
    	    reward - reward of this single operation
    	    terminal - True or False
    '''
    def step(self, input_action): # action is the angle to move
    	self.cur_step = self.cur_step + 1
    	last_state = self.cur_state
    	last_state = round(last_state, 2) # just in case
    	# update self.cur_state 
	self.cur_state = self.cur_state + input_action
        self.cur_state = round(self.cur_state, 2)
        # move to the next state and take a pic
        if abs(input_action) > 1: # COARSE
        	ur.change_focus_mode(ur.COARSE)
        else: # fine
        	ur.change_focus_mode(ur.FINE)
        if input_action > 0: # UP
        	ur.send_movej_screw(ur.UP)
        elif input_action < 0: # DOWN
        	ur.send_movej_screw(ur.DOWN)
        ur.camera_take_pic(PIC_NAME)
        next_image_path = os.path.join(PATH, PIC_NAME)

    	# special termination
    	if self.cur_state > MAX_ANGLE or self.cur_state < MIN_ANGLE:
    	    	return self.cur_state, next_image_path, True, False
	# choose to terminate
	if input_action == TERMINAL:
			# the second true only represents that terminating by TERMINAL action
	    	return self.cur_state, next_image_path, True, True

	# special case - failure
	if self.cur_step >= MAX_STEPS:
	    	return self.cur_state, next_image_path, True, False

	return self.cur_state, next_image_path, False, False
	
	'''
    def TENG(self, img):
    	guassianX = cv2.Sobel(img, cv2.CV_64F, 1, 0)
    	guassianY = cv2.Sobel(img, cv2.CV_64F, 1, 0)
    	return numpy.mean(guassianX * guassianX + 
    					  guassianY * guassianY)
	'''

    '''
    move - move the ur3 from start_angle to end_angle
    '''
    def move(self, start_angle, end_angle):
    ur.change_focus_mode(ur.FINE)
	ur.move_from_to(start_angle, end_angle)
	print("move from", start_angle, end_angle)