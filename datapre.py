import pandas as pd
import numpy as np
import tensorflow as tf 
from sklearn.preprocessing import StandardScaler 

class init_data(): 
    def __init__(self):
        self.usda_food_clip_nrm, self.usda_food_clip, self.nrm, self.indx = self.food_db() 
        self.inp_spec, self.inp_spec_nrm, self.inp_scaler,self.inp_spec_df  = self.prep_inp_spec()

    def food_db(self):
        usda_food = pd.read_csv(r'data/usda_sr_all_foods.csv')

        usda_food = usda_food.fillna(0)
        usda_food_indx = usda_food['name']
        usda_food["Cereals"] = usda_food["Food Group"].apply(lambda x: 0.7 if x=="Baked Foods" else 1 if x=="Breakfast Cereals" else 1 if x=="Grains and Pasta" else 0.5 if x=="Baby Foods" else 0)
        usda_food["Fruits"] = usda_food["Food Group"].apply(lambda x: 0.7 if x=="Fruits" else 0 )
        usda_food["Vegetables"] = usda_food["Food Group"].apply(lambda x: 0.7 if x=="Vegetables" else 0 )
        usda_food["nuts"] = usda_food["Food Group"].apply(lambda x: 0.7 if x=="Nuts and Seeds" else 0.3 if x=="Baby Foods" else 0)
        usda_food["pulses"] = usda_food["Food Group"].apply(lambda x: 0.7 if x=="Beans and Lentils" else 0.3 if x=="Baby Foods" else 0 )
        usda_food["dairy"] = usda_food["Food Group"].apply(lambda x: 0.7 if x=="Dairy and Egg Products" else 0 )
        usda_food["non-veg"] = usda_food["Food Group"].apply(lambda x: 1 if x=="Meats" else 1 if x=="Fish" else 0 )
        usda_food["processd"] = usda_food["Food Group"].apply(lambda x: 1 if x=="Beverages" else 1 if x=="Fast Foods" else 1 if x=="Soups and Sauces" else 0 )
        usda_food.drop(columns=["Food Group","name","ID","200 Calorie Weight (g)","PRAL score"], inplace= True)
        usda_cols = usda_food.columns.to_list()
        usda_cols = ["Cereals","Vegetables","nuts","pulses","dairy","non-veg","processd"]+usda_cols[:-8] 
        usda_food = usda_food[usda_cols]
        # clipping the values to 1000 and ignoring anything beyond
        clp_val = 1000
        usda_food_clip = usda_food.clip(upper=clp_val)
        nrm = tf.keras.layers.Normalization(axis=-1)
        nrm.adapt(usda_food_clip)
        usda_food_clip_nrm = nrm(usda_food_clip)
        return usda_food_clip_nrm , usda_food_clip , nrm , usda_food_indx
    
    def prep_inp_spec(self):
        
        inp_spec = pd.read_csv("data/nutri_req_cntrls.csv")
        inp_spec = inp_spec.fillna(0)

        inp_spec  = inp_spec.iloc[:27,:]
        inp_spec_df = inp_spec.set_index('Unnamed: 0')
        inp_scaler = StandardScaler()
        # Normalize the data
        inp_spec_nrm = inp_scaler.fit(inp_spec.values[:,2:])
        return inp_spec, inp_spec_nrm, inp_scaler, inp_spec_df 
    
    def get_inp_spec(self, spc, frm_tbl=True) :
        if frm_tbl == False and spc == None :
            return "spec not provided" 
        
        if frm_tbl == True : 
            age = spc['age'] ; mel_typ = spc['meal'] 
            inp_spc = self.inp_spec_df.loc[age,:]
            mel =  self.inp_spec_df.loc[mel_typ,:]
            inp_spc = inp_spc * mel ;
            if frm_tbl == False :
                inp_spc['Calories'] = spc['cal']
                inp_spc['Carbohydrate (g)'] = spc['carb']
                inp_spc['Protein (g)'] = spc['prot']
                inp_spc['Fat (g)'] = spc['fat']
            inp_spc_values = np.reshape(inp_spc.values, (-1,101))
            wgt = inp_spc_values[:,0]
            inp_spc_nrm = self.inp_scaler.transform( inp_spc_values[:,1:] )
            inp_spc_nrm = np.reshape(inp_spc_nrm[:,:25], (-1,1,25))

            return inp_spc_nrm, wgt
            
    def prep_kys_dtst(self, dflt=True, rnd_seed=4):
        df = pd.read_csv("data/food_clstr.csv")#food_clstr = pd.read_csv("data/food_clstr.csv")
        #df = self.usda_food_clip_nrm
        #df['cluster'] = food_clstr.values
        grouped = df.groupby('cluster') 

        # Define the fixed number of rows for each sub-dataframe
        num_dfs = 10 ; fixed_rows_per_df = 300

        # Initialize an empty list to store sub-dataframes
        sub_dfs = [0] #[pd.DataFrame(columns=df.columns) for _ in range(num_dfs)]
        grp_sz = df.groupby('cluster').size()
        grps  = {index: value for index, value in enumerate(grp_sz)}

        # Iterate over the number of sub-dataframes to create
        for i in range(num_dfs): 
            if i < rnd_seed:
                continue

            group_to_drop = [key for key, value in grps.items() if value <= i+1]
            if group_to_drop != [] :
                grouped = df[~df['cluster'].isin(group_to_drop)]
                df = grouped
                grouped = grouped.groupby('cluster')
                grps = {key: value for key, value in grps.items() if key not in group_to_drop}

            sub_dfs[0] = grouped.apply(lambda x: x.iloc[i])
            rows_to_append = fixed_rows_per_df - len(grps)
            if rows_to_append != 0 :
                rows = df.sample(n=rows_to_append)
                sub_dfs[0] = pd.concat([sub_dfs[0], rows] , axis=0 )
            sub_dfs[0].drop(columns = ['cluster'],inplace=True)
            # sub_dfs[0] = sub_dfs[0].values
            break
        
        #indx_df = df.isin(sub_dfs[0].values).all(axis=1)

        # Get the indices of the matching rows
        #kys_indx = df.index[indx_df].tolist() ;
        kys_indcs = sub_dfs[0]['Unnamed: 0'] ; # print(kys_indcs)
        sub_dfs[0].drop(columns=['Unnamed: 0'],inplace=True)
        sub_dfs[0] = sub_dfs[0].values ;
        sub_dfs = np.array(sub_dfs)
        return sub_dfs , kys_indcs


