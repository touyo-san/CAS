# https://github.com/WaveShapePlay/Arduino_RealTimePlot
# Modified to plot three variables from Arduino in a single graph
# Data format expected from Arduino: "value1,value2,value3" (comma-separated values)

import time
import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def animate(i, dataLists, ser):
    ser.write(b'g')                                     # Transmit the char 'g' to receive the Arduino data point
    arduinoData_string = ser.readline().decode('ascii').strip() # Decode and remove whitespace
    #print(arduinoData_string)                          # Debug print

    try:
        # Split the incoming data into three values
        data_values = [float(x) for x in arduinoData_string.split(',')]
        
        # Append each value to its respective list
        for idx, value in enumerate(data_values):
            dataLists[idx].append(value)
            dataLists[idx] = dataLists[idx][-50:]       # Keep last 50 points for each variable

    except:                                             # Pass if data point is bad                               
        pass
    
    ax.clear()                                          # Clear last data frame
    
    # Plot all three variables with different colors and labels
    ax.plot(dataLists[0], 'r-', label='Variable 1')
    ax.plot(dataLists[1], 'g-', label='Variable 2')
    ax.plot(dataLists[2], 'b-', label='Variable 3')
    
    ax.set_ylim([0, 10])                               # Set Y axis limit of plot
    ax.set_title("Arduino Data")                        # Set title of figure
    ax.set_ylabel("Value")                              # Set title of y axis
    ax.legend()                                         # Show legend

# Initialize three empty lists for the three variables
dataLists = [[], [], []]

fig = plt.figure()                                      # Create Matplotlib plots fig is the 'higher level' plot window
ax = fig.add_subplot(111)                               # Add subplot to main fig window

ser = serial.Serial("COM3", 9600)                       # Establish Serial object with COM port and BAUD rate to match Arduino Port/rate
time.sleep(2)                                           # Time delay for Arduino Serial initialization 

                                                        # Matplotlib Animation Fuction that takes takes care of real time plot.
                                                        # Note that 'fargs' parameter is where we pass in our dataLists and Serial object. 
ani = animation.FuncAnimation(fig, animate, frames=100, fargs=(dataLists, ser), interval=100) 

plt.show()                                              # Keep Matplotlib plot persistent on screen until it is closed
ser.close()                                             # Close Serial connection when plot is closed
