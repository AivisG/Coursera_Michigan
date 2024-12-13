import wordy
import PIL
from PIL import Image, ImageEnhance
import pytesseract
import numpy as np
import random

def clean_recognition(text):
    corrections = {
        '1': 'I',
        'l': 'I',
        '|': 'I',
        '0': 'O',
        'p': 'P',
    }
    text = text.strip()
    return corrections.get(text, text)

def solution(board: PIL.Image) -> str:
    
    global __known_pattern
    __known_pattern = np.zeros(5, dtype=str)
    known_letters = [] 
    false_letters = [] 
    played_words = []
    
    image = board
    print(type(image))
    image.show()
    
    square_size = 60
    line_width = 5
    num_columns = 5  
    num_rows = 5     
    
    results = []
    
    for row in range(num_rows):
        row_word = ""
        for col in range(num_columns):
            x = col * (square_size + line_width)
            y = row * square_size
            
            cell = image.crop((x, y, x + square_size, y + square_size))
            
            color = cell.getpixel((5, 5))
            hex_color = '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])
            if hex_color == '#000000':
                continue

            cell_gray = cell.convert("L")            

            enhancer = ImageEnhance.Contrast(cell_gray)
            enhanced_cell = enhancer.enhance(2.0)
            
            # Add sharpness enhancement
            sharpness_enhancer = ImageEnhance.Sharpness(enhanced_cell)
            enhanced_cell = sharpness_enhancer.enhance(3.0)

            resized_cell = enhanced_cell.resize((square_size * 2, square_size * 2), Image.LANCZOS)

            config = "--psm 10 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ|1l0p"
            # config2 = "--psm 10"
            
            recognized_text = pytesseract.image_to_string(resized_cell, config=config).strip()
            # recognized_text2 = pytesseract.image_to_string(resized_cell, config=config2).strip()

            result = clean_recognition(recognized_text)
            # print( "recognized text2", recognized_text2)

            results.append({
                "row": row + 1,
                "column": col + 1,
                "letter": result,
                "color": hex_color
            })
            
    
            print(f"Row {row + 1}, Column {col + 1} - Color: {hex_color}. Recognized Letter: {result}")
            row_word = row_word + result
            if col == 4:
                played_words.append(row_word)
    print("\nRaw results:")        
    print(results)
    print("\nCleaned results:")
    results_cleaned = [
        {key: value for key, value in item.items() if key != 'row'}
        for item in results
        if item['color'] not in ['#d3d3d3', '#000000'] and item['letter'] != ''
    ]
    print(results_cleaned)
    
    results_unique = []
    seen_items = set()  # Set to track unique combinations
    
    for item in results_cleaned:
        item_signature = (item['column'], item['letter'], item['color'])
        
        if item_signature not in seen_items:
            seen_items.add(item_signature)  
            results_unique.append(item)     
    
        
    print("\nUnique results:")        
    print(results_unique)
    print("\nKnown pattern:")   
    print(__known_pattern)
    
    for item in results_cleaned:
        if item['color'] == '#00274c':
            column_index = item['column'] - 1
            __known_pattern[column_index] = item['letter']
        elif item['color'] == '#ffcb05':
            known_letters.append(item['letter'])
        else:
            false_letters.append(item['letter'])    
    
    known_letters = np.array(known_letters)
    known_letters = np.unique(known_letters)
    
    print("Known Pattern:", __known_pattern)
    print("Known Letters:", known_letters)
    print("False Letters:", false_letters)
    
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    words_file = "words_very_short.txt" #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    print(type(words_file))
    with open(words_file, "r") as file:
            
        word_list: list[str] = list(set([line.strip().upper() for line in file.readlines()]))
    print("\nGanze Liste:", word_list)
    
    filtered_words = []
    
    if any(__known_pattern):
        filtered_words = [
            word for word in word_list if all(__known_pattern[i] == '' or word[i] == __known_pattern[i] for i in range(5))
            ]
        print("\n Words with known pattern:", filtered_words)
    if any(filtered_words):
        print("\n played words:", played_words)
        filtered_words = [
            word for word in filtered_words
            if word not in played_words
            ]
        print("\n List without played words:", filtered_words)
    if any(known_letters):
        filtered_words = [
            word for word in filtered_words
            if all(letter in word for letter in known_letters)
            ]
        print("\n Filtered words:", filtered_words)
            
     
    guess_list = [word for word in word_list]
    if not filtered_words:
        print("===No filtered words===")
        # known_letters = np.append(known_letters, ['P', 'I']) # This is wrong because we don't know if there was a P or an I in the last guess
        print("Known letters:", known_letters)
        guess_list = [word for word in word_list
                     if (all(letter in word for letter in known_letters)
                     and word not in played_words)]
        
    
        
    # Zeigt die ausgefilterte Liste
    print("\nFiltered words:", filtered_words)
    print("Guess list:", guess_list)
    
    if any(filtered_words):
        new_guess = random.choice(filtered_words)
    else:
        new_guess = random.choice(guess_list)
        
    print("New guess:", new_guess)
    print(type(new_guess))

    return new_guess

image = wordy.get_board_state()
    
solution(image)
