import json
import flask
import database

app = flask.Flask(__name__, template_folder='.')

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return flask.send_file('searchresults.html')

@app.route('/?', methods=['GET'])
@app.route('/regoverviews', methods=['GET'])
def regoverviews():
    dept = flask.request.args.get('dept')
    if dept is None:
        dept = ''
    num = flask.request.args.get('coursenum')
    if num is None:
        num = ''
    area = flask.request.args.get('area')
    if area is None:
        area = ''
    title = flask.request.args.get('title')
    if title is None:
        title = ''

    query = {'coursenum':num, 'dept':dept,
             'area':area,'title':title}                       
    courses = database.get_class_overviews(query)

    json_doc = json.dumps(courses)
    response = flask.make_response(json_doc)
    response.headers['Content-Type'] = 'application/json'

    return response

# display the class details when you click on class ID
@app.route('/regdetails', methods=['GET'])
def reg_details():
    classid = flask.request.args.get('classid')

    class_details = database.get_class_details(classid)
    json_doc = json.dumps(class_details)
    response = flask.make_response(json_doc)
    response.headers['Content-Type'] = 'application/json'

    return response
