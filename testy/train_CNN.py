import os
import pandas as pd
from collections import Counter
import glob
import lzma
from datetime import datetime
from datetime import timedelta
import numpy as np
import sys


os.environ["TF_FORCE_GPU_ALLOW_GROWTH"] = "true"

# Path to the folder containing CSV files
folder_path = '/home/marek/Documents/Programovani/Holter_bluetooth/Decode_holter/DH_dash/Holter_epochy_vysledky'

folder_path2 = '/home/marek/Documents/Programovani/Holter_bluetooth/Decode_holter/DH_dash/holter_vysledky'
# Initialize a counter for the 'hodnoceni' column
hodnoceni_counter = Counter()
hodnoceni = []
nazvy_souboru = []


def decompress_lzma(data):
    # Dekomprese souboru, i když je nedokončený 
    # https://stackoverflow.com/questions/37400583/python-lzma-compressed-data-ended-before-the-end-of-stream-marker-was-reached
    results = []
    while True:
        decomp = lzma.LZMADecompressor(lzma.FORMAT_AUTO, None, None)
        try:
            res = decomp.decompress(data)
        except lzma.LZMAError:
            if results:
                break  # Leftover data is not a valid LZMA/XZ stream; ignore it.
            else:
                raise  # Error on the first iteration; bail out.
            
            
        results.append(res)
        data = decomp.unused_data
        if not data:
            break
        if not decomp.eof:
            raise lzma.LZMAError("Compressed data ended before the end-of-stream marker was reached")
    return b"".join(results)
def validuj_casovou_znacku(time, data, max_diff=0.004):
        print(len(time), len(data))

        if len(time) != len(data):
            raise ValueError("Time and data lists must have the same length")
        
        sections = []
        corrupted_sections = []
        start = None
        start_index = 0

        cleaned_data = []
        cleaned_time = []

        for i in range(1, len(time)):
            if time[i] - time[i-1] < max_diff and time[i] > time[i-1]: # Validní data
                if start is None:
                    start = time[i - 1]
                    start_index = i - 1
            else: # Chyba, zapiš jako konec úseku
                if start is not None:
                    corrupted_sections.append((start, time[i - 1]))
                    sections.append((start_index,  i - 1))
                    
                    

                    start = None
        
        if start is not None:
            corrupted_sections.append((time[start_index], time[-1]))
            sections.append((start_index,  i - 1))
        
            
        
        for i in range(len(corrupted_sections)-1):
            section = corrupted_sections[i]
            if section[1] > corrupted_sections[i+1][0]:
                print(f"Chyba v úseku {datetime.fromtimestamp(section[0]).strftime('%H:%M:%S')} - {datetime.fromtimestamp(section[1]).strftime('%H:%M:%S')}")
                sections[i] = (None, None)

        for i in range(len(sections)):
            if sections[i] != (None, None):
                cleaned_data += data[sections[i][0]:sections[i][1]]
                cleaned_time += time[sections[i][0]:sections[i][1]]

        print(f"Počet chybějících dat: {len(data) - len(cleaned_data)}")
        return cleaned_time, cleaned_data

search_pattern = os.path.join(folder_path, "*.csv")
# Get all files that match the search pattern
matching_files = np.sort(glob.glob(search_pattern))

# Iterate through all files in the folder
for file_name in matching_files:
    if file_name.endswith('_epochy.csv'):
        nazvy_souboru.append(file_name.split('_epochy')[-2].split('/')[-1])
        # Read the CSV file
        df = pd.read_csv(file_name)
        # Update the counter with values from the 'hodnoceni' column
        #if 'hodnoceni' in df.columns:
        hodnoceni_counter.update(df['hodnoceni'])
        hodnoceni.append(df['hodnoceni'])

# Print the count of each type in the 'hodnoceni' column
for hodnoceni_type, count in hodnoceni_counter.items():
    print(f"{hodnoceni_type}: {count}")

# Load EKG data

# Get EKG filenames
print(nazvy_souboru)
ekg_files = []
ekg_data = []

# Build the search pattern
for i in nazvy_souboru:
    search_pattern = os.path.join(folder_path2, i + "*.ekg")
    # Get all files that match the search pattern
    matching_files = glob.glob(search_pattern)
    ekg_files.append(np.sort(matching_files))

print(ekg_files[0], hodnoceni[0])


for cislo_dne in range(len(ekg_files)):
    den = ekg_files[cislo_dne]
    print()
    print()
    print(f"Název souboru: {den[0]}")
    

    dta = []
    e_cz = []
    for soubor in range(len(den)):
        with open(den[soubor], "rb") as f:
            data = f.read() # přečti zkomprimované data EKG souboru

        print("Soubor byl přečten")

        dta_part = decompress_lzma(data).decode("utf-8").split(",") # dekomprimuj data souboru
        dta_part = dta_part[:-1] # poslední index je prázdný
        
        
        print(f"Počet zápisů v souboru č.{soubor+1}: {len(dta_part)}")
        print("Data dekomprimovány")

        # určení časové značky celého souboru
        ekg_casova_znacka = [float(value.split(";")[0]) for value in dta_part]
        
        start_time = datetime.strptime(den[soubor].split("_")[-2], "%y%m%d") - timedelta(minutes=5)
        end_time = start_time+timedelta(days=1) + timedelta(minutes=5)
        # zjištění správnost dat 
        
        ekg_casova_znacka2 = []
        for i, cas in enumerate(ekg_casova_znacka):
            if start_time <= datetime.fromtimestamp(cas) <= end_time:
                ekg_casova_znacka2.append(cas) #ekg_casova_znacka2.append(datetime.fromtimestamp(cas))
            else: 
                [print("ERROR V ČASOVÉ ZNAČCE") for i in range(5)]
                print(datetime.fromtimestamp(cas))
                dta_part = dta_part[:i]
                break

        e_cz += ekg_casova_znacka2
        dta += dta_part


   

    dta = [int(value.split(";")[1]) for value in dta]
    print(f"Počet použitelných dat: {len(dta)}")

    
    e_cz, dta = validuj_casovou_znacku(e_cz, dta)
    # Vypočítej množství dat v datovém souboru
    mozny_pocet_minut = int(len(dta)/(500*60))



    # Rozděl na 30s epochy
    
    epochy = [dta[i*500*30:i*500*30+500*30] for i in range(0, mozny_pocet_minut*2)]
    
    """
    if len(epochy) != len(hodnoceni[cislo_dne]):
        print("ERROR: Počet epoch a hodnocení se neshoduje")
        e_cz, dta = validuj_casovou_znacku(e_cz, dta)
        mozny_pocet_minut = int(len(dta)/(500*60))
        epochy = [dta[i*500*30:i*500*30+500*30] for i in range(0, mozny_pocet_minut*2)]

    """
    print(f"Počet epoch: {len(epochy)}")

    if len(epochy) != len(hodnoceni[cislo_dne]):
        print(hodnoceni[cislo_dne])
        print("ERROR: Počet epoch a hodnocení se neshoduje")
        sys.exit(1)

    

    ekg_data.append(epochy)
    print(f"Naměřený počet minut datového souboru: {mozny_pocet_minut}")
    
    # Určení, z kolika různých měření se výsledkový soubor skládá
    measurement_periods = []



for i in range(len(ekg_data)):
    print(len(ekg_data[i]))
    print(len(hodnoceni[i]), ekg_files[i][0])
    
    if len(ekg_data[i]) != len(hodnoceni[i]):
        print("ERROR: Počet epoch a hodnocení se neshoduje")
        sys.exit(1)



ekg_all = []
for i in ekg_data:
    for j in i:
        ekg_all.append(j)

hodnoceni_all = []
for i in hodnoceni:
    for j in i:
        hodnoceni_all.append(j)



print(np.array(ekg_all).shape)


from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score

import keras
from keras.layers import Dense, Flatten, Dropout, Conv1D, BatchNormalization, MaxPooling1D
from sklearn.metrics import confusion_matrix, classification_report, ConfusionMatrixDisplay
from keras.regularizers import l2
from keras.optimizers import Adam

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(hodnoceni_all)  # A->0, S->1, N->2


# Scale the EKG data from 0 to 1
scaler = StandardScaler()
X_scaled = scaler.fit_transform(ekg_all)




# Split into train and validation sets
X_train, X_val, y_train, y_val = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)
X_train = X_train.reshape(-1, 15000, 1)
X_val = X_val.reshape(-1, 15000, 1)



# Show distribution after split
train_unique, train_counts = np.unique(y_train, return_counts=True)
val_unique, val_counts = np.unique(y_val, return_counts=True)

print("Train dataset distribution:", dict(zip(label_encoder.classes_, train_counts)))
print("Validation dataset distribution:", dict(zip(label_encoder.classes_, val_counts)))

# Plot distributions
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# Training distribution
axes[0].bar(label_encoder.classes_, train_counts, color=['red', 'green', 'blue'])
axes[0].set_title("Training Data Distribution")
axes[0].set_xlabel("Category")
axes[0].set_ylabel("Count")

# Validation distribution
axes[1].bar(label_encoder.classes_, val_counts, color=['red', 'green', 'blue'])
axes[1].set_title("Validation Data Distribution")
axes[1].set_xlabel("Category")
axes[1].set_ylabel("Count")

#plt.show()



"""
# Define the model
model = keras.Sequential()


# Convolutional layer
model.add(Conv1D(128, 5, activation='relu', kernel_regularizer=l2(0.001), input_shape=(15000,1)))
model.add(BatchNormalization())
model.add(Dropout(0.5))

# Flatten before passing to Dense layers
model.add(Flatten())

# Fully connected layers
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(3, activation='softmax'))  # Three-class classification


# Compile
optimizer = Adam(learning_rate=0.0005)
model.compile(loss='sparse_categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])

# Ensure X_train and X_val are reshaped to (batch_size, 15000, 1)


# Train the model
history = model.fit(X_train, y_train, epochs=15, batch_size=32, verbose=1, validation_data=(X_val, y_val))
"""

"""
model = keras.Sequential()

# First Conv layer
model.add(Conv1D(128, 7, activation='relu', kernel_regularizer=l2(0.001), input_shape=(15000,1)))
model.add(BatchNormalization())
model.add(MaxPooling1D(pool_size=2))
model.add(Dropout(0.5))

# Second Conv layer
model.add(Conv1D(256, 5, activation='relu', kernel_regularizer=l2(0.001)))
model.add(BatchNormalization())
model.add(MaxPooling1D(pool_size=2))
model.add(Dropout(0.5))

# Third Conv layer
model.add(Conv1D(512, 3, activation='relu', kernel_regularizer=l2(0.001)))
model.add(BatchNormalization())
model.add(MaxPooling1D(pool_size=2))
model.add(Dropout(0.5))

# Flatten
model.add(Flatten())

# Fully connected layers
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(3, activation='softmax'))  # 3 classes

# Compile with adjusted learning rate
optimizer = Adam(learning_rate=0.0003)
model.compile(loss='sparse_categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])

"""



model = keras.Sequential()

model.add(keras.Input(shape=(15000,)))
model.add(Dense(64, activation='relu'))
model.add(Dense(64, activation='relu'))
model.add(Dropout(rate=0.25))
model.add(Dense(3, activation='softmax'))
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Train
history = model.fit(X_train, y_train, epochs=20, batch_size=32, validation_data=(X_val, y_val))




# Evaluate the model on the validation set
val_loss, val_accuracy = model.evaluate(X_val, y_val, verbose=0)
print(f"Validation Loss: {val_loss}")
print(f"Validation Accuracy: {val_accuracy}")

# Predict on the validation set
y_pred = model.predict(X_val)
y_pred_classes = np.argmax(y_pred, axis=1)

# Confusion matrix
conf_matrix = confusion_matrix(y_val, y_pred_classes)
disp = ConfusionMatrixDisplay(confusion_matrix=conf_matrix, display_labels=label_encoder.classes_)

# Calculate percentages
conf_matrix_percent = conf_matrix.astype('float') / conf_matrix.sum(axis=1)[:, np.newaxis] * 100

# Plot confusion matrix with percentages
fig, ax = plt.subplots(figsize=(8, 8))
im = ax.imshow(conf_matrix_percent, interpolation='nearest', cmap=plt.cm.Blues)
plt.colorbar(im, ax=ax)
ax.set_title("Confusion Matrix with Percentages")
ax.set_xticks(np.arange(len(label_encoder.classes_)))
ax.set_yticks(np.arange(len(label_encoder.classes_)))
ax.set_xticklabels(label_encoder.classes_)
ax.set_yticklabels(label_encoder.classes_)

# Loop over data dimensions and create text annotations
for i in range(conf_matrix.shape[0]):
    for j in range(conf_matrix.shape[1]):
        text = f"{conf_matrix[i, j]}\n({conf_matrix_percent[i, j]:.1f}%)"
        ax.text(j, i, text, ha="center", va="center", color="black")

plt.xlabel("Predicted Label")
plt.ylabel("True Label")

# Classification report
class_report = classification_report(y_val, y_pred_classes, target_names=label_encoder.classes_)
print("Classification Report:")
print(class_report)

# ROC AUC score (if applicable)
if len(label_encoder.classes_) == 2:  # Binary classification
    roc_auc = roc_auc_score(y_val, y_pred[:, 1])
    print(f"ROC AUC Score: {roc_auc}")

plt.figure()
# Plot training and validation accuracy
plt.plot(history.history.get('accuracy', history.history.get('sparse_categorical_accuracy')), label='Training Accuracy')
plt.plot(history.history.get('val_accuracy', history.history.get('val_sparse_categorical_accuracy')), label='Validation Accuracy')
plt.legend()
plt.show()