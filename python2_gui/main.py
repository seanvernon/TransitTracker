from bus_arrival import BusArrival
from card import Card
from train_arrival import TrainArrival
from utils import COLORS, FONTS, ROUTE_ID_DICT, STATION_IDS, WIDTH

from urllib import urlopen

import datetime
import pygame
import xml.etree.ElementTree as ET

def bus_arrivals(route, stop, key):
    URL_BASE = "http://www.ctabustracker.com/bustime/api/v1/getpredictions"
    arr_xml = urlopen(URL_BASE+"?key="+key+"&rt="+route+"&stpid="+stop)
    arr_xml = ET.parse(arr_xml)

    etas = []
    for child in arr_xml.getroot():
        if child.tag == "prd":
            etas.append(child)
        elif child.tag == "error":
            return []

    arr_lst = []
    for eta in etas: 
        line = eta[6].text
        direction = eta[8].text
        destination = eta[9].text
        pred_t = convert_timestamp(eta[0].text)
        arr_t = convert_timestamp(eta[10].text)
        wait_time = int(round((arr_t - pred_t).seconds / 60))
        arr_lst.append(BusArrival(line, direction, destination, wait_time))
    return arr_lst

def train_arrivals(station, key):
    URL_BASE = "http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx"
    arr_xml = urlopen(URL_BASE+"?key="+key+"&mapid="+station)
    arr_xml = ET.parse(arr_xml)

    etas = []
    for child in arr_xml.getroot():
        if child.tag == "eta":
            etas.append(child)
        elif child.tag == "errCd":
            if child.text != "0":
                print("API Error "+child.text)
                return []

    arr_lst = []
    for eta in etas:    
        line = eta[5].text
        vin = eta[4].text
        destination = eta[7].text
        pred_t = convert_timestamp(eta[9].text)
        arr_t = convert_timestamp(eta[10].text)
        wait_time = int(round((arr_t - pred_t).seconds / 60))
        arr = TrainArrival(line, vin, destination, wait_time)
        if arr not in arr_lst:
            arr_lst.append(arr)
    return arr_lst

def convert_timestamp(api_ts):
    if len(api_ts) == 17:
        return datetime.datetime(int(api_ts[:4]), int(api_ts[4:6]), int(api_ts[6:8]),\
                                 int(api_ts[9:11]), int(api_ts[12:14]), int(api_ts[15:17]))
    else:
        return datetime.datetime(int(api_ts[:4]), int(api_ts[4:6]), int(api_ts[6:8]),\
                                 int(api_ts[9:11]), int(api_ts[12:14]))

def draw_text(display, text, x, y, size, color, bold=False):
    if bold:
        font = pygame.font.Font(FONTS["Helvetica"], size, bold=True)
    else:
        font = pygame.font.Font(FONTS["Helvetica"], size)
    text_to_screen = font.render(text, True, color, None)
    textRect = text_to_screen.get_rect()
    textRect.top = y
    textRect.left = x
    display.blit(text_to_screen, textRect)

def load_arrivals(train_key, bus_key, station_ids, route_id_dict):
    arrivals = []
    for station in station_ids:
        arrivals += train_arrivals(station, train_key)
    for route in route_id_dict:
        for stop in route_id_dict[route]:
            arrivals += bus_arrivals(route, stop, bus_key)
    return sorted(arrivals, key=lambda card:card.wait_time)

def draw_arr_text(screen, arrival, i, anchor):
    if i >= 10:
        draw_text(screen, str(i), 10, anchor + 10, 36, COLORS["White"])
    else:
        draw_text(screen, str(i), 20, anchor + 10, 36, COLORS["White"])
    draw_text(screen, arrival.info_string(), 85, anchor + 10, 36, COLORS["White"])
    draw_text(screen, arrival.destination, 80, anchor + 50, 120, COLORS["White"])
    if arrival.wait_time <= 1:
        draw_text(screen, "Due", WIDTH - 300, anchor + 30, 140, COLORS["White"], True)
    else:
        if arrival.wait_time >= 10:
            draw_text(screen, str(arrival.wait_time), WIDTH - 410, anchor + 32, 140, COLORS["White"], True)
        else:
            draw_text(screen, str(arrival.wait_time), WIDTH - 350, anchor + 32, 140, COLORS["White"], True)
        draw_text(screen, "min", WIDTH - 245, anchor + 48, 120, COLORS["White"])

def next_open_frame(screen, top_card, bottom_card, curr_top_card, arrivals):
    screen.fill(COLORS["Black"])
    sprites = pygame.sprite.Group()
    top_card_arr = arrivals[curr_top_card]
    if curr_top_card + 1 < len(arrivals):
        bottom_card_arr = arrivals[curr_top_card + 1]
    else:
        bottom_card_arr = None

    top_card.rect.y = min(0, top_card.rect.y + 3)
    top_card.recolor(COLORS[top_card_arr.color])
    sprites.add(top_card)

    if bottom_card_arr is not None:
        bottom_card.rect.y = max(184, bottom_card.rect.y - 3)
        bottom_card.recolor(COLORS[bottom_card_arr.color])
        sprites.add(bottom_card)

    sprites.draw(screen)

    anchor = top_card.rect.y
    draw_arr_text(screen, top_card_arr, curr_top_card + 1, anchor)

    if bottom_card_arr is not None:
        anchor = bottom_card.rect.y
        draw_arr_text(screen, bottom_card_arr, curr_top_card + 2, anchor)

def next_close_frame(screen, top_card, bottom_card, curr_top_card, arrivals):
    screen.fill(COLORS["Black"])
    sprites = pygame.sprite.Group()
    top_card_arr = arrivals[curr_top_card]
    if curr_top_card + 1 < len(arrivals):
        bottom_card_arr = arrivals[curr_top_card + 1]
    else:
        bottom_card_arr = None

    top_card.rect.y = max(-176, top_card.rect.y - 3)
    top_card.recolor(COLORS[top_card_arr.color])
    sprites.add(top_card)

    if bottom_card_arr is not None:
        bottom_card.rect.y = min(360, bottom_card.rect.y + 3)
        bottom_card.recolor(COLORS[bottom_card_arr.color])
        sprites.add(bottom_card)

    sprites.draw(screen)

    anchor = top_card.rect.y
    draw_arr_text(screen, top_card_arr, curr_top_card + 1, anchor)

    if bottom_card_arr is not None:
        anchor = bottom_card.rect.y
        draw_arr_text(screen, bottom_card_arr, curr_top_card + 2, anchor)

def main(train_key, bus_key, station_ids, route_id_dict):
    # Initialize pygame
    pygame.init()
    pygame.font.init()

    # Initialize game/display logic
    window_size = (WIDTH, 360)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption("Transit Tracker - CTA")
    clock = pygame.time.Clock()
    done = False
    in_open_animation = True
    in_close_animation = False
    last_draw_time = 0
    last_pull_time = 0
    curr_top_card = 0

    # Create sprites
    top_card = Card(COLORS["Grey"], WIDTH, 176)
    top_card.rect.x = 60
    top_card.rect.y = -176
    bottom_card = Card(COLORS["Grey"], WIDTH, 176)
    bottom_card.rect.x = 60
    bottom_card.rect.y = 360

    arrivals = load_arrivals(TRAIN_KEY, BUS_KEY, STATION_IDS, ROUTE_ID_DICT)
    next_arrivals = []

    pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)

    while not done:
        # handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    pygame.mouse.set_visible(False)
                elif event.key == pygame.K_ESCAPE:
                    pygame.display.set_mode(window_size)
                    pygame.mouse.set_visible(True)
                elif event.key == pygame.K_q:
                    done = True

        now = pygame.time.get_ticks()

        # if a minute has passed, check for new arrivals
        if now - last_pull_time > 60000:
            try:
                next_arrivals = load_arrivals(TRAIN_KEY, BUS_KEY, STATION_IDS, ROUTE_ID_DICT)
                last_pull_time = now
            except IOError:
                continue

        # Code to do the open animation
        if in_open_animation:
            if top_card.rect.y == 0:
                in_open_animation = False
                last_draw_time = now
            else:
                if now - last_draw_time > 10:
                    next_open_frame(screen, top_card, bottom_card, curr_top_card, arrivals)
                    pygame.display.flip()
                    last_draw_time = now
        elif in_close_animation:
            if top_card.rect.y == -176:
                in_close_animation = False
                in_open_animation = True
                last_draw_time = now

                # Update curr_top_card if on last card
                curr_top_card += 2
                if (curr_top_card >= len(arrivals)):
                    # If new arrivals, update that too
                    if (len(next_arrivals) > 0):
                        arrivals = next_arrivals
                        next_arrivals = []
                    curr_top_card = 0

            else:
                if now - last_draw_time > 10:
                    next_close_frame(screen, top_card, bottom_card, curr_top_card, arrivals)
                    pygame.display.flip()
                    last_draw_time = now

        else:
            if now - last_draw_time > 6000:
                in_close_animation = True

        clock.tick(100)


if __name__ == "__main__":
    with open("./api/train_api_key.txt", 'r') as file:
        TRAIN_KEY = file.readline()[:-1]

    with open("./api/bus_api_key.txt", 'r') as file:
        BUS_KEY = file.readline()[:-1]

    main(TRAIN_KEY, BUS_KEY, STATION_IDS, ROUTE_ID_DICT)
    