# ftir-background-subtract

README FOR FTIR BACKGROUND SUBTRACT TOOL 
Copyright Nial Peters & Kayla Iacovino, 2014

Version 1.1.0
Released September 30, 2014
Contact: kiacovino@usgs.gov

RUNNING THE SCRIPT: 
Make sure you have the correct dependencies 
installed before running the script: 
Python 
wx
matplotlib 
pylab 
numpy

Navigate to the directory where bkgd_subtract.py is located. Type
"python bkgd_subtract.py" into a terminal. If you have all the
dependencies installed properly, it should run the program.


USING THE PROGRAM: 
Chose your file in the file chooser window. Your
spectrum file should be two columns with wavenumber and absorbances (see
the example file test-spectrum.CSV).

Use the red and green sliders to set the boundaries over which a
polynomial will be fit to your spectrum. Everything within the green
sliders will be included in the fit. Everything within the red sliders
will be excluded from the fit. The standard approach is to place the red
sliders just outside of the peak of interest and set the green sliders
to include as much background as possible corresponding to that peak.
Once you have chosen your slider positions, click "Apply". Clicking
apply will first find the limits set by your sliders and then calculate
a background polynomial. The polynomial will then be shown in the second
plot (blue points are points used in the fitting; red points are those
that could not be fit and were excluded from the fitting). The
background-subtracted portion of your spectrum will be shown in the
bottom plot. Hover your mouse over the peak to get the y-value.

The four buttons labelled "3500", "CO3", "4500", "5200", and "CO3 (2)"
will suggest placement of the sliders for various parts of the spectrum.
If using the suggested limits, do not click "Apply", which will read the
positions of the limits shown by the sliders. Instead use "Apply
suggested", which instead applies the values in the text boxes.

The "Get Limits" button will find the values of the sliders and put them
into the limit text boxes. Limits can also be typed in manually. You do
not need to click "Get Limits" before clicking "Apply".

The Fit Order is the order of the polynomial. We suggest using fit
orders from 1-5.


THE PLOTS:
There are three plots shown: (1) Your data [top]; (2) The fit to your data [center]; (3) The background-corrected data [lower].

The top plot contains the data loaded from your CSV file and should never be blank. Upon opening the program, the central and lower plots will be blank. Once a background is drawn, the central and lower plots will be populated.


A NOTE FOR MAC USERS:
For some reason, the standard matplotlib toolbar (containing such useful features as zoom, pan, save image) does not appear on Mac. You can use standard marplotlib keyboard shortcuts to get around this: 

Home/Reset					        	h or r
Back						            	c or left arrow or backspace
Forward						          	v or right arrow
Pan/Zoom					          	p
Zoom-to-rectangle			        o
Save						    	        s
Toggle fullscreen			        f
Constrain pan/zoom to x axis	hold x
Constrain pan/zoom to y axis	hold y
Preserve aspect ratio			    hold CONTROL
Toggle grid						        g
Toggle y axis scale (log/lin)	l


