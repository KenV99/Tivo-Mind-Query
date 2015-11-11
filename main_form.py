#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2015 KenV99
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import wx
import wx.grid as Grid
import wx.grid
import wx.xrc
from mind_query_rpc import RemoteExt
import os, sys
from ConfigParser import SafeConfigParser
import ctypes

class Settings(object):
    def __init__(self):
        self.fn = os.path.join(os.getcwd(), 'settings.ini')
        self.parser = SafeConfigParser()
        if os.path.isfile(self.fn) is False:
            self.createini()
        try:
            self.parser.read(self.fn)
            self.un = self.parser.get('settings','username')
            self.pw = self.parser.get('settings','password')
            self.tsn = self.parser.get('settings', 'tsn')
        except:
            self.un = ''
            self.pw = ''
            self.tsn = ''
        if self.un == '' or self.pw == '':
            msg = 'In order to use this program you MUST edit the ini file with your TiVo account\nuser name and password. For Offer Searches, you MUST also include your TSN.\nPlease relaunch the program after providing the info.'
            MessageBox = ctypes.windll.user32.MessageBoxA
            MessageBox(None, msg, 'Error - ini file incomplete', 0)
            sys.exit(-1)

    def createini(self):
        self.parser.add_section('settings')
        self.parser.set('settings' , 'username', '')
        self.parser.set('settings', 'password', '')
        self.parser.set('settings', 'tsn', '')
        try:
            with open(self.fn, 'w') as f:
                self.parser.write(f)
        except Exception as e:
            pass

# from wx.lib.dialogs import ScrolledMessageDialog
#
# def InfoText(parent, message, caption='Mind Server Error'):
#     dlg = ScrolledMessageDialog(parent, message, caption)
#     dlg.ShowModal()
#     dlg.Destroy()

def Info(parent, message, caption='Mind Server Error'):
    dlg =wx.MessageDialog(parent,message,caption, wx.OK|wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()

class KGrid(Grid.Grid):
    def __init__(self, parent, data, colnames):

        # The base class must be initialized *first*
        Grid.Grid.__init__(self, parent, -1)
        self.parent = parent
        self.data = data
        self.colnames = colnames
        self.CreateGrid(0,0)
        self.UpdateTable()
        self.Bind(Grid.EVT_GRID_LABEL_RIGHT_CLICK, self.OnLabelRightClicked)
        self.Bind(Grid.EVT_GRID_CELL_LEFT_CLICK, self.OnGridCellLeftClick)
        self.Bind(Grid.EVT_GRID_CELL_RIGHT_CLICK, self.OnGridCellRightClick)

    def UpdateTable(self, resetCols=True):
        self.BeginBatch()
        self.ClearGrid()
        self.PopulateTable(resetCols)
        self.EndBatch()
        self.ForceRefresh()

    def PopulateTable(self, resetCols=True):
        self.ClearGrid()
        if resetCols:
            if self.NumberCols > 0:
                self.DeleteCols(0,self.NumberCols)
            self.AppendCols(len(self.colnames))

        if self.NumberRows > 0:
            self.DeleteRows(0, self.NumberRows)

        for counter, colname in enumerate(self.colnames):
            self.SetColLabelValue(counter, colname)
        for x, row in enumerate(self.data):
            self.AppendRows(1)
            for y, col in enumerate(self.colnames):
                if col == 'Type':
                    type = row[1][col]
                    attr = Grid.GridCellAttr()
                    if type == 'series':
                        attr.SetTextColour('blue')
                        self.SetRowAttr(x, attr)
                    elif type == 'movie':
                        attr.SetTextColour('magenta')
                        self.SetRowAttr(x, attr)
                    elif type == 'special':
                        attr.SetTextColour('forest green')
                        self.SetRowAttr(x, attr)
                    elif type == '':
                        attr.SetTextColour('red')
                        self.SetRowAttr(x, attr)
                try:
                    self.SetCellValue(x, y, row[1][col])
                except Exception as e:
                    pass
        self.AutoSize()

    def OnLabelRightClicked(self, evt):
        # Did we click on a row or a column?
        row, col = evt.GetRow(), evt.GetCol()
        if row == -1: self.colPopup(col, evt)
        # elif col == -1: self.rowPopup(row, evt)

    def OnGridCellLeftClick(self, evt):
        row = evt.GetRow()
        self.SelectRow(row)

    def OnGridCellRightClick(self, evt):
        row = evt.GetRow()
        self.cellPopup(row,evt)

    def cellPopup(self, row, evt):
        menu = wx.Menu()
        sortID = wx.NewId()
        menu.Append(sortID, "Copy IDs to Clipboard")

        def copyToClipboard(event, self=self, row=row):
            pass
            sID = self.data[row][1]['Series ID']
            pID = self.data[row][1]['Episode ID']
            output = "seriesId : %s\nprogramId : %s\n" % (sID, pID)
            if wx.TheClipboard.Open():
                wx.TheClipboard.SetData(wx.TextDataObject(output.encode('utf-8')))
                wx.TheClipboard.Close()


        self.Bind(wx.EVT_MENU, copyToClipboard, id=sortID)

        self.PopupMenu(menu)
        menu.Destroy()
        return

    def colPopup(self, col, evt):
        """(col, evt) -> display a popup menu when a column label is
        right clicked"""
        x = self.GetColSize(col)/2
        menu = wx.Menu()
        id1 = wx.NewId()
        sortID = wx.NewId()

        xo, yo = evt.GetPosition()
        self.SelectCol(col)
        cols = self.GetSelectedCols()
        self.Refresh()
        # menu.Append(id1, "Delete Col(s)")
        menu.Append(sortID, "Sort Column")


        def sort(event, self=self, col=col):
            self.SortColumn(col)

        if len(cols) == 1:
            self.Bind(wx.EVT_MENU, sort, id=sortID)

        self.PopupMenu(menu)
        menu.Destroy()
        return

    def SortColumn(self, col):
        """
        col -> sort the data based on the column indexed by col
        """
        name = self.GetColLabelValue(col)
        tdata = sorted(self.data, key=lambda sx: sx[1][name])
        self.colnames = []
        for i in xrange(0, self.NumberCols):
            self.colnames.append(self.GetColLabelValue(i))
        self.data = tdata
        self.UpdateTable(resetCols=False)
        self.SetSortingColumn(col)
        self.parent.Layout()

###########################################################################
## Class MyFrame1
###########################################################################

class MyFrame1(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition,
                          size=wx.Size(1028, 772),
                          style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER | wx.TAB_TRAVERSAL)

        # self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        self.m_menubar1 = wx.MenuBar(0)
        # self.mb_settings = wx.Menu()
        # self.miSettings = wx.MenuItem(self.mb_settings, wx.ID_ANY, u"Settings", wx.EmptyString, wx.ITEM_NORMAL)
        # self.mb_settings.Append(self.miSettings)
        #
        # self.m_menubar1.Append(self.mb_settings, u"Settings")

        self.SetMenuBar(self.m_menubar1)

        bSizer1 = wx.FlexGridSizer(2, 0, 0, 0)
        bSizer1.AddGrowableCol(0)
        bSizer1.AddGrowableRow(1)
        bSizer1.SetFlexibleDirection(wx.BOTH)
        bSizer1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        gbSizer1 = wx.GridBagSizer(0, 0)
        gbSizer1.SetFlexibleDirection(wx.BOTH)
        gbSizer1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText4 = wx.StaticText(self, wx.ID_ANY, u"Text Search", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText4.Wrap(-1)
        gbSizer1.Add(self.m_staticText4, wx.GBPosition(0, 0), wx.GBSpan(1, 1), wx.ALL, 5)

        self.m_staticText17 = wx.StaticText(self, wx.ID_ANY, u"Search Type", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText17.Wrap(-1)
        gbSizer1.Add(self.m_staticText17, wx.GBPosition(1, 0), wx.GBSpan(1, 1), wx.ALL, 5)

        self.m_staticText18 = wx.StaticText(self, wx.ID_ANY, u"Search Field", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText18.Wrap(-1)
        gbSizer1.Add(self.m_staticText18, wx.GBPosition(2, 0), wx.GBSpan(1, 1), wx.ALL, 5)

        choFieldChoices = [u"Title", u"Title Prefix",u"Subtitle (episode)", u"Keyword",  u"Title Keyword", u"Subtitle Keyword", u"Description Keyword"]
        self.choField = wx.Choice(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choFieldChoices, 0|wx.TAB_TRAVERSAL)
        self.choField.SetSelection(0)
        gbSizer1.Add(self.choField, wx.GBPosition(2, 1), wx.GBSpan(1, 1), wx.ALL, 5)

        self.m_staticText19 = wx.StaticText(self, wx.ID_ANY, u"Language", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText19.Wrap(-1)
        gbSizer1.Add(self.m_staticText19, wx.GBPosition(3, 0), wx.GBSpan(1, 1), wx.ALL, 5)

        cmbLangChoices = [u"English", u"Spanish", u"All"]
        self.cmbLang = wx.ComboBox(self, wx.ID_ANY, u"English", wx.DefaultPosition, wx.DefaultSize, cmbLangChoices, 0|wx.TAB_TRAVERSAL)
        self.cmbLang.SetSelection(0)
        gbSizer1.Add(self.cmbLang, wx.GBPosition(3, 1), wx.GBSpan(1, 1), wx.ALL, 5)

        self.m_staticText20 = wx.StaticText(self, wx.ID_ANY, u"Limit to", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText20.Wrap(-1)
        gbSizer1.Add(self.m_staticText20, wx.GBPosition(4, 0), wx.GBSpan(1, 1), wx.ALL, 5)

        choObjChoices = [u"Content Search", u"Offer Search", u"Collection Search"]
        self.choObj = wx.Choice(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choObjChoices, 0|wx.TAB_TRAVERSAL)
        self.choObj.SetSelection(0)
        gbSizer1.Add(self.choObj, wx.GBPosition(1, 1), wx.GBSpan(1, 1), wx.ALL, 5)

        choLimitChoices = [ wx.EmptyString, u"movie", u"series", u"special"]
        self.choLimit = wx.Choice(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choLimitChoices, 0|wx.TAB_TRAVERSAL)
        self.choLimit.SetSelection(0)
        gbSizer1.Add(self.choLimit, wx.GBPosition(4, 1), wx.GBSpan(1, 1), wx.ALL, 5)

        cmbTxtSearchChoices = []
        self.cmbTxtSearch = wx.ComboBox(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                        cmbTxtSearchChoices, 0|wx.TAB_TRAVERSAL)
        gbSizer1.Add(self.cmbTxtSearch, wx.GBPosition(0, 1), wx.GBSpan(1, 1), wx.ALL, 5)

        self.m_button2 = wx.Button(self, wx.ID_ANY, u"&Search", wx.DefaultPosition, wx.DefaultSize, 0|wx.TAB_TRAVERSAL)

        gbSizer1.Add(self.m_button2, wx.GBPosition(6, 0), wx.GBSpan(1, 1), wx.ALL, 5)

        # gbSizer1.AddGrowableCol(3)
        # gbSizer1.AddGrowableRow(6)

        bSizer1.Add(gbSizer1, 1, wx.EXPAND, 5)

        self.grid = KGrid(self, data, colnames)
        self.grid.SetRowLabelSize(0)
        self.grid.EnableEditing(False)
        self.grid.EnableGridLines(True)
        self.grid.EnableDragGridSize(False)
        self.grid.AutoSizeColumns()
        self.grid.EnableDragColMove(True)
        self.grid.EnableDragColSize(True)
        self.grid.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
        self.grid.SetDefaultCellAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)

        bSizer1.Add(self.grid, 0, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(bSizer1)
        self.grid.Hide()
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.Bind(wx.EVT_MENU, self.showSettings, id=self.miSettings.GetId())
        self.m_button2.Bind(wx.EVT_BUTTON, self.do_search)
        self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyDown)
        self.m_button2.SetDefault()
        self.cmbTxtSearch.SetFocus()

        # self.result_grid.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.sort_grid)

    def OnKeyDown(self, evt):
        key = evt.GetKeyCode()
        if key == wx.WXK_RETURN:
            self.do_search(evt)
        else:
            evt.Skip()

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def showSettings(self, event):
        event.Skip()

    def do_search(self, event):
        wait = wx.BusyCursor()
        searchString = self.cmbTxtSearch.Value
        searchType = self.choObj.GetStringSelection().replace(" ", "")
        searchType = lowerfirst(searchType)
        searchField = self.choField.GetStringSelection().replace(" ", "")
        searchField = lowerfirst(searchField)
        searchLang = self.cmbLang.Value
        searchLimit = self.choLimit.GetStringSelection()
        un = settings.un
        pw = settings.pw
        tsn = settings.tsn
        remote = RemoteExt(un, pw, tsn)
        kwargs = {searchField:searchString, 'levelOfDetail':'medium', 'descriptionLanguage': searchLang}
        results = remote.genericSearch(searchType, **kwargs)
        if 'error' in results[0].keys():
            Info(self, results[0]['error'])
            return
        if searchType == 'contentSearch':
            coldict = {'collectionType':'Type', 'seasonEpisodeNum': 'SE#EP#', 'title': 'Series Title', 'subtitle':'Episode Title',
                       'originalAirdate':'Orig Air Date', 'partnerCollectionId': 'Series ID',
                       'partnerContentId': 'Episode ID', 'description': 'Description'}
            colnames = ['Type', 'SE#EP#', 'Series Title', 'Episode Title',
                       'Orig Air Date', 'Series ID',
                       'Episode ID', 'Description']
        elif searchType == 'offerSearch':
            coldict = {'collectionType':'Type', 'seasonEpisodeNum': 'SE#EP#', 'title': 'Series Title', 'subtitle':'Episode Title',
                       'originalAirdate':'Orig Air Date', 'startTime':'Upcoming date/time', 'partnerCollectionId': 'Series ID',
                       'partnerContentId': 'Episode ID', 'description': 'Description'}
            colnames = ['Type', 'SE#EP#', 'Series Title', 'Episode Title',
                       'Orig Air Date', 'Upcoming date/time','Series ID',
                       'Episode ID', 'Description']
        else:  #'collectionSearch'
            coldict = {'title': 'Title', 'collectionType':'Type', 'partnerCollectionId': 'Series ID',
                       'description': 'Description', 'originalAirdate':'Date'}
            colnames = ['Type', 'Title', 'Date', 'Series ID', 'Description']
        data = []
        for counter, result in enumerate(results):
            d = {}
            for k in coldict.keys():
                try:
                    d[coldict[k]] = result[k]
                except KeyError:
                    d[coldict[k]] = ''
            data.append((str(counter), d))

        try:
            self.grid.Show()
            self.grid.colnames = colnames
            self.grid.data = data
            self.grid.UpdateTable()

        except Exception as e:
            pass
        del wait
        self.Layout()

def lowerfirst(s):
    func = lambda s: s[:1].lower() + s[1:] if s else ''
    return func(s)


class MyApp(wx.App):

    # wxWindows calls this method to initialize the application
    def OnInit(self):

        # Create an instance of our customized Frame class
        frame = MyFrame1(None)
        frame.Show(True)

        # Tell wxWindows that this is our main window
        self.SetTopWindow(frame)

        # Return a success flag
        return True


if __name__ == '__main__':
    settings = Settings()
    colnames = ['Temp']
    data = [('1', {'Temp':'temp'})]
    # colnames, data = get_data(test=True)

    app = MyApp(0)     # Create an instance of the application class
    app.MainLoop()     # Tell it to start processing events