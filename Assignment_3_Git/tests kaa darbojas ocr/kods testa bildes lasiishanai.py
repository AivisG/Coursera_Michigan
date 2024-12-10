# Pytesseract builds on and uses PIL, so let's bring in that module,
# as well as the new module pytesseract
from PIL import Image
from IPython.display import display
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# The very first thing we probably want to do is just see if we can detect
# some text. We can do that with the image_to_string function. Note, there are
# no methods here, pytesseract is a simple module with a few functions.
newspaper_article = Image.open("atteels_testam3.png")
display(newspaper_article)

# Now, let's see if we can extract the text from this image
text = pytesseract.image_to_string(newspaper_article)
print(text)