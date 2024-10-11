from geopy import distance
import random
import mysql.connector

connection = mysql.connector.connect(
         host='localhost',
         port='3306',
         database='flight_game_final',
         user='root',
         password='',
         autocommit=True
         )

def welcome():
    # instead of asking to start new game or load game, only ask for username and check if it's already used
    print(" _   _               _ _        _____ _ _       _     _   \n| \ | | ___  _ __ __| (_) ___  |  ___| (_) __ _| |__ | |_ \n|  \| |/ _ \| '__/ _` | |/ __| | |_  | | |/ _` | '_ \| __|\n| |\  | (_) | | | (_| | | (__  |  _| | | | (_| | | | | |_ \n|_|_\_|\___/|_|  \__,_|_|\___| |_|   |_|_|\__, |_| |_|\__|\n/ ___|(_)_ __ ___  _   _| | __ _| |_ ___  |___/           \n\___ \| | '_ ` _ \| | | | |/ _` | __/ _ \| '__|           \n ___) | | | | | | | |_| | | (_| | || (_) | |              \n|____/|_|_| |_| |_|\__,_|_|\__,_|\__\___/|_|              ")
    print("Welcome to Nordic Flight Simulator! This beta version does not represent the final quality.")
    play_choice = input("Enter your username: ")
    return play_choice

def select_country():
    sql = f"select name from country where name in {'norway','finland','sweden','denmark'}"
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    country_list = []
    for i in result:
        print(i[0])
    for country in result:
        country_list.append(country[0].lower())
    while True:
        country = input("Please select a country:").lower()
        if country in country_list:
            return country
        else:
            print("invalid country")

def select_airport(country): #retreive all the available airports in the country the player located
    sql = f"select name from airport where iso_country = (select iso_country from country where name = '{country}' and type in ('large_airport','medium_airport'))"
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    num = 1
    for i in result:
        print(f'[{num}]: {i[0]}')
        num += 1
    return airport_selector_code_with_int_and_input(result)

def airport_selector_code_with_int_and_input(result):
    # instead of doing int(input, use this function to select airport while making sure the code does not error out
    while True:
        airport_str = input("Please select an airport:")
        if airport_str.isnumeric():
            airport_int = int(airport_str)
            if 0 < airport_int <= len(result):
                airport = result[airport_int - 1][0]
                return airport
            else:
                print("invalid input")
        else:
            print("invalid input")

def select_airport_in_game(country, location, fuel): #retreive all the available airports in the country the player located
    # but do it while in game, showing the needed fuel point count to fly to that airport
    sql = f"select name from airport where iso_country = (select iso_country from country where name = '{country}' and type in ('large_airport','medium_airport'))"
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    num = 1
    new_airport_list = []
    for thing in result:
        new_airport_list.append(thing[0])
    for airport in new_airport_list:
        airport_distance = distance_calculator(location, airport)
        need_fuel_point = calculate_fuel(airport_distance)
        print(f'[{num}]: {airport} (Needed fuel points: {need_fuel_point})')
        num += 1
    print(f"You have {fuel} fuel points.")
    return airport_selector_code_with_int_and_input(result)

def calculate_fuel(airport_distance):
    fuel_reduction = 1 - (check_fuel_reduction(name) / 100)
    need_fuel_point = airport_distance * fuel_reduction
    return int(need_fuel_point / 100)

def create_name():
    name = input("Please input the name you want to appear in the game:")
    repeat = check_name_repeat(name)
    while repeat != 0:
        name = input("This username has been taken. Please try again.:")
        repeat = check_name_repeat(name)
    return name

def check_name_repeat(name): #check if the name has already been taken
    sql = f"select player_name from player"
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    repeat = 0
    for i in result:
        if name in i.values():
            repeat = 1
    return repeat

def create_new_player(name,money,fuel):
    sql = f"INSERT INTO player (player_name, money, fuel_points) VALUES ('{name}',{money},{fuel})"
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql)

def distance_calculator(departure,arrival): #calculate and return the distance between the two airport
    departure = get_location_by_name(departure)
    arrival = get_location_by_name(arrival)
    airport_distance = int(distance.distance(departure,arrival).km)
    return airport_distance

def get_location_by_name(airport_name):
  sql= f"SELECT latitude_deg,longitude_deg FROM airport where name = '{airport_name}'"
  cursor = connection.cursor(dictionary=True)
  cursor.execute(sql)
  result = cursor.fetchone()
  latitude = result['latitude_deg']
  longitude = result['longitude_deg']
  airport = (latitude, longitude)
  return airport

def load_save(name):
    # using the load_save function to both load old game data and create new save file based on if name is in database
    sql = f"SELECT * FROM player where player_name = '{name}'"
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchone()
    if result is None:
        print('Save file not found! Starting new game.')
        print(f'Hi {name}, now you will choose your initial starting point.')
        start_country = select_country()
        start_airport = select_airport(start_country)
        money = 600
        fuel = 0
        create_new_player(name, money, fuel)
        print('Great! Now you are here. You can choose the thing you want to do by input the number.')
        start_game(money, fuel, start_airport, name)
    else:
        print('save file found!')
        print(result)
        money = result['money']
        fuel = result['fuel_points']
        location = result['location']
        start_game(money, fuel, location, name)

def start_game(money,fuel,location,name): #The main game program
    choice = input('\n[1]Start transport mission\n[2]Upgrading aircraft\n[3]Save game\n[4]Check your status\nChoose Things to Do:')
    if choice == '1':
        money,total_value = purchase_goods(money,location,name)
        print('The purchase of goods has been completed!')
        start_flight(money, fuel, location, name, total_value)

    elif choice == '2':
        money = purchase_upgrade(money,name)

    elif choice == '3':
        save_game(money, fuel, location, name)

    elif choice == '4':
        print(f'name:{name}; money:{money}; fuel:{fuel}; current location:{location}')

    start_game(money, fuel, location, name)

def save_game(money, fuel, location, name): #save the game data to the database
    sql = f"update player set money = {money}, fuel_points = {fuel}, location = '{location}' where player_name = '{name}'"
    cursor = connection.cursor()
    cursor.execute(sql)
    print('\nGame has been saved!')

def start_flight(money,fuel,location,name,total_value): #Move to another airport and calculate the earned money
    num = random.randint(1,6)
    if(num == 1 or num == 6):
        bonus = 10
    else: bonus = num
    print(f'\nRolled the dice, the number is {num}, you got {bonus} fuel points.')
    print('\nPlease select your flight destination.')
    fuel += bonus
    enough_fuel = False
    while not enough_fuel:
        dest_country = select_country()
        dest_airport = select_airport_in_game(dest_country, location, fuel)
        airport_distance = distance_calculator(location, dest_airport)
        need_fuel_point = calculate_fuel(airport_distance)
        if need_fuel_point == 0:
            need_fuel_point = 1
        if fuel < need_fuel_point:
            print('\nYou do not have enough fuel points!\n')
        else:
            enough_fuel = True
    total_value = total_value * (1 + airport_distance/1000)
    print(f'\nYou successfully reached your destination and earned {total_value:.0f}\n')
    money += total_value
    fuel -= need_fuel_point
    location = dest_airport
    start_game(money, fuel, location, name)

def check_fuel_reduction(name): #check the upgrade about the fuel the player have purchased
    sql = f"SELECT sum(fuel_reduction_percentage) FROM upgrade where upgrade_id in (select upgrade_id from player_upgrade where player_ID = '{get_player_ID(name)}')"
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchone()
    num = result['sum(fuel_reduction_percentage)']
    if num is None:
        num = 0
    return float(num)

def check_capacity_increase(name): #check the upgrade about the capacity the player have purchased
    sql = f"SELECT sum(capacity_increase_percentage) FROM upgrade where upgrade_id in (select upgrade_id from player_upgrade where player_ID = '{get_player_ID(name)}')"
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchone()
    num = result['sum(capacity_increase_percentage)']
    if num is None:
        num = 0
    return float(num)

def get_player_ID(name): #get player's ID by its name
    sql = f"select player_id from player where player_name = '{name}'"
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchone()
    return result['player_id']

def purchase_upgrade(money,name): #get the upgrade item from the database and check if any of them has been purchased
    choice = 0
    while choice != 'q':
        sql = f"select * from upgrade where upgrade_ID not in (select upgrade_ID from player_upgrade where player_ID = (select player_ID from player where player_name = '{name}'))"
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql)
        result = cursor.fetchall()
        num = 1
        for i in result:
            if i['type'] == '1':
                print(f'[{num}] capacity increase:{i["capacity_increase_percentage"]}; cost: {i["cost"]}')
            elif i['type'] == '2':
                print(f'[{num}] {i["fuel_reduction_percentage"]} percent reduction in fuel; cost: {i["cost"]}')
            num += 1
        choice = input('Please select the items to upgrade. Enter q to end.')
        if choice != 'q':
            choice = int(choice)
            if result[choice-1]['cost'] > money:
                print('\nYou do not have enough money!\n')
            else:
                money = money - result[choice-1]['cost']
                print(f"\nPurchase successful! You have {money} money left\n")
                sql = f"INSERT INTO player_upgrade (player_id, upgrade_id) VALUES ('{get_player_ID(name)}','{result[choice-1]['upgrade_ID']}')"
                cursor = connection.cursor()
                cursor.execute(sql)

    return money

def purchase_goods(money,location,name): #get the available goods from the database by location
    sql = f"select * from goods where goods_id in (select goods_id from goods_in_country where iso_country = (SELECT iso_country FROM airport where name = '{location}'))"
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    num = 1
    capacity = 100 + check_capacity_increase(name)
    for i in result:
        print(f'[{num}] {i["goods_name"]} weight:{i["goods_weight"]} value:{i["goods_value"]}\n')
        num += 1
    choice = 0
    total_value = 0
    while choice != 'q':
        print(f'You have {money} money and and {capacity} storage spaces left.')
        choice = input('Please select the items to purchase. Enter q to end.')
        if choice.isnumeric() and choice != 'q':
            choice = int(choice)
            if 0 < choice <= len(result):
                amount_str = input('Please enter the amount of goods:')
                if amount_str.isnumeric():
                    amount = int(amount_str)
                    value = result[choice-1]['goods_value']
                    weight = result[choice-1]['goods_weight']
                    if amount * value > money:
                        print("You don't have enough money!")
                    elif amount * weight > capacity:
                        print("You don’t have enough storage space!")
                    else:
                        total_value = amount * value + total_value
                        money = money - amount * value
                        capacity = capacity-weight*amount
                        print(f'\nPurchase successful!\n')
                else:
                    print("invalid input")
            else:
                print("invalid input")
        else:
            print("invalid input")
    return money, total_value

def start_program():
    # START THE GAME, also make name global
    global name
    name = welcome()
    load_save(name)

start_program()