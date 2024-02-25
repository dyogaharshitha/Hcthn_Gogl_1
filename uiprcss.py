import pandas as pd
import numpy as np

def inp_spec_indx(spec, cstm=None):
    if spec['age'] < 18:
        indx = 'ag' 
        indx = indx + ('1-3' if spec['age']<4 else '4-6' if spec['age']<7 
                       else '7-9' if spec['age']<10 else '10-12' if spec['age']<13
                       else '13-15' if spec['age']<16 else '16-17')
    else :
        indx = 'adlt_' 
        indx = indx + ('lowact' if spec['act'][1]=='low' else 'medact' if spec['act'][1]=='med' else 'highact')
    if spec['preg'] == True: 
        indx = 'pregn_3-6' if spec['months'] < 6 else 'preg_6-9'
    if spec['meal'][1] == 'breakfast' or spec['meal'][1] == 'dinner':
        mel='brkfst_dnnr' 
    else : 
        mel = spec['meal'] [1]
    print(spec['meal'])
    if cstm!=None   :
        return dict( {'age':indx , 'meal':mel , 'cal':spec['cal'],
                      'carb':spec['carb'],'prot':spec['prot'],'fat':spec['fat'] } )
    return dict( {'age':indx , 'meal':mel} ) 





