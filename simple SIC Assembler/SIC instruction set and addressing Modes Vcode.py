#simple SIC Assembler
#----------import lib-----------------#
import pandas as pd
import math 

#------------main program------------#
def main(): 
    column_names=["symbol" ,"instructions","reference"]
    program1=pd.read_csv("input1.csv",sep=" ",names=column_names)
    program2=pd.read_csv("input2.csv",names=column_names)
    print('\n---SIC Simplified Instructional Computer Assembler---\n')

    print("---------------------test program 1----------------------")
    print("---------------------------------------------------------")

    Pass1(program1)
    Pass2(program1)

    print("\n#########################################################")
    print("---------------------test program 2----------------------")
    print("---------------------------------------------------------")

    Pass1(program2)
    Pass2(program2)
    print("\n")

#---------SIC Assembler Pass1--------#
"""
Pass 1 (define symbol)
• Assign addresses to all statements (generate LOC).
• Save the values (address) assigned to all labels for Pass 2 (symbol_Taple).
• Perform some processing of assembler directives.
"""

def Pass1(df):
    print('-------------A simple SIC Assembler Pass1-------------\n')
    # print source program
    print('-----source program written in assembly language------\n')
    print(df)
    print('\n----------------------------------------------------\n')
    # Assign addresses to all statements  and print source program with loc
    print('---------Assimply Program with loc---------\n')
    df=generate_LOC(df)
    print(df)
    print('\n----------------------------------------------------\n')
    # Save the values (address) assigned to all labels and print symbol_Taple
    print('---symbol taple---\n')
    symbol_taple=symbol_Taple(df)
    print(symbol_taple)
    print('\n----------------------------------------------------\n')

def generate_LOC(df):
    loc = pd.Series([] ,dtype=pd.StringDtype())
    for i in range(len(df)):
        if df["instructions"][i] == "START":
            loc[i]=padhexa(df["reference"][i],4)
            loc[i+1]= loc[i]
              
        elif  df["instructions"][i] == "WORD":
            loc[i+1]= padhexa(add_hex(loc[i],"0x3"),4)
            

        elif (df["instructions"][i] == "RESERW" or df["instructions"][i] == "RESW"):
            loc[i+1]= padhexa(add_int_hex(loc[i], 3*int(df["reference"][i])),4)

        elif  df["instructions"][i] == "BYTE":
            if (df["reference"][i][0]== "x" or df["reference"][i][0]== "X" ):
                loc[i+1]= padhexa(add_int_hex(loc[i],math.ceil((len(df["reference"][i])-3.0)/2.0)),4)

            if (df["reference"][i][0]== "C" or df["reference"][i][0]== "c" ):
                loc[i+1]= padhexa(add_int_hex(loc[i],(len(df["reference"][i])-3)),4)
      
        elif  df["instructions"][i] == "RESERB":
            loc[i+1]= padhexa(add_int_hex(loc[i],df["reference"][i]),4)

        elif df["instructions"][i] == "END":
            break
        else:
            loc[i+1] = padhexa(add_hex(loc[i],"0x3"),4)

    df.insert(0,"loc",loc)
    
    return df

def symbol_Taple(df):
    symbol_taple = df[["symbol","loc"]]
    symbol_taple = symbol_taple[symbol_taple.symbol != '--']
    symbol_taple = symbol_taple.reset_index(drop=True)
    return symbol_taple

#---------SIC Assembler Pass2--------#
"""
Pass 2
• Assemble instructions.
• Generate data values defined by BYTE, WORD.
• Perform processing of assembler directives not done during Pass 1.
• Write the OP and the assembly listing

"""

def Pass2(df):
   # df=generate_LOC(df)
    print('-------------A simple SIC Assembler Pass2-------------\n')
    print('-----------Assimply Program with Object code----------\n')
    df=generate_OP(df)
    print(df)
    print('\n----------------------------------------------------\n')
    HTE(df)

def generate_OP(df):
    symbol_taple=symbol_Taple(df)
    object_code = pd.Series([],dtype=pd.StringDtype())
    for i in range(len(df)):
        if df["instructions"][i] in ["START","END","End"]:
            object_code[i]="--"
        
        elif df["instructions"][i] in ["RESW","RESERW","RESERB"]:
            object_code[i]="no obj. code"
       
        elif df["instructions"][i] == "WORD": 
            object_code [i] = padinthexa(df["reference"][i],6)

        elif df["instructions"][i] == "BYTE": 
           if (df["reference"][i][0]== "x" or df["reference"][i][0]== "X" ):
               object_code [i] = padhexa(df["reference"][i][2:-1],6)
           elif (df["reference"][i][0]== "C" or df["reference"][i][0]== "c" ):
                object_code [i] = '0x' + str(df["reference"][i][2:-1]).encode('utf-8').hex()
        
        elif isIndexed(df["reference"][i]) :
            op_code = get_opCode(df["instructions"][i])
            address = get_address(df["reference"][i] , symbol_taple)
            object_code [i] = padhexa(op_code,2)+ padhexa(add_hex(address,"0x8000"),4)[2:]


        elif not isIndexed(df["reference"][i]) :
            op_code = get_opCode(df["instructions"][i])
            address = get_address(df["reference"][i] , symbol_taple)    
            if address ==  None:
                 address= "0x0"
            object_code [i] = padhexa(op_code,2)+ padhexa(address,4)[2:]
       
        
    df.insert(4,"object_code",object_code)
    return df

def isIndexed(instructions):
    
    last_char = instructions.split(",")[-1]
    if last_char in ["x" , "X" ," x" , " X" ]:
        return True
    else: 
        return False

def get_opCode(instructions):
    SIC_instruction=pd.read_csv("SIC instruction set and addressing Modes1.csv")
    for i in range(len(SIC_instruction)):
        if instructions == SIC_instruction['Mnemonic'][i]:
            op_code = SIC_instruction['Opcode'][i]
            return op_code

def get_address(reference , symbol_taple):
    xx= reference.split(",")[0]
    
    for i in range(len(symbol_taple)):
        if xx == symbol_taple['symbol'][i]:
           address = symbol_taple['loc'][i]
           return address

    
#--------------HTTE recor---------------#
#https://www.youtube.com/watch?v=FFfog1tSKCw

def HTE(df):
    print("---------------HTE RECORD------------------")
    Head(df)
    Text(df)
    END(df)

def Head(df):
    #H/NAME:6BITS/START:6BITS/LENGTH:6BITS
    NAME=df.symbol[0].ljust(6, 'X')
    START=padhexa(df["loc"].iloc[1],6)
    End=padhexa(df["loc"].iloc[-1],6)
    LENGTH=padhexa(sub_hex(End,START),6)
    head="H/"+NAME+"."+START+"."+LENGTH
    print(head)

def Text(df):
#T/START:6BITS/LENGTH;2BITS/OBJECT CODE
    x=0
    flag=0
    OBJECT_CODE=[]
    for i in range(len(df)):     
        if df["object_code"][i] not in ["no obj. code","--"]:
            flag=0
            OBJECT_CODE.append(df["object_code"][i] )      
        elif  i!=0:
            if(flag==0 ):
                START=padhexa(df["loc"].iloc[x],6)
                End=padhexa(df["loc"].iloc[i],6)
                LENGTH=padhexa(sub_hex(End,START),2)
                Text="t/"+START+"."+LENGTH+"."+ '.'.join(OBJECT_CODE)
                print(Text)
                flag=1
                OBJECT_CODE.clear()
            x=i+1

def END(df):
    #E/START:6 BITS6
    End="E/"+padhexa(df["loc"].iloc[1],6)
    print(End)

#------------auxiliary function---------#

def add_hex(a, b):
   return hex(int(a, 16) + int(b, 16))

def add_int_hex(a, b):
   return hex(int(a, 16) + int(b))

def sub_hex(a, b):
   return hex(int(a, 16) - int(b, 16))

def padhexa(data,padded,start=0):
    data=int(data[start:],16)
    data=hex(data)
    data=str(data)[2:]
    return "0x"+data[:].zfill(padded)

def padinthexa(data,padded,start=0):
    data=int(data[start:])
    data=hex(data)
    data=str(data)[2:]
    return "0x"+data[:].zfill(padded)

main()

