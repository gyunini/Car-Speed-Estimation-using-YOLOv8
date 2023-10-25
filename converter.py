import os
import xml.etree.ElementTree as ET


#file_path = 'training/label_daejeon/Cheonan_gangjeong_20201019_1600_MON_15m_RH_highway_TW3_sunny_FHD.xml'
new_file_path = "txt/"
label_index = {"car":0,
               "truck":1,
               "bus":2}


def readXML(file_path):
    tree = ET.parse(file_path)
    i=1
    while(1):
        j=1
        root = tree.find("image["+str(i)+"]")
        if(root == None):
            break
        print(root.attrib)
        file_name = root.get("name")
        resolution_x = root.get("width")
        resolution_y = root.get("height")
        print(file_name)
        while(1):
            _box = root.find('box['+str(j)+']')
            #print(_box.attrib)
            if(_box == None):
                break
            old_label = _box.get('label')
            old_index = label_index[old_label]
            
            old_xtl = _box.get('xtl')
            old_ytl = _box.get('ytl')
            old_xbr = _box.get('xbr')
            old_ybr = _box.get('ybr')
            
            
            
            writeTXT(j,file_name,new_file_path,old_index,old_xtl,old_ytl,old_xbr,old_ybr, resolution_x,resolution_y)
            j+=1
        i+=1
   

def writeTXT(j,file_name,file_path,old_index,old_xtl,old_ytl,old_xbr,old_ybr,resolution_x,resolution_y):
    file_name = file_name[:-3]
    #print(file_name)
    file_name = file_path+file_name+"txt"
    #print(file_name)
    data =  str(old_index)+' '+str(round((float(old_xbr)+float(old_xtl))/2,2)/float(resolution_x)) +' '+str(round((float(old_ybr)+float(old_ytl))/2,2)/float(resolution_y)) +' '+str(round((float(old_xbr)-float(old_xtl)),2)/float(resolution_x)) +' '+str(round((float(old_ybr)-float(old_ytl)),2)/float(resolution_y))

    if(j==1):
        f = open(file_name,'w')
    else:
        f = open(file_name,'a')
        data = '\n'+data
    
    print(data)
    f.write(data)
    f.close()

#readXML(file_path,file_path)

folder = "xml/"
xml_list = os.listdir(folder)
for xml_file in xml_list:
    strd = xml_file
    print(strd)

    xml_file_path = folder+strd
    readXML(xml_file_path)
