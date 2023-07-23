import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
import mysql.connector as sql
from PIL import Image
import cv2
import os
import matplotlib.pyplot as plt
import re

#first page
st.title("Business card data with OCR")
selected = option_menu(None, ["Home","Upload & Extract","Modify"], 
                       icons=["house","cloud-upload","pencil-square"],
                       orientation="horizontal")
#intialize ocr
reader = easyocr.Reader(['en'])

#db connection intialize
mydb = sql.connect(host="localhost",
                   user="root",
                   password="BavaPreetha",
                   database= "bizcard_db"
                  )
mycursor = mydb.cursor(buffered=True)

#home page
if selected == "Home":
        st.subheader("In this streamlit web app you can upload an image of a business card and extract relevant information from it using easyOCR. You can view, modify or delete the extracted data in this app.")
    
#upload page
if selected == "Upload & Extract":
    st.subheader("Upload a Business Card")
    uploaded_card = st.file_uploader("upload here",label_visibility="collapsed",type=["png","jpeg","jpg"])
    
    #card is uploaded means below if loop will execute
    if uploaded_card is not None:
        
        #ocr processing
        def save_card(uploaded_card):
            with open(os.path.join("uploaded_cards",uploaded_card.name), "wb") as f:
                f.write(uploaded_card.getbuffer())   
        save_card(uploaded_card)
        st.image(uploaded_card)
        
        #ocr image processing
        def image_preview(image,res): 
            for (bbox, text, prob) in res: 
              # unpack the bounding box
                (tl, tr, br, bl) = bbox
                tl = (int(tl[0]), int(tl[1]))
                tr = (int(tr[0]), int(tr[1]))
                br = (int(br[0]), int(br[1]))
                bl = (int(bl[0]), int(bl[1]))
                cv2.rectangle(image, tl, br, (0, 255, 0), 2)
                cv2.putText(image, text, (tl[0], tl[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            plt.rcParams['figure.figsize'] = (15,15)
            plt.axis('off')
            plt.imshow(image)
           
        #ocr processing
        with st.spinner("Please wait processing image..."):
               st.set_option('deprecation.showPyplotGlobalUse', False)
               saved_img = os.getcwd()+ "\\" + "uploaded_cards"+ "\\"+ uploaded_card.name
               image = cv2.imread(saved_img)
               res = reader.readtext(saved_img)
               st.markdown("### Image Processed and Data Extracted")
               st.pyplot(image_preview(image,res))  
        saved_img = os.getcwd()+ "\\" + "uploaded_cards"+ "\\"+ uploaded_card.name
        result = reader.readtext(saved_img,detail = 0,paragraph=False)    
       
        #converting image to binary numbers to upload in sql
        def img_to_binary(file):
            with open(file, 'rb') as file:
                binaryData = file.read()
            return binaryData
        
        #intialize data empty data variable
        data = {"company_name" : [],
                "card_holder" : [],
                "designation" : [],
                "mobile_number" :[],
                "email" : [],
                "website" : [],
                "area" : [],
                "city" : [],
                "state" : [],
                "pin_code" : [],
                "image" : img_to_binary(saved_img)
               }
        #add values to data variable from oce processing output
        for i in range(0,10):
            if (res[i][1] != res[-1][1]):
                if "www" in res[i][1] or "WWW" in res[i][1]:
                    data["website"].append(res[i][1])
                elif "@" in res[i][1]:
                    data["email"].append(res[i][1])
                elif "." in res[i][1]:
                    data["mobile_number"].append(res[i][1])
                elif "area" in res[i][1]:
                    data["area"].append(res[i][1])
                elif "city" in res[i][1]:
                    data["city"].append(res[i][1])
                elif "state" in res[i][1]:
                    data["state"].append(res[i][1])
                elif "pin" in res[i][1]:
                    data["pin_code"].append(res[i][1])
                elif "Name" in res[i][1]:
                    data["card_holder"].append(res[i][1])
                elif "Designation" in res[i][1]:
                    data["designation"].append(res[i][1])
                elif "company" in res[i][1]:
                    data["company_name"].append(res[i][1])
            else:
                if "www" in res[i][1] or "WWW" in res[i][1]:
                    data["website"].append(res[i][1])
                elif "@" in res[i][1]:
                    data["email"].append(res[i][1])
                elif "." in res[i][1]:
                    data["mobile_number"].append(res[i][1])
                elif "area" in res[i][1]:
                    data["area"].append(res[i][1])
                elif "city" in res[i][1]:
                    data["city"].append(res[i][1])
                elif "state" in res[i][1]:
                    data["state"].append(res[i][1])
                elif "pin" in res[i][1]:
                    data["pin_code"].append(res[i][1])
                elif "Name" in res[i][1]:
                    data["card_holder"].append(res[i][1])
                elif "Designation" in res[i][1]:
                    data["designation"].append(res[i][1])
                elif "company" in res[i][1]:
                    data["company_name"].append(res[i][1])
                break

        #replace null values with empty
        if(data["company_name"] == []):
            data["company_name"].append("Empty")            
        if(data["designation"] == []):
            data["designation"].append("Empty")
        if(data["card_holder"] == []):
            data["card_holder"].append("Empty")
        if(data["pin_code"] == []):
            data["pin_code"].append("Empty")
        if(data["state"] == []):
            data["state"].append("Empty")
        if(data["city"] == []):
            data["city"].append("Empty")
        if(data["area"] == []):
            data["area"].append("Empty")
        if(data["mobile_number"] == []):
            data["mobile_number"].append("Empty")
        if(data["email"] == []):
            data["email"].append("Empty")
        if(data["website"] == []):
            data["website"].append("Empty")
        
        #convert data to dataframe
        def create_df(data):
            df = pd.DataFrame(data)
            return df
        df = create_df(data)
        st.write(df)
        
        #upload dataframe to database
        if st.button("Upload to Database"):
            for i,row in df.iterrows():
                sql = """INSERT INTO card_data(company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code,image)
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                mycursor.execute(sql, tuple(row))
                # the connection is not auto committed by default, so we must commit to save our changes
                mydb.commit()
            st.success("Uploaded to database successfully")
            
#modify page         
if selected == "Modify":
    mycursor.execute("SELECT card_holder FROM card_data")
    result = mycursor.fetchall()
    business_cards = {}
    
    for row in result:
        business_cards[row[0]] = row[0]
    selected_card = st.selectbox("Select a card holder name to update", list(business_cards.keys()))
    st.markdown("Update or modify any data below")
    
    #get data from sql
    mycursor.execute("select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from card_data WHERE card_holder=%s",(selected_card,))
    result = mycursor.fetchone()
    company_name = st.text_input("Company_Name", result[0])
    card_holder = st.text_input("Card_Holder", result[1])
    designation = st.text_input("Designation", result[2])
    mobile_number = st.text_input("Mobile_Number", result[3])
    email = st.text_input("Email", result[4])
    website = st.text_input("Website", result[5])
    area = st.text_input("Area", result[6])
    city = st.text_input("City", result[7])
    state = st.text_input("State", result[8])
    pin_code = st.text_input("Pin_Code", result[9])
    
    #update changes
    if st.button("Update changes"):
                mycursor.execute("""UPDATE card_data SET company_name=%s,card_holder=%s,designation=%s,mobile_number=%s,email=%s,website=%s,area=%s,city=%s,state=%s,pin_code=%s
                                    WHERE card_holder=%s""", (company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code,selected_card))
                mydb.commit()
                st.success("Updated in database successfully.")
                
    #delete changes
    if st.button("Delete Business Card"):
                mycursor.execute(f"DELETE FROM card_data WHERE card_holder='{selected_card}'")
                mydb.commit()
                st.success("Deleted from database successfully.")