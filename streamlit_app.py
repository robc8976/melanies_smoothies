# Import python packages
import streamlit as st

# add snowflake connector 07/11/25
import snowflake.connector
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


from snowflake.snowpark.functions import col

# add snowflake connector 07/11/25
private_key_str = st.secrets["snowflake"]["private_key"]
private_key_pp_str = st.secrets["snowflake"]["private_key_pp"].encode()
private_key = serialization.load_pem_private_key(
    private_key_str.encode(),
    #password=None,
    password=private_key_pp_str,
    backend=default_backend()
)
conn = snowflake.connector.connect(
    user=st.secrets["snowflake"]["user"],
    account=st.secrets["snowflake"]["account"],
    private_key=private_key,
    warehouse=st.secrets["snowflake"]["warehouse"],
    database=st.secrets["snowflake"]["database"],
    schema=st.secrets["snowflake"]["schema"],
    role=st.secrets["snowflake"]["role"]
)


# Write directly to the app
st.title(f":cup_with_straw::strawberry: Customize Your Smoothie!:banana::cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom Smoothie"""
)

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be: ', name_on_order)

#cnx = st.connection("snowflake")
#session = cnx.session()

#my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
cur = conn.cursor()
cur.execute("SELECT FRUIT_NAME FROM smoothies.public.fruit_options")
rows = cur.fetchall()
columns = [desc[0] for desc in cur.description]
import pandas as pd
my_dataframe = pd.DataFrame(rows, columns=columns)
cur.close()

#st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    , my_dataframe
    , max_selections = 5
)

if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
    
    #st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','"""+name_on_order+ """')"""
    
    #st.write(my_insert_stmt)
    #st.stop()
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        #session.sql(my_insert_stmt).collect()
        cur = conn.cursor()
        cur.execute(my_insert_stmt)
        cur.close()

import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response)

    
        st.success('Your Smoothie is ordered,' + name_on_order + '!', icon="✅")
