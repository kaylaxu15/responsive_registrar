#-----------------------------------------------------------------------
# testreg.py
# Author: Bob Dondero
#-----------------------------------------------------------------------

import sys
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
# import shutil
# import os
# import sqlite3
# import contextlib

#-----------------------------------------------------------------------

MAX_LINE_LENGTH = 72
UNDERLINE = '-' * MAX_LINE_LENGTH

#-----------------------------------------------------------------------

def get_args():

    parser = argparse.ArgumentParser(
        description='Test the ability of the reg application to '
            + 'handle "primary" (class overviews) queries')

    parser.add_argument(
        'serverURL', metavar='serverURL', type=str,
        help='the URL of the reg application')

    parser.add_argument(
        'browser', metavar='browser', type=str,
        choices=['firefox', 'chrome'],
        help='the browser (firefox or chrome) that you want to use')

    parser.add_argument(
        'mode', metavar='mode', type=str,
        choices=['normal', 'headless'],
        help='the mode (normal or headless) that this program should '
            + 'use when interacting with Firefox; headless tells '
            + 'the browser not to display its window and so is faster')

    args = parser.parse_args()

    return (args.serverURL, args.browser, args.mode)

#-----------------------------------------------------------------------

def create_driver(browser, mode):

    if browser == 'firefox':
        try:
            options = FirefoxOptions()
            if mode == 'headless':
                options.add_argument('-headless')
            driver = webdriver.Firefox(options=options)
        except Exception:  # required if using snap firefox
            options = FirefoxOptions()
            if mode == 'headless':
                options.add_argument('-headless')
            service = FirefoxService(
                executable_path='/snap/bin/geckodriver')
            driver = webdriver.Firefox(options=options, service=service)

    else:  # browser == 'chrome'
        options = ChromeOptions()
        if mode == 'headless':
            options.add_argument('-headless')
        options.add_argument('--remote-debugging-pipe')
        driver = webdriver.Chrome(options=options)

    return driver

#-----------------------------------------------------------------------

def print_flush(message):
    print(message)
    sys.stdout.flush()

#-----------------------------------------------------------------------

def run_test(driver, input_values):

    print_flush(UNDERLINE)
    for key, value in input_values.items():
        print_flush(key + ': |' + value + '|')

    try:
        if 'dept' in input_values:
            dept_input = driver.find_element(By.ID, 'deptInput')
            dept_input.send_keys(input_values['dept'])
        if 'coursenum' in input_values:
            coursenum_input = driver.find_element(By.ID,
                'coursenumInput')
            coursenum_input.send_keys(input_values['coursenum'])
        if 'area' in input_values:
            area_input = driver.find_element(By.ID, 'areaInput')
            area_input.send_keys(input_values['area'])
        if 'title' in input_values:
            title_input = driver.find_element(By.ID, 'titleInput')
            title_input.send_keys(input_values['title'])

        submit_button = driver.find_element(By.ID, 'submitButton')
        submit_button.click()

        overviews_table = driver.find_element(By.ID, 'overviewsTable')
        print_flush(overviews_table.text)

        if 'dept' in input_values:
            dept_input = driver.find_element(By.ID, 'deptInput')
            dept_input.clear()
        if 'coursenum' in input_values:
            coursenum_input = driver.find_element(By.ID,
                'coursenumInput')
            coursenum_input.clear()
        if 'area' in input_values:
            area_input = driver.find_element(By.ID, 'areaInput')
            area_input.clear()
        if 'title' in input_values:
            title_input = driver.find_element(By.ID, 'titleInput')
            title_input.clear()
    except Exception as ex:
        print(str(ex), file=sys.stderr)

#-----------------------------------------------------------------------

def main():
    server_url, browser, mode = get_args()

    driver = create_driver(browser, mode)

    driver.get(server_url)

    # Statement Testing
    run_test(driver,{})
    run_test(driver, {'dept':'COS'})
    run_test(driver, {'coursenum':'333'})
    run_test(driver, {'coursenum':'b'})
    run_test(driver, {'area':'qr'})
    run_test(driver, {'title':'intro'})
    run_test(driver, {'dept':'science'})
    run_test(driver, {'dept':'COS', 'coursenum':'3'})
    run_test(driver,{'dept':'COS', 'coursenum':'2',
                     'area':'qr', 'title':'intro'})

    # Tests for Special Characters
    run_test(driver, {'title':'C_S'})
    run_test(driver, {'title':'c%S'})

    # Tests for Corner Cases
    run_test(driver, {'title':'Independent Study'})
    run_test(driver, {'title':'Independent Study '})
    run_test(driver, {'title':'Independent Study  '})
    run_test(driver, {'title':' Independent Study'})
    run_test(driver, {'title':'  Independent Study'})

    # Test for Cross Referenced Departments Course
    run_test(driver, {'dept':'SOC', 'coursenum':'577'})

    # Test for Long Title
    long_title = '''Topics in International Relations:
    US Diplomacy & the Other Middle East'''
    run_test(driver, {'title':long_title})

    # Test for Long Description
    run_test(driver, {'dept':'WWS', 'coursenum':'598'})

    # Test for Course with Multiple Professors
    run_test(driver, {'title':'Elementary Pesian II'})

    # Test for Class with No Professors
    run_test(driver, {'dept':'WWS', 'coursenum':'402'})

    # # Test for database errors (commented out)
    # shutil.copy('reg.sqlite', 'regbackup.sqlite')
    # os.remove('reg.sqlite')

    # # Database Missing (cannot be opened)
    # run_test(driver, {})
    # run_test(driver, {'dept':'COS'})
    # run_test(driver, {'title':'Independent Study'})

    # # Restore Database
    # shutil.copy('regbackup.sqlite', 'reg.sqlite')

    # try:
    #     with sqlite3.connect(DATABASE_URL,
    #             isolation_level=None,
    #             uri=True) as connection:
    #         # drop a table in reg.sqlite
    #         with contextlib.closing(connection.cursor()) as cursor:
    #             cursor.execute('DROP TABLE crosslistings')
    # except Exception as ex:
    #     print(f'{sys.argv[0]}: {ex}',
    #           file = sys.stderr)
    #     sys.exit(1)

    # # Tests with Database Issues
    # run_test(driver, {})
    # run_test(driver, {'dept':'COS'})
    # run_test(driver, {'title':'Independent Study'})

    # # Restore Database
    # shutil.copy('regbackup.sqlite', 'reg.sqlite')

    driver.quit()

if __name__ == '__main__':
    main()
