from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse

from uploads.core.models import Document
from uploads.core.forms import DocumentForm

from math import *
import numpy as np
import csv
import sys
import xlsxwriter
from xlsxwriter.workbook import Workbook
from io import BytesIO
from io import StringIO

# for plotting
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64

# using plotly
import plotly.offline as opy
import plotly.graph_objs as go


##************VERSION**************##
#VERSION 1.1.0
#UPDATED NOVEMBER 2018
#MIT LICENSED

def readthedocs(request): #this allows the code to render the readthedocs.html file
    return render(request, 'core/readthedocs.html')

def home(request):
    documents = Document.objects.all()
    return render(request, 'core/home.html', { 'documents': documents })

# test adding second button
def second_button(request):
    if request.GET.get('second-button'):
        html_string = '<p>hello</p>'
        return render(request, 'core/home.html', {'html_string': html_string})
    return render(request, 'core/home.html')


def simple_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)

        # plot figure with mpl
        # wavenum, intensity = read_ftir_file(filename)
        # plt.plot(wavenum, intensity)
        # plt.gca().invert_xaxis()

        # buffer = BytesIO()
        # plt.savefig(buffer, format='png')
        # buffer.seek(0)
        # image_png = buffer.getvalue()
        # buffer.close()

        # graph = base64.b64encode(image_png)
        # graph = graph.decode('utf-8')

        # context = dict()
        # context['graph'] = graph #buffer.getvalue()

        # plot figure with plotly
        wavenum, intensity = read_ftir_file(filename)
        data = go.Data([go.Scatter(x=wavenum, y=intensity,
                                mode='lines', name='test',
                                opacity=0.8, marker_color='green')],
                      output_type='div')
        figure = go.Figure(data=data)
        figure.update_xaxes(autorange="reversed")
        graph = opy.plot(figure, auto_open=False, output_type='div')

        return render(request, "core/home.html", context={'graph': graph})

    return render(request, 'core/home.html')

def read_ftir_file(filename):
    reader = csv.reader(open('media/' + filename, "rt"))#, dialect="excel") 

    wavenumber = []
    absorbance = []

    for line in reader:
        wavenumber.append(float(line[0]))
        absorbance.append(float(line[1]))
    
    return np.array(wavenumber), np.array(absorbance)


def process_file(file_handle):
    
    # old code to export excel file from DensityX
    excel_file = BytesIO()

    xlwriter = pandas.ExcelWriter(excel_file, engine='xlsxwriter')

    output.to_excel(xlwriter, sheet_name='Density Data')
    original_user_data.to_excel(xlwriter, sheet_name='User Input')
    normed_user_data.to_excel(xlwriter, sheet_name='Normalized Data')
    #NOTE there is an option in the downloadable DensityX.py file (github) to switch on debugging, which writes all calculated values to excel file. This is not implemented in the online (Heroku) version.
    xlwriter.save()

    excel_file.seek(0)

    response = HttpResponse(excel_file.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = 'attachment; filename=DensityX-result.xlsx'

    return response
