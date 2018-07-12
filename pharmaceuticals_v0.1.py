"""
/***************************************************************************
 pharmaceuticals

 This plugin allows to simulate pharmaceuticals' concentration at the outlet
 of a stream, based on the measured concentration at the inlet and on the travel
 time of the sample collected at the inlet.
 The concentration at the outlet is simulated as:
 C_oulet = C_inlet * exp[-(k*t)],
 where: C_inlet is the measured pharmaceutical's concentration at the inlet
        k is the degradation rate coefficient for pharmaceutical (1/s)
        t is the time instant (s) when the sample collected at the inlet reaches
        the outlet (assuming that the measurement time istant is t=0)

Input needed -> a csv file with (at least) the following fields:
                - sample ID (arbitrary format)
                - measured pharmaceutical's concentration at the inlet
                  (arbitrary units of measurements)
                - date and time of measurement (YYYY-mm-dd hh:mm:ss)
                - average stream velocity (m/s)

Expected output -> a plot of the measured (and simulated) pharmaceutical's
                   concentration vs time of measurement (and time of arrival
                   of the collected sample at the outlet)

Installation requirements -> you need the pandas and matplotlib libraries
                             for plotting. To install them, run the OSGEO4W
                             Shell AS ADMINISTRATOR and run:
                             python -m pip install pandas
                             python -m pip install matplotlib

How to run the script -> run the batch file run_pharmaceuticals_v0.1.bat

                              -------------------
        begin                : 2018-06-25
        version              : 0.1
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Giovanna De Filippis
                               (Scuola Superiore Sant'Anna, Pisa, Italy)
        email                : g.defilippis@santannapisa.it
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

#Importing the sys module to interact with the operating system
import sys

#Importing the csv module to manage csv files
import csv

#Importing the pandas module to plot results
import pandas

from PyQt5 import uic
from PyQt5 import QtWidgets
#Importing all the methods of the QFileDialog and QMessageBox classes
from PyQt5.QtWidgets import QFileDialog, QMessageBox

#Importing the datetime module to manage date and time
import datetime
#Importing all the methods of the datetime and timedelta classes
from datetime import datetime, timedelta

#Importing all the methods of the exp class
from math import exp

#Importing all the methods of the pyplot class for plotting (the following lines
#are necessary in order not to have an error like: No module named 'tkinter' and
#in order to make the pyplot.show() command works)
import matplotlib
matplotlib.rcParams['backend'] = "Qt4Agg"
from matplotlib import pyplot

#Importing all the methods of the dates class to manage time along the x axis
from matplotlib import dates

class MyWindow(QtWidgets.QDialog):
    def __init__(self):

        #Showing the Dialog window (content of the pharmaceuticals_v0.1.ui file designed with QtDesigner)#
        super(MyWindow, self).__init__()
        uic.loadUi('pharmaceuticals_v0.1.ui', self)
        self.show()

        #When clicking the browse_button button, recall the method loadReadcsv
        self.browse_button.clicked.connect(self.loadReadcsv)

        #When clicking the run_button button, recall the method run
        self.run_button.clicked.connect(self.run)

    #The loadReadcsv method allows to look for the input csv file of pharmaceuticals' concentrations
    #and to retrieve the fields of date and time, measured pharmaceuticals' concentration at the inlet
    #and measured pharmaceuticals' concentration at the outlet
    def loadReadcsv(self):

        #getOpenFileName is a method of the QFileDialog class which allows to open a dialog window with
        #the heading "Select input csv file".
        #The argument "" makes this dialog window to open always at the same path, while '*.csv' allows
        #to filter csv files.
        #The getOpenFileName method returns the csv file inputfile and res, which allows to check if
        #I clicked Open or not
        #I use self.inputfile (and not just inputfile) because I will need this variable in the
        #retrieve*Data functions below
        self.inputfile,res=QFileDialog.getOpenFileName(self,"Select input csv file", "", '*.csv')

        #If I clicked Open (i.e., if res is True), then it does nothing, otherwise it prints an error message
        if res:
            pass
        else:
            print("You didn't select any csv file!")

        #The path_bar fills with the whole path of the selected csv file
        #(setText is a method of the QLabel class which holds the label's text)
        self.path_bar.setText(self.inputfile)

        #Opening the csv input file just selected
        with open(self.inputfile) as inputfile:

            #DictReader is a class of the csv method which reads a csv file and
            #returns a dictionary whose keys are given by the headers of the fields
            csvReader=csv.DictReader(inputfile,delimiter=';')

            #Iterating over the rows of the inputfile (each row becomes
            #a dictionary, where the keys are the headers of the fields)
            for row in csvReader:
                dictionary=dict(row)
                #Extractiong the headers of each field in the csv input file
                #(each header is a key of the dictionary)
                headers=list(dictionary.keys())
                #Inserting the string 'Select a field...' at the beginning of
                #the list headers
                headers.insert(0,'Select a field...')

            #Filling the combo boxes ID_field, time_field, conc_inlet and v_field
            #of the Dialog with headers of the csv input file (addItems is a method
            #of the QComboBox class which provides a list of options in a combo box)
            self.ID_field.addItems(headers)
            self.time_field.addItems(headers)
            self.conc_inlet.addItems(headers)
            self.v_field.addItems(headers)

            #Once the text in the ID_field combo box is changed,
            #recall the retrieveIdData function
            self.ID_field.currentIndexChanged.connect(self.retrieveIdData)
            #Once the text in the time_field combo box is changed,
            #recall the retrieveTimeData function
            self.time_field.currentIndexChanged.connect(self.retrieveTimeData)
            #Once the text in the conc_inlet combo box is changed,
            #recall the retrieveTimeData function
            self.conc_inlet.currentIndexChanged.connect(self.retrieveCinletData)
            #Once the text in the v_field combo box is changed,
            #recall the retrieveVelocityData function
            self.v_field.currentIndexChanged.connect(self.retrieveVelocityData)

    #The retrieveTimeData method allows to retrieve the values of samples IDs
    #and to store such values in a list sample_id
    def retrieveIdData(self):

        #Opening the csv input file
        with open(self.inputfile) as inputfile:

            #DictReader is a class of the csv method which reads a csv file and
            #returns a dictionary whose keys are given by the header of the fields
            csvReader=csv.DictReader(inputfile,delimiter=';')

            #The following list will contain values of the sample ID field of
            #the csv input file.
            #I use self.sample_id (and not just sample_id) because I will
            #need this variable in the run function below
            self.sample_id=[]

            #Reading the content of the combo box ID_field of the Dialog.
            #This content will be assigned to the variable id_field, which will
            #be a string (currentText is a method of the QComboBox class which
            #holds the text displayed in a combo box)
            id_field=self.ID_field.currentText()

            #Checking the content of the combo box ID_field of the Dialog
            if id_field=='Select a field...':
                print('Select a field for Sample ID')

            #Iterating over the rows of the inputfile (each row becomes
            #a dictionary, where the keys are the headers of the fields)
            for row in csvReader:
                dictionary=dict(row)
                #Extractiong the headers of each field in the csv input file
                #(each header is a key of the dictionary)
                headers=list(dictionary.keys())
                #Iterating over the headers list
                for field_name in headers:
                    #Filling the date_time list with values of date and time
                    #found in each row of the csv input file
                    if field_name==id_field:
                        self.sample_id.append(dictionary[field_name])

    #The retrieveTimeData method allows to retrieve the values of date and time of samples
    #and to store such values in a list date_time
    def retrieveTimeData(self):

        #Opening the csv input file
        with open(self.inputfile) as inputfile:

            #DictReader is a class of the csv method which reads a csv file and
            #returns a dictionary whose keys are given by the header of the fields
            csvReader=csv.DictReader(inputfile,delimiter=';')

            #The following list will contain values of the time field of
            #the csv input file.
            #I use self.date_time (and not just date_time) because I will
            #need this variable in the run function below
            self.date_time=[]

            #Reading the content of the combo box time_field of the Dialog.
            #This content will be assigned to the variable t_field, which will
            #be a string (currentText is a method of the QComboBox class which
            #holds the text displayed in a combo box)
            t_field=self.time_field.currentText()

            #Checking the content of the combo box time_field of the Dialog
            if t_field=='Select a field...':
                print('Select a field for Measurement time')

            #Iterating over the rows of the inputfile (each row becomes
            #a dictionary, where the keys are the headers of the fields)
            for row in csvReader:
                dictionary=dict(row)
                #Extractiong the headers of each field in the csv input file
                #(each header is a key of the dictionary)
                headers=list(dictionary.keys())
                #Iterating over the headers list
                for field_name in headers:
                    #Filling the date_time list with values of date and time
                    #found in each row of the csv input file
                    if field_name==t_field:
                        self.date_time.append(dictionary[field_name])

    #The retrieveCinletData method allows to retrieve the values of pharmaceuticals' concentrations
    #at the inlet and to store such values in a list inlet_conc
    def retrieveCinletData(self):

        #Opening the csv input file
        with open(self.inputfile) as inputfile:

            #DictReader is a class of the csv method which reads a csv file and
            #returns a dictionary whose keys are given by the header of the fields
            csvReader=csv.DictReader(inputfile,delimiter=';')

            #The following list will contain values of the inlet concentration
            #field of the csv input file.
            #I use self.inlet_conc (and not just inlet_conc) because I will
            #need this variable in the run function below
            self.inlet_conc=[]

            #Reading the content of the combo box conc_inlet of the Dialog.
            #This content will be assigned to the variable cinlet_field, which will
            #be a string (currentText is a method of the QComboBox class which
            #holds the text displayed in a combo box)
            cinlet_field=self.conc_inlet.currentText()

            #Checking the content of the combo box conc_inlet of the Dialog
            if cinlet_field=='Select a field...':
                print('Select a field for Concentration measured at the inlet')

            #Iterating over the rows of the inputfile (each row becomes
            #a dictionary, where the keys are the headers of the fields)
            for row in csvReader:
                dictionary=dict(row)
                #Extractiong the headers of each field in the csv input file
                #(each header is a key of the dictionary)
                headers=list(dictionary.keys())
                #Iterating over the headers list
                for field_name in headers:
                    #Filling the inlet_conc list with values of concentration
                    #at the inlet found in each row of the csv input file
                    if field_name==cinlet_field:
                        self.inlet_conc.append(dictionary[field_name])

    #The retrieveVelocityData method allows to retrieve the values of stream velocities
    #at the inlet and to store such values in a list avg_velocity
    def retrieveVelocityData(self):

        #Opening the csv input file
        with open(self.inputfile) as inputfile:

            #DictReader is a class of the csv method which reads a csv file and
            #returns a dictionary whose keys are given by the header of the fields
            csvReader=csv.DictReader(inputfile,delimiter=';')

            #The following list will contain values of the stream velocity
            #field of the csv input file.
            #I use self.avg_velocity (and not just avg_velocity) because I will
            #need this variable in the run function below
            self.avg_velocity=[]

            #Reading the content of the combo box v_field of the Dialog.
            #This content will be assigned to the variable velocity_field, which will
            #be a string (currentText is a method of the QComboBox class which
            #holds the text displayed in a combo box)
            velocity_field=self.v_field.currentText()

            #Checking the content of the combo box v_field of the Dialog
            if velocity_field=='Select a field...':
                print('Select a field for Average velocity of the stream at the inlet')

            #Iterating over the rows of the inputfile (each row becomes
            #a dictionary, where the keys are the headers of the fields)
            for row in csvReader:
                dictionary=dict(row)
                #Extractiong the headers of each field in the csv input file
                #(each header is a key of the dictionary)
                headers=list(dictionary.keys())
                #Iterating over the headers list
                for field_name in headers:
                    #Filling the outlet_conc list with values of concentration
                    #at the outlet found in each row of the csv input file
                    if field_name==velocity_field:
                        self.avg_velocity.append(dictionary[field_name])

    #The run method allows to simulate pharmaceuticals' concentration at the outlet, based on the
    #measured concentration at the inlet and on the travel time of the sample collected at the inlet until the outlet
    def run(self):

        #Checking the content of the combo box ID_field of the Dialog
        if self.ID_field.currentText()=='Select a field...':
            #An error message appears.
            #(QMessageBox.question is a method of the QtWidgets class which
            #shows a message box asking for something missing).
            #The message box will have a unique button 'Ok'
            check1=QMessageBox.question(self,'Error!',"Select a field for Sample ID", QMessageBox.Ok)
            #When clicking 'Ok', nothing appens (the Dialog remains open)
            if check1==QMessageBox.Ok:
                pass

        #Checking the content of the combo box time_field of the Dialog
        if self.time_field.currentText()=='Select a field...':
            #An error message appears.
            #(QMessageBox.question is a method of the QtWidgets class which
            #shows a message box asking for something missing).
            #The message box will have a unique button 'Ok'
            check2=QMessageBox.question(self,'Error!',"Select a field for Measurement time", QMessageBox.Ok)
            #When clicking 'Ok', nothing appens (the Dialog remains open)
            if check2==QMessageBox.Ok:
                pass

        #Checking the content of the combo box conc_inlet of the Dialog
        if self.conc_inlet.currentText()=='Select a field...':
            #An error message appears.
            #(QMessageBox.question is a method of the QtWidgets class which
            #shows a message box asking for something missing).
            #The message box will have a unique button 'Ok'
            check3=QMessageBox.question(self,'Error!',"Select a field for Concentration measured at the inlet", QMessageBox.Ok)
            #When clicking 'Ok', nothing appens (the Dialog remains open)
            if check3==QMessageBox.Ok:
                pass

        #Checking the content of the combo box v_field of the Dialog
        if self.v_field.currentText()=='Select a field...':
            #An error message appears.
            #(QMessageBox.question is a method of the QtWidgets class which
            #shows a message box asking for something missing).
            #The message box will have a unique button 'Ok'
            check4=QMessageBox.question(self,'Error!',"Select a field for Average velocity of the stream at the inlet", QMessageBox.Ok)
            #When clicking 'Ok', nothing appens (the Dialog remains open)
            if check4==QMessageBox.Ok:
                pass

        #Reading the content of the distance line edit.
        #(text is a method of the QtWidgets class which
        #holds the content of a line edit)
        d=self.distance.text()

        #Calculating the time shift (when sample collected at the inlet reaches the outlet).
        #This depends on the average velocity of the stream measured at the inlet (list avg_velocity)
        #and on the distance covered (value input into the distance line edit, i.e., d variable)

        #time_shift is a list containing the calculus of
        #time shift for each sample at the inlet
        time_shift=[]
        #Iterating over the list avg_velocity
        for v in self.avg_velocity:
            #Updating the list time_shift (recall that d and the
            #elements of the list avg_velocity are strings!).
            #As d is expressed in m and v is expressed in m/s,
            #then time_shift values will be expressed in seconds
            time_shift.append(float(d)/float(v))
        #date_time_shifted is a new list containing times from the list date_time
        #shifted by the amounts contained in the list time_shift.
        date_time_shifted=[]
        #Iterating over the list date_time
        for t in self.date_time:
            #Updating the list date_time_shifted (strptime is a method of the
            #datetime class which allows to convert a string in a datetime object).
            #By now, date_time_shifted is nothing but a copy of date_time, but its
            #elements are not strings (as in date_time) but datetime objects
            date_time_shifted.append(datetime.strptime(t,'%Y-%m-%d %H:%M:%S'))
        #Iterating over the length of the list time_shift
        for i in range(len(time_shift)):
            #Updating the list date_time_shifted (timedelta is a method of the
            #datetime class which allows to add some time to the original list date_time).
            #After the shift of the original list date_time, elements of the list
            #date_time_shifted are converted into strings.
            #(Each element of the date_time_shifted list has a format like
            #2000-01-01 00:00:00.00000 (with milliseconds). The split method allows to cut
            #what is after the point, i.e., allows to cut milliseconds. This is necessary
            #for plotting results
            date_time_shifted[i]=str(date_time_shifted[i]+timedelta(seconds=time_shift[i])).split(".")[0]

        #Reading the content of the degradation line edit.
        #(text is a method of the QtWidgets class which
        #holds the content of a line edit)
        k=self.degradation.text()

        #sim_conc is the list of simulated pharmaceuticals' concentration at the outlet
        sim_conc=[]
        #Iterating over the length of the list inlet_conc
        for i in range(len(self.inlet_conc)):
            #Calculating the simulated concentration at the outlet as
            #C_oulet = C_inlet * exp[-(k*t)],
            #where: C_inlet is the measured pharmaceuticals' concentration at the outlet (list inlet_conc)
            #       k is the degradation rate coefficient for pharmaceutical (1/s)
            #       t is the time instant (s) when the sample collected at the inlet reaches the outlet
            #       (the stating time istant is t=0, so actually t is a DeltaT; list time_shift)
            sim_conc.append(float(self.inlet_conc[i])*exp(-(float(k)*time_shift[i])))

        #Plotting results

        #First plot: measured concentration vs times

        #The x axis will contain values from the list date_time transformed
        #in a datetime object
        x_axis1=[]
        #Iterating over the list date_time
        for t in self.date_time:
            #Updating the list x_axis (strptime is a method of the datetime
            #class which allows to convert a string in a datetime object).
            #By now, x_axis is nothing but a copy of date_time, but its
            #elements are not strings (as in date_time) but datetime objects
            x_axis1.append(datetime.strptime(t,'%Y-%m-%d %H:%M:%S'))
        #The y axis will contain values from the list inlet_conc
        #(ATTENTION: these values must be numbers NOT strings!)
        y_axis1=[]
        for y in self.inlet_conc:
            y_axis1.append(float(y))

        #Setting the x axis
        pyplot.gca().xaxis.set_major_formatter(dates.DateFormatter('%Y-%m-%d %H:%M:%S'))

        #Plotting line
        pyplot.plot(x_axis1,y_axis1,zorder=2)

        #Plotting also points (important: use the pyplot.plot first!)
        pyplot.scatter(x_axis1,y_axis1,zorder=1)

        #Title and axis labels
        pyplot.title(self.conc_inlet.currentText())
        pyplot.xlabel("Time")
        pyplot.ylabel(self.conc_inlet.currentText())

        #Showing the plot
        pyplot.gcf().autofmt_xdate()
        pyplot.show()

        #Second plot: simulated concentration vs times

        #The x axis will contain values from the list date_time_shifted transformed
        #in a datetime object
        x_axis2=[]
        #Iterating over the list date_time_shifted
        for t in date_time_shifted:
            #Updating the list x_axis (strptime is a method of the datetime
            #class which allows to convert a string in a datetime object).
            #By now, x_axis is nothing but a copy of date_time_shifted, but its
            #elements are not strings (as in date_time) but datetime objects
            x_axis2.append(datetime.strptime(t,'%Y-%m-%d %H:%M:%S'))
        #The y axis will contain values from the list sim_conc
        #(ATTENTION: these values must be numbers NOT strings!)
        y_axis2=[]
        for y in sim_conc:
            y_axis2.append(float(y))

        #Setting the x axis
        pyplot.gca().xaxis.set_major_formatter(dates.DateFormatter('%Y-%m-%d %H:%M:%S'))

        #Plotting line
        pyplot.plot(x_axis2,y_axis2,zorder=2)

        #Plotting also points (important: use the pyplot.plot first!)
        pyplot.scatter(x_axis2,y_axis2,zorder=1)

        #Title and axis labels
        pyplot.title(self.conc_inlet.currentText(),fontsize=32)
        pyplot.xlabel("Time")
        pyplot.ylabel(self.conc_inlet.currentText())

        #Showing the plot
        pyplot.gcf().autofmt_xdate()
        pyplot.show()

        #Plotting two plots together
        pyplot.plot(x_axis1, y_axis1, x_axis2, y_axis2, )

        #Setting labels to plot points
        labels=[]
        for id in self.sample_id:
            labels.append(id)
        for i, label in enumerate(labels):
            pyplot.annotate(label,(x_axis1[i],y_axis1[i]))
            pyplot.annotate(label+'_out',(x_axis2[i],y_axis2[i]))

        #Showing the legend
        pyplot.gca().legend(('Concentration measured at the inlet','Concentration simulated at the outlet'))

        #Showing the plot
        pyplot.show()

        #Closing the Dialog
        self.hide()

#This cycle works with the three top instructions in the __init__ method showing the Dialog window#
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    app.exec_()
