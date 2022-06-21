#MD Jidanur Rahman
#7895504
#3010-A2

import socket,threading,sys,os,uuid,json,random

######    server requests handling functions #######

#checks if cookie exists in the client request headers
def check_cookie(headers):
    cookie_id = ""
    for item in headers[1:]:
        header = item.split(":")
        if header[0] == "Cookie":
            cookie_id = header[1]
    return cookie_id


#handle delete request
def delete_request(headers):
    response = "HTTP/1.1 200 OK\n"
    req = headers[0].split()[1]
    
    #cookie check
    cookie_id = check_cookie(headers)
    if cookie_id == "":
        cookie_id = uuid.uuid1()
        response += "Set-Cookie: " + str(cookie_id)+"\n"
    if "/api/memo" in req:
        try:
            memo_id = req.split('/')[3]
            # open memo for reading the data
            json_file = open("api/memo.json","r")
            data = json_file.read()
            json_file.close()

            #database exists
            if data:
                memo_list  = json.loads(data)
                item_found = False
                for item in memo_list:
                    #if key-id found then delete it
                    if item["id"] == memo_id:
                        memo_list.remove(item)
                        item_found = True
                # if id not found then send not found response
                if item_found == False:
                    response = 'HTTP/1.1 404 NOT FOUND\n\Memo does not exists'
                else:
                    # open memo for writing modified data
                    json_file = open("api/memo.json","w")
                    json.dump(memo_list,json_file)
                    json_file.close()
        except Exception as e:
            print(e)
            response = 'HTTP/1.1 404 NOT FOUND\n\Memo database Not Found'

    return response


#handle put request
def put_request(headers):

    response = "HTTP/1.1 200 OK\n"
    req = headers[0].split()[1]
    content =""
    #cookie check
    cookie_id = check_cookie(headers)
    if cookie_id == "":
        cookie_id = uuid.uuid1()
        response += "Set-Cookie: " + str(cookie_id)+"\n"
    if "/api/memo" in req:
        memo_id = req.split('/')[3]
        #getting the json contents
        idx = 1
        char =''
        while char != '{' and idx < len(headers):
            char = headers[idx]
            idx +=1
        content += char
        for i in range(idx,len(headers)):
            content += headers[i]
        if content[0] == "{": 
            modified_note = json.loads(content)
            try:
                # open memo for reading the data
                json_file = open("api/memo.json","r")
                data = json_file.read()
                json_file.close()
                if data:
                    memo_list  = json.loads(data)

                    memo_modified = False
                    for item in memo_list:
                        if item["id"] == memo_id:
                            item["note"] = modified_note["text"]
                            item["last modified"] = str(cookie_id)
                            memo_modified = True
                    # if id not found then send not found response
                    if memo_modified == False:
                        response = 'HTTP/1.1 404 NOT FOUND\n\Memo does not exists'
                    else:
                        # open memo for writing modified data
                        json_file = open("api/memo.json","w")
                        json.dump(memo_list,json_file)
                        json_file.close()
            except Exception as e:
                print(e)
                response = 'HTTP/1.1 404 NOT FOUND\n\Memo Not Found'

        
    return response



#handle post requests
def post_request(headers):
    response = "HTTP/1.1 200 OK\n"
    req = headers[0].split()[1]
    content =""
    newMemo = {}
    #cookie check
    cookie_id = check_cookie(headers)
    if cookie_id == "":
        cookie_id = uuid.uuid1()
        response += "Set-Cookie: " + str(cookie_id)+"\n"
    if req == "/api/memo":
        #getting the json contents
        idx = 1
        char =''
        while char != '{' and idx < len(headers):
            char = headers[idx]
            idx +=1
        content += char
        for i in range(idx,len(headers)):
            content += headers[i]
        #print(content)
        if content[0] == "{":
            data = json.loads(content)
            memo_id = str(random.randint(0,9999)) # random memo_id
            newMemo ={"last modified":str(cookie_id),"note":data["note"],"id": memo_id}
            try:
                # open memo for reading and adding new data
                json_file = open("api/memo.json","r+")
                data = json_file.read()
                if data:
                    memo_list  = json.loads(data)
                else: #starting new memo list
                    memo_list =[]
                memo_list.append(newMemo)
                print(memo_list)
                #clear old contents and write
                json_file.seek(0)
                json.dump(memo_list,json_file)
                json_file.close()

            except Exception as e:
                print(e)
                response = 'HTTP/1.1 404 NOT FOUND\n\Memo Not Found'
    return response




#handle get request
def get_request(headers):
    filename = headers[0].split()[1]
    response = "HTTP/1.1 200 OK\n"
    contents = ""
    img_content = ""
    
    #cookie check
    cookie_id = check_cookie(headers)
    if cookie_id == "":
        cookie_id = uuid.uuid1()
        response += "Set-Cookie: " + str(cookie_id) +"\n"
    
    if filename == '/': #default file to show
        filename = '/index.html'

    elif filename == '/favicon.ico':
        return response
    try:
        if "/images/" in filename:
            file = open("files" + filename,"rb")
        elif filename == "/api/memo":
            file = open("api/memo.json")
        else:
            file = open("files" + filename)
        
        contents = file.read()
        file.close()
    except Exception as e:
        print(e)
        response = 'HTTP/1.1 404 NOT FOUND\n\nFile Not Found'

    else:
        response += "content-length: " + str(len(contents)) +"\n"

        if filename == "/api/memo":
            response += "Content-Type: application/json"
            if contents == "": # if memo list is empty
                contents = "[]"
        elif "/images/" in filename:
            response += "Content-type: image/jpeg"
            response += "\nAccept-Ranges: bytes"
            img_content = contents
            contents = ""
            
        response += "\n\n" + contents

    return response,img_content




#handling client requests
def client_request(conn,addr):
    print("Connected by"+ str(addr))
    req  = conn.recv(1024)

    #client request parsing
    if req:
        print(req)
        req = req.decode('utf-8')
        headers = req.split('\n')
        req_type = headers[0].split()[0]
        img_content =""
        response =""
        if req_type == "GET":
            response = get_request(headers)
            #print(response)
            #handling tuple of 2 contents from get function
            img_content = response[1] #if get image request then it should be the bytes of image file
            response = response[0] # normal get requests

        elif req_type == "POST":
            response = post_request(headers)
        elif req_type == "PUT":
            response = put_request(headers)
        elif req_type == "DELETE":
            response = delete_request(headers)
            
        if len(img_content) > 2: # if image get request
            conn.send(response.encode())
            conn.send(img_content)
        else: # all other requests
            conn.sendall(response.encode())
   
    conn.close()
    sys.exit(0) # exiting the thread
    


############################################################


#main
server_host = "localhost"
server_port = int(sys.argv[1])
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_socket.bind((server_host,server_port))
server_socket.listen()

while True:
    print(threading.activeCount())
    try:
        conn,addr = server_socket.accept()
        curr_thread = threading.Thread(target=client_request,args=(conn,addr,))
        curr_thread.start()

    except Exception as e:
        print(e)
        print("exception caught")
        server_socket.close()
        os._exit(1)

    except KeyboardInterrupt as e:
        print("exit")
        server_socket.close()
        os._exit(0)
    
        

    
