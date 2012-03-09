# context of inherited method?
import testdata.CCMView

class GameView(testdata.CCMView.CCMView):
    pass

gv = GameView()
gv.wa()
