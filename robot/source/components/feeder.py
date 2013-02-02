
try:
    import wpilib
    import wpilib.SmartDashboard
except:
    import fake_wpilib as wpilib
    import fake_wpilib.SmartDashboard

initial_spd = 0    
feed_spd = .5
ZERO_FRISBEE = .5
ONE_FRISBEE = 1
TWO_FRISBEE = 1.5
THREE_FRISBEE = 2.0 
FOUR_FRISBEE = 2.5

FrisbeeCount = "Frisbee Count"

class Shooter():

    def __init__(self, feed_motor, frisbee_sensor, feed_sensor):
        self.feed_motor.Set(initial_spd)
        self.update = none
        
    def Feed():
        "'makes the feed motor go 1 full rotation then stops'"
        self.state = 1
        if feed_sensor.Get() >= 0 and state = 1:
            self.feed_motor.Set(feed_spd)        
            state = 2
        if feed_sensor.Get() >= 1000 and state = 2:
            self.feed_motor.Set(initial_spd)
            
    def GetFrisbeeCount():
        "'Gets the distance away an object is from the sensor based on the voltage of the sensor'"
        if self.frisbee_sensor.GetVoltage() = ZERO_FRISBEE:
            frisbee_count = 0
            
        if self.frisbee_sensor.GetVoltage() = ONE_FRISBEE:
            frisbee_count = 1
            
        if self.frisbee_sensor.GetVoltage() = TWO_FRISBEE:
            frisbee_count = 2
            
        if self.frisbee_sensor.GetVoltage() = THREE_FRISBEE:
            frisbee_count = 3
            
        if self.frisbee_sensor.GetVoltage() = FOUR_FRISBEE:
            frisbee_count = 4
            
        SmartDashboard.PutDouble(FrisbeeCount, frisbee_count)
"'Alternate frisbee counter: if the top sensor is recieving a value then their are 4 frisbees, if the 2nd sensor is receving a value and the top isn't then there are three frisbees, if all frisbees are recoving no value then there are zero frisbees then there are 0 frisbees'"