# https://github.com/WaveShapePlay/Arduino_RealTimePlot
# Modified to plot six variables from Arduino in two subplots
# Data format expected from Arduino: "value1,value2,value3,value4,value5,value6" (comma-separated values)

import time
import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def animate(i, dataLists, ser):
    ser.write(b'g')                                     # Transmit the char 'g' to receive the Arduino data point
    arduinoData_string = ser.readline().decode('ascii').strip() # Decode and remove whitespace
    #print(arduinoData_string)                          # Debug print

    try:
        # Split the incoming data into six values
        data_values = [float(x) for x in arduinoData_string.split(',')]
        
        # Append each value to its respective list
        for idx, value in enumerate(data_values):
            dataLists[idx].append(value)
            dataLists[idx] = dataLists[idx][-50:]       # Keep last 50 points for each variable

    except:                                             # Pass if data point is bad                               
        pass
    
    # Clear both subplots
    ax1.clear()                                         
    ax2.clear()                                         
    
    # Plot first three variables in first subplot
    ax1.plot(dataLists[0], 'r-', label='Accel_x')
    ax1.plot(dataLists[1], 'g-', label='Accel_y')
    ax1.plot(dataLists[2], 'b-', label='Accel_z')
    
    # Plot next three variables in second subplot
    ax2.plot(dataLists[3], 'c-', label='Gyro_x')
    ax2.plot(dataLists[4], 'm-', label='Gyro_y')
    ax2.plot(dataLists[5], 'y-', label='Gyro_z')
    
    # Configure first subplot
    ax1.set_ylim([-5, 5])   # Acceleration range of Nano 33 Iot is set at -4|4 g                              
    ax1.set_title("Arduino Data - Acceleration")             
    ax1.set_ylabel("Acceleration [g]")                             
    ax1.legend()                                        

    # Configure second subplot
    ax2.set_ylim([-2500, 2500])   # Gyroscope range of Nano 33 Iot is set at -2000|2000 dps                              
    ax2.set_title("Arduino Data - Gyroscope")             
    ax2.set_ylabel("Angular Velocity [dps]")                             
    ax2.legend()                                        

# Initialize six empty lists for the six variables
dataLists = [[], [], [], [], [], []]

fig = plt.figure(figsize=(12, 5))                       # Create wider figure for side-by-side plots
ax1 = fig.add_subplot(121)                              # Add first subplot (left side)
ax2 = fig.add_subplot(122)                              # Add second subplot (right side)

ser = serial.Serial("COM3", 9600)                       # Establish Serial object with COM port and BAUD rate to match Arduino Port/rate
time.sleep(2)                                           # Time delay for Arduino Serial initialization 

                                                        # Matplotlib Animation Fuction that takes takes care of real time plot.
                                                        # Note that 'fargs' parameter is where we pass in our dataLists and Serial object. 
ani = animation.FuncAnimation(fig, animate, frames=100, fargs=(dataLists, ser), interval=100) 

plt.tight_layout(pad=3.0)                               # Increase padding between subplots
plt.show()                                              
ser.close()                                             
