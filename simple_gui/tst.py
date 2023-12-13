def ternary_to_binary(ternary):
    decimal = int(str(ternary), 3)
    binary = bin(decimal)
    return binary[2:], decimal

print(ternary_to_binary(2022))