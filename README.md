# To-Do and Diary site
#### Video Demo:  <URL HERE>
#### Description:

My final project is a website to track your progress and record your thoughts throughout day. First you need to create an account then site automatically redirects you to that day’s diary and To-Dos. In that page you can create new To-Dos, tick them as completed or you can delete them. In settings page there is a habits tab. In that tab you can create new habits which will be added automatically to a day when you first create that day’s page. Next to To-Dos there is text area to enter your thoughts about day It saves the data every 5 seconds .If you want to change a habit or To-Do after you change it, you must press enter to save. In diary entries page you can see your old diaries, or you can create a diary for a specific day. In settings page which named as your user name. you can change your account details like email, user name, password, add and delete habits or delete your account.

## main.py
This file handles http requests from browser and java script. I used XMLHttpRequests to interact with the data in database which sends http requests to /api route of the server. I used that api approach to make the website respond to the sever without refreshing the page. I sent data to the server using header files of request which I needed to encode with encodeURIComponent function in js and decode with a urllib.parse.unquote method in server-side. 

##helpers.py
This file consists with sqlite table creation script, login require wrapper and id checkers that checks if a to-do or habit is users own.

##diary_entry.js
This file has functions for creating http requests to crate, change and delete a new todo and diary. Makes buttons and text inputs interactable without refreshing the page.

##diary_entry.html
This file has todos and diary text inputs and has the template to create new todos.

##entries.js
Makes cards on entries page clickable, delete buttons, go button work.

##entries.html
This page helps you to navigate through your diaries and go to a specific day’s diary.

##index.js
That script redirects you to today’s diary.
##settings.js
This file has functions to make tabs in settings.html work, and functions to create, delete, change habit. Has a alert function to inform user. Contains functions that sends http requests to server to change password, email, user name, and to delete account.

##settings.html
Settings page to change account details, And habits.
## layout.html
Has html code for navigation bar.

##register.html
Has a form to register a new user.

##signin.html
Has a form to sign in users.


