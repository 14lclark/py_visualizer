import curses

class Visualizer:
    
    '''
    Visualization base class.
    '''
    def __init__(self, state) -> None:
        raise NotImplementedError
    
    def update(self, new_state) -> None:
        '''
        Update the visualizer to a new state. 
        '''
        raise NotImplementedError
    
    def render(self, options):
        '''
        Process and display the current state in some way.
        '''
        
        raise NotImplementedError
    
class Vis2DTerminal(Visualizer):
    '''
    Visualizer for 2D grids given a dictionary of (x,y)-coordinates. 
    '''
    
    def __init__(self, state: dict = {}) -> None:
        #Curses setup
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        # curses.mousemask(1)
        self.stdscr.keypad(True)
        self.stdscr.nodelay(1)
        
        self.state = state
        self.pause = True
        self.coord_offset = (0,0)
        self.screen_dims = self.stdscr.getmaxyx()
        self.default_speed = 512
        self.speed = self.default_speed # render speed (number of frames rendered)
        self.mousex, self.mousey = None, None
        
    def update_state(self, new_state: dict) -> None:
        self.state = new_state

    def _move_window(self, x, y):
        offset_x, offset_y = self.coord_offset
        self.coord_offset = (offset_x + x, offset_y +  y)

    def _handle_input(self, c):
        
        def quit(*args, **kwargs):
            raise InterruptedError
        def toggle_pause(*args, **kwargs):
            self.pause = not self.pause
        def set_speed(val, *args, **kwargs):
            self.speed = int(val+1)
            if self.speed < 10:
                self.speed = 10
            elif self.speed > 5000:
                self.speed = 7000
        def mouse(*args, **kwargs):
            _, self.mousex, self.mousey, _, _ = curses.getmouse()
            
            
        def move(tup, *args, **kwargs):
            self._move_window(tup[0],tup[1])
            
        handle_dict = {
            curses.KEY_LEFT:  [move, (-1,0)],
            ord('4'):         [move, (-1,0)],
            curses.KEY_UP:    [move, (0,-1)],
            ord('8'):         [move, (0,-1)],
            curses.KEY_RIGHT: [move, (1,0)],
            ord('6'):         [move, (1,0)],
            curses.KEY_DOWN:  [move, (0,1)],
            ord('2'):         [move, (0,1)],
            
            ord('7'):         [move, (-1,-1)],
            ord('9'):         [move, (1,-1)],
            ord('3'):         [move, (1,1)],
            ord('1'):         [move, (-1,1)],
            ord('q'):         [quit, None],
            ord('p'):         [toggle_pause, None],
            ord('+'):         [set_speed, (self.speed/1.1)], # fewer frames per step
            ord('-'):         [set_speed, (self.speed*1.1)],  # more frames per step
            ord('='):         [set_speed, (self.default_speed)],
            
            curses.KEY_MOUSE: [mouse, None]
            }      
        
        if c in handle_dict:
            func, arg = handle_dict[c]
            func(arg)
        return
    def _render(self):
        rows, cols = self.screen_dims
        coords = list(self.state.keys())

        x_range = cols - 1
        y_range = rows - 1
        x_offset, y_offset = self.coord_offset
        x_min, y_min = x_offset,           y_offset
        x_max, y_max = x_offset + x_range, y_offset + y_range
        
        grid = [[' ' for _ in range(x_range + 1)]
                        for _ in range(y_range + 1)]

        for x, y in coords:
            if (x_min <= x <= x_max) and (y_min <= y <= y_max):
                grid[y - y_min][x - x_min] = '#'   
                
        for y in range(y_range):
            self.stdscr.addstr(y,0,''.join(grid[y]))
        self.stdscr.insstr(y_range,0,''.join(grid[y_range]))
        
        self.stdscr.addstr(0,0,f"Press q to exit, +/- to change speed.      x-range: [{x_min}, {x_max}] ")
        self.stdscr.addstr(1,0,f"Press p to (un)pause, = for default speed. y-range: [{y_min}, {y_max}] ")
            
        self.stdscr.refresh()
    
    def _catch_input(self, num_to_catch: int):
        for _ in range(num_to_catch):
            self._handle_input(self.stdscr.getch())
    
    def window_render(self):
        while not self.pause:
            for _ in range(self.speed):
                self._render()
                self._catch_input(10)
            break
        while self.pause:
            self._render()
            self._catch_input(10)
            
    def shutdown(self):
        '''
        Curses teardown.
        '''
        self.stdscr.clear()
        curses.nocbreak()
        curses.curs_set(1)
        # curses.mousemask(0)
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()
    
    
