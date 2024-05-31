# in the cs directory: python ./process/detect.py 
import os
import time
# calculate thereading time of a label(s)
start_time = time.time()

# pre data read .  store the seruak bynbers of reference labels and perception labels
src = "./moisture_estimation/tag.txt"
# record the str 
A  = list(0 for i in range(30))
B  = list(0 for i in range(30))
# record the tag num begin .   the function fo this variavle is to facilitate us to uniformly list the detected labels
TAG = list(-1 for i in range(30))
f = open(src,'r')
line  = f.readline()
# temp 
i = 0
while len(line) > 3:
    A[i]= line.replace("\n","").split(',')[1]
    B[i] = line.replace("\n","").split(',')[2]
    i = i+1
    line = f.readline()
    # print(line)
f.close()
print("success")
# record the str enabled,x is 1 or 0
A_1 = list(0 for i in range(len(A)))
B_1 = list(0 for i in range(len(B)))

# detected file
file_path = "/home/pi/Desktop/mercuryapi-1.37.2.24/cs/ThingMagicReader_test.csv"
# now line's id
temp = -1 # it is used to record which serial number was discovered and change subsequent values based on the valuse of that variable
# record the begin and now frequency . they serve as criteria for terminating records
begin = 0
now = -1
# for more read. to prevent incomplete reads ,we record the location of the last complete read and restart 
previous_size = os.path.getsize(file_path) # 0 
# make the input jump out . record the current number of detections 
i = -1
# the tag you want.  this variable represents the tag number you have selected
tag = -1
# give us the input's flag.  represent whether the tag to be detected has been selected
flag = 0
# control the search time. 
MAX = 10
# control the loop end .  write from te next frequency of the starting frequency
loop2 = 0 # whether to writethe starting frequency as a representative
loop = 0  # represents whether to startwriting from te next frequency

# create a folder to store all data :/process/data
# data 
# -----Data_id.txt
# -----Data_id2.txt
# -----predict.txt
if os.path.exists("./moisture_estimation/data") == False :
    os.mkdir("./moisture_estimation/data")
while 1:
    current_size = os.path.getsize(file_path)
    if previous_size < current_size :
        # from IF or EOF begin read
        f = open(file_path,'r')
        f.seek(previous_size)
        # read 
        line = f.readline()
        # about the data's write
        
        # data store we want
        f2 = open("./moisture_estimation/data/Data" + ".txt",'a') 
        while len(line) > 3 and len(line.split(',')) == 9:
            # becaues the file read may error or split's index isn't 9,we record the important position
            previous_size = f.tell()
            # get the id
            id = line.split(',')[0]
            # begin detect
            if i < MAX:
                i = i + 1
                print(i)

            if id in A :
                temp = A.index(id)
                A_1[temp] = 1
           
            elif id in B :
                temp = B.index(id)
                B_1[temp] = 1
               
            
            # only tell us the detected tag'id once
            if temp != -1 and A_1[temp] and B_1[temp]  and TAG[temp] == -1:
                # record the now tag begin id
                TAG[temp] = int(line.split(',')[1])
                print("detected tag:",temp+1,"its begin is",TAG[temp])
            # choice
            if flag == 0  and i >= MAX:
                print("we detected those tags: ",end = " ")
                for k in range(0,len(A)):
                    if(TAG[k] != -1):
                        print(k+1,end="  ")
                print("\nplease input the tag that you want:",end = " ")
                # input the tag you want
                tag = int(input())
                flag = 1
                # we want tag' begin id
                begin =TAG[tag-1]
                
            
            # judge the now
            elif (id == A[tag-1] or id == B[tag-1]) and i >= MAX :
                now = int(line.split(',')[1])
                frequency =  now
                print("tag:",tag,"\nbegin:",begin,"      now:",now)
                
                # write
                if(now != begin and temp == tag - 1 and loop2 == 0):
                    print("data source:",line.replace("\n","").split(",")[0])
                    print("---writting:",tag,"---")
                    loop = 1
                    f2.write(line+"\n")
                elif loop == 1 and now == begin :
                    print("data source:",line.replace("\n","").split(",")[0])
                    print("---writting:",tag,"---")
                    loop2 = 1
                    f2.write(line+"\n")
                elif  loop2 == 1  and (abs(now-begin) == 250 or begin == 924375) and temp == tag - 1:
                    # stop write and exit the process and close the file 
                    print("Frequency:",now)
                    print("---ending:",tag,"---")
                    f.close()
                    f2.close()
                    # use the tag as file name
                    os.rename("./moisture_estimation/data/Data.txt",("./moisture_estimation/data/Data_"+str(tag)+".txt"))
                    end_time = time.time()
                    print("total time: ", end_time - start_time)
                    exit()

            line = f.readline()
            temp = -1
        
        
        f.close()
        f2.close()
        print("----------------")
            
 
