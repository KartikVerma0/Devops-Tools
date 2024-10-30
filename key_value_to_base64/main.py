import base64

def encode_values_to_base64(input_file, output_file):
    with open(input_file, 'r') as file:
        lines = file.readlines()
    
    with open(output_file, 'w') as file:
        for line in lines:
            # Split each line into key and value by colon
            if ':' in line:
                key, value = line.split(':', 1)
                # Strip spaces and newline characters
                key = key.strip()
                value = value.strip().strip('"')  # Remove enclosing quotes if present
                # Encode the value in base64
                encoded_value = base64.b64encode(value.encode()).decode()
                # Write the key with encoded value to the output file
                file.write(f"{key}: {encoded_value}\n")

# Specify the input and output file names
input_file = 'input.txt'  # File containing the key-value pairs
output_file = 'output.txt'  # File to save the output

# Run the function
encode_values_to_base64(input_file, output_file)
