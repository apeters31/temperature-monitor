import os
import datetime
import csv
import json
import oneWire
import temperatureSensor
import ubidots
import oledHelper
# import config
dirName = os.path.dirname(os.path.abspath(__file__))
# read the config file relative to the script location
with open( '/'.join([dirName, 'config.json']) ) as f:
    config = json.load(f)

FILE_PATH = '/tmp/run/mountd/sda1'
#FILE_PATH = '/tmp/run/temperature-test'
token = config["token"]
deviceName = config["deviceName"]
oneWireGpio = 19

def __main__():
    # initialize oled
    oledHelper.init(dirName)
    
    device = ubidots.UbidotsDevice(token, deviceName)

    if not oneWire.setupOneWire(str(oneWireGpio)):
        print "Kernel module could not be inserted. Please reboot and try again."
        return -1

    # get the address of the temperature sensor
    # 	it should be the only device connected in this experiment    
    sensorAddresses = oneWire.scanAddresses()

     # See https://ubidots.com/docs/hw/ for data point specs                                                                                           
    dataPoint = {                                                                                                                                     
        'timestamp': int(float(datetime.datetime.today().strftime('%s.%f'))*1000.0)                                                                   
    }                                                                                                                                                 
    i = 1                                                                                                                                             
    for sensorAddress in sensorAddresses:                                                                                                             
        sensor = temperatureSensor.TemperatureSensor("oneWire", { "address": sensorAddress, "gpio": oneWireGpio })                                    
        if not sensor.ready:                                                                                                                          
            print "Sensor was not set up correctly. Please make sure that your sensor is firmly connected to the GPIO specified above and try again." 
            return -1                                                                                                                                 
                                                                                                                                                      
        temperature = sensor.readValue()                                                                                                              
        dataPoint[('temperature-%s' % sensorAddress)] = temperature                                                                                   
        # oledHelper.writeMeasurements(sensorAddress, temperature, i + 1)                                                                             
        i = i + 1   
    
    # instantiate the temperature sensor object
    # sensor = temperatureSensor.TemperatureSensor("oneWire", { "address": sensorAddress, "gpio": oneWireGpio })
    # if not sensor.ready:
    #     print "Sensor was not set up correctly. Please make sure that your sensor is firmly connected to the GPIO specified above and try again."
    #     return -    # check and print the temperature
    # temperature = sensor.readValue()
    # dataPoint = {
    #     "temperature": temperature
    # }
    ubidots_data_point = dataPoint.copy()              
    ubidots_data_point.pop('timestamp', None)
    device.pushDataPoint(dataPoint)
    
    # Write data to USB key if attac                                                                                                                  
    keys = dataPoint.keys()                                                                                                                           
    if os.path.isdir(FILE_PATH):                                                                                                                      
        new_file = False                                                                                                                              
        if not os.path.isfile('%s/temperature-data.json' % FILE_PATH):                                                                                
            new_file = True                                                                                                                           
                                                                                                                                                      
        # Create the file if it does not exist so that we can open it with r+                                                                         
        if new_file:                                                                                                                                  
            with open('%s/temperature-data.json' % FILE_PATH, 'w+') as f:                                                                             
                f.write('')                                                                                                                           
                                                                                                                                                      
        with open('%s/temperature-data.json' % FILE_PATH, 'r+') as f:                                                                                 
            if new_file:                                                                                                                              
                f.write('[')                                                                                                                          
                                                                                                                                                      
            else:                                                                                                                                     
                f.read()                                                                                                                              
                f.seek(-1, os.SEEK_END)                                                                                                               
                f.write(',\n')                                                                                                                        
            f.write(json.dumps(dataPoint, indent = 2))                                                                                                
            f.write(']')                                                                                                                              
        with open('%s/temperature-data.csv' % FILE_PATH, 'a+') as f:                                                                                  
            dict_writer = csv.DictWriter(f, keys)                                                                                                     
            dict_writer.writerows([dataPoint])
    
    # write to oled screen
    oledHelper.writeMeasurements(temperature)

if __name__ == '__main__':
    __main__()
