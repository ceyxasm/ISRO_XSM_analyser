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
      'peak instance': t_peak,
      'rise instance': t_rise,
      'decay instance': t_decay,
      'i_start': i_start,
      'i_stop': i_stop,
      'i_peak': i_peak,
      'i_rise': i_peak,
      'i_decay': i_decay,
  }


  return data

