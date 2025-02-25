# -*- coding:utf-8 -*-
# Require Header
import os
import json
from functools import partial

# Sys Header
import sys
import traceback
import subprocess

import plugin.Qt as Qt
from Qt.QtCore import *
from Qt.QtGui import *
from Qt.QtWidgets import *

def loadUiType(uiFile):
    import plugin.Qt as Qt
    if Qt.__binding__.startswith('PyQt'):
        from Qt import _uic as uic
        return uic.loadUiType(uiFile)
    elif Qt.__binding__ == 'PySide':
        import pysideuic as uic
    else:
        import pyside2uic as uic
        
    import xml.etree.ElementTree as xml
    from cStringIO import StringIO

    parsed = xml.parse(uiFile)
    widget_class = parsed.find('widget').get('class')
    form_class = parsed.find('class').text

    with open(uiFile, 'r') as f:
        o = StringIO()
        frame = {}

        uic.compileUi(f, o, indent=0)
        pyc = compile(o.getvalue(), '<string>', 'exec')
        exec pyc in frame

        # Fetch the base_class and form class based on their type
        # in the xml from designer
        form_class = frame['Ui_%s'%form_class]
        base_class = eval('%s'%widget_class)

    return form_class, base_class

from Qt.QtCompat import wrapInstance

DIR = os.path.dirname(__file__)
UI_PATH = os.path.join(DIR,"ui","Cam_Item_Layout.ui") 
GUI_STATE_PATH = os.path.join(DIR, "json" ,'GUI_STATE.json')
form_class , base_class = loadUiType(UI_PATH)

class Cam_Item_Layout(form_class,base_class):
    def __init__(self,MainWindow):
        super(Cam_Item_Layout,self).__init__()
        self.setupUi(self)
        self.MainWindow = MainWindow
        self.Item_Add_BTN.clicked.connect(self.Item_Add_Fn) 
        self.Item_Clear_BTN.clicked.connect(self.Item_Clear_Fn) 
        self.Cam_Item_Num = 0
        self.Cam_Item_Scroll.verticalScrollBar().valueChanged.connect(self.Scroll_Fn)
        self.Scroll_Offset = 0

        self.Attr = {}
        self.Attr["Add_Crv_LE"] = ""
        self.Attr["Add_Motion_Path_LE"] = ""
        self.Attr["Name"] = ""
        
    def Item_Add_Fn(self):
        self.Cam_Item_Num += 1
        return Cam_Item(self,self.MainWindow)
        
    def Item_Clear_Fn(self):
        for i,child in enumerate(self.Item_Layout.children()):
            if i != 0:
                child.deleteLater()

    def Scroll_Fn(self):
        self.Scroll_Offset = self.Cam_Item_Scroll.verticalScrollBar().value()
        
UI_PATH = os.path.join(DIR,"ui","Cam_Item.ui") 
form_class , base_class = loadUiType(UI_PATH)

class Cam_Item(form_class,base_class):

    def __init__(self,parent,MainWindow):
        super(Cam_Item,self).__init__()
        self.setupUi(self)
        self.MainWindow = MainWindow
        self.Cam_Del_BTN.clicked.connect(self.Cam_Del_BTN_Fn)
        self.Cam_Con_CB.stateChanged.connect(self.Cam_Con_CB_Fn)

        # Note 初始化创建参数
        TotalCount = len(parent.Item_Layout.children())
        parent.Item_Layout.layout().insertWidget(TotalCount-1,self)
        self.Cam_LE.setText("Cam_Item_%s" % parent.Cam_Item_Num)
        self.Cam_Num_Label.setText(u"镜头%s" % TotalCount)
        self.setObjectName("Cam_Item_%s" % TotalCount)
        self.Num = TotalCount
        self.Attr = {}
        self.Attr["Add_CamGrp_LE"] = ""
        self.Attr["Add_Loc_LE"] = ""
        self.Attr["Add_Crv_LE"] = ""
        self.Attr["Add_Motion_Path_LE"] = ""
        self.Attr["Strat_Time_SB"] = 0
        self.Attr["End_Time_SB"] = 0
        self.MainWindow.Save_Json_Fun()

    def Cam_Del_BTN_Fn(self):
        self.deleteLater()
        ChildrenList = self.parent().children()
        for i,child in enumerate(ChildrenList):
            if i != 0:
                if i > self.Num:
                    # Note 修正 child 的序号
                    child.num -= 1
                    child.Cam_Num_Label.setText(u"镜头%s" % (i-1))
                    child.setObjectName("Cam_Item_%s" % (i-1))
                else:
                    child.Cam_Num_Label.setText(u"镜头%s" % i)
                    child.setObjectName("Cam_Item_%s" % i)
        
        self.Attr["Add_CamGrp_LE"] = ""
        self.Attr["Add_Loc_LE"] = ""
        self.Attr["Add_Crv_LE"] = ""
        self.Attr["Add_Motion_Path_LE"] = ""
        self.Attr["Strat_Time_SB"] = ""
        self.Attr["End_Time_SB"] = ""
        self.MainWindow.Save_Json_Fun()

    def Cam_Con_CB_Fn(self):
        ChildrenList = self.parent().children()
        for i,child in enumerate(ChildrenList):
            if i != 0:
                child.Cam_Con_CB.setChecked(False)
        
        self.Cam_Con_CB.setChecked(True)