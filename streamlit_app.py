# Import python packages
import streamlit as st
import os
import requests  
import pandas as pd
from snowflake.snowpark.functions import col
# from snowflake.snowpark.context import get_active_session -- remove line for SniS

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw: :pray:")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)


# after defining active session... remove the select box 
# Create a select Box
#option = st.selectbox(
#    "What is your favorite fruit?",
#    ("Banana", "Strawberries", "Peaches"),
#)
#st.write("Your favorite fruit is:", option)

# add name box for orders
name_on_order = st.text_input("Name on Smoothie:", "")
st.write("The name on your Smoothie will be:", name_on_order)

cnx = st.connection("snowflake")
#cnx = st.connection("",
#    type="snowflake",
#    account="JDIMKAV-NZB70666",
#    user="chestercar",
#    password="nickelv@n735SF")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"),col("SEARCH_ON"))
#st.dataframe(data=my_dataframe, use_container_width=True) #to check content of the dataframe
#st.stop() # to stop the code up to this point only, good for checking code

# create a version of my_dataframe but call it pd_df
pd_df =  my_dataframe.to_pandas()
#st.dataframe(pd_df) # to check pandas dataframe
#st.stop()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    max_selections=5
    )

if ingredients_list:
#    st.write("You selected:", ingredients_list)
#    st.text(ingredients_list)

    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # add "Search On" code, link to learn more on loc and iloc funcitons (https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html)
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
      
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)  
        st_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True) # Put the JSON into a Dataframe


    #st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
                    values ('""" + ingredients_string + """','""" + name_on_order + """')"""
                    
    #st.write(my_insert_stmt)
    #st.stop()
    time_to_insert=st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered, '+name_on_order+'!', icon="✅")
