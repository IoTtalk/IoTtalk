
g=9.8
size = 0.7
scene = display(width=600, height=500, background=vector(0.6,0.3,0.2), center=vector(-7,7,0))
floor = box(length=24, height=0.5, width=4, color=color.green, pos=vector(-9,0,0))
box(length=8, height=0.5, width=4, color=color.red, pos= vector(7,0,0) )
box(length=8, height=0.5, width=4, color=color.green, pos= vector(15,0,0) )

scene.range=16
camera_x1=0.8
camera_x2=0.0
scene.forward=vector(camera_x1,camera_x2,-1)

preloadAudio('Startup.wav')
preloadAudio('chord.wav')
preloadAudio('gj.wav')

def balljump(spd):
    if (spd < 3): return 

    ball = sphere(pos=vector(-24.5, 10.0, 0.0), radius=size, color=color.white)
    ball.velocity = vector(spd, -1.0, 0.0)

    dt = 0.003
    gj_playFlag=1

    def resetScene():
        scene.background = vector(0.6, 0.3, 0.2)
        
    
    def jump():
        global gj_playFlag

        #console.log(ball.pos.x, ball.pos.y)
        if ball.pos.x < 15:
          rate(1000, jump)
        else:
          ball.visible = False
          gj_playFlag = 1 
          return

        if (ball.pos.x < 10 and ball.pos.x > 1.5) and ball.pos.y < 1 :
            scene.background = vector(0,0,0)
            if gj_playFlag: 
                playAudio('gj.wav') 
                gj_playFlag=0
            rate(4, resetScene)
		
        previous_x = ball.pos.x
        ball.pos = ball.pos + ball.velocity * dt

        if ball.pos.y < size and ball.velocity.y < 0:
            ball.velocity.y = - ball.velocity.y
            playAudio('chord.wav')
        else:
            ball.velocity.y = ball.velocity.y - g * dt
    
    jump()

def Speed(data):
    if data != None:
        balljump(data[0])

def setup():
    profile = {
        'dm_name': 'Ball-throw2',
        'odf_list': [Speed],
    }

    dai(profile)
    playAudio('Startup.wav')

setup()

