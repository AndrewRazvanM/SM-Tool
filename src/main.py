from app import Application
import curses   

def main(stdscr):
    app = Application(stdscr)
    app.run()

def app_caller():
    curses.wrapper(main)
    
if __name__ == "__main__":
    curses.wrapper(main)