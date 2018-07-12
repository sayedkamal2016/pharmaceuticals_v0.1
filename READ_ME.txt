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

For a whole description of this plugin, please refer to the technical
documentation provided in the documentation folder.

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
