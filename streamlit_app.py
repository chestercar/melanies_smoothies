# Import python packages
import streamlit as st
import os
import requests  
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
my_dataframe = session.table("smoothies.public.fruit_options").select("FRUIT_NAME","SEARCH_ON")
#st.dataframe(data=my_dataframe, use_container_width=True)

# Collect rows into Python objects
rows = my_dataframe.collect()  # returns list of Row objects

# Build mapping from display → use
options_map = {row["FRUIT_NAME"]: row["SEARCH_ON"] for row in rows}

selected_display = st.multiselect(
    "Choose up to 5 ingredients:",
    options=list(options_map.keys()),
    max_selections=5
    )

# Map display values to use values
ingredients_list = [options_map[d] for d in selected_display]

if ingredients_list:
#    st.write("You selected:", ingredients_list)
#    st.text(ingredients_list)

    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
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

