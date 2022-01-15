from flask import Flask, render_template, url_for, redirect, request, session
from helpers import login_required
import sqlite3
import datetime
from werkzeug.security import generate_password_hash, check_password_hash



#connection = sqlite3.connect("bookme.db", check_same_thread=False)

#cursor = connection.cursor()


app = Flask(__name__)

app.config["SESSION_TYPE"] = "filesystem"

app.secret_key = b'fjeshfl;jsf%^&$('


if __name__ == "__main__":
    app.run(debug = True)



# login page
@app.route("/", methods=["GET", "POST"])
def login():
    
    session.clear()

    if request.method == "GET":
        return render_template("login.html")

    # POST
    else:

        # getting user input from the form
        email = request.form.get("email")
        password = request.form.get("password")

        # checking that the user completes both fields of the form
        if not email or not password:
            return "<h1> You must enter an email and a password. </h1>"

        else:
            # connecting to the db
            connection = sqlite3.connect("bookme.db", check_same_thread=False)
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            row=cursor.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchall()
            connection.commit
            cursor.close()
            connection.close()

            # checking that there is an account for that email address
            if len(row) == 0:
                return "<h1> There is no user registered with this email address. </h1>"

            # checking for password validity
            else:
                registeredPassword = row[0]["hash"]

                if check_password_hash(registeredPassword, password) == False:
                    
                    return "<h1> The password is not correct. </h1>"

                else:
                    # storing useful data in session
                    session["username"] = row[0]["first_name"]
                    session["id"] = row[0]["id"]
                    session["email"] = row[0]["email"]
                    return redirect("/homepage")



# register page
@app.route("/register", methods = ["GET", "POST"])
def register():
    
    session.clear()

    if request.method == "GET":
        return render_template("register.html")

    else:
        # fetching user input from form
        firstName = request.form.get("first_name")
        lastName = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmPassword = request.form.get("confirm_password")

        # checking for full completion of the form
        if not firstName or not lastName or not email or not password or not confirmPassword:
            return "<h1> Sorry but you must fill all the sections of the form. </h1>"

        else:
            # checking that email address is not already registered 
            connection = sqlite3.connect("bookme.db", check_same_thread=False)
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            rows = cursor.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchall()
            connection.commit()
            cursor.close()
            connection.close()

            if len(rows)!=0:
                return "<h1> Sorry, there is already an account with this email address. </h1>"

            # checking for valid firstName and lastName input
            elif firstName.isalpha() == False or lastName.isalpha() == False:
                return "<h1> Sorry, your first name and last name must only contain letters."

            elif len(firstName) <= 1 or len(lastName) <=1:
                return "<h1> Sorry, your first name and last name must be more than 1 letter long."

            # checking password validity and security level
            elif len(password) < 8 or len(password) > 12:
                return "<h1> Sorry, your password must be between 8 and 12 characters long. </h1>"

            elif " " in password:
                return "<h1> Sorry, your password cannot contain any white space </h1>"

            else:
                specialChars = "!\"#$%&\'()*+, -./:;<=>?@[\]^_`{|}~"
                contains_num = False
                contains_low = False
                contains_up = False
                contains_spe = False

                for c in password:
                    if c.isnumeric() == True:
                        contains_num = True
                    if c.islower() == True:
                        contains_low = True
                    if c.isupper() == True:
                        contains_up = True
                    if c in specialChars:
                        contains_spe = True

                if contains_num == False:
                    return "<h1> Sorry, your password must contain at least one digit </h1>"

                elif contains_low == False:
                    return "<h1> Sorry, your password must contain at least one lowercase letter </h1>"

                elif contains_up == False:
                    return "<h1> Sorry, your password must contain at least one uppercase letter </h1>"

                elif contains_spe == False:
                    return "<h1> Sorry, your password must contain at least one special character </h1>"

                elif password != confirmPassword:
                    return "<h1> Sorry, the password doesn't match the password confirmation. </h1>"

                # if the user input is good, we store his info in the database
                else:
                    # hashing the password for security
                    pwhash = generate_password_hash(password)

                    # inserting user info in the users table
                    connection = sqlite3.connect("bookme.db", check_same_thread=False)
                    connection.row_factory = sqlite3.Row
                    cursor = connection.cursor()
                    cursor.execute("INSERT INTO users VALUES (NULL, ?, ?, ?, ?)", (email, firstName, lastName, pwhash))
                    connection.commit()

                    # fetching current user id
                    user = cursor.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchall()
                    userId = user[0]["id"]

                    # setting default constraints for the user (by defualt, the user is available between 8am and 6pm)
                    cursor.execute("INSERT INTO constraints VALUES (?, ?, ?, ?)", (userId, "00:00", "08:00", "day_start"))
                    connection.commit()
                    cursor.execute("INSERT INTO constraints VALUES (?, ?, ?, ?)", (userId, "18:00", "23:59", "day_end"))
                    connection.commit()

                    cursor.close()
                    connection.close()

                    return redirect("/")



@app.route("/homepage")
@login_required
def homepage():
    
    username = session["username"]

    # create current date object
    today = datetime.date.today()
    # get a an iso date string from the date
    todayDate = today.isoformat()
    # extract weekday
    todayDay = today.strftime("%A")

    ## find the days of the week corresponding to the current day
    # creating an empty list to store the dates (as iso strings) of the days of the week corresponding to today's date
    weekDates = []

    # getting the day's number of the current date (from 0 to 6)
    day_num = datetime.date.weekday(today)

    # adding or substracting to the current date by the appropritate number of days to get the other dates of the week, then adding each date to the list as an iso string
    for i in range(- day_num , 7 - day_num ) :
        weekDayDate = today + datetime.timedelta(days = i)
        weekDates.append(weekDayDate.isoformat())
    ##


    # Creating a list of the week days to later pass to the template so that we can iterate over it at the same time as we iterate over the list of lists of events.
    weekDays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]



    ## for displaying today and today's event on the template 
    # for current user and day, retrieve events from database
    connection = sqlite3.connect("bookme.db", check_same_thread=False)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    rows = cursor.execute("SELECT * FROM events WHERE user_id = ? AND e_date = ? ORDER BY e_start", (session["id"], todayDate)).fetchall()
    connection.commit()
    cursor.close()
    connection.close()

    message = ""
    if len(rows) == 0 :
        message = "There are no events today."
    ##
    
    ## for displayling the week corresponding to the current day with all its events
    # weekEvents is a list which will store 7 lists, one for each day of the week, and each one containing the events for that day as dictionaries
    # weekEvents is a list of lists of dictionaries
    # to build it we will iterate over the 7 dates stored in the weekDates list that we built earlier, and for each of these dates, query the database for the corresonding list of events
    weekEvents = []

    for date in weekDates :
        connection = sqlite3.connect("bookme.db", check_same_thread=False)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        events = cursor.execute("SELECT * FROM events WHERE user_id = ? AND e_date = ? ORDER BY e_start", (session["id"], date)).fetchall()
        connection.commit()
        cursor.close()
        connection.close()
        weekEvents.append(events)
    ##

    ## for diaplaying the next week and its events
    # for the next week, we take the last date of the weekDates list as a starting point and loop 7 times to add the seven next dates in the nextWeekDates list
    lastWeekDate = datetime.date.fromisoformat(weekDates[6])
    nextWeekDates = []

    for i in range(7):
        newdate = lastWeekDate + datetime.timedelta(days=i+1)
        nextWeekDates.append(newdate.isoformat())

    ## similarly to the weekEvents list above, we query from the databse the events corresponding to each date of the nextWeekDates list and append the nextWeekEvents list
    nextWeekEvents = []

    for date in nextWeekDates:
        connection = sqlite3.connect("bookme.db", check_same_thread=False)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        events = cursor.execute("SELECT * FROM events WHERE user_id = ? AND e_date = ? ORDER BY e_start", (session["id"], date)).fetchall()
        connection.commit()
        cursor.close()
        connection.close()
        nextWeekEvents.append(events)

    ##


    return render_template("homepage.html", user_name = username, today_day = todayDay, today_date = todayDate, message = message, rows = rows, week_days = weekDays, week_dates = weekDates, week_events = weekEvents, next_week_dates = nextWeekDates, next_week_events = nextWeekEvents )


# this route has to be reworked and split in two disctinct routes, one for adding events, the other for deleting them
@app.route("/manage", methods = ["GET", "POST"])
@login_required
def manage():

    if request.method == "POST":

        # collect event-date, event-start-time, event-end-time, and event-decription from the form(s)
        # adder form
        eDate = request.form.get("e_date")
        eStart = request.form.get("e_start")
        eEnd = request.form.get("e_end")
        eDescription = request.form.get("e_description")

        ## checking for valid imput

        # checking for completion of the form
        if not eDate or not eStart or not eEnd or not eDescription:
            return "<h1>You must fill in all the fields.</h1>"

        # checking that description isn't too long
        elif len(eDescription) > 100 :
            return "<h1>The description is too long, you are limited to 100 characters.</h1>"

        else:
            # checking for valid date format
            try :
                checkDate = datetime.date.fromisoformat(eDate)

            except:
                return "<h1>You must input a valid date in the following format : YYYY-MM-DD</h1>"

            ### to do :check that the date is not too far in the past or future

            ## checking for valid time input
            # checking for valid time input
            if len(eStart) > 5 or len(eEnd) > 5 :
                return "<h1>You must input a valid start-time and end-time in the following format : HH:MM</h1>"

            else:
                try:
                    checkStart = datetime.time.fromisoformat(eStart)
                    checkEnd = datetime.time.fromisoformat(eEnd)
                except:
                    return "<h1>YOu must input a valid start time and end time in the following format : HH:MM</h1>"

                else:
                    # checking that event start is earlier than event end
                    if checkStart >= checkEnd :
                        return "<h1>The event start must be earlier than the event end</h1>"
            ##

            ## prevent overlapping
            # fetch other events on the same date in database
            connection = sqlite3.connect("bookme.db", check_same_thread=False)
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            checkRows = cursor.execute("SELECT * FROM events WHERE user_id = ? AND e_date = ?", (session["id"], eDate)).fetchall()
            connection.commit()
            
            # if any, check that events aren't overlapping with the event the user is trying to add
            if len(checkRows) != 0 :

                for event in checkRows :
                    start = datetime.time.fromisoformat(event["e_start"])
                    end = datetime.time.fromisoformat(event["e_end"])

                    if (  checkStart > start and checkStart < end ) or ( checkEnd > start and checkEnd < end ) or (checkStart < start and checkEnd > end):
                        return "<h1>The event is overlapping with a preexisting event.</h1>"
            ##

            # store event data in database
            connection = sqlite3.connect("bookme.db", check_same_thread=False)
            cursor = connection.cursor()
            cursor.execute("INSERT INTO events VALUES (NULL, ?, ?, ?, ?, ?)", (session["id"],eDate, eStart, eEnd, eDescription))
            connection.commit()
            cursor.close()
            connection.close()

            return redirect("/manage")
        

    # GET
    else :

        ### display events

        connection = sqlite3.connect("bookme.db", check_same_thread=False)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        rows = cursor.execute("SELECT * FROM events WHERE user_id = ? ORDER BY e_date ASC, e_start ASC", (session["id"],)).fetchall()
        connection.commit()
        cursor.close()
        connection.close()

        ## separate events in future and past events
        # get today's date
        today = datetime.date.today()

        # create two empty lists, one for ealier dates, one for later dates (as well as the current one)
        previous = []
        coming = []

        # check the rows returned by the database and check for each dictionnary if the date (converted from iso format) is earlier or later than today
        # append the dictionnary to one of the two lists depending on the result
        for row in rows:
            convertedDate = datetime.date.fromisoformat(row["e_date"])
            if convertedDate >= today :
                coming.append(row)
            else :
                previous.append(row)
            
        return render_template("manage.html", coming = coming, previous = previous)



# route for deleting events
@app.route("/delete_event/<eDelete>", methods = ["POST"])
@login_required
def delete_event(eDelete):

    # delete the event corresponding to the eDelete data (the id of the selected event) received from the form
    eDelete = int(eDelete)
    connection = sqlite3.connect("bookme.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM events WHERE e_id = ? AND user_id = ?", (eDelete, session["id"]))
    connection.commit()
    cursor.close()
    connection.close()

    return redirect("/manage")




@app.route("/availability", methods = ["GET", "POST"])
@login_required
def availability():

    if request.method == "POST" :
        
        dayStart = request.form.get("day_start")
        dayEnd = request.form.get("day_end")
        breaktimeStart = request.form.get("breaktime_start")
        breaktimeEnd = request.form.get("breaktime_end")

        ## checking for valid input
        # checking that the correct fields have been filled:

        if (dayStart and not dayEnd) or (not dayStart and dayEnd):
            return "<h1>If you decide to define a day-start, you must select both start-time and end-time</h1>"

        elif (breaktimeStart and not breaktimeEnd) or (breaktimeEnd and not breaktimeStart):
            return "<h1>If you decide to define a break, you must select both start-time and end-time</h1>"

        else :
            ## if only day_start and day_end were selected and no break was defined
            if (dayStart and dayEnd) and (not breaktimeStart and not breaktimeEnd) :
                
                # checking for valid format
                try :
                    dayStartTime = datetime.time.fromisoformat(dayStart)
                    dayEndTime = datetime.time.fromisoformat(dayEnd)

                except:
                    return "<h1>The start-time and end-time must be in the following format : HH:MM</h1>"
                
                # checking that start-time is earlier than end-time
                else :
                    if dayStartTime >= dayEndTime :
                        return "<h1>The day-start-time must be earlier than the day-end-time.</h1>"

            
                # update the day start and day end in the database
                connection = sqlite3.connect("bookme.db", check_same_thread=False)
                cursor = connection.cursor()
                cursor.execute("UPDATE constraints SET c_end = ? WHERE user_id = ? AND c_type = 'day_start' ", (dayStart, session["id"]))
                connection.commit()
                cursor.execute("UPDATE constraints SET c_start = ? WHERE user_id = ? AND c_type = 'day_end' ", (dayEnd, session["id"]))
                connection.commit()
                cursor.close()
                connection.close()

                return redirect("/availability")
            ##


            ## if only breaktime was defined
            elif (not dayStart and not dayEnd) and (breaktimeStart and breaktimeEnd):
                
                # checking for valid format
                try :
                    breaktimeStartTime = datetime.time.fromisoformat(breaktimeStart)
                    breaktimeEndTime = datetime.time.fromisoformat(breaktimeEnd)
                
                except :
                    return "<h1>All time values must be in the following format : HH:MM</h1>"
                
                # cbecking that break start is earlier than break end
                else:
                    if breaktimeStartTime >= breaktimeEndTime:
                        return "<h1>The break's start-time must be earlier than the break's end-time.</h1>"

                # check if break time is present in database
                connection = sqlite3.connect("bookme.db", check_same_thread=False)
                connection.row_factory = sqlite3.Row
                cursor = connection.cursor()
                breakTime = cursor.execute("SELECT * FROM constraints WHERE user_id = ? AND c_type = 'break_time' ", (session["id"],)).fetchall()
                connection.commit()
                cursor.close()
                connection.close()

                # if already present, update breaktime in database
                if len(breakTime) != 0 :
                    connection = sqlite3.connect("bookme.db", check_same_thread=False)
                    cursor = connection.cursor()
                    cursor.execute("UPDATE constraints SET c_start = ?, c_end = ? WHERE user_id = ? AND c_type = 'break_time' ", (breaktimeStart, breaktimeEnd, session["id"]))
                    connection.commit()
                    cursor.close()
                    connection.close()

                    return redirect("/availability")
                    

                # if not present, add breaktime to databse
                else :
                    connection = sqlite3.connect("bookme.db", check_same_thread=False)
                    cursor = connection.cursor()
                    cursor.execute("INSERT INTO constraints VALUES (?, ?, ?, ?)", (session["id"], breaktimeStart, breaktimeEnd, "break_time"))
                    connection.commit()
                    cursor.close()
                    connection.close()

                    return redirect("/availability")

            ##

            
            ## if both a breaktime and day start / day end were defined
            else :

                # checking for valid format
                try :
                    dayStartTime = datetime.time.fromisoformat(dayStart)
                    dayEndTime = datetime.time.fromisoformat(dayEnd)
                    breaktimeStartTime = datetime.time.fromisoformat(breaktimeStart)
                    breaktimeEndTime = datetime.time.fromisoformat(breaktimeEnd)

                except:
                    return "<h1>All time values must be in the following format : HH:MM</h1>"

                # cbecking that break start is earlier than break end and that day start is earlier than day end
                else:
                    if dayStartTime >= dayEndTime :
                        return "<h1>The day-start-time must be earlier than the day-end-time.</h1>"
                    elif breaktimeStartTime >= breaktimeEndTime:
                        return "<h1>The break's start-time must be earlier than the break's end-time.</h1>"

                # check if break time is present in database
                connection = sqlite3.connect("bookme.db", check_same_thread=False)
                connection.row_factory = sqlite3.Row
                cursor = connection.cursor()
                breakTime = cursor.execute("SELECT * FROM constraints WHERE user_id = ? AND c_type = 'break_time' ", (session["id"],)).fetchall()
                connection.commit()
                cursor.close()
                connection.close()

                # if already present, update breaktime, day start, and day end in database in database
                if len(breakTime) != 0 :
                    connection = sqlite3.connect("bookme.db", check_same_thread=False)
                    cursor = connection.cursor()
                    cursor.execute("UPDATE constraints SET c_end = ? WHERE user_id = ? AND c_type = 'day_start' ", (dayStart, session["id"]))
                    connection.commit()
                    cursor.execute("UPDATE constraints SET c_start = ? WHERE user_id = ? AND c_type = 'day_end' ", (dayEnd, session["id"]))
                    connection.commit()
                    cursor.execute("UPDATE constraints SET c_start = ?, c_end = ? WHERE user_id = ? AND c_type = 'break_time' ", (breaktimeStart, breaktimeEnd, session["id"]))
                    connection.commit()
                    cursor.close()
                    connection.close()

                    return redirect("/availability")
                    
                # if not present, update day start and day end, and add breaktime to databse
                else :
                    connection = sqlite3.connect("bookme.db", check_same_thread=False)
                    cursor = connection.cursor()
                    cursor.execute("UPDATE constraints SET c_end = ? WHERE user_id = ? AND c_type = 'day_start' ", (dayStart, session["id"]))
                    connection.commit()
                    cursor.execute("UPDATE constraints SET c_start = ? WHERE user_id = ? AND c_type = 'day_end' ", (dayEnd, session["id"]))
                    connection.commit()
                    cursor.execute("INSERT INTO constraints VALUES (?, ?, ?, ?)", (session["id"], breaktimeStart, breaktimeEnd, "break_time"))
                    connection.commit()
                    cursor.close()
                    connection.close()

                    return redirect("/availability")
            
            ##


    # GET 
    else :
        ## fetch current day_start day_end as well as breaktime_start and breaktime_end if defined :
        connection = sqlite3.connect("bookme.db", check_same_thread=False)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        constraints = cursor.execute("SELECT * FROM constraints WHERE user_id = ?", (session["id"],)).fetchall()
        connection.commit()
        cursor.close()
        connection.close()

        # these variables will hold the values we want to display in the template
        dStart = None
        dEnd = None
        bStart = None
        bEnd = None

        # assign to each of the variables created the corresponding value by looking at the times defined in the database
        for event in constraints:
            if event["c_type"] == "day_start" :
                dStart = event["c_end"]
            elif event["c_type"] == "day_end" :
                dEnd = event["c_start"]
            elif event["c_type"] == "break_time" :
                bStart = event["c_start"]
                bEnd = event["c_end"]

        return render_template("availability.html", day_start = dStart, day_end = dEnd, breaktime_start = bStart, breaktime_end = bEnd)



# route handling the diaplay of the contacts and contact requests
@app.route("/contacts")
@login_required
def contacts():

    # fetch contacts requests where the current user's email is the contact_email (receiver), and contacts for the current user_email in the database
    connection = sqlite3.connect("bookme.db", check_same_thread=False)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    requests = cursor.execute("SELECT * FROM requests WHERE contact_email = ?", (session["email"],)).fetchall()
    contacts = cursor.execute("SELECT * FROM contacts WHERE user_email = ?", (session["email"],)).fetchall()
    connection.commit()
    cursor.close()
    connection.close()

    return render_template("contacts.html", requests = requests, contacts = contacts)



# route handling sending a contact request to another user
@app.route("/addcontact", methods = ["POST"])
@login_required
def addcontact():
    
    # receive data from form
    contactEmail = request.form.get("contact_email")

    # check that the email entered corresponds to a registered user
    connection = sqlite3.connect("bookme.db", check_same_thread=False)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    users = cursor.execute("SELECT * FROM users WHERE email = ?", (contactEmail,)).fetchall()
    connection.commit()
    cursor.close()
    connection.close()

    # if no registered user with this email is found , return a message
    if len(users) == 0:
        return "<h1>There is no user with this email address.</h1>"

    # checking that the user isn't sending a request to themselves
    elif contactEmail == session["email"]:
        return "<h1>You can't send a contact request to yourself</h1>"

    # if a registred user with this email is found , then check in the database that the current user hasn't already sent them a request
    else:
        connection = sqlite3.connect("bookme.db", check_same_thread=False)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        requests = cursor.execute("SELECT * FROM requests WHERE user_email = ? AND contact_email = ?", (session["email"], contactEmail)).fetchall()
        connection.commit()
        cursor.close()
        connection.close()
        
        # if a request has already been sent to this user, return a message
        if len(requests) != 0 :
            return "<h1>You have already sent a request to that user.</h1>"

        # if the user to whom you are sending a request has already sent you one, return a message to the user to inform them and suggest they accept the user
        connection = sqlite3.connect("bookme.db", check_same_thread=False)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        receivedRequests = cursor.execute("SELECT * FROM requests WHERE user_email = ? AND contact_email = ?", (contactEmail, session["email"])).fetchall()
        connection.commit()
        cursor.close()
        connection.close()

        if len(receivedRequests) != 0:
            return "<h1>This user has sent you a contact request, no need to send them one too, if you want to add them as a contact you can accept their request.</h1>"


        # if the user is already a contact, return a message
        connection = sqlite3.connect("bookme.db", check_same_thread=False)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        contacts = cursor.execute("SELECT * FROM contacts WHERE user_email = ? AND contact_email = ?", (session["email"], contactEmail,)).fetchall()
        connection.commit()
        cursor.close()
        connection.close()

        if len(contacts) != 0 :
            return "<h1>This user is already one of your contacts</h1>"


        # if no request has been sent to this user yet, add request to the database
        else :
            connection = sqlite3.connect("bookme.db", check_same_thread=False)
            cursor = connection.cursor()
            cursor.execute("INSERT INTO requests VALUES (NULL, ?, ?)", (session["email"], contactEmail))
            connection.commit()
            cursor.close()
            connection.close()

            return redirect("/contacts")    



# route handling accepting and refusing contact requests
# the route is dynamically generated depending on what form was submitted and receives extra arguments from that form (see url_for() in the contacts.html template )
@app.route("/manage_requests/<request_id>/<action>", methods = ["POST"])
@login_required
def manage_requests(request_id, action):

    if action == "accept" :
        # fetch the info of the corresponding request from the database requests table 
        connection = sqlite3.connect("bookme.db", check_same_thread=False)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cRequests = cursor.execute("SELECT * FROM requests WHERE r_id = ?", (request_id,)).fetchall()
        connection.commit()
        cursor.close()
        connection.close()

        # get the sender's user_email
        cRequest = cRequests[0]
        senderEmail = cRequest["user_email"]

        
        # insert the data into the databse contacts table for both the sender and the receiver (current user)
        connection = sqlite3.connect("bookme.db", check_same_thread=False)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("INSERT INTO contacts VALUES (?, ?)", (session["email"], senderEmail))
        cursor.execute("INSERT INTO contacts VALUES (?, ?)", (senderEmail, session["email"]))
        connection.commit()
        cursor.close()
        connection.close()

        # delete the request from the requests table in the database
        connection = sqlite3.connect("bookme.db", check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute("DELETE FROM requests WHERE r_id = ?", (request_id,))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect("/contacts")

    elif action == "refuse" :
        # delete the request from the database requests table
        connection = sqlite3.connect("bookme.db", check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute("DELETE FROM requests WHERE r_id = ?", (request_id,))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect("/contacts")

    else:

        return "<h1>Error</h1>"



# route for viewing a contact's availability
# the route is dynamically generated using the extra argument "contact_email" from the form
@app.route("/view_contact/<contact_email>", methods = ["POST"])
@login_required
def view_contact(contact_email):

    # for this contact, get the user id
    connection = sqlite3.connect("bookme.db", check_same_thread=False)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    contactID = cursor.execute("SELECT id FROM users WHERE email = ?", (contact_email,)).fetchall()[0]["id"]
    connection.commit()
    cursor.close()
    connection.close()

    # get today's date
    todayDate = datetime.date.today()

    # create a list that will store 15 iso format dates starting from today's date
    datesList = []

    # create a list that will store 15 weekdays
    weekdaysList = []

    for i in range(15):
        dayDate = todayDate + datetime.timedelta(days=i)
        datesList.append(dayDate.isoformat())
        weekdaysList.append(dayDate.strftime("%A"))

    # create a list that will contain lists of events for each day
    daysEventsList = []

    # for each date get their events from the database
    for date in datesList :
        connection = sqlite3.connect("bookme.db", check_same_thread=False)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        events = cursor.execute("SELECT * FROM events WHERE user_id = ? AND e_date = ?", (contactID, date)).fetchall()
        connection.commit()
        cursor.close()
        connection.close()
        daysEventsList.append(events)

    # get the contact's constraints
    connection = sqlite3.connect("bookme.db", check_same_thread=False)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    constraints = cursor.execute("SELECT * FROM constraints WHERE user_id = ?", (contactID,)).fetchall()
    connection.commit()
    cursor.close()
    connection.close()

    # reminder
    # datesList = []
    # weekdaysList = []
    # daysEventsList = []

    # create a new list "allConstraints" which will store a list of both events and constraints times for each day day.
    allConstraints = []

    # first add all the events
    for i in range(15):
        newList = []
        for event in daysEventsList[i]:
            newDict = {}
            newDict["c_date"] = event["e_date"]
            newDict["c_start"] = event["e_start"]
            newDict["c_end"] = event["e_end"]
            newList.append(newDict)

        allConstraints.append(newList)

    # then for each day, add the constraints
    for i in range(15):
        for constraint in constraints:
            newDict = {}
            newDict["c_date"] = datesList[i]
            newDict["c_start"] = constraint["c_start"]
            newDict["c_end"] = constraint["c_end"]
            allConstraints[i].append(newDict)

    
    # sort the allConstraints list by c_start (bubble sort)
    for day in allConstraints:
        n = len(day)
        for i in range(n):
            for j in range(n-i-1):
                if datetime.time.fromisoformat(day[j]["c_start"]) > datetime.time.fromisoformat(day[j+1]["c_start"]) :
                    day[j], day[j+1] = day[j+1], day[j]


    # create a new list "availabilitiy", and populate it by getting all the gaps in each day of the "allConstraints" list
    availability = []

    for day in allConstraints:
        dayAvailability = []
        for i in range(len(day)-1) :
            a = {}
            if datetime.time.fromisoformat(day[i]["c_end"]) < datetime.time.fromisoformat(day[i+1]["c_start"]) :
                a["a_start"] = day[i]["c_end"]
                a["a_end"] = day[i+1]["c_start"]
                dayAvailability.append(a)
        availability.append(dayAvailability)


    # return the template with this "availability" list
    return render_template("contact_availability.html", contact_email = contact_email, dates_list = datesList, weekdays_list = weekdaysList, availability = availability)
