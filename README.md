# **BOOKME**
&nbsp;

## Video Demo:  https://youtu.be/9aFvOeQSe4g

&nbsp;

---

&nbsp;

## **Description**

&nbsp;

### In short :
Bookme is a web application built with Flask which allows users to register for an account and manage a personal calendar / planner as well as add other users, so that they can see their availability. 

&nbsp;

### Getting started, features :
Start by createing an account on the "register" page, then login.
Once that's done, you can set your daily availability on the "availability" page, then start adding events to your calendar on the "manage calendar" page. You can also delete events from this page.
Once you have added a few events, you will be able to view them on your "homepage" page (yes I know that's kind of a repetition here), provided that they are planned for this week or the next one.
You also have the possibility to add other users by their email address on the "contacts" page, and once they've accepted your contact request, view their availability. It is aldo on this page that you can see the contact requests that you have received.

&nbsp;

---

&nbsp;

## **Why this app ?**

&nbsp;

I work as an English teacher in the private industry, most of my students are working adults, often with busy schedules, and since my school doesn't use any web platform for students to book lessons with their teachers or record the number of hours of lessons they've had, my colleagues and I have to contact them by phone, sms, or email (it varies with each student), and we generally don't know when they're available, nor do they know when we are available either, which often results in several back and forth messages to arrange a date for a lesson, which required a lot of time when you ad up all the students.
I often think that things would be a lot simpler if students could use a platform to see when their teachers are available and book lessons themselves, with the teacher only having to accept the request for the lesson to be set for both. This platform could also be used to record the number of hours each student has on their balance, as well as how many they've already used, etc...
This is how I got the idea to start working on such a web application, which resulted in me creating Bookme, a very basic version and implementation of this idea.

&nbsp;

---

&nbsp;

## **Files and their functions**

&nbsp;

- ### app.py
This is the heart of the application, where all the necessary modules are imported, where the application is initialized, and where all the routes are defined.
It ended up being quite large, so now that I think about it, if I had to do it again or improve it, I would break it down into different files.

&nbsp;

- ### helpers.py
This is where my "login_required()" decorator function is defined.
Related to what I said just above about the "app.py" being too large, some chunks of code could have been defined as functions here instead of being fully written in "app.py", such as my code used to calculate whether an event overlaps with another, or my code used to calculate the gaps between events to generate a user's availability.

&nbsp;

- ### layout.html
The basic layout template for my html pages, with the necessary meta data in the head sections, loading bootstrap, linking my css stylesheet as well as the special font "pushster" that I use throughout my pages.

&nbsp;

- ### layout2.html
All pages except the "login" and "register" pages extend this layout template, which itself extends the "layout.html" template.
This one is responsible for adding the navbar to all the pages that extend it. 

&nbsp;

- ### login.html
The default page with the "/" route. This is where you login using your email and password, or click on the register button to be redirected toward the register page if you don't have an account yet.
If I had to redo it, I would probably change this route to "/login" and make the "/homepage" route the default "/" route instead.

&nbsp;

- ### register.html
The page where you go to create an account, you will be asked to provide a first name, a last name, an email address, and a password, which you need to confirm by typing it a second time.
You will be redirected to the login page upon successful completion of the form.

&nbsp;

- ### homepage.html
The page where are displayed your events for the day, as well as all the events for this week and the next one.
It took me a long time to decide how I was going to display the "calendar" part of my application, and after some time weighing different options such as "js fullcalendar" amongst others. I decided to make my own, simpler system, albeit much more basic of course, in order to start working on the core features as soon as I could.
The page retrieves all the events for this week and the next one from the database, and also gets from the backend a list of the days of the week, as well as all the correct dates for these two weeks.
The current week will always be displayed from Monday to Sunday no matter what the current day is. This is executed in the homepage route's function, which calculates the position of the current day of the week in a week (0 for Monday, 1 for Tuesday, etc...), then calculates what days need to come before and after based on that number as well as their respective dates.
Then for the second week, we only need to start where the first week ends.

&nbsp;

- ### availability.html
Each user can define what time their availability starts every day as well as what time it ends, and if they wish to, add a breaktime somewhere in the middle.
By default each user starts with a day that starts at 08:00am and ends at 06:00pm, with no predefined breaktime.
The way it is stored in the database is the following :
In the table called constraints, 3 rows will be added, one with a start time of 00:00 and an end time corresponding to the day start time of the user (08:00 by default), another with a start time corresponding to the day end time of the user (18:00 by default), and finally, if the user defined a breaktime, one last row with the start time and the end time of this breaktime.

&nbsp;

- ### manage.html
The template for the "manage calendar" page, where users can add or delete events.

&nbsp;

- ### contacts.html
The page where you can add contacts by email, view your contact list, as well as view the contact requests you have received.
You can click on "view availability" for any of your contacts, and you will be redirected to this user's "{{user_email}}'s availabiliy" page, more on that in the next bulletpoint.
You can also accept or refuse contact requests on this page.

&nbsp;

- ### contact_availability.html
This is the template for the page where you can view the availability of a selected contact for the next 15 days, starting from the current day. To access this page, you need to click "view availability" on one of your contacts on the "contacts" page.
A user's availability is calculated by combining for each day, the user's events as well as the user's constraints (day start, day end, and breaktime if any), then finding the gaps inbetween them if there are any.

&nbsp;

- ### styles.css
My custom stylesheet, nothing special to say about it, I used bootstrap for most of the layout, the navbar, as well as to style the forms.
I used the very convenient website https://coolors.co/ to create a color palette.
Something you'll notice if you check my css out, is that I'm quite the hsl guy, a system far superior to the rgb one ;).

&nbsp;

- ### bookme.db
My sqlite database, which I interact wiht using the python built in sqlite3 module.
This database contains the following tables :
- users
- events
- contacts
- requests (for unanswered contact requests)
- constraints (for users' personal availability constraints (see "availability.html" above))

Here is the full schema of the database :

> CREATE TABLE users (id INTEGER,  email TEXT NOT NULL UNIQUE, first_name TEXT NOT NULL, last_name TEXT NOT NULL, hash TEXT NOT NULL, PRIMARY KEY(id));


>CREATE TABLE events (e_id INTEGER, user_id INTEGER NOT NULL, e_date TEXT NOT NULL, e_start TEXT NOT NULL, e_end TEXT NOT NULL , e_description TEXT NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id), PRIMARY KEY(e_id));


>CREATE TABLE constraints (user_id INTEGER NOT NULL, c_start TEXT NOT NULL , c_end TEXT NOT NULL, C_type TEXT NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id));

Notes for above : c_type can have 3 possible values : "day_start", "day_end", or "break_time"


>CREATE TABLE requests (r_id INTEGER NOT NULL, user_email TEXT NOT NULL, contact_email TEXT NOT NULL, FOREIGN KEY (user_email) REFERENCES users(email), FOREIGN KEY (contact_email) REFERENCES users(email), PRIMARY KEY(r_id));

Notes for above : user_email corresponds to the email of the user who sent the request, while contact_email corresponds to the email of the user who received it


>CREATE TABLE contacts (user_email TEXT NOT NULL, contact_email TEXT NOT NULL, FOREIGN KEY (user_email) REFERENCES users(email), FOREIGN KEY (contact_email) REFERENCES users(email));

&nbsp;

---

&nbsp;

## **Potential problems, limitations, shortcomings**

&nbsp;

As it stands now, the application has a lot of room for improvement as well as several serious limitations, here are the most obvious ones :

- Time zones aren't taken into consideration as of today.
- The way events are currently handled, it is difficult to have an event start on one day and end on the next day, or at least it is only possible if doing it with two separate events.
- On the manage page, coming and past events don't take the current time into consideration.
- Impossible to change the password for the moment.
- potential security risks (maybe ?) when receiving data from the requests accept/delete form, would be good to add some additional checking on the server side (make sure that the id of the accepted or refused request corresponds to one of the requests received by the current user's email).
- There needs to be the possibility to define days where you aren't available and not just hours.
- It is currently impossible to go forwards or backward in the weeks of the calendars.

&nbsp;

---

&nbsp;

## **Room for improvement, additional features, etc...**

&nbsp;

- The most essential component that is currently missing : The ability to book appointments with other users based on their availability. I didn't have the time to implement this feature due to personal time constraints, but I'd like to keep working on the project and add this feature in the near future, it's very easy to do.
- Make it possible to change your password or user info.
- Make it possible to remove a contact.
- Send an email after registration to ask the user to confirm their email address.
- Make it impossible to pick times which are not rounded to 0 or 5 (ex : 15:37, 08:52, etc...)
- Possibility to make an event repeatable.
- Highlight the current day on the homepage
- Add flash alerts instead when the user performs certain actions such as completing a form.
- Handle form completion errors directly on the page rather than redirecting to an empty page with an error message.
- Probably the most important limitation of all that needs to be fixed, is the unability to move towards the future or the past in the calendar in order to view other weeks.
- And in relation to that, add the possility to display the calendar view on a daily, weekly, or monthly scale.

&nbsp;

---

&nbsp;

## **Challenges, and what I've learned in the process**

&nbsp;

I have learned a lot while building this app, and not just on the technical side of things, but also about planning, design, motivation, research, scope management, work organisation, etc...

&nbsp;

### A real IDE
My first challenge was to move from the CS50 IDE.
I started this project during CS50 2021 and up to that point I had been using it for all the problem sets and labs of the course, but I decided it was time to remove all the training wheels and start working directly on my computer on a "real" IDE.
I first downloaded Visual Studio, and feeling overwhelmed, I quickly decided to install VS Code instead.
I then had to learn how to set up my project, install extentions, set up a virtual environment, pip install some modules, familiarize myself with VS Code, etc...
Setting up the project took me a good ammount of time and research.

&nbsp;

### Calendar display
My second challenge was about displaying the calendar, because I knew this was going to be paramount for this type of application, but I was intimidated by tools such as "js fullcalendar", so instead, after a bit of time hesitating and thinking about this, I decided to take a more basic and simple approach in order to get the project going.

&nbsp;

### Project management and work organization
Something I quickly realised, is that things can get messy pretty quickly if you don't plan well or proceed step by step with specific goals for what you want to do when you work... 
You start building a route, then realise you need to modify a table in your database to add a column, but then you realise that one of your html template needs to take this new column into consideration because there's a form related to it there, and before you know it you're working on 10 different places in your project at the same time, with some left unfinished.
S.m.a.r.t goals are your friends. 

&nbsp;

### Managing scope, features, and time
Sometimes it seems like there is alway something to be added, something to change, to improve, and that nothing is ever complete, optimized, or perfectly implemented, and it quickly became cleat that I was going to have to cut down on a number of features and nice touches if I wanted to finish my project in time.
In the end, even while doing so, I didn't make it before the CS50 2021 deadline. But I learned never to underestimate the amount of time one needs to build such a project, not to be too greedy with additional features, and that detailed, specific planning is key.
As a quote I like goes "Failing to plan is planning to fail." 

&nbsp;

----

&nbsp;

## **Thanks**

&nbsp;

I'd like to thank the CS50 and edx team for this excellent course, I can now thanks to all of you envision a future where I can fulfill my dream of being a software developper as well as a digital nomad. 
I look back on my first scratch project, and I realize how much I have been able to progress since then, to the point where I am now, writing these lines after having created from zero (from scratch, pun intended) my very own first web application using several languages and a framework while using a real IDE, and having learned so much in the process.
Thanks from France.

&nbsp;

---

&nbsp;

Yoann GRUDZIEN 2022-01-11

