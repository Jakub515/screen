#!/usr/bin/bash
echo "Setup uruchomiony"

echo "Zatrzymuję usługę systemową"

# sudo systemctl stop screen_test
# sudo systemctl disable screen_test

echo "Zatrzymuję wszystkie procesy związane z usługą, nie licząc własnego"

MY_PID=$1

# Znajdź wszystkie procesy związane z /usr/local/bin/screen_test
ps -ef | grep "/usr/local/bin/screen_test" | awk '{print $2}' | while read pid; do
    # Sprawdź, czy PID jest różny od twojego procesu
    if [ "$pid" != "$MY_PID" ]; then
        # Zakończ proces
        sudo kill $pid
    fi
done

# Tablica do przechowywania danych
declare -a data_array

echo "Wprowadź 5 danych do zapisania w pliku $2"

# Tworzymy kopię pliku konfiguracyjnego, aby zachować oryginalne dane
temp_file=$(mktemp)

# Skopiuj zawartość oryginalnego pliku do tymczasowego pliku
cp "$2" "$temp_file"

# Warunki dla danych
# 1. Pierwszy input - 16 liczb
while true; do
    echo "Wprowadź pierwszy ciąg 16 liczb:"
    read data
    if [[ "$data" =~ ^[0-9]{16}$ ]]; then
        data_array+=("$data")
        break
    elif [ -z "$data" ]; then
        data_array+=($(sed -n '1p' "$temp_file"))  # Dodaj istniejącą wartość z pliku
        break
    else
        echo "Błąd! Wprowadź ciąg dokładnie 16 liczb."
    fi
done

# 2. Drugi input - 32-znakowy ciąg
while true; do
    echo "Wprowadź drugi ciąg 32 znaków:"
    read data
    if [[ "${#data}" -eq 32 ]]; then
        data_array+=("$data")
        break
    elif [ -z "$data" ]; then
        data_array+=($(sed -n '2p' "$temp_file"))  # Dodaj istniejącą wartość z pliku
        break
    else
        echo "Błąd! Wprowadź dokładnie 32 znaki."
    fi
done

# 3. Trzeci input - 48-znakowy ciąg
while true; do
    echo "Wprowadź trzeci ciąg 48 znaków:"
    read data
    if [[ "${#data}" -eq 48 ]]; then
        data_array+=("$data")
        break
    elif [ -z "$data" ]; then
        data_array+=($(sed -n '3p' "$temp_file"))  # Dodaj istniejącą wartość z pliku
        break
    else
        echo "Błąd! Wprowadź dokładnie 48 znaków."
    fi
done

# 4. Czwarty input - 48-znakowy ciąg
while true; do
    echo "Wprowadź czwarty ciąg 48 znaków:"
    read data
    if [[ "${#data}" -eq 48 ]]; then
        data_array+=("$data")
        break
    elif [ -z "$data" ]; then
        data_array+=($(sed -n '4p' "$temp_file"))  # Dodaj istniejącą wartość z pliku
        break
    else
        echo "Błąd! Wprowadź dokładnie 48 znaków."
    fi
done

# 5. Piąty input - adres e-mail
while true; do
    echo "Wprowadź piąty input (adres e-mail):"
    read data
    if [[ "$data" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
        data_array+=("$data")
        break
    elif [ -z "$data" ]; then
        data_array+=($(sed -n '5p' "$temp_file"))  # Dodaj istniejącą wartość z pliku
        break
    else
        echo "Błąd! Wprowadź poprawny adres e-mail."
    fi
done

# 6. Szósty input - dowolny ciąg znaków
echo "Wprowadź szósty input (dowolny ciąg znaków):"
read data
if [ -n "$data" ]; then
    data_array+=("$data")
else
    data_array+=($(sed -n '6p' "$temp_file"))  # Dodaj istniejącą wartość z pliku
fi

# Zapisz dane w pliku konfiguracyjnym
# Nadpisz plik z danymi z tablicy, ale jeśli dane były puste, zostaną one pominięte
line_index=1
for entry in "${data_array[@]}"; do
    sed -i "${line_index}s/.*/$entry/" "$2"  # Zaktualizuj odpowiednią linię w pliku
    ((line_index++))
done

echo "Dane zostały zapisane w pliku $2."

