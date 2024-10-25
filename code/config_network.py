def zero_matrix(n):
    result = []

    # Column headers
    result.append("  To \u2192    " + " ".join(f"C{i+1}" for i in range(n)) + "  J")
    
    result.append((f"From \u2193 Qn " + " 0 " * (n)).rstrip())

    for i in range(n):
        # Row header and row content
        result.append((f"       C{i+1} " + " 0 " * (n+1)).rstrip())
    
    return "\n".join(result)

# Example usage
n = 5
# print(zero_matrix(n))

# with open('./config/network.txt', 'w') as file:
#     file.write(zero_matrix(n))

def remove_headers(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    result = []
    result.append(list(((lines[1].split("Qn")[-1][1:]).split())))

    for line in lines[2:]:
        formatted_line = "".join((line.split("C")[-1][1:]).split())
        result.append(list(formatted_line))
    
    # return "\n".join(result)
    return result

    

# Example usage
print(remove_headers('./config/network.txt'))