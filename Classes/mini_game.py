from functions import (get_image, split_text, draw_circle,
                       draw_slanted_line, draw_vertical_line, draw_rect)
from dataclasses import dataclass
import random
import time
import pygame

RPS_OPTIONS = ('rock', 'paper', 'scissors')


class MainGame:
    def __init__(self, game) -> None:
        self.game = game

        self.mid_w = self.game.DISPLAY_W // 2
        self.mid_h = self.game.DISPLAY_H // 2

        self.run_display, self.show_rules, self.running = True, True, False
        self.total_attempts = 0
        self.attempt = 0
        self.correct = 0
        self.incorrect = 0
        self.tie = 0
        self.title = ''
        self.rules = ''

        self.game_rules = {
            'rps': {
                'title': 'Rock Paper Scissor',
                'rules': (
                    "In Rock, Paper, Scissors, two players"
                    " each choose one of three options: "
                    "Rock, Paper, or Scissors. Rock beats"
                    " Scissors, Scissors beats Paper, and "
                    "Paper beats Rock. If both players choose"
                    " the same option, the round is a tie. "
                    "The game is usually played in multiple"
                    " rounds, and the player with the most wins "
                    "is the overall winner."
                ),
                'total_attempts': {
                    'easy': 3,
                    'medium': 2,
                    'hard': 1
                }
            },
            'hangman': {
                'title': 'Hangman',
                'rules': (
                    "In Hangman, one player chooses a word,"
                    " and the others guess letters to reveal it. "
                    "Correct guesses fill in blanks, while"
                    " wrong guesses bring the hangman closer to completion. "
                    "The goal: guess the word before the drawing is finished!"
                ),
            },
            'binarize': {
                'title': 'Binarize',
                'rules': (
                    "In Binarize, players convert decimal numbers"
                    " into binary. The goal: accurately transform "
                    "random decimal numbers into their binary"
                    " equivalents and test your binary conversion skills!"
                )
            },
            'encrypter': {
                'title': 'Encrypter',
                'rules': (
                    "In Encrypter, players decode a message"
                    " using a given encryption method, with clues like "
                    '"only HEXES will save you, B=2." Alternatively,'
                    ' players encode messages following specific rules. '
                    "The goal: master cryptography through decoding"
                    " and encoding challenges!"
                )
            },
            'math_champ': {
                'title': 'Math Champ',
                'rules': (
                    "In Math Champ, players solve equations"
                    " like A + A = 4 or B + A = 7 by deducing the values of "
                    "the variables. The goal: use logic and "
                    "problem-solving skills to figure out the correct values!"
                )
            }
        }

    def configure(self) -> None:
        self.reset_game()
        self.total_attempts = self.get_rule_value('total_attempts')
        self.title = self.get_rule_value('title')
        self.rules = self.get_rule_value('rules')

    def reset_game(self) -> None:
        self.total_attempts = 0
        self.attempt = 0
        self.correct = 0
        self.incorrect = 0
        self.tie = 0
        self.title = ''
        self.rules = ''

    def get_rule_value(self, column_name: str):
        rule = self.game_rules.get(self.game.game_mode, {}).get(column_name)
        if isinstance(rule, dict):
            return rule.get(self.game.difficulty, 1)
        return rule

    def blit_screen(self) -> None:
        self.game.window.blit(self.game.display, (0, 0))
        pygame.display.update()
        self.game.reset_keys()

    def display_rules(self) -> None:
        self.show_rules = True
        font_size = 30
        line_height = font_size + 5

        lines = split_text(
            self.rules,
            self.game.second_font,
            font_size,
            self.mid_w
        )

        while self.show_rules:
            self.game.check_events()

            if self.game.START_KEY:
                self.show_rules = False

            self.game.display.fill(self.game.BLACK)

            for idx, line in enumerate(lines):
                y = (self.mid_h - len(lines) *
                     line_height // 2 + idx * line_height)
                self.game.draw_text(
                    line,
                    font_size,
                    self.mid_w,
                    y,
                    font=self.game.second_font,
                    color=self.game.WHITE,
                    position='center'
                )

            self.game.draw_text(
                self.title,
                50,
                self.mid_w,
                self.mid_h - 200,
                font=self.game.second_font,
                color=self.game.RED,
                position='center'
            )
            self.game.proceed('PLAY')
            self.blit_screen()


class RPSGame(MainGame):
    def __init__(self, game) -> None:
        MainGame.__init__(self, game)
        self.is_winner = False
        self.user_selected = False
        self.state = 'paper'
        self.random_option = False
        self.show_animation = False

        self.result_text = {
            None: ('Tie', self.game.WHITE),
            True: ('You Win', self.game.GREEN),
            False: ('You Lose', self.game.RED)
        }

        # small right options
        sm_w, sm_h, gap = 150, 150, 175

        self.s_rock = Hand(
            game,
            'rock',
            sm_w,
            sm_h,
            (self.game.DISPLAY_W - sm_w) // 2 - gap,
            (self.game.DISPLAY_H - sm_w) // 2
        )

        self.s_paper = Hand(
            game,
            'paper',
            sm_w,
            sm_h,
            (self.game.DISPLAY_W - sm_w) // 2,
            (self.game.DISPLAY_H - sm_w) // 2
        )

        self.s_scissors = Hand(
            game,
            'scissors',
            sm_w,
            sm_h,
            (self.game.DISPLAY_W - sm_w) // 2 + gap,
            (self.game.DISPLAY_H - sm_w) // 2
        )

        # large right options
        lg_w, lg_h = 500, 500

        self.r_rock = Hand(
            game,
            'rock',
            lg_w,
            lg_h,
            self.game.DISPLAY_W - 400,
            self.mid_h // 2
        )

        self.r_paper = Hand(
            game,
            'paper',
            lg_w,
            lg_h,
            self.game.DISPLAY_W - 450,
            self.mid_h // 2
        )

        self.r_scissors = Hand(
            game,
            'scissors',
            lg_w,
            lg_h,
            self.game.DISPLAY_W - 450,
            self.mid_h // 2
        )

        # large left options
        self.l_rock = Hand(
            game,
            'rock',
            lg_w, lg_h, -100,
            self.mid_h // 2,
            True
        )

        self.l_paper = Hand(
            game,
            'paper',
            lg_w,
            lg_h,
            -50,
            self.mid_h // 2,
            True
        )

        self.l_scissors = Hand(
            game,
            'scissors',
            lg_w,
            lg_h,
            -50,
            self.mid_h // 2,
            True
        )

        self.options = {
            'paper': self.s_paper,
            'rock': self.s_rock,
            'scissors': self.s_scissors,
            'r_paper': self.r_paper,
            'r_rock': self.r_rock,
            'r_scissors': self.r_scissors,
            'l_paper': self.l_paper,
            'l_rock': self.l_rock,
            'l_scissors': self.l_scissors
        }

    def play(self) -> None:
        self.run_display = True
        while self.run_display:
            self.user_selected = False
            self.game.display.fill(self.game.BLACK)

            self.random_option = random.choice(RPS_OPTIONS)
            self.display_menu()
            self.display_score()

            if self.user_selected:
                self.attempt += 1
                self.did_user_win()
                self.display_result()

                if self.attempt == self.total_attempts or self.is_winner:
                    self.run_display = False

            self.blit_screen()

    def did_user_win(self) -> None:
        if self.state == self.random_option:
            self.is_winner = None
            self.tie += 1
        elif (self.state == 'rock' and self.random_option == 'scissors') or \
                (self.state == 'paper' and self.random_option == 'rock') or \
                (self.state == 'scissors' and self.random_option == 'paper'):
            self.is_winner = True
            self.correct += 1
        else:
            self.is_winner = False
            self.incorrect += 1

    def display_menu(self) -> None:
        self.game.check_events()
        self.check_input()
        self.draw_options()

    def display_result(self) -> None:
        self.display_animation()

        start_time = time.time()
        while time.time() - start_time < 2:
            self.game.display.fill(self.game.BLACK)

            # display right and left large hand selected by user and game
            self.options[f'r_{self.state}'].draw()
            self.options[f'l_{self.random_option}'].draw()

            # Display result text
            text, color = self.result_text[self.is_winner]

            self.game.draw_text(
                text,
                30,
                self.mid_w,
                self.mid_h,
                position='center',
                color=color
            )

            self.blit_screen()

    def display_score(self) -> None:
        self.game.draw_text(
            self.incorrect,
            50,
            15,
            10,
            color=self.game.RED
        )

        self.game.draw_text(
            self.correct,
            50,
            self.game.DISPLAY_W - 15,
            10,
            color=self.game.GREEN,
            position='topright'
        )

        self.game.draw_text(
            self.tie,
            50,
            self.game.DISPLAY_W // 2, 40,
            color=self.game.ORANGE,
            position='center'
        )

    def display_animation(self) -> None:
        start_time = time.time()

        cycles = 2
        cycle_height = 250
        cycle_duration = 0.25

        original_left_y = self.l_rock.rect.y
        original_right_y = self.r_rock.rect.y

        # Perform the animation
        self.show_animation = True
        while self.show_animation:
            elapsed_time = time.time() - start_time
            cycle_phase = ((elapsed_time % cycle_duration) /
                           (cycle_duration / 2))

            # check if time is not done max 2 sec and reset to default
            if elapsed_time > cycles * cycle_duration:
                self.show_animation = False
                self.l_rock.rect.y = original_left_y
                self.r_rock.rect.y = original_right_y
                break

            # Calculate vertical offset based on cycle phase
            if cycle_phase <= 1:
                offset = int(cycle_height * cycle_phase)  # Moving up
            else:
                offset = int(cycle_height * (2 - cycle_phase))  # Moving down

            # Apply the offset to the rock positions
            self.l_rock.rect.y = original_left_y - offset
            self.r_rock.rect.y = original_right_y - offset

            # Render the updated positions
            self.game.display.fill(self.game.BLACK)
            self.display_large_hands()
            self.blit_screen()

    def draw_options(self) -> None:
        option = self.options[self.state]

        pygame.draw.rect(
            self.game.display,
            option.border_color,
            option.rect,
            option.border_width
        )

        self.s_rock.draw()
        self.s_paper.draw()
        self.s_scissors.draw()

        self.display_large_hands()

    def move_cursor(self) -> None:
        # get index of user selected option of (rock, paper, scissors)
        current_index = RPS_OPTIONS.index(self.state)

        # check if user clicks left or to the right
        # set current selected option
        if self.game.LEFT_KEY:
            self.state = RPS_OPTIONS[(current_index - 1) % len(RPS_OPTIONS)]
        elif self.game.RIGHT_KEY:
            self.state = RPS_OPTIONS[(current_index + 1) % len(RPS_OPTIONS)]

    def check_input(self) -> None:
        self.move_cursor()
        if self.game.START_KEY:
            self.user_selected = self.state

    def display_large_hands(self) -> None:
        self.r_rock.draw()
        self.l_rock.draw()


class Hand:
    def __init__(self, game, hand_type, w, h, x, y, left_handed=False) -> None:
        if hand_type not in RPS_OPTIONS:
            raise ValueError('Hand type is not valid!')

        self.game = game
        self.type = hand_type
        self.left_handed = left_handed
        self.w, self.h, self.x, self.y = w, h, x, y

        self.__loaded_img = get_image(
            (f'l_{self.type}' if self.left_handed else f'{self.type}') + '.png'
        )

        self.img = pygame.transform.scale(self.__loaded_img, (self.w, self.h))
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.border_color = self.game.RED
        self.border_width = 5

    def draw(self) -> None:
        self.game.display.blit(self.img, self.rect)


@dataclass
class Alphabet:
    name: str
    x: int
    y: int
    h: int
    w: int
    is_used: bool = False
    is_guessed: bool = False


class HangmanGame(MainGame):
    def __init__(self, game):
        MainGame.__init__(self, game)
        self.is_winner = False
        self.state = False
        self.word = None
        self.alphabet_objects = {}
        self.used_options = []
        self.alphabet = list('abcdefghijklmnopqrstuvwxyz')

        x, y = 20, 20
        for letter in self.alphabet:

            self.alphabet_objects[letter] = Alphabet(
                name=letter.upper(),
                x=x,
                y=y,
                h=35,
                w=35
            )

            x += 30

    def play(self) -> None:
        self.word = self.get_random_word(self.game.difficulty)
        self.run_display = True
        while self.run_display:
            self.check_input()
            self.game.display.fill(self.game.WHITE)

            self.game.draw_text(
                'Gues the word or he will die',
                30,
                self.mid_w,
                75,
                position='center',
                color=self.game.RED
            )

            self.draw_gallows()
            self.draw_word_lines()
            self.draw_options()

            self.blit_screen()

            self.did_user_win()

    def did_user_win(self) -> None:
        if self.incorrect >= 6:
            self.run_display = False
            self.is_winner = False
            return

        for char in self.word:
            if not self.alphabet_objects[char].is_guessed:
                return

        self.run_display = False
        self.is_winner = True

    def draw_options(self) -> None:

        rect_x = 50
        rect_y = self.game.DISPLAY_H - 90
        rect_width = 40
        rect_height = 40

        step = ((self.game.DISPLAY_W - (len(self.alphabet_objects) * 3.5))
                / len(self.alphabet_objects))

        for char in self.alphabet_objects.values():
            color = self.game.WHITE
            if char.is_used:
                color = self.game.RED

            self.game.draw_text(
                char.name,
                24,
                (rect_x + rect_width // 2) + 2,
                (rect_y + rect_height // 2) - 2.5,
                position='center',
                color=color
            )

            rect_x += step

        self.blit_screen()

    def check_input(self) -> None:
        self.game.check_events()

        for char in self.game.OTHER_KEY:
            if char in self.alphabet_objects:
                if not self.alphabet_objects[char].is_used:
                    self.alphabet_objects[char].is_used = True

                    if char in self.word:
                        self.alphabet_objects[char].is_guessed = True

                    if char not in self.word:
                        self.incorrect += 1

    def draw_gallows(self):
        display = self.game.display
        black = self.game.BLACK
        dw, dh = self.game.DISPLAY_W, self.game.DISPLAY_H

        # Draw base structure
        pygame.draw.rect(
            display,
            black,
            (0, dh - 250, dw, dh)
        )  # Horizontal bottom line

        pygame.draw.rect(
            display,
            black,
            (dw - 475, 200, 15, 275)
        )  # Vertical right long line

        pygame.draw.line(
            display,
            black,
            (750, dh - 525),
            (810, dh - 450), 15
        )  # Slanted line

        pygame.draw.rect(
            display,
            black,
            (650, dh - 525, 170, 10)
        )  # Horizontal top line

        pygame.draw.rect(
            display,
            black,
            (650, 200, 15, 50)
        )  # Vertical top line

        # Draw hangman parts incrementally
        if self.incorrect >= 1:
            draw_circle(
                self.game.display,
                (657, 275),
                25,
                5,
                self.game.RED
            )  # Head

        if self.incorrect >= 2:
            draw_vertical_line(
                self.game.display,
                (657, 300),
                100,
                5,
                self.game.RED
            )  # Body

        if self.incorrect >= 3:
            draw_slanted_line(
                self.game.display,
                (657, 315),
                (-50, 50),
                7,
                self.game.RED
            )  # Left arm

        if self.incorrect >= 4:
            draw_slanted_line(
                self.game.display,
                (657, 315),
                (50, 50),
                7,
                self.game.RED
            )  # Right arm

        if self.incorrect >= 5:
            draw_slanted_line(
                self.game.display,
                (657, 400),
                (-50, 50),
                7,
                self.game.RED
            )  # Left leg

        if self.incorrect >= 6:
            draw_slanted_line(
                self.game.display,
                (657, 400),
                (50, 50),
                7,
                self.game.RED
            )  # Right leg

    def draw_word_lines(self):
        word = self.word
        display = self.game.display

        line_length = 60
        space_between_lines = 15
        start_x = (self.game.DISPLAY_W // 2 -
                   (len(word) * (line_length +
                                 space_between_lines)) // 2)

        start_y = 575
        f_size = 40

        # Draw lines for each letter in the word
        for i, char in enumerate(word):
            # Get the corresponding alphabet object for the character
            char_obj = self.alphabet_objects[char]

            # Draw the line for the current character
            # (even if it's not guessed yet)
            pygame.draw.line(
                display,
                self.game.WHITE,
                (start_x + i * (line_length +
                                space_between_lines), start_y),
                (start_x + i * (line_length +
                                space_between_lines) + line_length, start_y),
                3
            )

            # If the character has been guessed, display it
            if char_obj.is_guessed:
                # Calculate the width of the character to center it on the line
                font = pygame.font.Font(self.game.font, f_size)

                # Get both width and height
                char_width, char_height = font.size(char)

                # Calculate the x-coordinate to center the text
                char_x = (start_x + i * (line_length + space_between_lines)
                          + (line_length - char_width) // 2)

                self.game.draw_text(
                    char,
                    f_size,
                    char_x,
                    start_y - 50,
                    color=self.game.WHITE,
                    position='topleft'
                )

    def get_random_word(self, difficulty):
        words = {
            'easy': ['cat',
                     'dog',
                     'hat',
                     'sun',
                     'ball',
                     'apple',
                     'tree',
                     'star',
                     'fish',
                     'moon'
                     ],
            'medium': ['jungle',
                       'monkey',
                       'puzzle',
                       'bridge',
                       'shadow',
                       'river',
                       'ocean',
                       'laptop',
                       'forest',
                       'mountain'
                       ],
            'hard': ['pneumonia',
                     'subterranean',
                     'juxtaposition',
                     'xylophone',
                     'quizzical',
                     'antidisestablishmentarianism',
                     'cryptography',
                     'neuroplasticity',
                     'photosynthesis',
                     'hippopotomonstrosesquipedaliophobia'
                     ],
        }
        return random.choice(words[difficulty])


class QuizGame(MainGame):
    def __init__(self, game):
        super().__init__(game)
        self.game = game
        self.question = None
        self.options = None
        self.correct_key = None
        self.is_winner = False
        self.answer = None
        self.helper = None
        self.a, self.b, self.c, self.d = False, False, False, False

    def play(self):
        """Method to be overridden in child classes if custom logic is needed."""
        while self.run_display:
            self.check_input()
            self.game.display.fill(self.game.BLACK)

            self.draw_options()
            self.helper()
            self.did_user_win()

            self.blit_screen()

    def check_input(self):
        """Handles input to determine which option is selected."""
        self.game.check_events()
        if 'a' in self.game.OTHER_KEY:
            self.a = True
        elif 'b' in self.game.OTHER_KEY:
            self.b = True
        elif 'c' in self.game.OTHER_KEY:
            self.c = True
        elif 'd' in self.game.OTHER_KEY:
            self.d = True

        if self.a or self.b or self.c or self.d:
            self.run_display = False

    def did_user_win(self):
        """Checks if the user selected the correct option."""
        if self.a and self.correct_key == 'A':
            self.is_winner = True
        elif self.b and self.correct_key == 'B':
            self.is_winner = True
        elif self.c and self.correct_key == 'C':
            self.is_winner = True
        elif self.d and self.correct_key == 'D':
            self.is_winner = True


    def draw_options(self):
        """Displays the question and options on the screen."""
        options_rects = [
            {"pos": (100, 100), "size": (200, 50), "text": "A "},
            {"pos": (100, 200), "size": (200, 50), "text": "B "},
            {"pos": (100, 300), "size": (200, 50), "text": "C "},
            {"pos": (100, 400), "size": (200, 50), "text": "D "},
        ]

        # Display the question
        self.game.draw_text(
            f'Question: {self.question}', 40,
            self.game.DISPLAY_W / 2, 50,
            color=self.game.ORANGE, position='center', font=self.game.second_font
        )

        # Draw the options
        for i, option in enumerate(options_rects):
            key = list(self.options.keys())[i]
            text = f"{key}: {self.options[key]}"

            # Draw the rectangle
            draw_rect(
                self.game.display,
                option["pos"],
                option["size"],
                self.game.BLACK,
                border_thickness=2,
                border_color=self.game.WHITE,
            )

            # Add text inside the rectangle
            x, y = (option["pos"][0] + 10, option["pos"][1] + 10)  # Adjust text position
            self.game.draw_text(text, 25, x, y, color=self.game.WHITE, font=self.game.second_font)


class MathChampGame(QuizGame):
    def __init__(self, game):
        super().__init__(game)
        self.game = game

    def play(self):
        """Override to include math-specific equation generation."""
        self.generate_equation(self.game.difficulty)
        super().play()

    def generate_equation(self, game_mode):
        """Generates a math equation and populates options."""
        values = {
            "A": 2,
            "B": 3,
            "C": 5,
            "D": 7,
            "E": 11
        }

        difficulty = {
            'easy': 2,
            'medium': 3,
            'hard': 4
        }

        num_variables = difficulty[game_mode]
        chosen_vars = random.sample(list(values.items()), num_variables)

        equation_str = " + ".join([f"{var}" for var, _ in chosen_vars])
        equation_result = sum([val for _, val in chosen_vars])

        options = set()
        while len(options) < 3:
            incorrect = random.randint(equation_result - 4, equation_result + 4)
            if incorrect != equation_result:
                options.add(incorrect)

        options = list(options)
        options.append(equation_result)
        random.shuffle(options)

        self.options = {
            "A": options[0],
            "B": options[1],
            "C": options[2],
            "D": options[3],
        }

        correct_option_key = list(self.options.keys())[options.index(equation_result)]
        self.question, self.answer, self.correct_key = equation_str, equation_result, correct_option_key
        self.helper = self.draw_helper

    def draw_helper(self):
        values = {
            "A": 2,
            "B": 3,
            "C": 5,
            "D": 7,
            "E": 11
        }

        # Calculations to display
        calculations = [
            f'A + A = {values["A"] + values["A"]}',
            f'B + A = {values["B"] + values["A"]}',
            f'B + C = {values["B"] + values["C"]}',
            f'C + D = {values["D"] + values["C"]}',
            f'D + E = {values["D"] + values["E"]}'
        ]

        for i, calc in enumerate(calculations, 1):
            self.game.draw_text(calc, 25, self.game.DISPLAY_W - 150, (i * 50), color=self.game.WHITE,
                                font=self.game.second_font)


class BinaryConversionGame(QuizGame):
    def __init__(self, game):
        super().__init__(game)
        self.game = game

    def play(self):
        """Override to include binary-specific logic generation."""
        self.generate_binary_question()
        super().play()

    def generate_binary_question(self):
        """Generates a binary question with multiple-choice options."""
        # Generate a random binary value within a defined range
        num_bits = random.randint(4, 8)  # Generate between 4 to 8 bits
        binary_value = ''.join(random.choices(['0', '1'], k=num_bits))
        decimal_value = int(binary_value, 2)

        # Generate incorrect options
        options = set()
        while len(options) < 3:
            incorrect = random.randint(decimal_value - 10, decimal_value + 10)
            if incorrect != decimal_value:
                options.add(incorrect)

        # Combine correct and incorrect options
        options = list(options)
        options.append(decimal_value)
        random.shuffle(options)

        # Assign to class properties
        self.options = {
            "A": options[0],
            "B": options[1],
            "C": options[2],
            "D": options[3],
        }
        correct_option_key = list(self.options.keys())[options.index(decimal_value)]

        # Set question and answer
        self.question = f"What is the decimal equivalent of {binary_value}?"
        self.answer = decimal_value
        self.correct_key = correct_option_key
        self.helper = self.draw_helper

    def draw_helper(self):
        """Provide helper information to teach binary conversion."""
        # Example conversion for illustration
        binary_example = "1011"
        decimal_example = int(binary_example, 2)

        # Helper display
        helper_text = [
            f"Hint: Binary {binary_example} = Decimal {decimal_example}.",
            "Each binary digit (bit) represents a power of 2, starting from the right:",
            "For example, from right to left:",
            f"  1 (2^3) + 0 (2^2) + 1 (2^1) + 1 (2^0) = {decimal_example}",
            "Step-by-step: Start with the rightmost bit and multiply it by 2^0, the next by 2^1, and so on.",
            "Then, add up the results to get the decimal value.",
            "For binary 1011, you get: 1*8 + 0*4 + 1*2 + 1*1 = 11 in decimal.",
            "Remember: 1 represents 'on' (or 'true'), and 0 represents 'off' (or 'false')."
        ]

        for i, text in enumerate(helper_text, 1):
            self.game.draw_text(text, 20, self.game.DISPLAY_W - 50, (i * 30) + 50, color=self.game.WHITE, font=self.game.second_font, position='topright')


class WordDecryptionGame(QuizGame):
    def __init__(self, game):
        super().__init__(game)
        self.game = game
        self.encryption_method = None
        self.hints_enabled = True

    def play(self):
        """Override to include decryption-specific game logic."""
        self.generate_encrypted_challenge()
        super().play()

    def generate_encrypted_challenge(self):
        """Generates a hex-based encrypted word or sentence with options."""
        # Predefined hex-based options
        hex_easy_options = [
            {"YOU": "19-F-15"},
            {"MINE": "D-9-E-5"},
            {"DATA": "4-1-14-1"}
        ]

        hex_medium_options = [
            {"I": "9", "SEE": "13-5-5", "YOU": "19-F-15"},
            {"NOT": "E-F-14", "ENOUGH": "5-E-F-15-7-8", "TIME": "14-9-D-5"},
            {"NOT": "E-F-14", "SAFE": "13-1-6-5", "HERE": "8-13-12"}
        ]

        hex_hard_options = [
            {"YOUR": "19-F-15-12", "DATA": "4-1-14-1", "IS": "9-13", "MINE": "D-9-E-5"},
            {"TIME": "14-9-D-5", "IS": "9-13", "RUNNING": "17-15-E-5-9-14-7", "OUT": "F-15-21-14"},
            {"QUIT": "11-15-9-14", "WHILE": "17-8-9-5", "YOU": "19-F-15", "CAN": "3-1-E"}
        ]

        # Select options based on difficulty
        if self.game.difficulty == "easy":
            options_set = random.choice(hex_easy_options)
        elif self.game.difficulty == "medium":
            options_set = random.choice(hex_medium_options)
        elif self.game.difficulty == "hard":
            options_set = random.choice(hex_hard_options)
        else:
            raise ValueError("Invalid difficulty level")

        # Prepare encrypted word and correct answer
        encrypted_word = random.choice(list(options_set.values()))
        original_word = [key for key, value in options_set.items() if value == encrypted_word][0]

        # Generate distractors
        distractors = [key for key in options_set.keys() if key != original_word]

        # Add default distractors if necessary
        default_distractors = ["ALPHA", "BETA", "DELTA", "OMEGA"]
        while len(distractors) < 3:
            distractors.append(random.choice(default_distractors))

        # Combine correct answer and distractors
        options = [original_word] + distractors[:3]  # Ensure exactly 4 options
        random.shuffle(options)

        # Assign to class properties
        self.options = {
            "A": options[0],
            "B": options[1],
            "C": options[2],
            "D": options[3],
        }
        correct_option_key = list(self.options.keys())[options.index(original_word)]

        # Set question and answer
        self.question = f"Decrypt this hex: {encrypted_word}"
        self.answer = original_word
        self.correct_key = correct_option_key
        self.helper = self.draw_helper
        self.encryption_method = "Hexadecimal Encoding"

    def draw_helper(self):
        """Provide optional hints for hexadecimal encoding."""
        if not self.hints_enabled:
            return

        # Explain hexadecimal encoding
        hints = [
            "Hint: Hexadecimal encoding uses numbers 0-9 ",
            "and letters A-F to represent values.",
            "Hint: Each hexadecimal value corresponds to a character,",
            " where 'A' = 1, 'B' = 2, and so on.",
            "Hint: Convert each hex digit to its decimal equivalent and",
            " then map it to the corresponding letter in the alphabet.",
            "Tip: For example, 'A' in hexadecimal is 1 in decimal,",
            " 'B' is 2, 'C' is 3, and so on until 'F' = 15.",
            "Tip: If you see something like 'D-9-E-5',",
            " try converting each value separately and then combine the results to form a word."
        ]

        for i, hint in enumerate(hints, 1):
            self.game.draw_text(hint, 20, self.game.DISPLAY_W - 50, (i * 30) + 50, color=self.game.WHITE, font=self.game.second_font, position='topright')

