import csv

def read_txt_file(filename):
    data = []  # List to store the data from the text file
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()  # Remove leading/trailing whitespaces
            if line:  # Check if the line is not empty
                fields = line.split()  # Split the line based on spaces
                data.append(tuple(fields))  # Append the fields as a tuple to the list
    return data

# convert data2.txt to a csv file
data = read_txt_file('data2.txt')
with open('data2.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows(data)



