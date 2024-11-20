import sys
import sqlite3
import contextlib

DATABASE_URL = 'file:reg.sqlite?mode=ro'
ERROR_MSG = (
    "A server error occured. "
    "Please contact the system administrator."
    )

# handle escape chars
def handle_special_characters(query):
    """Function to place the escape character in front of % and _"""
    return query.replace('%', r'\%').replace('_', r'\_')

# find classes
def search_database(cursor, query):
    """
    Generates the desire query string with the command line inputs
    Executes the query and prints its contents
    """
    stmt_str = 'SELECT * FROM courses, classes, crosslistings'
    stmt_str += ' WHERE classes.courseid = crosslistings.courseid'
    stmt_str += ' AND crosslistings.courseid = courses.courseid'
    stmt_str += ' AND crosslistings.dept LIKE ?'
    stmt_str += ' AND crosslistings.coursenum LIKE ?'
    stmt_str += ' AND courses.area LIKE ? AND courses.title LIKE ?'
    stmt_str += " ESCAPE '\\'"
    stmt_str += ' ORDER BY crosslistings.dept,'
    stmt_str += ' crosslistings.coursenum,classes.classid'

    words = ['%' for i in range(4)]
    if query["dept"] is not None:
        words[0] = f'%{query["dept"]}%'
    if query["coursenum"] is not None:
        words[1] = f'%{query["coursenum"]}%'
    if query["area"] is not None:
        words[2] = f'%{query["area"]}%'
    if query["title"] is not None:
        words[3] = f'%{handle_special_characters(query["title"])}%'

    cursor.execute(stmt_str, words)

    table = cursor.fetchall()

    courses = []

    for row in table:
        classid, dept, crs = row[5], row[13], row[14]
        area, title = row[1], row[2]
        courses.append({'classid':classid,
                        'dept':dept,
                        'coursenum':crs,
                        'area':area,
                        'title':title})

    return [True, courses]

#-------------------------------------------------------------#
# COURSE DETAILS
def get_profs(cursor, classid):
    cursor.execute(
    '''
    SELECT * 
    FROM classes, coursesprofs, profs 
    WHERE classes.classid = ? 
    AND classes.courseid = coursesprofs.courseid
    AND coursesprofs.profid = profs.profid 
    ORDER BY profs.profname ASC
    ''',
    [str(classid)])
    prof_rows = cursor.fetchall()
    # print(prof_rows)

    profnames = []
    if len(prof_rows) != 0:
        for prof in prof_rows:
            profnames.append(prof[-1])
    return profnames

# throwing exception for invalid classid
def check_class_id(cursor, classid):
    cursor.execute('''SELECT * FROM classes
                WHERE classes.classid = ?''', [str(classid)])
    table = cursor.fetchall()

    if len(table) == 0:
        error_str = f'no class with classid {classid} exists'
        return error_str
    return []


# return format for the details of the course
def class_details(cursor, classid):
    merge_condition = (
    'AND classes.courseid = crosslistings.courseid '
    'AND crosslistings.courseid = courses.courseid '
    'ORDER BY crosslistings.dept, crosslistings.coursenum')

    stmt = (
    'SELECT * FROM classes, courses, crosslistings '
    'WHERE classes.classid = ? ' 
    + merge_condition)

    if classid == '':
        return [False, "missing classid"]
    elif classid == None:
        return [False, "missing classid"]

    try:
        classid = int(classid)
    except Exception:
        return [False, "non-integer classid"]

    error_msg = check_class_id(cursor, classid)
    if len(error_msg) != 0:
        return [False, error_msg]

    cursor.execute(stmt, [str(classid)])
    table = cursor.fetchall()

    first_row = table[0]

    deptcoursenums = []

    for row in table:
        deptcoursenums.append({'dept': row[13],
                               'coursenum': str(row[14])})

    profs = get_profs(cursor, classid)

    courses_dict = {'classid':int(first_row[0]), 'days':first_row[2],
                    'starttime':first_row[3], 'endtime':first_row[4], 
                    'bldg':first_row[5], 'roomnum': first_row[6], 
                    'courseid':int(first_row[1]), 
                    'deptcoursenums': deptcoursenums,
                    'area': first_row[8],
                    'title': first_row[9], 'descrip': first_row[10], 
                    'prereqs': first_row[11], 'profnames': profs
                    }

    return [True, courses_dict]

#-------------------------------------------------------------#

def get_class_overviews(query):
    try:
        with sqlite3.connect(
                DATABASE_URL,
                isolation_level=None,
                uri=True) as connection:

            with contextlib.closing(connection.cursor()) as cursor:

                # handle client request
                output = search_database(cursor, query)
                return output

    except Exception as ex:
        print(f'{sys.argv[0]}: {ex}', file=sys.stderr)
        return [False, ERROR_MSG]


def get_class_details(class_id):
    try:
        with sqlite3.connect(
                DATABASE_URL,
                isolation_level=None,
                uri=True) as connection:

            with contextlib.closing(connection.cursor()) as cursor:

                # handle client request
                output = class_details(cursor, class_id)
                return output

    except Exception as ex:
        print(f'{sys.argv[0]}: {ex}', file=sys.stderr)
        return [False, ERROR_MSG]
