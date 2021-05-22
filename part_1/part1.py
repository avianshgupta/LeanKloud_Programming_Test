from flask import Flask, request, redirect, jsonify
from flask_restplus import Api, Resource, fields
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import date, datetime, timedelta
import mysql.connector
import enum
from functools import wraps
import jwt

class EnumStatus(enum.Enum):
    '''Enumeration for task Status'''
    not_started = 'Not started'
    in_progress = 'In progress'
    finished = 'Finished'


insert_query = "insert into tasks(task, due, status) values(%s,%s,%s)"
update_query = "update tasks set task=%s, due=%s, status=%s where id=%s"
delete_query = "delete from tasks where id=%s"
params = [('Build an API', '2021-05-12', 'Not started'), ('?????', '2021-05-24', 'Finished'), ('profit!', '2021-06-06', 'Finished')]

# database connection and creation
try:
    db = mysql.connector.connect(host="localhost", username="root", password="@Gmail123", database="taskdb")
    data_c = db.cursor()
except:
    db = mysql.connector.connect(host="localhost", username="root", password="@Gmail123")
    data_c = db.cursor()
    data_c.execute('create database taskdb')
    data_c.execute('use taskdb')
    data_c.execute('create table tasks(id int PRIMARY KEY AUTO_INCREMENT, task varchar(100),due date,status varchar(20));')
    data_c.execute('create table users(uid varchar(200) PRIMARY KEY, permission varchar(10));')
    data_c.executemany(insert_query, params)
    db.commit()
    
def convtToEnum(s):
    '''
    Input: string s
    Output: equivalent enumeration
    '''
    for name in EnumStatus:
        if name.value == s:
            return name
    return -1

def getTasks():
    '''retrieves the tasks form the database and returns a list of task objects along with the id of last task'''
    tasks = []
    data_c.execute('select * from tasks')
    ct = 0
    for i in data_c:
        tasks.append({'id': i[0], 'task': i[1], 'due': i[2], 'status': convtToEnum(i[3])})
        ct = i[0]
    # print(tasks)
    return tasks, ct


authorizations = {
    'apikey': {
        'type' : 'apiKey',
        'in' : 'header',
        'name' : 'X-API-KEY'
    }
}

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='TodoMVC API',
    description='A simple TodoMVC API',  authorizations=authorizations
)
app.config['SECRET_KEY'] = 'mysecretkey'

def readPermission(f):
    '''For providing read access to the user'''
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']
        if not token:
            return {'message': 'User ID not found'}, 401
        data_c.execute("select * from users where uid=%s", (token,))
        user = data_c.fetchall()
        if len(user) == 0:
            return {'message': 'Access Denied',
                    'error': 'user with id {} NOT FOUND'.format(token)}, 401
        return f(*args, **kwargs)
    return decorated

def writePermission(f):
    '''For providing write access to the user'''
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']
        if not token:
            return {'message': 'User ID not found'}, 401
        data_c.execute("select * from users where uid=%s", (token,))
        user = data_c.fetchall()
        # print("->", user)
        if len(user) == 0 or (len(user) == 1 and user[0][1] != 'write'):
                return {'message': 'Access Denied'}, 403
        return f(*args, **kwargs)
    return decorated

ns = api.namespace('todos', description='TODO operations')
apitoken = api.namespace('generateToken', description='Generate API token')

todo = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'task': fields.String(required=True, description='The task details'),
    'due': fields.Date(required=True, description='when this task should be finished'),
    'status': fields.String(required=True, description='The task status(Not started, In progress, Finished)', enum=[name.value for name in EnumStatus], attribute='status.value')
})


class TodoDAO(object):
    def __init__(self): 
        self.todos, self.counter = getTasks()

    def get(self, id):
        '''
        Input: id
        Output: todo object corresponding to the identifier
        '''
        for todo in self.todos:
            if todo['id'] == id:
                return todo
        api.abort(404, "Todo {} doesn't exist".format(id))

    def create(self, data):
        '''
        create a toda with the given data and add it to the database
        '''
        todo = data
        enumval = convtToEnum(data['status'])
        if enumval != -1:
            todo['status'] = enumval
            todo['id'] = self.counter = self.counter + 1
            self.todos.append(todo)
            param = (data['task'], data['due'], enumval.value)
            data_c.execute(insert_query, param)
            db.commit()
            return todo
        api.abort(404, "Invalid status {}".format(data['status']))

    def update(self, id, data):
        '''
        update the todo corresponding to the identifier given
        '''
        todo = self.get(id)
        enumval = convtToEnum(data['status'])
        if enumval != -1:
            todo['status'] = enumval
            todo.update(data)
            param = (data['task'], data['due'], enumval.value, id)
            data_c.execute(update_query, param)
            db.commit()
            return todo
        api.abort(404, "Invalid status {}".format(data['status']))
        return None

    def delete(self, id):
        '''
        delete the todo corresponding to the identifier
        '''
        todo = self.get(id)
        self.todos.remove(todo)
        self.counter -= 1
        data_c.execute(delete_query, (id,))
        db.commit()
    
    
    def get_finished_task(self):
        '''
        returns a list of todos that are finished
        '''
        fin = []
        for todo in self.todos:
            if todo['status'] == EnumStatus.finished:
                fin.append(todo)
        return fin

    def convt_to_date(self, d):
        '''
        Input: date string(d)
        Output: date object
        '''
        nd = list(map(int,d.split('-')))
        return date(nd[0], nd[1], nd[2])

    def get_overdue_task(self):
        '''
        returns a list of tasks that are overdue
        '''
        overdue = []
        for todo in self.todos:
            if (todo['status'] == EnumStatus.in_progress or todo['status'] == EnumStatus.not_started) and date.today() > todo['due']: #self.convt_to_date(todo['due']):
                overdue.append(todo)
        return overdue
    
    def get_task_by_duedate(self, dd):
        '''
        Input: due_date
        Output: list of tasks corresponding to the due date
        '''
        tasks = []
        for todo in self.todos:
            if (todo['due'] == self.convt_to_date(dd)):
                tasks.append(todo)
        return tasks


@apitoken.route('/')
class TokenGenerator(Resource):
    '''Generates the  API token'''
    @apitoken.param('username','Username',_in='query',required=True)
    @apitoken.param('password','Password',_in='query',required=True)
    @apitoken.param('permission','Permission',_in='query',required=True, enum=['read', 'write'])
    def get(self):
        data = request.args
        token = jwt.encode({'user': data['username'], 'exp': datetime.utcnow() + timedelta(minutes=30)}, app.config['SECRET_KEY'])
        data_c.execute('insert into users values(%s,%s)', (token.decode('UTF-8'), data['permission']))
        db.commit()
        return jsonify({'token': token.decode('UTF-8')})


DAO = TodoDAO()

@ns.route('/')
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''
    @api.doc(security='apikey')
    @readPermission
    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all tasks'''
        return DAO.todos

    @api.doc(security='apikey')
    @writePermission
    @ns.doc('create_todo')
    @ns.expect(todo)
    @ns.marshal_with(todo, code=201)
    def post(self):
        '''Create a new task'''
        return DAO.create(api.payload), 201


@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class Todo(Resource):
    '''Show a single todo item and lets you delete them'''
    @api.doc(security='apikey')
    @readPermission
    @ns.doc('get_todo')
    @ns.marshal_with(todo)
    def get(self, id):
        '''Fetch a given resource'''
        return DAO.get(id)

    @api.doc(security='apikey')
    @writePermission
    @ns.doc('delete_todo')
    @ns.response(204, 'Todo deleted')
    def delete(self, id):
        '''Delete a task given its identifier'''
        DAO.delete(id)
        return '', 204

    @api.doc(security='apikey')
    @writePermission
    @ns.doc('update_todo_status')
    @ns.response(204, 'status updated')
    @ns.param('status','Task Status',_in='query',required=True, enum=[name.value for name in EnumStatus])
    @ns.marshal_with(todo)
    def post(self, id):
        '''Update status of task given its identifier'''
        data = request.args
        todo = DAO.get(id)
        todo['status'] = data['status']
        return DAO.update(id, todo)

    @api.doc(security='apikey')
    @writePermission
    @ns.expect(todo)
    @ns.marshal_with(todo)
    def put(self, id):
        '''Update a task given its identifier'''
        return DAO.update(id, api.payload)

@ns.route('/overdue')
class OverdueList(Resource):
    '''Shows a list of all overdue todos'''
    @api.doc(security='apikey')
    @readPermission
    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all overdue tasks'''
        return DAO.get_overdue_task()


@ns.route('/finished')
class FinishedList(Resource):
    '''Shows a list of all finished todos'''
    @api.doc(security='apikey')
    @readPermission
    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all finished tasks'''
        return DAO.get_finished_task()


@ns.route('/due')
class dueList(Resource):
    '''Shows a list of tasks which are due to be finished on that specified date'''
    @api.doc(security='apikey')
    @readPermission
    @ns.doc('list_todos')
    @ns.param('due_date','Due Date',_in='query',required=True)
    @ns.marshal_list_with(todo)
    def get(self):
        '''List of tasks which are due to be finished on that specified date'''
        date = request.args
        if 'due_date' in date:
            return DAO.get_task_by_duedate(date['due_date'])


if __name__ == '__main__':
    app.run(debug=True)