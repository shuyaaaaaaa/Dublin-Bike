# Script for making changes to the database
#Purpose is to give us an idea of layout for how to make changes to the database
import login
import pymysql

try:
    # Connect to database
    conn = pymysql.connect(host=login.dbHost, user=login.dbUser, password=login.dbPassword, database=login.dbDatabase)
    cursor = conn.cursor()
    print("Connection to database successful!")

    # EXAMPLE SQL Statement
    sql = 'INSERT INTO static(number, contract_name, name, address, position_lat, position_lng, banking, bonus) VALUES("42", "dublin", "SMITHFIELD NORTH", "Smithfield North", "53.349562", "-6.278198", "0", "0")'
    cursor.execute(sql)
    conn.commit()
    print('Task executed successfully.')
    
except Exception as e:
    print(f"Database error: {e}")
    # Rollback any changes made to database if there was an error
    conn.rollback() 

# Close the connection
cursor.close()
conn.close()  