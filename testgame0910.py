import sys, random
import pygame
from pygame.locals import *
import numpy as np

white = (255,255,255)
black = (0,0,0)
cyaan = (0,255,255)
yellow = (255,255,0)
red=(255,100,0)
#setting
screen_size=(500,1000)
field_size=(300,600)
flag_pos=1.2
time_now = 0
time_old = 0
start_time=0
dx=field_size[0]/screen_size[0]
dy=field_size[1]/screen_size[1]
class tagsp_probe:
    def __init__(self,x,y,vx,vy,pitch):
        self.r_init=np.array([[x],[y],[vx],[vy],[1]])
        self.r=np.array([[x],[y],[vx],[vy],[1]])
        self.pitch_init=pitch
        self.pitch=pitch
        self.shape=np.array([[3,3,9,9,12,12,9,9,3,3,9,-9,-3,-3,-9,-9,-12,-12,-9,-9,-3,-3],[15,10,10,15,15,-4,-4,4,4,-10,-15,-15,-10,4,4,-4,-4,15,15,10,10,15]])
        self.crush_shape=[np.array([[15,9,9,14,9,9,15,6,2,0,-2,-6,-15,-9,-9,-14,-9,-9,-15,-6,-2,0,2,6],[15,6,2,0,-2,-6,-15,-9,-9,-14,-9,-9,-15,-6,-2,0,2,6,15,9,9,14,9,9]]),np.array([[5,0,-5,0],[0,-5,0,5]])]
        self.shape_init=np.array([[3,3,9,9,12,12,9,9,3,3,9,-9,-3,-3,-9,-9,-12,-12,-9,-9,-3,-3],[15,10,10,15,15,-4,-4,4,4,-10,-15,-15,-10,4,4,-4,-4,15,15,10,10,15]])
        self.frame=[np.array([[-10,-11,-16,-5],[-4,-4,-10,-10]]),np.array([[10,11,16,5],[-4,-4,-10,-10]]),np.array([[10,11,13,8],[-4,-4,-8,-8]]),np.array([[-10,-11,-13,-8],[-4,-4,-8,-8]])]
        self.end_time=12
        self.rocket_mass_ratio=0.97
        self.state="engine off"
        self.T=110
    def reset(self):
        self.r=self.r_init
        self.pitch=self.pitch_init
        self.state="engine on"
    def draw(self,t):
        probe_att=np.array([[np.cos(self.pitch),np.sin(self.pitch)],[np.sin(self.pitch),-np.cos(self.pitch)]])@self.shape
        probe_loc=np.array([[self.r[0,0]/dx+screen_size[0]/2],[screen_size[1]*0.95-self.r[1,0]/dy]])@np.ones((1,self.shape.shape[1]))
        probe=((probe_att+probe_loc).T).tolist()
        pygame.draw.polygon(screen,cyaan,probe)
        if self.state=="engine on":
            for i in range(len(self.frame)):
                frame_att=np.array([[np.cos(self.pitch),np.sin(self.pitch)],[np.sin(self.pitch),-np.cos(self.pitch)]])@self.frame[i]
                frame_loc=np.array([[self.r[0,0]/dx+screen_size[0]/2],[screen_size[1]*0.95-self.r[1,0]/dy]])@np.ones((1,self.frame[i].shape[1]))
                frame=((frame_att+frame_loc).T).tolist()
                if i<2:
                    pygame.draw.polygon(screen,((t*1000)%135+120,0,0),frame)
                else:
                    pygame.draw.polygon(screen,((t*2000)%135+120,200,0),frame)
        elif self.state=="crushed" or self.state=="time over":
            explosion_loc=np.array([[self.r[0,0]/dx+screen_size[0]/2],[screen_size[1]*0.95-self.r[1,0]/dy]])@np.ones((1,self.crush_shape[0].shape[1]))
            explosion=((explosion_loc+self.crush_shape[0]).T).tolist()
            pygame.draw.polygon(screen,red,explosion)
            explosion_loc=np.array([[self.r[0,0]/dx+screen_size[0]/2],[screen_size[1]*0.95-self.r[1,0]/dy]])@np.ones((1,self.crush_shape[1].shape[1]))
            explosion=((explosion_loc+self.crush_shape[1]).T).tolist()
            pygame.draw.polygon(screen,yellow,explosion)
    def eqm(self,x):
        m=20*(x[4,0]*(1-self.rocket_mass_ratio)+self.rocket_mass_ratio)
        g=9.393e20*6.6743e-11/(x[1,0]+473e3)**2
        a=self.T/m
        return np.vstack([x[2:4,0:1],np.array([[a*np.sin(self.pitch)],[-g+a*np.cos(self.pitch)],[-1/self.end_time]])])
    def update(self,dt):
        if self.state=="engine on":
            k1=self.eqm(self.r)
            k2=self.eqm(self.r+k1*dt/2)
            k3=self.eqm(self.r+k2*dt/2)
            k4=self.eqm(self.r+k3*dt)
            self.r=self.r+dt/6*(k1+2*k2+2*k3+k4)
    def flag_check(self):
        if self.state=="engine on" and self.r[1,0]<=0:
            if abs(self.r[3,0])<20:
                self.state="landed"
            else:
                self.state="crushed"
        elif self.state=="engine on" and self.r[4,0]<0:
            self.state="time over"
def draw_gauge(screen,fuel_remain): # fuel gauge
    screen.fill(white,(10,150,40,204))
    screen.fill(black,(12,152,36,200))
    decrease=(1-fuel_remain)*200
    screen.fill(yellow,(12,152+decrease,36,200-decrease))
    text = font.render(str(100-int(decrease/2))+"%", True,white)
    screen.blit(text,(10,100))
def draw_flag(screen,x):
    screen.fill(white,(screen_size[0]/2+x/dx-1,screen_size[1]*0.95-25,2,25))
    screen.fill(yellow,(screen_size[0]/2+x/dx+1,screen_size[1]*0.95-25,18,12))
def draw_backgroud(screen):
    screen.fill(black)
    screen.fill(white,(0,screen_size[1]*0.95,600,screen_size[1]*0.06))
def draw_score(screen,x,target):
    text = font.render(str(int(abs(x-target)))+"m from target", True,white)
    screen.blit(text,(100,200))
def check_key(key,prope):
    global theta,engine,x,start_time
    if key==K_SPACE:
        probe.reset()
        start_time=pygame.time.get_ticks()/1000
    elif key == K_LEFT:
        probe.pitch-=np.pi/12
    elif key == K_RIGHT:
        probe.pitch+=np.pi/12
pygame.init()
engine=False
screen=pygame.display.set_mode(screen_size)
font = pygame.font.SysFont(None, 50)
probe=tagsp_probe(-80,500,0,-70,-np.pi/12)
while True:
    time_old=time_now
    time_now=pygame.time.get_ticks()/1000
    dt=(time_now-time_old)
    draw_backgroud(screen)
    draw_flag(screen,flag_pos)
    probe.flag_check()
    probe.update(dt)
    probe.draw(time_now)
    if probe.state=="engine on":
        draw_gauge(screen,probe.r[4,0])
    if probe.state=="landed":
        text = font.render(str(int(abs(probe.r[0,0]-flag_pos)))+" m from target", True,white)
        screen.blit(text,(100,150))
    if probe.state=="crushed":
        text = font.render("probe crushed", True,white)
        screen.blit(text,(100,150))
    if probe.state=="time over":
        text = font.render("time over", True,white)
        screen.blit(text,(100,150))
    if not probe.state=="engine on":
        text = font.render("press space to start", True,white)
        screen.blit(text,(100,200))
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            check_key(event.key,probe)