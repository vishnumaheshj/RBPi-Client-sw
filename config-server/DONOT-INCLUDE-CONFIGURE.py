import subprocess

if __name__ == "__main__":
    addr = raw_input("Enter Hub ID\n")
    execute = "mkpasswd " + addr + " -m sha-512 -S asdfghjkl"
    result = subprocess.check_output(execute, shell = True)
    result = result[:-1]
    file = open("/etc/dotshadow", "w")
    file.write(result)
    file.close()

