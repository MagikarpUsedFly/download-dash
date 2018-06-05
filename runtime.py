import downloader_class as dc
import time
from threading import Thread
import curses
import os
import sys

##
# Runtime.py Script is designed to simulate a hot dog downloader race
##

# hard coding url for now
url1 = 'http://ipv4.download.thinkbroadband.com/5MB.zip'
url2 = 'http://ipv4.download.thinkbroadband.com/10MB.zip'
url3 = 'http://ipv4.download.thinkbroadband.com/20MB.zip'
url4 = 'http://ipv4.download.thinkbroadband.com/50MB.zip'
url5 = 'http://ipv4.download.thinkbroadband.com/100MB.zip'

# Setting Up colors and Terminal Res Tracker.
#--------------------------------------------------------------------------------------------------------#

# Instantiating screen object
screen = curses.initscr()

# Cursor visibility = false
curses.curs_set(0)

# starting and declaring colors for the program
curses.start_color()
curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_RED, curses.COLOR_YELLOW)
curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)
curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)

red                 = 1 # red text with black background
yellow_background   = 2 # yellow background hurts eyes
blue                = 3 # blue text black background
default             = 4 # green text with black background
yellow_text         = 5 # yellow text with black bacground
cyan_dots           = 6 # blue dots when race is done

# Window_res determines middle_height, middle_width, pos_start x
def window_res(screen):
    window_height, window_width = screen.getmaxyx()
    middle_height = (round(window_height/2 - 1))
    middle_width = (round(window_width/2 -1))
    pos_start_x = (window_width -1)
    return middle_height, middle_width

window_height, window_width = window_res(screen)

# Setting bacground color for first window launch
screen.bkgd(curses.color_pair(yellow_background))

#----------------------------------------------------------------------------------------------------------#

def func():
    # Firt try is used to display the countdown screen before race
    try:
        for x in range(3, 0, -1):
            count = 0
            while(count != 1000):
                middle_height, middle_width = window_res(screen)
                screen.clear()
                screen.border()
                screen.addstr(middle_height - 2, middle_width - 22 ,
                    '(>0.0)>   -_-_COUNTDOWN HYPE_-_-   <(0.0<)', curses.color_pair(yellow_background))
                screen.addch(middle_height, middle_width - 1, str(x) , curses.color_pair(yellow_background))
                screen.refresh()
                count += 1

        count1 = 0
        while(count1 != 1000):
            middle_height, middle_width = window_res(screen)
            screen.clear()
            screen.border()
            screen.addstr(middle_height - 2, middle_width - 22 ,
                '(>0.0)>   -_-_COUNTDOWN HYPE_-_-   <(0.0<)', curses.color_pair(yellow_background))
            screen.addstr(middle_height, middle_width - 2, 'GO!', curses.color_pair(yellow_background))
            screen.refresh()
            count1 += 1

        screen.clear()

    # For user wanting to ctr ^C
    except KeyboardInterrupt:
        curses.endwin()
        sys.exit("Keyboard Interrupt")

    # Declaring an array of players and instantiating those players and setting url total length
    players = []
    for i in range(0, 5, 1):
        players.append(dc.Downloader())

    # Declaring an array of threads
    threads = []
    for p in players:
        threads.append(Thread(target=p.download, args=(url5,)))

    # Starting the array of threads
    for thread in threads:
        thread.start()

    # Setting color for the race window
    screen.bkgd(curses.color_pair(default))

    try:
        max_download_speed = 0
        split_timer = time.time()
        start_time = time.time()

        while(True):
            # Setting middle_width and height
            middle_height, middle_width = window_res(screen)

            # Getting window size
            window_height, window_width = screen.getmaxyx()

            # Clearing each for each new frame of print
            screen.clear()

            # Displaying border
            screen.border()

            percent_print = []
            for p in players:
                percent_print.append(int((window_width - 23) * p.data_length/p.total_length))

            # Determing peak_download and highest overall peak_download
            for p in players:
                p.peak_download = (p.chunk_rate/1024/1024)
                if p.peak_download > max_download_speed:
                    max_download_speed = p.peak_download

            # Displaying overall peak download to screen
            screen.addstr(36, 2, "Overall Peak Download Rate Recorded: ", curses.color_pair(blue))
            screen.addstr(36, 39, "%.3f Mbs" % (max_download_speed), curses.color_pair(yellow_text))

            # Title for the race window
            screen.addstr(2, middle_width - 10, "Hot Dog Downloader", curses.color_pair(blue))
            screen.addstr(3, middle_width - 14, '--------------------------', curses.color_pair(blue))

            # Y componet offset for players

            y_offset = 6
            # Used in percent_print array
            x = 0

            for p in players:

                # Displaying the player, rate, percent downloaded and start/finish animation
                screen.addstr(y_offset, 2,  "Player"+str(x+1)+" ::", curses.color_pair(cyan_dots))
                screen.addstr(y_offset, 13, "| Rate: %.3f MBs" %
                    (round(p.chunk_rate/1024/1024, 3)))
                screen.addstr(y_offset, 31, "| Percent Downloaded: %s%%" % (p.get_percent_done()))
                screen.addstr(y_offset+2, 2, "start |%s:]%s| finish!" %
                    ('-' * percent_print[x], ' ' *(window_width - 23 - percent_print[x])),
                    curses.color_pair(yellow_text))

                # Displaying the peak download
                if(p.chunk_rate > p.peak_download_high):
                    p.peak_download_high = p.chunk_rate
                screen.addstr(y_offset+4, 2, "Peak Download Rate Recorded:", curses.color_pair(blue))
                screen.addstr(y_offset+4, 34, "%.3f Mbs" % (p.peak_download_high/1024/1024), curses.color_pair(yellow_text))

                # If done hen print static image for load animation but can still be resized
                if(p.get_percent_done() == 100):
                    screen.addstr(y_offset, 21, "0.000", curses.color_pair(red))
                    screen.addstr(y_offset+2, 2, "start |%s:]%s| finish!" %
                        ('-' * percent_print[x], ' ' *(window_width - 22 - percent_print[x])),
                        curses.color_pair(yellow_text))
                    p.done_flag = True

                # Display overall average download when done
                if(p.done_flag == True and p.get_percent_done() == 100):
                    if(p.stop_avg_flag == False):
                        p.time_end = time.time()
                        p.stop_avg_flag = True
                    p.overall_average_download = round(((p.total_length /(p.time_end - start_time)) /1024/1024), 3)
                    screen.addstr(y_offset+4, 46, "Overall Average Download Speed:", curses.color_pair(blue))
                    screen.addstr(y_offset+4, 81, "%.3f MBs" % (p.overall_average_download), curses.color_pair(yellow_text))
                else:
                    pass

                y_offset += 6 # Offesting the next racer in y-direction
                x += 1
            screen.refresh()
            time.sleep(.1)

    except KeyboardInterrupt:
        curses.endwin()
        sys.exit("Keyboard Interrupt")
        for thread in threads:
            thread.join()
func()
