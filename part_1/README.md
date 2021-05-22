# Part 1

## Problem Statement

**Flask** is a framework to build web applications using python, and flask-restplus is a framework
to build RESTful APIs in flask. This example tutorial builds a Todo application (to keep
list of todos). Your task is as follows:
1. Start with the flask-restplus tutorial, and enhance it as described below. The tutorial code base must be the starting point for this exercise.
2. Implement the storage for tasks, and associated state, in a database such as sqlite or mysql. Preferably, don't use SQL Alchemy, instead, use the native DB API for that database.
3. Add 2 new fields to a task:  
  a. Due by, type date, of when this task should be finished  
  b. Status - Not started, In progress, and Finished  
4. Add or modify web methods to change the status of tasks.
5. Implement the following additional end points:  
  a. **"GET /due?due_date=yyyy-mm-dd"** - this gets a list of tasks which are due to be finished on that specified date   
  b. **"GET /overdue"** - this gets all tasks which are past their due date, as of the date this query is run   
  c. **"GET /finished"** - this gets all tasks which are finished 
6. **For extra credit**, implement authorization for this web app, with both read and write access. Users with write access can create and change the status of tasks. Users with read access can only view tasks, via the above APIs, but cannot create or modify them.
