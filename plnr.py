import pandas as pd
import numpy as np
import tensorflow as tf
import pickle
from sklearn.neighbors import KNeighborsClassifier
from datapre import init_data 

with open("my_model_4.pkl", "rb") as f:
    loaded_model_bytes = f.read()
 # Unpickle the model
#model = pickle.loads(loaded_model_bytes)


with open("model.json", "r") as json_file:
    loaded_model_json = json_file.read()
loaded_model = tf.keras.models.model_from_json(loaded_model_json)

# Load weights
loaded_model.load_weights("model_weights.h5")

dt_obj = init_data() ; 
dsh_indx = dt_obj.indx ; 

class meal_planner():
  def __init__(self, spc):
     self.input, self.wgt  = dt_obj.get_inp_spec(spc) 
     self.kys , self.kys_indx = dt_obj.prep_kys_dtst()
     self.dsh_indx =  dt_obj.indx  
     
  def predict(self,model,input,kys,nrm=None):
    
    # Use the loaded model for prediction
    #kys = nrm(kys_ref)
    prd = loaded_model.predict([input,kys])

    kys = tf.cast(kys, tf.float32)
    self.distances = tf.norm(tf.repeat(tf.expand_dims(kys,axis=1),4,axis=1) - tf.expand_dims(prd,axis=2), axis=-1)
    inds_alt = tf.argsort(self.distances,axis=-1) [:,:,:5]   # btch,4,1
    inds = inds_alt[:,:,0]
    #inds = tf.squeeze(inds,axis=-1)
    
    return inds 

  def get_meal_plan( self , atmpt=1 ):
    kys = self.kys ; dsh_indx= self.dsh_indx
    wgt = self.wgt ; input= self.input
    if atmpt == 1 : 
        self.inds = self.predict(loaded_model, input, kys)  ; print(self.inds)
        act_kys = tf.gather(self.kys_indx, self.inds)  ; act_kys = tf.reshape(act_kys, (-1))
        dshs = dsh_indx.iloc[act_kys]
        wgt = wgt * [0.1,0.2,0.3,0.4]
        return dshs, wgt

    else: 
       dst = self.distances[:,:,:5] 

       


