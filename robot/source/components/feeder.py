try:
    import wpilib
except:
    import fake_wpilib as wpilib


INITIAL_SPD = 0    
FEED_SPD = .5
ZERO_FRISBEE = .5
ONE_FRISBEE = 1
TWO_FRISBEE = 1.5
THREE_FRISBEE = 2.0 
FOUR_FRISBEE = 2.5

FrisbeeCount = "Frisbee Count"

class Feeder():

    def __init__(self, feed_motor, frisbee_sensor, feed_sensor):
        self.feed_motor.Set(INITIAL_SPD)
        self.update = None
        self.feed_motor = INITIAL_SPD
    def Feed(self):
        "'makes the feed motor go 1 full rotation then stops'"
        self.state = 1
        if self.feed_sensor.Get() >= 0 and self.state == 1:
            self.update = True        
            self.state = 2
        if self.feed_sensor.Get() >= 1000 and self.state == 2:
            self.update = False
            
    def GetFrisbeeCount(self):
        "'Gets the distance away an object is from the sensor based on the voltage of the sensor'"
        if self.frisbee_sensor.GetVoltage() >= ZERO_FRISBEE:
            frisbee_count = 0
            return 0
        elif self.frisbee_sensor.GetVoltage() >= ONE_FRISBEE:
            frisbee_count = 1
            return 1
        elif self.frisbee_sensor.GetVoltage() >= TWO_FRISBEE:
            frisbee_count = 2
            return 2
        elif self.frisbee_sensor.GetVoltage() >= THREE_FRISBEE:
            frisbee_count = 3
            return 3
        elif self.frisbee_sensor.GetVoltage() >= FOUR_FRISBEE:
            frisbee_count = 4
            return 4
        wpilib.SmartDashboard.PutDouble(FrisbeeCount, frisbee_count)
"'Alternate frisbee counter: if the top sensor is receiving a value then their are 4 frisbees, if the 2nd sensor is receving a value and the top isn't then there are three frisbees, if all frisbees are recoving no value then there are zero frisbees then there are 0 frisbees'"

    def Update():
        
        if self.update == True:
            self.feed_motor.Set(FEED_SPD)
            self.update = False
        if self.update == False:
            self.feed_motor.Set(INITIAL_SPD)
    