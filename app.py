from flask import Flask, request, jsonify
from conn import connection
from settings import logger, handle_exceptions
import psycopg2

app = Flask(__name__)



# Query:
# CREATE TABLE hospital(sno SERIAL PRIMARY KEY ,patient_name VARCHAR(200) NOT NULL,
# admission DATE NOT NULL, treatments VARCHAR(400), discharge DATE NOT NULL);

# Table:
#  sno | patient_name | admission  |     treatments     | discharge  |      order_tests      |  test_results   |        prescription        | payment
# -----+--------------+------------+--------------------+------------+-----------------------+-----------------+----------------------------+---------
#    1 | Andrew       | 1912-06-19 | band-aid, glucose  | 1912-07-02 | Hemoglobin, Sugar, BP | Negative in all | Lemonade, Eye drops, Vicks | Done
#    2 | Hosikage     | 1929-10-09 | Check-up, Insuline | 1929-10-30 | Abc, Xyz              | Positive in Abc | Ear drops, hair oil        | pending





@app.route("/patients", methods=["GET", "POST"], endpoint='add_new_patients')             # Add new patient
@handle_exceptions
def add_new_patients():
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to add item in the cart")

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


@app.route("/", methods=["GET"], endpoint='show_patients_list')        # READ the details
@handle_exceptions
def show_patients_list():
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to display all patients in the list")

    cur.execute("SELECT * FROM hospital")
    data = cur.fetchall()
    # Log the details into logger file
    logger(__name__).info("Displayed list of all patients in the list")

    return jsonify({"message": data}), 200



@app.route("/patients/<int:sno>", methods=["PUT"], endpoint='update_patients_details')  # Update the details
@handle_exceptions
def update_patients_details(sno):          # Update the details of patient
    # Start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to update the details ")

    # Search the patient if found in the list
    cur.execute("SELECT patient_name from hospital where sno = %s", (sno,))
    get_patient = cur.fetchone()

     # if patient not found then return message
    if not get_patient:
        return jsonify({"message": "Patient not found"}), 200

    # take values from user
    data = request.get_json()
    patient_name = data.get('patient')
    admission = data.get('admission')
    treatments = data.get('treatments')
    discharge = data.get('discharge')

     # Check what value need to be modified
    if patient_name:
        cur.execute("UPDATE hospital SET patient_name = %s WHERE sno = %s", (patient_name, sno))
    elif admission:
        cur.execute("UPDATE hospital SET admission = %s WHERE sno = %s", (admission, sno))
    elif treatments:
        cur.execute("UPDATE hospital SET treatments = %s WHERE sno = %s", (treatments, sno))
    elif discharge:
        cur.execute("UPDATE hospital SET losses = %s WHERE sno = %s", (discharge, sno))

    # Commit the changes in to table
    conn.commit()
    # Log the details into logger file
    logger(__name__).info(f"Details updated: {data}")
    return jsonify({"message": "Details updated", "Details": data}), 200


@app.route("/report/<string:name>", methods=["GET"], endpoint='patient_report')        # READ the details
@handle_exceptions
def patient_report(name):
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to display patient's details in the report")

    cur.execute("SELECT * FROM hospital WHERE patient_name = %s", (name,))
    data = cur.fetchone()

    if not data:
        return jsonify({"message": "Patient not found"}), 200

    # Log the details into logger file
    logger(__name__).info("Displayed patient's details in the list")

    return jsonify({"message": data}), 200



@app.route("/search/<string:name>", methods=["GET"], endpoint='search_patients')        # READ the details
@handle_exceptions
def search_patients(name):
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to search patients in the list")

    cur.execute("SELECT * FROM hospital WHERE patient_name = %s", (name,))
    data = cur.fetchall()

    if not data:
        return jsonify({"message": "Patient not found"}), 200
    # Log the details into logger file
    logger(__name__).info(f"Displayed all patients with {name} in the list")

    return jsonify({"message": data}), 200


@app.route("/delete/<int:sno>", methods=["DELETE"], endpoint='delete_patients')      # DELETE an item from cart
@handle_exceptions
def delete_patients(sno):
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to delete the patients from the table")

    delete_query = "DELETE from hospital WHERE sno = %s"
    cur.execute(delete_query, (sno,))
    conn.commit()

    # Log the details into logger file
    logger(__name__).info(f"Account no {sno} deleted from the table")
    return jsonify({"message": "Deleted Successfully", "item_no": sno}), 200


@app.route("/patients/tests/<int:sno>", methods=["PUT"], endpoint='add_ordered_tests')  # Add tests to be done
@handle_exceptions
def add_ordered_tests(sno):
    # Start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to add tests to be done ")

    # Search the patient if found in the list
    cur.execute("SELECT patient_name from hospital where sno = %s", (sno,))
    get_patient = cur.fetchone()

     # if patient not found then return message
    if not get_patient:
        return jsonify({"message": "Patient not found"}), 200

    # take values from user
    data = request.get_json()
    order_tests = data.get('tests')

    cur.execute("UPDATE hospital SET order_tests = %s WHERE sno = %s", (order_tests, sno))

    # Commit the changes in to table
    conn.commit()

    # Log the details into logger file
    logger(__name__).info(f"{order_tests} tests has been told by the doctor")
    return jsonify({"message": f"{order_tests} tests has been told by the doctor",
                    "Details": data}), 200


@app.route("/patients/test_results/<int:sno>", methods=["PUT"], endpoint='test_results')  # Add tests results
@handle_exceptions
def add_test_results(sno):
    # Start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to add tests results")

    # Search the patient if found in the list
    cur.execute("SELECT patient_name from hospital where sno = %s", (sno,))
    get_patient = cur.fetchone()

     # if patient not found then return message
    if not get_patient:
        return jsonify({"message": "Patient not found"}), 200

    # take values from user
    data = request.get_json()
    test_results = data.get('results')

    cur.execute("UPDATE hospital SET test_results = %s WHERE sno = %s", (test_results, sno))

    # Commit the changes in to table
    conn.commit()

    # Log the details into logger file
    logger(__name__).info(f"Results of test: {data} ")
    return jsonify({"message": f"Results of test: {data}",
                    "Details": data}), 200


@app.route("/patients/prescription/<int:sno>", methods=["PUT"], endpoint='add_prescription')  # Add prescription
@handle_exceptions
def add_prescription(sno):
    # Start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to add prescription")

    # Search the patient if found in the list
    cur.execute("SELECT patient_name from hospital where sno = %s", (sno,))
    get_patient = cur.fetchone()

     # if patient not found then return message
    if not get_patient:
        return jsonify({"message": "Patient not found"}), 200

    # take values from user
    data = request.get_json()
    prescription = data.get('prescription')

    cur.execute("UPDATE hospital SET prescription = %s WHERE sno = %s", (prescription, sno))

    # Commit the changes in to table
    conn.commit()

    # Log the details into logger file
    logger(__name__).info(f"{prescription} has been given by the doctor")
    return jsonify({"message": f"{prescription} has been given by the doctor",
                    "Details": data}), 200


@app.route("/patients/payment_sts/<int:sno>", methods=["PUT"], endpoint='update_payment_status')  # Add prescription
@handle_exceptions
def update_payment_status(sno):
    # Start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to update payment status")

    # Search the patient if found in the list
    cur.execute("SELECT patient_name from hospital where sno = %s", (sno,))
    get_patient = cur.fetchone()

     # if patient not found then return message
    if not get_patient:
        return jsonify({"message": "Patient not found"}), 200

    # take values from user
    data = request.get_json()
    payment = data.get('payment')

    cur.execute("UPDATE hospital SET payment = %s WHERE sno = %s", (payment, sno))

    # Commit the changes in to table
    conn.commit()

    # Log the details into logger file
    logger(__name__).info(f"Payment status of patient id {sno} has been updated to {payment}")
    return jsonify({"message": f"Payment status of patient id {sno} has been updated to {payment}",
                    "Details": data}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
