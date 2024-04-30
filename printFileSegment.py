def print_file_segment(file_path, position, num_bytes=200):
    """
    Print bytes around a specific position in a file to help diagnose encoding errors.
    
    :param file_path: Path to the file
    :param position: The byte position where the error occurred
    :param num_bytes: Number of bytes to read around the position (default 40)
    """
    with open(file_path, 'rb') as file:
        # Move to a position a few bytes before the problem if possible
        start = max(0, position - num_bytes // 2)
        file.seek(start)
        
        # Read the specified number of bytes around the problematic position
        data = file.read(num_bytes)
        
        # Print the data as a string, escaping non-ASCII bytes
        print(data.decode('utf-8', errors='replace'))

# Use the function to print the context around the problematic position
csv_file_path = 'voicenotes/voice_notes.csv'  # Update this with your actual file path
problematic_position = 155011  # The position mentioned in your error
print_file_segment(csv_file_path, problematic_position)