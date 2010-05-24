# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore


class GradientWidget(QtGui.QGraphicsView):
    def __init__(self):
        QtGui.QGraphicsView.__init__(self)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QtGui.QGraphicsView.NoAnchor)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)
        
        self.gradRect = QtGui.QGraphicsRectItem(QtCore.QRectF(0, -10, 100, 10))
        self.gradient = QtGui.QLinearGradient(QtCore.QPointF(0,0), QtCore.QPointF(100,0))
        self.gradient.setColorAt(0, QtGui.QColor(0,0,0))
        self.gradient.setColorAt(1, QtGui.QColor(255,0,0))
        self.gradRect.setBrush(QtGui.QBrush(self.gradient))
        self.scene = QtGui.QGraphicsScene()
        self.setScene(self.scene)
        self.scene.addItem(self.gradRect)
        
        self.ticks = []
        self.addTick(0, QtGui.QColor(0,0,0), True)
        self.addTick(1, QtGui.QColor(255,0,0), True)
        self.setMaximumHeight(40)
        self.setFrameStyle(QtGui.QFrame.NoFrame | QtGui.QFrame.Plain)
     
        
    def addTick(self, x, c, e=False):
        tick = Tick([x*100, 0], c, e)
        self.ticks.append(tick)
        self.scene.addItem(tick)
        tick.connect(QtCore.SIGNAL('tickChanged'), self.tickChanged)
        
    def tickChanged(self, tick=None, delete=False):
        #print "tick changed"
        if delete:
            tick.disconnect(QtCore.SIGNAL('tickChanged'), self.tickChanged)
            self.ticks.remove(tick)
            self.scene.removeItem(tick)
        self.ticks.sort(lambda a,b: cmp(a.pos().x(), b.pos().x()))
        self.gradient.setStops([(t.x(), t.color) for t in self.ticks])
        self.gradRect.setBrush(QtGui.QBrush(self.gradient))
        self.emit(QtCore.SIGNAL('gradientChanged'), self)
        
    def resizeEvent(self, ev):
        self.fitInView(QtCore.QRectF(-6, -20, 112, 20), QtCore.Qt.KeepAspectRatio)
        
    def mouseReleaseEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton and len(self.items(ev.pos())) < 1:
            pos = self.mapToScene(ev.pos())
            self.addTick(pos.x()/100., QtGui.QColor(0,0,0))
            self.tickChanged()
        else:
            return QtGui.QGraphicsView.mouseReleaseEvent(self, ev)
        
    def getGradient(self):
        return self.gradient
        
    def getColor(self, x):
        x2 = ticks[0].x()
        for i in range(1,len(ticks)):
            x1 = x2
            x2 = ticks[i].x()
            if x1 < x and x2 >= x:
                f = (x-x1) / (x2-x1)
                c1 = ticks[i-1].color
                c2 = ticks[i].color
                r = c1.red() * (1.-f) + c2.red() * f
                g = c1.green() * (1.-f) + c2.green() * f
                b = c1.blue() * (1.-f) + c2.blue() * f
                c = QtGui.QColor()
                
                
            
        
## Multiple inheritance not allowed in PyQt. Retarded workaround:
class QObjectWorkaround:
    def __init__(self):
        self._qObj_ = QtCore.QObject()
    def connect(self, *args):
        return QtCore.QObject.connect(self._qObj_, *args)
    def disconnect(self, *args):
        return QtCore.QObject.disconnect(self._qObj_, *args)
    def emit(self, *args):
        return QtCore.QObject.emit(self._qObj_, *args)
        
        
class Tick(QtGui.QGraphicsPolygonItem, QObjectWorkaround):
    def __init__(self, pos, color, endTick=False, scale=10):
        QObjectWorkaround.__init__(self)
        self.scale = scale
        self.color = color
        self.endTick = endTick
        self.pg = QtGui.QPolygonF([QtCore.QPointF(0,0), QtCore.QPointF(-scale/3**0.5,scale), QtCore.QPointF(scale/3**0.5,scale)])
        QtGui.QGraphicsPolygonItem.__init__(self, self.pg)
        self.setPos(pos[0], pos[1])
        self.setFlags(QtGui.QGraphicsItem.ItemIsMovable | QtGui.QGraphicsItem.ItemIsSelectable)
        self.setBrush(QtGui.QBrush(QtGui.QColor(self.color)))

    def x(self):
        return self.pos().x()/100.

    def mouseMoveEvent(self, ev):
        if self.endTick:
            return
        if not ev.buttons() & QtCore.Qt.LeftButton:
            return
            
            
        newPos = ev.scenePos() + self.mouseOffset
        newPos.setY(self.pos().y())
        newPos.setX(min(max(newPos.x(), 0), 100))
        self.setPos(newPos)
        self.emit(QtCore.SIGNAL('tickChanged'), self)
        ev.accept()

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            ev.accept()
            self.mouseOffset = self.pos() - ev.scenePos()
            self.pressPos = ev.scenePos()
        elif ev.button() == QtCore.Qt.RightButton:
            ev.accept()
            if self.endTick:
                return
            self.emit(QtCore.SIGNAL('tickChanged'), self, True)
            
    def mouseReleaseEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton and ev.scenePos() == self.pressPos:
            self.color = QtGui.QColorDialog.getColor(self.color, None, "Select Color", QtGui.QColorDialog.ShowAlphaChannel)
            self.setBrush(QtGui.QBrush(QtGui.QColor(self.color)))
            self.emit(QtCore.SIGNAL('tickChanged'), self)
        