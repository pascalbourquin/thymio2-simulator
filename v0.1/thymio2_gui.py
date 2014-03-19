import threading

from Tkinter import *
from thymio2 import *

thymio = None
widgets_leds_prox_h = [None, None, None, None, None, None, None, None]
widgets_prox_h = [None, None, None, None, None, None, None]
widgets_leds_prox_v = [None, None]
widgets_prox_v = [None, None]
widgets_leds_circle = [None, None, None, None, None, None, None, None]
widgets_leds_buttons = [None, None, None, None, None]
widgets_buttons = [None, None, None, None, None]
widgets_motor_target = [None, None]

BUTTONS_TEMPO = 1000
timers_buttons = [0, 0, 0, 0, 0]

#MAX=4000 MIN=900 cf. behavior_leds_prox
PROX_H_THRESHOLD = (4000-900) // 2

def EventMoteur(nouvelleValeur):
    # nouvelle valeur en argument
    #print 'param=', nouvelleValeur
    pass

def MenuOuvrir():
	pass
	
def PlacerLed(canvas, x, y):
	l = canvas.create_oval(x-10,y-10,x+10,y+10,fill='red')
	return l

def PlacerLeds(canvas):
	widgets_leds_prox_h[0] = PlacerLed(canvas, 109, 160)
	widgets_leds_prox_h[1] = PlacerLed(canvas, 222, 95)
	widgets_leds_prox_h[2] = PlacerLed(canvas, 332, 70)
	widgets_leds_prox_h[3] = PlacerLed(canvas, 372, 70)
	widgets_leds_prox_h[4] = PlacerLed(canvas, 480, 95)
	widgets_leds_prox_h[5] = PlacerLed(canvas, 597, 160)
	widgets_leds_prox_h[6] = PlacerLed(canvas, 190, 621)
	widgets_leds_prox_h[7] = PlacerLed(canvas, 516, 621)

	#widgets_leds_prox_v[0] = PlacerLed(canvas, 283, 92)
	#widgets_leds_prox_v[1] = PlacerLed(canvas, 422, 92)

	widgets_leds_circle[0] = PlacerLed(canvas, 351, 98)
	widgets_leds_circle[1] = PlacerLed(canvas, 443, 137)
	widgets_leds_circle[2] = PlacerLed(canvas, 481, 227)
	widgets_leds_circle[3] = PlacerLed(canvas, 443, 321)
	widgets_leds_circle[4] = PlacerLed(canvas, 351, 360)
	widgets_leds_circle[5] = PlacerLed(canvas, 262, 321)
	widgets_leds_circle[6] = PlacerLed(canvas, 225, 227)
	widgets_leds_circle[7] = PlacerLed(canvas, 262, 137)

	widgets_leds_buttons[HW_BUTTONS_BACKWARD] 	= PlacerLed(canvas, 351, 300)
	widgets_leds_buttons[HW_BUTTONS_LEFT] 		= PlacerLed(canvas, 280, 227)
	widgets_leds_buttons[HW_BUTTONS_CENTER]		= PlacerLed(canvas, 362, 227)
	widgets_leds_buttons[HW_BUTTONS_FORWARD]	= PlacerLed(canvas, 351, 156)
	widgets_leds_buttons[HW_BUTTONS_RIGHT]		= PlacerLed(canvas, 420, 227)

def EventBouton(numBouton):
	if numBouton == HW_BUTTONS_BACKWARD or \
	   numBouton == HW_BUTTONS_LEFT or \
	   numBouton == HW_BUTTONS_CENTER or \
	   numBouton == HW_BUTTONS_FORWARD or \
	   numBouton == HW_BUTTONS_RIGHT:
		AsebaVmLockHardware()
		thymio['hardware']['buttons'][numBouton] = 1
		thymio['hardware']['leds_buttons'][numBouton] = 32
		AsebaVmUnlockHardware()
		timers_buttons[numBouton] = BUTTONS_TEMPO

def EventProxHorizontal(numProx):
	print 'EventProxHorizontal: numProx=' + str(numProx)
	AsebaVmLockHardware()
	thymio['hardware']['prox_h'][numProx] = widgets_prox_h[numProx].get()
	if thymio['hardware']['prox_h'][numProx] < PROX_H_THRESHOLD:
		valLed = 32
	else:
		valLed = 0
	
	if 0 <= numProx <= 1:
		thymio['hardware']['leds_prox_h'][numProx] = valLed
	elif numProx == 2:
		thymio['hardware']['leds_prox_h'][numProx] = valLed
		thymio['hardware']['leds_prox_h'][numProx+1] = valLed
	elif 3 <= numProx <= 6:
		thymio['hardware']['leds_prox_h'][numProx+1] = valLed
	AsebaVmUnlockHardware()
	
def PlacerBouton(canvas, x, y, c):
	b = Button(canvas, text = ' ', command = c)
	b.place(x=x, y=y)
	return b
	
def PlacerBoutons(canvas):
	widgets_buttons[HW_BUTTONS_BACKWARD] = PlacerBouton(canvas, 345, 313, lambda: EventBouton(HW_BUTTONS_BACKWARD))
	widgets_buttons[HW_BUTTONS_LEFT] = PlacerBouton(canvas, 255, 215, lambda: EventBouton(HW_BUTTONS_LEFT))
	widgets_buttons[HW_BUTTONS_CENTER] = PlacerBouton(canvas, 335, 215, lambda: EventBouton(HW_BUTTONS_CENTER))
	widgets_buttons[HW_BUTTONS_FORWARD] = PlacerBouton(canvas, 345, 120, lambda: EventBouton(HW_BUTTONS_FORWARD))
	widgets_buttons[HW_BUTTONS_RIGHT] = PlacerBouton(canvas, 433, 215, lambda: EventBouton(HW_BUTTONS_RIGHT))
	
def PlacerMoteurs(canvas):
	widgets_motor_target[HW_MOTOR_RIGHT_TARGET] = Scale(canvas, from_=500, to=-500, orient=VERTICAL, length=170, width=10, command=None)
	widgets_motor_target[HW_MOTOR_RIGHT_TARGET].place(x=580, y=400)
	widgets_motor_target[HW_MOTOR_LEFT_TARGET] = Scale(canvas, from_=500, to=-500, orient=VERTICAL, length=170, width=10, command=None)
	widgets_motor_target[HW_MOTOR_LEFT_TARGET].place(x=80, y=400)

def PlacerProxHorizontal(canvas):
	widgets_prox_h[0] = Scale(canvas, from_=0, to=4300, orient=HORIZONTAL, length=40, width=20, command=lambda x: EventProxHorizontal(0))
	widgets_prox_h[1] = Scale(canvas, from_=0, to=4300, orient=HORIZONTAL, length=40, width=20, command=lambda x: EventProxHorizontal(1))
	widgets_prox_h[2] = Scale(canvas, from_=0, to=4300, orient=HORIZONTAL, length=40, width=20, command=lambda x: EventProxHorizontal(2))
	widgets_prox_h[3] = Scale(canvas, from_=0, to=4300, orient=HORIZONTAL, length=40, width=20, command=lambda x: EventProxHorizontal(3))
	widgets_prox_h[4] = Scale(canvas, from_=0, to=4300, orient=HORIZONTAL, length=40, width=20, command=lambda x: EventProxHorizontal(4))
	widgets_prox_h[5] = Scale(canvas, from_=0, to=4300, orient=HORIZONTAL, length=40, width=20, command=lambda x: EventProxHorizontal(5))
	widgets_prox_h[6] = Scale(canvas, from_=0, to=4300, orient=HORIZONTAL, length=40, width=20, command=lambda x: EventProxHorizontal(6))
	widgets_prox_h[0].set(4300)
	widgets_prox_h[1].set(4300)
	widgets_prox_h[2].set(4300)
	widgets_prox_h[3].set(4300)
	widgets_prox_h[4].set(4300)
	widgets_prox_h[5].set(4300)
	widgets_prox_h[6].set(4300)
	widgets_prox_h[0].place(x=60, y=100)
	widgets_prox_h[1].place(x=180, y=30)
	widgets_prox_h[2].place(x=330, y=10)
	widgets_prox_h[3].place(x=475, y=30)
	widgets_prox_h[4].place(x=595, y=100)
	widgets_prox_h[5].place(x=165, y=640)
	widgets_prox_h[6].place(x=490, y=640)

def PlacerProxVertical(canvas):
	widgets_prox_v[0] = Scale(canvas, from_=0, to=4300, orient=HORIZONTAL, length=40, width=20, command=None)
	widgets_prox_v[0].place(x=255, y=35)
	widgets_prox_v[1] = Scale(canvas, from_=0, to=4300, orient=HORIZONTAL, length=40, width=20, command=None)
	widgets_prox_v[1].place(x=405, y=35)
	
REFRESH_TIME = 100	

def UpdateLed(canvas, val, widgetLedNum):
	if val < 1:
		canvas.itemconfig(widgetLedNum, fill='black')
	else:
		canvas.itemconfig(widgetLedNum, fill='red')

def UpdateLeds(canvas):
	for i in range(5):
		UpdateLed(canvas, thymio['hardware']['leds_buttons'][i], widgets_leds_buttons[i])
	for i in range(8):
		UpdateLed(canvas, thymio['hardware']['leds_circle'][i], widgets_leds_circle[i])
	for i in range(8):
		UpdateLed(canvas, thymio['hardware']['leds_prox_h'][i], widgets_leds_prox_h[i])
	
def UpdateButtonsTimers():
	#print timers_buttons
	for i in range(5):
		timers_buttons[i] = timers_buttons[i] - REFRESH_TIME
		if timers_buttons[i] < 0:
			timers_buttons[i] = 0
			thymio['hardware']['buttons'][i] = 0
			thymio['hardware']['leds_buttons'][i] = 0

def UpdateMotors(canvas):
	widgets_motor_target[HW_MOTOR_LEFT_TARGET].set(thymio['hardware']['motor_targets'][HW_MOTOR_LEFT_TARGET])
	widgets_motor_target[HW_MOTOR_RIGHT_TARGET].set(thymio['hardware']['motor_targets'][HW_MOTOR_RIGHT_TARGET])
	return
				
def UpdateGUI(canvas):
	AsebaVmLockHardware()
	UpdateButtonsTimers()
	UpdateLeds(canvas)
	UpdateMotors(canvas)
	AsebaVmUnlockHardware()
	Win.after(REFRESH_TIME, UpdateGUI, canvas)

Win = Tk()

# MENU

menubar = Menu(Win)

menufichier = Menu(menubar,tearoff=0)
menufichier.add_command(label="Ouvrir une image",command=MenuOuvrir)
menufichier.add_command(label="Fermer l'image",command=MenuOuvrir)
menufichier.add_command(label="Quitter",command=Win.destroy)
menubar.add_cascade(label="Fichier", menu=menufichier)

menuaide = Menu(menubar,tearoff=0)
menuaide.add_command(label="A propos",command=MenuOuvrir)
menubar.add_cascade(label="Aide", menu=menuaide)

Win.config(menu=menubar)

# DESSIN PRINCIPAL

Dessin = Canvas(Win)

photo = PhotoImage(file='images/thymio2.gif')
Dessin.create_image(0,0,anchor=NW,image=photo)
Dessin.config(height=700,width=700)
Dessin.pack(side = LEFT, padx = 0, pady = 0)


#Bouton = Button(Dessin, text ='Effacer', command = lambda: EventBouton(HW_BUTTONS_BACKWARD))
#Bouton.place(x=200, y=200)

'''
EventTimer()
'''

PlacerLeds(Dessin)
PlacerBoutons(Dessin)
PlacerMoteurs(Dessin)
PlacerProxHorizontal(Dessin)
#PlacerProxVertical(Dessin)

#Dessin.itemconfig(leds_buttons[0], fill='blue')

thymio = AsebaVmInit()
thread_thymio = threading.Thread(group=None, target=AsebaVmMainLoop, args=(thymio,))
thread_thymio.start()

UpdateGUI(Dessin)

Win.mainloop()

