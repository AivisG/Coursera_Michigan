from PIL import Image, ImageFont, ImageDraw
import random

class Letter:
    def  __init__(self, letter: str) -> None:
        
        self.letter: str = letter
        self.in_correct_place = False
        self.in_word = False
        
        #lieliku klaat return abaas daljaas
    def is_in_correct_place(self) -> bool():
        return self.in_correct_place
        
    def is_in_word(self) -> bool():
        return self.in_word

class DisplaySpecification:
    """A dataclass for holding display specifications for WordyPy. The following
    values are defined:
         - block_width: the width of each character in pixels
         - block_height: the height of each character in pixels
         - correct_location_color: the hex code to color the block when it is correct
         - incorrect_location_color: the hex code to color the block when it is in the wrong location but exists in the string
         - incorrect_color: the hex code to color the block when it is not in the string
         - space_between_letters: the amount of padding to put between characters, in pixels
         - word_color: the hex code of the background color of the string
     """
    
    block_width: int = 80
    block_height: int = 80
    correct_location_color: str = "#00274C" #PAREIZAA VIETAA Tumshi zils
    incorrect_location_color: str = "#FFCB05" #IR VAARDAA dzeltens
    incorrect_color: str = "#D3D3D3" #NAV VAARDAA peleeks
    space_between_letters: int = 5 
    word_color: str = "#FFFFFF"
       
class Bot:
    
    def  __init__(self, word_list_file: str, display_spec: DisplaySpecification) -> None:
        self.word_list_file: str = word_list_file
        self.display_spec: DisplaySpecification = display_spec
        
        with open(self.word_list_file, "r") as file:
            self.word_list: list[str] = [line.strip().upper() for line in file.readlines()]
            
    def _tuple_to_str(self, pixels: tuple) -> str:
        """Convert an (R, G, B) tuple to a hex string for color comparison."""
        r, g, b = pixels[:3]  # Ignore alpha if present
        return f"#{r:02X}{g:02X}{b:02X}"


    def _process_image(self, guess: str, guess_Image: Image) -> list[Letter]:
        """Process the feedback image by interpreting the color blocks and updating the letter statuses."""
        letters = []
        curr_loc = 0
        num_letters = (guess_Image.width + self.display_spec.space_between_letters) // (
            self.display_spec.block_width + self.display_spec.space_between_letters
        )
        
        for i in range(num_letters):
            # Crop each letter block from the guess image
            letter_block = guess_Image.crop((
                curr_loc, 0, 
                curr_loc + self.display_spec.block_width, 
                self.display_spec.block_height
            ))

            # Get the background color of the letter block (top-left pixel as representative)
            background_color = letter_block.getpixel((0, 0))
            background_color_hex = self._tuple_to_str(background_color)

            # Create a new Letter object for the corresponding letter in the guess
            letter = Letter(guess[i])
            
            # Determine the status of the letter based on the background color
            if background_color_hex == self.display_spec.correct_location_color:
                letter.in_correct_place = True
            elif background_color_hex == self.display_spec.incorrect_location_color:
                letter.in_word = True
            else:
                # Letter is neither correct nor in the word (based on color)
                letter.in_word = False

            letters.append(letter)
            curr_loc += self.display_spec.block_width + self.display_spec.space_between_letters

        return letters
    
        
    def make_guess(self) -> str:

        guess = random.choice(self.word_list)
        print(f"Nosuutiitais vaards {guess}")
        return guess
                
    def record_guess_results(self, guess: str, guess_results: Image) -> None:
    
        guess_results = self._process_image(guess, guess_results)
    
        if guess in self.word_list:
            print(guess)
            self.word_list.remove(guess)
        
        
        pareizaa_liste = {}
        for letter in guess_results:
            # print(letter.in_correct_place)
            if letter.in_correct_place:
                print(f"burts {letter.letter} atrodas {guess.index(letter.letter)} pozicijaa guess vaardaa")
                pareizaa_liste[letter.letter] = guess.index(letter.letter)
        print(pareizaa_liste)
        
        if pareizaa_liste != {}:
            self.word_list = [word for word in self.word_list if all(position < len(word) and word[position] ==  
                                                        letter for letter, position in pareizaa_liste.items())]
            
            print(f"Liste peec skjiroshanas ar burtiem pareizajaa vietaa: {self.word_list}")  
        
        else:
            for letter in guess_results:
                if not letter.in_word:
                    print(f"Burts {letter.letter} nav meerkja vaardaa")
                    self.word_list = [word for word in self.word_list if letter.letter not in word]
        print(f"Liste peec skjiroshanas ar burtiem kuri nav meerkja vaardaa: {self.word_list}")      
                

class GameEngine:
    """The GameEngine represents a new WordPy game to play."""

    def __init__(self, display_spec: DisplaySpecification = None) -> None:
        """Creates a new WordyPy game engine. If the game_spec is None then
        the engine will use the default color and drawing values, otherwise
        it will override the defaults using the provided specification
        """
        # det the display specification to defaults or user provided values
        if display_spec == None:
            display_spec = DisplaySpecification()
        self.display_spec = display_spec

        self.err_input = False
        self.err_guess = False
        self.prev_guesses = []  # record the previous guesses

    def play(self, bot: Bot, word_list_file: str = "words-mittel.txt", target_word: str = None) -> Image:  
        """Plays a new game, using the supplied bot. By default the GameEngine
        will look in words.txt for the list of allowable words and choose one
        at random. Set the value of target_word to override this behavior and
        choose the word that must be guessed by the bot.
        """

        def format_results(results) -> str:
            """Small function to format the results into a string for quick
            review by caller.
            """
            response = ""
            for letter in results:
                if letter.is_in_correct_place():
                    response = response + letter.letter
                elif letter.is_in_word():
                    response = response + "*"
                else:
                    response = response + "?"
            return response

        # read in the dictionary of allowable words
        word_list: list(str) = list(
            map(lambda x: x.strip().upper(), open(word_list_file, "r").readlines())
        )
        # record the known correct positions
        known_letters: list(str) = [None, None, None, None, None]
        # set of unused letters
        unused_letters = set()

        # assign the target word to a member variable for use later
        if target_word is None:
            target_word = random.choice(word_list).upper()
        else:
            target_word = target_word.upper()
            if target_word not in word_list:
                print(f"Target word {target_word} must be from the word list")
                self.err_input = True
                return

        print(
            f"Playing a game of WordyPy using the word list file of {word_list_file}.\nThe target word \
                for this round is {target_word}\n"
        )

        MAX_GUESSES = 6
        for i in range(1, MAX_GUESSES):
            # ask the bot for it's guess and evaluate
            guess: str = bot.make_guess()

            # print out a line indicating what the guess was
            print(f"Evaluating bot guess of {guess}")

            if guess not in word_list:
                print(f"Guessed word {guess} must be from the word list")
                self.err_guess = True
            elif guess in self.prev_guesses:
                print("Guess word cannot be the same one as previously used!")
                self.err_guess = True

            if self.err_guess:
                return

            self.prev_guesses.append(guess)  # record the previous guess
            for j, letter in enumerate(guess):
                if letter in unused_letters:
                    print(
                        f"The bot's guess used {letter} which was previously identified as not used!"
                    )
                    self.err_guess = True
                if known_letters[j] is not None:
                    if letter != known_letters[j]:
                        print(
                            f"Previously identified {known_letters[j]} in the correct position is not used at position {j}!"
                        )
                        self.err_guess = True

                if self.err_guess:
                    return

            # get the results of the guess
            correct, results = self._set_feedback(guess, target_word)

            # print out a line indicating whether the guess was correct or not
            print(f"Was this guess correct? {correct}")

            # get the image to be returned to the caller
            img = self._format_results(results)

            print("Sending guess results to bot:\n")
            
            img.show()

            bot.record_guess_results(guess, img)

            # if they got it correct we can just end
            if correct:
                print(f"Great job, you found the target word in {i} guesses!")
                return

        # if we get here, the bot didn't guess the word
        print("Thanks for playing! You didn't find the target word in the number of guesses allowed.")
        return

    def _set_feedback(self, guess: str, target_word: str) -> tuple[bool, list[Letter]]:
        # whether the complete guess is correct
        # set it to True initially and then switch it to False if any letter doesn't match
        correct: bool = True

        letters = []
        for j in range(len(guess)):
            # create a new Letter object
            letter = Letter(guess[j])

            # check to see if this character is in the same position in the
            # guess and if so set the in_correct_place attribute
            if guess[j] == target_word[j]:
                letter.in_correct_place = True
                print(f"Tests. sheit burts {guess[j]} tika atziits par in_correct_place")
            else:
                # we know they don't have a perfect answer, so let's update
                # our correct variable for feedback
                correct = False

            # check to see if this character is anywhere in the word
            if guess[j] in target_word:
                letter.in_word = True
                print(f"Tests. sheit burts {guess[j]} tika atziits par in_word")
            # add this letter to our list of letters
            letters.append(letter)

        return correct, letters

    def _render_letter(self, letter: Letter) -> Image:
        """This function renders a single Letter object as an image."""
        # set color string as appropriate
        
        print(f"Sheit burts {letter.letter} ir nonaacis _render_letter lai sanjemtu kraasu.")
        print(f"Sheit burta {letter.letter} statuss pareizajaa vietaa ir {letter.in_correct_place}.")
        print(f"Sheit burta {letter.letter} statuss pareizajaa vietaa ir {letter.in_word}.")

        color: str = self.display_spec.incorrect_color
        if letter.is_in_correct_place():
            color = self.display_spec.correct_location_color
        elif letter.is_in_word():
            color = self.display_spec.incorrect_location_color

        # now we create a new image of width x height with the given color
        block = Image.new(
            "RGB",
            (self.display_spec.block_width, self.display_spec.block_height),
            color=color,
        )
        # and we actually render that image and get a handle back
        draw = ImageDraw.Draw(block)

        # for the lettering we need to identify the center of the block,
        # so we calculate that as the (X,Y) position to render text
        X: int = self.display_spec.block_width // 2
        Y: int = self.display_spec.block_height // 2

        # we will create a font object for drawing lettering
        FONT_SIZE: int = 50
        #IZNJEEMU SHEIT LAUKAA un ieliku citu font = ImageFont.truetype("assets/roboto_font/Roboto-Bold.ttf", FONT_SIZE)
        
        try:
            font = ImageFont.truetype("assets/roboto_font/Roboto-Bold.ttf", FONT_SIZE)
        except OSError:
            print("Roboto font not found, using default font.")
            font = ImageFont.load_default()  # Use default font if Roboto is not available
            
        #liidz shejienei
            
        # now we can draw the letter and tell PIL we want to have the
        # character centered in the box using the anchor attribute
        draw.text((X, Y), letter.letter, size=FONT_SIZE, anchor="mm", font=font)
        
        def rgb_to_hex(rgb):
            return "#{:02X}{:02X}{:02X}".format(rgb[0], rgb[1], rgb[2])
        colorcolor = block.getpixel((5,5))
        colorcolorHEX = rgb_to_hex(colorcolor)
        print(f"Kvadraata kraasa: {colorcolorHEX}")
        
        
        return block

    def _format_results(self, letters: list[Letter]) -> Image:
        """This function does the hard work of converting the list[Letter]
        for a guess into an image.
        """
        # some constants that determine what a word of these letters
        # will look like. The algorithm for rendering a word is that
        # we will render each letter independently and put some spacing between
        # them. This means the total word width is equal to the size of
        # all of the letters and the spacing, and the word height is equal
        # to the size of just a single letter
        WORD_WIDTH: int = (len(letters) * self.display_spec.block_width) + (
            len(letters) - 1
        ) * self.display_spec.space_between_letters
        WORD_HEIGHT: int = self.display_spec.block_height

        # we can use the paste() function to place one PIL.Image on top
        # of another PIL.Image
        word = Image.new(
            "RGB", (WORD_WIDTH, WORD_HEIGHT), color=self.display_spec.word_color
        )
        curr_loc = 0
        for letter in letters:
            # we can render the letter and then paste, setting the location
            # as X,Y position we want to paste it in
            rendered_letter: Image = self._render_letter(letter)
            word.paste(rendered_letter, (curr_loc, 0))
            curr_loc += (
                self.display_spec.block_width + self.display_spec.space_between_letters
            )

        return word
    
words_file = "words_mittel.txt"

# Create a new GameEngine with the default DisplaySpecification
ge = GameEngine()

# # Initialize the student Bot
bot = Bot(words_file, ge.display_spec)

ge.play(bot, word_list_file=words_file)