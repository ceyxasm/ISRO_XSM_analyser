import os
import json
from flask import Flask,flash,request,redirect,url_for,render_template
import matplotlib.pyplot as plt
import numpy as np
from astropy.visualization import astropy_mpl_style
from astropy.utils.data import get_pkg_data_filename
from astropy.io import fits
from astropy.visualization import astropy_mpl_style
from webui import WebUI
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
    return render_template("upload_page.html")
def stable(signal):
  timer=0
  ts=0
  for i in range(len(signal)):
    if signal[i]!=0 and timer==0:
      ts=i
      timer=1
    if signal[i]==0 and timer==1:
      timer=0
      if i-ts<120:
        for j in range(ts, i+1):
          signal[j]=0

  return signal
def biner(signal):
  z=[]
  for i in signal:
    if i> 800 and i<= 5011:
      z.append(1000) #type B
    elif i>5011 and i<= 25000:
      z.append(5000) #type C
    elif i>25000 and i<= 250000:
      z.append(25000) #type M
    elif i>2500000:
      z.append(250000) #type X
    elif i<=800: z.append(0) #inconclusive, could be A
  return z
def extractor( signal, time):
  stable_signal= stable(biner(signal))
  t_start=[]
  i_start=[]

  start_flux=[]
  end_flux=[]
  
  t_stop=[]
  i_stop=[]

  peak_count=[]
  t_peak=[]
  i_peak=[]

  i_rise=[]
  t_rise=[]

  i_decay=[]
  t_decay=[]

  cat=[]
  timer=0
  for i in range(len(signal)):
    if stable_signal[i] >99 and timer==0:
      t_start.append(time[i])
      i_start.append(i)
      timer=1

    if stable_signal[i] <99 and timer==1:
      t_stop.append(time[i])
      i_stop.append(i)
      timer=0
      if t_start==[]:
        t_start.append(0)
        i_start.append(0)


  for i in range(len(t_start)):
    peak_count_val=0
    peak_instance=0
    for index in range(i_start[i], i_stop[i]):
      if peak_count_val< signal[index]:
        peak_count_val= signal[index]
        peak_instance= index

    peak_count.append( peak_count_val )
    t_peak.append( time[peak_instance])
    i_peak.append(peak_instance)

    bin_max= max(stable_signal[i_start[i]: i_stop[i]])
    if bin_max==1000: cat.append('B')
    elif bin_max==5000: cat.append('C')
    elif bin_max==25000: cat.append('M')
    elif bin_max==250000: cat.append('X')

  # for i in range(len(t_start)):
  #   up_thresh=  signal[i_peak[i]]/20
  #   down_thresh=  signal[i_peak[i]]/2
  #   start_flux.append(up_thresh)
  #   end_flux.append(down_thresh)

  for i in range(len(t_start)):
    start_t, end_t, start_i, end_i=t_peak[i], t_peak[i], i_peak[i], i_peak[i]
    while( signal[start_i]> peak_count[i]/20 and start_i>i_start[i]):
      start_i-=1
    while( signal[end_i]> peak_count[i]/2 and end_i<i_stop[i]):
      end_i+=1
    i_rise.append(start_i)
    i_decay.append(end_i)
    t_rise.append( time[start_i] )
    t_decay.append( time[end_i] )
  
  data={
      't_start': t_start,
      't_stop': t_stop,
      'category': cat,
      'peak count rate': peak_count,
      't_peak': t_peak,
      't_rise': t_rise,
      't_decay': t_decay,
      'i_start': i_start,
      'i_stop': i_stop,
      'i_peak': i_peak,
      'i_rise': i_peak,
      'i_decay': i_decay,
  }


  return data
@app.route('/uploads/<filename>', methods=['GET', 'POST'])
def download(filename):
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename=filename)

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
    
    x=img_data['TIME'].tolist()
    y=img_data['RATE'].tolist()
    params=extractor(y,x)
    json_dump=json.dumps(params)
    with open(name+".json", "w") as outfile:
        outfile.write(json_dump)
    print(params['t_start'])
    names=str(["Type C"])
    rise_period=(np.array(params['t_peak'])-np.array(params['t_rise'])).tolist()
    decay_period=(np.array(params['t_decay'])-np.array(params['t_peak'])).tolist()
    return render_template("analysis_page.html",x=x,y=y,names=names,tstart=params['t_start'],
            tstop=params['t_stop'],
            params=params,
            rise_period=rise_period,
            decay_period=decay_period,
            fname=name+".json")
ui=WebUI(app)
if __name__ == "__main__":
    ui.run()
