import pytesseract
from PIL import Image,ImageFilter
import re
import sqlite3
from base64 import b64encode
from io import BytesIO
from PIL import Image
import streamlit as st



SQL_DB_PATH = "business_cards.db"
sqlite_connection = sqlite3.connect(SQL_DB_PATH)
sqlite_cursor = sqlite_connection.cursor()
first_run = False

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Business card", use_column_width=True)
    st.write("")
    st.write("Image upload ok...")

    Input_path = uploaded_file
    output_path = "Sample.jpg"
    img = Image.open(Input_path)
    sharpened_img = img.filter(ImageFilter.SHARPEN)
    sharpened_img.save(output_path)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\M8470441\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
    image = Image.open(output_path)
    text = pytesseract.image_to_string(image)

    print(text.split("\n"))
    print(text)

    info = {
            "Company name": None,
            "Name": None,
            "Designation": None,
            "Phone number": None,
            "Mail ID": None,
            "Website": None,
            "Address": None
        }
    Designation_lower = ['sales','manager', "analyst","Officer","engineer","designer","director","Automation"]
    Designation_upper = [s.upper() for s in Designation_lower]
    Designation = Designation_upper
    print(Designation)

    company_name_1 = ["private","limited","ltd","pvt","industries","business"]
    company_name = [s.upper() for s in company_name_1]
    print(company_name)

    address_list = ['STREET','NO',",","CITY"]
    print(address_list)


    lines = text.split('\n')
    pattern = re.compile(r'^[a-zA-Z\s,]+$', re.MULTILINE)
    for line in lines:
        line_upper = line.upper()
        if pattern.match(line_upper) and all(keyword not in line_upper for keyword in Designation):
            print(line_upper)
            info["Name"] = line_upper.strip()
            break

    lines = text.split('\n')
    address_list_1 =[]
    address = []
    phone_number_1 =[]
    phone_number = []
    phone_number_pattern = re.compile(r'^[\d\s+-]+$')
    n=0
    lines = [item for item in lines if item.strip()]
    print(lines)
    try:
        for line in lines:
            line_upper = line.upper()
            n = n+1
            if any(item in line_upper for item in company_name):
                info["Company name"] = line_upper.strip()
                #print("####>",info["Company name"])

            elif any(item in line_upper for item in Designation):
                k=n
                #print("<<<<<<<<<",line,"---",k)
                #print("Ok")
                info["Designation"] = line_upper.strip()
                #print("--->",info["Designation"])


            elif any(item in line_upper for item in address_list):
                print("Okkk")

                address_list_1 = line_upper.strip()
                address.append(address_list_1)
                #print(address)
                info["Address"] = ' '.join(address)
                #print("--->",info["Address"],"--",n)    



            elif phone_number_pattern.match(line):
                phone_number_1 = re.sub(r'\D', '', line)
                phone_number.append(phone_number_1)
                phone_no = ' '.join(phone_number).replace(' ',',')
                info["Phone number"] = phone_no

            elif "+" in line:
                info["Phone number"] = line.strip()

            elif "@" in line:
                info["Mail ID"] = line.strip()

            elif "com" in line:
                info["Website"] = line.strip()

        info["Name"] = lines[k-2]
        #print(info["Name"])
    except Exception as e:
        print(e)

      
    if "REGIONAL SALES MANAGER" in Designation:
        None
    data = {}
    details = {}
    for key, value in info.items():
            data = f"{key}:{value}"
            #print(data)
            details.update(info.items())
    show = details.pop("Image", None)
    print(show)
       

    st.table(details)
    save_button = st.button("Save information")

    if save_button:
        with open(output_path, 'rb') as file:
            blobData = file.read()
        details["Image"] = (blobData)
        with open("output_file.txt", 'w') as file1:
            file1.write(str(blobData))

        query = '''
            INSERT INTO Business_details (
                Company_name, Name, Designation, Phone_number, Mail_id, Website, Address, Image
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''' 
        params = (
            details["Company name"],
            details["Name"],
            details["Designation"],
            details["Phone number"],
            details["Mail ID"],
            details["Website"],
            details["Address"],
            details["Image"]
            )

        sqlite_cursor.execute(query,params)

        sqlite_connection.commit()
if first_run == False:        
    name_details = sqlite_cursor.execute("SELECT Name FROM Business_details")
    name_details_1 = name_details.fetchall()
    name_list = [item[0] for item in name_details_1]
    print(name_list)
    search_text = st.text_input("Search for an item:", "")

    # Filter items based on search text
try:    
    filtered_items = [item for item in name_list if search_text.lower() in item.lower()]

    # Display filtered items
    if filtered_items:
        st.write("Filtered items:")
        for item in filtered_items:
            st.write(item)
    else:
        st.write("No items found matching the search criteria.")
    #print("======>>>",filtered_items)
    name_search_key_conf = st.button("Get_Details")
    Delete_detail = st.button("Delete this business card details")
    if name_search_key_conf:
        details = sqlite_cursor.execute("SELECT * FROM Business_details WHERE Name = ?", (search_text,))
        details_1 = details.fetchall()
        #print("---------->",details_1)
        details_2 = list(details_1[0])
        details_3 = details_2[:-1]
        image_details = (details_2[-1])
        test = "image555.jpg"
        with open(test, 'wb') as file:
            file.write(image_details)

        details_list = ["Company_name","Name","Designation","Phone_number","Mail_ID","Website","Address"]
        details_list_dic = dict(zip(details_list,details_3))
        table = st.table(details_list_dic)
        st.image(test, caption="Business card Image", use_column_width=True)
except Exception as c:
    print(c)    



if Delete_detail:
        try:
            sqlite_cursor.execute("DELETE FROM Business_details WHERE Name = ?", (filtered_items))
            sqlite_connection.commit() 
            sqlite_connection.close()
        except Exception as e:
            print (e)    
    
