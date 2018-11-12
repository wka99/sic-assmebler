
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

def optab_to_dict(opt):
    optab_dict=[]
    a=[]
    while True:
        line=opt.readline()
        if not line: break
        a=line.split(" ")
        key=a[0]
        value=a[1].replace("\n","")
        optab_dict.append({'key':key,'value':value})
    return optab_dict

def optab_search(opcode,optab_dict):
    for i in optab_dict:
        if(opcode==i['key']):
            return True,i['value']
    else: return False,'error'

def symtab_to_dict(symt):
    symtab_dict=[]
    a=[]
    while True:
        line=symt.readline()
        if not line: break
        a=line.split(" ")
        key=a[0]
        value=a[1].replace("\n","")
        symtab_dict.append({'key':key,'value':value})
    return symtab_dict

def symtab_search(operand,symtab_dict):
     for i in symtab_dict:
        if(operand==i['key']):
            return True,i['value']
     else: return False,'error'
    
def pass1():
    # 패스1의 입력값 -> assembly program
    prog=open("assembly_program.txt","r")
    # 중간 파일 생성
    intf=open("intermediatefile.txt","w")
    # SYMTAB 생성
    symtab =open("symbol_table.txt","w")
    # optab 파일
    optab=open("optab.txt","r")
    #optab을 dict로
    opdict=optab_to_dict(optab)
    programlen=0
    d=[]
    startadd=0
    locctr=0
    #read first input line
    line1=prog.readline()
    intf.write("-      ")
    intf.write("".join(line1))
    name=line1[0:9].replace(' ','')
    opcode=line1[9:17].replace(' ','').upper()
    operand=line1[17:].replace('\n','').replace(' ','')
    if(opcode=='START'):
        startadd=intToHex(operand)
        locctr=startadd
    #start가 아니면 locctr은 0
        
    while True:#문서가 끝나기 전까지 한줄씩 읽기
        line=prog.readline()
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
                    symtab.write(data)
                #write line to intermediate file
                intf.write(locctr+" ")
                intf.write("".join(line))
                #search optab for opcode
                if(optab_search(opcode,opdict)):#opcode가 optab에 존재하는 경우
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
            intf.write(locctr+" ")
            intf.write("".join(line))
            
    #save program length     
    programlen=hex(int(locctr,16)-int(startadd,16))
    return programlen,startadd
    f1.close()
    f2.close()
    f3.close()
    f4.close()

def pass2(pass1):
    length,startadd=pass1
    length=length.replace("0x","")#프로그램 길이
    startadd=startadd.replace("0x","")#프로그램 시작 주소
    addr_list=[]
    d=[]
    
    header_record="" #헤더 레코드
    text_record="" #텍스트 레코드
    end_record="" #엔드 레코드
    operand_addr=0 #operand address
    opcode_value=0
    # 중간 파일
    intf=open("intermediatefile.txt","r")
    # 목적 프로그램 파일
    objprog=open("objectProgram.txt","w")
    # SYMTAB 파일
    symtab=open("symbol_table.txt","r")
    # optab 파일
    optab=open("optab.txt","r")
    # obtab dict
    optabc=optab_to_dict(optab)
    # symtab dict
    symtabc=symtab_to_dict(symtab)
    #print(symtabc)
    while True:#문서가 끝나기 전까지 한줄씩 읽기
        line=intf.readline()
        if not line: break#문서가 끝나면 while문을 나감
        addr=line[:7].replace(' ','').replace('0x','')
        name=line[7:16].replace(' ','')
        opcode=line[16:24].replace(' ','').replace('\n','').upper()
        operand=line[24:].replace('\n','').replace(' ','')
        oflag,opcodevalue=optab_search(opcode,optabc)
        sflag,symbolvalue=symtab_search(operand,symtabc)
        d.append({'addr':addr,'name':name,'opcode':opcode,'operand':operand})
        if(opcode=='START'):#헤더 레코드
            addr_list.append(addr)
            header_record="H"+name+' '*(6-len(name))+'0'*(6-len(operand))+operand+'0'*(6-len(length))+length+"\n"
            objprog.write(header_record)
            header_record=""
        elif(opcode=='END'):#엔드 레코드
            end_record="E"+'0'*(6-len(startadd))+startadd
            objprog.write(end_record)
            end_record=""
        else:#텍스트 레코드
            if(line[0]!='.'):#not a comment line
                if(oflag):#search optab for opcode
                    if(sflag):#search symtab for operand
                        operand_addr=symbolvalue.replace("0x","")
                        opcode_value=opcodevalue.replace("0x","")
                        
                    
                
            
        
            
                                  
pass2(pass1())

            
        
    
