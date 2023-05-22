import dpkt
import socket

with open('imgmp4.pcap', 'rb') as f: 
    pcap = dpkt.pcap.Reader(f)
    dic = {}
    imgidx = 1
    mp4idx = 1
    
    for timestamp, buf in pcap:
        eth = dpkt.ethernet.Ethernet(buf)
        ip = eth.data

        if eth.type != dpkt.ethernet.ETH_TYPE_IP:
            continue
        if ip.p != dpkt.ip.IP_PROTO_TCP:
            continue
        #if socket.inet_ntoa(ip.src) != '101.79.241.17' or socket.inet_ntoa(ip.dst) != '203.232.131.77':
        #continue

        tcp = ip.data

        if len(str(tcp.data.hex())) < 10:
            continue

        #print('Timestamp: ', timestamp)
        #print('IP: %s -> %s len=%d' % (socket.inet_ntoa(ip.src), socket.inet_ntoa(ip.dst), ip.len))
        #print('Port : %d -> %d ack=%d seq=%d' % (tcp.sport, tcp.dport, tcp.ack, tcp.seq))
        #print('Payload: ', str(tcp.data))
        streamIndex = socket.inet_ntoa(ip.src) + ':' + str(tcp.sport) + ':'
        streamIndex += socket.inet_ntoa(ip.dst) + ':' + str(tcp.dport) + ':' + str(tcp.ack)
        #print('StreamIndex: %s, Payload: %s' % (streamIndex, str(tcp.data)))

        if streamIndex in dic:
            streamIndexValue = dic[streamIndex]
            streamIndexValue += '放送' + str(tcp.seq) + '新聞' + str(tcp.data.hex())
            del dic[streamIndex]
            dic[streamIndex] = streamIndexValue
        #    print(str(tcp.seq) + '新聞' + str(tcp.data.hex()))
        else:
            dic[streamIndex] = str(tcp.seq) + '新聞' + str(tcp.data.hex())
        #   print(str(tcp.seq) + '新聞' + str(tcp.data.hex()))

    for key in dic:
        streamValue1 = dic[key]
        arr_streamvalue1 = streamValue1.split('放送')

        strSeq = []
        strData = []
        for val in arr_streamvalue1:
            arr_streamvalue2 = val.split('新聞')
            strSeq.append(arr_streamvalue2[0])
            strData.append(arr_streamvalue2[1])

        for i in range(len(strSeq)):
            for j in range(len(strSeq) - 1):
                string_seq = int(strSeq[j + 1])
                string_data = strData[j + 1]
                if int(strSeq[j]) > int(strSeq[j + 1]):
                    del strSeq[j + 1]
                    strSeq.insert(j, string_seq)
                    del strData[j + 1]
                    strData.insert(j, string_data)

        allpacket = ''
        for packet in strData:
            allpacket += packet

        result1 = allpacket.find('ffd8ffe0') ##이미지 시작
        result2 = allpacket.find('ffd9')     ##이미지의 끝
        result3 = allpacket.find('0000001866747970') ## mp4 시작
        # result4 = allpacket.find('000000206674797069736f6d') ## mp4 끝

        imgString = ''
        mp4String = ''
        if result1 > -1 and result2 > -1: ## 음수가 나오는경우 : 파일이 깨진것
            imgString = allpacket[result1:result2+4]
            print(imgString)


            if len(imgString) % 2 == 0:	
                with open(str(imgidx) + ".jpg", "wb") as project: ##헥사코드가 홀수 : 이미지 파일이 깨짐
                    project.write(bytes.fromhex(imgString))
                    imgidx = imgidx + 1
                    
                    
        if result3 > -1: ## and result4 > -1: ## 음수가 나오는경우 : 파일이 깨진것
            mp4String = allpacket[result3:] ## result4+24]
            print(mp4String)
            
            if len(mp4String) % 2 == 0:
                with open(str(mp4idx) + ".mp4", "wb") as project:
                    project.write(bytes.fromhex(mp4String))
                    mp4idx = mp4idx + 1