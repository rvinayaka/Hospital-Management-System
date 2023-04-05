from flask import Flask, request, jsonify
from conn import connection
from settings import logger

app = Flask(__name__)



# Query:
# CREATE TABLE hospital(sno SERIAL PRIMARY KEY ,patient_name VARCHAR(200) NOT NULL,
# admission DATE NOT NULL, treatments VARCHAR(400), discharge DATE NOT NULL);

# Table:
#  sno | patient_name | admission  |     treatments     | discharge
# -----+--------------+------------+--------------------+------------
#    1 | Andrew       | 1912-06-19 | band-aid, glucose  | 1912-07-02
#    2 | Hosikage     | 1929-10-09 | Check-up, Insuline | 1929-10-30

@app.route("/patients", methods=["GET", "POST"])             # Add new patient
def add_new_patients():
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to add item in the cart")

    try:
        patient_name = request.json["patient"]
        admission = request.json["admission"]
        treatments = request.json["treatments"]
        discharge = request.json["discharge"]

        # format = {
        #     "patient": "Hosikage",
        #     "admission": "1929-10-09",
        #     "treatments": "injection, saline",
        #     "discharge": "1929-10-30"
        # }

        add_query = """INSERT INTO hospital(patient_name, admission, treatments,  
                            discharge) VALUES (%s, %s, %s, %s)"""

        values = (patient_name, admission, treatments, discharge)
        cur.execute(add_query, values)
        # commit to database
        conn.commit()
        logger(__name__).info(f"{patient_name} added in the list")
        return jsonify({"message": "Item added to the cart"}), 200
    except Exception as error:
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": error})
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence details added, closing the connection")


@app.route("/", methods=["GET"])        # READ the details
def show_patients_list():
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to display all patients in the list")

    try:
        cur.execute("SELECT * FROM hospital")
        data = cur.fetchall()
        # Log the details into logger file
        logger(__name__).info("Displayed list of all patients in the list")

        return jsonify({"message": data}), 200
    except Exception as error:
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": error})
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence details displayed, closing the connection")



@app.route("/patients/<int:sno>", methods=["PUT"])  # Update the details
def update_patients_details(sno):          # Update the details of patient
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to update the details ")

    try:
        cur.execute("SELECT patient_name from hospital where sno = %s", (sno,))
        get_patient = cur.fetchone()

        if not get_patient:
            return jsonify({"message": "Patient not found"}), 200

        data = request.get_json()
        patient_name = data.get('patient')
        admission = data.get('admission')
        treatments = data.get('treatments')
        discharge = data.get('discharge')

        if patient_name:
            cur.execute("UPDATE hospital SET patient_name = %s WHERE sno = %s", (patient_name, sno))
        elif admission:
            cur.execute("UPDATE hospital SET admission = %s WHERE sno = %s", (admission, sno))
        elif treatments:
            cur.execute("UPDATE hospital SET treatments = %s WHERE sno = %s", (treatments, sno))
        elif discharge:
            cur.execute("UPDATE hospital SET losses = %s WHERE sno = %s", (discharge, sno))

        conn.commit()
        # Log the details into logger file
        logger(__name__).info(f"Details updated: {data}")
        return jsonify({"message": "Details updated", "Details": data}), 200
    except Exception as error:
        # Raise an error and log into the log file
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": error})
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence details updated, closing the connection")


@app.route("/report/<string:name>", methods=["GET"])        # READ the details
def patient_report(name):
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to display patient's details in the report")

    try:
        cur.execute("SELECT * FROM hospital WHERE patient_name = %s", (name, ))
        data = cur.fetchone()

        if not data:
            return jsonify({"message": "Patient not found"}), 200

        # Log the details into logger file
        logger(__name__).info("Displayed patient's details in the list")

        return jsonify({"message": data}), 200
    except Exception as error:
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": error})
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence details displayed, closing the connection")



@app.route("/search/<string:name>", methods=["GET"])        # READ the details
def search_patients(name):
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to search patients in the list")

    try:
        cur.execute("SELECT * FROM hospital WHERE patient_name = %s", (name, ))
        data = cur.fetchall()

        if not data:
            return jsonify({"message": "Patient not found"}), 200
        # Log the details into logger file
        logger(__name__).info(f"Displayed all patients with {name} in the list")

        return jsonify({"message": data}), 200
    except Exception as error:
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": error})
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence details displayed, closing the connection")


@app.route("/delete/<int:sno>", methods=["DELETE"])      # DELETE an item from cart
def delete_patients(sno):
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to delete the patients from the table")


    try:
        delete_query = "DELETE from hospital WHERE sno = %s"
        cur.execute(delete_query, (sno,))
        conn.commit()

        # Log the details into logger file
        logger(__name__).info(f"Account no {sno} deleted from the table")
        return jsonify({"message": "Deleted Successfully", "item_no": sno}), 200
    except Exception as error:
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": error})
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence accounts deleted, closing the connection")




if __name__ == "__main__":
    app.run(debug=True, port=5000)
