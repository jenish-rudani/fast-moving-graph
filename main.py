import random
import pyqtgraph as pg
from collections import deque
from pyqtgraph.Qt import QtGui, QtCore
from signal import pause
from threading import Thread
from queue import Queue
import signal


def keyBoardInterruptHandler(signal, frame):
  global wObj
  print("Signal Caught")
  wObj.exit()


signal.signal(signal.SIGTERM, keyBoardInterruptHandler)
signal.signal(signal.SIGINT, keyBoardInterruptHandler)

app = QtGui.QApplication([])
win = pg.GraphicsWindow()


class Graph:
  def __init__(self, ):
    self.numberofTags = 10
    self.count = 0
    self.maxLen = 1000  # max number of data points to show on graph
    self.db = {}
    self.tagCounter = 0
    self.running = True
    self.app = app
    self.win = win
    self.q = [Queue() for i in range(10)]
    self.dat = [deque() for i in range(10)]
    self.plotHandler = None
    self.curveHandler = [None for i in range(10)]
    self.colorList = ["#803723", "#1ff2ed", "#00fa5c",
                      "#aff0ed", "#f1af00", "#803723", "#8025ab", "#baa4a4", "#00cc99", "#990099"]

    self.initPlotHandler()

    self.graphUpdateSpeedMs = 40
    self.timer = QtCore.QTimer()  # to create a thread that calls a function at intervals
    self.timer.timeout.connect(self.update)
    self.timer.start(self.graphUpdateSpeedMs)

  def initPlotHandler(self):
    for i in range(10):
      self.plotHandler = self.win.addPlot()
      self.plotHandler.setYRange(-20, -70, padding=0.02)
      self.plotHandler.setXRange(0, self.maxLen, padding=0.1)
      self.win.nextRow()
      color = self.colorList[i]
      self.curveHandler[i] = self.plotHandler.plot(pen=pg.mkPen(color))

  def update(self):
    for i in range(len(self.db.keys())):
      if len(self.dat[i]) > self.maxLen:
        self.dat[i].popleft()
      try:
        self.dat[i].append(self.q[i].get(block=False))
        self.curveHandler[i].setData(self.dat[i])
      except Exception:
        self.curveHandler[i].setData(self.dat[i])
    self.app.processEvents()

  def yt(self, tag_id, rssi):
    print("Count {} | Tag Detected : {} | RSSI : {}".format(
        self.count, tag_id, rssi))
    if tag_id not in self.db:
      print("Not in database")
      self.db[tag_id] = self.tagCounter
      self.tagCounter += 1
    self.count += 1
    n = self.db[tag_id]
    if len(self.dat[n]) > self.maxLen:
      self.dat[n].popleft()
    self.dat[n].append(rssi)
    self.curveHandler[n].setData(self.dat[n])
    self.app.processEvents()

  def randomDataGenerator(self):
    a = ['111', '222', '333', '444', '555', '666', '777', '888', '999', '000']
    while self.running:
      randomIndex = random.randint(0, 9)
      temp = -random.randint(15, 55)
      tag = a[randomIndex]
      self.yt(tag, temp)

  def exit(self):
    self.running = False
    import time
    time.sleep(1)
    QtGui.QApplication.closeAllWindows()

  def main(self):
    print("Starting Reading")
    self.randomDataGenerator()
    print("Reading Stopped")


if __name__ == '__main__':
  try:
    a = QtGui.QApplication.instance()
    wObj = Graph()
    T1 = Thread(target=wObj.main)
    T1.daemon = True
    T1.start()
    a.exec_()
  except Exception as e:
    print(e)
