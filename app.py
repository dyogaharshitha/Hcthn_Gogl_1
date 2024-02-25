import streamlit as st
import uiprcss 
import plnr

def main():
    st.title("Meal planner App")

    dflt =  st.empty()
    
    # Define a number input widget
    age = st.number_input("Enter age:", min_value=0, max_value=100, value=25)
    options = [('Breakfast', 'breakfast'), ('Lunch', 'lunch'), ('Dinner', 'dinner'),
               ('Snacks', 'snaks'), ('for whole day', 'wholeday') ]
    # Create a dropdown menu
    mel_typ = st.selectbox(
    'Select an option',options, format_func=lambda option: option[0]  )
    preg=False ; months = 3
    if st.toggle('Pregnant'):
        preg = True ; months = st.number_input("Enter months:", min_value=0, max_value=9, value=5) 
    act_opt = [('Low', 'low'), ('Moderate', 'med'), ('High', 'high') ]
    act = st.selectbox( 'Select an option',act_opt, format_func=lambda option: option[0]  )

    spec = {'age':age , 'act':act, 'meal':mel_typ, 'preg':preg, 'months':months}

    cstm  = st.empty()
    if st.checkbox('gat custom plan'):
        spec['cal'] = st.number_input("Enter required calories : ")
        spec['carb'] = st.number_input("Enter required cabohydrates in g: ")
        spec['prot'] = st.number_input("Enter required proteins in g : ")
        spec['fat'] = st.number_input("Enter required fats in g: ")

    # Define a submit button
    submit_button = st.button("Submit")
    
    # Check if the submit button is pressed
    if submit_button:
        inp_spc = uiprcss.inp_spec_indx(spec) 
        plnnr = plnr.meal_planner(inp_spc)
        dsh , wgt = plnnr.get_meal_plan()

        # Display the output
        #st.write("Meal plan :", dsh , wgt)
        dsh = dsh.drop_duplicates()
        st.write("Meal plan :", dsh.values)

if __name__ == "__main__":
    main()
