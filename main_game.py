from geopy import distance
import random

from database_connection import connection
'''
create a file called "database_connection.py" in the same folder as this file 
and add the following with your database information
---------------------------------------------------------------
import mysql.connector

connection = mysql.connector.connect(
         host='127.0.0.1',
         port='3306',
         database='',
         user='',
         password='',
         autocommit=True
         )
---------------------------------------------------------------
'''

def rng_seed():
    return random.randint(1, 10)

def airport_location(icao):
    sql = f"select name, latitude_deg, longitude_deg from airport where ident = %s and iso_country = 'FI'"
    cursor = connection.cursor()
    cursor.execute(sql, (icao,))
    result = cursor.fetchall()
    return result[0]
    # fetches airport name and location coordinates with icao code into a tuple inside a list with one item
    # so we return the tuple from the list
    # ONLY AIRPORTS IN FINLAND !!!!

def distance_check(icao):
    sql = f"select ident, name, type from airport where iso_country = 'FI' and type in ('small_airport','medium_airport', 'large_airport')"
    # take all *_airport in finland
    current_location = airport_location(icao)
    cursor = connection.cursor()
    cursor.execute(sql)
    all_airports = cursor.fetchall()
    # take note of current location and fetch EVERY *_airport

    possible_airports = []
    # create empty list for all possible airports

    for possible_airport in all_airports:
        test_location = airport_location(possible_airport[0])
        test_location_coordinates = test_location[1], test_location[2]
        current_location_coordinates = current_location[1], current_location[2]
        if distance.distance(current_location_coordinates, test_location_coordinates).kilometers < possible_flight:
            possible_airports.append(possible_airport)
    # i changed location to also return the name so it broke a bunch of stuff. this works, though

    return possible_airports

def fly(target_airport):
    new_location = airport_location(target_airport)
    if new_location == []:
        print("invalid icao code")
        return
    # check if target airport exists

    new_location_coords = new_location[1], new_location[2]
    current_location_coords = current_location[1], current_location[2]
    # i don't know how to us geopy the "right way" so just convert tuple into new tuple. probably bad

    new_distance = distance.distance(new_location_coords, current_location_coords).km
    print(current_location_coords)
    if new_distance < possible_flight:
        return new_location, new_distance
    # make sure flight is actually possible with distance limit

    else:
        return "too far"
    # flight not possible!

def choose_delivery_task():
    sql = f"select ident, name, type from airport where iso_country = 'FI' and type in ('small_airport','medium_airport', 'large_airport')"
    # take all *_airport in finland
    cursor = connection.cursor()
    cursor.execute(sql)
    all_airports = cursor.fetchall()
    # return all those airports to list
    random.shuffle(all_airports)
    random_airport = all_airports[0]
    if random_airport == current_location:
        print("oops")
        return
        # temporary, happens when delivery task is in same airport as the player is in
    else:
        return random_airport

def complete_delivery():
    print("delivery complete!")
    return

def start_delivery_task():
    print(f"new delivery task! deliver package to {delivery_target_airport}")
    while True:
        user_accept_delivery_task = input("accept task? yes/no\n")
        if user_accept_delivery_task == "yes":
            print("delivery task accepted")
            return True
        elif user_accept_delivery_task == "no":
            print("delivery task not accepted")
            return False
        else:
            print("invalid input")


possible_flight = 1000
current_day = 0
total_distance = 0
live = False
on_delivery_task = False
current_location = []
airport = []
delivery_target_airport = []
# create variables and lists, possibly better ways of doing it all

while not live:
    airport = input("icao of airport? ").upper()
    current_location = airport_location(airport)
    print(current_location)
    # temporary
    if current_location == []:
        print("invalid icao")
    else:
        live = True
# before actual gameplay starts, choose starting airport and check if it's real

while live:
    if not on_delivery_task:
        delivery_target = choose_delivery_task()
        if delivery_target == []:
            print("target same as current airport")
        delivery_target_airport = delivery_target[0]

    if delivery_target_airport == airport:
        complete_delivery()
        on_delivery_task = False
    # check if at delivery target

    print(f"you are at {current_location[0]} ({airport})")
    print(f"you have flown {total_distance:.2f} km")
    print(f"you are on day {current_day}")

    if rng_seed() > 8 and not on_delivery_task:
        delivery_task_start = start_delivery_task()
        if delivery_task_start:
            on_delivery_task = True
    # rng_seed() returns an integer between 1 and 10
    # if that is 9 or 10 (20% chance) give player ability to start delivery task

    if on_delivery_task:
        print(f"you have a delivery to {delivery_target_airport}")

    action = input("What do you want to do? Options: fly, check, quit, wait ")

    if action == "fly":
        new_airport = input("icao of airport? ").upper()
        new_flight = fly(new_airport)
        # start flight operation. returns (location tuple (name, coordinates) and distance) in a tuple

        if new_flight == None:
            print("invalid icao code")
        # target airport does not exist
        elif new_flight == "too far":
            print("distance too long")
        # target airport too far

        else:
            total_distance = new_flight[1] + total_distance
            current_location = new_flight[0]
            airport = new_airport
            current_day += 1
        # add flown distance to total, make new location the current location, and add a day to counter

    elif action == "check":
        for possible_airport in distance_check(airport):
            print(f"{possible_airport[1]}, ICAO code: {possible_airport[0]}, Type: {possible_airport[2]}")
    # distance_check function returns list of all airports you can fly to inside "possible_flight" variable
    # then print every possible airport inside that list

    elif action == "wait":
        current_day += 1
        # track how many "days" have gone by

    elif action == "quit":
        print(f"you flew {total_distance:.2f} km in {current_day} days!")
        break