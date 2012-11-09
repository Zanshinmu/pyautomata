#!/usr/bin/python
import Image
import ImageOps
import random
import sys
import os
import threading
import math
from threading import Thread
import pygame
from pygame.locals import *
import wx

condition = threading.Condition()

class Worker(Thread):
   def __init__ (self, rule, lines, step, seed):
      Thread.__init__(self)
      self.rule = rule
      self.lines = lines
      self.step = step
      self.seed = seed
   def run(self):
        condition.acquire()
        result, dims = line( self.rule,  self.lines, self.step, self.seed)
        showResult( self.rule ,result, dims)
        condition.notify()
        condition.release()

def step(a, rule, k=2, r=1):
    nbrs = [a[c:] + a[:c] for c in range(-r, r+1, 1)]
    l = []
    for t in apply(zip, nbrs):
        result = 0
        for i in t:
            result = (result * k) + i
        l.append(result)
    return [((rule / (k ** v)) % k) for v in l]

def line(rule, steps, stepper, seed, k=2, r=1):
    seed = ([0] * steps) + seed + ([0] * steps)
    result = seed[:]
    for i in range(steps):
        seed = stepper(seed, rule, k=k, r=r)
        result += seed[:]
    return result, (len(seed), steps + 1)

def pil_to_pygame_img(pil_img):
    imgstr = pil_img.tostring()
    return pygame.image.fromstring(imgstr, pil_img.size, 'RGB')

def showResult(n,result, dims, k=2):
    i = Image.new("RGB", dims)
    i.putdata(result)
    i = ImageOps.autocontrast(i)
    new = pil_to_pygame_img(i)
    screen = pygame.display.get_surface()
    if not screen.get_width == dims[1]:
      initScreen(dims[0],dims[1])
    screen.blit(pil_to_pygame_img(i),(0,0))
    if pygame.font:
    	font = pygame.font.Font(None, 36)
    	ts = 'Rule ' + str(n)
    	text = font.render(ts, 1, (255, 255, 10))
    	textpos = text.get_rect()
    	textpos.centerx = screen.get_rect().centery
    	screen.blit(text, textpos)
    pygame.display.flip()

def runAutomata(n,lines, seed):
    worker = Worker(n,lines,step,seed)
    worker.setDaemon(True)
    condition.acquire()
    worker.start()
    condition.wait()

def initScreen(x,y):
   screen = pygame.display.set_mode((x,y))
   pygame.display.set_caption('Cellular Automata')
   pygame.mouse.set_visible(0)
   background = pygame.Surface(screen.get_size())
   background = background.convert()
   background.fill((0, 0, 0))
   screen.blit(background, (0, 0))
   pygame.display.flip()

class MyFrame(wx.Frame):
   def __init__(self,parent,id):
      wx.Frame.__init__(self,parent,wx.ID_ANY,size = (350, 150),title="Controls")
      self.label1 = wx.StaticText(self,-1,"Rule",(1, 20))
      self.slider1 = wx.Slider(self, -1, 30, 0, 255, (50, 10), (300, 50),wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
      self.label2 = wx.StaticText(self,-1,"Lines",(1, 70))
      self.slider2 = wx.Slider(self, -1, 50, 300, 800, (50, 50), (300, 50),wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
      self.label3 = wx.StaticText(self,-1,"Seed",(1, 120))
      self.slider3 = wx.Slider(self, -1, 1, 0, 16, (50, 90), (300, 50),wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
      self.Bind(wx.EVT_SLIDER, self.sliderUpdate)
      self.sliderUpdate(self)
      
   def sliderUpdate(self, event):
       runAutomata(self.slider1.GetValue(),self.slider2.GetValue(), [int(x) for x in str(self.slider3.GetValue()).zfill(1)])
   
        
if ( __name__ == "__main__"):
   pygame.init()
   initScreen(300,300)
   app=wx.PySimpleApp()
   frame=MyFrame(None,-1)
   frame.Show()
   app.MainLoop()
  
        

