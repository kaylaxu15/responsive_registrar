import flask
from flask import Flask, render_template
import database

app = Flask(__name__, template_folder='.')

def get_prior_request():
    prev_dept = flask.request.cookies.get('prev_dept')
    prev_dept = '' if prev_dept is None else prev_dept

    prev_num = flask.request.cookies.get('prev_num')
    prev_num = '' if prev_num is None else prev_num

    prev_area = flask.request.cookies.get('prev_area')
    prev_area  = '' if prev_area is None else prev_area

    prev_title = flask.request.cookies.get('prev_title')
    if prev_title is None:
        prev_title = ''

    prev_query = {'coursenum':prev_num, 'dept':prev_dept,
             'area':prev_area,'title':prev_title} 
    return prev_query

@app.route('/', methods=['GET'])
@app.route('/?', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
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

    
    # get the last search's data
    prev_query = get_prior_request()
    if courses is None:
        return render_template(
            'errordetails.html',
            error='''A server error occurred.
             Please contact the system administrator.''')
    if courses[0] is False:
        return render_template('errordetails.html', error=courses[1])
    return render_template(
        'searchresults.html',
        courses=courses,
        prev_query=prev_query)

# display the class details when you click on class ID
@app.route('/regdetails', methods=['GET'])
def reg_details():
    classid = flask.request.args.get('classid')

    if classid == "":
        return render_template(
            'errordetails.html',
            error="missing classid")

    try:
        classid = int(classid)
    except ValueError:
        return render_template(
            'errordetails.html',
            error="non-integer classid")

    # get last search data for the go back button
    prev_query = get_prior_request()

    class_details = database.get_class_details(classid)

    try:
        if class_details is None:
            return render_template(
                'errordetails.html',
                error='''A server error occurred.
                 Please contact the system administrator.''')
        if class_details[0] is False:
            return render_template(
                'errordetails.html',
                error=class_details[1])
        return render_template(
            'classdetails.html',
            classid=classid,
            class_details=class_details,
            prev_query=prev_query)
    except KeyError:
        return render_template(
            'classdetails.html',
            classid=classid,
            class_details=class_details,
            prev_query=prev_query)


@app.route('/classoverviews', methods=['GET'])
def class_overviews():
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

    html_code = render_template(
        'searchresults.html',
        courses=courses,
        prev_query=query)
    response = flask.make_response(html_code)
    response.set_cookie('prev_dept', dept)
    response.set_cookie('prev_num', num)
    response.set_cookie('prev_area', area)
    response.set_cookie('prev_title', title)
    return response
