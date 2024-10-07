from flask import Flask, render_template, request
from googletrans import Translator, LANGUAGES
from langdetect import detect, DetectorFactory
import nltk
from nltk.stem import PorterStemmer, WordNetLemmatizer

DetectorFactory.seed = 0  # For consistent language detection
app = Flask(__name__)
translation_history = []
favorites = []

# Download required NLTK resources (only need to run once)
nltk.download('punkt')
nltk.download('wordnet')

def detect_and_translate(text, target_lang):
    try:
        # Detect language
        result_lang = detect(text)

        # Translate language
        translator = Translator()
        translate_text = translator.translate(text, dest=target_lang).text

        return result_lang, translate_text
    except Exception as e:
        print(f"Error: {e}")
        return None, "Translation failed. Please try again."

def stem_and_lemmatize(text):
    stemmer = PorterStemmer()
    lemmatizer = WordNetLemmatizer()
    words = nltk.word_tokenize(text)
    stemmed_words = [stemmer.stem(word) for word in words]
    lemmatized_words = [lemmatizer.lemmatize(word) for word in words]
    return ' '.join(stemmed_words), ' '.join(lemmatized_words)

@app.route('/')
def index():
    return render_template('index.html', languages=LANGUAGES, history=translation_history, favorites=favorites)

@app.route('/trans', methods=['POST'])
def trans():
    translation = ""
    detected_lang = ""
    if request.method == 'POST':
        text = request.form['text']
        target_lang = request.form['target_lang']

        # Apply stemming and lemmatization
        stemmed_text, lemmatized_text = stem_and_lemmatize(text)

        detected_lang, translation = detect_and_translate(text, target_lang)

        translation_history.append({
            'original': text,
            'stemmed': stemmed_text,
            'lemmatized': lemmatized_text,
            'detected': detected_lang,
            'translated': translation,
            'target_lang': target_lang
        })

    return render_template('index.html', translation=translation, detected_lang=detected_lang, languages=LANGUAGES, history=translation_history, favorites=favorites)

@app.route('/favorite/<int:history_index>')
def favorite(history_index):
    if 0 <= history_index < len(translation_history):
        if translation_history[history_index] not in favorites:
            favorites.append(translation_history[history_index])
    return index()

@app.route('/download/<int:history_index>')
def download(history_index):
    if 0 <= history_index < len(translation_history):
        translation_record = translation_history[history_index]
        content = (f"Original: {translation_record['original']}\n"
                   f"Stemmed: {translation_record['stemmed']}\n"
                   f"Lemmatized: {translation_record['lemmatized']}\n"
                   f"Detected Language: {translation_record['detected']}\n"
                   f"Translation: {translation_record['translated']}")
        
        file_path = f"translation_{history_index}.txt"
        with open(file_path, 'w') as file:
            file.write(content)
        
        return f"Download your translation <a href='/{file_path}'>here</a>."
    return "Translation not found."

@app.route('/clear_history')
def clear_history():
    global translation_history
    translation_history = []  # Clear the translation history
    return index()

if __name__ == '__main__':
    app.run(debug=True)
