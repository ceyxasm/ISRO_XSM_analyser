import os
from flask import Flask,flash,request,redirect,url_for
import matplotlib.pyplot as plt
import numpy as np
from astropy.visualization import astropy_mpl_style
from astropy.utils.data import get_pkg_data_filename
from astropy.io import fits
from astropy.visualization import astropy_mpl_style
plt.style.use(astropy_mpl_style)

app = Flask(__name__)

UPLOAD_FOLDER="./uploads"
ALLOWED_EXTENSIONS={"lc","fits","xls"}
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('show_lc', name=filename))
            #return "file saved"
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''
@app.route('/show_lc/<name>',methods=['GET','POST'])
def show_lc(name):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('show_lc', name=filename))
    image_file = fits.open('./uploads/'+name)
    image_data = fits.getdata('./uploads/'+name)
    img_data=image_file[1].data
    
    x=img_data['TIME']
    y=img_data['RATE']

    return '''<head>
	<!-- Load plotly.js into the DOM -->
	<script src='https://cdn.plot.ly/plotly-2.9.0.min.js'></script>
</head>

<body>
	<div id='myDiv'><!-- Plotly chart will be drawn inside this DIV --></div>
        <script>
        var trace1 = {
  x: '''+str(img_data['TIME'].tolist())+''',
  y: '''+str(img_data['RATE'].tolist())+''',
  type: 'scatter'
};
        var layout={
            shapes:[
            {
            type:'rect';
            xref:'x';
            yref:'paper';
            x0:tstart;
            y0:0;
            x1:tstop;
            y1:1;
            fillcolor:'#d3d3d3';
            opacity:0.2;
            line:{
                width:0;
                };
                }]
            }


console.log(trace1);
var data = [trace1];

Plotly.newPlot('myDiv', data);

        </script>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
</body>'''
    #return "Sex sux mach gye"

if __name__ == "__main__":
    app.run()
