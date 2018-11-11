# 패스1의 입력값 -> assembly program
prog=open("assembly_program.txt","r")
# 중간 파일 생성
intf=open("intermediatefile.txt","w")
# SYMTAB 생성
symtab =open("symbol_table.txt","w")
# optab 파일
optab=open("optab.txt","r")

def intToHex(input):
    count=0
    hn=0
    for i in input:
        if(not(i.isdigit())):
            count+=1
            toasci=ord(i.upper())-65+10
            hn+=(toasci)*16**(len(input)-count)
            if (not(toasci<=15 and toasci>=10)):
                print("ERROR : 16진수의 형태가 아닙니다")
                break;
        else:
            count+=1
            hn+=(ord(i)-48)*16**(len(input)-count)
    return hex(hn)

def make_optab_dict(opt):
    optab=[]
    a=[]
    while True:
        line=opt.readline()
        if not line: break
        a=line.split(" ")
        key=a[0]
        value=a[1].replace("\n","")
        optab.append({'key':key,'value':value})
    return optab

def pass1(f1,f2,f3,f4):
    programlen=0
    d=[]
    optab=make_optab_dict(f4)
    startadd=0
    locctr=0
    #read first input line
    line1=f1.readline()
    f2.write("-      ")
    f2.write("".join(line1))
    name=line1[0:9].replace(' ','')
    opcode=line1[9:17].replace(' ','').upper()
    operand=line1[17:].replace('\n','').replace(' ','')
    if(opcode=='START'):
        startadd=intToHex(operand)
        locctr=startadd
    #start가 아니면 locctr은 0
        
    while True:#문서가 끝나기 전까지 한줄씩 읽기
        line=f1.readline()
        if not line: break#문서가 끝나면 while문을 나감
        name=line[0:9].replace(' ','')
        opcode=line[9:17].replace(' ','').upper().replace('\n','')
        operand=line[17:].replace('\n','').replace(' ','')
        d.append({'name':name,'opcode':opcode,'operand':operand})
        if(opcode!='END'):#opcode가 end가 아닐때
            if(line[0]!='.'):#not a comment line
                if(name!=""):#if there is a symbol in the label field
                    data=name+" "+locctr+"\n"
                    print(data)
                    #insert data to symtab
                    f3.write(data)
                #write line to intermediate file
                f2.write(locctr+" ")
                f2.write("".join(line))
                #search optab for opcode
                for i in optab:#opcode가 optab에 존재하는 경우
                    if(opcode == i['key']):
                        locctr=(hex(int(locctr,16)+3))
                #어셈블리 지시자
                if(opcode=='WORD'):
                    locctr=(hex(int(locctr,16)+3))
                elif(opcode =='RESW'):
                    num=int(operand,16)
                    locctr=(hex(int(locctr,16)+num*3))
                elif(opcode =='RESB'):
                    num=int(operand)
                    locctr=(hex(int(locctr,16)+num))
                elif(opcode == 'BYTE'):
                    if(operand[0]=="x"):
                        locctr = hex(int(locctr,16)+(len(operand)-3)/2)
                    elif(operand[0]=="c"):
                        locctr = hex(int(locctr,16)+(len(operand)-3))
                        
        else:#write last line to intermediate file
            f2.write(locctr+" ")
            f2.write("".join(line))
            
    #save program length     
    programlen=hex(int(locctr,16)-int(startadd,16))

    f1.close()
    f2.close()
    f3.close()
    f4.close()
'''
def pass2():
    d=[]
    intf=open("intermediatefile.txt.","r")
    while True:#문서가 끝나기 전까지 한줄씩 읽기
        line=intf.readline()
        if not line: break#문서가 끝나면 while문을 나감
        addr=line[:7].replace(' ','')
        name=line[7:16].replace(' ','')
        opcode=line[16:24].replace(' ','').upper().replace('\n','')
        operand=line[24:].replace('\n','').replace(' ','')
        d.append({'addr':addr,'name':name,'opcode':opcode,'operand':operand})
        if(opcode=='START'):
'''
            
pass1(prog,intf,symtab,optab)
#pass2()

            
        
    
