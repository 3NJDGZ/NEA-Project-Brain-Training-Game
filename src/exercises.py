import pygame
import random
from abc import ABC
from abc import abstractmethod
from mysqlmodel import PlayerDataManager
import pygame_gui
from pygame_gui.core import ObjectID


# Class Errors (Only used during development for the Chalkboard Challenge Exercise)
class NumberOfOperandError(Exception):
    def __init__(self, message = "Number of Operands not in (1, 5) range."):
        self.message = message
        super().__init__(self.message)

class NoEquations(Exception):
    def __init__(self, message = "No Equations present/generated for the Chalkboard Challenge Exercise"):
        self.message = message
        super().__init__(self.message)

# Cell Object used to make an actual grid of cells; used for the exercises: Memory Matrix, and Schulte Table
# Acts as a parent super class as both Memory Matrix, and Schulte Table Cells will be slightly different to each other hence use of Polymorphism + Inheritance (also reduces amount of code)
class Cell():
    def __init__(self, x: int, y: int, tile_size: int, cols: int, rows: int, LINE_COLOUR):
        self._x = x
        self._y = y
        self.tile_size = tile_size
        self.cols = cols
        self.rows = rows
        self.LINE_COLOUR = LINE_COLOUR
        self.LINE_WIDTH = 5
        self._walls = {"top": True,
                      "right": True,
                      "bottom": True,
                      "left": True}

    def draw_cell(self, WIN):
        if self._walls['top']:
            pygame.draw.line(WIN, self.LINE_COLOUR, (self._x, self._y), (self._x + self.tile_size, self._y), self.LINE_WIDTH)
        if self._walls['right']:
            pygame.draw.line(WIN, self.LINE_COLOUR, (self._x + self.tile_size, self._y), (self._x + self.tile_size, self._y + self.tile_size), self.LINE_WIDTH)
        if self._walls['bottom']:
            pygame.draw.line(WIN, self.LINE_COLOUR, (self._x + self.tile_size, self._y + self.tile_size), (self._x, self._y + self.tile_size), self.LINE_WIDTH)
        if self._walls['left']:
            pygame.draw.line(WIN, self.LINE_COLOUR, (self._x, self._y + self.tile_size), (self._x, self._y), self.LINE_WIDTH)

# Parent Super Class (Abstract Base Class) for all Exercises; acts as the 'template' for them. Provides an interface before the actual implementation of the exercise.
class CognitiveExercise(ABC):
    def __init__(self, CognitiveAreaID: int, PDM: PlayerDataManager):
        self._CognitiveAreaID = CognitiveAreaID
        self._PDM = PDM
        self._WIDTH = 1280
        self._HEIGHT = 720
        self._points_earned = 0
        self._completely_finished = False
        self._already_added_time = False
    
    def get_completely_finished(self):
        return self._completely_finished

    def get_already_added_time(self):
        return self._already_added_time

    def set_already_added_time(self, value_to_be_set: bool):
        self._already_added_time = value_to_be_set

    @abstractmethod
    def calculate_points(self):
        pass

    @abstractmethod
    def record_points_on_DB(self, points):
        pass

    @abstractmethod
    def draw_exercise_on_screen(self, WIN):
        pass

    @abstractmethod
    def user_input(self, event):
        pass

# Chalkboard Challenge Code (Cognitive Area: Problem-Solving 4)
class ChalkboardChallenge(CognitiveExercise):
    def __init__(self, CognitiveAreaID: int, PDM: PlayerDataManager):
        super().__init__(CognitiveAreaID, PDM)

        # Stores the Equation Objects and how many to do
        self.__EQUATIONS = []
        self.__number_of_equations_to_do = 5

        # Stores the number of (in)correct answers
        self.__amount_of_correct_answers = 0
        self.__amount_of_incorrect_answers = 0

        # Boolean value used to signify when to record the points earned onto the database 
        self.__record_points = False

        # Set range of values where the equations can get their numbers from (0-10)
        self.lower_threshold = 0
        self.higher_threshold = 10

        # Generate two equations upon intialisation of this ChalkboardChallenge Object and store them into the 'self.__EQUATIONS' list
        self.generate_equation()
        self.generate_equation()

    def calculate_points(self):
        self.__amount_of_incorrect_answers = 5 - self.__amount_of_correct_answers

        # each correct answer is worth +200 points, each incorrect answer is worth -200 points, total points is the sum of them
        self._points_earned = (self.__amount_of_correct_answers * 200) + (self.__amount_of_incorrect_answers * -200)
        print(self._points_earned) 
        return self._points_earned
    
    def record_points_on_DB(self, points):
        self._PDM.record_points_from_exercises_on_DB(points, self._CognitiveAreaID)

    def user_input(self, event):
        if event.type == pygame.KEYDOWN:

            # Check that the number of equations left to do is above 0
            if self.__number_of_equations_to_do != 0:
                if event.key == pygame.K_z: # Used to check if the left equation is larger than the right equation
                    self.__number_of_equations_to_do -= 1
                    if self.__EQUATIONS[0].get_answer() > self.__EQUATIONS[1].get_answer():
                        self.__amount_of_correct_answers += 1
                    self.generate_new_set_of_equations()
                elif event.key == pygame.K_x: # Used to check if the equations are equal to each other
                    self.__number_of_equations_to_do -= 1
                    if self.__EQUATIONS[0].get_answer() == self.__EQUATIONS[1].get_answer():
                        self.__amount_of_correct_answers += 1
                    self.generate_new_set_of_equations()
                elif event.key == pygame.K_c: # Used to check if the right equation is larger than the left equation
                    self.__number_of_equations_to_do -= 1
                    if self.__EQUATIONS[0].get_answer() < self.__EQUATIONS[1].get_answer():
                        self.__amount_of_correct_answers += 1
                    self.generate_new_set_of_equations()
    
    def show_final_score(self, font, WIN):
        # 'screen' surface shown to the user when the complete the exercise
        self.__EQUATIONS = []
        text = f"Final Score: {self.__amount_of_correct_answers} / 5, Points: {self._points_earned}"
        text_surface = font.render(text, True, (255, 255, 255))
        WIN.blit(text_surface, ((1600 - text_surface.get_width()) / 2, (900 - text_surface.get_height()) / 2))
 
    def draw_exercise_on_screen(self, WIN):
        # Draw base rect surface onto screen
        pygame.draw.rect(WIN, (2, 5, 25), pygame.Rect(160, 90, self._WIDTH, self._HEIGHT))

        # font
        font = pygame.font.Font(None, 36) 
        if self.__number_of_equations_to_do > 0:

            pygame.draw.rect(WIN, (50, 50, 50), pygame.Rect(180, 110, 610, 680)) # left tile
            pygame.draw.rect(WIN, (50, 50, 100), pygame.Rect(810, 110, 610, 680)) # right tile
            pygame.draw.rect(WIN, (100, 50, 100), pygame.Rect(600, 610, 400, 200)) # middle selection tile

            # Middle Selection Tile 
            text_to_be_shown = "Determine which side is larger"
            text_to_be_shown_surface = font.render(text_to_be_shown, True, (255, 255, 255))
            controls = "LEFT 'Z', EQUAL 'X', RIGHT 'C'"
            controls_surface = font.render(controls, True, (255, 255, 255))

            # First Equation
            equation1 = self.__EQUATIONS[0].get_equation()
            equation1_surface = font.render(equation1, True, (255, 255, 255))

            # Second Equation 
            equation2 = self.__EQUATIONS[1].get_equation()
            equation2_surface = font.render(equation2, True, (255, 255, 255))

            # Drawing said equations onto the screen
            WIN.blit(equation1_surface, ((610 + 180) / 2, (680 + 110) / 2))
            WIN.blit(equation2_surface, (610 + ((610 + 180) / 2), (680 + 110) / 2))
            WIN.blit(text_to_be_shown_surface, ((1600 - text_to_be_shown_surface.get_width()) / 2, 625))
            WIN.blit(controls_surface, ((1600 - controls_surface.get_width()) / 2, 675))
        else:
            # If there are no more equations to do then show the user the final score and record their points earned onto the database
            self.show_final_score(font, WIN)
            if not self.__record_points: # Boolean value here used to avoid repeatedly committing changes to the database as this subroutine is called within a loop
                points = self.calculate_points()
                self.record_points_on_DB(points)
                self.__record_points = True

                # Signify that this current exercise is completely finished
                self._completely_finished = True
        
    def generate_equation(self):
        
        # number of operands are randomly generated; length of the 'operands' array is used to declare the equations overall 'difficulty' (e.g., more/less complex)
        operands = []
        no_of_operands = random.randint(2, 5)

        # generate the operands
        for x in range(no_of_operands):
            # get a random value from the threshold parameters (0-10)
            random_operand = random.randint(self.lower_threshold, self.higher_threshold)
            operands.append(random_operand)

        # Create a new 'Equation' object and append to the array
        self.__EQUATIONS.append(Equation(operands))

    def generate_new_set_of_equations(self):
        # Overwrite the array, and create two new equations to be used
        self.__EQUATIONS = []
        self.generate_equation()
        self.generate_equation()
    
    def show_every_equation(self):
        if len(self.__EQUATIONS) > 0:
            for equation in self.__EQUATIONS:
                print(f"{equation.get_equation()} = {equation.get_answer()}")
        else:
            raise NoEquations()

class Equation():
    def __init__(self, operands):
        self.operators = ["+", "-", "*", "//"]
        self.__operands = operands
        self.__difficulty = len(operands) -1
        self.__answer = 0 # default value 
        self.__equation = self.create_equation()
    
    def get_equation(self):
        return self.__equation

    def get_answer(self):
        return self.__answer
    
    def get_random_operator(self):
        random_operator = self.operators[random.randint(0, 3)]
        return random_operator

    def create_equation(self):
        # lowest number is the easiest, largest is the hardest
        if len(self.__operands) <= 5:
            while True:
                try:
                    if self.__difficulty == 1:
                        self.__equation = f"{self.__operands[0]} {self.get_random_operator()} {self.__operands[1]}"
                    elif self.__difficulty == 2:
                        self.__equation = f"({self.__operands[0]} {self.get_random_operator()} {self.__operands[1]}) {self.get_random_operator()} {self.__operands[2]}"
                    elif self.__difficulty == 3:
                        self.__equation = f"({self.__operands[0]} {self.get_random_operator()} {self.__operands[1]}) {self.get_random_operator()} ({self.__operands[2]} {self.get_random_operator()} {self.__operands[3]})"
                    elif self.__difficulty == 4:
                        self.__equation = f"(({self.__operands[0]} {self.get_random_operator()} {self.__operands[1]}) {self.get_random_operator()} ({self.__operands[2]} {self.get_random_operator()} {self.__operands[3]})) {self.get_random_operator()} {self.__operands[4]}"
                    self.__answer = eval(self.__equation) # https://www.geeksforgeeks.org/python-evaluate-expression-given-in-string/
                    if isinstance(self.__answer, int):
                        break
                except ZeroDivisionError:
                    print("Cannot Divide By Zero!")
            return self.__equation
        else:
            raise NumberOfOperandError()
# End of Chalkboard Challenge Code

# Memory Matrix Code (Cognitive Area: Memory 1)
class MemoryMatrix(CognitiveExercise):
    def __init__(self, CognitiveAreaID: int, PDM: PlayerDataManager):
        super().__init__(CognitiveAreaID, PDM)

        # Necessary Attributes
        self.__trail_active = False # three trails are set for this exercise
        self.__record_points = False

        # Load settings
        settings = PDM.get_settings('Memory Matrix')
        parameters = settings['Parameters']
        # parameters extracted from the settings file and used in generating how many highlighted cells should be used for each pattern in each trail
        # each trail will get gradually harder than the one before
        number_of_highlighted_cells_one = random.randint(parameters[0][0], parameters[0][1])
        number_of_highlighted_cells_two = random.randint(parameters[1][0], parameters[1][1])
        number_of_highlighted_cells_three = random.randint(parameters[2][0], parameters[2][1])

        # Patterns
        self.__patterns = [MMPattern(number_of_highlighted_cells_one), MMPattern(number_of_highlighted_cells_two), MMPattern(number_of_highlighted_cells_three)]
        self.__current_pos = 0
        self.__current_pattern = self.__patterns[self.__current_pos]

        # Variables required for input
        self.__space_bar_down = False
        self.__space_bar_press_time = 0

        # Mouse positions 
        self.__mouse_position = 0
        self.__mouse_x = 0
        self.__mouse_y = 0

    def find_mouse_pos(self): # https://www.youtube.com/watch?v=OYw9D75d7Lw
        self.__mouse_position = pygame.mouse.get_pos()
        self.__mouse_x = self.__mouse_position[0]
        self.__mouse_y = self.__mouse_position[1]
        print(f"[{self.__mouse_x}, {self.__mouse_y}]")
    
    def find_cell_position(self):
        # Exercise screen is 1280*720, and is (160, 90) away from point of origin (0, 0)
        # Each cell size is again 100
        cell_column_positioning = (self.__mouse_x - 400) // 100 # every cell is +400 away in the x direction from point of origin
        cell_row_positioining = (self.__mouse_y - 150) // 100 # every cell is +150 away in the y direction from point of origin
        return cell_column_positioning, cell_row_positioining
    
    def user_selection_cells(self):
        if not self._completely_finished:
            # Check that the mouse position is in the correct area 
            if self.__mouse_x >= 400 and self.__mouse_y >= 150 and self.__mouse_x <= 1200 and self.__mouse_y <= 750:

                # Get row. col position 
                col_pos, row_pos = self.find_cell_position()

                # Use said values as index positioning to get correct cell from 'MMPattern' object (the grid of cells is also stored as a 2D array)s
                selected_cell = self.__current_pattern.get_grid_of_cells()[row_pos][col_pos]

                # Checks if the selected cell is highlighted, and that it has not yet been selected by the user
                if selected_cell.get_highlighted_cell() and not selected_cell.get_selected_by_user():
                    selected_cell.set_selected_by_user(True)

                    # increase the points 
                    print("You have selected a correct cell!")
                    self.calculate_points()

                # Used to avoid user from selecting the same cell and getting infinite points
                elif selected_cell.get_highlighted_cell() and selected_cell.get_selected_by_user():
                    print("You have already selected this cell!")
                else:

                    # Checks if the user has already selected a wrong cell (seen in red on the screen)
                    if selected_cell.get_selected_by_user() and selected_cell.get_incorrect():
                        print("You have already selected this wrong cell!")
                    else:

                        # decrease points and increment amount of errors for current pattern (max errors allowed: 3; else the trail ends and the next trail begins)
                        self.__current_pattern.increment_number_of_errors()
                        selected_cell.set_incorrect(True)
                        selected_cell.set_selected_by_user(True)
                        print("You have selected a wrong cell!")
                        self._points_earned -= 50
                
                # Check if the number of errors for the current trail is 3
                if self.__current_pattern.get_number_of_errors() == 3:
                    self.go_to_next_trail()
                
                # Abstract the user selected patterns
                if selected_cell.get_highlighted_cell():
                    self.__current_pattern.dynamically_update_user_selected_cells(col_pos, row_pos)
                
                # Compares the patterns of the highlighted cells and the user's selected cells (both patterns are abstracted as a 2D array)
                if self.__current_pattern.get_abstracted_pattern() == self.__current_pattern.get_user_selected_abstracted_pattern():
                    print("You got this trail fully correct!")

                    # Increase points by 100 and automatically go to the next trail
                    self._points_earned += 100
                    self.go_to_next_trail()
    
    def go_to_next_trail(self):
        if self.__current_pos < 2:
            self.__current_pattern.set_finished(True)
            self.__current_pos += 1
            self.__current_pattern = self.__patterns[self.__current_pos]

            # Reset all base values back to original state
            self.__space_bar_down = False
            self.__trail_active = False
        else:
            print("No more trails!")
            self._completely_finished = True

    def calculate_points(self):
        self._points_earned += 20
    
    def record_points_on_DB(self, points):
        self._PDM.record_points_from_exercises_on_DB(points, self._CognitiveAreaID)
    
    def draw_exercise_on_screen(self, WIN):
        # font
        font = pygame.font.Font(None, 50) 

        # If exercise is finished show users how many points they have earned and record said points earned onto the MySQL database
        if self._completely_finished:
            pygame.draw.rect(WIN, (0, 0, 0), pygame.Rect(160, 90, self._WIDTH, self._HEIGHT))
            final_score_text = f"Final Score: {self._points_earned}"
            final_score_text_surface = font.render(final_score_text, True, (255, 255, 255))
            WIN.blit(final_score_text_surface, ((1600 - final_score_text_surface.get_width()) / 2, (900 - final_score_text_surface.get_height()) / 2))
            if not self.__record_points:
                self.record_points_on_DB(self._points_earned)
                self.__record_points = True
        else:
            # Drawing
            pygame.draw.rect(WIN, (255, 216, 107), pygame.Rect(160, 90, self._WIDTH, self._HEIGHT))
            self.__current_pattern.draw_cells(WIN)

            # Text Surface Creation + Drawing onto Screen
            difficulty_text = f"Difficulty: {self._PDM.get_settings('Memory Matrix')['Difficulty']}"
            difficulty_text_surface = font.render(difficulty_text, True, (255, 255, 255))
            WIN.blit(difficulty_text_surface, (170, 105))
            score_text = f"Score: {self._points_earned}"
            score_text_surface = font.render(score_text, True, (255, 255, 255))
            WIN.blit(score_text_surface, (500, 105))
            trail_number_text = f"Trail: {self.__current_pos + 1}"
            trail_number_text_surface = font.render(trail_number_text, True, (255, 255, 255))
            WIN.blit(trail_number_text_surface, (1000, 105))
            space_bar_text = "PRESS 'SPACE' TO REVEAL THE HIGHLIGHTED CELLS"
            space_bar_text_surface = font.render(space_bar_text, True, (255, 255, 255))
            WIN.blit(space_bar_text_surface, ((1600 - space_bar_text_surface.get_width()) / 2, 765))

            # Checking Timers
            self.__current_time = pygame.time.get_ticks()
            if self.__space_bar_down:
                self.__current_pattern.set_show_value(True)
                if self.__current_time - self.__space_bar_press_time > 4000: # Checks if 4 seconds have passed since the player has last pressed the space bar
                    self.__space_bar_down = False
                    self.__trail_active = True
                    self.__current_pattern.set_show_value(False)
                    self.__current_pattern.set_user_selected_cells(True)

        # https://www.youtube.com/watch?v=YOCt8nsQqEo pygame timers tutorial used
    
    def user_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not self.__space_bar_down and not self.__trail_active:
                self.__space_bar_press_time = pygame.time.get_ticks() 
                self.__space_bar_down = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # left mouse button
                self.find_mouse_pos()
                if self.__trail_active:
                    self.user_selection_cells()

class MMPattern():
    def __init__(self, number_of_highlighted_cells: int):
        # This will work in the same way as generating a maze except without creating a path + disabling walls 
        self.__grid_of_cells = []

        self.__abstracted_pattern = [] # Abstracted Pattern of the Highlighted Cells represented as a 2D matrix with 1s and 0s
        self.__user_selected_abstracted_pattern = [] # Abstracted Pattern of the selected cells by the user represented in the same way as mentioned above

        # Default parameters for each cell and the overall grid dimension
        self.__tile_size = 100
        self.__rows = 6
        self.__cols = 8
        self.__number_of_highlighted_cells = number_of_highlighted_cells

        # Boolean Variables 
        self.__finished = False
        self.__show_highlights = False
        self.__show_user_selected_cells = False

        # Stores number of errors made from the user
        self.__errors = 0 # cap at three

        # Setup the grid of cells 
        for row_number in range(self.__rows):
            row = []
            for col_number in range(self.__cols):
                row.append(MMCell(self.__tile_size * col_number, self.__tile_size * row_number, self.__tile_size, self.__cols, self.__rows, (0, 0, 0)))
            self.__grid_of_cells.append(row)
        
        # Setup an empty grid of cells (used for the abstracted pattern for user)
        for row_number in range(self.__rows):
            row = []
            for col_number in range(self.__cols):
                row.append(0)
            self.__user_selected_abstracted_pattern.append(row)

        # Generate random highlighted pattern of cells, abstract it, then store it as a 2D array of 0s and 1s (1s representing a higlighted cell)
        # Will be used to compare to the user's abstracted pattern
        self.generate_cell_pattern()
        self.store_pattern()
    
    def get_user_selected_abstracted_pattern(self):
        return self.__user_selected_abstracted_pattern
    
    def get_abstracted_pattern(self):
        return self.__abstracted_pattern
    
    def set_finished(self, value_to_be_set: bool):
        self.__finished = value_to_be_set
    
    def get_finished(self):
        return self.__finished
    
    def get_number_of_errors(self):
        return self.__errors

    def increment_number_of_errors(self):
        self.__errors += 1
    
    def get_grid_of_cells(self):
        return self.__grid_of_cells
    
    def set_show_value(self, value_to_be_set: bool):
        self.__show_highlights = value_to_be_set
    
    def set_user_selected_cells(self, value_to_be_set: bool):
        self.__show_user_selected_cells = value_to_be_set
    
    def generate_cell_pattern(self):
        for x in range(0, self.__number_of_highlighted_cells):
                    # Generate Random Positioning for Cell
                    random_row = random.randint(0, self.__rows)
                    random_col = random.randint(0, self.__cols)
                    random_cell = self.__grid_of_cells[random_row-1][random_col-1]

                    # Check if current cell is not highlighted
                    if random_cell.get_highlighted_cell() == False:
                        random_cell.set_highlighted(True)
                    else:
                        # If it is highlighted, then find another position 
                        while True:
                            random_row = random.randint(0, self.__rows)
                            random_col = random.randint(0, self.__cols)
                            random_cell = self.__grid_of_cells[random_row-1][random_col-1]
                            if not random_cell.get_highlighted_cell():
                                random_cell.set_highlighted(True)
                                break
    
    def store_pattern(self):
        # creating and storing the pattern, 1s representing a a highlighted cell
        for row in self.__grid_of_cells:
            pattern_row = []
            for cell in row:
                if cell.get_highlighted_cell():
                    pattern_row.append(1)
                else:
                    pattern_row.append(0)
            self.__abstracted_pattern.append(pattern_row)
        
        # Printing the stored pattern
        for row in self.__abstracted_pattern:
            print(row)
        print("\n")
    
    def dynamically_update_user_selected_cells(self, col_pos: int, row_pos: int):
        self.__user_selected_abstracted_pattern[row_pos][col_pos] = 1

    def draw_cells(self, WIN):
        for row in self.__grid_of_cells:
                for cell in row:
                    cell.draw_cell(WIN, self.__show_highlights, self.__show_user_selected_cells)

class MMCell(Cell):
    def __init__(self, x: int, y: int, tile_size: int, cols: int, rows: int, LINE_COLOUR):
        super().__init__(x, y, tile_size, cols, rows, LINE_COLOUR)
        self.__highlighted = False
        self.__selected_by_user = False
        self.__incorrect = False
        self._x = x + 400
        self._y = y + 150
    
    def set_incorrect(self, value_to_be_set: bool):
        self.__incorrect = value_to_be_set
    
    def get_incorrect(self):
        return self.__incorrect

    def set_highlighted(self, value_to_be_set: bool):
        self.__highlighted = value_to_be_set
    
    def get_highlighted_cell(self):
        return self.__highlighted

    def set_selected_by_user(self, value_to_be_set: bool):
        self.__selected_by_user = value_to_be_set
    
    def get_selected_by_user(self):
        return self.__selected_by_user

    def draw_cell(self, WIN, draw_highlighted: bool, draw_user_selection: bool):

        if self.__selected_by_user and self.__incorrect:
            pygame.draw.rect(WIN, (255, 0, 0), (self._x+5, self._y+5, self.tile_size-10, self.tile_size-10))
        elif self.__selected_by_user and draw_user_selection: # draw the selected cells by the user
            pygame.draw.rect(WIN, (176, 206, 255), (self._x+5, self._y+5, self.tile_size-10, self.tile_size-10))

        if self.__highlighted and draw_highlighted: # draw the highlighted cells from the pattern to show to the user
            pygame.draw.rect(WIN, (0, 213, 255), (self._x+5, self._y+5, self.tile_size-10, self.tile_size-10))
        if self._walls['top']:
            pygame.draw.line(WIN, self.LINE_COLOUR, (self._x, self._y), (self._x + self.tile_size, self._y), self.LINE_WIDTH)
        if self._walls['right']:
            pygame.draw.line(WIN, self.LINE_COLOUR, (self._x + self.tile_size, self._y), (self._x + self.tile_size, self._y + self.tile_size), self.LINE_WIDTH)
        if self._walls['bottom']:
            pygame.draw.line(WIN, self.LINE_COLOUR, (self._x + self.tile_size, self._y + self.tile_size), (self._x, self._y + self.tile_size), self.LINE_WIDTH)
        if self._walls['left']:
            pygame.draw.line(WIN, self.LINE_COLOUR, (self._x, self._y + self.tile_size), (self._x, self._y), self.LINE_WIDTH)
# End of Memory Matrix Code

# Schulte Table Code (Cognitive Area: Attention 2)
class SchulteTable(CognitiveExercise):
    def __init__(self, CognitiveAreaID: int, PDM: PlayerDataManager):
        super().__init__(CognitiveAreaID, PDM)

        # Load Settings
        settings = PDM.get_settings('Schulte Table')
        self.grid_dimension = settings['Grid Dimension'] # options are only 4 or 5 
        self.__colour = settings['Colour']
        self.__table_grid = TableGrid(self.grid_dimension, self.__colour)

        # Mouse Positions
        self.__mouse_pos = pygame.mouse.get_pos()
        self.__mouse_x = self.__mouse_pos[0]
        self.__mouse_y = self.__mouse_pos[1]

        self.__next_number_to_find = 1 # starting number
        self.__record_points = False # Check if we need to record points

        # Time variables
        self.__space_bar_time = 0
        self.__space_bar_down = False
    
    def calculate_points(self):
        # Calculates points for the user based on max points (which is also calculated too)
        max_points = 50 * (self.grid_dimension**2)
        print(max_points)
        seconds_to_complete = (pygame.time.get_ticks() - self.__space_bar_time) // 1000
        print(f"Seconds to complete: {seconds_to_complete}")
        self._points_earned = max_points - (50 * seconds_to_complete)
        print(self._points_earned)

    def record_points_on_DB(self, points):
        self._PDM.record_points_from_exercises_on_DB(points, 2)
    
    def draw_exercise_on_screen(self, WIN):
        # Draw base 'screen' surface 
        pygame.draw.rect(WIN, (255, 110, 161), pygame.Rect(160, 90, self._WIDTH, self._HEIGHT))

        # Declare font
        font = pygame.font.Font(None, 50)

        if self.__space_bar_down:
            # Calculate the time
            time = (pygame.time.get_ticks() - self.__space_bar_time) // 1000

            # Draw the grid of cells + their numbers
            self.__table_grid.draw_cells(WIN, True)
            
            # Text surfaces + drawing them onto the screen
            find_next_number_text = f"FIND {self.__next_number_to_find}"
            find_next_number_text_surface = font.render(find_next_number_text, True, (255, 255, 255))
            WIN.blit(find_next_number_text_surface, ((1600 - find_next_number_text_surface.get_width()) / 2, 150))
            time_text = f"TIME: {time}"
            time_text_surface = font.render(time_text, True, (255, 255, 255))
            WIN.blit(time_text_surface, ((1600 - time_text_surface.get_width()) / 2, 715))
            difficulty_text = f"Difficulty: {self._PDM.get_settings('Schulte Table')['Difficulty']}"
            difficulty_text_surface = font.render(difficulty_text, True, (255, 255, 255))
            WIN.blit(difficulty_text_surface, (170, 105))


            if self._completely_finished:

                # If finished show user how many points they have received and record them onto the databsae
                pygame.draw.rect(WIN, (0, 0, 0), pygame.Rect(160, 90, self._WIDTH, self._HEIGHT)) # draw new 'screen' surface 

                # Text
                final_score_text = f"Final Score: {self._points_earned}"
                final_score_text_surface = font.render(final_score_text, True, (255, 255, 255))
                WIN.blit(final_score_text_surface, ((1600 - final_score_text_surface.get_width()) / 2, (900 - final_score_text_surface.get_height()) / 2))
                
                # Record
                if not self.__record_points:
                    self.record_points_on_DB(self._points_earned)
                    self.__record_points = True

        else:
            # Introductory 'screen' surface to the user when they collide with exercise cell
            text = "PRESS SPACE TO SHOW THE NUMBERS"
            text_surface = font.render(text, True, (255, 255, 255))
            WIN.blit(text_surface, ((1600 - text_surface.get_width()) / 2, (900 - text_surface.get_height()) / 2))
    
    def select_cells(self):
        
        # Calculate the min x and min y for the mouse position 
        min_x = ((1600 - (100 * self.grid_dimension)) / 2)
        min_y = ((900 - (100 * self.grid_dimension)) / 2)

        # Check if the user's mouse click is within position/area
        if self.__mouse_x >= min_x and self.__mouse_x <= (min_x + (100 * self.grid_dimension)) and self.__mouse_y >= min_y and self.__mouse_y <= (min_y + (100 * self.grid_dimension)):

            # Get row col position of cell where user has clicked
            col_pos, row_pos = self.find_cell_position()
            current_number = self.__table_grid.get_grid_of_cells()[row_pos][col_pos].get_number()

            # Checks if the user has clicked on the final number
            if self.__next_number_to_find == self.grid_dimension**2:

                # Set this exercise to completely finished and calculate and record points onto the database
                self._completely_finished = True
                self.calculate_points()
            
            # Checks if the user has selected the next correct number
            elif current_number == self.__next_number_to_find:
                print("Correct!")
                self.__next_number_to_find += 1
            else:
                self._points_earned -= 50
                print("Incorrect!")
        else:
            print("Mouse click is out of range!")

    def find_cell_position(self):
        cell_column_positioning = (self.__mouse_x - ((1600 - (100 * self.grid_dimension)) // 2)) // 100
        cell_row_positioining = (self.__mouse_y - ((900 - (100 * self.grid_dimension)) // 2)) // 100
        return cell_column_positioning, cell_row_positioining
    
    def update_mouse_coordinates(self):
        self.__mouse_pos = pygame.mouse.get_pos()
        self.__mouse_x = self.__mouse_pos[0]
        self.__mouse_y = self.__mouse_pos[1]

    def user_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not self.__space_bar_down and not self._completely_finished:
                self.__space_bar_down = True
                self.__space_bar_time = pygame.time.get_ticks()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.__space_bar_down and not self._completely_finished:
                self.update_mouse_coordinates()
                self.select_cells()

class TableGrid():
    def __init__(self, grid_dimension: int, colour: bool):
        self.__grid_of_cells = [] # setup list; 2D list in final form 
        self.__array_of_numbers = [] # array of numbers which will be used to label each cell within the grid randomly

        # declare grid dimension + size
        self.__rows = grid_dimension
        self.__cols = grid_dimension
        self.__max_number = grid_dimension**2

        # Tile parameters
        self.__tile_size = 100
        self.__colour = colour

        # generate the array of numbers in a random order
        for number in range(0, self.__max_number):
            self.__array_of_numbers.append(number + 1)
        random.shuffle(self.__array_of_numbers)

        # Setup the grid of cells
        index = 0
        for row_number in range(self.__rows):
            row = []
            for col_number in range(self.__cols):
                row.append(TGCell(self.__tile_size * col_number, self.__tile_size * row_number, self.__tile_size, self.__cols, self.__rows, (0, 0, 0), self.__array_of_numbers[index], grid_dimension, self.__colour))
                index += 1 # index is used to declare which number will be allocated to each cell from the self.__array_of_numbers
            self.__grid_of_cells.append(row)
    
    def get_grid_of_cells(self):
        return self.__grid_of_cells

    def draw_cells(self, WIN, show_numbers: bool):
        for row in self.__grid_of_cells:
            for cell in row:
                cell.draw_cell(WIN, show_numbers)

class TGCell(Cell):
    def __init__(self, x: int, y: int, tile_size: int, cols: int, rows: int, LINE_COLOUR, Number: int, grid_dimension, colour_enable: bool):
        super().__init__(x, y, tile_size, cols, rows, LINE_COLOUR)
        # Adjust the positions of the cells/grid by adjusting the positon of each cell when drawn
        if grid_dimension == 5:
            self._x = x + 550
            self._y = y + 200
        elif grid_dimension == 4:
            self._x = x + 600
            self._y = y + 250

        # Attributes for the label of the cell
        self.__number = Number
        self.__colour = colour_enable # boolean value used to signify whether a number within a cell should be colourised in red (only true if user settings allow)
        self.number_colour = (255, 255, 255)
        if self.__colour:
                random_num = random.randint(1, 2)
                if random_num == 1:
                    self.number_colour = (255, 0, 0)
    
    def get_number(self):
        return self.__number

    def draw_cell(self, WIN, show_numbers: bool):

        # Polymorphed code where it then calls the original method from the parent super class
        if show_numbers:
        
            # generates the text number surface and then draws them individually into each centre of each cell
            font = pygame.font.Font(None, 40)
            number_text = str(self.__number)
            number_text_surface = font.render(number_text, True, self.number_colour)
            WIN.blit(number_text_surface, (self._x + ((100 - number_text_surface.get_width()) / 2), self._y + ((100 - number_text_surface.get_height()) / 2)))

        return super().draw_cell(WIN)
# End of Schulte Table Code

# Aiming Code (Cognitive Area: Speed 3)
class Aiming(CognitiveExercise):
    def __init__(self, CognitiveAreaID: int, PDM: PlayerDataManager):
        super().__init__(CognitiveAreaID, PDM)
        self.__space_bar_down = False
        self.__record_points = False

        # Generate a new target with a random position upon initialisation
        self.__target = Target(random.randint(200, 1080), random.randint(300, 500))

        # Load Settings
        settings = PDM.get_settings('Aiming')
        parameters = settings['Parameters']
        self.__time_limit = parameters[0][0]
        self.__points_increase = parameters[0][1]

        # Time
        self.__space_bar_press_time = 0
        self.__current_time = 0

        # Mouse Positions
        self.__mouse_pos = pygame.mouse.get_pos()
        self.__mouse_x = self.__mouse_pos[0]
        self.__mouse_y = self.__mouse_pos[1]
    
    def update_mouse_pos(self):
        self.__mouse_pos = pygame.mouse.get_pos()
        self.__mouse_x = self.__mouse_pos[0]
        self.__mouse_y = self.__mouse_pos[1]
    
    def check_if_player_clicks_on_target(self):
        # uses pygame rect collision (collidepoint) to check if the user has clicked on the target
        if self.__target.get_target_rect().collidepoint(self.__mouse_x, self.__mouse_y):
            return True
        else:
            return False

    def calculate_points(self):
        self._points_earned += self.__points_increase
    
    def record_points_on_DB(self, points):
        self._PDM.record_points_from_exercises_on_DB(self._points_earned, 3)
    
    def draw_exercise_on_screen(self, WIN):
        # declare font
        font = pygame.font.Font(None, 50)

        # Current time
        self.__current_time = pygame.time.get_ticks()

        if self.__space_bar_down:
            # Draw main 'screen' surface
            pygame.draw.rect(WIN, (54, 217, 106), pygame.Rect(160, 90, self._WIDTH, self._HEIGHT))

            # Draw the target on the 'screen'
            self.__target.draw_target(WIN)

            # Calculate the time left 
            elapsed_time = (self.__current_time - self.__space_bar_press_time) // 1000
            time_left = self.__time_limit - elapsed_time
            
            # Text surfaces + drawing
            difficulty_text = f"Difficulty: {self._PDM.get_settings('Aiming')['Difficulty']}"
            difficulty_text_surface = font.render(difficulty_text, True, (255, 255, 255))
            WIN.blit(difficulty_text_surface, (170, 105))
            time_left_text = f"TIME LEFT: {time_left}"
            time_left_text_surface = font.render(time_left_text, True, (255, 255, 255))
            WIN.blit(time_left_text_surface, (170, 150))
            points_text = f"TOTAL POINTS: {self._points_earned}"
            points_text_surface = font.render(points_text, True, (255, 255, 255))
            WIN.blit(points_text_surface, (170, 195))

            if time_left == 0:
                # if no more time flag this exercise as completely finished
                self._completely_finished = True
            if self._completely_finished:
                # If finished show user their score and record onto the database
                pygame.draw.rect(WIN, (0, 0, 0), pygame.Rect(160, 90, self._WIDTH, self._HEIGHT))
                final_score_text = f"FINAL SCORE: {self._points_earned}"
                final_score_text_surface = font.render(final_score_text, True, (255, 255, 255))
                WIN.blit(final_score_text_surface, ((1600 - final_score_text_surface.get_width()) / 2, (900 - final_score_text_surface.get_height()) / 2))
                if not self.__record_points:
                    self.record_points_on_DB(self._points_earned)
                    self.__record_points = True
        else:
            # Start screen shown to user 
            pygame.draw.rect(WIN, (54, 217, 106), pygame.Rect(160, 90, self._WIDTH, self._HEIGHT))
            tutorial_text = "PRESS 'SPACE' TO REVEAL THE TARGETS"
            tutorial_text_surface = font.render(tutorial_text, True, (255, 255, 255))
            WIN.blit(tutorial_text_surface, ((1600 - tutorial_text_surface.get_width()) / 2, (900 - tutorial_text_surface.get_height()) / 2))
        
    def user_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not self.__space_bar_down:
                print("Space bar has been pressed!")
                self.__space_bar_down = True
                self.__space_bar_press_time = pygame.time.get_ticks()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.__space_bar_down:
                if not self._completely_finished:
                    self.update_mouse_pos()

                    # if user clicks on a target successfully generate and overwrite a new target with a new position
                    if self.check_if_player_clicks_on_target():
                        print("Clicked on a target!")
                        self.__target = Target(random.randint(200, 1080), random.randint(300, 500))
                        self.calculate_points()
                    else:
                        # decrease amount of points if user misclicks a target
                        self._points_earned -= 50
                        print("Did not click on a target!")
            
class Target():
    def __init__(self, x: int, y: int):
        self.__x = x + 160
        self.__y = y + 90

        # Get image plus generate rect 
        self.image = pygame.transform.scale(pygame.image.load("src/target image/Target.png"), (100, 100)).convert_alpha()
        self.__rect = self.image.get_rect(center=(self.__x, self.__y))

    def get_target_rect(self):
        return self.__rect
    
    def draw_target(self, WIN):
        WIN.blit(self.image, self.__rect)
# End of Aiming Code

# Amanda's and Ephen Question Recall Code (Cognitive Area: Memory 1)
class QuestionAnswerExercise(CognitiveExercise):
    def __init__(self, CognitiveAreaID: int, PDM: PlayerDataManager):
        super().__init__(CognitiveAreaID, PDM)
        # retrieve question + corresponding answer from user settings file, or from the default settings if none is present
        self.__question_answer = PDM.get_question_answer_from_settings()
        self.__question = self.__question_answer[0]
        self.__answer = self.__question_answer[1]

        self.__user_answer = '' # set default value of user answer input to nothing
        self.__correct = False
        self.__record_points = False
        
        # UI
        self.__MANAGER = pygame_gui.UIManager((1600, 900), 'Theme/theme.json')
        self.__ANSWER_INPUT = pygame_gui.elements.UITextEntryLine(placeholder_text='Type Answer Here',relative_rect=pygame.Rect((600, 500), (400, 50)), manager = self.__MANAGER, object_id=ObjectID(class_id="@text_entry_lines",object_id="#answer_text_entry"))

    def calculate_points(self):
        return super().calculate_points()
    
    def record_points_on_DB(self, points):
        self._PDM.record_points_from_exercises_on_DB(points, self._CognitiveAreaID)
    
    def draw_exercise_on_screen(self, WIN):
        # Declare font
        font = pygame.font.Font(None, 36)

        if not self._completely_finished:
            # reveal UI
            self.__ANSWER_INPUT.show()
            
            # Draw 'screen' surface
            pygame.draw.rect(WIN, (255, 97, 237), pygame.Rect(160, 90, self._WIDTH, self._HEIGHT))
            
            # Update UI manager
            self.__MANAGER.update(0.06)

            # Text surface + drawing onto screen
            question_text = self.__question
            question_text_surface = font.render(question_text, True, (255, 255, 255))
            WIN.blit(question_text_surface, ((1600 - question_text_surface.get_width()) / 2, (900 - question_text_surface.get_height()) / 2))
            self.__MANAGER.draw_ui(WIN)
        else:
            # show user whether or not they got the question correct and award points accordingly
            pygame.draw.rect(WIN, (0, 0, 0), pygame.Rect(160, 90, self._WIDTH, self._HEIGHT))
            if self.__correct:
                text = "Correct! +200pts."
                self._points_earned += 200
            else:
                text = "Incorrect! -100pts."
                self._points_earned -= 100
            
            # record points onto database
            if not self.__record_points:
                self.record_points_on_DB(self._points_earned)
                self.__record_points = True
            
            # create text surface and draw onto screen + hide UI
            text_surface = font.render(text, True, (255, 255, 255))
            WIN.blit(text_surface, ((1600 - text_surface.get_width()) / 2, (900 - text_surface.get_height()) / 2))
            self.__ANSWER_INPUT.hide()
    
    def user_input(self, event):
        if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED and event.ui_object_id == "#answer_text_entry":
            self.__user_answer = event.text
        
        elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED and event.ui_object_id == "#answer_text_entry":
            # Checking if the answer is correct
            if self.__user_answer == self.__answer:
                self.__correct = True
            else:
                print("Incorrect!")
            self._completely_finished = True
        
        self.__MANAGER.process_events(event)
# End of code