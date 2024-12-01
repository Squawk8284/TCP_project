import random

def generate_random_numbers_in_file(file_path, rows=10):
    # Generate rows of random numbers, with each row containing 3 numbers between 0 and 5
    data = [[random.randint(0, 15) for _ in range(3)] for _ in range(rows)]
    
    # Write the comment and data to the text file
    with open(file_path, 'w') as file:
        # Add a comment at the start of the file
        #file.write("# This file contains rows of random numbers between 0 and 5, separated by commas\n")
        
        for i, row in enumerate(data):
            file.write(' '.join(map(str, row)))
            if i < rows - 1:  # Only add newline if it's not the last row
                file.write('\n')

if __name__ == "__main__":
    # Set file path and number of rows to generate
    for i in range(1,5):
        file_path = f'queue{i}.txt'
        generate_random_numbers_in_file(file_path)  # Correct function call
        print(f"File '{file_path}' has been created with random numbers.")
