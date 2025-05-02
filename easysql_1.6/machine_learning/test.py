import os
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Embedding, LSTM, Bidirectional, Dense
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Sequential, model_from_json
import re
import pickle
import matplotlib.pyplot as plt


def preprocess_pipeline(data):
    sentences = data.split('\n')
    index = 0
    for i in sentences:
        if i:
            sentences[index] = re.sub(r'^\[\d{2}/\d{2}/\d{4} \d{1,2}:\d{2}:\d{2} [AP]M\] ', '', i.upper())
            index += 1
    return sentences[:index]


def train_store():
    input_file = "/home/bibhas/Documents/EASYSQL/T13/easysql_1.6/generalize_queries2.txt"
    with open(input_file, 'r', encoding='utf-8') as file:
        data = file.read()

    os.system('clear')  # Change 'cls' to 'clear' for Linux/macOS

    tokenize_sentences = preprocess_pipeline(data)
    tokenizer = Tokenizer(oov_token='<oov>', filters='')
    tokenizer.fit_on_texts(tokenize_sentences)

    total_words = len(tokenizer.word_index) + 1

    input_sequences = []
    for line in tokenize_sentences:
        token_list = tokenizer.texts_to_sequences([line])[0]
        for i in range(1, len(token_list)):
            input_sequences.append(token_list[:i + 1])

    max_sequence_len = max(len(x) for x in input_sequences)
    input_sequences = np.array(pad_sequences(input_sequences, maxlen=max_sequence_len, padding='pre'))

    X, label = input_sequences[:, :-1], input_sequences[:, -1]
    ys = tf.keras.utils.to_categorical(label, num_classes=total_words)

    from sklearn.model_selection import train_test_split
    X_train, X_val, Y_train, Y_val = train_test_split(X, ys, test_size=0.2, random_state=42)

    model = Sequential([
        Embedding(total_words, 100),
        Bidirectional(LSTM(128)),  # Reduced neurons for efficiency
        Dense(total_words, activation='softmax')
    ])

    adam = Adam(learning_rate=0.001)  # Lower learning rate
    model.compile(loss='categorical_crossentropy', optimizer=adam, metrics=['accuracy'])

    history = model.fit(X_train, Y_train, epochs=50, validation_data=(X_val, Y_val), verbose=1)

    # Save model architecture & weights
    with open('lstm_model.json', 'w') as json_file:
        json_file.write(model.to_json())
    model.save_weights('lstm_model.weights.h5')

    # Save tokenizer & history
    with open("training_history.pkl", "wb") as file:
        pickle.dump(history.history, file)
    with open("tokenizer.pkl", "wb") as file:
        pickle.dump(tokenizer, file)
    with open('max_sequence_len.int', 'w') as file:
        file.write(str(max_sequence_len))


def testing_plot():
    try:
        with open("training_history.pkl", "rb") as file:
            history = pickle.load(file)

        plt.figure(figsize=(12, 4))
        plt.subplot(1, 2, 1)
        plt.plot(history['loss'], label="Training Loss")
        plt.plot(history['val_loss'], label="Validation Loss")
        plt.title("Loss over Epochs")
        plt.xlabel("Epochs")
        plt.ylabel("Loss")
        plt.legend()

        plt.subplot(1, 2, 2)
        plt.plot(history['accuracy'], label="Training Accuracy")
        plt.plot(history['val_accuracy'], label="Validation Accuracy")
        plt.title("Accuracy over Epochs")
        plt.xlabel("Epochs")
        plt.ylabel("Accuracy")
        plt.legend()

        plt.show()
    except FileNotFoundError:
        print("Training history not found. Run training first.")


def predict_top_5_words(model, tokenizer, seed_text):
    with open('max_sequence_len.int', 'r') as file:
        max_sequence_len = int(file.read())

    token_list = tokenizer.texts_to_sequences([seed_text])[0]
    token_list = pad_sequences([token_list], maxlen=max_sequence_len - 1, padding='pre')

    predicted = model.predict(token_list, verbose=0)
    top_indexes = np.argsort(predicted[0])[-5:][::-1]  # Top 5 predictions

    return [tokenizer.index_word[idx] for idx in top_indexes if idx in tokenizer.index_word]


def main():
    with open('lstm_model.json', 'r') as json_file:
        model = model_from_json(json_file.read())
    model.load_weights('lstm_model.weights.h5')
    model.compile(loss='categorical_crossentropy', optimizer=Adam(learning_rate=0.001), metrics=['accuracy'])

    with open("tokenizer.pkl", "rb") as file:
        tokenizer = pickle.load(file)

    print("Model and tokenizer loaded successfully!")

    while True:
        seed_text = input("\nEnter text (or type 'exit' to quit): ")
        if seed_text.lower() == "exit":
            break
        print("Predicted words:", predict_top_5_words(model, tokenizer, seed_text))


#train_store()
#testing_plot()
main()
