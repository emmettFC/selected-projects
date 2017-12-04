'''
    Build annotation automatically from openCv bounding rectangle dimensions
'''

from xml.etree import ElementTree as ET
import re

def buildAnnotation(x, y, h, w, filename, object, folder):
    xmin = x
    ymin = y 
    ymax = y + h 
    xmax = x + w 
    path = './' + folder + '/' + filename
    xml_data = '''<annotation>
        <folder>'''+folder+'''</folder>
        <filename>'''+filename+'''</filename>
        <path>'''+path+'''</path>
        <source>
            <database>Unknown</database>
        </source>
        <size>
            <width>500</width>
            <height>888</height>
            <depth>3</depth>
        </size>
        <segmented>0</segmented>
        <object>
            <name>'''+objectName+'''</name>
            <pose>Unspecified</pose>
            <truncated>0</truncated>
            <difficult>0</difficult>
            <bndbox>
                <xmin>'''+xmin+'''</xmin>
                <ymin>'''+ymin+'''</ymin>
                <xmax>'''+xmax+'''</xmax>
                <ymax>'''+ymax+'''</ymax>
            </bndbox>
        </object>
    </annotation>'''
    # write annotation to xml file
    tree = ET.XML(xml_data)
    outFile = path.replace('.jpg', '.xml')
    with open(outFile, "w") as f:
        f.write(ET.tostring(tree))



