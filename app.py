# _*_ coding: utf-8 _*_

from functools import wraps, update_wrapper
from flask import Flask, send_file, render_template, make_response, request, jsonify

from io import BytesIO, StringIO
import json
import requests
import matplotlib.pyplot as plt
import io
import random
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime
from realstatement_visualizing import Realstatement_visualizing

def nocache(view):
  @wraps(view)
  def no_cache(*args, **kwargs):
    response = make_response(view(*args, **kwargs))
    response.headers['Last-Modified'] = datetime.now()
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response
  return update_wrapper(no_cache, view)

app= Flask(__name__)
rv = Realstatement_visualizing()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chart',methods=["post"])
@nocache
def normal():
    file_name = rv.file_name_parser()
    return render_template("chart.html", width=800, height=600, file_name=file_name)



@app.route('/plot_png')
@nocache
def plot_png():
    plt = rv.triple_grap()
    img = BytesIO()
    plt.savefig(img, format='png', dpi=300)
    img.seek(0)  ## object를 읽었기 때문에 처음으로 돌아가줌
    return send_file(img, mimetype='image/png')
    #output = io.BytesIO()
    #FigureCanvas(plt).print_png(output)
    #return Response(output.getvalue(), mimetype='image/png')

# @app.route('/plot_png')
# @nocache
# def plot_png():
#     fig = Figure()
#     axis = fig.add_subplot(1, 1, 1)
#     xs = range(10000)
#     ys = [random.randint(1, 50) for x in xs]
#     axis.plot(xs, ys)
#     output = io.BytesIO()
#     FigureCanvas(fig).print_png(output)
#     return Response(output.getvalue(), mimetype='image/png')
#



if __name__ == '__main__':
    app.debug = True
    app.run()