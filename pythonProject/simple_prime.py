primes = []
for num in range(2, 251):
    if all(num % i != 0 for i in range(2, int(num**0.5)+1)):
        primes.append(num)

with open("results.txt", "w") as f:
    f.write("Prime numbers 1-250:\n")
    f.write(", ".join(map(str, primes)))
    f.write(f"\n\nTotal: {len(primes)} primes")

print(f"Found {len(primes)} primes in results.txt")

#still trying