symbol = ["add", "sub", "neg", "eq", "lt", "gt", "and", "or", "not"]
def initialize(file):
    with open(file, 'r') as f:
        line = f.readlines()
    return line


def clear_format(line):
    line = [x.split('/')[0] for x in line]
    line = [x.replace('\r', '') for x in line]
    line = [x.replace('\t', '') for x in line]
    line = [x.replace('\n', '') for x in line]
    while '' in line:
        line.remove('')
    return line


def check_command(str):
    if str in symbol:
        return "al"
    elif str.split(" ")[0] == "push":
        return "pu"
    elif str.split(" ")[0] == "pop":
        return "po"


translator = {
    "add": ["@SP", "AM=M-1", "D=M", "A=A-1", "M=D+M"],
    "sub": ["@SP", "AM=M-1", "D=M", "A=A-1", "M=M-D"],
    "or": ["@SP", "AM=M-1", "D=M", "A=A-1", "M=D|M"],
    "and": ["@SP", "AM=M-1", "D=M", "A=A-1", "M=D&M"],
    "neg": ["@SP", "A=M-1", "M=-M"],
    "not": ["@SP", "A=M-1", "M=!M"],
    "eq": ["@SP", "AM=M-1", "D=M", "A=A-1", "D=M-D", "M=-1"],
    "eqend": ["D;JEQ", "@SP", "A=M-1", "M=0"],
    "gt": ["@SP", "AM=M-1", "D=M", "A=A-1", "D=M-D", "M=-1"],
    "gtend": ["D;JGT", "@SP", "A=M-1", "M=0"],
    "lt": ["@SP", "AM=M-1", "D=M", "A=A-1", "D=M-D", "M=-1"],
    "ltend": ["D;JLT", "@SP", "A=M-1", "M=0"]
}


def push_pop_check(str):
    if check_command(str) == "pu" or check_command(str) == "po":
        return str.split()[1], str.split()[2]

push_end = ["@SP", "A=M", "M=D", "@SP", "M=M+1"]
def push(segment, index):
    code = []
    code.append("@" + index)
    code.append("D=A")
    if segment == "constant":
        code.extend(push_end)
    elif segment == "local":
        code.extend(["@LCL", "A=D+M", "D=M"])
        code.extend(push_end)
    elif segment == "this":
        code.extend(["@THIS", "A=D+M", "D=M"])
        code.extend(push_end)
    elif segment == "that":
        code.extend(["@THAT", "A=D+M", "D=M"])
        code.extend(push_end)
    elif segment == "argument":
        code.extend(["@ARG", "A=D+M", "D=M"])
        code.extend(push_end)
    elif segment == "pointer":
        code.extend(["@3", "A=D+A", "D=M"])
        code.extend(push_end)
    elif segment == "temp":
        code.extend(["@5", "A=D+A", "D=M"])
        code.extend(push_end)
    elif segment == "static":
        code.extend(["@" + filename + "." + index, "D=M"])
        code.extend(push_end)
    return code

pop_part = ["@SP", "AM=M-1", "D=M", "M=0"]
def pop(segment, index):
    code = []
    code.append("@" + index)
    code.append("D=A")
    if (segment == "local"):
        code.extend(["@LCL", "A=D+M", "D=A", "@R13", "M=D"])
        code.extend(pop_part)
        code.extend(["@R13", "A=M", "M=D", "@R13", "M=0"])
    elif (segment == "argument"):
        code.extend(["@ARG", "A=D+M", "D=A", "@R13", "M=D"])
        code.extend(pop_part)
        code.extend(["@R13", "A=M", "M=D", "@R13", "M=0"])
    elif (segment == "this"):
        code.extend(["@THIS", "A=D+M", "D=A", "@R13", "M=D"])
        code.extend(pop_part)
        code.extend(["@R13", "A=M", "M=D", "@R13", "M=0"])
    elif (segment == "that"):
        code.extend(["@THAT", "A=D+M", "D=A", "@R13", "M=D"])
        code.extend(pop_part)
        code.extend(["@R13", "A=M", "M=D", "@R13", "M=0"])
    elif (segment == "temp"):
        code.extend(["@5", "A=D+A", "D=A", "@R13", "M=D"])
        code.extend(pop_part)
        code.extend(["@R13", "A=M", "M=D", "@R13", "M=0"])
    elif (segment == "pointer"):
        code.extend(["@3", "A=D+A", "D=A", "@R13", "M=D"])
        code.extend(pop_part)
        code.extend(["@R13", "A=M", "M=D", "@R13", "M=0"])
    elif (segment == "static"):
        code.extend(["@" + filename + "." + index, "D=A", "@R13", "M=D"])
        code.extend(pop_part)
        code.extend(["@R13", "A=M", "M=D", "@R13", "M=0"])
    return code

finalcode = []
def codewriter(string, i, filename):
    if check_command(string) == "al":
        finalcode.append("//" + string)
        finalcode.extend(translator[string])
        if string == "gt" or string == "lt" or string == "eq":
            finalcode.append("@IFEQ" + str(i) + filename)
            finalcode.extend(translator[string + "end"])
            finalcode.append("(IFEQ" + str(i) + filename + ")")
    elif check_command(string) == "pu":
        finalcode.append("//" + string)
        segment, index = push_pop_check(string)
        finalcode.extend(push(segment, index))
    elif check_command(string) == "po":
        finalcode.append("//" + string)
        segment, index = push_pop_check(string)
        finalcode.extend(pop(segment, index))


def file_creator(code, filename):
    with open(filename, 'w') as f:
        for x in code:
            f.write(x)
            f.write("\n")


file = input("Enter File Name: ")
filename = file.split(".")[0]
line = initialize(file)
format_code = clear_format(line)
for i in range(len(format_code)):
    codewriter(format_code[i], i, filename)
finalcode.extend(["(END)", "@END", "0;JMP"])
file_creator(finalcode, filename.split(".")[0] + ".asm")
