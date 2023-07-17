# WisdomPost
## Video Demo:  https://youtu.be/5EQwO6yET5o

## Description:

#### WisdomPost is a web application which allows users to make posts about specific topics in various different fields, allowing it to be a dynamic educational purpose, content-sharing application. Everyone can register an account, edit their profile, have a custom avatar according to their email and wether they have an account, make posts under specific categories for a specific topic, edit or delete their posts, search for posts, see who posted what or just read as a guest. It is almost a community platform too, it only lacks ability to comment, message people and attach images from your local computer, but they can obtain email of the authors and send them an email. Additional verification like email verification can be added too. All of these features can or will be implemented in future, but for now the application serves it's sole purpose as a final project.

## Under the hood: 

#### I used Python with Flask backend framework, SQLAlchemy and MySQL for the database, templates with HTML and Jinja, Javascript and JQuery for client-side to server-side code, CSS for styling those templates and a little help of Bootstrap too. Backend code and database configurational code is separated in two files (app.py and database.py), providing more transparency and tidiness of the project structure. When backend needs to perform an operation with database, methods within the database file are called instead of being mixed in with the backend code. Frontend part (templates and styles) are within 'templates' and 'static' folders. The design and layout are simple and serve their purpose, with a little help of Bootstrap the process was only a little bit sped up. Style and layout can surely be improved, but frontend is not my cup of tea so i invested what i knew and what i learned on the go. Functionality and logic behind it all was what only interested me, perhaps if i collaborated with another person and they liked to do layout and style, app would definetly look way better. It's still a full-stack application, had to invest time for both backend and frontend. 

## Things i learned:

#### Throughout the process i learned and realized many new things. What i realized was that only through projects and getting your hands dirty is the way to learn things, something i wish i realized long ago. What i learned is how to use Flask framework with Python, SQLAlchemy, refreshed my memory of HTML, learned some layout and design techniques in CSS, learned a little bit of Javascript and how to use some JQuery with it to make the pages a little bit more interactive, send POST requests with Ajax with JSON to my application, grabbing the data and responding back with jsonify library, making pagination possible to avoid overloading the pages with all the posts. Not the proudest with the design of the application, but definetly am a little bit in terms of actually learning something new and making it work under the hood. Worked on this project little over a month with little breaks to avoid burning out. As this was a final project for CS50, i did have to invest more effort and time than on all the problem sets and labs i did, but it was definetly a more enjoyable experience when learning new things on the go rather than solving problems (Tideman *cough* *cough*). This is the story of this short journey of learning and coding for several months in CS50x course, thanks to CS50 teachers for brain-friendly and playful way of learning and guidance for real-world project example.

## Things i'd recommend to beginners like me:

#### Do the real projects, avoid being stuck in tutorial hell and learning, start small, learn on the go, reflect on your past and watch how you're improving.





