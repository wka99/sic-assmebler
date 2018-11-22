def stringToHex(input):
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

#for optab
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

def optab_search2(opcode,optab_dict):
    for i in optab_dict:
        if(opcode==i['key']):
            return True
    else: return False
    
# for symtab
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
        if(operand.replace(',x','')==i['key']):
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
    startadd=0
    locctr=0
    #read first input line
    line1=prog.readline()
    name=line1[0:9].replace(' ','')
    opcode=line1[9:17].replace(' ','').upper()
    operand=line1[17:].replace('\n','').replace(' ','')
    if(opcode=='START'):
        startadd=stringToHex(operand)
        locctr=startadd
        intf.write("     ")
        intf.write("".join(line1))
    #start가 아니면 locctr은 0
        
    while True:#문서가 끝나기 전까지 한줄씩 읽기
        line=prog.readline()
        if not line: break#문서가 끝나면 while문을 나감
        name=line[0:9].replace(' ','')
        opcode=line[9:17].replace(' ','').replace('\n','').upper()  
        operand=line[17:].replace('\n','').replace(' ','')
        
        if(opcode!='END'):#opcode가 end가 아닐때
            if(line[0]!='.'):#not a comment line
                if(name!=""):#if there is a symbol in the label field
                    data=name+" "+locctr+"\n"
                    print(data.replace("0x",""))
                    #insert data to symtab
                    symtab.write(data.replace("0x",""))
                #write line to intermediate file
                intf.write(locctr.replace("0x","")+" ")
                intf.write("".join(line))
                #search optab for opcode
                if(optab_search2(opcode,opdict)):#opcode가 optab에 존재하는 경우
                    locctr=(hex(int(locctr,16)+(3)))
                #어셈블리 지시자
                elif(opcode=='WORD'):
                    locctr=(hex(int(locctr,16)+(3)))
                elif(opcode =='RESW'):
                    num=int(operand,16)
                    locctr=(hex(int(locctr,16)+num*3))
                elif(opcode =='RESB'):
                    num=int(operand)
                    locctr=(hex(int(locctr,16)+num))
                elif(opcode =='BYTE'):
                    if(operand[0]=="x"):
                        locctr = hex(int(locctr,16)+(len(operand)-3)/2)
                    elif(operand[0]=="c"):
                        locctr = hex(int(locctr,16)+(len(operand)-3))
                        
        else:#write last line to intermediate file
            intf.write(locctr.replace("0x","")+" ")
            intf.write("".join(line))
    #save program length     
    programlen=hex(int(locctr,16)-int(startadd,16))
    return programlen,startadd


def pass2(pass1):
    
    length,startadd=pass1
    length=length.replace("0x","")#프로그램 길이
    startadd=startadd.replace("0x","")#프로그램 시작 주소
    
    addr_list=[]#주소 리스트
    temp=[]#텍스트 레코드 목적코드 임시저장
    
    header_record="" #헤더 레코드
    text_record="" #텍스트 레코드
    end_record="" #엔드 레코드
    operand_addr=0 #operand address
    opcode_value=0 #opcode 연산코드

    # 중간 파일
    intf=open("intermediatefile.txt","r")
    # 목적 프로그램 파일
    objprog=open("objectProgram.txt","w")
    # SYMTAB 파일
    symtab=open("symbol_table.txt","r")
    # optab 파일
    optab=open("optab.txt","r")
    # list 파일
    listf=open("listfile.txt","w")
    # obtab dict
    optabc=optab_to_dict(optab)
    # symtab dict
    symtabc=symtab_to_dict(symtab)

    while True:#문서가 끝나기 전까지 한줄씩 읽기
        line=intf.readline()
        if not line: break#문서가 끝나면 while문을 나감
        addr=line[:5].replace(' ','')
        name=line[5:14].replace(' ','')
        opcode=line[14:22].replace(' ','').replace('\n','').upper()
        operand=line[22:].replace('\n','').replace(' ','')
        #optab,symtab 존재여부 플래그 생성
        #value 1.optab의 경우, opcode에 해당하는 연산코드
        #2.symtab의 경우 operand에 해당하는 주소
        oflag,opcodevalue=optab_search(opcode,optabc)
        sflag,symbolvalue=symtab_search(operand,symtabc)
        if(addr!=""):
            addr_list.append(addr)
        if(opcode=='START'):#헤더 레코드
            header_record="H"+name+' '*(6-len(name))+'0'*(6-len(operand))+operand+'0'*(6-len(length))+length
            listf.write(operand+"   "+line)
            objprog.write(header_record.upper())
            header_record=""
        elif(opcode=='END'):#엔드 레코드
            listf.write(line[0:5]+"       "+line[5:])
            end_record="\n"+"E"+'0'*(6-len(startadd))+startadd
        else:#텍스트 레코드
            if(line[0]!='.'):#not a comment line
                if(oflag):#search optab for opcode
                    if(sflag):#search symtab for operand
                        operand_addr=symbolvalue
                        opcode_value=opcodevalue
                        if(opcode=="STCH" or opcode=="LDCH"):
                            if int(operand_addr[0],16)<=8:
                               operand_addr=hex(int(operand_addr[0],16)+8).replace("0x","")+operand_addr[1:]
                               tobj=opcode_value+operand_addr
                        else:
                            tobj=opcode_value+operand_addr
                    elif opcode=="RSUB":
                        opcode_value=opcodevalue
                        tobj=opcode_value+"0000"
                    listf.write(line[0:5]+tobj+" "+line[5:])
                    temp.append(tobj)
                elif (opcode=="WORD"):
                    l=hex(int(operand)).replace("0x","")
                    tobj='0'*(6-len(l))+l
                    listf.write(line[0:5]+tobj+" "+line[5:])
                    temp.append(tobj)
                elif (opcode=="BYTE"):
                    if operand.find("c")!=-1:
                        t=operand.replace("c","").replace("'","")
                        th=""
                        for i in t:
                            th+=hex(ord(i)).replace("0x","")
                            
                        #6개씩 출력    
                        i=0
                        listf.write(line[0:5])
                        while i<len(th):
                            length=0
                            if i>=6:
                                listf.write("     ")
                            while i<len(th) and length+1<=6:
                                listf.write(th[i])
                                length+=1
                                i+=1
                            if(i<=6):
                                listf.write(" "+line[5:])
                            else:
                                listf.write("\n") 
                        
                        temp.append(th)
                        
                    elif operand.find("x")!=-1:
                       listf.write(line[0:5]+operand.replace('x','').replace("'","")+" "+line[5:])
                       temp.append(operand.replace('x','').replace("'",""))
                else:#RESW,RESB의 경우 목적코드 없음
                    listf.write(line[0:5]+"       "+line[5:])
                    temp.append("")
    i=0
    while i<len(temp):#1e만큼씩 출력/ 초과되는 경우, 다음 텍스트 레코드 초기화
        length=0
        objprog.write("\nT"+'0'*(6-len(addr_list[i]))+addr_list[i].upper())
        while i<len(temp) and length+len(temp[i])//2<=30:
            text_record+=temp[i]
            length+=len(temp[i])//2
            i+=1
        a=hex(length).replace("0x","")
        text_record=a+text_record
        objprog.write(text_record.upper())
        text_record=""
            
    objprog.write(end_record.upper())
    print(temp)


if __name__=="__main__":
    pass2(pass1())

            
        
    
